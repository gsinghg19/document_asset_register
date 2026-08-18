"""Write asset entries into the DynamoDB asset register table."""

from collections.abc import Iterable

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


def put_asset_entries(entries: Iterable[AssetEntry]) -> None:
    """Persist multiple asset entries in a single batch.

    Uses boto3's `batch_writer`, which handles the 25-item-per-request
    DynamoDB limit and retries unprocessed items automatically.
    """
    table = _table()
    with table.batch_writer() as batch:
        for entry in entries:
            batch.put_item(Item=entry.to_dynamodb_item())
