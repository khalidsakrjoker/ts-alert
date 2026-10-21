from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated process settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(
        default="development",
        pattern="^(development|test|production)$",
    )
    log_level: str = Field(
        default="info",
        pattern="^(debug|info|warn|error)$",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once and fail fast on invalid values."""

    return Settings()
