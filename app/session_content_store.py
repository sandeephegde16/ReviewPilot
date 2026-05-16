"""Write-oriented data access for stored session content."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from time import perf_counter

from app.schemas import GradeableConcept
from app.session_store import SessionNotFoundError
from app.telemetry import emit_event


def save_session_concepts_json(
    *,
    database_path: Path,
    session_id: str,
    concepts: list[GradeableConcept],
    trace_id: str,
    review_id: str | None = None,
) -> None:
    """Persist extracted concepts to the owning session_content row."""
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=review_id,
        session_id=session_id,
        step_name="save_session_concepts_json.query_started",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    concepts_json = json.dumps([concept.model_dump(mode="json") for concept in concepts])
    connection = sqlite3.connect(database_path)
    try:
        cursor = connection.execute(
            """
            UPDATE session_content
            SET concepts_json = ?
            WHERE id = ?
            """,
            (concepts_json, session_id),
        )
        if cursor.rowcount == 0:
            elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
            emit_event(
                trace_id=trace_id,
                review_id=review_id,
                session_id=session_id,
                step_name="save_session_concepts_json.session_not_found",
                tool_name=None,
                data_store="sqlite",
                provider_name=None,
                validation_status="failed",
                retry_count=0,
                elapsed_ms=elapsed_ms,
                failure_reason="session_not_found",
            )
            raise SessionNotFoundError(session_id)
        connection.commit()
    except sqlite3.Error as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=review_id,
            session_id=session_id,
            step_name="save_session_concepts_json.query_failed",
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
        step_name="save_session_concepts_json.query_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
        details={"concept_count": len(concepts)},
    )
