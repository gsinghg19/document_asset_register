"""Read asset entries back out of the DynamoDB asset register table."""

import boto3

from assetRegister.src.config import get_settings
from assetRegister.src.models import AssetEntry


def _table():
    settings = get_settings()
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(settings.dynamodb_table_name)


def list_asset_entries() -> list[AssetEntry]:
    """Return every asset entry in the table.

    Uses a table scan, which is fine at the scale of an internal asset
    register. If the table grows large enough for this to matter, switch to
    a query against a GSI (e.g. on `uploadDate`).
    """
    items: list[dict] = []
    table = _table()
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return [AssetEntry.from_dynamodb_item(item) for item in items]


def get_asset_entry(asset_id: str) -> AssetEntry | None:
    """Fetch a single asset entry by id, or None if it doesn't exist."""
    response = _table().get_item(Key={"assetId": asset_id})
    item = response.get("Item")
    if item is None:
        return None
    return AssetEntry.from_dynamodb_item(item)
