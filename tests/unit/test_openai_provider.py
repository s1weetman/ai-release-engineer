"""Tests for the OpenAI structured-planning provider adapter."""

from dataclasses import dataclass

import pytest

from ai_release_engineer.models import ImplementationPlan, PlanStep
from ai_release_engineer.providers import OpenAIPlanningProvider, ProviderResponseError


@dataclass
class FakeUsage:
    input_tokens: int = 80
    output_tokens: int = 20
    total_tokens: int = 100


@dataclass
class FakeResponse:
    output_parsed: ImplementationPlan | None
    id: str = "resp_123"
    model: str = "gpt-test-2026-10-07"
    usage: FakeUsage | None = None


class FakeResponsesAPI:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.kwargs: dict[str, object] | None = None

    def parse(self, **kwargs: object) -> FakeResponse:
        self.kwargs = kwargs
        return self._response


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.responses = FakeResponsesAPI(response)


def make_plan() -> ImplementationPlan:
    return ImplementationPlan(
        summary="Update the application safely.",
        steps=(
            PlanStep(
                order=1,
                description="Modify the existing application module.",
                paths=("src/app.py",),
            ),
        ),
        validation_commands=("python -m pytest",),
    )


def test_openai_provider_returns_structured_plan_and_usage_metadata() -> None:
    client = FakeClient(FakeResponse(output_parsed=make_plan(), usage=FakeUsage()))
    provider = OpenAIPlanningProvider(
        api_key="test-key",
        model="gpt-test",
        client=client,
    )

    result = provider.generate_plan(
        instructions="Plan safely.",
        input_text="Repository context.",
    )

    assert result.plan.summary == "Update the application safely."
    assert result.metadata.provider == "openai"
    assert result.metadata.model == "gpt-test"
    assert result.metadata.model_version == "gpt-test-2026-10-07"
    assert result.metadata.response_id == "resp_123"
    assert result.metadata.usage.input_tokens == 80
    assert result.metadata.usage.output_tokens == 20
    assert result.metadata.usage.total_tokens == 100
    assert client.responses.kwargs is not None
    assert client.responses.kwargs["text_format"] is ImplementationPlan


def test_openai_provider_rejects_missing_parsed_plan() -> None:
    client = FakeClient(FakeResponse(output_parsed=None))
    provider = OpenAIPlanningProvider(
        api_key="test-key",
        model="gpt-test",
        client=client,
    )

    with pytest.raises(ProviderResponseError, match="no parsed implementation plan"):
        provider.generate_plan(
            instructions="Plan safely.",
            input_text="Repository context.",
        )


@pytest.mark.parametrize("api_key,model", [("", "gpt-test"), ("test-key", "")])
def test_openai_provider_rejects_blank_configuration(api_key: str, model: str) -> None:
    with pytest.raises(ValueError):
        OpenAIPlanningProvider(api_key=api_key, model=model, client=FakeClient(FakeResponse(None)))
