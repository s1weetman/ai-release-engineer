"""Baseline tests for the MVP demo target."""

from greeting import greet


def test_default_greeting() -> None:
    assert greet("Steve") == "Hello, Steve!"
