"""Small deterministic health metadata for the application foundation."""

from typing import TypedDict

from ai_release_engineer import __version__


class SystemInfo(TypedDict):
    """Public metadata returned by the application health layer."""

    name: str
    version: str
    status: str


def get_system_info() -> SystemInfo:
    """Return deterministic application identity and health metadata."""
    return {
        "name": "AI Release Engineer",
        "version": __version__,
        "status": "ok",
    }
