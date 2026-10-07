"""End-to-end local MVP demo orchestration."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from ai_release_engineer.demo.provider import DemoPlanningProvider
from ai_release_engineer.demo.scenarios import DemoScenarioDefinition
from ai_release_engineer.evidence import EvidenceBuilder
from ai_release_engineer.models import (
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStage,
    EvidenceBundle,
    ValidationKind,
)
from ai_release_engineer.planning import PlanningAgent
from ai_release_engineer.repository import RepositoryService
from ai_release_engineer.runner import CommandRunner, IsolatedChangeExecutor
from ai_release_engineer.validation import ValidationGate, ValidationPipeline, ValidationSpec


@dataclass(frozen=True, slots=True)
class DemoResult:
    """Complete result of one local MVP demonstration."""

    evidence: EvidenceBundle
    validation_gate_passed: bool
    expected_to_pass: bool


_VALIDATIONS = (
    ValidationSpec(
        kind=ValidationKind.TEST,
        name="pytest",
        command=("python", "-m", "pytest", "-q"),
    ),
    ValidationSpec(
        kind=ValidationKind.LINT,
        name="ruff",
        command=("python", "-m", "ruff", "check", "."),
    ),
    ValidationSpec(
        kind=ValidationKind.TYPE,
        name="mypy",
        command=("python", "-m", "mypy", "greeting.py", "tests"),
    ),
)


def run_demo(
    *,
    scenario: DemoScenarioDefinition,
    source_root: Path,
    runner: CommandRunner,
) -> DemoResult:
    """Run analysis, planning, approval, change, validation, and evidence collection."""
    repository = RepositoryService(source_root)
    provider = DemoPlanningProvider(scenario.plan)
    planning_result = PlanningAgent(
        repository=repository,
        provider=provider,
    ).create_plan(scenario.request)

    run_id = uuid4()
    plan_approval = ApprovalRecord(
        run_id=run_id,
        stage=ApprovalStage.PLAN,
        decision=ApprovalDecision.APPROVED,
        actor="demo-user",
        comment="Deterministic MVP demo plan approval.",
    )

    with IsolatedChangeExecutor(source_root=source_root, runner=runner) as executor:
        executor.apply_changes(scenario.changes)
        validation_run = ValidationPipeline().run(
            executor=executor,
            specs=_VALIDATIONS,
        )
        evidence = EvidenceBuilder().build(
            run_id=run_id,
            request=scenario.request,
            plan=planning_result.plan,
            source_root=source_root,
            workspace_root=executor.workspace_root,
            changes=scenario.changes,
            validations=validation_run.validations,
            tool_results=validation_run.tool_results,
            provider_metadata=planning_result.provider,
            approvals=(plan_approval,),
        )

    return DemoResult(
        evidence=evidence,
        validation_gate_passed=ValidationGate.passed(evidence.validations),
        expected_to_pass=scenario.expected_to_pass,
    )
