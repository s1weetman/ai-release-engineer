"""Provider-neutral contracts for implementation planning."""

from dataclasses import dataclass
from typing import Protocol

from ai_release_engineer.models.plan import ImplementationPlan


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Normalized token usage captured from one model call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class ProviderCallMetadata:
    """Provider and model identity captured for auditability."""

    provider: str
    model: str
    model_version: str
    response_id: str
    usage: TokenUsage


@dataclass(frozen=True, slots=True)
class ProviderPlanResponse:
    """A validated plan plus evidence about the model call that produced it."""

    plan: ImplementationPlan
    metadata: ProviderCallMetadata


class PlanningProvider(Protocol):
    """Provider-neutral interface used by the planning agent."""

    def generate_plan(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> ProviderPlanResponse:
        """Generate one structured implementation plan."""
        ...
