"""Tests for validated runtime configuration."""

import pytest
from pydantic import ValidationError

from ai_release_engineer.config import Settings


def test_settings_have_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.command_timeout_seconds == 120
    assert settings.max_tool_output_chars == 50_000


def test_settings_load_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARE_ENVIRONMENT", "test")
    monkeypatch.setenv("ARE_COMMAND_TIMEOUT_SECONDS", "30")

    settings = Settings(_env_file=None)

    assert settings.environment == "test"
    assert settings.command_timeout_seconds == 30


def test_invalid_timeout_fails_clearly() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, command_timeout_seconds=0)
