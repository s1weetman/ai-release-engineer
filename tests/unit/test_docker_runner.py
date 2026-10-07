"""Tests for Docker-backed command execution."""

import subprocess
from pathlib import Path
from typing import Any

import pytest

from ai_release_engineer.runner import DockerCommandRunner


def test_docker_runner_builds_restricted_command_and_captures_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, Any] = {}

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["command"] = command
        observed["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="x" * 2_000,
            stderr="warning",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    runner = DockerCommandRunner(
        image="python:test",
        timeout_seconds=30,
        max_output_chars=1_000,
    )
    result = runner.run(
        workspace=tmp_path,
        argv=("python", "-m", "pytest"),
    )

    command = observed["command"]
    assert isinstance(command, list)
    assert "--network" in command
    assert "none" in command
    assert "--cap-drop" in command
    assert "ALL" in command
    assert "no-new-privileges" in command
    assert "python:test" in command
    assert command[-3:] == ["python", "-m", "pytest"]

    assert result.success is True
    assert result.exit_code == 0
    assert len(result.stdout) <= 1_000
    assert result.stdout.endswith("...[truncated]")
    assert result.stderr == "warning"
    assert result.duration_ms >= 0


def test_docker_runner_returns_timeout_evidence_and_forces_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[:2] == ["docker", "run"]:
            raise subprocess.TimeoutExpired(
                cmd=command,
                timeout=1,
                output="partial stdout",
                stderr="partial stderr",
            )
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    runner = DockerCommandRunner(timeout_seconds=1)
    result = runner.run(
        workspace=tmp_path,
        argv=("pytest",),
    )

    assert result.success is False
    assert result.exit_code is None
    assert result.stdout == "partial stdout"
    assert "partial stderr" in result.stderr
    assert "timed out after 1 seconds" in result.stderr
    assert any(command[:3] == ["docker", "rm", "-f"] for command in calls)
