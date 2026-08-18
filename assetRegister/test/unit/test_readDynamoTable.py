from datetime import date

from assetRegister.src.models import AssetEntry
from assetRegister.src.readDynamoTable import get_asset_entry, list_asset_entries
from assetRegister.src.writeItemToTable import put_asset_entry


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


def test_get_asset_entry_returns_none_when_missing(moto_aws):
    assert get_asset_entry("does-not-exist") is None


def test_get_asset_entry_returns_stored_entry(moto_aws):
    put_asset_entry(make_entry("asset-1"))

    entry = get_asset_entry("asset-1")

    assert entry is not None
    assert entry.assetId == "asset-1"
    assert entry.uploadDate == date(2026, 8, 18)


def test_list_asset_entries_returns_everything(moto_aws):
    put_asset_entry(make_entry("asset-1"))
    put_asset_entry(make_entry("asset-2"))

    entries = list_asset_entries()

    assert {e.assetId for e in entries} == {"asset-1", "asset-2"}
