"""Structured implementation plan contracts."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlanStep(BaseModel):
    """One ordered implementation action proposed by the planning agent."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    order: int = Field(ge=1)
    description: str = Field(min_length=3, max_length=2_000)
    paths: tuple[str, ...] = ()

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only step descriptions."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("description must not be blank")
        return cleaned

    @field_validator("paths")
    @classmethod
    def paths_must_be_relative(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        """Prevent absolute and parent-traversal paths from entering plans."""
        for path in values:
            if not path or path.startswith("/") or path.startswith("\\"):
                raise ValueError("plan paths must be non-empty relative paths")
            if ".." in path.replace("\\", "/").split("/"):
                raise ValueError("plan paths must not traverse parent directories")
        return values


class ImplementationPlan(BaseModel):
    """A validated, human-reviewable plan produced before code is changed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str = Field(min_length=5, max_length=4_000)
    steps: tuple[PlanStep, ...] = Field(min_length=1)
    risks: tuple[str, ...] = ()
    validation_commands: tuple[str, ...] = ()

    @field_validator("steps")
    @classmethod
    def steps_must_be_in_unique_order(cls, steps: tuple[PlanStep, ...]) -> tuple[PlanStep, ...]:
        """Require deterministic, non-duplicated ordering."""
        orders = [step.order for step in steps]
        if len(orders) != len(set(orders)):
            raise ValueError("plan step order values must be unique")
        if orders != sorted(orders):
            raise ValueError("plan steps must be sorted by order")
        return steps
