# ReviewPilot

ReviewPilot is an evidence-backed assignment review system for transcript-driven concept extraction, assignment-requirement extraction, project grading, and workflow orchestration.

The repository is built around one constraint: the LLM should interpret collected facts, but it should not invent them. Extraction, grading, persistence, and orchestration are all schema-driven and observable.

## What This Repo Demonstrates

This codebase is useful as a reference implementation for the following concepts:

- Schema-driven LLM requests and responses using Pydantic models
- Canonical prompt construction separated from provider execution
- Provider routing with fallback and cooldown behavior
- Structured output validation with one repair attempt
- Evidence-backed grading from bounded repository snippets
- Conversation-loop orchestration with tool planning and terminal conditions
- SQLite-backed persistence for session content, assignments, submissions, and grades
- Structured telemetry for API, workflow, provider, and persistence steps
- UI workflows that operate on stored session state instead of transient prompt state

## Current Product Surface

ReviewPilot currently supports:

- extracting gradeable concepts from a stored session transcript
- extracting assignment requirements from stored assignment descriptions
- grading a student submission against concepts
- grading a student submission against assignment requirements
- orchestrating multi-step review flows through a planner loop
- viewing sessions, assignments, submissions, and stored grades through the browser UI

The browser UI is served from the backend and redirects `/` to `/assignments`.

## Core Review Flow

The main vertical slice in this repo is:

1. Store a session transcript and assignment metadata in SQLite.
2. Extract gradeable concepts from the session transcript.
3. Extract assignment requirements from assignment descriptions.
4. Collect bounded project evidence from a repo, local folder, or zip upload.
5. Grade the submission against stored concepts and assignment requirements.
6. Persist structured scores to `student_grades`.
7. Advance submission status in `assignment_submissions`.

The orchestrator adds a planner loop in front of those workflows so a single request can run one or more of them in sequence.

## Architecture

### 1. HTTP layer

`app/main.py` exposes the API and converts domain failures into structured error responses. Responses are pretty-printed JSON to make browser inspection easier during development.

### 2. Prompt shaping

The spec modules build canonical requests:

- `app/concept_extraction_spec.py`
- `app/assignment_requirement_extraction_spec.py`
- `app/concept_grading_spec.py`
- `app/assignment_requirement_grading_spec.py`
- `app/orchestrator_spec.py`

These modules are responsible for:

- prompt input fields
- system instructions
- repair guidance
- schema selection
- mapping validated output back into API responses

### 3. Structured provider layer

The shared LLM execution path lives in:

- `app/structured_provider.py`
- `app/structured_extraction.py`
- `app/external_provider_payloads.py`

This layer handles:

- provider-specific payload creation
- structured schema enforcement
- validation
- one repair attempt after schema failure
- provider/model routing
- retry metadata and telemetry

### 3a. LLM execution details

This repo explicitly uses the following patterns:

- `tool calls`:
  the orchestrator planner does not execute workflows directly. It returns
  structured `TOOL_REQUEST` responses with allowlisted `tool_calls`, and the
  backend executes those tools.

- `canonical requests`:
  each extraction, grading, and planner turn is shaped into one canonical
  structured request before it reaches a provider. Prompt construction is
  separated from provider invocation.

- `structured output`:
  every LLM-facing workflow has a fixed response schema backed by Pydantic
  models. The model is expected to return machine-parseable output, not free-form
  prose.

- `constrained decoding`:
  provider payloads are shaped to force structured output modes. Anthropic uses
  forced tool output with the supplied schema, and Gemini uses structured JSON
  schema output.

- `schema validation`:
  provider output is validated after the call. If validation fails, the system
  performs one repair attempt using validation-aware repair guidance. If repair
  still fails, the request returns a structured failure.

- `multi-provider routing`:
  provider/model candidates are chosen through the shared routing layer. The
  system tracks retries and cooldown behavior instead of hardcoding one provider
  path.

- `failover and fallback`:
  if a provider cannot be built, fails during invocation, or returns invalid
  structured output, routing advances to the next configured candidate. Concept
  extraction can fall back to a heuristic provider when configured. Grading and
  orchestrator planning only use non-heuristic real-model candidates.

- `telemetry`:
  request, provider, validation, repair, persistence, and orchestrator steps all
  emit structured events with traceable metadata.

### 4. Workflow layer

Reusable workflows live in `app/review_workflows.py`.

These functions are used by both:

- the direct HTTP endpoints
- the orchestrator tool executions

That keeps prompt logic and grading logic in one place instead of duplicating them per entrypoint.

### 5. Orchestrator loop

The orchestrator lives in:

- `app/orchestrator_service.py`
- `app/orchestrator_spec.py`
- `app/orchestrator_provider.py`

It is a real loop, not a one-shot router:

1. load current session and submission state
2. ask planner for the next action
3. execute allowlisted coarse tools
4. feed tool results back into the next planner turn
5. repeat until `FINAL_REVIEW` or `FALLBACK`

