"""Runner interfaces for isolated command execution."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ai_release_engineer.models.results import ToolResult


class CommandRunner(Protocol):
    """Executes one validated command inside an isolated workspace."""

    def run(self, *, workspace: Path, argv: Sequence[str]) -> ToolResult:
        """Run a command and return machine-readable execution evidence."""
        ...
