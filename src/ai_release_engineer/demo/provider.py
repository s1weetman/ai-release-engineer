"""Deterministic planning provider used by the reproducible MVP demo."""

from ai_release_engineer.models import ImplementationPlan
from ai_release_engineer.providers import (
    ProviderCallMetadata,
    ProviderPlanResponse,
    TokenUsage,
)


class DemoPlanningProvider:
    """Return a pre-defined structured plan through the real provider boundary."""

    def __init__(self, plan: ImplementationPlan) -> None:
        self._plan = plan

    def generate_plan(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> ProviderPlanResponse:
        """Return the deterministic plan while preserving provider metadata."""
        if not instructions.strip():
            raise ValueError("planning instructions must not be blank")
        if not input_text.strip():
            raise ValueError("repository context must not be blank")

        return ProviderPlanResponse(
            plan=self._plan,
            metadata=ProviderCallMetadata(
                provider="demo",
                model="deterministic-demo-planner",
                model_version="1.0",
                response_id="demo-plan",
                usage=TokenUsage(
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                ),
            ),
        )
