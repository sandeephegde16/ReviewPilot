"""API tests for the ReviewPilot FastAPI app."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.assignment_requirement_extraction_spec as assignment_requirement_extraction_spec
import app.assignment_requirement_provider as assignment_requirement_provider
import app.concept_extraction_spec as concept_extraction_spec
import app.concept_grading_provider as concept_grading_provider
import app.concept_provider as concept_provider
import app.main as main_module
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
                assignment_requirements_json,
                required_deliverables_json,
                rubric_json,
                due_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "assignment-foundations",
                    "session-older",
                    "Agent Basics Project",
                    "Build a basic agent loop.",
                    json.dumps([]),
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
                    json.dumps([]),
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
                    json.dumps([]),
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
                    json.dumps([]),
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
        connection.execute(
            """
            INSERT INTO student_grades (
                id,
                submission_id,
                concept_scores,
                assignment_requirement_scores,
                rubric_scores,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "student-grade-submission-capstone",
                "submission-capstone",
                json.dumps(
                    [
                        {
                            "concept": "Tool registration",
                            "score": 8,
                            "max_score": 9,
                            "coverage_level": "strong",
                            "evidence": [
                                "The walkthrough demonstrates MCP tool registration end to end."
                            ],
                            "deductions": ["Schema validation detail is brief."],
                        }
                    ]
                ),
                json.dumps(
                    [
                        {
                            "requirement_title": "Walkthrough evidence",
                            "score": 4,
                            "max_score": 5,
                            "evidence": [
                                "The submitted demo covers the full review pilot flow."
                            ],
                        }
                    ]
                ),
                json.dumps(
                    [
                        {
                            "criterion": "delivery",
                            "score": 5,
                            "max_score": 5,
                            "evidence": ["The demo recording is complete and clear."],
                        }
                    ]
                ),
                "2026-05-13T11:00:00+05:30",
            ),
        )
        connection.commit()
    finally:
        connection.close()


def _build_stored_concepts_fixture() -> list[dict[str, object]]:
    """Return a stable stored concepts document used by document API tests."""
    return [
        {
            "name": "Tool registration",
            "summary": "Explains how MCP tools are exposed to the runtime.",
            "grading_reason": "Students should be able to wire tools correctly.",
            "concept_importance": 9,
            "evidence": ["MCP tool registration connects tools to the runtime."],
        },
        {
            "name": "Schema validation",
            "summary": "Covers validating structured inputs and outputs.",
            "grading_reason": "Students should validate tool contracts.",
            "concept_importance": 8,
            "evidence": ["Schema validation keeps integrations reliable."],
        },
    ]


def _build_stored_assignment_requirements_fixture() -> list[dict[str, object]]:
    """Return a stable stored assignment requirements document for API tests."""
    return [
        {
            "assignment_requirement_id": "assignment-mcp",
            "assignment_title": "MCP Integration Project",
            "assignment_description": "Wire an MCP-backed workflow.",
            "due_at": "2026-05-21T23:59:59+05:30",
            "required_deliverables": ["repo", "tests"],
            "requirements": [
                {
                    "requirement_type": "mandatory_deliverable",
                    "title": "Repository submission",
                    "summary": "Submit a repository that contains the MCP workflow implementation.",
                    "evidence": ["Wire an MCP-backed workflow."],
                }
            ],
        },
        {
            "assignment_requirement_id": "assignment-capstone",
            "assignment_title": "Capstone Demo",
            "assignment_description": "Submit a full review pilot walkthrough.",
            "due_at": "2026-05-22T23:59:59+05:30",
            "required_deliverables": ["repo", "video"],
            "requirements": [
                {
                    "requirement_type": "evidence_expectation",
                    "title": "Walkthrough evidence",
                    "summary": (
                        "Provide a walkthrough that demonstrates the full review "
                        "pilot flow."
                    ),
                    "evidence": ["Submit a full review pilot walkthrough."],
                }
            ],
        },
    ]


