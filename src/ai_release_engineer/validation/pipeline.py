"""Normalize command execution into typed validation evidence."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from ai_release_engineer.models.results import (
    ToolResult,
    ValidationKind,
    ValidationResult,
    ValidationStatus,
)


class ValidationExecutor(Protocol):
    """Executor surface required by the validation pipeline."""

    def run_command(self, argv: Sequence[str]) -> ToolResult:
        """Execute one validation command."""
        ...


@dataclass(frozen=True, slots=True)
class ValidationSpec:
    """One named validation command and its evidence category."""

    kind: ValidationKind
    name: str
    command: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationRun:
    """Raw tool evidence and normalized validation results."""

    tool_results: tuple[ToolResult, ...]
    validations: tuple[ValidationResult, ...]


class ValidationPipeline:
    """Execute validation specifications and normalize their results."""

    def run(
        self,
        *,
        executor: ValidationExecutor,
        specs: Sequence[ValidationSpec],
    ) -> ValidationRun:
        """Run every validation spec and retain both raw and normalized evidence."""
        tool_results: list[ToolResult] = []
        validations: list[ValidationResult] = []

        for spec in specs:
            if not spec.name.strip():
                raise ValueError("validation name must not be blank")
            if not spec.command:
                raise ValueError(f"validation command must not be empty: {spec.name}")

            tool = executor.run_command(spec.command)
            tool_results.append(tool)
            validations.append(
                ValidationResult(
                    kind=spec.kind,
                    name=spec.name,
                    status=ValidationStatus.PASSED if tool.success else ValidationStatus.FAILED,
                    command=spec.command,
                    details=self._details(tool),
                    duration_ms=tool.duration_ms,
                )
            )

        return ValidationRun(
            tool_results=tuple(tool_results),
            validations=tuple(validations),
        )

    @staticmethod
    def _details(tool: ToolResult) -> str:
        """Combine bounded stdout/stderr into reviewable evidence."""
        pieces = []
        if tool.stdout:
            pieces.append(tool.stdout)
        if tool.stderr:
            pieces.append(tool.stderr)
        if not pieces:
            return f"exit_code={tool.exit_code}"
        return "\n".join(pieces)
