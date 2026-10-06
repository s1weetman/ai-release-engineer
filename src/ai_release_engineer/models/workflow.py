"""Workflow state contracts for a governed AI-assisted change run."""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from ai_release_engineer.models.change_request import ChangeRequest


class WorkflowState(StrEnum):
    """Allowed lifecycle states for a change run."""

    RECEIVED = "received"
    ANALYZING = "analyzing"
    PLAN_READY = "plan_ready"
    PLAN_APPROVED = "plan_approved"
    IMPLEMENTING = "implementing"
    VALIDATING = "validating"
    REVIEW_READY = "review_ready"
    RELEASE_APPROVED = "release_approved"
    PR_PREPARED = "pr_prepared"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowRun(BaseModel):
    """Identifies one governed execution of a change request."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    request: ChangeRequest
    state: WorkflowState = WorkflowState.RECEIVED
