"""Pydantic schemas used by the ReviewPilot API."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

ReasoningLevel = Literal["low", "medium", "high"]
SubmissionSourceType = Literal["github_pr", "local_folder", "zip_upload"]
CoverageLevel = Literal["missing", "weak", "partial", "strong"]


class SessionSummary(BaseModel):
    """Public response model for a session summary."""

    session_id: str = Field(description="Unique identifier for the session.")
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


class AssignmentRequirementExtractionSource(BaseModel):
    """Internal model for assignment rows used during requirement extraction."""

    assignment_requirement_id: str = Field(description="Unique identifier for the assignment.")
    assignment_title: str = Field(description="Stored title for the assignment.")
    assignment_description: str = Field(
        description="Stored description used to extract assignment requirements."
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
    concept_importance: int = Field(
        description=(
            "Importance score from 1 to 10 based on how central the concept is to the session."
        ),
        ge=1,
        le=10,
    )
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


def get_concept_extraction_output_schema(*, max_concepts: int | None = None) -> dict[str, Any]:
    """Return a provider schema for concept extraction with an optional output cap."""
    schema = deepcopy(_build_cached_concept_extraction_output_schema())
    if max_concepts is not None:
        schema["properties"]["concepts"]["maxItems"] = max_concepts
    return schema


class ExtractAssignmentRequirementsRequest(BaseModel):
    """Public request payload for assignment requirement extraction."""

    reasoning_level: ReasoningLevel = Field(
        default="medium",
        description="Requested reasoning depth for assignment requirement extraction.",
    )


class ConceptGradingCriterion(BaseModel):
    """One requested concept and its grading weight for project scoring."""

    concept_name: str = Field(description="Concept label that must be graded.")
    summary: str = Field(description="Short explanation of what the concept covers.")
    grading_reason: str = Field(description="Why this concept matters for grading.")
    max_score: int = Field(
        ge=1,
        description="Maximum number of points available for this concept.",
    )


class GradeConceptsRequest(BaseModel):
    """Public request payload for project concept grading."""

    student_id: str = Field(description="Unique identifier for the student being graded.")
    session_id: str = Field(description="Unique identifier for the related session.")
    source_type: SubmissionSourceType = Field(
        description="Submission source type used to collect project evidence."
    )
    repo_url: str | None = Field(
        default=None,
        description="Repository or pull request URL when the source type is github_pr.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local folder path when the source type is local_folder.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Zip archive path when the source type is zip_upload.",
    )
    reasoning_level: ReasoningLevel = Field(
        default="medium",
        description="Requested reasoning depth for concept grading.",
    )
    concepts: list[ConceptGradingCriterion] = Field(
        min_length=1,
        description="Concepts that must be scored against the project evidence.",
    )

    @model_validator(mode="after")
    def validate_source_fields(self) -> GradeConceptsRequest:
        """Require the source locator that matches the selected source type."""
        if self.source_type == "github_pr":
            if self.repo_url is None or self.local_path is not None or self.zip_path is not None:
                raise ValueError(
                    "github_pr submissions require repo_url and must not include "
                    "local_path or zip_path."
                )
        elif self.source_type == "local_folder":
            if self.local_path is None or self.repo_url is not None or self.zip_path is not None:
                raise ValueError(
                    "local_folder submissions require local_path and must not include "
                    "repo_url or zip_path."
                )
        else:
            if self.zip_path is None or self.repo_url is not None or self.local_path is not None:
                raise ValueError(
                    "zip_upload submissions require zip_path and must not include "
                    "repo_url or local_path."
                )
        return self


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
        remaining_fields = {key: value for key, value in node.items() if key != "$ref"}
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


class UpdateSessionConceptsRequest(BaseModel):
    """Public request payload for replacing the stored session concepts document."""

    concepts: list[GradeableConcept] = Field(
        default_factory=list,
        description="Stored gradeable concepts that should replace the session document.",
    )


class SessionConceptsResponse(BaseModel):
    """Public response payload for the stored session concepts document."""

    session_id: str = Field(description="Unique identifier for the session.")
    concepts: list[GradeableConcept] = Field(
        default_factory=list,
        description="Stored gradeable concepts currently persisted for the session.",
    )


AssignmentRequirementType = Literal[
    "mandatory_deliverable",
    "forbidden_project_type",
    "scoring_criterion",
    "evidence_expectation",
]


class ExtractedAssignmentRequirement(BaseModel):
    """One evidence-backed assignment requirement extracted from assignment text."""

    requirement_type: AssignmentRequirementType = Field(
        description="Canonical category for the extracted assignment requirement."
    )
    title: str = Field(description="Short label for the extracted assignment requirement.")
    summary: str = Field(description="Brief explanation of the requirement.")
    evidence: list[str] = Field(
        description="Assignment title or description evidence supporting the requirement.",
        min_length=1,
    )


class AssignmentRequirementExtractionResult(BaseModel):
    """Extracted requirements for one assignment row in the session."""

    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement record."
    )
    assignment_title: str = Field(description="Stored title for the assignment.")
    requirements: list[ExtractedAssignmentRequirement] = Field(
        description="Extracted requirements for this assignment.",
        min_length=1,
    )


class AssignmentRequirementsExtractionOutput(BaseModel):
    """Validated structured output returned by the assignment extraction provider."""

    assignment_requirements: list[AssignmentRequirementExtractionResult] = Field(
        description="Assignment requirements extracted from stored assignment evidence.",
        min_length=1,
    )


@lru_cache(maxsize=1)
def _build_cached_assignment_requirements_extraction_output_schema() -> dict[str, Any]:
    """Cache the JSON schema used for structured assignment requirement extraction."""
    return _inline_local_json_schema_refs(
        AssignmentRequirementsExtractionOutput.model_json_schema()
    )


def get_assignment_requirements_extraction_output_schema(
    *,
    max_assignment_requirements: int | None = None,
) -> dict[str, Any]:
    """Return a provider schema for assignment extraction with an optional item cap."""
    schema = deepcopy(_build_cached_assignment_requirements_extraction_output_schema())
    if max_assignment_requirements is not None:
        schema["properties"]["assignment_requirements"]["items"]["properties"]["requirements"][
            "maxItems"
        ] = max_assignment_requirements
    return schema


class ExtractAssignmentRequirementsResponse(BaseModel):
    """Public response payload for extracted session assignment requirements."""

    session_id: str = Field(description="Unique identifier for the session.")
    assignment_requirements: list[AssignmentRequirementExtractionResult] = Field(
        description="Assignment requirements extracted from stored assignment evidence."
    )
    warnings: list[ApiWarning] = Field(
        default_factory=list,
        description="Warnings describing any fallback behavior during extraction.",
    )


class StoredAssignmentRequirementResult(BaseModel):
    """Stored requirements for one assignment row in the session."""

    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement record."
    )
    assignment_title: str = Field(description="Stored title for the assignment.")
    assignment_description: str | None = Field(
        default=None,
        description="Stored assignment description shown in the assignments workspace.",
    )
    due_at: str | None = Field(
        default=None,
        description="Stored due date for the assignment requirement, when available.",
    )
    required_deliverables: list[str] = Field(
        default_factory=list,
        description="Stored deliverables associated with the assignment requirement.",
    )
    requirements: list[ExtractedAssignmentRequirement] = Field(
        default_factory=list,
        description="Stored requirements currently persisted for this assignment.",
    )


class UpdateSessionAssignmentRequirementsRequest(BaseModel):
    """Public request payload for replacing stored assignment requirements."""

    assignment_requirements: list[StoredAssignmentRequirementResult] = Field(
        default_factory=list,
        description="Stored assignment requirements that should replace the session document.",
    )


class SessionAssignmentRequirementsResponse(BaseModel):
    """Public response payload for stored session assignment requirements."""

    session_id: str = Field(description="Unique identifier for the session.")
    assignment_requirements: list[StoredAssignmentRequirementResult] = Field(
        default_factory=list,
        description="Stored assignment requirements currently persisted for the session.",
    )


class ConceptScoreResult(BaseModel):
    """One evidence-backed score awarded to a requested grading concept."""

    concept: str = Field(description="Concept label that was graded.")
    score: int = Field(
        ge=0,
        description="Awarded score for the concept.",
    )
    max_score: int = Field(
        ge=1,
        description="Maximum number of points available for the concept.",
    )
    coverage_level: CoverageLevel = Field(
        description="Strength of concept coverage observed in the project evidence."
    )
    evidence: list[str] = Field(
        description="Concrete project evidence supporting the awarded score.",
        min_length=1,
    )
    deductions: list[str] = Field(
        default_factory=list,
        description="Reasons points were not awarded in full.",
    )

    @model_validator(mode="after")
    def validate_score_range(self) -> ConceptScoreResult:
        """Ensure awarded scores never exceed the configured concept maximum."""
        if self.score > self.max_score:
            raise ValueError("score must be less than or equal to max_score.")
        return self


class ConceptGradingOutput(BaseModel):
    """Validated structured output returned by the concept grading provider."""

    concept_scores: list[ConceptScoreResult] = Field(
        description="Concept scores derived from the collected project evidence.",
        min_length=1,
    )


@lru_cache(maxsize=1)
def _build_cached_concept_grading_output_schema() -> dict[str, Any]:
    """Cache the JSON schema used for structured concept grading output."""
    return _inline_local_json_schema_refs(ConceptGradingOutput.model_json_schema())


def get_concept_grading_output_schema(
    *,
    max_concept_scores: int | None = None,
) -> dict[str, Any]:
    """Return a provider schema for concept grading with an optional item cap."""
    schema = deepcopy(_build_cached_concept_grading_output_schema())
    if max_concept_scores is not None:
        schema["properties"]["concept_scores"]["maxItems"] = max_concept_scores
    return schema


class ProjectEvidenceFileSnippet(BaseModel):
    """One bounded file excerpt included in collected project evidence."""

    path: str = Field(description="Repository-relative path for the excerpted file.")
    content_excerpt: str = Field(description="Bounded text excerpt collected from the file.")


class ProjectEvidenceBundle(BaseModel):
    """Collected project evidence prepared before concept grading."""

    project_root: str = Field(description="Resolved local root path for the collected project.")
    file_inventory: list[str] = Field(
        default_factory=list,
        description="Repository-relative file inventory used to ground grading decisions.",
    )
    documentation_snippets: list[ProjectEvidenceFileSnippet] = Field(
        default_factory=list,
        description="Collected documentation excerpts such as README content.",
    )
    implementation_snippets: list[ProjectEvidenceFileSnippet] = Field(
        default_factory=list,
        description="Collected implementation excerpts used for concept grading.",
    )
    test_snippets: list[ProjectEvidenceFileSnippet] = Field(
        default_factory=list,
        description="Collected test excerpts used for concept grading.",
    )
    summary_text: str = Field(
        description="Bounded human-readable summary of the collected project evidence."
    )


class ConceptGradingContext(BaseModel):
    """Internal student, session, and source metadata used for concept grading."""

    submission_id: str = Field(description="Unique identifier for the submission being graded.")
    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable course-visible identifier for the student.")
    student_full_name: str = Field(description="Full name of the student.")
    session_id: str = Field(description="Unique identifier for the session.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement being graded."
    )
    session_title: str = Field(description="Stored title for the related session.")
    session_topic: str = Field(description="Stored topic summary for the related session.")
    source_type: SubmissionSourceType = Field(description="Submission source type.")
    repo_url: str | None = Field(
        default=None,
        description="Repository or pull request URL when the source type is github_pr.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local folder path when the source type is local_folder.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Zip archive path when the source type is zip_upload.",
    )


class ConceptGradingSource(ConceptGradingContext):
    """Internal grading source passed into canonical concept grading preparation."""

    concepts: list[ConceptGradingCriterion] = Field(
        description="Requested concept grading criteria for the submission.",
        min_length=1,
    )
    project_evidence: ProjectEvidenceBundle = Field(
        description="Collected evidence bundle prepared from the project source."
    )


class GradeConceptsResponse(BaseModel):
    """Public response payload for scored project concepts."""

    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable course-visible identifier for the student.")
    student_full_name: str = Field(description="Full name of the student.")
    session_id: str = Field(description="Unique identifier for the session.")
    source_type: SubmissionSourceType = Field(description="Submission source type.")
    repo_url: str | None = Field(
        default=None,
        description="Repository or pull request URL when the source type is github_pr.",
    )
    local_path: str | None = Field(
        default=None,
        description="Local folder path when the source type is local_folder.",
    )
    zip_path: str | None = Field(
        default=None,
        description="Zip archive path when the source type is zip_upload.",
    )
    concept_scores: list[ConceptScoreResult] = Field(
        description="Evidence-backed scores for each requested concept.",
        min_length=1,
    )
    warnings: list[ApiWarning] = Field(
        default_factory=list,
        description="Warnings describing any fallback behavior during grading.",
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
    source_type: SubmissionSourceType = Field(description="Submission source type.")
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
    concept_scores: list[ConceptScoreResult] = Field(
        default_factory=list,
        description="Persisted concept scores currently stored for the submission.",
    )
    assignment_requirement_scores: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Persisted assignment-requirement scores currently stored for the submission.",
    )
    rubric_scores: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Persisted rubric scores currently stored for the submission.",
    )


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
    source_type: SubmissionSourceType = Field(description="Submission source type.")
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