The orchestrator protocol uses these response types:

- `TOOL_REQUEST`
- `CONTEXT_UPDATE`
- `FINAL_REVIEW`
- `FALLBACK`

### 6. Persistence layer

SQLite access and persistence helpers live in:

- `app/session_store.py`
- `app/session_content_store.py`
- `app/assignment_requirement_store.py`
- `app/student_grade_store.py`

The repo intentionally uses explicit query helpers instead of a large ORM abstraction.

## API Endpoints

### Health and orchestration

- `GET /health`
- `POST /orchestrator/run`

### Session content

- `GET /allsessions`
- `GET /sessions/{session_id}/concepts`
- `PUT /sessions/{session_id}/concepts`
- `POST /sessions/{session_id}/extract-concepts`
- `GET /sessions/{session_id}/assignment-requirements`
- `PUT /sessions/{session_id}/assignment-requirements`
- `POST /sessions/{session_id}/extract-assignment-requirements`
- `GET /sessions/{session_id}/assignments`

### Grading

- `POST /grade/concepts`
- `POST /grade/assignment-requirements`

### Submission views

- `GET /sessions/{session_id}/submissions`
- `GET /students/{student_id}/submissions`

The OpenAPI contract is stored in `openapi/reviewpilot.openapi.yaml`.

## Orchestrator Operations

`POST /orchestrator/run` accepts these high-level operations:

- `synthesize_concepts`
- `synthesize_assignment_requirements`
- `grade_concepts`
- `grade_assignment_requirements`
- `grade_rubrics`
- `grade_all`

Current implementation notes:

- `grade_concepts` only allows concept-related coarse tools
- `grade_assignment_requirements` only allows requirement-related coarse tools
- `grade_all` can chain extraction and grading together
- `grade_rubrics` is recognized but not implemented yet and returns a structured failure

### Example orchestrator request

```json
{
  "operation": "grade_all",
  "session_id": "session-newer",
  "student_id": "student-ada",
  "assignment_requirement_id": "assignment-mcp",
  "source_type": "local_folder",
  "local_path": "/tmp/student-project",
  "reasoning_level": "medium",
  "refresh_policy": "reuse_or_missing"
}
```

## Scoring Rules

Both concept grading and assignment-requirement grading use the same normalized scoring rules:

- every item has `max_score = 50`
- awarded scores are rounded up to the next multiple of `5`
- awarded scores are clamped to the range `25..50`

Examples:

- `24 -> 25`
- `26 -> 30`
- `33 -> 35`
- `49 -> 50`

This is enforced in the backend schema layer, not only in prompt text.

## Evidence Collection

Project grading does not send the entire repository blindly to the LLM.

`app/project_evidence.py` collects bounded evidence such as:

- file inventory
- README or documentation snippets
- implementation snippets
- test snippets
- a summarized evidence bundle

The grading prompts are explicitly instructed to use only collected evidence.

## Data Model

The SQLite schema is defined in `db/schema.sql`.

Main tables:

- `students`
- `session_content`
- `assignment_requirement`
- `assignment_submissions`
- `student_grades`

Key persisted JSON fields:

- `session_content.concepts_json`
- `assignment_requirement.assignment_requirements_json`
- `assignment_submissions.status`
- `student_grades.concept_scores`
- `student_grades.assignment_requirement_scores`
- `student_grades.rubric_scores`

Submission status currently supports:

- `submitted`
- `under_review`
- `concepts_graded`
- `assignment_requirements_graded`
- `reviewed`
- `needs_resubmission`

## Telemetry and Observability

Telemetry is a first-class part of the design.

Structured events are emitted for:

- API request start and completion
- query start, completion, and failure
- provider selection
- provider invocation
- schema validation
- repair attempts
- workflow persistence
- orchestrator planner turns

Common event fields include:

- `trace_id`
- `review_id` when available
- `session_id`
- `step_name`
- `tool_name`
- `provider_name`
- `model_name`
- `validation_status`
- `retry_count`
- `elapsed_ms`
- `failure_reason`

Telemetry helpers live in `app/telemetry.py`.

## Provider Configuration

Tracked provider policy lives in `.reviewpilot.config.json`.

Current config sections:

- `concept_extraction`
- `concept_grading`

These define:

- primary provider
- fallback providers
- model candidate order
- cooldown duration
- failures before cooldown

Local secrets live in `.env`:

```bash
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Environment variables can still override provider behavior for one-off runs. The config helper lives in `app/config.py`.

## Repository Layout

```text
app/
  main.py                           HTTP API entrypoints
  schemas.py                        Pydantic request/response and orchestrator schemas
  structured_provider.py            Provider abstraction for structured outputs
  structured_extraction.py          Validation, repair, and provider routing
  external_provider_payloads.py     Anthropic/Gemini payload shaping
  review_workflows.py               Reusable extraction and grading workflows
  orchestrator_service.py           Conversation-loop orchestration engine
  orchestrator_spec.py              Planner prompt shaping
  project_evidence.py               Bounded repository evidence collection
  session_store.py                  Read-side SQLite queries
  student_grade_store.py            Grade persistence and submission status updates
  ui/                               Browser UI assets
