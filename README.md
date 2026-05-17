# ReviewPilot

ReviewPilot is an early bootstrap for an assignment review agent. The current repository contains a minimal FastAPI app, a SQLite schema, an OpenAPI spec, and a design spec for the larger review workflow.

## What is here now

- `app/main.py`: FastAPI app with `GET /health`, `GET /allsessions`, `GET /sessions/{session_id}/concepts`, `PUT /sessions/{session_id}/concepts`, `POST /sessions/{session_id}/extract-concepts`, `GET /sessions/{session_id}/assignment-requirements`, `PUT /sessions/{session_id}/assignment-requirements`, `POST /sessions/{session_id}/extract-assignment-requirements`, `POST /grade/concepts`, `GET /sessions/{session_id}/submissions`, and `GET /students/{student_id}/submissions`
- `db/schema.sql`: SQLite schema for students, session content, assignment requirements, and submissions
- `openapi/reviewpilot.openapi.yaml`: OpenAPI contract for the current HTTP endpoints
- `DESIGN_SPEC.md`: target architecture and planned review flow
- `Makefile`: common setup, run, lint, test, and database commands

## Quick start

Requirements:

- Python 3.12+
- `uv`
- `sqlite3`

```bash
make sync
make db-schema-check
make db-init
make run
```

The app starts on `http://127.0.0.1:8000`. The browser UI redirects `/` to
`/assignments`. Available endpoints:

- `GET /health`
- `GET /allsessions`
- `GET /sessions/{session_id}/concepts`
- `PUT /sessions/{session_id}/concepts`
- `POST /sessions/{session_id}/extract-concepts`
- `GET /sessions/{session_id}/assignment-requirements`
- `PUT /sessions/{session_id}/assignment-requirements`
- `POST /sessions/{session_id}/extract-assignment-requirements`
- `POST /grade/concepts`
- `GET /sessions/{session_id}/submissions`
- `GET /students/{student_id}/submissions`

Session API telemetry is emitted as one JSON log line per event to server stdout.

## Structured extraction providers

`POST /sessions/{session_id}/extract-concepts` and
`POST /sessions/{session_id}/extract-assignment-requirements`
now share the same provider routing, schema validation, and repair flow.
Successful concept extraction also persists the extracted concept list to
`session_content.concepts_json`.
Successful assignment requirement extraction also persists each assignment's
extracted requirement list to `assignment_requirement.assignment_requirements_json`.
`POST /grade/concepts` reuses the same structured extraction stack, but it
collects bounded project evidence first and only falls back across configured
real models. It does not fall back to the heuristic provider. Successful
concept grading also persists the extracted concept scores JSON to
`student_grades.concept_scores`.

Available provider modes:

- `anthropic` (default primary): real Claude API call using forced tool output with the canonical schema
- `gemini` (default secondary): real Gemini API call using structured JSON schema output
- `heuristic` (default final fallback): local deterministic fallback, no external API call

Each extracted concept includes `concept_importance`, an integer from `1` to `10`
that indicates how central the concept is to the session.

Configuration is now split into:

- [.reviewpilot.config.json](/Users/sandeep.hegde/IdeaProjects/EAG_V3/Assignment_Week5_GradePilot/.reviewpilot.config.json): tracked provider routing policy, model order, and cooldown settings
- `.env`: local API keys loaded automatically at startup
- [.env.example](/Users/sandeep.hegde/IdeaProjects/EAG_V3/Assignment_Week5_GradePilot/.env.example): template for the local `.env`

Provider routing config:

```json
{
  "concept_extraction": {
    "primary_provider": "anthropic",
    "fallback_providers": ["gemini", "heuristic"],
    "model_candidates": {
      "anthropic": ["claude-sonnet-4-6"],
      "gemini": ["gemini-2.5-flash"],
      "heuristic": ["heuristic-v1"]
    },
    "cooldown_seconds": 60,
    "failures_before_cooldown": 2
  },
  "concept_grading": {
    "primary_provider": "anthropic",
    "fallback_providers": ["gemini"],
    "model_candidates": {
      "anthropic": ["claude-sonnet-4-6"],
      "gemini": ["gemini-2.5-flash"]
    },
    "cooldown_seconds": 60,
    "failures_before_cooldown": 2
  }
}
```

Local `.env`:

```bash
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

Environment variables still override the repo config when you need a one-off change:

- `REVIEWPILOT_CONCEPT_PROVIDER`
- `REVIEWPILOT_CONCEPT_MODEL`
- `REVIEWPILOT_CONCEPT_FALLBACK_PROVIDERS`
- `REVIEWPILOT_CONCEPT_GRADING_PROVIDER`
- `REVIEWPILOT_CONCEPT_GRADING_MODEL`
- `REVIEWPILOT_CONCEPT_GRADING_FALLBACK_PROVIDERS`
- `REVIEWPILOT_ANTHROPIC_CONCEPT_MODELS`
- `REVIEWPILOT_GEMINI_CONCEPT_MODELS`
- `REVIEWPILOT_HEURISTIC_CONCEPT_MODELS`
- `REVIEWPILOT_ANTHROPIC_CONCEPT_GRADING_MODELS`
- `REVIEWPILOT_GEMINI_CONCEPT_GRADING_MODELS`
- `REVIEWPILOT_PROVIDER_FAILURES_BEFORE_COOLDOWN`
- `REVIEWPILOT_PROVIDER_COOLDOWN_SECONDS`

## Useful commands

```bash
make lint
make test
make db-shell
```

## Current status

This is still a scaffold. The multi-step review loop, tool orchestration, tracing, and review APIs described in `DESIGN_SPEC.md` are not implemented yet.
