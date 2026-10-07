"""OpenAI Responses API adapter for structured implementation planning."""

from typing import Any, Protocol, cast

from openai import OpenAI

from ai_release_engineer.models.plan import ImplementationPlan
from ai_release_engineer.providers.base import (
    ProviderCallMetadata,
    ProviderPlanResponse,
    TokenUsage,
)


class ProviderResponseError(RuntimeError):
    """Raised when a provider response cannot be used safely."""


class _UsageLike(Protocol):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class _ParsedResponseLike(Protocol):
    id: str
    model: str
    usage: _UsageLike | None
    output_parsed: ImplementationPlan | None


class OpenAIPlanningProvider:
    """OpenAI adapter using the Responses API structured-output parser."""

    provider_name = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: Any | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be blank")
        if not model.strip():
            raise ValueError("model must not be blank")

        self._model = model.strip()
        self._client = client if client is not None else OpenAI(api_key=api_key)

    def generate_plan(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> ProviderPlanResponse:
        """Generate and parse an ImplementationPlan through OpenAI."""
        response = cast(
            _ParsedResponseLike,
            self._client.responses.parse(
                model=self._model,
                instructions=instructions,
                input=input_text,
                text_format=ImplementationPlan,
            ),
        )

        plan = response.output_parsed
        if plan is None:
            raise ProviderResponseError("provider returned no parsed implementation plan")

        usage = response.usage
        token_usage = TokenUsage(
            input_tokens=usage.input_tokens if usage is not None else 0,
            output_tokens=usage.output_tokens if usage is not None else 0,
            total_tokens=usage.total_tokens if usage is not None else 0,
        )
        metadata = ProviderCallMetadata(
            provider=self.provider_name,
            model=self._model,
            model_version=response.model,
            response_id=response.id,
            usage=token_usage,
        )
        return ProviderPlanResponse(plan=plan, metadata=metadata)
