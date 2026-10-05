"""Tests for the base application health metadata."""

from ai_release_engineer import __version__
from ai_release_engineer.health import get_system_info


def test_system_info_reports_application_identity() -> None:
    info = get_system_info()

    assert info["name"] == "AI Release Engineer"
    assert info["version"] == __version__
    assert info["status"] == "ok"


def test_version_is_semantic_version_shape() -> None:
    major, minor, patch = __version__.split(".")

    assert major.isdigit()
    assert minor.isdigit()
    assert patch.isdigit()