def _seed_session_concepts_json(
    *,
    database_path: Path,
    session_id: str,
    concepts: list[dict[str, object]],
) -> None:
    """Seed one session row with a valid stored concepts JSON document."""
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            UPDATE session_content
            SET concepts_json = ?
            WHERE id = ?
            """,
            (json.dumps(concepts), session_id),
        )
        connection.commit()
    finally:
        connection.close()


def _seed_assignment_requirements_json(
    *,
    database_path: Path,
    assignment_requirements: list[dict[str, object]],
) -> None:
    """Seed assignment_requirement rows with stored requirements JSON documents."""
    connection = sqlite3.connect(database_path)
    try:
        for assignment_requirement in assignment_requirements:
            connection.execute(
                """
                UPDATE assignment_requirement
                SET assignment_requirements_json = ?
                WHERE id = ?
                """,
                (
                    json.dumps(assignment_requirement["requirements"]),
                    assignment_requirement["assignment_requirement_id"],
                ),
            )
        connection.commit()
    finally:
        connection.close()


def _build_test_project_folder(project_root: Path) -> Path:
    """Create a bounded local project used for concept grading tests."""
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "README.md").write_text(
        "\n".join(
            [
                "# Binary Search Project",
                "README explains O(log n) search complexity.",
                "The implementation favors binary search over linear scan.",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "src").mkdir(exist_ok=True)
    (project_root / "src" / "search.py").write_text(
        "\n".join(
            [
                "def binary_search(items, target):",
                "    left = 0",
                "    right = len(items) - 1",
                "    while left <= right:",
                "        midpoint = (left + right) // 2",
                "        if items[midpoint] == target:",
                "            return midpoint",
                "        if items[midpoint] < target:",
                "            left = midpoint + 1",
                "        else:",
                "            right = midpoint - 1",
                "    return -1",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "tests" / "test_search.py").write_text(
        "\n".join(
            [
                "from src.search import binary_search",
                "",
                "def test_binary_search_handles_empty_list():",
                "    assert binary_search([], 3) == -1",
                "",
                "def test_binary_search_finds_single_item():",
                "    assert binary_search([7], 7) == 0",
                "",
                "def test_binary_search_handles_missing_target():",
                "    assert binary_search([1, 2, 3], 4) == -1",
            ]
        ),
        encoding="utf-8",
    )
    return project_root


class _RecordingStructuredExtractionProvider:
    """Test double for the shared structured extraction provider interface."""

    provider_name = "test-provider"
    model_name = "test-model"

    def __init__(self, responses: list[dict[str, object]]) -> None:
        """Store canned responses and record incoming requests."""
        self._responses = responses
        self.requests: list[tuple[object, str, object | None]] = []

    def extract_structured_output(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Return the next canned response while recording the canonical request."""
        self.requests.append((request, trace_id, repair_context))
        return self._responses.pop(0)

    def extract_concepts(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Compatibility wrapper for concept-specific callers in older tests."""
        return self.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )


class _RaisingConceptProvider:
    """Test double that raises during provider invocation."""

    def __init__(self, *, provider_name: str, model_name: str, message: str) -> None:
        """Store provider identity and the failure message to raise."""
        self.provider_name = provider_name
        self.model_name = model_name
        self.message = message

    def extract_structured_output(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Raise a runtime error to simulate a provider-call failure."""
        del request, trace_id, repair_context
        raise RuntimeError(self.message)

    def extract_concepts(
        self,
        request,
        *,
        trace_id: str,
        repair_context=None,
    ) -> dict[str, object]:
        """Compatibility wrapper for concept-specific callers in older tests."""
        return self.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )


def test_root_redirects_to_assignments(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET / should redirect browsers into the assignments workspace."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/assignments"


def test_assignments_page_serves_html_shell(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /assignments should serve the browser application shell."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get("/assignments")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Axiom</title>" in response.text
    assert "Assignments" in response.text


def test_get_all_sessions_returns_session_titles_topics_and_ids(
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
            "session_id": "session-empty",
            "session_title": "Observability",
            "session_topic": "Tracing review workflows",
        },
        {
            "session_id": "session-newer",
            "session_title": "Advanced MCP",
            "session_topic": "MCP transports and tool registration",
        },
        {
            "session_id": "session-older",
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should be able to wire tools correctly.",
                        "concept_importance": 9,
                        "evidence": ["MCP tool registration connects tools to the runtime."],
                    },
                    {
                        "name": "Schema validation",
                        "summary": "Covers validating tool inputs and outputs.",
                        "grading_reason": "Students should produce reliable structured outputs.",
                        "concept_importance": 8,
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
        lambda: provider,
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
                "concept_importance": 9,
                "evidence": ["MCP tool registration connects tools to the runtime."],
            },
            {
                "name": "Schema validation",
                "summary": "Covers validating tool inputs and outputs.",
                "grading_reason": "Students should produce reliable structured outputs.",
                "concept_importance": 8,
                "evidence": ["Transport setup and schema validation keep integrations reliable."],
            },
        ],
        "warnings": [],
    }
    provider_request, recorded_trace_id, repair_context = provider.requests[0]
    assert recorded_trace_id == "trace-extract-success"
    assert repair_context is None
    assert provider_request.operation_name == concept_extraction_spec.DEFAULT_OPERATION_NAME
    assert provider_request.session_id == "session-newer"
    assert provider_request.output_mode == "json_schema_strict"
    assert provider_request.reasoning_level == "high"
    assert provider_request.reasoning_type == "structured_extraction"
    assert provider_request.max_concepts == 5
    assert provider_request.response_schema["title"] == "ConceptExtractionOutput"
    assert provider_request.response_schema["type"] == "object"
    assert provider_request.response_schema["required"] == ["concepts"]
    assert "concepts" in provider_request.response_schema["properties"]
    assert provider_request.response_schema["properties"]["concepts"]["maxItems"] == 5
    assert provider_request.response_schema["properties"]["concepts"]["items"]["required"] == [
        "name",
        "summary",
        "grading_reason",
        "concept_importance",
        "evidence",
    ]
    assert "MCP tool registration connects tools to the runtime." in (
        provider_request.session_transcript or ""
    )


