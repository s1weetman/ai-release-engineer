"""Validated application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the local engine."""

    model_config = SettingsConfigDict(
        env_prefix="ARE_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    command_timeout_seconds: int = Field(default=120, ge=1, le=3_600)
    max_tool_output_chars: int = Field(default=50_000, ge=1_000, le=1_000_000)
    openai_model: str = Field(default="gpt-6-luna", min_length=1, max_length=200)
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings object per process."""
    return Settings()
