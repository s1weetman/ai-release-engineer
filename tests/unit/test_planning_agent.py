"""Tests for the repository-aware planning agent."""

from pathlib import Path

import pytest

from ai_release_engineer.models import ChangeRequest, ImplementationPlan, PlanStep
from ai_release_engineer.planning import PlanRepositoryPathError, PlanningAgent
from ai_release_engineer.providers import (
    ProviderCallMetadata,
    ProviderPlanResponse,
    TokenUsage,
)
from ai_release_engineer.repository import RepositoryService


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "sample_repo"


class FakePlanningProvider:
    """Deterministic provider used to test planning orchestration."""

    def __init__(self, plan: ImplementationPlan) -> None:
        self._plan = plan
        self.instructions: str | None = None
        self.input_text: str | None = None

    def generate_plan(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> ProviderPlanResponse:
        self.instructions = instructions
        self.input_text = input_text
        return ProviderPlanResponse(
            plan=self._plan,
            metadata=ProviderCallMetadata(
                provider="fake",
                model="fake-planner",
                model_version="fake-planner-v1",
                response_id="resp_test",
                usage=TokenUsage(
                    input_tokens=100,
                    output_tokens=25,
                    total_tokens=125,
                ),
            ),
        )


def make_request() -> ChangeRequest:
    return ChangeRequest(
        repository="example/sample-repo",
        title="Update greeting behavior",
        description="Update the sample greeting function and verify it with tests.",
        requested_by="steve",
    )


def test_planning_agent_builds_repository_context_and_returns_metadata() -> None:
    plan = ImplementationPlan(
        summary="Update the greeting safely.",
        steps=(
            PlanStep(
                order=1,
                description="Modify the greeting implementation.",
                paths=("src/app.py",),
            ),
        ),
        validation_commands=("python -m pytest",),
    )
    provider = FakePlanningProvider(plan)
    agent = PlanningAgent(
        repository=RepositoryService(FIXTURE_ROOT),
        provider=provider,
    )

    result = agent.create_plan(make_request())

    assert result.plan == plan
    assert result.provider.provider == "fake"
    assert result.provider.usage.total_tokens == 125
    assert provider.input_text is not None
    assert "src/app.py" in provider.input_text
    assert "BEGIN UNTRUSTED FILE" in provider.input_text
    assert provider.instructions is not None
    assert "planning only" in provider.instructions


def test_planning_agent_allows_new_file_under_existing_directory() -> None:
    plan = ImplementationPlan(
        summary="Add a greeting helper.",
        steps=(
            PlanStep(
                order=1,
                description="Create the helper next to the application module.",
                paths=("src/greeting.py",),
            ),
        ),
    )
    agent = PlanningAgent(
        repository=RepositoryService(FIXTURE_ROOT),
        provider=FakePlanningProvider(plan),
    )

    result = agent.create_plan(make_request())

    assert result.plan.steps[0].paths == ("src/greeting.py",)


def test_planning_agent_rejects_hallucinated_repository_structure() -> None:
    plan = ImplementationPlan(
        summary="Attempt an invalid edit.",
        steps=(
            PlanStep(
                order=1,
                description="Edit a path whose parent directory does not exist.",
                paths=("does-not-exist/deep/file.py",),
            ),
        ),
    )
    agent = PlanningAgent(
        repository=RepositoryService(FIXTURE_ROOT),
        provider=FakePlanningProvider(plan),
    )

    with pytest.raises(PlanRepositoryPathError, match="outside known repository structure"):
        agent.create_plan(make_request())
