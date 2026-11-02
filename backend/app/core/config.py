"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings populated from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
    )

    app_name: str = "AEGIS Financial Risk Intelligence API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    environment: str = "production"
    auth_expose_reset_token: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
