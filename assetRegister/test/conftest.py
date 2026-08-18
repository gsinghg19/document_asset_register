import os

import boto3
import pytest
from moto import mock_aws

from assetRegister.src.config import get_settings

TEST_REGION = "eu-west-2"
TEST_BUCKET = "test-document-asset-register"
TEST_TABLE = "test-document-asset-register"


@pytest.fixture
def moto_aws(monkeypatch):
    """Spin up a fake S3 bucket + DynamoDB table for a single test.

    Also points `Settings` at the fake bucket/table via env vars, and clears
    the `get_settings` cache so each test starts from a clean config.
    """
    monkeypatch.setenv("AWS_REGION", TEST_REGION)
    monkeypatch.setenv("S3_BUCKET_NAME", TEST_BUCKET)
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", TEST_TABLE)
    # moto still wants *some* credentials present in the environment.
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    get_settings.cache_clear()

    with mock_aws():
        s3 = boto3.client("s3", region_name=TEST_REGION)
        s3.create_bucket(
            Bucket=TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": TEST_REGION},
        )

        dynamodb = boto3.client("dynamodb", region_name=TEST_REGION)
        dynamodb.create_table(
            TableName=TEST_TABLE,
            AttributeDefinitions=[{"AttributeName": "assetId", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "assetId", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )

        yield

    get_settings.cache_clear()