def test_extract_session_concepts_persists_concepts_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Successful concept extraction should update session_content.concepts_json."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should be able to wire tools correctly.",
                        "concept_importance": 9,
                        "evidence": ["MCP tool registration connects tools to the runtime."],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-persist"},
    )

    assert response.status_code == 200
    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT concepts_json
            FROM session_content
            WHERE id = ?
            """,
            ("session-newer",),
        ).fetchone()
    finally:
        connection.close()

    assert row is not None
    assert json.loads(row[0]) == response.json()["concepts"]


def test_extract_session_concepts_accepts_plain_text_transcript(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-concepts should use raw text transcripts."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Agent workflows",
                        "summary": "Explains how agents coordinate tools and control flow.",
                        "grading_reason": "Students should understand orchestrated workflows.",
                        "concept_importance": 8,
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
        lambda: provider,
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
                "concept_importance": 8,
                "evidence": [
                    ("Agents coordinate tools, prompts, and control flow for repeatable workflows.")
                ],
            }
        ],
        "warnings": [],
    }
    provider_request, _, repair_context = provider.requests[0]
    assert repair_context is None
    assert "Agents coordinate tools, prompts, and control flow for repeatable workflows." in (
        provider_request.session_transcript or ""
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Agent workflows",
                        "summary": "Explains how agents coordinate tools and control flow.",
                        "grading_reason": "Students should understand orchestrated workflows.",
                        "concept_importance": 8,
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
        lambda: provider,
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Telemetry workflows",
                        "summary": "Synthesizes the main workflow concept from the topic.",
                        "grading_reason": "Students should understand the core workflow shape.",
                        "concept_importance": 7,
                        "evidence": ["Session topic: Tracing review workflows"],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda: provider,
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
                "concept_importance": 7,
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should enforce structured contracts.",
                        "concept_importance": 8,
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
        lambda: provider,
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {"concepts": [{"name": "Still invalid"}]},
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda: provider,
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
    primary_provider = _RecordingStructuredExtractionProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {"concepts": [{"name": "Still invalid"}]},
        ]
    )
    fallback_provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Should not run",
                        "summary": "Fallback provider should never be called here.",
                        "grading_reason": "Schema failure should stop the workflow.",
                        "concept_importance": 6,
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
        lambda: primary_provider,
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
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Telemetry workflows",
                        "summary": "Synthesizes the main workflow concept from the topic.",
                        "grading_reason": "Students should understand the core workflow shape.",
                        "concept_importance": 7,
                        "evidence": ["Session topic: Tracing review workflows"],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda: provider,
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
        "save_session_concepts_json.query_started",
        "save_session_concepts_json.query_completed",
        "extract_session_concepts.concepts_persisted",
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
        event["tool_name"] == concept_extraction_spec.DEFAULT_TOOL_NAME for event in extract_events
    )
    assert all(event["reasoning_level"] == "medium" for event in extract_events)
    assert all(
        event["reasoning_type"] == concept_extraction_spec.DEFAULT_REASONING_TYPE
        for event in extract_events
    )
    canonical_request_event = telemetry_events[5]
    assert canonical_request_event["provider_name"] is None
    assert canonical_request_event["model_name"] is None
    assert canonical_request_event["details"] == {
        "session_id": "session-empty",
        "operation_name": concept_extraction_spec.DEFAULT_OPERATION_NAME,
        "reasoning_level": "medium",
        "reasoning_type": concept_provider.DEFAULT_REASONING_TYPE,
        "output_mode": concept_provider.DEFAULT_OUTPUT_MODE,
        "max_concepts": 5,
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
    assert telemetry_events[13]["details"] == {"concept_count": 1}
    assert telemetry_events[14]["provider_name"] == "test-provider"
    assert telemetry_events[14]["model_name"] == "test-model"
    assert telemetry_events[15]["provider_name"] == "test-provider"
    assert telemetry_events[15]["model_name"] == "test-model"


def test_extract_session_concepts_emits_repair_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Repair workflows should emit schema failure, repair, and repair success events."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {"concepts": [{"name": "Schema validation"}]},
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should preserve structured outputs.",
                        "concept_importance": 8,
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
        lambda: provider,
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
        "save_session_concepts_json.query_started",
        "save_session_concepts_json.query_completed",
        "extract_session_concepts.concepts_persisted",
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


def test_extract_session_concepts_returns_structured_error_when_persistence_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Persistence failures should return a structured 500 response."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should be able to wire tools correctly.",
                        "concept_importance": 9,
                        "evidence": ["MCP tool registration connects tools to the runtime."],
                    }
                ]
            }
        ]
    )

    def _raise_persistence_failure(**kwargs) -> None:
        """Simulate a database write failure during concept persistence."""
        del kwargs
        raise sqlite3.Error("write failed")

    monkeypatch.setattr(
        concept_provider,
        "select_concept_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setattr(main_module, "save_session_concepts_json", _raise_persistence_failure)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-concepts",
        headers={"X-Trace-Id": "trace-extract-persist-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "session_concepts_persistence_failed",
            "message": "Unable to save extracted concepts for the session.",
            "trace_id": "trace-extract-persist-failure",
        }
    }


def test_extract_session_concepts_falls_back_when_primary_provider_is_invalid(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Extraction should skip an invalid primary provider and route to a different provider."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    fallback_provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Tool registration",
                        "summary": "Explains how MCP tools are exposed to the runtime.",
                        "grading_reason": "Students should wire tool registration correctly.",
                        "concept_importance": 9,
                        "evidence": ["MCP tool registration connects tools to the runtime."],
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
        lambda: (_ for _ in ()).throw(
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
    fallback_provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "Schema validation",
                        "summary": "Explains output validation for tool results.",
                        "grading_reason": "Students should preserve structured outputs.",
                        "concept_importance": 8,
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
        lambda: _RaisingConceptProvider(
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
    fallback_provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concepts": [
                    {
                        "name": "MCP transports",
                        "summary": "Explains how transports move MCP data.",
                        "grading_reason": "Students should configure transports correctly.",
                        "concept_importance": 8,
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
        lambda: _RaisingConceptProvider(
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


def test_extract_session_assignment_requirements_returns_extracted_requirements(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /sessions/{session_id}/extract-assignment-requirements should return results."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "assignment_requirements": [
                    {
                        "assignment_requirement_id": "assignment-mcp",
                        "assignment_title": "MCP Integration Project",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "MCP-backed workflow",
                                "summary": "Students must build the MCP-based workflow.",
                                "evidence": ["Wire an MCP-backed workflow."],
                            }
                        ],
                    },
                    {
                        "assignment_requirement_id": "assignment-capstone",
                        "assignment_title": "Capstone Demo",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "Review pilot walkthrough",
                                "summary": "Students must submit the full walkthrough.",
                                "evidence": ["Submit a full review pilot walkthrough."],
                            }
                        ],
                    },
                ]
            }
        ]
    )
    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setattr(
        provider_router,
        "build_provider_candidates",
        lambda: [provider_router.ProviderCandidate("heuristic", "heuristic-v1")],
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-assignment-requirements",
        json={"reasoning_level": "high"},
        headers={"X-Trace-Id": "trace-assignment-requirements"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-newer",
        "assignment_requirements": [
            {
                "assignment_requirement_id": "assignment-mcp",
                "assignment_title": "MCP Integration Project",
                "requirements": [
                    {
                        "requirement_type": "mandatory_deliverable",
                        "title": "MCP-backed workflow",
                        "summary": "Students must build the MCP-based workflow.",
                        "evidence": ["Wire an MCP-backed workflow."],
                    }
                ],
            },
            {
                "assignment_requirement_id": "assignment-capstone",
                "assignment_title": "Capstone Demo",
                "requirements": [
                    {
                        "requirement_type": "mandatory_deliverable",
                        "title": "Review pilot walkthrough",
                        "summary": "Students must submit the full walkthrough.",
                        "evidence": ["Submit a full review pilot walkthrough."],
                    }
                ],
            },
        ],
        "warnings": [],
    }
    provider_request, recorded_trace_id, repair_context = provider.requests[0]
    assert recorded_trace_id == "trace-assignment-requirements"
    assert repair_context is None
    assert (
        provider_request.operation_name
        == assignment_requirement_extraction_spec.DEFAULT_OPERATION_NAME
    )
    assert provider_request.reasoning_type == "structured_extraction"
    assert provider_request.max_assignment_requirements == 5
    assert provider_request.response_schema["title"] == "AssignmentRequirementsExtractionOutput"
    assert provider_request.response_schema["required"] == ["assignment_requirements"]
    assert (
        provider_request.response_schema["properties"]["assignment_requirements"]["items"][
            "properties"
        ]["requirements"]["maxItems"]
        == 5
    )
    assert [source.assignment_requirement_id for source in provider_request.assignment_sources] == [
        "assignment-mcp",
        "assignment-capstone",
    ]
    assert "Wire an MCP-backed workflow." in provider_request.prompt_input_fields[1].value


def test_extract_session_assignment_requirements_persists_assignment_requirements_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Successful assignment extraction should update assignment_requirement rows."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "assignment_requirements": [
                    {
                        "assignment_requirement_id": "assignment-mcp",
                        "assignment_title": "MCP Integration Project",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "MCP-backed workflow",
                                "summary": "Students must build the MCP-based workflow.",
                                "evidence": ["Wire an MCP-backed workflow."],
                            }
                        ],
                    },
                    {
                        "assignment_requirement_id": "assignment-capstone",
                        "assignment_title": "Capstone Demo",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "Review pilot walkthrough",
                                "summary": "Students must submit the full walkthrough.",
                                "evidence": ["Submit a full review pilot walkthrough."],
                            }
                        ],
                    },
                ]
            }
        ]
    )
    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-persist"},
    )

    assert response.status_code == 200
    connection = sqlite3.connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, assignment_requirements_json
            FROM assignment_requirement
            WHERE session_content_id = ?
            ORDER BY id ASC
            """,
            ("session-newer",),
        ).fetchall()
    finally:
        connection.close()

    assert {row[0]: json.loads(row[1]) for row in rows} == {
        "assignment-capstone": response.json()["assignment_requirements"][1]["requirements"],
        "assignment-mcp": response.json()["assignment_requirements"][0]["requirements"],
    }


