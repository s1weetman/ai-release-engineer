"""Tests for normalized validation evidence and deterministic gating."""

from collections.abc import Sequence

import pytest

from ai_release_engineer.models import ToolResult, ValidationKind, ValidationStatus
from ai_release_engineer.validation import (
    ValidationGate,
    ValidationGateError,
    ValidationPipeline,
    ValidationSpec,
)


class FakeValidationExecutor:
    """Return deterministic tool results in the order requested."""

    def __init__(self, results: Sequence[ToolResult]) -> None:
        self._results = list(results)
        self.commands: list[tuple[str, ...]] = []

    def run_command(self, argv: Sequence[str]) -> ToolResult:
        self.commands.append(tuple(argv))
        if not self._results:
            raise AssertionError("fake executor ran out of tool results")
        return self._results.pop(0)


def make_tool(*, name: str, success: bool, stdout: str = "") -> ToolResult:
    return ToolResult(
        tool_name=name,
        success=success,
        exit_code=0 if success else 1,
        stdout=stdout,
        stderr="" if success else "failure details",
        duration_ms=10,
    )


def test_pipeline_normalizes_test_lint_type_and_security_results() -> None:
    executor = FakeValidationExecutor(
        (
            make_tool(name="pytest", success=True, stdout="55 passed"),
            make_tool(name="ruff", success=True, stdout="All checks passed"),
            make_tool(name="mypy", success=True, stdout="Success"),
            make_tool(name="security", success=True, stdout="No findings"),
        )
    )
    specs = (
        ValidationSpec(
            kind=ValidationKind.TEST,
            name="unit-tests",
            command=("python", "-m", "pytest"),
        ),
        ValidationSpec(
            kind=ValidationKind.LINT,
            name="ruff-lint",
            command=("python", "-m", "ruff", "check", "."),
        ),
        ValidationSpec(
            kind=ValidationKind.TYPE,
            name="mypy",
            command=("python", "-m", "mypy", "src", "tests"),
        ),
        ValidationSpec(
            kind=ValidationKind.SECURITY,
            name="security-scan",
            command=("security-scan",),
        ),
    )

    run = ValidationPipeline().run(executor=executor, specs=specs)

    assert [result.kind for result in run.validations] == [
        ValidationKind.TEST,
        ValidationKind.LINT,
        ValidationKind.TYPE,
        ValidationKind.SECURITY,
    ]
    assert all(result.status is ValidationStatus.PASSED for result in run.validations)
    assert len(run.tool_results) == 4
    assert ValidationGate.passed(run.validations) is True


def test_failed_validation_blocks_success() -> None:
    executor = FakeValidationExecutor(
        (
            make_tool(name="pytest", success=True),
            make_tool(name="security", success=False),
        )
    )
    specs = (
        ValidationSpec(
            kind=ValidationKind.TEST,
            name="unit-tests",
            command=("pytest",),
        ),
        ValidationSpec(
            kind=ValidationKind.SECURITY,
            name="security-scan",
            command=("security-scan",),
        ),
    )

    run = ValidationPipeline().run(executor=executor, specs=specs)

    assert run.validations[1].status is ValidationStatus.FAILED
    assert ValidationGate.passed(run.validations) is False
    with pytest.raises(ValidationGateError, match="security:security-scan=failed"):
        ValidationGate.require_passed(run.validations)


def test_skipped_or_missing_validation_does_not_pass_gate() -> None:
    skipped = (
        run := ValidationPipeline().run(
            executor=FakeValidationExecutor((make_tool(name="pytest", success=True),)),
            specs=(
                ValidationSpec(
                    kind=ValidationKind.TEST,
                    name="unit-tests",
                    command=("pytest",),
                ),
            ),
        )
    ).validations
    assert run.validations[0].status is ValidationStatus.PASSED
    assert ValidationGate.passed(skipped) is True

    from ai_release_engineer.models import ValidationResult

    skipped_result = ValidationResult(
        kind=ValidationKind.SECURITY,
        name="security-scan",
        status=ValidationStatus.SKIPPED,
        details="not configured",
        duration_ms=0,
    )

    assert ValidationGate.passed((skipped_result,)) is False
    assert ValidationGate.passed(()) is False
