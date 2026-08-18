import boto3
from datetime import date

from assetRegister.src.config import get_settings
from assetRegister.src.models import AssetEntry
from assetRegister.src.writeItemToTable import put_asset_entry


def test_put_asset_entry_writes_item(moto_aws):
    entry = AssetEntry(
        assetId="asset-1",
        uploaderName="Gurpreet Singh",
        fileName="Invoice",
        originalFileName="invoice.pdf",
        uploadDate=date(2026, 8, 18),
        s3Bucket="test-document-asset-register",
        s3Key="uploads/asset-1/invoice.pdf",
        contentType="application/pdf",
        fileSizeBytes=1234,
    )

    put_asset_entry(entry)

    settings = get_settings()
    table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(
        settings.dynamodb_table_name
    )
    stored = table.get_item(Key={"assetId": "asset-1"})["Item"]
    assert stored["uploaderName"] == "Gurpreet Singh"
    assert stored["uploadDate"] == "2026-08-18"
