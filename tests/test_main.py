"""API tests for the ReviewPilot FastAPI app."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.concept_orchestrator as concept_orchestrator
import app.concept_provider as concept_provider
import app.provider_router as provider_router
from app.logging_config import configure_logging
from app.main import app
from app.transcript_parser import normalize_transcript_text


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
                    (
                        "Agents coordinate tools, prompts, and control flow for "
                        "repeatable workflows."
                    ),
                    json.dumps(["agents", "tools"]),
                    "2026-05-10T09:00:00+05:30",
                ),
                (
                    "session-newer",
                    "EAG-V3",
                    "Advanced MCP",
                    "MCP transports and tool registration",
                    json.dumps(
                        [
                            {
                                "speaker": "Instructor",
                                "text": "MCP tool registration connects tools to the runtime.",
                            },
                            {
                                "speaker": "Instructor",
                                "text": (
                                    "Transport setup and schema validation keep "
                                    "integrations reliable."
                                ),
                            },
                        ]
                    ),
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


class _RecordingConceptProvider:
    """Test double for the concept extraction provider interface."""

    provider_name = "test-provider"
    model_name = "test-model"

    def __init__(self, responses: list[dict[str, object]]) -> None:
        """Store canned responses and record incoming requests."""
        self._responses = responses
        self.requests: list[tuple[object, str, object | None]] = []

    def extract_concepts(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Return the next canned response while recording the canonical request."""
        self.requests.append((request, trace_id, repair_context))
        return self._responses.pop(0)