def test_extract_session_assignment_requirements_returns_warning_when_none_are_stored(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Sessions without assignment rows should return an empty result with a warning."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            DELETE FROM assignment_requirement
            WHERE session_content_id = ?
            """,
            ("session-empty",),
        )
        connection.commit()
    finally:
        connection.close()
    provider = _RecordingStructuredExtractionProvider([])
    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-empty/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-warning"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-empty",
        "assignment_requirements": [],
        "warnings": [
            {
                "code": "session_assignment_requirements_not_available",
                "message": "No assignment requirements are stored for this session.",
            }
        ],
    }
    assert provider.requests == []


def test_extract_session_assignment_requirements_repairs_schema_failure_once(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Assignment requirement extraction should retry once on schema failure."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {"assignment_requirements": [{"assignment_requirement_id": "assignment-mcp"}]},
            {
                "assignment_requirements": [
                    {
                        "assignment_requirement_id": "assignment-mcp",
                        "assignment_title": "MCP Integration Project",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "MCP-backed workflow",
                                "summary": "Students must build the MCP-based workflow.",
                                "evidence": ["Wire an MCP-backed workflow."],
                            }
                        ],
                    },
                    {
                        "assignment_requirement_id": "assignment-capstone",
                        "assignment_title": "Capstone Demo",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "Review pilot walkthrough",
                                "summary": "Students must submit the full walkthrough.",
                                "evidence": ["Submit a full review pilot walkthrough."],
                            }
                        ],
                    },
                ]
            },
        ]
    )
    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-repair"},
    )

    assert response.status_code == 200
    assert len(provider.requests) == 2
    _, _, repair_context = provider.requests[1]
    assert repair_context is not None
    assert repair_context.schema_check_failed is True
    assert repair_context.validation_errors
    assert response.json()["assignment_requirements"][0]["assignment_requirement_id"] == (
        "assignment-mcp"
    )


def test_extract_session_assignment_requirements_returns_structured_error_for_missing_session(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Missing sessions should return a structured 404 for assignment extraction."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-missing/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-missing"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "session_not_found",
            "message": "Unable to find the requested session.",
            "trace_id": "trace-assignment-missing",
        }
    }


def test_extract_session_assignment_requirements_returns_structured_error_for_missing_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Assignment extraction should return a structured 500 on DB failure."""
    missing_database_path = tmp_path / "missing.db"
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(missing_database_path))
    client = TestClient(app)

    response = client.post(
        "/sessions/session-newer/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-query-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "assignment_requirement_extraction_source_query_failed",
            "message": ("Unable to fetch the assignment data required for requirement extraction."),
            "trace_id": "trace-assignment-query-failure",
        }
    }


