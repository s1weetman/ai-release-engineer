"""Docker-backed command runner for disposable execution workspaces."""

import subprocess
from pathlib import Path
from time import perf_counter
from typing import Sequence
from uuid import uuid4

from ai_release_engineer.models.results import ToolResult
from ai_release_engineer.runner.policy import CommandPolicy


class DockerUnavailableError(RuntimeError):
    """Raised when the Docker CLI is not available."""


class DockerCommandRunner:
    """Run allowlisted commands in a locked-down Docker container."""

    def __init__(
        self,
        *,
        image: str = "python:3.12-slim",
        timeout_seconds: int = 120,
        max_output_chars: int = 50_000,
        memory: str = "512m",
        cpus: str = "1.0",
        policy: CommandPolicy | None = None,
    ) -> None:
        if not image.strip():
            raise ValueError("image must not be blank")
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        if max_output_chars < 1:
            raise ValueError("max_output_chars must be at least 1")

        self._image = image.strip()
        self._timeout_seconds = timeout_seconds
        self._max_output_chars = max_output_chars
        self._memory = memory
        self._cpus = cpus
        self._policy = policy or CommandPolicy()

    def run(self, *, workspace: Path, argv: Sequence[str]) -> ToolResult:
        """Execute one allowlisted command inside a restricted container."""
        root = workspace.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise NotADirectoryError(f"workspace is not an existing directory: {root}")

        validated = self._policy.validate(argv)
        container_name = f"are-{uuid4().hex[:12]}"
        docker_command = self._docker_command(
            workspace=root,
            container_name=container_name,
            argv=validated,
        )

        started = perf_counter()
        try:
            completed = subprocess.run(
                docker_command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
            )
            elapsed_ms = int((perf_counter() - started) * 1_000)
            return ToolResult(
                tool_name=self._tool_name(validated),
                success=completed.returncode == 0,
                exit_code=completed.returncode,
                stdout=self._truncate(completed.stdout),
                stderr=self._truncate(completed.stderr),
                duration_ms=elapsed_ms,
            )
        except subprocess.TimeoutExpired as exc:
            self._force_remove(container_name)
            elapsed_ms = int((perf_counter() - started) * 1_000)
            stdout = self._coerce_output(exc.stdout)
            stderr = self._coerce_output(exc.stderr)
            timeout_message = f"command timed out after {self._timeout_seconds} seconds"
            combined_stderr = f"{stderr}\n{timeout_message}".strip()
            return ToolResult(
                tool_name=self._tool_name(validated),
                success=False,
                exit_code=None,
                stdout=self._truncate(stdout),
                stderr=self._truncate(combined_stderr),
                duration_ms=elapsed_ms,
            )
        except FileNotFoundError as exc:
            raise DockerUnavailableError("Docker CLI is not available") from exc

    def _docker_command(
        self,
        *,
        workspace: Path,
        container_name: str,
        argv: tuple[str, ...],
    ) -> list[str]:
        """Build the deterministic Docker command line."""
        return [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "256",
            "--memory",
            self._memory,
            "--cpus",
            self._cpus,
            "--workdir",
            "/workspace",
            "--mount",
            f"type=bind,src={workspace},dst=/workspace,rw",
            self._image,
            *argv,
        ]

    def _force_remove(self, container_name: str) -> None:
        """Best-effort cleanup when the Docker CLI call times out."""
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _truncate(self, value: str) -> str:
        """Cap tool output so one command cannot create unbounded evidence."""
        if len(value) <= self._max_output_chars:
            return value

        marker = "\n...[truncated]"
        keep = max(0, self._max_output_chars - len(marker))
        return f"{value[:keep]}{marker}"

    @staticmethod
    def _coerce_output(value: str | bytes | None) -> str:
        """Normalize subprocess timeout output."""
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    @staticmethod
    def _tool_name(argv: tuple[str, ...]) -> str:
        """Create a short audit-friendly tool label."""
        return " ".join(argv[:3])
