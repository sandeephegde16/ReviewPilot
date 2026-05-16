"""Pydantic schemas used by the ReviewPilot API."""

from copy import deepcopy
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field

ReasoningLevel = Literal["low", "medium", "high"]


class SessionSummary(BaseModel):
    """Public response model for a session summary."""

    session_title: str = Field(description="Stored title for the session.")
    session_topic: str = Field(description="Stored topic summary for the session.")


class SessionExtractionSource(BaseModel):
    """Internal model for session data used during concept extraction."""

    id: str = Field(description="Unique identifier for the session.")
    session_title: str = Field(description="Stored title for the session.")
    session_topic: str = Field(description="Stored topic summary for the session.")
    session_transcript: str | None = Field(
        default=None,
        description="Raw transcript payload stored for the session.",
    )


class ExtractConceptsRequest(BaseModel):
    """Public request payload for gradeable concept extraction."""

    reasoning_level: ReasoningLevel = Field(
        default="medium",
        description="Requested reasoning depth for concept extraction.",
    )


class ApiWarning(BaseModel):
    """Machine-readable warning details for partial fallbacks."""

    code: str = Field(description="Stable warning code.")
    message: str = Field(description="Human-readable warning message.")


class GradeableConcept(BaseModel):
    """Public response model for one extracted gradeable concept."""

    name: str = Field(description="Short concept label.")
    summary: str = Field(description="Brief explanation of the concept.")
    grading_reason: str = Field(description="Why this concept is relevant for grading.")
    evidence: list[str] = Field(
        description="Session evidence used to justify the concept.",
        min_length=1,
    )


class ConceptExtractionOutput(BaseModel):
    """Validated structured output returned by the extraction provider."""

    concepts: list[GradeableConcept] = Field(
        description="Gradeable concepts extracted from the session.",
        min_length=1,
    )


@lru_cache(maxsize=1)
def _build_cached_concept_extraction_output_schema() -> dict[str, Any]:
    """Cache the JSON schema used for structured concept extraction output."""
    return _inline_local_json_schema_refs(ConceptExtractionOutput.model_json_schema())


def get_concept_extraction_output_schema() -> dict[str, Any]:
    """Return a copy of the concept extraction output schema for provider requests."""
    return deepcopy(_build_cached_concept_extraction_output_schema())


def _inline_local_json_schema_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline local Pydantic JSON schema references for provider compatibility."""
    schema_copy = deepcopy(schema)
    definitions = schema_copy.pop("$defs", {})
    return _inline_schema_node(schema_copy, definitions)


def _inline_schema_node(
    node: Any,
    definitions: dict[str, Any],
) -> Any:
    """Recursively inline local `$ref` values within a JSON schema node."""
    if isinstance(node, list):
        return [_inline_schema_node(item, definitions) for item in node]
    if not isinstance(node, dict):
        return node

    reference = node.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/$defs/"):
        definition_name = reference.removeprefix("#/$defs/")
        referenced_definition = definitions.get(definition_name)
        if referenced_definition is None:
            raise ValueError(f"Missing JSON schema definition for reference: {reference}")
        merged_definition = deepcopy(referenced_definition)
        remaining_fields = {
            key: value for key, value in node.items() if key != "$ref"
        }
        merged_definition.update(remaining_fields)
        return _inline_schema_node(merged_definition, definitions)

    normalized_node = {
        key: _inline_schema_node(value, definitions)
        for key, value in node.items()
        if key != "$defs"
    }
    if normalized_node.get("type") == "object" and "additionalProperties" not in normalized_node:
        normalized_node["additionalProperties"] = False
    return normalized_node


class ExtractConceptsResponse(BaseModel):
    """Public response payload for extracted gradeable concepts."""

    session_id: str = Field(description="Unique identifier for the session.")
    concepts: list[GradeableConcept] = Field(
        description="Gradeable concepts extracted from the session.",
        min_length=1,
    )
    warnings: list[ApiWarning] = Field(
        default_factory=list,
        description="Warnings describing any fallback behavior during extraction.",
    )


class SessionSubmission(BaseModel):
    """Public response model for an assignment submission in a session."""

    submission_id: str = Field(description="Unique identifier for the submission.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the related assignment requirement."
    )
    assignment_title: str = Field(description="Assignment title shown to reviewers.")
    due_at: str | None = Field(
        default=None,
        description="Assignment due date stored for the related requirement.",
    )
    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable student code used by the course.")
    student_full_name: str = Field(description="Full name of the submitting student.")
    source_type: Literal["github_pr", "local_folder", "zip_upload"] = Field(
        description="Submission source type."
    )
    repo_url: str | None = Field(
        default=None,
        description="Repository URL when the source type is github_pr.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local folder path when the source type is local_folder.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Uploaded zip path when the source type is zip_upload.",
    )
    youtube_demo_url: str | None = Field(
        default=None,
        description="Optional demo recording URL provided by the student.",
    )
    linkedin_url: str | None = Field(
        default=None,
        description="Optional LinkedIn URL provided by the student.",
    )
    status: Literal["submitted", "under_review", "reviewed", "needs_resubmission"] = Field(
        description="Current review status for the submission."
    )
    submitted_at: str = Field(description="Submission timestamp stored in SQLite.")


class StudentSubmission(BaseModel):
    """Public response model for an assignment submission for a single student."""

    submission_id: str = Field(description="Unique identifier for the submission.")
    session_id: str = Field(description="Unique identifier for the related session.")
    session_title: str = Field(description="Stored title for the related session.")
    session_topic: str = Field(description="Stored topic summary for the related session.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the related assignment requirement."
    )
    assignment_title: str = Field(description="Assignment title shown to reviewers.")
    due_at: str | None = Field(
        default=None,
        description="Assignment due date stored for the related requirement.",
    )
    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable student code used by the course.")
    student_full_name: str = Field(description="Full name of the submitting student.")
    source_type: Literal["github_pr", "local_folder", "zip_upload"] = Field(
        description="Submission source type."
    )
    repo_url: str | None = Field(
        default=None,
        description="Repository URL when the source type is github_pr.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local folder path when the source type is local_folder.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Uploaded zip path when the source type is zip_upload.",
    )
    youtube_demo_url: str | None = Field(
        default=None,
        description="Optional demo recording URL provided by the student.",
    )
    linkedin_url: str | None = Field(
        default=None,
        description="Optional LinkedIn URL provided by the student.",
    )
    status: Literal["submitted", "under_review", "reviewed", "needs_resubmission"] = Field(
        description="Current review status for the submission."
    )
    submitted_at: str = Field(description="Submission timestamp stored in SQLite.")


class ApiError(BaseModel):
    """Machine-readable error details for API failures."""

    code: str = Field(description="Stable error code for the failure type.")
    message: str = Field(description="Human-readable error message.")
    trace_id: str = Field(description="Trace identifier for correlating logs.")


class ApiErrorResponse(BaseModel):
    """Top-level error response payload."""

    error: ApiError
