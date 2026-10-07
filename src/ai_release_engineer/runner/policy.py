"""Deterministic command policy for the Phase 1 executor."""

from collections.abc import Sequence
from pathlib import PurePath


class UnsafeCommandError(ValueError):
    """Raised when a command is outside the Phase 1 allowlist."""


class CommandPolicy:
    """Allow only explicitly supported validation-tool commands."""

    _DIRECT_TOOLS = {"mypy", "pytest", "ruff"}
    _PYTHON_EXECUTABLES = {"python", "python3"}
    _PYTHON_MODULES = {"mypy", "pytest", "ruff"}

    def validate(self, argv: Sequence[str]) -> tuple[str, ...]:
        """Return a normalized command or reject it."""
        command = tuple(str(part).strip() for part in argv)
        if not command or not command[0]:
            raise UnsafeCommandError("command must not be empty")
        if any(not part for part in command):
            raise UnsafeCommandError("command arguments must not be blank")

        executable = PurePath(command[0]).name
        if executable in self._DIRECT_TOOLS:
            return command

        if executable in self._PYTHON_EXECUTABLES:
            if len(command) < 3 or command[1] != "-m":
                raise UnsafeCommandError(
                    "python commands must use an allowlisted module through '-m'"
                )
            if command[2] not in self._PYTHON_MODULES:
                raise UnsafeCommandError(f"python module is not allowlisted: {command[2]}")
            return command

        raise UnsafeCommandError(f"command is not allowlisted: {executable}")
