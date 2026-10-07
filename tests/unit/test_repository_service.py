"""Tests for bounded local repository analysis."""

from pathlib import Path

import pytest

from ai_release_engineer.repository import RepositoryService, UnsafeRepositoryPathError


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "sample_repo"


def test_list_tree_returns_deterministic_repository_entries() -> None:
    service = RepositoryService(FIXTURE_ROOT)

    entries = service.list_tree()
    paths = [entry.path for entry in entries]

    assert "README.md" in paths
    assert "src" in paths
    assert "src/app.py" in paths
    assert "config/settings.txt" in paths


def test_read_text_reads_file_inside_repository() -> None:
    service = RepositoryService(FIXTURE_ROOT)

    content = service.read_text("src/app.py")

    assert 'return f"Hello, {name}!"' in content


@pytest.mark.parametrize(
    "unsafe_path",
    (
        "../outside.txt",
        "../../etc/passwd",
        "/etc/passwd",
    ),
)
def test_read_text_rejects_path_escape(unsafe_path: str) -> None:
    service = RepositoryService(FIXTURE_ROOT)

    with pytest.raises(UnsafeRepositoryPathError):
        service.read_text(unsafe_path)


def test_search_text_returns_file_and_line_number() -> None:
    service = RepositoryService(FIXTURE_ROOT)

    matches = service.search_text("feature_flag")

    assert len(matches) == 1
    assert matches[0].path == "config/settings.txt"
    assert matches[0].line_number == 2
    assert matches[0].line == "feature_flag=enabled"


def test_search_text_rejects_empty_query() -> None:
    service = RepositoryService(FIXTURE_ROOT)

    with pytest.raises(ValueError, match="search query must not be empty"):
        service.search_text("")


def test_metadata_reports_non_git_fixture() -> None:
    service = RepositoryService(FIXTURE_ROOT)

    metadata = service.metadata()

    assert metadata.is_git_repository is False
    assert metadata.branch is None
    assert metadata.commit_sha is None


def test_repository_root_must_exist(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        RepositoryService(tmp_path / "missing")
