"""Read-only data access for session content."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from time import perf_counter

from app.schemas import SessionSummary
from app.telemetry import emit_event


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
