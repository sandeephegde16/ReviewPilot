"""Provider interfaces, factories, and adapters for structured extraction workflows."""

from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from app.config import (
    get_anthropic_api_key,
    get_concept_extraction_model_name,
    get_concept_extraction_provider_name,
    get_gemini_api_key,
)
from app.external_provider_payloads import (
    ANTHROPIC_MESSAGES_API_URL,
    GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE,
    ProviderReasoningMetadata,
    get_provider_reasoning_metadata,
)
from app.external_provider_payloads import (
    build_anthropic_input_schema as _build_anthropic_input_schema,
)
from app.external_provider_payloads import (
    build_anthropic_request_body as _build_anthropic_request_body,
)
from app.external_provider_payloads import (
    build_gemini_request_body as _build_gemini_request_body,
)
from app.external_provider_payloads import (
    build_provider_user_prompt as _build_provider_user_prompt,
)
from app.external_provider_payloads import (
    extract_anthropic_tool_input as _extract_anthropic_tool_input,
)
from app.external_provider_payloads import (
    extract_gemini_structured_output as _extract_gemini_structured_output,
)
from app.heuristic_provider import (
    MAX_HEURISTIC_CONCEPT_COUNT,
    HeuristicStructuredExtractionProvider,
)
from app.provider_http import post_json as _post_json
from app.schemas import (
    AssignmentRequirementExtractionSource,
    ConceptGradingCriterion,
    ReasoningLevel,
    SubmissionSourceType,
)

DEFAULT_REASONING_TYPE = "structured_extraction"
DEFAULT_OUTPUT_MODE = "json_schema_strict"
OutputMode = Literal["json_schema_strict"]
__all__ = [
    "ANTHROPIC_MESSAGES_API_URL",
    "AnthropicStructuredExtractionProvider",
    "CanonicalStructuredExtractionRequest",
    "DEFAULT_OUTPUT_MODE",
    "DEFAULT_REASONING_TYPE",
    "GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE",
    "GeminiStructuredExtractionProvider",
    "HeuristicStructuredExtractionProvider",
    "MAX_HEURISTIC_CONCEPT_COUNT",
    "OutputMode",
    "PromptInputField",
    "ProviderReasoningMetadata",
    "StructuredExtractionProvider",
    "StructuredExtractionRepairContext",
    "_build_anthropic_input_schema",
    "_build_anthropic_request_body",
    "_build_gemini_request_body",
    "_build_provider_user_prompt",
    "_extract_anthropic_tool_input",
    "_extract_gemini_structured_output",
    "_post_json",
    "build_structured_extraction_provider",
    "get_provider_reasoning_metadata",
    "select_structured_extraction_provider",
]


class PromptInputField(BaseModel):
    """One labeled prompt field included in the provider user prompt."""

    label: str = Field(description="Human-readable label shown in the prompt.")
    value: str = Field(description="Prompt content for the labeled field.")


class CanonicalStructuredExtractionRequest(BaseModel):
    """Provider-agnostic request for one structured extraction workflow."""

    session_id: str = Field(description="Unique identifier for the session.")
    student_id: str = Field(
        default="",
        description="Unique identifier for the student, when relevant to this workflow.",
    )
    student_code: str = Field(
        default="",
        description="Stable course-visible identifier for the student, when relevant.",
    )
    student_full_name: str = Field(
        default="",
        description="Full name of the student, when relevant to this workflow.",
    )
    operation_name: str = Field(description="Canonical internal operation name.")
    reasoning_level: ReasoningLevel = Field(description="Requested reasoning depth.")
    reasoning_type: str = Field(description="Canonical extraction mode.")
    output_mode: OutputMode = Field(description="Requested structured output mode.")
    response_schema: dict[str, Any] = Field(
        description="JSON schema defining the structured output required from the provider.",
    )
    prompt_subject: str = Field(description="Prompt heading used before the input evidence.")
    prompt_input_fields: list[PromptInputField] = Field(
        default_factory=list,
        description="Ordered prompt fields included in the provider user prompt.",
    )
    system_instruction_lines: list[str] = Field(
        default_factory=list,
        description="Task instructions shared across providers for this extraction workflow.",
    )
    repair_guidance_lines: list[str] = Field(
        default_factory=list,
        description="Additional repair-only guidance appended after schema validation fails.",
    )
    repair_output_example: dict[str, Any] = Field(
        default_factory=dict,
        description="Compact valid output example shown during schema repair retries.",
    )
    telemetry_details: dict[str, Any] = Field(
        default_factory=dict,
        description="Safe metadata emitted with canonical-request telemetry.",
    )
    session_title: str = Field(
        default="",
        description="Stored title for the session, when relevant to this workflow.",
    )
    session_topic: str = Field(
        default="",
        description="Stored topic summary for the session, when relevant to this workflow.",
    )
    session_transcript: str | None = Field(
        default=None,
        description="Normalized transcript text used for concept extraction when available.",
    )
    source_type: SubmissionSourceType | None = Field(
        default=None,
        description="Submission source type used for project grading when relevant.",
    )
    repo_url: str | None = Field(
        default=None,
        description="Repository or pull request URL used for project grading when relevant.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local project folder path used for project grading when relevant.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Zip archive path used for project grading when relevant.",
    )
    assignment_sources: list[AssignmentRequirementExtractionSource] = Field(
        default_factory=list,
        description="Stored assignment rows used during assignment requirement extraction.",
    )
    grading_concepts: list[ConceptGradingCriterion] = Field(
        default_factory=list,
        description="Requested project grading concepts when relevant to this workflow.",
    )
    project_evidence_summary: str = Field(
        default="",
        description="Bounded project evidence summary used for grading when relevant.",
    )
    max_concepts: int | None = Field(
        default=None,
        ge=1,
        description="Maximum number of concepts the provider should return, when relevant.",
    )
    max_assignment_requirements: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Maximum number of extracted requirements to return per assignment record, "
            "when relevant."
        ),
    )


