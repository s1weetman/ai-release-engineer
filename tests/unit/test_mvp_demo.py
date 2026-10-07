"""Tests for the complete Phase 1 MVP demonstration workflow."""

from collections.abc import Sequence
from pathlib import Path

from ai_release_engineer.demo import DemoScenario, get_demo_scenario, run_demo
from ai_release_engineer.models import ToolResult, ValidationStatus


DEMO_ROOT = Path(__file__).parents[2] / "examples" / "mvp_demo" / "target_repo"


class ScenarioRunner:
    """Deterministic command runner for demo orchestration tests."""

    def __init__(self, *, fail_pytest: bool = False) -> None:
        self._fail_pytest = fail_pytest
        self.commands: list[tuple[str, ...]] = []

    def run(self, *, workspace: Path, argv: Sequence[str]) -> ToolResult:
        assert workspace.exists()
        command = tuple(argv)
        self.commands.append(command)

        is_pytest = command[:3] == ("python", "-m", "pytest")
        success = not (self._fail_pytest and is_pytest)

        return ToolResult(
            tool_name=" ".join(command[:3]),
            success=success,
            exit_code=0 if success else 1,
            stdout="passed" if success else "",
            stderr="" if success else "1 failed",
            duration_ms=10,
        )


def test_success_scenario_runs_complete_mvp_flow() -> None:
    original = (DEMO_ROOT / "greeting.py").read_text(encoding="utf-8")
    runner = ScenarioRunner()

    result = run_demo(
        scenario=get_demo_scenario(DemoScenario.SUCCESS),
        source_root=DEMO_ROOT,
        runner=runner,
    )

    assert result.validation_gate_passed is True
    assert result.expected_to_pass is True
    assert result.evidence.status.value == "passed"
    assert result.evidence.change_summary.files_changed == 2
    assert result.evidence.model_call is not None
    assert result.evidence.model_call.provider == "demo"
    assert result.evidence.approvals[0].actor == "demo-user"
    assert all(
        validation.status is ValidationStatus.PASSED
        for validation in result.evidence.validations
    )
    assert len(runner.commands) == 3
    assert (DEMO_ROOT / "greeting.py").read_text(encoding="utf-8") == original


def test_failure_scenario_records_failed_validation_and_blocks_gate() -> None:
    runner = ScenarioRunner(fail_pytest=True)

    result = run_demo(
        scenario=get_demo_scenario(DemoScenario.VALIDATION_FAILURE),
        source_root=DEMO_ROOT,
        runner=runner,
    )

    assert result.validation_gate_passed is False
    assert result.expected_to_pass is False
    assert result.evidence.status.value == "failed"
    assert result.evidence.validations[0].status is ValidationStatus.FAILED
    assert result.evidence.validations[1].status is ValidationStatus.PASSED
    assert result.evidence.validations[2].status is ValidationStatus.PASSED
