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
            INSERT INTO students (
                id,
                student_code,
                full_name,
                email,
                github_username,
                linkedin_url,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "student-ada",
                    "STU-001",
                    "Ada Lovelace",
                    "ada@example.com",
                    "ada-lovelace",
                    "https://linkedin.com/in/ada-lovelace",
                    "2026-05-09T09:00:00+05:30",
                ),
                (
                    "student-grace",
                    "STU-002",
                    "Grace Hopper",
                    "grace@example.com",
                    "grace-hopper",
                    "https://linkedin.com/in/grace-hopper",
                    "2026-05-09T10:00:00+05:30",
                ),
                (
                    "student-linus",
                    "STU-003",
                    "Linus Torvalds",
                    "linus@example.com",
                    "linus-torvalds",
                    "https://linkedin.com/in/linus-torvalds",
                    "2026-05-09T11:00:00+05:30",
                ),
            ],
        )
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
                (
                    "session-empty",
                    "EAG-V3",
                    "Observability",
                    "Tracing review workflows",
                    None,
                    json.dumps(["telemetry", "logs"]),
                    "2026-05-12T09:00:00+05:30",
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO assignment_requirement (
                id,
                session_content_id,
                assignment_title,
                assignment_description,
                required_deliverables_json,
                rubric_json,
                due_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "assignment-foundations",
                    "session-older",
                    "Agent Basics Project",
                    "Build a basic agent loop.",
                    json.dumps(["README", "demo"]),
                    json.dumps({"correctness": 5, "clarity": 5}),
                    "2026-05-20T23:59:59+05:30",
                    "2026-05-10T10:00:00+05:30",
                ),
                (
                    "assignment-mcp",
                    "session-newer",
                    "MCP Integration Project",
                    "Wire an MCP-backed workflow.",
                    json.dumps(["repo", "tests"]),
                    json.dumps({"tooling": 5, "architecture": 5}),
                    "2026-05-21T23:59:59+05:30",
                    "2026-05-11T10:00:00+05:30",
                ),
                (
                    "assignment-capstone",
                    "session-newer",
                    "Capstone Demo",
                    "Submit a full review pilot walkthrough.",
                    json.dumps(["repo", "video"]),
                    json.dumps({"delivery": 5, "observability": 5}),
                    "2026-05-22T23:59:59+05:30",
                    "2026-05-11T11:00:00+05:30",
                ),
                (
                    "assignment-empty",
                    "session-empty",
                    "Telemetry Drill",
                    "Submit tracing notes.",
                    json.dumps(["notes"]),
                    json.dumps({"coverage": 10}),
                    "2026-05-23T23:59:59+05:30",
                    "2026-05-12T10:00:00+05:30",
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO assignment_submissions (
                id,
                assignment_requirement_id,
                student_id,
                source_type,
                repo_url,
                local_path,
                zip_path,
                youtube_demo_url,
                linkedin_url,
                submitted_at,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "submission-foundations",
                    "assignment-foundations",
                    "student-ada",
                    "zip_upload",
                    None,
                    None,
                    "/tmp/submissions/ada-foundations.zip",
                    "https://youtu.be/ada-foundations",
                    "https://linkedin.com/in/ada-lovelace",
                    "2026-05-11T18:00:00+05:30",
                    "reviewed",
                ),
                (
                    "submission-mcp",
                    "assignment-mcp",
                    "student-ada",
                    "github_pr",
                    "https://github.com/example/ada-mcp-project/pull/12",
                    None,
                    None,
                    "https://youtu.be/ada-mcp",
                    "https://linkedin.com/in/ada-lovelace",
                    "2026-05-12T17:15:00+05:30",
                    "submitted",
                ),
                (
                    "submission-capstone",
                    "assignment-capstone",
                    "student-grace",
                    "local_folder",
                    None,
                    "/tmp/submissions/grace-capstone",
                    None,
                    "https://youtu.be/grace-capstone",
                    "https://linkedin.com/in/grace-hopper",
                    "2026-05-13T10:30:00+05:30",
                    "under_review",
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
            "session_title": "Observability",
            "session_topic": "Tracing review workflows",
        },
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


def test_get_session_submissions_returns_all_submissions_for_session(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/submissions should return submissions for one session."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-newer/submissions",
        headers={"X-Trace-Id": "trace-session-submissions"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "submission_id": "submission-capstone",
            "assignment_requirement_id": "assignment-capstone",
            "assignment_title": "Capstone Demo",
            "due_at": "2026-05-22T23:59:59+05:30",
            "student_id": "student-grace",
            "student_code": "STU-002",
            "student_full_name": "Grace Hopper",
            "source_type": "local_folder",
            "repo_url": None,
            "local_path": "/tmp/submissions/grace-capstone",
            "zip_path": None,
            "youtube_demo_url": "https://youtu.be/grace-capstone",
            "linkedin_url": "https://linkedin.com/in/grace-hopper",
            "status": "under_review",
            "submitted_at": "2026-05-13T10:30:00+05:30",
        },
        {
            "submission_id": "submission-mcp",
            "assignment_requirement_id": "assignment-mcp",
            "assignment_title": "MCP Integration Project",
            "due_at": "2026-05-21T23:59:59+05:30",
            "student_id": "student-ada",
            "student_code": "STU-001",
            "student_full_name": "Ada Lovelace",
            "source_type": "github_pr",
            "repo_url": "https://github.com/example/ada-mcp-project/pull/12",
            "local_path": None,
            "zip_path": None,
            "youtube_demo_url": "https://youtu.be/ada-mcp",
            "linkedin_url": "https://linkedin.com/in/ada-lovelace",
            "status": "submitted",
            "submitted_at": "2026-05-12T17:15:00+05:30",
        },
    ]


def test_get_session_submissions_returns_empty_list_for_session_without_submissions(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/submissions should return an empty list when none exist."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-empty/submissions",
        headers={"X-Trace-Id": "trace-session-empty"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_session_submissions_returns_structured_error_for_missing_session(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/submissions should return a structured 404 for bad ids."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-missing/submissions",
        headers={"X-Trace-Id": "trace-session-missing"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "session_not_found",
            "message": "Unable to find the requested session.",
            "trace_id": "trace-session-missing",
        }
    }


def test_get_session_submissions_returns_structured_error_for_missing_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/submissions should return a structured 500 on DB failure."""
    missing_database_path = tmp_path / "missing.db"
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(missing_database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-newer/submissions",
        headers={"X-Trace-Id": "trace-session-query-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "session_submission_query_failed",
            "message": "Unable to fetch session submissions.",
            "trace_id": "trace-session-query-failure",
        }
    }


def test_get_session_submissions_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GET /sessions/{session_id}/submissions should emit JSON telemetry lines."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.get(
        "/sessions/session-newer/submissions",
        headers={"X-Trace-Id": "trace-session-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "get_session_submissions.request_received",
        "list_session_submissions.query_started",
        "list_session_submissions.query_completed",
        "get_session_submissions.request_completed",
    ]
    assert all(event["trace_id"] == "trace-session-telemetry" for event in telemetry_events)
    assert all(event["tool_name"] is None for event in telemetry_events)
    assert all(event["data_store"] == "sqlite" for event in telemetry_events)


def test_get_student_submissions_returns_all_submissions_for_student(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /students/{student_id}/submissions should return submissions for one student."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/students/student-ada/submissions",
        headers={"X-Trace-Id": "trace-student-submissions"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "submission_id": "submission-mcp",
            "session_id": "session-newer",
            "session_title": "Advanced MCP",
            "session_topic": "MCP transports and tool registration",
            "assignment_requirement_id": "assignment-mcp",
            "assignment_title": "MCP Integration Project",
            "due_at": "2026-05-21T23:59:59+05:30",
            "student_id": "student-ada",
            "student_code": "STU-001",
            "student_full_name": "Ada Lovelace",
            "source_type": "github_pr",
            "repo_url": "https://github.com/example/ada-mcp-project/pull/12",
            "local_path": None,
            "zip_path": None,
            "youtube_demo_url": "https://youtu.be/ada-mcp",
            "linkedin_url": "https://linkedin.com/in/ada-lovelace",
            "status": "submitted",
            "submitted_at": "2026-05-12T17:15:00+05:30",
        },
        {
            "submission_id": "submission-foundations",
            "session_id": "session-older",
            "session_title": "Foundations",
            "session_topic": "Intro to agent workflows",
            "assignment_requirement_id": "assignment-foundations",
            "assignment_title": "Agent Basics Project",
            "due_at": "2026-05-20T23:59:59+05:30",
            "student_id": "student-ada",
            "student_code": "STU-001",
            "student_full_name": "Ada Lovelace",
            "source_type": "zip_upload",
            "repo_url": None,
            "local_path": None,
            "zip_path": "/tmp/submissions/ada-foundations.zip",
            "youtube_demo_url": "https://youtu.be/ada-foundations",
            "linkedin_url": "https://linkedin.com/in/ada-lovelace",
            "status": "reviewed",
            "submitted_at": "2026-05-11T18:00:00+05:30",
        },
    ]


def test_get_student_submissions_returns_empty_list_for_student_without_submissions(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /students/{student_id}/submissions should return an empty list when none exist."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/students/student-linus/submissions",
        headers={"X-Trace-Id": "trace-student-empty"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_student_submissions_returns_structured_error_for_missing_student(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /students/{student_id}/submissions should return a structured 404 for bad ids."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/students/student-missing/submissions",
        headers={"X-Trace-Id": "trace-student-missing"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "student_not_found",
            "message": "Unable to find the requested student.",
            "trace_id": "trace-student-missing",
        }
    }


def test_get_student_submissions_returns_structured_error_for_missing_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /students/{student_id}/submissions should return a structured 500 on DB failure."""
    missing_database_path = tmp_path / "missing.db"
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(missing_database_path))
    client = TestClient(app)

    response = client.get(
        "/students/student-ada/submissions",
        headers={"X-Trace-Id": "trace-student-query-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "student_submission_query_failed",
            "message": "Unable to fetch student submissions.",
            "trace_id": "trace-student-query-failure",
        }
    }


def test_get_student_submissions_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GET /students/{student_id}/submissions should emit JSON telemetry lines."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.get(
        "/students/student-ada/submissions",
        headers={"X-Trace-Id": "trace-student-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "get_student_submissions.request_received",
        "list_student_submissions.query_started",
        "list_student_submissions.query_completed",
        "get_student_submissions.request_completed",
    ]
    assert all(event["trace_id"] == "trace-student-telemetry" for event in telemetry_events)
    assert all(event["tool_name"] is None for event in telemetry_events)
    assert all(event["data_store"] == "sqlite" for event in telemetry_events)
