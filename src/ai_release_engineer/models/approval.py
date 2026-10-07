"""Human approval contracts."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStage(StrEnum):
    """Workflow checkpoints that require human authorization."""

    PLAN = "plan"
    RELEASE = "release"


class ApprovalDecision(StrEnum):
    """Human decision captured at an approval checkpoint."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRecord(BaseModel):
    """Auditable record of a human approval decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: UUID
    stage: ApprovalStage
    decision: ApprovalDecision
    actor: str = Field(min_length=1, max_length=200)
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    comment: str | None = Field(default=None, max_length=2_000)
