from datetime import date

import pytest
from pydantic import ValidationError

from assetRegister.src.models import AssetEntry


def make_entry(**overrides) -> AssetEntry:
    defaults = dict(
        assetId="asset-1",
        uploaderName="Gurpreet Singh",
        fileName="Invoice",
        originalFileName="invoice.pdf",
        uploadDate=date(2026, 8, 18),
        s3Bucket="my-bucket",
        s3Key="uploads/asset-1/invoice.pdf",
        contentType="application/pdf",
        fileSizeBytes=1234,
    )
    defaults.update(overrides)
    return AssetEntry(**defaults)


def test_asset_entry_round_trips_through_dynamodb_item():
    entry = make_entry()
    item = entry.to_dynamodb_item()

    assert item["uploadDate"] == "2026-08-18"
    assert isinstance(item["createdAt"], str)

    rebuilt = AssetEntry.from_dynamodb_item(item)
    assert rebuilt.assetId == entry.assetId
    assert rebuilt.uploadDate == entry.uploadDate


def test_asset_entry_requires_all_fields():
    with pytest.raises(ValidationError):
        AssetEntry(assetId="asset-1")


def test_asset_entry_rejects_invalid_date():
    with pytest.raises(ValidationError):
        make_entry(uploadDate="not-a-date")
