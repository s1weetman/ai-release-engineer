"""Tests for diff summaries and serializable evidence bundles."""

import json
from pathlib import Path
from uuid import uuid4

from ai_release_engineer.evidence import ChangeSummaryBuilder, EvidenceBuilder
from ai_release_engineer.models import (
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStage,
    ChangeOperation,
    ChangeRequest,
    EvidenceStatus,
    FileChange,
    ImplementationPlan,
    PlanStep,
    ToolResult,
    ValidationKind,
    ValidationResult,
    ValidationStatus,
)
from ai_release_engineer.providers import ProviderCallMetadata, TokenUsage


def make_request() -> ChangeRequest:
    return ChangeRequest(
        repository="example/sample",
        title="Update greeting behavior",
        description="Update the greeting and add a helper module for the feature.",
        requested_by="steve",
    )


def make_plan() -> ImplementationPlan:
    return ImplementationPlan(
        summary="Update the greeting and add a helper.",
        steps=(
            PlanStep(
                order=1,
                description="Update the existing greeting.",
                paths=("src/app.py",),
            ),
            PlanStep(
                order=2,
                description="Add the helper module.",
                paths=("src/helper.py",),
            ),
        ),
        validation_commands=("python -m pytest",),
    )


def prepare_roots(tmp_path: Path) -> tuple[Path, Path, tuple[FileChange, ...]]:
    source = tmp_path / "source"
    workspace = tmp_path / "workspace"
    (source / "src").mkdir(parents=True)
    (workspace / "src").mkdir(parents=True)

    original = 'def greet() -> str:\n    return "Hello"\n'
    updated = 'def greet() -> str:\n    return "Hello, world"\n'
    helper = 'def helper() -> str:\n    return "ready"\n'

    (source / "src" / "app.py").write_text(original, encoding="utf-8")
    (workspace / "src" / "app.py").write_text(updated, encoding="utf-8")
    (workspace / "src" / "helper.py").write_text(helper, encoding="utf-8")

    changes = (
        FileChange(
            operation=ChangeOperation.UPDATE,
            path="src/app.py",
            content=updated,
        ),
        FileChange(
            operation=ChangeOperation.CREATE,
            path="src/helper.py",
            content=helper,
        ),
    )
    return source, workspace, changes


def test_change_summary_reports_files_counts_and_unified_diff(tmp_path: Path) -> None:
    source, workspace, changes = prepare_roots(tmp_path)

    summary = ChangeSummaryBuilder().build(
        source_root=source,
        workspace_root=workspace,
        changes=changes,
    )

    assert summary.files_changed == 2
    assert summary.additions == 3
    assert summary.deletions == 1
    assert summary.files[0].path == "src/app.py"
    assert summary.files[1].operation is ChangeOperation.CREATE
    assert "--- a/src/app.py" in summary.unified_diff
    assert "+++ b/src/helper.py" in summary.unified_diff
    assert summary.diff_truncated is False


def test_change_summary_bounds_large_diff(tmp_path: Path) -> None:
    source, workspace, changes = prepare_roots(tmp_path)

    summary = ChangeSummaryBuilder(max_diff_chars=80).build(
        source_root=source,
        workspace_root=workspace,
        changes=changes,
    )

    assert len(summary.unified_diff) <= 80
    assert summary.unified_diff.endswith("...[diff truncated]")
    assert summary.diff_truncated is True


def test_evidence_bundle_is_json_serializable_and_derives_passed_status(
    tmp_path: Path,
) -> None:
    source, workspace, changes = prepare_roots(tmp_path)
    run_id = uuid4()
    validation = ValidationResult(
        kind=ValidationKind.TEST,
        name="unit-tests",
        status=ValidationStatus.PASSED,
        command=("python", "-m", "pytest"),
        details="2 passed",
        duration_ms=25,
    )
    tool = ToolResult(
        tool_name="python -m pytest",
        success=True,
        exit_code=0,
        stdout="2 passed",
        duration_ms=25,
    )
    provider = ProviderCallMetadata(
        provider="openai",
        model="gpt-test",
        model_version="gpt-test-2026-10-07",
        response_id="resp_123",
        usage=TokenUsage(input_tokens=100, output_tokens=25, total_tokens=125),
    )
    approval = ApprovalRecord(
        run_id=run_id,
        stage=ApprovalStage.PLAN,
        decision=ApprovalDecision.APPROVED,
        actor="steve",
    )

    bundle = EvidenceBuilder().build(
        run_id=run_id,
        request=make_request(),
        plan=make_plan(),
        source_root=source,
        workspace_root=workspace,
        changes=changes,
        validations=(validation,),
        tool_results=(tool,),
        provider_metadata=provider,
        approvals=(approval,),
    )

    payload = json.loads(bundle.model_dump_json())

    assert bundle.validation_passed is True
    assert bundle.status is EvidenceStatus.PASSED
    assert payload["schema_version"] == "1.0"
    assert payload["status"] == "passed"
    assert payload["validation_passed"] is True
    assert payload["change_summary"]["files_changed"] == 2
    assert payload["model_call"]["total_tokens"] == 125
    assert payload["approvals"][0]["actor"] == "steve"


def test_failed_validation_marks_evidence_failed(tmp_path: Path) -> None:
    source, workspace, changes = prepare_roots(tmp_path)
    failed = ValidationResult(
        kind=ValidationKind.SECURITY,
        name="security-scan",
        status=ValidationStatus.FAILED,
        details="finding detected",
        duration_ms=12,
    )

    bundle = EvidenceBuilder().build(
        run_id=uuid4(),
        request=make_request(),
        plan=make_plan(),
        source_root=source,
        workspace_root=workspace,
        changes=changes,
        validations=(failed,),
    )

    assert bundle.validation_passed is False
    assert bundle.status is EvidenceStatus.FAILED
