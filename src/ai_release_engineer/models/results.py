"""Typed results for tools and validation gates."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ValidationStatus(StrEnum):
    """Normalized result status for deterministic quality gates."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolResult(BaseModel):
    """Machine-readable result from a controlled tool invocation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool_name: str = Field(min_length=1, max_length=200)
    success: bool
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = Field(ge=0)


class ValidationResult(BaseModel):
    """Normalized result from a test, lint, type, or security gate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=200)
    status: ValidationStatus
    details: str = ""
    duration_ms: int = Field(ge=0)
