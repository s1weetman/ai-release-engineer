"""Serializable evidence models for AI-assisted change runs."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_release_engineer.models.approval import ApprovalRecord
from ai_release_engineer.models.change_request import ChangeRequest
from ai_release_engineer.models.changes import ChangeOperation
from ai_release_engineer.models.plan import ImplementationPlan
from ai_release_engineer.models.results import ToolResult, ValidationResult, ValidationStatus


class EvidenceStatus(StrEnum):
    """Overall deterministic validation status for an evidence bundle."""

    PASSED = "passed"
    FAILED = "failed"


class FileDiffSummary(BaseModel):
    """Summary of one changed file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str = Field(min_length=1, max_length=500)
    operation: ChangeOperation
    additions: int = Field(ge=0)
    deletions: int = Field(ge=0)


class ChangeSummary(BaseModel):
    """Machine-readable and human-reviewable summary of repository changes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    files: tuple[FileDiffSummary, ...]
    files_changed: int = Field(ge=0)
    additions: int = Field(ge=0)
    deletions: int = Field(ge=0)
    unified_diff: str = ""
    diff_truncated: bool = False


class ModelCallEvidence(BaseModel):
    """Normalized model-call metadata retained in the evidence bundle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=200)
    response_id: str = Field(min_length=1, max_length=500)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class EvidenceBundle(BaseModel):
    """Auditable evidence produced for one AI-assisted change run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    run_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    request: ChangeRequest
    plan: ImplementationPlan
    model_call: ModelCallEvidence | None = None
    change_summary: ChangeSummary
    tool_results: tuple[ToolResult, ...] = ()
    validations: tuple[ValidationResult, ...] = Field(min_length=1)
    approvals: tuple[ApprovalRecord, ...] = ()
    validation_passed: bool
    status: EvidenceStatus

    @model_validator(mode="after")
    def status_must_match_validation_evidence(self) -> "EvidenceBundle":
        """Reject any bundle whose claimed status disagrees with validation evidence."""
        expected_passed = all(
            result.status is ValidationStatus.PASSED for result in self.validations
        )
        expected_status = EvidenceStatus.PASSED if expected_passed else EvidenceStatus.FAILED

        if self.validation_passed is not expected_passed or self.status is not expected_status:
            raise ValueError("evidence status must be derived from validation results")
        return self