class StructuredExtractionRepairContext(BaseModel):
    """Repair metadata returned to the provider after schema validation fails."""

    schema_check_failed: bool = Field(
        default=True,
        description="Whether the previous model response failed schema validation.",
    )
    previous_output: dict[str, Any] = Field(
        description="Previous structured output sent back for repair.",
    )
    validation_errors: list[str] = Field(
        description="Schema validation errors returned to the provider on repair.",
    )


class StructuredExtractionProvider(Protocol):
    """Protocol implemented by any structured extraction provider."""

    provider_name: str
    model_name: str

    def extract_structured_output(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Return a JSON-like structured payload for one extraction request."""


class AnthropicStructuredExtractionProvider:
    """Anthropic-backed provider using forced tool use for structured output."""

    provider_name = "anthropic"

    def __init__(self, *, model_name: str, api_key: str) -> None:
        """Store the configured Anthropic model and API key."""
        self.model_name = model_name
        self.api_key = api_key

    def extract_structured_output(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Call Anthropic Messages API and extract the forced tool input payload."""
        del trace_id
        response_payload = _post_json(
            provider_name=self.provider_name,
            url=ANTHROPIC_MESSAGES_API_URL,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            body=_build_anthropic_request_body(
                request=request,
                model_name=self.model_name,
                repair_context=repair_context,
            ),
        )
        return _extract_anthropic_tool_input(
            response_payload=response_payload,
            operation_name=request.operation_name,
        )

    def extract_concepts(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Compatibility wrapper for older concept-specific callers."""
        return self.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )


class GeminiStructuredExtractionProvider:
    """Gemini-backed provider using native structured JSON schema output."""

    provider_name = "gemini"

    def __init__(self, *, model_name: str, api_key: str) -> None:
        """Store the configured Gemini model and API key."""
        self.model_name = model_name
        self.api_key = api_key

    def extract_structured_output(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Call Gemini generateContent API and parse the structured JSON response."""
        del trace_id
        response_payload = _post_json(
            provider_name=self.provider_name,
            url=GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE.format(model_name=self.model_name),
            headers={
                "content-type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            body=_build_gemini_request_body(
                request=request,
                model_name=self.model_name,
                repair_context=repair_context,
            ),
        )
        return _extract_gemini_structured_output(response_payload=response_payload)

    def extract_concepts(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Compatibility wrapper for older concept-specific callers."""
        return self.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )


def select_structured_extraction_provider() -> StructuredExtractionProvider:
    """Build the configured primary provider for structured extraction."""
    provider_name = get_concept_extraction_provider_name()
    return build_structured_extraction_provider(
        provider_name=provider_name,
        model_name=get_concept_extraction_model_name(provider_name),
    )


def build_structured_extraction_provider(
    *,
    provider_name: str,
    model_name: str,
) -> StructuredExtractionProvider:
    """Build a structured extraction provider for one explicit provider/model pair."""
    if provider_name == "heuristic":
        return HeuristicStructuredExtractionProvider(model_name=model_name)
    if provider_name == "anthropic":
        anthropic_api_key = get_anthropic_api_key()
        if anthropic_api_key is None:
            raise LookupError("Anthropic provider is selected but no API key is configured.")
        return AnthropicStructuredExtractionProvider(
            model_name=model_name,
            api_key=anthropic_api_key,
        )
    if provider_name == "gemini":
        gemini_api_key = get_gemini_api_key()
        if gemini_api_key is None:
            raise LookupError("Gemini provider is selected but no API key is configured.")
        return GeminiStructuredExtractionProvider(
            model_name=model_name,
            api_key=gemini_api_key,
        )

    raise LookupError(
        "No structured extraction provider is available for the current configuration."
    )
