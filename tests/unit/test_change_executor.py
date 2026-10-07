"""Tests for disposable workspaces and bounded file changes."""

from collections.abc import Sequence
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_release_engineer.models import ChangeOperation, FileChange
from ai_release_engineer.models.results import ToolResult
from ai_release_engineer.runner import (
    FileChangeConflictError,
    IsolatedChangeExecutor,
    UnsafeWorkspacePathError,
    WorkspaceNotReadyError,
)


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "sample_repo"


class FakeRunner:
    """Deterministic runner used to test executor orchestration."""

    def __init__(self) -> None:
        self.workspace: Path | None = None
        self.argv: tuple[str, ...] | None = None

    def run(self, *, workspace: Path, argv: Sequence[str]) -> ToolResult:
        self.workspace = workspace
        self.argv = tuple(argv)
        return ToolResult(
            tool_name="fake",
            success=True,
            exit_code=0,
            stdout="ok",
            stderr="",
            duration_ms=1,
        )


def test_executor_updates_disposable_copy_without_touching_source() -> None:
    source_content = (FIXTURE_ROOT / "src" / "app.py").read_text(encoding="utf-8")
    runner = FakeRunner()

    with IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner) as executor:
        executor.apply_changes(
            (
                FileChange(
                    operation=ChangeOperation.UPDATE,
                    path="src/app.py",
                    content='def greet(name: str) -> str:\n    return f"Hi, {name}!"\n',
                ),
            )
        )

        workspace_content = (executor.workspace_root / "src" / "app.py").read_text(encoding="utf-8")
        assert 'return f"Hi, {name}!"' in workspace_content

    assert (FIXTURE_ROOT / "src" / "app.py").read_text(encoding="utf-8") == source_content


def test_executor_creates_new_file_under_existing_directory() -> None:
    runner = FakeRunner()

    with IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner) as executor:
        created = executor.apply_changes(
            (
                FileChange(
                    operation=ChangeOperation.CREATE,
                    path="src/new_module.py",
                    content="VALUE = 1\n",
                ),
            )
        )

        assert created[0].read_text(encoding="utf-8") == "VALUE = 1\n"


def test_executor_rejects_conflicting_file_operations() -> None:
    runner = FakeRunner()

    with IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner) as executor:
        with pytest.raises(FileChangeConflictError, match="already exists"):
            executor.apply_changes(
                (
                    FileChange(
                        operation=ChangeOperation.CREATE,
                        path="src/app.py",
                        content="replacement",
                    ),
                )
            )

        with pytest.raises(FileChangeConflictError, match="not an existing file"):
            executor.apply_changes(
                (
                    FileChange(
                        operation=ChangeOperation.UPDATE,
                        path="src/missing.py",
                        content="replacement",
                    ),
                )
            )


def test_executor_rejects_create_under_missing_directory() -> None:
    runner = FakeRunner()

    with (
        IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner) as executor,
        pytest.raises(FileChangeConflictError, match="parent directory"),
    ):
        executor.apply_changes(
                (
                    FileChange(
                        operation=ChangeOperation.CREATE,
                        path="missing/new.py",
                        content="VALUE = 1\n",
                    ),
                )
            )


@pytest.mark.parametrize("path", ("../outside.py", "/absolute.py", "src/../../outside.py"))
def test_file_change_contract_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(ValidationError):
        FileChange(
            operation=ChangeOperation.CREATE,
            path=path,
            content="unsafe",
        )


def test_executor_deletes_disposable_workspace_after_context_exit() -> None:
    runner = FakeRunner()
    executor = IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner)

    with executor:
        root = executor.workspace_root
        assert root.exists()

    assert not root.exists()
    with pytest.raises(WorkspaceNotReadyError):
        _ = executor.workspace_root


def test_executor_passes_active_workspace_to_runner() -> None:
    runner = FakeRunner()

    with IsolatedChangeExecutor(source_root=FIXTURE_ROOT, runner=runner) as executor:
        result = executor.run_command(("python", "-m", "pytest"))
        active_root = executor.workspace_root

        assert result.success is True
        assert runner.workspace == active_root
        assert runner.argv == ("python", "-m", "pytest")


def test_executor_rejects_write_through_symlink_outside_workspace(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (source / "link.txt").symlink_to(outside)

    runner = FakeRunner()
    with (
        IsolatedChangeExecutor(source_root=source, runner=runner) as executor,
        pytest.raises(UnsafeWorkspacePathError, match="escapes disposable workspace"),
    ):
        executor.apply_changes(
                (
                    FileChange(
                        operation=ChangeOperation.UPDATE,
                        path="link.txt",
                        content="changed",
                    ),
                )
            )

    assert outside.read_text(encoding="utf-8") == "secret"
