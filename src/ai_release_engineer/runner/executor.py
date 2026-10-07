"""High-level isolated change executor."""

from collections.abc import Iterable, Sequence
from pathlib import Path
from types import TracebackType

from ai_release_engineer.models.changes import FileChange
from ai_release_engineer.models.results import ToolResult
from ai_release_engineer.runner.base import CommandRunner
from ai_release_engineer.runner.workspace import DisposableWorkspace


class IsolatedChangeExecutor:
    """Apply bounded file changes and run validation commands in a disposable workspace."""

    def __init__(self, *, source_root: Path, runner: CommandRunner) -> None:
        self._workspace = DisposableWorkspace(source_root)
        self._runner = runner

    def __enter__(self) -> "IsolatedChangeExecutor":
        self._workspace.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._workspace.__exit__(exc_type, exc_value, traceback)

    @property
    def workspace_root(self) -> Path:
        """Return the active disposable workspace path."""
        return self._workspace.root

    def apply_changes(self, changes: Iterable[FileChange]) -> tuple[Path, ...]:
        """Apply a sequence of bounded file changes."""
        return tuple(self._workspace.apply_change(change) for change in changes)

    def run_command(self, argv: Sequence[str]) -> ToolResult:
        """Run one command using the configured isolated command runner."""
        return self._runner.run(workspace=self.workspace_root, argv=argv)
