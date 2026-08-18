import boto3
from datetime import date

from assetRegister.src.config import get_settings
from assetRegister.src.models import AssetEntry
from assetRegister.src.writeItemToTable import put_asset_entries, put_asset_entry


def make_entry(asset_id: str) -> AssetEntry:
    return AssetEntry(
        assetId=asset_id,
        uploaderName="Gurpreet Singh",
        fileName="Invoice",
        originalFileName="invoice.pdf",
        uploadDate=date(2026, 8, 18),
        s3Bucket="test-document-asset-register",
        s3Key=f"uploads/{asset_id}/invoice.pdf",
        contentType="application/pdf",
        fileSizeBytes=1234,
    )


def test_put_asset_entry_writes_item(moto_aws):
    put_asset_entry(make_entry("asset-1"))

    settings = get_settings()
    table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(
        settings.dynamodb_table_name
    )
    stored = table.get_item(Key={"assetId": "asset-1"})["Item"]
    assert stored["uploaderName"] == "Gurpreet Singh"
    assert stored["uploadDate"] == "2026-08-18"


def test_put_asset_entries_writes_every_item(moto_aws):
    entries = [make_entry(f"asset-{i}") for i in range(3)]

    put_asset_entries(entries)

    settings = get_settings()
    table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(
        settings.dynamodb_table_name
    )
    stored_ids = {item["assetId"] for item in table.scan()["Items"]}
    assert stored_ids == {"asset-0", "asset-1", "asset-2"}
