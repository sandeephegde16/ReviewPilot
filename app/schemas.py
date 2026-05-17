"""Pydantic schemas used by the ReviewPilot API."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

ReasoningLevel = Literal["low", "medium", "high"]
SubmissionSourceType = Literal["github_pr", "local_folder", "zip_upload"]
CoverageLevel = Literal["missing", "weak", "partial", "strong"]
REVIEW_ITEM_MIN_SCORE = 25
REVIEW_ITEM_MAX_SCORE = 50
SubmissionStatus = Literal[
    "submitted",
    "under_review",
    "concepts_graded",
    "assignment_requirements_graded",
    "reviewed",
    "needs_resubmission",
]


def _normalize_review_score(value: int) -> int:
    """Round scores up to the next multiple of five and enforce the shared score floor."""
    rounded_score = ((max(1, value) + 4) // 5) * 5
    return max(REVIEW_ITEM_MIN_SCORE, rounded_score)


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

    @field_validator("max_score", mode="after")
    @classmethod
    def normalize_max_score(cls, value: int) -> int:
        """Normalize all concept grading criteria to the shared fixed max score."""
        del value
        return REVIEW_ITEM_MAX_SCORE


def _validate_submission_source_fields(
    *,
    source_type: SubmissionSourceType,
    repo_url: str | None,
    local_path: str | None,
    zip_path: str | None,
) -> None:
    """Require the source locator that matches the selected submission source type."""
    if source_type == "github_pr":
        if repo_url is None or local_path is not None or zip_path is not None:
            raise ValueError(
                "github_pr submissions require repo_url and must not include "
                "local_path or zip_path."
            )
        return
    if source_type == "local_folder":
        if local_path is None or repo_url is not None or zip_path is not None:
            raise ValueError(
                "local_folder submissions require local_path and must not include "
                "repo_url or zip_path."
            )
        return
    if zip_path is None or repo_url is not None or local_path is not None:
        raise ValueError(
            "zip_upload submissions require zip_path and must not include repo_url or local_path."
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
        _validate_submission_source_fields(
            source_type=self.source_type,
            repo_url=self.repo_url,
            local_path=self.local_path,
            zip_path=self.zip_path,
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
    requirements: list[ExtractedAssignmentRequirement] = Field(
        default_factory=list,
        description="Stored requirements currently persisted for this assignment.",
    )


class AssignmentRequirementGradingCriterion(BaseModel):
    """One requested assignment requirement and its grading weight for project scoring."""

    requirement_type: AssignmentRequirementType = Field(
        description="Canonical category for the requested assignment requirement."
    )
    title: str = Field(description="Short assignment-requirement label that must be graded.")
    summary: str = Field(description="Brief explanation of what the requirement covers.")
    evidence: list[str] = Field(
        description="Stored assignment evidence that justifies grading this requirement.",
        min_length=1,
    )
    max_score: int = Field(
        ge=1,
        description="Maximum number of points available for this assignment requirement.",
    )

    @field_validator("max_score", mode="after")
    @classmethod
    def normalize_max_score(cls, value: int) -> int:
        """Normalize all requirement grading criteria to the shared fixed max score."""
        del value
        return REVIEW_ITEM_MAX_SCORE


class GradeAssignmentRequirementsRequest(BaseModel):
    """Public request payload for project assignment-requirement grading."""

    student_id: str = Field(description="Unique identifier for the student being graded.")
    session_id: str = Field(description="Unique identifier for the related session.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement being graded."
    )
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
        description="Requested reasoning depth for assignment-requirement grading.",
    )
    requirements: list[AssignmentRequirementGradingCriterion] = Field(
        min_length=1,
        description="Assignment requirements that must be scored against the project evidence.",
    )

    @model_validator(mode="after")
    def validate_source_fields(self) -> GradeAssignmentRequirementsRequest:
        """Require the source locator that matches the selected source type."""
        _validate_submission_source_fields(
            source_type=self.source_type,
            repo_url=self.repo_url,
            local_path=self.local_path,
            zip_path=self.zip_path,
        )
        return self


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


class StoredSessionAssignment(BaseModel):
    """Stored assignment metadata for one assignment row in the session."""

    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement record."
    )
    assignment_title: str = Field(description="Stored title for the assignment.")
    assignment_description: str = Field(
        description="Stored assignment description shown in the assignments workspace."
    )
    due_at: str | None = Field(
        default=None,
        description="Stored due date for the assignment, when available.",
    )
    required_deliverables: list[str] = Field(
        default_factory=list,
        description="Stored deliverables associated with the assignment.",
    )


class SessionAssignmentsResponse(BaseModel):
    """Public response payload for stored session assignment metadata."""

    session_id: str = Field(description="Unique identifier for the session.")
    assignments: list[StoredSessionAssignment] = Field(
        default_factory=list,
        description="Stored assignments currently persisted for the session.",
    )


class ConceptScoreResult(BaseModel):
    """One evidence-backed score awarded to a requested grading concept."""

    concept: str = Field(description="Concept label that was graded.")
    score: int = Field(
        ge=REVIEW_ITEM_MIN_SCORE,
        description=(
            "Awarded score for the concept, normalized to a multiple of five between "
            "25 and max_score."
        ),
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

    @field_validator("max_score", mode="after")
    @classmethod
    def normalize_max_score(cls, value: int) -> int:
        """Normalize all concept score outputs to the shared fixed max score."""
        del value
        return REVIEW_ITEM_MAX_SCORE

    @field_validator("score", mode="before")
    @classmethod
    def normalize_score(cls, value: int) -> int:
        """Round awarded concept scores up to the next allowed multiple of five."""
        return _normalize_review_score(value)

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


class AssignmentRequirementScoreResult(BaseModel):
    """One evidence-backed score awarded to a requested assignment requirement."""

    requirement_title: str = Field(description="Assignment requirement label that was graded.")
    requirement_type: AssignmentRequirementType = Field(
        description="Canonical category for the graded assignment requirement."
    )
    score: int = Field(
        ge=REVIEW_ITEM_MIN_SCORE,
        description=(
            "Awarded score for the assignment requirement, normalized to a multiple "
            "of five between 25 and max_score."
        ),
    )
    max_score: int = Field(
        ge=1,
        description="Maximum number of points available for the assignment requirement.",
    )
    coverage_level: CoverageLevel = Field(
        description="Strength of requirement coverage observed in the project evidence."
    )
    evidence: list[str] = Field(
        description="Concrete project evidence supporting the awarded score.",
        min_length=1,
    )
    deductions: list[str] = Field(
        default_factory=list,
        description="Reasons points were not awarded in full.",
    )

    @field_validator("max_score", mode="after")
    @classmethod
    def normalize_max_score(cls, value: int) -> int:
        """Normalize all requirement score outputs to the shared fixed max score."""
        del value
        return REVIEW_ITEM_MAX_SCORE

    @field_validator("score", mode="before")
    @classmethod
    def normalize_score(cls, value: int) -> int:
        """Round awarded requirement scores up to the next allowed multiple of five."""
        return _normalize_review_score(value)

    @model_validator(mode="after")
    def validate_score_range(self) -> AssignmentRequirementScoreResult:
        """Ensure awarded scores never exceed the configured requirement maximum."""
        if self.score > self.max_score:
            raise ValueError("score must be less than or equal to max_score.")
        return self


class AssignmentRequirementGradingOutput(BaseModel):
    """Validated structured output returned by the assignment-requirement grading provider."""

    assignment_requirement_scores: list[AssignmentRequirementScoreResult] = Field(
        description="Assignment-requirement scores derived from the collected project evidence.",
        min_length=1,
    )


@lru_cache(maxsize=1)
def _build_cached_assignment_requirement_grading_output_schema() -> dict[str, Any]:
    """Cache the JSON schema used for structured assignment-requirement grading output."""
    return _inline_local_json_schema_refs(AssignmentRequirementGradingOutput.model_json_schema())


def get_assignment_requirement_grading_output_schema(
    *,
    max_assignment_requirement_scores: int | None = None,
) -> dict[str, Any]:
    """Return a provider schema for assignment-requirement grading with an optional item cap."""
    schema = deepcopy(_build_cached_assignment_requirement_grading_output_schema())
    if max_assignment_requirement_scores is not None:
        schema["properties"]["assignment_requirement_scores"]["maxItems"] = (
            max_assignment_requirement_scores
        )
    return schema


class AssignmentRequirementGradingContext(BaseModel):
    """Internal student, session, and assignment metadata used for requirement grading."""

    submission_id: str = Field(description="Unique identifier for the submission being graded.")
    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable course-visible identifier for the student.")
    student_full_name: str = Field(description="Full name of the student.")
    session_id: str = Field(description="Unique identifier for the session.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement being graded."
    )
    assignment_title: str = Field(
        description="Stored title for the assignment requirement being graded."
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


class AssignmentRequirementGradingSource(AssignmentRequirementGradingContext):
    """Internal grading source passed into canonical assignment-requirement preparation."""

    requirements: list[AssignmentRequirementGradingCriterion] = Field(
        description="Requested assignment requirements for the submission.",
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


class GradeAssignmentRequirementsResponse(BaseModel):
    """Public response payload for scored project assignment requirements."""

    student_id: str = Field(description="Unique identifier for the student.")
    student_code: str = Field(description="Stable course-visible identifier for the student.")
    student_full_name: str = Field(description="Full name of the student.")
    session_id: str = Field(description="Unique identifier for the session.")
    assignment_requirement_id: str = Field(
        description="Unique identifier for the assignment requirement being graded."
    )
    assignment_title: str = Field(
        description="Stored title for the assignment requirement being graded."
    )
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
    assignment_requirement_scores: list[AssignmentRequirementScoreResult] = Field(
        description="Evidence-backed scores for each requested assignment requirement.",
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
    status: SubmissionStatus = Field(description="Current review status for the submission.")
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
    status: SubmissionStatus = Field(description="Current review status for the submission.")
    submitted_at: str = Field(description="Submission timestamp stored in SQLite.")


class ApiError(BaseModel):
    """Machine-readable error details for API failures."""

    code: str = Field(description="Stable error code for the failure type.")
    message: str = Field(description="Human-readable error message.")
    trace_id: str = Field(description="Trace identifier for correlating logs.")


class ApiErrorResponse(BaseModel):
    """Top-level error response payload."""

    error: ApiError


OrchestratorOperation = Literal[
    "synthesize_concepts",
    "synthesize_assignment_requirements",
    "grade_concepts",
    "grade_assignment_requirements",
    "grade_rubrics",
    "grade_all",
]
OrchestratorRefreshPolicy = Literal["reuse_or_missing", "force_refresh"]
OrchestratorToolName = Literal[
    "extract_concepts",
    "extract_assignment_requirements",
    "grade_concepts",
    "grade_assignment_requirements",
]
OrchestratorPlannerResponseType = Literal[
    "TOOL_REQUEST",
    "CONTEXT_UPDATE",
    "FINAL_REVIEW",
    "FALLBACK",
]
OrchestratorPlannerReasoningType = Literal[
    "input_validation",
    "artifact_reuse",
    "prerequisite_planning",
    "grading_plan",
    "composite_grading_plan",
    "state_update",
    "failure_handling",
]
OrchestratorRunStatus = Literal["success", "failed", "partial"]
OrchestratorToolExecutionStatus = Literal["success", "failed"]


class OrchestratorGradingPolicy(BaseModel):
    """Stable grading-policy defaults used by orchestrator grading tools."""

    default_assignment_requirement_max_score: int = Field(
        default=REVIEW_ITEM_MAX_SCORE,
        ge=1,
        description="Default max score applied to stored assignment requirements.",
    )

    @field_validator("default_assignment_requirement_max_score", mode="after")
    @classmethod
    def normalize_default_assignment_requirement_max_score(cls, value: int) -> int:
        """Normalize orchestrator requirement grading defaults to the fixed max score."""
        del value
        return REVIEW_ITEM_MAX_SCORE


class RunReviewOrchestratorRequest(BaseModel):
    """Public request payload for the ReviewPilot conversation-loop orchestrator."""

    operation: OrchestratorOperation = Field(
        description="Requested top-level workflow that the orchestrator should satisfy."
    )
    session_id: str = Field(description="Unique identifier for the related session.")
    student_id: str | None = Field(
        default=None,
        description="Unique identifier for the student when grading work is requested.",
    )
    assignment_requirement_id: str | None = Field(
        default=None,
        description=(
            "Unique identifier for the assignment requirement when requirement grading "
            "or grade_all is requested."
        ),
    )
    source_type: SubmissionSourceType | None = Field(
        default=None,
        description="Submission source type used for grading operations.",
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
        description="Requested reasoning depth for planner and workflow calls.",
    )
    refresh_policy: OrchestratorRefreshPolicy = Field(
        default="reuse_or_missing",
        description="Whether stored artifacts may be reused or must be regenerated.",
    )
    grading_policy: OrchestratorGradingPolicy = Field(
        default_factory=OrchestratorGradingPolicy,
        description="Default score-policy inputs used by orchestrator grading tools.",
    )
    max_turns: int = Field(
        default=6,
        ge=1,
        le=8,
        description="Maximum planner turns allowed before the orchestrator fails closed.",
    )

    @model_validator(mode="after")
    def validate_operation_requirements(self) -> RunReviewOrchestratorRequest:
        """Require the minimum context needed for the requested orchestrator operation."""
        grading_operations = {
            "grade_concepts",
            "grade_assignment_requirements",
            "grade_rubrics",
            "grade_all",
        }
        requirement_scoped_operations = {
            "grade_assignment_requirements",
            "grade_rubrics",
            "grade_all",
        }
        if self.operation in grading_operations:
            if self.student_id is None:
                raise ValueError("Grading operations require student_id.")
            if self.source_type is None:
                raise ValueError("Grading operations require source_type.")
            _validate_submission_source_fields(
                source_type=self.source_type,
                repo_url=self.repo_url,
                local_path=self.local_path,
                zip_path=self.zip_path,
            )
        elif any(
            field is not None
            for field in (
                self.source_type,
                self.repo_url,
                self.local_path,
                self.zip_path,
            )
        ):
            if self.source_type is None:
                raise ValueError("Submission source fields require source_type.")
            _validate_submission_source_fields(
                source_type=self.source_type,
                repo_url=self.repo_url,
                local_path=self.local_path,
                zip_path=self.zip_path,
            )

        if (
            self.operation in requirement_scoped_operations
            and self.assignment_requirement_id is None
        ):
            raise ValueError(
                "grade_assignment_requirements, grade_rubrics, and grade_all "
                "require assignment_requirement_id."
            )
        return self


class OrchestratorPlannerChecks(BaseModel):
    """Self-check summary returned by the planner on each conversation turn."""

    inputs_sufficient: bool = Field(description="Whether the visible inputs are sufficient.")
    allowed_tools_only: bool = Field(
        description="Whether only allowlisted tools were used in the proposed response."
    )
    prerequisites_satisfied_or_planned: bool = Field(
        description="Whether grading prerequisites already exist or are requested earlier."
    )
    duplicate_actions_avoided: bool = Field(
        description="Whether duplicate tool calls were avoided without justification."
    )
    plan_is_minimal: bool = Field(
        description="Whether the returned step or tool selection is minimal."
    )


class OrchestratorPlannerToolCall(BaseModel):
    """One coarse-grained tool call requested by the planner."""

    tool_name: OrchestratorToolName = Field(
        description="Coarse workflow action that the backend should execute."
    )


class OrchestratorPlannerKnowledgeState(BaseModel):
    """Optional planner-visible state snapshot returned in a context-update turn."""

    concepts_present: bool | None = Field(
        default=None,
        description="Whether a reusable concepts document is currently available.",
    )
    assignment_requirements_present: bool | None = Field(
        default=None,
        description="Whether reusable assignment requirements are currently available.",
    )
    concept_scores_present: bool | None = Field(
        default=None,
        description="Whether stored concept scores are currently available.",
    )
    assignment_requirement_scores_present: bool | None = Field(
        default=None,
        description="Whether stored assignment-requirement scores are currently available.",
    )
    concept_extraction_completed: bool | None = Field(
        default=None,
        description="Whether concept extraction is complete for the requested run.",
    )
    assignment_requirement_extraction_completed: bool | None = Field(
        default=None,
        description="Whether assignment-requirement extraction is complete.",
    )
    concept_grading_completed: bool | None = Field(
        default=None,
        description="Whether concept grading is complete for the requested run.",
    )
    assignment_requirement_grading_completed: bool | None = Field(
        default=None,
        description="Whether assignment-requirement grading is complete.",
    )
    next_goal: str | None = Field(
        default=None,
        description="Optional short summary of the next planner goal.",
    )


class OrchestratorPlannerContextUpdate(BaseModel):
    """Optional state summary returned by the planner between tool requests."""

    knowledge_state: OrchestratorPlannerKnowledgeState | None = Field(
        default=None,
        description="Planner-visible knowledge summary after considering prior tool results.",
    )
    next_goal: str = Field(description="Short description of the next planner objective.")


class OrchestratorPlannerFinalReview(BaseModel):
    """Planner-authored terminal review summary for one orchestrator run."""

    status: Literal["success", "partial"] = Field(
        description="Planner-selected terminal status when the completion condition is met."
    )
    summary: str = Field(description="Concise explanation of why the run can terminate.")


class OrchestratorPlannerErrorDetails(BaseModel):
    """Closed structured metadata returned for fallback planner errors."""

    missing_inputs: list[str] = Field(
        default_factory=list,
        description="Any required inputs that prevented the planner from proceeding.",
    )
    failed_tools: list[OrchestratorToolName] = Field(
        default_factory=list,
        description="Any coarse workflow tools that failed before fallback was returned.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Additional machine-readable error notes for the failed planner turn.",
    )


class OrchestratorPlannerError(BaseModel):
    """Machine-readable planner error returned on failed turns."""

    error_code: str | None = Field(
        default=None,
        description="Stable failure code when the planner cannot continue.",
    )
    message: str | None = Field(
        default=None,
        description="Human-readable error message for planner failure states.",
    )
    details: OrchestratorPlannerErrorDetails | None = Field(
        default=None,
        description="Optional structured error metadata for planner failures.",
    )


class OrchestratorPlannerTurnOutput(BaseModel):
    """Validated structured planner output for one orchestrator conversation turn."""

    response_type: OrchestratorPlannerResponseType = Field(
        description="Conversation-loop response type selected by the planner."
    )
    reasoning_type: OrchestratorPlannerReasoningType = Field(
        description="Canonical reasoning category used for this planner turn."
    )
    reasoning_summary: str = Field(
        description="Brief visible explanation of the planner's decision for this turn."
    )
    checks: OrchestratorPlannerChecks = Field(
        description="Planner self-check results for the returned turn."
    )
    tool_calls: list[OrchestratorPlannerToolCall] = Field(
        default_factory=list,
        description="Tool calls requested when response_type is TOOL_REQUEST.",
    )
    context_update: OrchestratorPlannerContextUpdate | None = Field(
        default=None,
        description="Optional context update returned when response_type is CONTEXT_UPDATE.",
    )
    final_review: OrchestratorPlannerFinalReview | None = Field(
        default=None,
        description="Optional terminal review returned when response_type is FINAL_REVIEW.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Planner warnings observed while building the turn response.",
    )
    error: OrchestratorPlannerError = Field(
        default_factory=OrchestratorPlannerError,
        description="Structured fallback details for FALLBACK turns.",
    )

    @model_validator(mode="after")
    def validate_turn_shape(self) -> OrchestratorPlannerTurnOutput:
        """Require the fields that correspond to the selected planner response type."""
        if self.response_type == "TOOL_REQUEST":
            if not self.tool_calls:
                raise ValueError("TOOL_REQUEST responses require at least one tool_calls entry.")
            if self.context_update is not None or self.final_review is not None:
                raise ValueError(
                    "TOOL_REQUEST responses must not include context_update or final_review."
                )
            return self
        if self.response_type == "CONTEXT_UPDATE":
            if self.context_update is None:
                raise ValueError(
                    "CONTEXT_UPDATE responses require a context_update payload."
                )
            if self.tool_calls or self.final_review is not None:
                raise ValueError(
                    "CONTEXT_UPDATE responses must not include tool_calls or final_review."
                )
            return self
        if self.response_type == "FINAL_REVIEW":
            if self.final_review is None:
                raise ValueError("FINAL_REVIEW responses require final_review.")
            if self.tool_calls or self.context_update is not None:
                raise ValueError(
                    "FINAL_REVIEW responses must not include tool_calls or context_update."
                )
            return self
        if self.tool_calls or self.context_update is not None or self.final_review is not None:
            raise ValueError(
                "FALLBACK responses must not include tool_calls, context_update, or final_review."
            )
        if self.error.error_code is None or self.error.message is None:
            raise ValueError("FALLBACK responses require error_code and message.")
        return self


@lru_cache(maxsize=1)
def _build_cached_orchestrator_planner_output_schema() -> dict[str, Any]:
    """Cache the JSON schema used for planner turn structured output."""
    return _inline_local_json_schema_refs(OrchestratorPlannerTurnOutput.model_json_schema())


def get_orchestrator_planner_output_schema() -> dict[str, Any]:
    """Return a provider-compatible JSON schema for one planner turn output."""
    return deepcopy(_build_cached_orchestrator_planner_output_schema())


class OrchestratorPlannerTurnRecord(BaseModel):
    """Persisted planner-turn summary returned in the public orchestrator response."""

    turn_number: int = Field(description="1-based planner turn number.")
    response_type: OrchestratorPlannerResponseType = Field(
        description="Planner response type returned for the turn."
    )
    reasoning_type: OrchestratorPlannerReasoningType = Field(
        description="Reasoning category selected by the planner."
    )
    reasoning_summary: str = Field(
        description="Visible explanation of the planner's decision for the turn."
    )
    checks: OrchestratorPlannerChecks = Field(description="Planner self-check results.")
    tool_calls: list[OrchestratorPlannerToolCall] = Field(
        default_factory=list,
        description="Tool calls requested on the planner turn.",
    )
    context_update: OrchestratorPlannerContextUpdate | None = Field(
        default=None,
        description="Optional state-update summary returned by the planner.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Planner warnings captured on the turn.",
    )
    error: OrchestratorPlannerError = Field(
        default_factory=OrchestratorPlannerError,
        description="Structured planner failure details for the turn.",
    )


class OrchestratorToolExecutionResult(BaseModel):
    """Public summary of one tool execution performed by the orchestrator."""

    tool_name: OrchestratorToolName = Field(
        description="Coarse workflow action executed by the backend."
    )
    status: OrchestratorToolExecutionStatus = Field(
        description="Outcome for the executed tool call."
    )
    output_summary: str = Field(description="Short machine-visible summary of the tool result.")
    error_code: str | None = Field(
        default=None,
        description="Stable failure code when the tool execution failed.",
    )
    error_message: str | None = Field(
        default=None,
        description="Human-readable tool execution error message when applicable.",
    )


class ReviewOrchestratorExecutionResult(BaseModel):
    """Aggregated exact workflow responses returned by the orchestrator."""

    extract_concepts_response: ExtractConceptsResponse | None = Field(
        default=None,
        description="Embedded exact response from the concept extraction workflow.",
    )
    extract_assignment_requirements_response: ExtractAssignmentRequirementsResponse | None = (
        Field(
            default=None,
            description=(
                "Embedded exact response from the assignment-requirement extraction workflow."
            ),
        )
    )
    grade_concepts_response: GradeConceptsResponse | None = Field(
        default=None,
        description="Embedded exact response from the concept grading workflow.",
    )
    grade_assignment_requirements_response: GradeAssignmentRequirementsResponse | None = Field(
        default=None,
        description=(
            "Embedded exact response from the assignment-requirement grading workflow."
        ),
    )


class RunReviewOrchestratorResponse(BaseModel):
    """Public response payload for a completed orchestrator run."""

    trace_id: str = Field(description="Trace identifier for correlating orchestrator events.")
    requested_operation: OrchestratorOperation = Field(
        description="Requested top-level workflow that the orchestrator attempted."
    )
    status: OrchestratorRunStatus = Field(description="Terminal orchestrator run status.")
    reasoning_type: OrchestratorPlannerReasoningType = Field(
        description="Reasoning category used on the terminal planner turn."
    )
    reasoning_summary: str = Field(
        description="Visible explanation from the terminal planner turn."
    )
    planner_turns: list[OrchestratorPlannerTurnRecord] = Field(
        default_factory=list,
        description="Planner turn history captured during the conversation loop.",
    )
    tool_results: list[OrchestratorToolExecutionResult] = Field(
        default_factory=list,
        description="Executed coarse tool results in the order they were run.",
    )
    result: ReviewOrchestratorExecutionResult = Field(
        default_factory=ReviewOrchestratorExecutionResult,
        description="Aggregated exact workflow responses produced or reused by the run.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Orchestrator-level warnings collected across planner turns.",
    )
    error: OrchestratorPlannerError = Field(
        default_factory=OrchestratorPlannerError,
        description="Structured terminal failure details when the run does not succeed.",
    )