class _RaisingConceptProvider:
    """Test double that raises during provider invocation."""

    def __init__(self, *, provider_name: str, model_name: str, message: str) -> None:
        """Store provider identity and the failure message to raise."""
        self.provider_name = provider_name
        self.model_name = model_name
        self.message = message

    def extract_concepts(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Raise a runtime error to simulate a provider-call failure."""
        del request, trace_id, repair_context
        raise RuntimeError(self.message)


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


def test_extract_session_concepts_returns_concepts_from_transcript(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should return validated concepts."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should be able to wire tools correctly.",
                        "evidence": [
                            "MCP tool registration connects tools to the runtime."
                        ],
                    },
                    {
                        "name": "Schema validation",
                        "summary": "Covers validating tool inputs and outputs.",
                        "grading_reason": "Students should produce reliable structured outputs.",
                        "evidence": [
                            "Transport setup and schema validation keep integrations reliable."
                        ],
                    },
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [provider_router.ProviderCandidate("heuristic", "heuristic-v1")],
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        json={"reasoning_level": "high"},
        headers={"X-Trace-Id": "trace-extract-success"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-newer",
        "concepts": [
            {
                "name": "Tool registration",
                "summary": "Explains how MCP tools are exposed to the runtime.",
                "grading_reason": "Students should be able to wire tools correctly.",
                "evidence": [
                    "MCP tool registration connects tools to the runtime."
                ],
            },
            {
                "name": "Schema validation",
                "summary": "Covers validating tool inputs and outputs.",
                "grading_reason": "Students should produce reliable structured outputs.",
                "evidence": [
                    "Transport setup and schema validation keep integrations reliable."
                ],
            },
        ],
        "warnings": [],
    }
    provider_request, recorded_trace_id, repair_context = provider.requests[0]
    assert recorded_trace_id == "trace-extract-success"
    assert repair_context is None
    assert provider_request.operation_name == concept_orchestrator.DEFAULT_OPERATION_NAME
    assert provider_request.session_id == "session-newer"
    assert provider_request.output_mode == "json_schema_strict"
    assert provider_request.reasoning_level == "high"
    assert provider_request.reasoning_type == "structured_extraction"
    assert provider_request.response_schema["title"] == "ConceptExtractionOutput"
    assert provider_request.response_schema["type"] == "object"
    assert provider_request.response_schema["required"] == ["concepts"]
    assert "concepts" in provider_request.response_schema["properties"]
    assert "MCP tool registration connects tools to the runtime." in (
        provider_request.session_transcript or ""
    )


def test_extract_session_concepts_accepts_plain_text_transcript(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should use raw text transcripts."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Agent workflows",
                        "summary": "Explains how agents coordinate tools and control flow.",
                        "grading_reason": "Students should understand orchestrated workflows.",
                        "evidence": [
                            (
                                "Agents coordinate tools, prompts, and control flow for "
                                "repeatable workflows."
                            )
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [provider_router.ProviderCandidate("heuristic", "heuristic-v1")],
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-older/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-plain-text"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-older",
        "concepts": [
            {
                "name": "Agent workflows",
                "summary": "Explains how agents coordinate tools and control flow.",
                "grading_reason": "Students should understand orchestrated workflows.",
                "evidence": [
                    (
                        "Agents coordinate tools, prompts, and control flow for "
                        "repeatable workflows."
                    )
                ],
            }
        ],
        "warnings": [],
    }
    provider_request, _, repair_context = provider.requests[0]
    assert repair_context is None
    assert (
        "Agents coordinate tools, prompts, and control flow for repeatable workflows."
        in (provider_request.session_transcript or "")
    )


def test_normalize_transcript_text_removes_timestamp_artifacts_and_chunks_long_text() -> None:
    """Transcript normalization should strip subtitle timing noise and retain later content."""
    transcript_payload = (
        "All right, here I am again and today we're going to move uh slightly "
        "0:1010 secondsforward. We're going to talk about MCP which is our model "
        "context protocol and why it was invented. "
        "1:071 minute, 7 secondsare following uh Twitter or LinkedIn you're going to "
        "see that every day there's someone who's just creating new apps. "
        "2:042 minutes, 4 secondsSo creating application is not going to be mo but "
        "creating them on the fly within let's say a second of request is going to be "
        "what is going to be super exciting."
    )

    normalized_transcript = normalize_transcript_text(transcript_payload)

    assert normalized_transcript is not None
    assert "0:1010 seconds" not in normalized_transcript
    assert "1:071 minute, 7 seconds" not in normalized_transcript
    assert "2:042 minutes, 4 seconds" not in normalized_transcript
    assert "forward." in normalized_transcript
    assert "are following" in normalized_transcript
    assert "super exciting." in normalized_transcript
    assert "\n" in normalized_transcript


def test_extract_session_concepts_cleans_timestamp_artifacts_before_provider_call(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Canonical request transcript should be cleaned before provider invocation."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            UPDATE session_content
            SET session_transcript = ?
            WHERE id = ?
            """,
            (
                (
                    "All right, here I am again and today we're going to move uh "
                    "slightly 0:1010 secondsforward. We're going to talk about MCP "
                    "which is our model context protocol and why it was invented. "
                    "1:071 minute, 7 secondsare following uh Twitter or LinkedIn "
                    "you're going to see that every day there's someone who's just "
                    "creating new apps."
                ),
                "session-older",
            ),
        )
        connection.commit()
    finally:
        connection.close()
    provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Agent workflows",
                        "summary": "Explains how agents coordinate tools and control flow.",
                        "grading_reason": "Students should understand orchestrated workflows.",
                        "evidence": [
                            (
                                "All right, here I am again and today we're going "
                                "to move uh slightly forward."
                            )
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [provider_router.ProviderCandidate("heuristic", "heuristic-v1")],
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-older/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-clean-transcript"},
    )

    assert response.status_code == 200
    provider_request, _, repair_context = provider.requests[0]
    assert repair_context is None
    assert provider_request.session_transcript is not None
    assert "0:1010 seconds" not in provider_request.session_transcript
    assert "1:071 minute, 7 seconds" not in provider_request.session_transcript
    assert "forward." in provider_request.session_transcript
    assert "creating new apps." in provider_request.session_transcript


