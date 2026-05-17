"""Concept grading request shaping and workflow specification."""

from __future__ import annotations

import app.concept_grading_provider as concept_grading_provider
from app.schemas import (
    ConceptGradingOutput,
    ConceptGradingSource,
    GradeConceptsResponse,
    ReasoningLevel,
    get_concept_grading_output_schema,
)
from app.structured_extraction import (
    PreparedExtractionEvent,
    PreparedStructuredExtraction,
    StructuredExtractionSpec,
)

DEFAULT_OPERATION_NAME = "grade_submission_concepts"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = "project_grading"
DEFAULT_STEP_PREFIX = "grade_submission_concepts"

CONCEPT_GRADING_SPEC = StructuredExtractionSpec[ConceptGradingOutput, GradeConceptsResponse](
    step_prefix=DEFAULT_STEP_PREFIX,
    output_model=ConceptGradingOutput,
    schema_failure_code="concept_grading_schema_validation_failed",
    schema_failure_message=(
        "Unable to validate the concept grading output after schema repair."
    ),
    select_primary_provider=lambda: concept_grading_provider.select_concept_grading_provider(),
    build_provider=lambda *, provider_name, model_name: (
        concept_grading_provider.build_concept_grading_provider(
            provider_name=provider_name,
            model_name=model_name,
        )
    ),
    build_provider_candidates=lambda: (
        concept_grading_provider.build_concept_grading_provider_candidates()
    ),
)


def prepare_concept_grading(
    *,
    grading_source: ConceptGradingSource,
    reasoning_level: ReasoningLevel,
) -> PreparedStructuredExtraction[ConceptGradingOutput, GradeConceptsResponse]:
    """Build the canonical request and response mapper for concept grading."""
    request = concept_grading_provider.CanonicalConceptGradingRequest(
        session_id=grading_source.session_id,
        student_id=grading_source.student_id,
        student_code=grading_source.student_code,
        student_full_name=grading_source.student_full_name,
        operation_name=DEFAULT_OPERATION_NAME,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=concept_grading_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_concept_grading_output_schema(
            max_concept_scores=len(grading_source.concepts)
        ),
        prompt_subject="Student project evidence",
        prompt_input_fields=[
            concept_grading_provider.PromptInputField(
                label="Student details",
                value=_format_student_details(grading_source),
            ),
            concept_grading_provider.PromptInputField(
                label="Session details",
                value=_format_session_details(grading_source),
            ),
            concept_grading_provider.PromptInputField(
                label="Submission source",
                value=_format_submission_source(grading_source),
            ),
            concept_grading_provider.PromptInputField(
                label="Requested grading concepts",
                value=_format_grading_concepts(grading_source),
            ),
            concept_grading_provider.PromptInputField(
                label="Project evidence",
                value=grading_source.project_evidence.summary_text,
            ),
        ],
        system_instruction_lines=[
            "Score each requested concept independently against the project evidence.",
            "Return one concept_scores entry for each requested concept.",
            "Each concept entry must use the exact requested concept_name as concept.",
            "Set score as an integer from 0 to max_score for that requested concept.",
            "Set coverage_level to one of missing, weak, partial, or strong.",
            "Use only the collected project evidence and do not invent facts.",
            "Evidence entries must quote or closely paraphrase concrete project details.",
            "Deductions must explain missing or weak coverage when full points are not awarded.",
        ],
        repair_guidance_lines=[
            "Return one concept_scores entry for every requested grading concept.",
            (
                "Each entry must include concept, score, max_score, coverage_level, "
                "evidence, and deductions."
            ),
            "score must be less than or equal to max_score.",
        ],
        repair_output_example={
            "concept_scores": [
                {
                    "concept": "time complexity",
                    "score": 4,
                    "max_score": 5,
                    "coverage_level": "strong",
                    "evidence": [
                        "README explains O(log n) search complexity.",
                        "Code implements binary search rather than linear scan.",
                    ],
                    "deductions": ["Space complexity is not discussed."],
                }
            ]
        },
        telemetry_details={
            "submission_id": grading_source.submission_id,
            "session_id": grading_source.session_id,
            "student_id": grading_source.student_id,
            "operation_name": DEFAULT_OPERATION_NAME,
            "reasoning_level": reasoning_level,
            "reasoning_type": DEFAULT_REASONING_TYPE,
            "output_mode": concept_grading_provider.DEFAULT_OUTPUT_MODE,
            "concept_count": len(grading_source.concepts),
            "response_schema_title": "ConceptGradingOutput",
            "source_type": grading_source.source_type,
            "project_file_count": len(grading_source.project_evidence.file_inventory),
            "documentation_snippet_count": len(
                grading_source.project_evidence.documentation_snippets
            ),
            "implementation_snippet_count": len(
                grading_source.project_evidence.implementation_snippets
            ),
            "test_snippet_count": len(grading_source.project_evidence.test_snippets),
        },
        session_title=grading_source.session_title,
        session_topic=grading_source.session_topic,
        source_type=grading_source.source_type,
        repo_url=grading_source.repo_url,
        local_path=grading_source.local_path,
        zip_path=grading_source.zip_path,
        grading_concepts=grading_source.concepts,
        project_evidence_summary=grading_source.project_evidence.summary_text,
    )

    return PreparedStructuredExtraction(
        request=request,
        warnings=[],
        build_response=lambda output, response_warnings: GradeConceptsResponse(
            student_id=grading_source.student_id,
            student_code=grading_source.student_code,
            student_full_name=grading_source.student_full_name,
            session_id=grading_source.session_id,
            source_type=grading_source.source_type,
            repo_url=grading_source.repo_url,
            local_path=grading_source.local_path,
            zip_path=grading_source.zip_path,
            concept_scores=output.concept_scores,
            warnings=response_warnings,
        ),
        preparation_events=[
            PreparedExtractionEvent(
                step_suffix="canonical_request_built",
                validation_status="passed",
                details=request.telemetry_details,
            )
        ],
    )


def _format_student_details(grading_source: ConceptGradingSource) -> str:
    """Format stable student metadata for the provider prompt."""
    return "\n".join(
        [
            f"Student ID: {grading_source.student_id}",
            f"Student code: {grading_source.student_code}",
            f"Student name: {grading_source.student_full_name}",
        ]
    )


def _format_session_details(grading_source: ConceptGradingSource) -> str:
    """Format stable session metadata for the provider prompt."""
    return "\n".join(
        [
            f"Session ID: {grading_source.session_id}",
            f"Session title: {grading_source.session_title}",
            f"Session topic: {grading_source.session_topic}",
        ]
    )


def _format_submission_source(grading_source: ConceptGradingSource) -> str:
    """Format source locator details for the provider prompt."""
    return "\n".join(
        [
            f"source_type: {grading_source.source_type}",
            f"repo_url: {grading_source.repo_url or '(not provided)'}",
            f"local_path: {grading_source.local_path or '(not provided)'}",
            f"zip_path: {grading_source.zip_path or '(not provided)'}",
        ]
    )


def _format_grading_concepts(grading_source: ConceptGradingSource) -> str:
    """Format requested grading concepts into stable prompt text."""
    lines: list[str] = []
    for index, concept in enumerate(grading_source.concepts, start=1):
        lines.extend(
            [
                f"{index}. Concept name: {concept.concept_name}",
                f"   Summary: {concept.summary}",
                f"   Grading reason: {concept.grading_reason}",
                f"   Max score: {concept.max_score}",
            ]
        )
    return "\n".join(lines)
