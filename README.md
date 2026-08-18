# document_asset_register

An app that uploads documents and stores them in an S3 bucket, and creates a
matching DynamoDB asset register entry (uploader name, file name, upload
date) from a React upload form.

## Architecture

- `frontend/` — React (Vite) upload form. Posts the file + metadata to the
  backend as `multipart/form-data`.
- `assetRegister/src/` — FastAPI backend.
  - `publishAssetEntry.py` — the app; `POST /assets` uploads the file to S3
    then writes the DynamoDB entry, `GET /assets` / `GET /assets/{id}` read
    it back.
  - `s3_client.py`, `writeItemToTable.py`, `readDynamoTable.py` — thin boto3
    wrappers around S3 and DynamoDB.
  - `models.py` — the `AssetEntry` pydantic model (shared shape for the API
    response and the DynamoDB item).
  - `config.py` — env-driven settings (region, bucket name, table name).
- `assetRegister/pipelines/provision_infra.py` — one-off script to create
  the S3 bucket and DynamoDB table (see below).
- `assetRegister/test/` — `unit`/`integration` tests run against
  [moto](https://github.com/getmoto/moto)-mocked AWS (no real AWS needed,
  no cost); `E2E` drives the real frontend + backend with Playwright.

## Setup

1. **Python backend**

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **AWS resources** — requires your own AWS credentials to be configured
   (`aws configure` or `aws sso login`). Creates an S3 bucket and a
   `document-asset-register` DynamoDB table in `eu-west-2`:

   ```bash
   python -m assetRegister.pipelines.provision_infra
   ```

   Copy the bucket/table names it prints into a `.env` file (see
   `.env.example`).

3. **Frontend**

   ```bash
   cd frontend
   npm install
   cp .env.example .env   # only needed if the backend isn't on localhost:8000
   ```

## Running it

```bash
# terminal 1
uvicorn assetRegister.src.publishAssetEntry:app --reload

# terminal 2
cd frontend && npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`), fill in the
form, and upload a document. It should appear in the table below the form,
in your S3 bucket, and as an item in the DynamoDB table.

## Tests

```bash
# unit + integration (mocked AWS, no credentials or provisioned infra needed)
pytest assetRegister/test/unit assetRegister/test/integration

# end-to-end (needs both servers above running, and real/reachable AWS)
cd frontend && npx playwright install chromium   # first time only
RUN_E2E=1 pytest assetRegister/test/E2E
```

## Continuous integration

`.github/workflows/pr-tests.yml` runs the unit tests on every pull request
into `main`. If they pass, the PR is auto-merged; if they fail, a comment is
left on the PR noting the failure.

## To do next

- Get AWS credentials working (`aws configure` or `aws sso login`).
- Run `python -m assetRegister.pipelines.provision_infra` and copy the printed
  bucket/table names into a `.env` (from `.env.example`).
- Start the backend (`uvicorn assetRegister.src.publishAssetEntry:app --reload`)
  and frontend (`npm run dev` in `frontend/`).
