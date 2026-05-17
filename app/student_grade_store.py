"""Write-oriented data access for persisted student grading payloads."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from app.schemas import ConceptScoreResult
from app.telemetry import emit_event


def save_student_concept_scores(
    *,
    database_path: Path,
    session_id: str,
    submission_id: str,
    concept_scores: list[ConceptScoreResult],
    trace_id: str,
    review_id: str | None = None,
) -> None:
    """Upsert persisted concept scores for one submission into student_grades."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_student_concept_scores.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
        details={"submission_id": submission_id},
    )
    concept_scores_json = json.dumps(
        [concept_score.model_dump(mode="json") for concept_score in concept_scores]
    )
    grade_id = f"student-grade-{submission_id}"
    created_at = datetime.now(UTC).isoformat()
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            INSERT INTO student_grades (
                id,
                submission_id,
                concept_scores,
                assignment_requirement_scores,
                rubric_scores,
                created_at
            ) VALUES (?, ?, ?, '[]', '[]', ?)
            ON CONFLICT (submission_id)
            DO UPDATE SET concept_scores = excluded.concept_scores
            """,
            (
                grade_id,
                submission_id,
                concept_scores_json,
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
            step_name="save_student_concept_scores.query_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
            details={"submission_id": submission_id},
        )
        raise
    finally:
        connection.close()

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_student_concept_scores.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
        details={
            "submission_id": submission_id,
            "concept_score_count": len(concept_scores),
        },
    )
