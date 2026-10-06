"""Read-only repository analysis with strict workspace boundaries."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


class UnsafeRepositoryPathError(ValueError):
    """Raised when a requested path escapes the configured repository root."""


@dataclass(frozen=True, slots=True)
class RepositoryTreeEntry:
    """One file or directory discovered inside the repository."""

    path: str
    is_directory: bool


@dataclass(frozen=True, slots=True)
class FileMatch:
    """One text-search hit inside a repository file."""

    path: str
    line_number: int
    line: str


@dataclass(frozen=True, slots=True)
class RepositoryMetadata:
    """Basic local Git repository metadata."""

    root: str
    branch: str | None
    commit_sha: str | None
    is_git_repository: bool


class RepositoryService:
    """Provides bounded, read-only inspection of one local repository."""

    def __init__(self, root: Path) -> None:
        resolved = root.expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"repository root does not exist: {resolved}")
        if not resolved.is_dir():
            raise NotADirectoryError(f"repository root is not a directory: {resolved}")
        self._root = resolved

    @property
    def root(self) -> Path:
        """Return the canonical repository root."""
        return self._root

    def _resolve_relative_path(self, relative_path: str) -> Path:
        """Resolve a repository-relative path and reject workspace escapes."""
        if not relative_path:
            raise UnsafeRepositoryPathError("repository path must not be empty")

        candidate = (self._root / relative_path).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise UnsafeRepositoryPathError(
                f"path escapes repository root: {relative_path}"
            ) from exc
        return candidate

    def list_tree(self) -> tuple[RepositoryTreeEntry, ...]:
        """Return a deterministic recursive tree, excluding the .git directory."""
        entries: list[RepositoryTreeEntry] = []
        for path in sorted(self._root.rglob("*")):
            relative = path.relative_to(self._root)
            if ".git" in relative.parts:
                continue
            entries.append(
                RepositoryTreeEntry(
                    path=relative.as_posix(),
                    is_directory=path.is_dir(),
                )
            )
        return tuple(entries)

    def read_text(self, relative_path: str) -> str:
        """Read a UTF-8 text file that is inside the repository boundary."""
        path = self._resolve_relative_path(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"repository file does not exist: {relative_path}")
        if not path.is_file():
            raise IsADirectoryError(f"repository path is not a file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def search_text(self, query: str) -> tuple[FileMatch, ...]:
        """Search UTF-8 text files for a literal string."""
        if not query:
            raise ValueError("search query must not be empty")

        matches: list[FileMatch] = []
        for entry in self.list_tree():
            if entry.is_directory:
                continue
            path = self._resolve_relative_path(entry.path)
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query in line:
                    matches.append(
                        FileMatch(
                            path=entry.path,
                            line_number=line_number,
                            line=line,
                        )
                    )
        return tuple(matches)

    def metadata(self) -> RepositoryMetadata:
        """Return basic Git metadata without mutating the repository."""
        git_dir = self._root / ".git"
        if not git_dir.exists():
            return RepositoryMetadata(
                root=str(self._root),
                branch=None,
                commit_sha=None,
                is_git_repository=False,
            )

        branch = self._git_value("rev-parse", "--abbrev-ref", "HEAD")
        commit_sha = self._git_value("rev-parse", "HEAD")
        return RepositoryMetadata(
            root=str(self._root),
            branch=branch,
            commit_sha=commit_sha,
            is_git_repository=True,
        )

    def _git_value(self, *args: str) -> str | None:
        """Run one read-only Git command and return its stripped output."""
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self._root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return None
        value = completed.stdout.strip()
        return value or None