def test_extract_session_assignment_requirements_returns_structured_error_when_persistence_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Persistence failures should return a structured 500 response."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "assignment_requirements": [
                    {
                        "assignment_requirement_id": "assignment-empty",
                        "assignment_title": "Telemetry Drill",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "Tracing notes",
                                "summary": "Students must submit tracing notes.",
                                "evidence": ["Submit tracing notes."],
                            }
                        ],
                    }
                ]
            }
        ]
    )

    def _raise_persistence_failure(**kwargs) -> None:
        """Simulate a database write failure during assignment persistence."""
        del kwargs
        raise sqlite3.Error("write failed")

    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setattr(
        main_module,
        "save_assignment_requirement_requirements_json",
        _raise_persistence_failure,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/sessions/session-empty/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-persist-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "assignment_requirements_persistence_failed",
            "message": "Unable to save extracted assignment requirements.",
            "trace_id": "trace-assignment-persist-failure",
        }
    }


def test_extract_session_assignment_requirements_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Assignment requirement extraction should emit workflow telemetry."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "assignment_requirements": [
                    {
                        "assignment_requirement_id": "assignment-empty",
                        "assignment_title": "Telemetry Drill",
                        "requirements": [
                            {
                                "requirement_type": "mandatory_deliverable",
                                "title": "Tracing notes",
                                "summary": "Students must submit tracing notes.",
                                "evidence": ["Submit tracing notes."],
                            }
                        ],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        assignment_requirement_provider,
        "select_assignment_requirement_extraction_provider",
        lambda: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/sessions/session-empty/extract-assignment-requirements",
        headers={"X-Trace-Id": "trace-assignment-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "extract_session_assignment_requirements.request_received",
        "list_session_assignment_requirement_sources.query_started",
        "list_session_assignment_requirement_sources.query_completed",
        "extract_session_assignment_requirements.assignment_sources_fetched",
        "extract_session_assignment_requirements.canonical_request_built",
        "extract_session_assignment_requirements.provider_selection_started",
        "extract_session_assignment_requirements.provider_selection_completed",
        "extract_session_assignment_requirements.provider_call_started",
        "extract_session_assignment_requirements.provider_call_completed",
        "extract_session_assignment_requirements.schema_validation_passed",
        "extract_session_assignment_requirements.completed",
        "save_assignment_requirement_requirements_json.query_started",
        "save_assignment_requirement_requirements_json.query_completed",
        "extract_session_assignment_requirements.assignment_requirements_persisted",
        "extract_session_assignment_requirements.request_completed",
    ]
    assert all(event["trace_id"] == "trace-assignment-telemetry" for event in telemetry_events)
    assignment_events = [
        event
        for event in telemetry_events
        if event["step_name"].startswith("extract_session_assignment_requirements.")
    ]
    assert all(event["session_id"] == "session-empty" for event in assignment_events)
    assert all(
        event["tool_name"] == assignment_requirement_extraction_spec.DEFAULT_TOOL_NAME
        for event in assignment_events
    )
    assert telemetry_events[4]["details"] == {
        "session_id": "session-empty",
        "operation_name": assignment_requirement_extraction_spec.DEFAULT_OPERATION_NAME,
        "reasoning_level": "medium",
        "reasoning_type": assignment_requirement_provider.DEFAULT_REASONING_TYPE,
        "output_mode": assignment_requirement_provider.DEFAULT_OUTPUT_MODE,
        "max_assignment_requirements": 5,
        "response_schema_title": "AssignmentRequirementsExtractionOutput",
        "assignment_count": 1,
    }
    assert telemetry_events[7]["details"] == {
        "provider_reasoning_level": None,
        "provider_reasoning_type": None,
    }
    assert telemetry_events[12]["details"] == {"assignment_requirement_count": 1}


def test_get_session_concepts_returns_stored_document(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/concepts should return the stored concepts document."""
    database_path = tmp_path / "reviewpilot.db"
    concepts = _build_stored_concepts_fixture()
    _build_test_database(database_path)
    _seed_session_concepts_json(
        database_path=database_path,
        session_id="session-newer",
        concepts=concepts,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-newer/concepts",
        headers={"X-Trace-Id": "trace-get-concepts"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-newer",
        "concepts": concepts,
    }


def test_update_session_concepts_persists_request_document(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """PUT /sessions/{session_id}/concepts should replace the stored concepts JSON."""
    database_path = tmp_path / "reviewpilot.db"
    concepts = _build_stored_concepts_fixture()
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.put(
        "/sessions/session-newer/concepts",
        json={
            "session_id": "session-newer",
            "concepts": concepts,
        },
        headers={"X-Trace-Id": "trace-update-concepts"},
    )

    assert response.status_code == 200
    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT concepts_json
            FROM session_content
            WHERE id = ?
            """,
            ("session-newer",),
        ).fetchone()
    finally:
        connection.close()

    assert row is not None
    assert json.loads(row[0]) == concepts
    assert response.json() == {
        "session_id": "session-newer",
        "concepts": concepts,
    }


def test_get_session_assignment_requirements_returns_stored_document(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """GET /sessions/{session_id}/assignment-requirements should return stored JSON."""
    database_path = tmp_path / "reviewpilot.db"
    assignment_requirements = _build_stored_assignment_requirements_fixture()
    _build_test_database(database_path)
    _seed_assignment_requirements_json(
        database_path=database_path,
        assignment_requirements=assignment_requirements,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.get(
        "/sessions/session-newer/assignment-requirements",
        headers={"X-Trace-Id": "trace-get-assignment-doc"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-newer",
        "assignment_requirements": assignment_requirements,
    }


def test_update_session_assignment_requirements_persists_request_document(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """PUT /sessions/{session_id}/assignment-requirements should replace stored JSON."""
    database_path = tmp_path / "reviewpilot.db"
    assignment_requirements = [
        {
            "assignment_requirement_id": "assignment-mcp",
            "assignment_title": "MCP Integration Project",
            "requirements": [
                {
                    "requirement_type": "mandatory_deliverable",
                    "title": "Repository submission",
                    "summary": "Submit the repository with the MCP-backed workflow.",
                    "evidence": ["Wire an MCP-backed workflow."],
                }
            ],
        },
        {
            "assignment_requirement_id": "assignment-capstone",
            "assignment_title": "Capstone Demo",
            "requirements": [],
        },
    ]
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)
    expected_assignment_requirements = [
        {
            "assignment_requirement_id": "assignment-mcp",
            "assignment_title": "MCP Integration Project",
            "assignment_description": "Wire an MCP-backed workflow.",
            "due_at": "2026-05-21T23:59:59+05:30",
            "required_deliverables": ["repo", "tests"],
            "requirements": [
                {
                    "requirement_type": "mandatory_deliverable",
                    "title": "Repository submission",
                    "summary": "Submit the repository with the MCP-backed workflow.",
                    "evidence": ["Wire an MCP-backed workflow."],
                }
            ],
        },
        {
            "assignment_requirement_id": "assignment-capstone",
            "assignment_title": "Capstone Demo",
            "assignment_description": "Submit a full review pilot walkthrough.",
            "due_at": "2026-05-22T23:59:59+05:30",
            "required_deliverables": ["repo", "video"],
            "requirements": [],
        },
    ]

    response = client.put(
        "/sessions/session-newer/assignment-requirements",
        json={
            "session_id": "session-newer",
            "assignment_requirements": assignment_requirements,
        },
        headers={"X-Trace-Id": "trace-update-assignment-doc"},
    )

    assert response.status_code == 200
    connection = sqlite3.connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, assignment_requirements_json
            FROM assignment_requirement
            WHERE session_content_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            ("session-newer",),
        ).fetchall()
    finally:
        connection.close()

    assert {row[0]: json.loads(row[1]) for row in rows} == {
        "assignment-mcp": assignment_requirements[0]["requirements"],
        "assignment-capstone": assignment_requirements[1]["requirements"],
    }
    assert response.json() == {
        "session_id": "session-newer",
        "assignment_requirements": expected_assignment_requirements,
    }


def test_update_session_assignment_requirements_returns_404_for_missing_assignment_row(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """PUT assignment requirements should reject unknown assignment rows for a session."""
    database_path = tmp_path / "reviewpilot.db"
    _build_test_database(database_path)
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.put(
        "/sessions/session-newer/assignment-requirements",
        json={
            "assignment_requirements": [
                {
                    "assignment_requirement_id": "assignment-missing",
                    "assignment_title": "Missing Assignment",
                    "requirements": [],
                }
            ],
        },
        headers={"X-Trace-Id": "trace-update-assignment-missing-row"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "assignment_requirement_not_found",
            "message": "Unable to find one or more assignment requirements for the session.",
            "trace_id": "trace-update-assignment-missing-row",
        }
    }


def test_grade_submission_concepts_returns_scores_for_local_folder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """POST /grade/concepts should return structured concept scores for a local project."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concept_scores": [
                    {
                        "concept": "time complexity",
                        "score": 4,
                        "max_score": 5,
                        "coverage_level": "strong",
                        "evidence": [
                            "README explains O(log n) search complexity.",
                            "Code implements binary search rather than linear scan.",
                            "Tests cover empty, single-item, and missing-target cases.",
                        ],
                        "deductions": ["Space complexity is not discussed."],
                    }
                ]
            }
        ]
    )

    def _unexpected_primary_provider():
        raise AssertionError(
            "grade_submission_concepts should build the first provider from candidates."
        )

    monkeypatch.setattr(
        concept_grading_provider,
        "select_concept_grading_provider",
        _unexpected_primary_provider,
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6")],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        lambda *, provider_name, model_name: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-success"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "student_id": "student-ada",
        "student_code": "STU-001",
        "student_full_name": "Ada Lovelace",
        "session_id": "session-newer",
        "source_type": "local_folder",
        "repo_url": None,
        "local_path": str(project_root),
        "zip_path": None,
        "concept_scores": [
            {
                "concept": "time complexity",
                "score": 4,
                "max_score": 5,
                "coverage_level": "strong",
                "evidence": [
                    "README explains O(log n) search complexity.",
                    "Code implements binary search rather than linear scan.",
                    "Tests cover empty, single-item, and missing-target cases.",
                ],
                "deductions": ["Space complexity is not discussed."],
            }
        ],
        "warnings": [],
    }
    provider_request, recorded_trace_id, repair_context = provider.requests[0]
    assert recorded_trace_id == "trace-grade-concepts-success"
    assert repair_context is None
    assert provider_request.operation_name == "grade_submission_concepts"
    assert provider_request.student_id == "student-ada"
    assert provider_request.student_code == "STU-001"
    assert provider_request.student_full_name == "Ada Lovelace"
    assert provider_request.source_type == "local_folder"
    assert provider_request.local_path == str(project_root)
    assert provider_request.grading_concepts[0].concept_name == "time complexity"
    assert (
        "README explains O(log n) search complexity." in provider_request.project_evidence_summary
    )
    assert "test_binary_search_handles_empty_list" in provider_request.project_evidence_summary


def test_grade_submission_concepts_persists_concept_scores_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Successful concept grading should upsert student_grades.concept_scores."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concept_scores": [
                    {
                        "concept": "time complexity",
                        "score": 4,
                        "max_score": 5,
                        "coverage_level": "strong",
                        "evidence": [
                            "README explains O(log n) search complexity.",
                            "Code implements binary search rather than linear scan.",
                        ],
                        "deductions": ["Space complexity is not discussed."],
                    }
                ]
            }
        ]
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6")],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        lambda *, provider_name, model_name: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-persist"},
    )

    assert response.status_code == 200
    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT concept_scores
            FROM student_grades
            WHERE submission_id = ?
            """,
            ("submission-mcp",),
        ).fetchone()
    finally:
        connection.close()

    assert row is not None
    assert json.loads(row[0]) == response.json()["concept_scores"]


def test_grade_submission_concepts_falls_back_to_second_real_model(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Concept grading should retry on the next configured non-heuristic candidate."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)
    fallback_provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concept_scores": [
                    {
                        "concept": "time complexity",
                        "score": 5,
                        "max_score": 5,
                        "coverage_level": "strong",
                        "evidence": ["README explains O(log n) search complexity."],
                        "deductions": [],
                    }
                ]
            }
        ]
    )

    def _unexpected_primary_provider():
        raise AssertionError(
            "grade_submission_concepts should not use select_concept_grading_provider."
        )

    def _build_provider(*, provider_name: str, model_name: str):
        if provider_name == "anthropic":
            return _RaisingConceptProvider(
                provider_name=provider_name,
                model_name=model_name,
                message="anthropic grading failure",
            )
        return fallback_provider

    monkeypatch.setattr(
        concept_grading_provider,
        "select_concept_grading_provider",
        _unexpected_primary_provider,
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("gemini", "gemini-2.5-flash"),
        ],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        _build_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-fallback"},
    )

    assert response.status_code == 200
    assert response.json()["concept_scores"][0]["score"] == 5
    assert len(fallback_provider.requests) == 1


