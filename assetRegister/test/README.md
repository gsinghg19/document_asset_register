# Tests

## Layout

- `unit/` — tests individual functions in isolation:
  - `test_models.py` — `AssetEntry` pydantic validation and DynamoDB
    item round-tripping.
  - `test_writeItemToTable.py` — `put_asset_entry`.
  - `test_readDynamoTable.py` — `get_asset_entry`, `list_asset_entries`.
- `integration/` — `test_publishAssetEntry.py` drives the FastAPI app
  through `TestClient`, exercising the full `POST /assets` → S3 upload →
  DynamoDB write → `GET /assets` / `GET /assets/{id}` flow.
- `E2E/` — `test_upload_flow.py` drives the real React frontend in a
  browser (via Playwright) against a running backend.
- `conftest.py` — shared `moto_aws` fixture used by `unit` and
  `integration`. It spins up a fake S3 bucket and DynamoDB table with
  [moto](https://github.com/getmoto/moto), points `Settings` at them, and
  tears them down after the test. No AWS credentials, network access, or
  cost required.

## Running

```bash
# unit + integration — mocked AWS, no credentials or provisioned infra needed
pytest assetRegister/test/unit assetRegister/test/integration

# just one layer
pytest assetRegister/test/unit
pytest assetRegister/test/integration
```

### E2E

Unlike the other two, E2E does **not** mock AWS — it exercises the real
frontend, the real backend, and (unless pointed at test resources) your
real S3 bucket and DynamoDB table. It's skipped by default and in CI.

```bash
# terminal 1
uvicorn assetRegister.src.publishAssetEntry:app --reload

# terminal 2
cd frontend && npm run dev

# terminal 3, first time only
cd frontend && npx playwright install chromium

# terminal 3
RUN_E2E=1 pytest assetRegister/test/E2E
```

## CI

`.github/workflows/pr-tests.yml` runs `unit/` on every pull request into
`main` and is a required check — a PR can't merge until it passes. It does
not run `integration/` or `E2E/` yet; see the repo's top-level README
"To do next" for follow-ups.
