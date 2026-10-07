"""Disposable repository workspace with bounded file mutations."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from types import TracebackType

from ai_release_engineer.models.changes import ChangeOperation, FileChange


class WorkspaceNotReadyError(RuntimeError):
    """Raised when a disposable workspace is used outside its context."""


class UnsafeWorkspacePathError(ValueError):
    """Raised when a mutation escapes the disposable workspace."""


class FileChangeConflictError(ValueError):
    """Raised when a requested create/update conflicts with workspace state."""


class DisposableWorkspace:
    """Copy a repository into a temporary directory and destroy it afterward."""

    _IGNORED_NAMES = (
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
    )

    def __init__(self, source_root: Path) -> None:
        resolved = source_root.expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"source repository does not exist: {resolved}")
        if not resolved.is_dir():
            raise NotADirectoryError(f"source repository is not a directory: {resolved}")

        self._source_root = resolved
        self._temp_dir: TemporaryDirectory[str] | None = None
        self._root: Path | None = None

    def __enter__(self) -> "DisposableWorkspace":
        self._temp_dir = TemporaryDirectory(prefix="ai-release-engineer-")
        root = Path(self._temp_dir.name) / "repository"
        shutil.copytree(
            self._source_root,
            root,
            ignore=shutil.ignore_patterns(*self._IGNORED_NAMES),
            symlinks=True,
        )
        self._root = root.resolve()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
        self._root = None
        self._temp_dir = None

    @property
    def root(self) -> Path:
        """Return the active disposable workspace root."""
        if self._root is None:
            raise WorkspaceNotReadyError("workspace is not active")
        return self._root

    def apply_change(self, change: FileChange) -> Path:
        """Apply one validated create/update operation inside the workspace."""
        target = self._resolve_path(change.path)
        parent = target.parent
        if not parent.exists() or not parent.is_dir():
            raise FileChangeConflictError(
                f"parent directory does not exist in workspace: {change.path}"
            )

        if change.operation is ChangeOperation.CREATE:
            if target.exists():
                raise FileChangeConflictError(f"create target already exists: {change.path}")
        elif change.operation is ChangeOperation.UPDATE and (
            not target.exists() or not target.is_file()
        ):
            message = f"update target is not an existing file: {change.path}"
            raise FileChangeConflictError(message)

        target.write_text(change.content, encoding="utf-8")
        return target

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve a path and enforce the workspace boundary again."""
        root = self.root
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise UnsafeWorkspacePathError(
                f"path escapes disposable workspace: {relative_path}"
            ) from exc
        return candidate