db/
  schema.sql                        SQLite schema
openapi/
  reviewpilot.openapi.yaml          Generated API contract
tests/
  test_main.py                      End-to-end API and orchestrator tests
  test_telemetry.py                 Telemetry formatting coverage
```

## Quick Start

Requirements:

- Python 3.12+
- `uv`
- `sqlite3`

Commands:

```bash
make sync
make db-schema-check
make db-init
make run
```

After startup:

- API: `http://127.0.0.1:8000`
- UI: `http://127.0.0.1:8000/assignments`

## Development Commands

```bash
make lint
make test
make db-shell
```

## Testing

The test suite covers:

- API request and response validation
- structured extraction provider routing
- schema repair behavior
- grading persistence
- submission status updates
- orchestrator turn progression
- telemetry emission

Preferred verification commands:

```bash
make db-schema-check
make lint
make test
```

## Known Gaps

These are the main current limitations:

- rubric grading is not implemented yet
- planner/provider configuration is still concept-config-driven rather than fully split by workflow
- SQLite schema changes are handled directly; there is no general migration framework
- the UI surfaces stored grades and documents, so stale grading rows can exist until a regrade runs

## Practical Reading Order

If you want to understand the repo quickly, read files in this order:

1. `app/main.py`
2. `app/schemas.py`
3. `app/review_workflows.py`
4. `app/structured_extraction.py`
5. `app/orchestrator_service.py`
6. `app/session_store.py`
7. `db/schema.sql`

That sequence maps the public API, the request/response contracts, the shared LLM workflow path, the orchestrator loop, and the underlying storage model.

## Exact Orchestrator Prompt Used

The following is the exact orchestrator planner instruction block currently used in the codebase. This comes from the `system_instruction_lines` and `repair_guidance_lines` used by the orchestrator planner request.

```python
system_instruction_lines=[
    "You are ReviewPilot Orchestrator Agent.",
    (
        "Your job is to decide what to do next in a multi-turn workflow to satisfy "
        "the requested operation."
    ),
    "You do not execute tools yourself.",
    "You must use tool calls for extraction and grading work.",
    "You must base decisions only on the current state and previous tool results.",
    "Do not invent evidence, artifacts, or successful tool outcomes.",
    "Work in these stages:",
    "1. Validate required inputs.",
    "2. Inspect current_state and previous tool results.",
    "3. Decide whether stored artifacts can be reused or must be refreshed.",
    "4. Choose the smallest correct next action or terminal response.",
    "5. Run the required self-checks before returning.",
    "Reason step-by-step internally, but do not reveal hidden chain-of-thought.",
    "Return only visible reasoning_summary and the required structured fields.",
    (
        "You may return only one of these response types: TOOL_REQUEST, "
        "CONTEXT_UPDATE, FINAL_REVIEW, FALLBACK."
    ),
    "Use only tools listed in Available tools.",
    "Never request duplicate tool calls unless refresh_policy is force_refresh.",
    "Prefer the smallest next step that makes progress.",
    (
        "Respect prerequisites: grade_concepts requires concepts; "
        "grade_assignment_requirements requires assignment requirements."
    ),
    "If a tool fails, use the failure result in your next decision.",
    "If required inputs are missing and no allowed tool can recover them, return FALLBACK.",
    "Return FINAL_REVIEW only if the Completion condition is satisfied in Current state.",
    "Self-check before returning:",
    "- every tool call is allowlisted",
    "- prerequisites are already satisfied or made satisfiable by this turn",
    "- duplicate actions are avoided",
    "- the selected response is minimal for the requested operation",
    "- FALLBACK is used when progress is no longer possible",
],
repair_guidance_lines=[
    "TOOL_REQUEST responses must include at least one tool_calls entry.",
    "CONTEXT_UPDATE responses must include context_update and no tool_calls.",
    "FINAL_REVIEW responses must include final_review and no tool_calls.",
    "FALLBACK responses must include error.error_code and error.message.",
    "Always return checks with all required boolean fields.",
]
```

## Prompt Evaluation Output

The following is the prompt-evaluation output for the orchestrator prompt above.

```json
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": false,
  "fallbacks": true,
  "overall_clarity": "Excellent orchestration prompt. It clearly defines the agent role, separates orchestration from tool execution, supports multi-turn state through current_state and previous tool results, includes response-type constraints, handles failures and missing inputs, and adds repair guidance for schema compliance. The main improvements would be to include the full JSON schema directly, explicitly require a reasoning_type field if needed for evaluation, and define the exact required boolean fields for checks."
}
```
