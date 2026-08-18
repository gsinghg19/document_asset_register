"""Provision the AWS resources the asset register backend needs:

  - an S3 bucket to store uploaded documents
  - a DynamoDB table to store asset entries

This is meant to be run once (by you, with your own AWS credentials) before
starting the backend for the first time. It is idempotent — safe to re-run,
it will skip anything that already exists.

Usage:
    python -m assetRegister.pipelines.provision_infra

Requires AWS credentials to be available in the usual boto3 ways (env vars,
`~/.aws/credentials`, SSO session, etc).
"""

import sys

import boto3
from botocore.exceptions import ClientError

AWS_REGION = "eu-west-2"
DYNAMODB_TABLE_NAME = "document-asset-register"


def resolve_bucket_name(sts_client) -> str:
    """S3 bucket names must be globally unique, so derive one from the
    account id rather than asking the user to pick something free."""
    account_id = sts_client.get_caller_identity()["Account"]
    return f"document-asset-register-{account_id}"


def ensure_bucket(s3_client, bucket_name: str) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"S3 bucket already exists: {bucket_name}")
        return
    except ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        if status != 404:
            raise

    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
    )
    s3_client.put_bucket_versioning(
        Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
    )
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
        },
    )
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )
    print(f"Created S3 bucket: {bucket_name}")


def ensure_table(dynamodb_client, table_name: str) -> None:
    try:
        dynamodb_client.describe_table(TableName=table_name)
        print(f"DynamoDB table already exists: {table_name}")
        return
    except ClientError as err:
        if err.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    dynamodb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "assetId", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "assetId", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb_client.get_waiter("table_exists").wait(TableName=table_name)
    print(f"Created DynamoDB table: {table_name}")


def main() -> None:
    sts_client = boto3.client("sts", region_name=AWS_REGION)
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    dynamodb_client = boto3.client("dynamodb", region_name=AWS_REGION)

    try:
        bucket_name = resolve_bucket_name(sts_client)
        ensure_bucket(s3_client, bucket_name)
        ensure_table(dynamodb_client, DYNAMODB_TABLE_NAME)
    except ClientError as err:
        print(f"AWS error: {err}", file=sys.stderr)
        sys.exit(1)

    print()
    print("Done. Put these in your .env (see .env.example):")
    print(f"  AWS_REGION={AWS_REGION}")
    print(f"  S3_BUCKET_NAME={bucket_name}")
    print(f"  DYNAMODB_TABLE_NAME={DYNAMODB_TABLE_NAME}")


if __name__ == "__main__":
    main()
