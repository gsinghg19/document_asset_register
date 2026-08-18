"""End-to-end test driving the real React frontend against the real backend.

Unlike the unit/integration tests, this does NOT mock AWS — it exercises the
actual browser form, the actual FastAPI backend, and (unless you point it at
a test bucket/table via env vars) your real S3 bucket and DynamoDB table.

Requires, running beforehand:
  - the backend:  uvicorn assetRegister.src.publishAssetEntry:app
  - the frontend: npm run dev --prefix frontend

Skipped by default (and in CI) unless RUN_E2E=1 is set, since it needs both
servers up and real/reachable AWS resources.

Usage:
  RUN_E2E=1 pytest assetRegister/test/E2E
"""

import os
import tempfile

import pytest
from playwright.sync_api import expect, sync_playwright

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") != "1",
    reason="set RUN_E2E=1 to run against live frontend/backend servers",
)


def test_submitting_the_form_uploads_a_document():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as tmp:
        tmp.write("test document contents")
        tmp_path = tmp.name

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(FRONTEND_URL)

        page.get_by_label("Uploader name").fill("Gurpreet Singh")
        page.get_by_label("File name").fill("E2E test document")
        page.set_input_files('input[type="file"]', tmp_path)
        page.get_by_role("button", name="Upload").click()

        expect(page.get_by_text("E2E test document")).to_be_visible(timeout=10_000)

        browser.close()
