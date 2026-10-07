"""Assemble a serializable evidence bundle from validated run artifacts."""

from collections.abc import Sequence
from pathlib import Path
from uuid import UUID

from ai_release_engineer.evidence.diff import ChangeSummaryBuilder
from ai_release_engineer.models.approval import ApprovalRecord
from ai_release_engineer.models.change_request import ChangeRequest
from ai_release_engineer.models.changes import FileChange
from ai_release_engineer.models.evidence import EvidenceBundle, ModelCallEvidence
from ai_release_engineer.models.plan import ImplementationPlan
from ai_release_engineer.models.results import ToolResult, ValidationResult
from ai_release_engineer.providers.base import ProviderCallMetadata


class EvidenceBuilder:
    """Create complete, serializable evidence for one local change run."""

    def __init__(self, *, change_summary_builder: ChangeSummaryBuilder | None = None) -> None:
        self._change_summary_builder = change_summary_builder or ChangeSummaryBuilder()

    def build(
        self,
        *,
        run_id: UUID,
        request: ChangeRequest,
        plan: ImplementationPlan,
        source_root: Path,
        workspace_root: Path,
        changes: Sequence[FileChange],
        validations: Sequence[ValidationResult],
        tool_results: Sequence[ToolResult] = (),
        provider_metadata: ProviderCallMetadata | None = None,
        approvals: Sequence[ApprovalRecord] = (),
    ) -> EvidenceBundle:
        """Build a versioned evidence bundle with derived validation status."""
        change_summary = self._change_summary_builder.build(
            source_root=source_root,
            workspace_root=workspace_root,
            changes=changes,
        )
        model_call = (
            self._model_call_evidence(provider_metadata)
            if provider_metadata is not None
            else None
        )
        return EvidenceBundle(
            run_id=run_id,
            request=request,
            plan=plan,
            model_call=model_call,
            change_summary=change_summary,
            tool_results=tuple(tool_results),
            validations=tuple(validations),
            approvals=tuple(approvals),
        )

    @staticmethod
    def _model_call_evidence(metadata: ProviderCallMetadata) -> ModelCallEvidence:
        """Normalize provider metadata into a serializable evidence model."""
        return ModelCallEvidence(
            provider=metadata.provider,
            model=metadata.model,
            model_version=metadata.model_version,
            response_id=metadata.response_id,
            input_tokens=metadata.usage.input_tokens,
            output_tokens=metadata.usage.output_tokens,
            total_tokens=metadata.usage.total_tokens,
        )