def test_extract_session_concepts_returns_warning_when_transcript_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should fall back to the session topic."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Telemetry workflows",
                        "summary": "Synthesizes the main workflow concept from the topic.",
                        "grading_reason": "Students should understand the core workflow shape.",
                        "evidence": ["Session topic: Tracing review workflows"],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-empty/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-warning"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-empty",
        "concepts": [
            {
                "name": "Telemetry workflows",
                "summary": "Synthesizes the main workflow concept from the topic.",
                "grading_reason": "Students should understand the core workflow shape.",
                "evidence": ["Session topic: Tracing review workflows"],
            }
        ],
        "warnings": [
            {
                "code": "session_transcript_not_available",
                "message": (
                    "Session transcript not available, synthesized concepts are based on "
                    "session topic."
                ),
            }
        ],
    }
    provider_request, _, repair_context = provider.requests[0]
    assert repair_context is None
    assert provider_request.session_transcript is None
    assert provider_request.session_title == "Observability"
    assert provider_request.session_topic == "Tracing review workflows"


def test_extract_session_concepts_repairs_schema_failure_once(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should retry once on schema failure."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should enforce structured contracts.",
                        "evidence": [
                            "Transport setup and schema validation keep integrations reliable."
                        ],
                    }
                ]
            },
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-repair"},
    )

    assert response.status_code == 200
    assert response.json()["concepts"][0]["name"] == "Schema validation"
    assert len(provider.requests) == 2
    repair_request, _, repair_context = provider.requests[1]
    assert repair_request.session_id == "session-newer"
    assert repair_request.output_mode == "json_schema_strict"
    assert repair_context is not None
    assert repair_context.schema_check_failed is True
    assert repair_context.previous_output == {"concepts": [{"name": "Schema validation"}]}
    assert repair_context.validation_errors


def test_extract_session_concepts_returns_structured_error_after_failed_repair(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should fail after repair is exhausted."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {"concepts": [{"name": "Still invalid"}]},
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [provider_router.ProviderCandidate("heuristic", "heuristic-v1")],
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-failed-repair"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "concept_schema_validation_failed",
            "message": "Unable to validate the extracted concepts after schema repair.",
            "trace_id": "trace-extract-failed-repair",
        }
    }


def test_extract_session_concepts_does_not_fall_back_after_failed_schema_repair(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Schema-invalid provider output should fail fast instead of hopping providers."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    primary_provider = _RecordingConceptProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {"concepts": [{"name": "Still invalid"}]},
        ]
    )
    fallback_provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Should not run",
                        "summary": "Fallback provider should never be called here.",
                        "grading_reason": "Schema failure should stop the workflow.",
                        "evidence": ["This response must not be used."],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("gemini", "gemini-2.5-flash"),
        ],
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: primary_provider,
    )

    def _build_fallback_provider(*, provider_name: str, model_name: str):
        assert provider_name == "gemini"
        assert model_name == "gemini-2.5-flash"
        return fallback_provider

    monkeypatch.setattr(
        concept_provider,
        "build_concept_extraction_provider",
        _build_fallback_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-no-fallback-after-schema-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "concept_schema_validation_failed",
            "message": "Unable to validate the extracted concepts after schema repair.",
            "trace_id": "trace-extract-no-fallback-after-schema-failure",
        }
    }
    assert len(primary_provider.requests) == 2
    assert len(fallback_provider.requests) == 0


def test_extract_session_concepts_returns_structured_error_for_missing_session(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should return a structured 404."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-missing/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-missing-session"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "session_not_found",
            "message": "Unable to find the requested session.",
            "trace_id": "trace-extract-missing-session",
        }
    }


