"""Tests for deterministic command allowlisting."""

import pytest

from ai_release_engineer.runner import CommandPolicy, UnsafeCommandError


@pytest.mark.parametrize(
    "argv",
    (
        ("pytest",),
        ("ruff", "check", "."),
        ("mypy", "src"),
        ("python", "-m", "pytest"),
        ("python3", "-m", "ruff", "check", "."),
    ),
)
def test_command_policy_allows_supported_validation_tools(argv: tuple[str, ...]) -> None:
    assert CommandPolicy().validate(argv) == argv


@pytest.mark.parametrize(
    "argv",
    (
        ("bash", "-c", "rm -rf /"),
        ("sh", "-c", "echo unsafe"),
        ("python", "-c", "print('unsafe')"),
        ("python", "-m", "http.server"),
        ("curl", "https://example.com"),
    ),
)
def test_command_policy_rejects_unsafe_commands(argv: tuple[str, ...]) -> None:
    with pytest.raises(UnsafeCommandError):
        CommandPolicy().validate(argv)


def test_command_policy_rejects_empty_command() -> None:
    with pytest.raises(UnsafeCommandError):
        CommandPolicy().validate(())
