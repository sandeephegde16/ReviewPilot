"""Write-oriented data access for stored assignment requirements."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from time import perf_counter

from app.schemas import AssignmentRequirementExtractionResult, StoredAssignmentRequirementResult
from app.session_store import SessionNotFoundError
from app.telemetry import emit_event

EMPTY_ASSIGNMENT_REQUIREMENTS_JSON = json.dumps([])


class StoredAssignmentRequirementNotFoundError(Exception):
    """Raised when a stored assignment requirement update targets a missing row."""


def save_assignment_requirement_requirements_json(
    *,
    database_path: Path,
    session_id: str,
    assignment_requirements: list[AssignmentRequirementExtractionResult],
    trace_id: str,
    review_id: str | None = None,
) -> None:
    """Persist extracted requirement lists back to their assignment_requirement rows."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_assignment_requirement_requirements_json.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(database_path)
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
                step_name="save_session_assignment_requirements_document.session_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="session_not_found",
            )
            raise SessionNotFoundError(session_id)

        connection.execute(
            """
            UPDATE assignment_requirement
            SET assignment_requirements_json = ?
            WHERE session_content_id = ?
            """,
            (EMPTY_ASSIGNMENT_REQUIREMENTS_JSON, session_id),
        )
        for assignment_requirement in assignment_requirements:
            requirements_json = json.dumps(
                [
                    requirement.model_dump(mode="json")
                    for requirement in assignment_requirement.requirements
                ]
            )
            cursor = connection.execute(
                """
                UPDATE assignment_requirement
                SET assignment_requirements_json = ?
                WHERE id = ? AND session_content_id = ?
                """,
                (
                    requirements_json,
                    assignment_requirement.assignment_requirement_id,
                    session_id,
                ),
            )
            if cursor.rowcount == 0:
                elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
                emit_event(
                    trace_id=trace_id,
                    review_id=review_id,
                    session_id=session_id,
                    step_name=(
                        "save_assignment_requirement_requirements_json."
                        "assignment_requirement_not_found"
                    ),
                    tool_name=None,
                    data_store="sqlite",
                    provider_name=None,
                    validation_status="failed",
                    retry_count=0,
                    elapsed_ms=elapsed_ms,
                    failure_reason="assignment_requirement_not_found",
                    details={
                        "assignment_requirement_id": (
                            assignment_requirement.assignment_requirement_id
                        )
                    },
                )
                raise sqlite3.IntegrityError(
                    "assignment_requirement_not_found: "
                    f"{assignment_requirement.assignment_requirement_id}"
                )
        connection.commit()
    except sqlite3.Error as exc:
        connection.rollback()
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="save_assignment_requirement_requirements_json.query_failed",
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

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_assignment_requirement_requirements_json.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
        details={"assignment_requirement_count": len(assignment_requirements)},
    )


def save_session_assignment_requirements_document(
    *,
    database_path: Path,
    session_id: str,
    assignment_requirements: list[StoredAssignmentRequirementResult],
    trace_id: str,
    review_id: str | None = None,
) -> None:
    """Persist one UI-edited assignment requirements document for a session."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_session_assignment_requirements_document.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            UPDATE assignment_requirement
            SET assignment_requirements_json = ?
            WHERE session_content_id = ?
            """,
            (EMPTY_ASSIGNMENT_REQUIREMENTS_JSON, session_id),
        )
        for assignment_requirement in assignment_requirements:
            requirements_json = json.dumps(
                [
                    requirement.model_dump(mode="json")
                    for requirement in assignment_requirement.requirements
                ]
            )
            cursor = connection.execute(
                """
                UPDATE assignment_requirement
                SET assignment_requirements_json = ?
                WHERE id = ? AND session_content_id = ?
                """,
                (
                    requirements_json,
                    assignment_requirement.assignment_requirement_id,
                    session_id,
                ),
            )
            if cursor.rowcount == 0:
                elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
                emit_event(
                    trace_id=trace_id,
                    review_id=review_id,
                    session_id=session_id,
                    step_name=(
                        "save_session_assignment_requirements_document."
                        "assignment_requirement_not_found"
                    ),
                    tool_name=None,
                    data_store="sqlite",
                    provider_name=None,
                    validation_status="failed",
                    retry_count=0,
                    elapsed_ms=elapsed_ms,
                    failure_reason="assignment_requirement_not_found",
                    details={
                        "assignment_requirement_id": (
                            assignment_requirement.assignment_requirement_id
                        )
                    },
                )
                raise StoredAssignmentRequirementNotFoundError(
                    assignment_requirement.assignment_requirement_id
                )
        connection.commit()
    except (SessionNotFoundError, StoredAssignmentRequirementNotFoundError):
        connection.rollback()
        raise
    except sqlite3.Error as exc:
        connection.rollback()
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="save_session_assignment_requirements_document.query_failed",
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

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_session_assignment_requirements_document.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
        details={"assignment_requirement_count": len(assignment_requirements)},
    )