def test_extract_session_concepts_returns_structured_error_for_missing_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should return a structured 500 on DB failure."""
    missing_database_path = tmp_path / "missing.db"
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(missing_database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-query-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "session_extraction_source_query_failed",
            "message": "Unable to fetch the session data required for concept extraction.",
            "trace_id": "trace-extract-query-failure",
        }
    }


def test_extract_session_concepts_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """POST /sessions/{session_id}/extract-concepts should emit workflow telemetry."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Telemetry workflows",
                        "summary": "Synthesizes the main workflow concept from the topic.",
                        "grading_reason": "Students should understand the core workflow shape.",
                        "evidence": ["Session topic: Tracing review workflows"],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/sessions/session-empty/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "extract_session_concepts.request_received",
        "get_session_extraction_source.query_started",
        "get_session_extraction_source.query_completed",
        "extract_session_concepts.session_fetched",
        "extract_session_concepts.transcript_fallback_used",
        "extract_session_concepts.canonical_request_built",
        "extract_session_concepts.provider_selection_started",
        "extract_session_concepts.provider_selection_completed",
        "extract_session_concepts.provider_call_started",
        "extract_session_concepts.provider_call_completed",
        "extract_session_concepts.schema_validation_passed",
        "extract_session_concepts.completed",
        "extract_session_concepts.request_completed",
    ]
    assert all(event["trace_id"] == "trace-extract-telemetry" for event in telemetry_events)
    extract_events = [
        event
        for event in telemetry_events
        if event["step_name"].startswith("extract_session_concepts.")
    ]
    assert all(event["session_id"] == "session-empty" for event in extract_events)
    assert all(
        event["tool_name"] == concept_orchestrator.DEFAULT_TOOL_NAME
        for event in extract_events
    )
    assert all(event["reasoning_level"] == "medium" for event in extract_events)
    assert all(
        event["reasoning_type"] == concept_orchestrator.DEFAULT_REASONING_TYPE
        for event in extract_events
    )
    canonical_request_event = telemetry_events[5]
    assert canonical_request_event["provider_name"] is None
    assert canonical_request_event["model_name"] is None
    assert canonical_request_event["details"] == {
        "session_id": "session-empty",
        "operation_name": concept_orchestrator.DEFAULT_OPERATION_NAME,
        "reasoning_level": "medium",
        "reasoning_type": concept_provider.DEFAULT_REASONING_TYPE,
        "output_mode": concept_provider.DEFAULT_OUTPUT_MODE,
        "response_schema_title": "ConceptExtractionOutput",
        "has_session_transcript": False,
        "session_transcript_length": 0,
        "used_transcript_fallback": True,
        "session_title_present": True,
        "session_topic_present": True,
    }
    assert telemetry_events[8]["details"] == {
        "provider_reasoning_level": None,
        "provider_reasoning_type": None,
    }
    assert telemetry_events[7]["provider_name"] == "test-provider"
    assert telemetry_events[7]["model_name"] == "test-model"
    assert telemetry_events[10]["validation_status"] == "passed"
    assert telemetry_events[12]["provider_name"] == "test-provider"
    assert telemetry_events[12]["model_name"] == "test-model"


def test_extract_session_concepts_emits_repair_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Repair workflows should emit schema failure, repair, and repair success events."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingConceptProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should preserve structured outputs.",
                        "evidence": [
                            "Transport setup and schema validation keep integrations reliable."
                        ],
                    }
                ]
            },
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-repair-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "extract_session_concepts.request_received",
        "get_session_extraction_source.query_started",
        "get_session_extraction_source.query_completed",
        "extract_session_concepts.session_fetched",
        "extract_session_concepts.canonical_request_built",
        "extract_session_concepts.provider_selection_started",
        "extract_session_concepts.provider_selection_completed",
        "extract_session_concepts.provider_call_started",
        "extract_session_concepts.provider_call_completed",
        "extract_session_concepts.schema_validation_failed",
        "extract_session_concepts.repair_started",
        "extract_session_concepts.provider_call_started",
        "extract_session_concepts.provider_call_completed",
        "extract_session_concepts.schema_validation_passed",
        "extract_session_concepts.repair_completed",
        "extract_session_concepts.completed",
        "extract_session_concepts.request_completed",
    ]
    assert telemetry_events[9]["validation_status"] == "failed"
    assert telemetry_events[9]["retry_count"] == 0
    assert telemetry_events[10]["validation_status"] == "pending"
    assert telemetry_events[10]["retry_count"] == 1
    assert telemetry_events[10]["details"]["validation_errors"]
    assert telemetry_events[13]["validation_status"] == "passed"
    assert telemetry_events[13]["retry_count"] == 1
    assert telemetry_events[14]["validation_status"] == "passed"
    assert telemetry_events[14]["retry_count"] == 1
    assert telemetry_events[16]["retry_count"] == 1


