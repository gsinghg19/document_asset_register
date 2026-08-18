"""Thin wrapper around the S3 upload call used by the asset register."""

import boto3

from assetRegister.src.config import get_settings


def _s3_client():
    settings = get_settings()
    return boto3.client("s3", region_name=settings.aws_region)


def upload_file_to_s3(file_bytes: bytes, key: str, content_type: str) -> str:
    """Upload `file_bytes` to the configured bucket under `key`.

    Returns the s3:// URI of the stored object.
    """
    settings = get_settings()
    client = _s3_client()
    client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{settings.s3_bucket_name}/{key}"
