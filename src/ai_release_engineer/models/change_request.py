"""Domain model for a bounded software change request."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChangeRequest(BaseModel):
    """A user's requested repository change."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    repository: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=10_000)
    requested_by: str = Field(min_length=1, max_length=200)

    @field_validator("repository")
    @classmethod
    def repository_must_be_owner_slash_name(cls, value: str) -> str:
        """Require a simple GitHub-style owner/repository identifier."""
        cleaned = value.strip()
        if cleaned.count("/") != 1:
            raise ValueError("repository must use owner/name format")
        owner, name = cleaned.split("/", maxsplit=1)
        if not owner or not name:
            raise ValueError("repository must use owner/name format")
        return cleaned

    @field_validator("title", "description", "requested_by")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        """Reject strings that only contain whitespace."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value must not be blank")
        return cleaned
