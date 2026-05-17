"""Assignment-requirement grading request shaping and workflow specification."""

from __future__ import annotations

import app.assignment_requirement_grading_provider as assignment_requirement_grading_provider
from app.schemas import (
    AssignmentRequirementGradingOutput,
    AssignmentRequirementGradingSource,
    GradeAssignmentRequirementsResponse,
    ReasoningLevel,
    get_assignment_requirement_grading_output_schema,
)
from app.structured_extraction import (
    PreparedExtractionEvent,
    PreparedStructuredExtraction,
    StructuredExtractionSpec,
)

DEFAULT_OPERATION_NAME = "grade_submission_assignment_requirements"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = "project_grading"
DEFAULT_STEP_PREFIX = "grade_submission_assignment_requirements"

ASSIGNMENT_REQUIREMENT_GRADING_SPEC = StructuredExtractionSpec[
    AssignmentRequirementGradingOutput, GradeAssignmentRequirementsResponse
](
    step_prefix=DEFAULT_STEP_PREFIX,
    output_model=AssignmentRequirementGradingOutput,
    schema_failure_code="assignment_requirement_grading_schema_validation_failed",
    schema_failure_message=(
        "Unable to validate the assignment-requirement grading output after schema repair."
    ),
    select_primary_provider=lambda: (
        assignment_requirement_grading_provider.select_assignment_requirement_grading_provider()
    ),
    build_provider=lambda *, provider_name, model_name: (
        assignment_requirement_grading_provider.build_assignment_requirement_grading_provider(
            provider_name=provider_name,
            model_name=model_name,
        )
    ),
    build_provider_candidates=lambda: (
        assignment_requirement_grading_provider.build_assignment_requirement_grading_provider_candidates()
    ),
)


