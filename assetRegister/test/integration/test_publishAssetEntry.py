import io

from fastapi.testclient import TestClient

from assetRegister.src.config import get_settings
from assetRegister.src.publishAssetEntry import app


def test_upload_asset_stores_file_in_s3_and_entry_in_dynamodb(moto_aws):
    client = TestClient(app)

    response = client.post(
        "/assets",
        data={
            "uploaderName": "Gurpreet Singh",
            "fileName": "Invoice",
            "uploadDate": "2026-08-18",
        },
        files={"file": ("invoice.pdf", io.BytesIO(b"%PDF-1.4 fake pdf bytes"), "application/pdf")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["uploaderName"] == "Gurpreet Singh"
    assert body["originalFileName"] == "invoice.pdf"
    assert body["s3Key"].endswith("invoice.pdf")

    # File actually landed in S3.
    import boto3

    settings = get_settings()
    s3 = boto3.client("s3", region_name=settings.aws_region)
    obj = s3.get_object(Bucket=settings.s3_bucket_name, Key=body["s3Key"])
    assert obj["Body"].read() == b"%PDF-1.4 fake pdf bytes"

    # Entry is retrievable through the API.
    get_response = client.get(f"/assets/{body['assetId']}")
    assert get_response.status_code == 200
    assert get_response.json()["assetId"] == body["assetId"]

    list_response = client.get("/assets")
    assert list_response.status_code == 200
    assert any(a["assetId"] == body["assetId"] for a in list_response.json())


def test_upload_asset_rejects_empty_file(moto_aws):
    client = TestClient(app)

    response = client.post(
        "/assets",
        data={
            "uploaderName": "Gurpreet Singh",
            "fileName": "Invoice",
            "uploadDate": "2026-08-18",
        },
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )

    assert response.status_code == 400


def test_get_unknown_asset_returns_404(moto_aws):
    client = TestClient(app)

    response = client.get("/assets/does-not-exist")

    assert response.status_code == 404
