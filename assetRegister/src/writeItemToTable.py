"""Write asset entries into the DynamoDB asset register table."""

import boto3

from assetRegister.src.config import get_settings
from assetRegister.src.models import AssetEntry


def _table():
    settings = get_settings()
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(settings.dynamodb_table_name)


def put_asset_entry(entry: AssetEntry) -> None:
    """Persist a single asset entry as an item in the DynamoDB table."""
    _table().put_item(Item=entry.to_dynamodb_item())