def prepare_assignment_requirement_grading(
    *,
    grading_source: AssignmentRequirementGradingSource,
    reasoning_level: ReasoningLevel,
) -> PreparedStructuredExtraction[
    AssignmentRequirementGradingOutput, GradeAssignmentRequirementsResponse
]:
    """Build the canonical request and response mapper for requirement grading."""
    request = assignment_requirement_grading_provider.CanonicalAssignmentRequirementGradingRequest(
        session_id=grading_source.session_id,
        student_id=grading_source.student_id,
        student_code=grading_source.student_code,
        student_full_name=grading_source.student_full_name,
        operation_name=DEFAULT_OPERATION_NAME,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=assignment_requirement_grading_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_assignment_requirement_grading_output_schema(
            max_assignment_requirement_scores=len(grading_source.requirements)
        ),
        prompt_subject="Student project evidence",
        prompt_input_fields=[
            assignment_requirement_grading_provider.PromptInputField(
                label="Student details",
                value=_format_student_details(grading_source),
            ),
            assignment_requirement_grading_provider.PromptInputField(
                label="Session details",
                value=_format_session_details(grading_source),
            ),
            assignment_requirement_grading_provider.PromptInputField(
                label="Assignment details",
                value=_format_assignment_details(grading_source),
            ),
            assignment_requirement_grading_provider.PromptInputField(
                label="Submission source",
                value=_format_submission_source(grading_source),
            ),
            assignment_requirement_grading_provider.PromptInputField(
                label="Requested assignment requirements",
                value=_format_grading_requirements(grading_source),
            ),
            assignment_requirement_grading_provider.PromptInputField(
                label="Project evidence",
                value=grading_source.project_evidence.summary_text,
            ),
        ],
        system_instruction_lines=[
            (
                "Score each requested assignment requirement independently against "
                "the project evidence."
            ),
            (
                "Return one assignment_requirement_scores entry for each requested "
                "assignment requirement."
            ),
            ("Each score entry must use the exact requested title as requirement_title."),
            "Set score as an integer from 0 to max_score for that requested requirement.",
            "Set coverage_level to one of missing, weak, partial, or strong.",
            "Use only the collected project evidence and do not invent facts.",
            "Evidence entries must quote or closely paraphrase concrete project details.",
            "Deductions must explain missing or weak coverage when full points are not awarded.",
        ],
        repair_guidance_lines=[
            "Return one assignment_requirement_scores entry for every requested requirement.",
            (
                "Each entry must include requirement_title, requirement_type, score, "
                "max_score, coverage_level, evidence, and deductions."
            ),
            "score must be less than or equal to max_score.",
        ],
        repair_output_example={
            "assignment_requirement_scores": [
                {
                    "requirement_title": "MCP-backed workflow",
                    "requirement_type": "mandatory_deliverable",
                    "score": 4,
                    "max_score": 5,
                    "coverage_level": "strong",
                    "evidence": [
                        "README describes the MCP workflow implementation.",
                        "Code registers MCP tools and calls them from the review flow.",
                    ],
                    "deductions": ["Automated validation coverage is limited."],
                }
            ]
        },
        telemetry_details={
            "submission_id": grading_source.submission_id,
            "session_id": grading_source.session_id,
            "student_id": grading_source.student_id,
            "assignment_requirement_id": grading_source.assignment_requirement_id,
            "operation_name": DEFAULT_OPERATION_NAME,
            "reasoning_level": reasoning_level,
            "reasoning_type": DEFAULT_REASONING_TYPE,
            "output_mode": assignment_requirement_grading_provider.DEFAULT_OUTPUT_MODE,
            "requirement_count": len(grading_source.requirements),
            "response_schema_title": "AssignmentRequirementGradingOutput",
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
        project_evidence_summary=grading_source.project_evidence.summary_text,
    )

    return PreparedStructuredExtraction(
        request=request,
        warnings=[],
        build_response=lambda output, response_warnings: GradeAssignmentRequirementsResponse(
            student_id=grading_source.student_id,
            student_code=grading_source.student_code,
            student_full_name=grading_source.student_full_name,
            session_id=grading_source.session_id,
            assignment_requirement_id=grading_source.assignment_requirement_id,
            assignment_title=grading_source.assignment_title,
            source_type=grading_source.source_type,
            repo_url=grading_source.repo_url,
            local_path=grading_source.local_path,
            zip_path=grading_source.zip_path,
            assignment_requirement_scores=output.assignment_requirement_scores,
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


def _format_student_details(grading_source: AssignmentRequirementGradingSource) -> str:
    """Format stable student metadata for the provider prompt."""
    return "\n".join(
        [
            f"Student ID: {grading_source.student_id}",
            f"Student code: {grading_source.student_code}",
            f"Student name: {grading_source.student_full_name}",
        ]
    )


def _format_session_details(grading_source: AssignmentRequirementGradingSource) -> str:
    """Format stable session metadata for the provider prompt."""
    return "\n".join(
        [
            f"Session ID: {grading_source.session_id}",
            f"Session title: {grading_source.session_title}",
            f"Session topic: {grading_source.session_topic}",
        ]
    )


def _format_assignment_details(grading_source: AssignmentRequirementGradingSource) -> str:
    """Format stable assignment metadata for the provider prompt."""
    return "\n".join(
        [
            f"Assignment requirement ID: {grading_source.assignment_requirement_id}",
            f"Assignment title: {grading_source.assignment_title}",
        ]
    )


def _format_submission_source(grading_source: AssignmentRequirementGradingSource) -> str:
    """Format source locator details for the provider prompt."""
    return "\n".join(
        [
            f"source_type: {grading_source.source_type}",
            f"repo_url: {grading_source.repo_url or '(not provided)'}",
            f"local_path: {grading_source.local_path or '(not provided)'}",
            f"zip_path: {grading_source.zip_path or '(not provided)'}",
        ]
    )


def _format_grading_requirements(grading_source: AssignmentRequirementGradingSource) -> str:
    """Format requested assignment requirements into stable prompt text."""
    lines: list[str] = []
    for index, requirement in enumerate(grading_source.requirements, start=1):
        lines.extend(
            [
                f"{index}. Requirement title: {requirement.title}",
                f"   Requirement type: {requirement.requirement_type}",
                f"   Summary: {requirement.summary}",
                f"   Assignment evidence: {' | '.join(requirement.evidence)}",
                f"   Max score: {requirement.max_score}",
            ]
        )
    return "\n".join(lines)
