# ReviewPilot

ReviewPilot is an early bootstrap for an assignment review agent. The current repository contains a minimal FastAPI app, a SQLite schema, an OpenAPI spec, and a design spec for the larger review workflow.

## What is here now

- `app/main.py`: FastAPI app with `GET /health` and `GET /allsessions`
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

The app starts on `http://127.0.0.1:8000`. Available endpoints:

- `GET /health`
- `GET /allsessions`

Session API telemetry is emitted as one JSON log line per event to server stdout.

## Useful commands

```bash
make lint
make test
make db-shell
```

## Current status

This is still a scaffold. The multi-step review loop, tool orchestration, tracing, and review APIs described in `DESIGN_SPEC.md` are not implemented yet.
