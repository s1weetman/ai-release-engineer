"""Tests for P1-T2 domain model contracts."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from ai_release_engineer.models import (
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStage,
    ChangeRequest,
    ImplementationPlan,
    PlanStep,
    ToolResult,
    ValidationResult,
    ValidationStatus,
    WorkflowRun,
    WorkflowState,
)


def make_request() -> ChangeRequest:
    return ChangeRequest(
        repository="s1weetman/ai-release-engineer",
        title="Add repository scanner",
        description="Add a safe repository scanner for the local MVP.",
        requested_by="steve",
    )


def test_change_request_accepts_bounded_repository_request() -> None:
    request = make_request()

    assert request.repository == "s1weetman/ai-release-engineer"
    assert request.title == "Add repository scanner"


@pytest.mark.parametrize("repository", ["missing-slash", "/repo", "owner/", "a/b/c"])
def test_change_request_rejects_invalid_repository_format(repository: str) -> None:
    with pytest.raises(ValidationError):
        ChangeRequest(
            repository=repository,
            title="Valid title",
            description="This description is long enough.",
            requested_by="steve",
        )


def test_workflow_run_starts_received() -> None:
    run = WorkflowRun(request=make_request())

    assert run.state is WorkflowState.RECEIVED


def test_plan_requires_ordered_unique_steps() -> None:
    with pytest.raises(ValidationError):
        ImplementationPlan(
            summary="Make the requested change safely.",
            steps=(
                PlanStep(order=2, description="Second step"),
                PlanStep(order=1, description="First step"),
            ),
        )


def test_plan_rejects_path_traversal() -> None:
    with pytest.raises(ValidationError):
        PlanStep(order=1, description="Unsafe edit", paths=("../secrets.txt",))


def test_tool_and_validation_results_are_typed() -> None:
    tool = ToolResult(
        tool_name="pytest",
        success=True,
        exit_code=0,
        stdout="2 passed",
        duration_ms=250,
    )
    validation = ValidationResult(
        name="unit-tests",
        status=ValidationStatus.PASSED,
        details=tool.stdout,
        duration_ms=tool.duration_ms,
    )

    assert validation.status is ValidationStatus.PASSED


def test_approval_record_captures_human_decision() -> None:
    approval = ApprovalRecord(
        run_id=uuid4(),
        stage=ApprovalStage.PLAN,
        decision=ApprovalDecision.APPROVED,
        actor="steve",
    )

    assert approval.stage is ApprovalStage.PLAN
    assert approval.decision is ApprovalDecision.APPROVED
    assert approval.decided_at.tzinfo is not None


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ChangeRequest(
            repository="s1weetman/ai-release-engineer",
            title="Valid title",
            description="This description is long enough.",
            requested_by="steve",
            unexpected="not allowed",  # type: ignore[call-arg]
        )
