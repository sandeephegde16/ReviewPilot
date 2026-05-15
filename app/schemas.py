"""Pydantic schemas used by the ReviewPilot API."""

from typing import Literal

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    """Public response model for a session summary."""

    session_title: str = Field(description="Stored title for the session.")
    session_topic: str = Field(description="Stored topic summary for the session.")


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
