"""Deterministic success and failure scenarios for the local MVP demo."""

from dataclasses import dataclass
from enum import StrEnum

from ai_release_engineer.models import (
    ChangeOperation,
    ChangeRequest,
    FileChange,
    ImplementationPlan,
    PlanStep,
)


class DemoScenario(StrEnum):
    """Available reproducible MVP demo scenarios."""

    SUCCESS = "success"
    VALIDATION_FAILURE = "validation-failure"


@dataclass(frozen=True, slots=True)
class DemoScenarioDefinition:
    """All deterministic inputs needed for one demo run."""

    name: DemoScenario
    request: ChangeRequest
    plan: ImplementationPlan
    changes: tuple[FileChange, ...]
    expected_to_pass: bool


def _request() -> ChangeRequest:
    return ChangeRequest(
        repository="demo/greeting-service",
        title="Add an excited greeting option",
        description=(
            "Add an optional excited boolean argument to greet(). "
            "The default greeting must stay unchanged. When excited is true, "
            "return the complete greeting in uppercase and add a regression test."
        ),
        requested_by="demo-user",
    )


def _plan() -> ImplementationPlan:
    return ImplementationPlan(
        summary="Add an optional excited greeting while preserving existing behavior.",
        steps=(
            PlanStep(
                order=1,
                description="Update greet() with an optional excited boolean argument.",
                paths=("greeting.py",),
            ),
            PlanStep(
                order=2,
                description="Add a regression test for excited greeting behavior.",
                paths=("tests/test_excited.py",),
            ),
        ),
        risks=(
            "The default greeting behavior must remain backward compatible.",
        ),
        validation_commands=(
            "python -m pytest -q",
            "python -m ruff check .",
            "python -m mypy greeting.py tests",
        ),
    )


def _success_changes() -> tuple[FileChange, ...]:
    return (
        FileChange(
            operation=ChangeOperation.UPDATE,
            path="greeting.py",
            content='''"""Greeting behavior for the MVP demo."""


def greet(name: str, excited: bool = False) -> str:
    message = f"Hello, {name}!"
    return message.upper() if excited else message
''',
        ),
        FileChange(
            operation=ChangeOperation.CREATE,
            path="tests/test_excited.py",
            content='''"""Regression test for the requested excited greeting feature."""

from greeting import greet


def test_excited_greeting_is_uppercase() -> None:
    assert greet("Steve", excited=True) == "HELLO, STEVE!"
''',
        ),
    )


def _failure_changes() -> tuple[FileChange, ...]:
    return (
        FileChange(
            operation=ChangeOperation.UPDATE,
            path="greeting.py",
            content='''"""Greeting behavior for the MVP demo."""


def greet(name: str, excited: bool = False) -> str:
    message = f"Hello, {name}!"
    if excited:
        return "HELLO!"
    return message
''',
        ),
        FileChange(
            operation=ChangeOperation.CREATE,
            path="tests/test_excited.py",
            content='''"""Regression test for the requested excited greeting feature."""

from greeting import greet


def test_excited_greeting_is_uppercase() -> None:
    assert greet("Steve", excited=True) == "HELLO, STEVE!"
''',
        ),
    )


def get_demo_scenario(name: DemoScenario) -> DemoScenarioDefinition:
    """Return one deterministic demo definition."""
    if name is DemoScenario.SUCCESS:
        return DemoScenarioDefinition(
            name=name,
            request=_request(),
            plan=_plan(),
            changes=_success_changes(),
            expected_to_pass=True,
        )

    return DemoScenarioDefinition(
        name=name,
        request=_request(),
        plan=_plan(),
        changes=_failure_changes(),
        expected_to_pass=False,
    )
