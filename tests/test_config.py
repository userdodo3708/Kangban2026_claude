"""Pydantic Settings .env loading tests."""

from __future__ import annotations

from pathlib import Path

from app.core.config import Settings


def test_settings_load_from_env_file(tmp_path: Path, monkeypatch) -> None:
    for key in (
        "APP_NAME",
        "APP_VERSION",
        "APP_ENV",
        "DEBUG",
        "LOG_LEVEL",
        "DATABASE_URL",
        "REDIS_URL",
        "DEEPSEEK_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_NAME=test-konban",
                "APP_VERSION=9.9.9",
                "APP_ENV=test",
                "DEBUG=true",
                "LOG_LEVEL=DEBUG",
                "DATABASE_URL=postgresql+psycopg2://localhost:5432/test",
                "REDIS_URL=redis://localhost:6379/1",
                "DEEPSEEK_API_KEY=test-only",
                "UNKNOWN_KEY=ignored",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_name == "test-konban"
    assert settings.app_version == "9.9.9"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql+psycopg2://localhost:5432/test"
    assert settings.redis_url == "redis://localhost:6379/1"
    assert settings.deepseek_api_key is not None
    assert settings.deepseek_api_key.get_secret_value() == "test-only"
