"""Data model for a single asset register entry."""

from datetime import date, datetime, timezone

from pydantic import BaseModel, Field


class AssetEntry(BaseModel):
    """One row in the DynamoDB asset register table."""

    assetId: str
    uploaderName: str
    fileName: str
    originalFileName: str
    uploadDate: date
    s3Bucket: str
    s3Key: str
    contentType: str
    fileSizeBytes: int
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dynamodb_item(self) -> dict:
        """Serialize to plain JSON-safe types for a DynamoDB `put_item` call."""
        item = self.model_dump()
        item["uploadDate"] = self.uploadDate.isoformat()
        item["createdAt"] = self.createdAt.isoformat()
        return item

    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "AssetEntry":
        return cls(**item)
