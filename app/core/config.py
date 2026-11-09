"""Application settings loaded from the project-root .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration; secrets come from environment/.env only."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "konban"
    app_version: str = "0.1.0"
    app_env: str = "local"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://localhost:5432/konban"
    redis_url: str = "redis://localhost:6379/0"

    deepseek_api_key: SecretStr | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
