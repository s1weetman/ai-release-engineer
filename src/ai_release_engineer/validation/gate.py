"""Deterministic validation policy."""

from collections.abc import Sequence

from ai_release_engineer.models.results import ValidationResult, ValidationStatus


class ValidationGateError(RuntimeError):
    """Raised when validation evidence is not sufficient to continue."""


class ValidationGate:
    """Blocks success unless every required validation result passed."""

    @staticmethod
    def passed(results: Sequence[ValidationResult]) -> bool:
        """Return true only when at least one result exists and all passed."""
        return bool(results) and all(result.status is ValidationStatus.PASSED for result in results)

    @classmethod
    def require_passed(cls, results: Sequence[ValidationResult]) -> None:
        """Raise when validation evidence is failed, skipped, or absent."""
        if cls.passed(results):
            return

        failures = [
            f"{result.kind.value}:{result.name}={result.status.value}"
            for result in results
            if result.status is not ValidationStatus.PASSED
        ]
        detail = ", ".join(failures) if failures else "no validation results"
        raise ValidationGateError(f"validation gate did not pass: {detail}")
