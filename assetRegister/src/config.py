"""Runtime configuration for the asset register backend.

Values are read from environment variables (optionally via a `.env` file in
the repo root during local development). Defaults match the names the
provisioning script (`assetRegister/pipelines/provision_infra.py`) creates.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    aws_region: str = "eu-west-2"
    s3_bucket_name: str = "document-asset-register"
    dynamodb_table_name: str = "document-asset-register"

    # Origins allowed to call the API from a browser (the local Vite dev server).
    cors_allow_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
