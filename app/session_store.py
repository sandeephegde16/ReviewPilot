"""Read-only data access for session, student, and submission content."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from time import perf_counter

from app.schemas import (
    AssignmentRequirementExtractionSource,
    SessionExtractionSource,
    SessionSubmission,
    SessionSummary,
    StudentSubmission,
)
from app.telemetry import emit_event


class SessionNotFoundError(Exception):
    """Raised when a requested session does not exist."""


class StudentNotFoundError(Exception):
    """Raised when a requested student does not exist."""


def _build_read_only_uri(database_path: Path) -> str:
    """Build a read-only SQLite URI for the configured database path."""
    return f"file:{database_path.resolve()}?mode=ro"


def list_session_summaries(
    *,
    database_path: Path,
    trace_id: str,
    review_id: str | None = None,
) -> list[SessionSummary]:
    """Fetch all stored session titles and topics from SQLite."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_session_summaries.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(_build_read_only_uri(database_path), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT session_title, session_topic
            FROM session_content
            ORDER BY created_at DESC, id ASC
            """
        ).fetchall()
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            step_name="list_session_summaries.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
        )
        raise
    finally:
        connection.close()

    session_summaries = [SessionSummary.model_validate(dict(row)) for row in rows]
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_session_summaries.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return session_summaries


def get_session_extraction_source(
    *,
    database_path: Path,
    session_id: str,
    trace_id: str,
    review_id: str | None = None,
) -> SessionExtractionSource:
    """Fetch one session and the fields required for concept extraction."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="get_session_extraction_source.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(_build_read_only_uri(database_path), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            """
            SELECT id, session_title, session_topic, session_transcript
            FROM session_content
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
        if row is None:
            elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
            emit_event(
                trace_id=trace_id,
                review_id=review_id,
                session_id=session_id,
                step_name="get_session_extraction_source.session_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="session_not_found",
            )
            raise SessionNotFoundError(session_id)
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="get_session_extraction_source.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
        )
        raise
    finally:
        connection.close()

    extraction_source = SessionExtractionSource.model_validate(dict(row))
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="get_session_extraction_source.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return extraction_source


def list_session_assignment_requirement_sources(
    *,
    database_path: Path,
    session_id: str,
    trace_id: str,
    review_id: str | None = None,
) -> list[AssignmentRequirementExtractionSource]:
    """Fetch assignment requirement rows linked to one session."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="list_session_assignment_requirement_sources.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(_build_read_only_uri(database_path), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        session_exists = connection.execute(
            """
            SELECT 1
            FROM session_content
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
        if session_exists is None:
            elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
            emit_event(
                trace_id=trace_id,
                review_id=review_id,
                session_id=session_id,
                step_name="list_session_assignment_requirement_sources.session_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="session_not_found",
            )
            raise SessionNotFoundError(session_id)

        rows = connection.execute(
            """
            SELECT
              assignment_requirement.id AS assignment_requirement_id,
              assignment_requirement.assignment_title AS assignment_title,
              assignment_requirement.assignment_description AS assignment_description
            FROM assignment_requirement
            WHERE assignment_requirement.session_content_id = ?
            ORDER BY assignment_requirement.created_at ASC, assignment_requirement.id ASC
            """,
            (session_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="list_session_assignment_requirement_sources.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
        )
        raise
    finally:
        connection.close()

    assignment_sources = [
        AssignmentRequirementExtractionSource.model_validate(dict(row)) for row in rows
    ]
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="list_session_assignment_requirement_sources.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return assignment_sources


def list_session_submissions(
    *,
    database_path: Path,
    session_id: str,
    trace_id: str,
    review_id: str | None = None,
) -> list[SessionSubmission]:
    """Fetch all assignment submissions linked to a single session."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_session_submissions.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(_build_read_only_uri(database_path), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        # A missing session and a session with no submissions both yield zero joined rows,
        # so we validate the session identifier first to keep the API contract explicit.
        session_exists = connection.execute(
            """
            SELECT 1
            FROM session_content
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
        if session_exists is None:
            elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
            emit_event(
                trace_id=trace_id,
                review_id=review_id,
                step_name="list_session_submissions.session_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="session_not_found",
            )
            raise SessionNotFoundError(session_id)

        rows = connection.execute(
            """
            SELECT
              assignment_submissions.id AS submission_id,
              assignment_requirement.id AS assignment_requirement_id,
              assignment_requirement.assignment_title AS assignment_title,
              assignment_requirement.due_at AS due_at,
              students.id AS student_id,
              students.student_code AS student_code,
              students.full_name AS student_full_name,
              assignment_submissions.source_type AS source_type,
              assignment_submissions.repo_url AS repo_url,
              assignment_submissions.local_path AS local_path,
              assignment_submissions.zip_path AS zip_path,
              assignment_submissions.youtube_demo_url AS youtube_demo_url,
              assignment_submissions.linkedin_url AS linkedin_url,
              assignment_submissions.status AS status,
              assignment_submissions.submitted_at AS submitted_at
            FROM assignment_requirement
            JOIN assignment_submissions
              ON assignment_submissions.assignment_requirement_id = assignment_requirement.id
            JOIN students
              ON students.id = assignment_submissions.student_id
            WHERE assignment_requirement.session_content_id = ?
            ORDER BY assignment_submissions.submitted_at DESC, assignment_submissions.id ASC
            """,
            (session_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            step_name="list_session_submissions.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
        )
        raise
    finally:
        connection.close()

    session_submissions = [SessionSubmission.model_validate(dict(row)) for row in rows]
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_session_submissions.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return session_submissions


def list_student_submissions(
    *,
    database_path: Path,
    student_id: str,
    trace_id: str,
    review_id: str | None = None,
) -> list[StudentSubmission]:
    """Fetch all assignment submissions linked to a single student."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_student_submissions.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(_build_read_only_uri(database_path), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        # A missing student and a student with no submissions both yield zero joined rows,
        # so we validate the student identifier first to keep the API contract explicit.
        student_exists = connection.execute(
            """
            SELECT 1
            FROM students
            WHERE id = ?
            """,
            (student_id,),
        ).fetchone()
        if student_exists is None:
            elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
            emit_event(
                trace_id=trace_id,
                review_id=review_id,
                step_name="list_student_submissions.student_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="student_not_found",
            )
            raise StudentNotFoundError(student_id)

        rows = connection.execute(
            """
            SELECT
              assignment_submissions.id AS submission_id,
              session_content.id AS session_id,
              session_content.session_title AS session_title,
              session_content.session_topic AS session_topic,
              assignment_requirement.id AS assignment_requirement_id,
              assignment_requirement.assignment_title AS assignment_title,
              assignment_requirement.due_at AS due_at,
              students.id AS student_id,
              students.student_code AS student_code,
              students.full_name AS student_full_name,
              assignment_submissions.source_type AS source_type,
              assignment_submissions.repo_url AS repo_url,
              assignment_submissions.local_path AS local_path,
              assignment_submissions.zip_path AS zip_path,
              assignment_submissions.youtube_demo_url AS youtube_demo_url,
              assignment_submissions.linkedin_url AS linkedin_url,
              assignment_submissions.status AS status,
              assignment_submissions.submitted_at AS submitted_at
            FROM assignment_submissions
            JOIN assignment_requirement
              ON assignment_requirement.id = assignment_submissions.assignment_requirement_id
            JOIN session_content
              ON session_content.id = assignment_requirement.session_content_id
            JOIN students
              ON students.id = assignment_submissions.student_id
            WHERE assignment_submissions.student_id = ?
            ORDER BY assignment_submissions.submitted_at DESC, assignment_submissions.id ASC
            """,
            (student_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            step_name="list_student_submissions.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
        )
        raise
    finally:
        connection.close()

    student_submissions = [StudentSubmission.model_validate(dict(row)) for row in rows]
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        step_name="list_student_submissions.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return student_submissions
