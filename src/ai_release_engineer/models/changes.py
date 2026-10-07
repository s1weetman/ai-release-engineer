"""Validated file-change contracts for the isolated executor."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChangeOperation(StrEnum):
    """File operations allowed by the Phase 1 executor."""

    CREATE = "create"
    UPDATE = "update"


class FileChange(BaseModel):
    """One bounded text-file mutation inside an execution workspace."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: ChangeOperation
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=1_000_000)

    @field_validator("path")
    @classmethod
    def path_must_be_repository_relative(cls, value: str) -> str:
        """Reject absolute paths and parent-directory traversal."""
        normalized = value.strip().replace("\\", "/")
        if not normalized or normalized.startswith("/"):
            raise ValueError("change path must be a non-empty repository-relative path")
        if ".." in normalized.split("/"):
            raise ValueError("change path must not traverse parent directories")
        return normalized
