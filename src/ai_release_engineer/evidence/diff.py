"""Build bounded unified-diff summaries for explicit file changes."""

from collections.abc import Sequence
from difflib import unified_diff
from pathlib import Path

from ai_release_engineer.models.changes import ChangeOperation, FileChange
from ai_release_engineer.models.evidence import ChangeSummary, FileDiffSummary


class ChangeSummaryBuilder:
    """Compare explicit changes between source and disposable workspace."""

    def __init__(self, *, max_diff_chars: int = 100_000) -> None:
        if max_diff_chars < 1:
            raise ValueError("max_diff_chars must be at least 1")
        self._max_diff_chars = max_diff_chars

    def build(
        self,
        *,
        source_root: Path,
        workspace_root: Path,
        changes: Sequence[FileChange],
    ) -> ChangeSummary:
        """Build per-file counts and a bounded unified diff."""
        source = source_root.expanduser().resolve()
        workspace = workspace_root.expanduser().resolve()

        files: list[FileDiffSummary] = []
        diff_sections: list[str] = []
        total_additions = 0
        total_deletions = 0

        for change in changes:
            source_path = self._resolve_inside(source, change.path)
            workspace_path = self._resolve_inside(workspace, change.path)

            before = ""
            if change.operation is ChangeOperation.UPDATE:
                if not source_path.exists() or not source_path.is_file():
                    raise FileNotFoundError(f"source update path does not exist: {change.path}")
                before = source_path.read_text(encoding="utf-8")

            if not workspace_path.exists() or not workspace_path.is_file():
                raise FileNotFoundError(f"workspace change path does not exist: {change.path}")
            after = workspace_path.read_text(encoding="utf-8")

            diff_lines = list(
                unified_diff(
                    before.splitlines(keepends=True),
                    after.splitlines(keepends=True),
                    fromfile=f"a/{change.path}",
                    tofile=f"b/{change.path}",
                )
            )
            additions, deletions = self._count_changes(diff_lines)
            total_additions += additions
            total_deletions += deletions
            files.append(
                FileDiffSummary(
                    path=change.path,
                    operation=change.operation,
                    additions=additions,
                    deletions=deletions,
                )
            )
            diff_sections.append("".join(diff_lines))

        full_diff = "".join(diff_sections)
        truncated = len(full_diff) > self._max_diff_chars
        if truncated:
            marker = "\n...[diff truncated]"
            keep = max(0, self._max_diff_chars - len(marker))
            full_diff = f"{full_diff[:keep]}{marker}"

        return ChangeSummary(
            files=tuple(files),
            files_changed=len(files),
            additions=total_additions,
            deletions=total_deletions,
            unified_diff=full_diff,
            diff_truncated=truncated,
        )

    @staticmethod
    def _resolve_inside(root: Path, relative_path: str) -> Path:
        """Resolve one path while preserving the source/workspace boundary."""
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"change path escapes evidence root: {relative_path}") from exc
        return candidate

    @staticmethod
    def _count_changes(diff_lines: Sequence[str]) -> tuple[int, int]:
        """Count added/deleted content lines while ignoring diff headers."""
        additions = sum(
            1 for line in diff_lines if line.startswith("+") and not line.startswith("+++")
        )
        deletions = sum(
            1 for line in diff_lines if line.startswith("-") and not line.startswith("---")
        )
        return additions, deletions