def test_grade_submission_concepts_returns_structured_error_when_all_models_fail(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Concept grading should return a structured error after all real models fail."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)

    def _unexpected_primary_provider():
        raise AssertionError(
            "grade_submission_concepts should not use select_concept_grading_provider."
        )

    def _build_provider(*, provider_name: str, model_name: str):
        return _RaisingConceptProvider(
            provider_name=provider_name,
            model_name=model_name,
            message=f"{provider_name} grading failure",
        )

    monkeypatch.setattr(
        concept_grading_provider,
        "select_concept_grading_provider",
        _unexpected_primary_provider,
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [
            provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6"),
            provider_router.ProviderCandidate("gemini", "gemini-2.5-flash"),
        ],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        _build_provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-provider-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "concept_grading_provider_failed",
            "message": "Unable to grade the requested concepts with the configured providers.",
            "trace_id": "trace-grade-concepts-provider-failure",
        }
    }


def test_grade_submission_concepts_returns_structured_error_when_persistence_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Concept grading should return a structured error when persistence fails."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concept_scores": [
                    {
                        "concept": "time complexity",
                        "score": 4,
                        "max_score": 5,
                        "coverage_level": "strong",
                        "evidence": ["README explains O(log n) search complexity."],
                        "deductions": ["Space complexity is not discussed."],
                    }
                ]
            }
        ]
    )

    def _raise_persistence_failure(**kwargs) -> None:
        """Simulate a database write failure during concept-grade persistence."""
        del kwargs
        raise sqlite3.Error("write failed")

    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6")],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        lambda *, provider_name, model_name: provider,
    )
    monkeypatch.setattr(
        main_module,
        "save_student_concept_scores",
        _raise_persistence_failure,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-persist-failure"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "concept_grading_persistence_failed",
            "message": "Unable to save concept grading for the student submission.",
            "trace_id": "trace-grade-concepts-persist-failure",
        }
    }


