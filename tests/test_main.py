"""API tests for the ReviewPilot FastAPI app."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.logging_config import configure_logging
from app.main import app


def _build_test_database(database_path: Path) -> None:
    """Create a temporary SQLite database with session seed data."""
    schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(schema_path.read_text())
        connection.executemany(
            """
            INSERT INTO session_content (
                id,
                course_code,
                session_title,
                session_topic,
                session_transcript,
                concepts_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "session-older",
                    "EAG-V3",
                    "Foundations",
                    "Intro to agent workflows",
                    None,
                    json.dumps(["agents", "tools"]),
                    "2026-05-10T09:00:00+05:30",
                ),
                (
                    "session-newer",
                    "EAG-V3",
                    "Advanced MCP",
                    "MCP transports and tool registration",
                    None,
                    json.dumps(["mcp", "transport"]),
                    "2026-05-11T09:00:00+05:30",
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def test_get_all_sessions_returns_session_titles_and_topics(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /allsessions should return ordered session summaries."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get("/allsessions", headers={"X-Trace-Id": "trace-success"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "session_title": "Advanced MCP",
            "session_topic": "MCP transports and tool registration",
        },
        {
            "session_title": "Foundations",
            "session_topic": "Intro to agent workflows",
        },
    ]


def test_get_all_sessions_returns_structured_error_for_missing_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /allsessions should return a structured error when the DB is unavailable."""
    missing_database_path = tmp_path / "missing.db"
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(missing_database_path))
    client = TestClient(app)

    response = client.get("/allsessions", headers={"X-Trace-Id": "trace-failure"})

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "session_query_failed",
            "message": "Unable to fetch session summaries.",
            "trace_id": "trace-failure",
        }
    }


def test_get_all_sessions_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GET /allsessions should emit JSON telemetry lines to stdout."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.get("/allsessions", headers={"X-Trace-Id": "trace-telemetry"})

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "get_all_sessions.request_received",
        "list_session_summaries.query_started",
        "list_session_summaries.query_completed",
        "get_all_sessions.request_completed",
    ]
    assert all(event["trace_id"] == "trace-telemetry" for event in telemetry_events)
    assert all(event["tool_name"] is None for event in telemetry_events)
    assert all(event["data_store"] == "sqlite" for event in telemetry_events)
