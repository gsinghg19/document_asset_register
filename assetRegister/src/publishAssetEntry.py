"""FastAPI app: receives the upload form, writes the file to S3, and
publishes the corresponding asset entry to DynamoDB.

Run locally with:
    uvicorn assetRegister.src.publishAssetEntry:app --reload
"""

import uuid
from datetime import date

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from assetRegister.src.config import get_settings
from assetRegister.src.models import AssetEntry
from assetRegister.src.readDynamoTable import get_asset_entry, list_asset_entries
from assetRegister.src.s3_client import upload_file_to_s3
from assetRegister.src.writeItemToTable import put_asset_entry

app = FastAPI(title="Document Asset Register")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_asset_entry(
    uploader_name: str,
    file_name: str,
    upload_date: date,
    original_file_name: str,
    file_bytes: bytes,
    content_type: str,
) -> AssetEntry:
    """Orchestrates the upload: S3 write, then DynamoDB write.

    Kept as a plain function (separate from the HTTP handler) so it can be
    unit/integration tested, or driven from a script, without going through
    FastAPI.
    """
    asset_id = str(uuid.uuid4())
    s3_key = f"uploads/{asset_id}/{original_file_name}"

    upload_file_to_s3(file_bytes, s3_key, content_type)

    entry = AssetEntry(
        assetId=asset_id,
        uploaderName=uploader_name,
        fileName=file_name,
        originalFileName=original_file_name,
        uploadDate=upload_date,
        s3Bucket=get_settings().s3_bucket_name,
        s3Key=s3_key,
        contentType=content_type,
        fileSizeBytes=len(file_bytes),
    )
    put_asset_entry(entry)
    return entry


@app.post("/assets", response_model=AssetEntry)
async def upload_asset(
    uploaderName: str = Form(...),
    fileName: str = Form(...),
    uploadDate: date = Form(...),
    file: UploadFile = File(...),
) -> AssetEntry:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    return create_asset_entry(
        uploader_name=uploaderName,
        file_name=fileName,
        upload_date=uploadDate,
        original_file_name=file.filename or fileName,
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
    )


@app.get("/assets", response_model=list[AssetEntry])
def get_assets() -> list[AssetEntry]:
    return list_asset_entries()


@app.get("/assets/{asset_id}", response_model=AssetEntry)
def get_asset(asset_id: str) -> AssetEntry:
    entry = get_asset_entry(asset_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return entry
