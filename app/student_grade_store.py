"""Write-oriented data access for persisted student grading payloads."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from app.schemas import GradeConceptsResponse
from app.telemetry import emit_event


def save_student_concept_grade_json(
    *,
    database_path: Path,
    session_id: str,
    assignment_requirement_id: str,
    student_id: str,
    concept_grade_response: GradeConceptsResponse,
    trace_id: str,
    review_id: str | None = None,
) -> None:
    """Upsert the full concept grading response into student_grades.concept_grade."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_student_concept_grade_json.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
        details={
            "student_id": student_id,
            "assignment_requirement_id": assignment_requirement_id,
        },
    )
    concept_grade_json = json.dumps(concept_grade_response.model_dump(mode="json"))
    grade_id = f"student-grade-{session_id}-{assignment_requirement_id}-{student_id}"
    created_at = datetime.now(UTC).isoformat()
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            INSERT INTO student_grades (
                id,
                session_content_id,
                assignment_requirement_id,
                student_id,
                concept_grade,
                assignment_requirement_grade,
                rubric_grade,
                created_at
            ) VALUES (?, ?, ?, ?, ?, '[]', '[]', ?)
            ON CONFLICT (session_content_id, assignment_requirement_id, student_id)
            DO UPDATE SET concept_grade = excluded.concept_grade
            """,
            (
                grade_id,
                session_id,
                assignment_requirement_id,
                student_id,
                concept_grade_json,
                created_at,
            ),
        )
        connection.commit()
    except sqlite3.Error as exc:
        connection.rollback()
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="save_student_concept_grade_json.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
            details={
                "student_id": student_id,
                "assignment_requirement_id": assignment_requirement_id,
            },
        )
        raise
    finally:
        connection.close()

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_student_concept_grade_json.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
        details={
            "student_id": student_id,
            "assignment_requirement_id": assignment_requirement_id,
            "concept_score_count": len(concept_grade_response.concept_scores),
        },
    )