def test_grade_submission_concepts_emits_structured_telemetry(
    monkeypatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Concept grading should emit the expected structured workflow telemetry."""
    database_path = tmp_path / "reviewpilot.db"
    project_root = _build_test_project_folder(tmp_path / "student-project")
    _build_test_database(database_path)
    provider = _RecordingStructuredExtractionProvider(
        [
            {
                "concept_scores": [
                    {
                        "concept": "time complexity",
                        "score": 4,
                        "max_score": 5,
                        "coverage_level": "strong",
                        "evidence": ["README explains O(log n) search complexity."],
                        "deductions": ["Space complexity is not discussed."],
                    }
                ]
            }
        ]
    )

    def _unexpected_primary_provider():
        raise AssertionError(
            "grade_submission_concepts should not use select_concept_grading_provider."
        )

    monkeypatch.setattr(
        concept_grading_provider,
        "select_concept_grading_provider",
        _unexpected_primary_provider,
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider_candidates",
        lambda: [provider_router.ProviderCandidate("anthropic", "claude-sonnet-4-6")],
    )
    monkeypatch.setattr(
        concept_grading_provider,
        "build_concept_grading_provider",
        lambda *, provider_name, model_name: provider,
    )
    monkeypatch.setenv("REVIEWPILOT_DB_PATH", str(database_path))
    configure_logging(force=True)
    client = TestClient(app)

    response = client.post(
        "/grade/concepts",
        json={
            "student_id": "student-ada",
            "session_id": "session-newer",
            "source_type": "local_folder",
            "local_path": str(project_root),
            "concepts": [
                {
                    "concept_name": "time complexity",
                    "summary": "Evaluate how the project explains and implements complexity.",
                    "grading_reason": (
                        "Algorithmic efficiency is part of the session learning goals."
                    ),
                    "max_score": 5,
                }
            ],
        },
        headers={"X-Trace-Id": "trace-grade-concepts-telemetry"},
    )

    assert response.status_code == 200
    stdout = capsys.readouterr().out.strip().splitlines()
    telemetry_events = [json.loads(line) for line in stdout if line.startswith("{")]
    assert [event["step_name"] for event in telemetry_events] == [
        "grade_submission_concepts.request_received",
        "get_concept_grading_context.query_started",
        "get_concept_grading_context.query_completed",
        "grade_submission_concepts.grading_context_fetched",
        "grade_submission_concepts.project_evidence_collection_started",
        "grade_submission_concepts.project_evidence_collected",
        "grade_submission_concepts.canonical_request_built",
        "grade_submission_concepts.provider_selection_started",
        "grade_submission_concepts.provider_selection_completed",
        "grade_submission_concepts.provider_call_started",
        "grade_submission_concepts.provider_call_completed",
        "grade_submission_concepts.schema_validation_passed",
        "grade_submission_concepts.completed",
        "save_student_concept_scores.query_started",
        "save_student_concept_scores.query_completed",
        "grade_submission_concepts.concept_scores_persisted",
        "grade_submission_concepts.request_completed",
    ]
    assert telemetry_events[5]["details"]["project_file_count"] >= 3
    assert telemetry_events[6]["details"] == {
        "submission_id": "submission-mcp",
        "session_id": "session-newer",
        "student_id": "student-ada",
        "operation_name": "grade_submission_concepts",
        "reasoning_level": "medium",
        "reasoning_type": "project_grading",
        "output_mode": concept_grading_provider.DEFAULT_OUTPUT_MODE,
        "concept_count": 1,
        "response_schema_title": "ConceptGradingOutput",
        "source_type": "local_folder",
        "project_file_count": 3,
        "documentation_snippet_count": 1,
        "implementation_snippet_count": 1,
        "test_snippet_count": 1,
    }
    assert telemetry_events[9]["details"] == {
        "provider_reasoning_level": None,
        "provider_reasoning_type": None,
    }
    assert telemetry_events[14]["details"] == {
        "submission_id": "submission-mcp",
        "concept_score_count": 1,
    }


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
            "concept_scores": [
                {
                    "concept": "Tool registration",
                    "score": 8,
                    "max_score": 9,
                    "coverage_level": "strong",
                    "evidence": [
                        "The walkthrough demonstrates MCP tool registration end to end."
                    ],
                    "deductions": ["Schema validation detail is brief."],
                }
            ],
            "assignment_requirement_scores": [
                {
                    "requirement_title": "Walkthrough evidence",
                    "score": 4,
                    "max_score": 5,
                    "evidence": [
                        "The submitted demo covers the full review pilot flow."
                    ],
                }
            ],
            "rubric_scores": [
                {
                    "criterion": "delivery",
                    "score": 5,
                    "max_score": 5,
                    "evidence": ["The demo recording is complete and clear."],
                }
            ],
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
            "concept_scores": [],
            "assignment_requirement_scores": [],
            "rubric_scores": [],
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