def test_extract_session_concepts_falls_back_when_primary_provider_is_invalid(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Extraction should skip an invalid primary provider and route to a different provider."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    fallback_provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should wire tool registration correctly.",
                        "evidence": [
                            "MCP tool registration connects tools to the runtime."
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("gemini", "gemini-2.5-flash"),
        ],
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: (_ for _ in ()).throw(
            LookupError("Anthropic provider is selected but no API key is configured.")
        ),
    )

    def _build_fallback_provider(*, provider_name: str, model_name: str):
        assert provider_name == "gemini"
        assert model_name == "gemini-2.5-flash"
        return fallback_provider

    monkeypatch.setattr(
        concept_provider,
        "build_concept_extraction_provider",
        _build_fallback_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-fallback-invalid-primary"},
    )

    assert response.status_code == 200
    assert response.json()["concepts"][0]["name"] == "Tool registration"
    assert len(fallback_provider.requests) == 1


def test_extract_session_concepts_falls_back_after_primary_provider_call_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Extraction should route to a different provider when the primary call fails."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    fallback_provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should preserve structured outputs.",
                        "evidence": [
                            "Transport setup and schema validation keep integrations reliable."
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("gemini", "gemini-2.5-flash"),
        ],
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: _RaisingConceptProvider(
            provider_name="anthropic",
            model_name="claude-sonnet-4-6",
            message="anthropic upstream failure",
        ),
    )

    def _build_fallback_provider(*, provider_name: str, model_name: str):
        assert provider_name == "gemini"
        assert model_name == "gemini-2.5-flash"
        return fallback_provider

    monkeypatch.setattr(
        concept_provider,
        "build_concept_extraction_provider",
        _build_fallback_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-fallback-provider-failure"},
    )

    assert response.status_code == 200
    assert response.json()["concepts"][0]["name"] == "Schema validation"
    assert len(fallback_provider.requests) == 1


def test_extract_session_concepts_falls_back_to_different_model_same_provider(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Extraction should try a second model for the same provider before giving up."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    fallback_provider = _RecordingConceptProvider(
        [
            {
                "concepts": [
                    {
                        "name": "MCP transports",
                        "summary": "Explains how transports move MCP data.",
                        "grading_reason": "Students should configure transports correctly.",
                        "evidence": [
                            "Transport setup and schema validation keep integrations reliable."
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("anthropic", "claude-haiku-4-5-20251001"),
        ],
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda *, reasoning_level: _RaisingConceptProvider(
            provider_name="anthropic",
            model_name="claude-sonnet-4-6",
            message="anthropic primary model failure",
        ),
    )

    def _build_fallback_provider(*, provider_name: str, model_name: str):
        assert provider_name == "anthropic"
        assert model_name == "claude-haiku-4-5-20251001"
        return fallback_provider

    monkeypatch.setattr(
        concept_provider,
        "build_concept_extraction_provider",
        _build_fallback_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-fallback-model"},
    )

    assert response.status_code == 200
    assert response.json()["concepts"][0]["name"] == "MCP transports"
    assert len(fallback_provider.requests) == 1


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
