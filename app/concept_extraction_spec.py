"""Concept extraction request shaping and workflow specification."""

from __future__ import annotations

import app.concept_provider as concept_provider
from app.schemas import (
    ApiWarning,
    ConceptExtractionOutput,
    ExtractConceptsResponse,
    ReasoningLevel,
    SessionExtractionSource,
    get_concept_extraction_output_schema,
)
from app.structured_extraction import (
    PreparedExtractionEvent,
    PreparedStructuredExtraction,
    StructuredExtractionSpec,
)
from app.structured_extraction import (
    StructuredExtractionError as ConceptExtractionError,
)
from app.transcript_parser import normalize_transcript_text

DEFAULT_OPERATION_NAME = "extract_gradeable_concepts"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = concept_provider.DEFAULT_REASONING_TYPE
DEFAULT_STEP_PREFIX = "extract_session_concepts"
DEFAULT_MAX_CONCEPTS = 5
TRANSCRIPT_WARNING = ApiWarning(
    code="session_transcript_not_available",
    message="Session transcript not available, synthesized concepts are based on session topic.",
)

CONCEPT_EXTRACTION_SPEC = StructuredExtractionSpec[
    ConceptExtractionOutput, ExtractConceptsResponse
](
    step_prefix=DEFAULT_STEP_PREFIX,
    output_model=ConceptExtractionOutput,
    schema_failure_code="concept_schema_validation_failed",
    schema_failure_message="Unable to validate the extracted concepts after schema repair.",
    select_primary_provider=lambda: concept_provider.select_concept_extraction_provider(),
    build_provider=lambda *, provider_name, model_name: (
        concept_provider.build_concept_extraction_provider(
            provider_name=provider_name,
            model_name=model_name,
        )
    ),
)


def prepare_concept_extraction(
    *,
    session_source: SessionExtractionSource,
    reasoning_level: ReasoningLevel,
) -> PreparedStructuredExtraction[ConceptExtractionOutput, ExtractConceptsResponse]:
    """Build the canonical request and response mapper for concept extraction."""
    warnings: list[ApiWarning] = []
    preparation_events: list[PreparedExtractionEvent] = []
    session_transcript = normalize_transcript_text(session_source.session_transcript)
    if session_transcript is None:
        warnings.append(TRANSCRIPT_WARNING)

    if not session_source.session_title.strip() and not session_source.session_topic.strip():
        raise ConceptExtractionError(
            code="concept_extraction_failed",
            message="Unable to prepare usable session evidence for concept extraction.",
        )

    request = concept_provider.CanonicalConceptExtractionRequest(
        session_id=session_source.id,
        operation_name=DEFAULT_OPERATION_NAME,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=concept_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_concept_extraction_output_schema(
            max_concepts=DEFAULT_MAX_CONCEPTS
        ),
        prompt_subject="Session evidence",
        prompt_input_fields=[
            concept_provider.PromptInputField(label="Session ID", value=session_source.id),
            concept_provider.PromptInputField(
                label="Session title",
                value=session_source.session_title,
            ),
            concept_provider.PromptInputField(
                label="Session topic",
                value=session_source.session_topic,
            ),
            concept_provider.PromptInputField(
                label="Session transcript",
                value=session_transcript or "(Not available. Use session title and topic only.)",
            ),
        ],
        system_instruction_lines=[
            "Extract the most gradeable concepts from the session evidence.",
            "A gradeable concept must be specific enough to evaluate in student work.",
            (
                "Each concept must include concept_importance as an integer from 1 to 10 "
                "showing how central the concept is to the session."
            ),
            "Use only concepts that are directly supported by the session evidence.",
            "Do not invent evidence or concepts that are absent from the session.",
        ],
        repair_guidance_lines=[
            "Make sure every concept includes concept_importance as an integer from 1 to 10."
        ],
        repair_output_example={
            "concepts": [
                {
                    "name": "Concept name",
                    "summary": "Short description of the concept.",
                    "grading_reason": "Why this concept matters for grading.",
                    "concept_importance": 8,
                    "evidence": ["Exact supporting session evidence."],
                }
            ]
        },
        telemetry_details={
            "session_id": session_source.id,
            "operation_name": DEFAULT_OPERATION_NAME,
            "reasoning_level": reasoning_level,
            "reasoning_type": DEFAULT_REASONING_TYPE,
            "output_mode": concept_provider.DEFAULT_OUTPUT_MODE,
            "max_concepts": DEFAULT_MAX_CONCEPTS,
            "response_schema_title": "ConceptExtractionOutput",
            "has_session_transcript": session_transcript is not None,
            "session_transcript_length": len(session_transcript or ""),
            "used_transcript_fallback": bool(warnings),
            "session_title_present": bool(session_source.session_title.strip()),
            "session_topic_present": bool(session_source.session_topic.strip()),
        },
        session_title=session_source.session_title,
        session_topic=session_source.session_topic,
        session_transcript=session_transcript,
        max_concepts=DEFAULT_MAX_CONCEPTS,
    )
    if warnings:
        preparation_events.append(
            PreparedExtractionEvent(
                step_suffix="transcript_fallback_used",
                validation_status="passed",
                failure_reason=TRANSCRIPT_WARNING.code,
            )
        )
    preparation_events.append(
        PreparedExtractionEvent(
            step_suffix="canonical_request_built",
            validation_status="passed",
            details=request.telemetry_details,
        )
    )
    return PreparedStructuredExtraction(
        request=request,
        warnings=warnings,
        build_response=lambda output, response_warnings: ExtractConceptsResponse(
            session_id=session_source.id,
            concepts=output.concepts,
            warnings=response_warnings,
        ),
        preparation_events=preparation_events,
    )
