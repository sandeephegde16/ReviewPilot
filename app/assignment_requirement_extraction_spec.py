"""Assignment requirement request shaping and workflow specification."""

from __future__ import annotations

import app.assignment_requirement_provider as assignment_requirement_provider
from app.schemas import (
    ApiWarning,
    AssignmentRequirementExtractionSource,
    AssignmentRequirementsExtractionOutput,
    ExtractAssignmentRequirementsResponse,
    ReasoningLevel,
    get_assignment_requirements_extraction_output_schema,
)
from app.structured_extraction import (
    PreparedExtractionEvent,
    PreparedStructuredExtraction,
    StructuredExtractionError,
    StructuredExtractionSpec,
)

DEFAULT_OPERATION_NAME = "extract_assignment_requirements"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = assignment_requirement_provider.DEFAULT_REASONING_TYPE
DEFAULT_STEP_PREFIX = "extract_session_assignment_requirements"
DEFAULT_MAX_ASSIGNMENT_REQUIREMENTS = 5
AssignmentRequirementExtractionError = StructuredExtractionError
NO_ASSIGNMENT_REQUIREMENTS_WARNING = ApiWarning(
    code="session_assignment_requirements_not_available",
    message="No assignment requirements are stored for this session.",
)

ASSIGNMENT_REQUIREMENT_EXTRACTION_SPEC = StructuredExtractionSpec[
    AssignmentRequirementsExtractionOutput, ExtractAssignmentRequirementsResponse
](
    step_prefix=DEFAULT_STEP_PREFIX,
    output_model=AssignmentRequirementsExtractionOutput,
    schema_failure_code="assignment_requirement_schema_validation_failed",
    schema_failure_message=(
        "Unable to validate the extracted assignment requirements after schema repair."
    ),
    select_primary_provider=lambda: (
        assignment_requirement_provider.select_assignment_requirement_extraction_provider()
    ),
    build_provider=lambda *, provider_name, model_name: (
        assignment_requirement_provider.build_assignment_requirement_extraction_provider(
            provider_name=provider_name,
            model_name=model_name,
        )
    ),
)


def prepare_assignment_requirement_extraction(
    *,
    session_id: str,
    assignment_sources: list[AssignmentRequirementExtractionSource],
    reasoning_level: ReasoningLevel,
) -> PreparedStructuredExtraction[
    AssignmentRequirementsExtractionOutput, ExtractAssignmentRequirementsResponse
]:
    """Build the canonical request and response mapper for assignment extraction."""
    warnings: list[ApiWarning] = []
    if not assignment_sources:
        warnings.append(NO_ASSIGNMENT_REQUIREMENTS_WARNING)

    request = assignment_requirement_provider.CanonicalAssignmentRequirementExtractionRequest(
        session_id=session_id,
        operation_name=DEFAULT_OPERATION_NAME,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=assignment_requirement_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_assignment_requirements_extraction_output_schema(
            max_assignment_requirements=DEFAULT_MAX_ASSIGNMENT_REQUIREMENTS
        ),
        prompt_subject="Assignment evidence",
        prompt_input_fields=[
            assignment_requirement_provider.PromptInputField(
                label="Session ID",
                value=session_id,
            ),
            assignment_requirement_provider.PromptInputField(
                label="Assignment records",
                value=_format_assignment_sources_for_prompt(assignment_sources),
            ),
        ],
        system_instruction_lines=[
            "Extract explicit assignment requirements from the assignment evidence.",
            (
                "Return one assignment_requirements entry for each assignment record present "
                "in the evidence."
            ),
            (
                "Classify each requirement as mandatory_deliverable, "
                "forbidden_project_type, scoring_criterion, or evidence_expectation."
            ),
            (
                "Use only requirements that are directly supported by the assignment "
                "title and description."
            ),
            (
                "Do not invent deliverables, restrictions, scoring criteria, or evidence "
                "expectations that are absent from the assignment evidence."
            ),
        ],
        repair_guidance_lines=[
            (
                "Every assignment entry must include assignment_requirement_id, "
                "assignment_title, and a non-empty requirements list."
            ),
            (
                "Every requirement must include requirement_type, title, summary, "
                "and evidence."
            ),
        ],
        repair_output_example={
            "assignment_requirements": [
                {
                    "assignment_requirement_id": "assignment-1",
                    "assignment_title": "Assignment title",
                    "requirements": [
                        {
                            "requirement_type": "mandatory_deliverable",
                            "title": "Deliverable title",
                            "summary": "What the student must submit or demonstrate.",
                            "evidence": ["Exact supporting assignment text."],
                        }
                    ],
                }
            ]
        },
        telemetry_details={
            "session_id": session_id,
            "operation_name": DEFAULT_OPERATION_NAME,
            "reasoning_level": reasoning_level,
            "reasoning_type": DEFAULT_REASONING_TYPE,
            "output_mode": assignment_requirement_provider.DEFAULT_OUTPUT_MODE,
            "max_assignment_requirements": DEFAULT_MAX_ASSIGNMENT_REQUIREMENTS,
            "response_schema_title": "AssignmentRequirementsExtractionOutput",
            "assignment_count": len(assignment_sources),
        },
        assignment_sources=assignment_sources,
        max_assignment_requirements=DEFAULT_MAX_ASSIGNMENT_REQUIREMENTS,
    )

    preparation_events = [
        PreparedExtractionEvent(
            step_suffix="canonical_request_built",
            validation_status="passed",
            details=request.telemetry_details,
        )
    ]
    short_circuit_response = None
    short_circuit_event = None
    if warnings:
        short_circuit_response = ExtractAssignmentRequirementsResponse(
            session_id=session_id,
            assignment_requirements=[],
            warnings=warnings,
        )
        short_circuit_event = PreparedExtractionEvent(
            step_suffix="no_assignment_requirements_found",
            validation_status="passed",
            failure_reason=NO_ASSIGNMENT_REQUIREMENTS_WARNING.code,
        )

    return PreparedStructuredExtraction(
        request=request,
        warnings=warnings,
        build_response=lambda output, response_warnings: ExtractAssignmentRequirementsResponse(
            session_id=session_id,
            assignment_requirements=output.assignment_requirements,
            warnings=response_warnings,
        ),
        preparation_events=preparation_events,
        short_circuit_response=short_circuit_response,
        short_circuit_event=short_circuit_event,
    )


def _format_assignment_sources_for_prompt(
    assignment_sources: list[AssignmentRequirementExtractionSource],
) -> str:
    """Format assignment rows into stable prompt text for external providers."""
    if not assignment_sources:
        return "(No assignment records are stored for this session.)"

    formatted_records: list[str] = []
    for assignment_source in assignment_sources:
        formatted_records.append(
            "\n".join(
                [
                    f"Assignment requirement ID: {assignment_source.assignment_requirement_id}",
                    f"Assignment title: {assignment_source.assignment_title}",
                    f"Assignment description: {assignment_source.assignment_description}",
                ]
            )
        )
    return "\n\n".join(formatted_records)
