UV ?= uv
APP_MODULE ?= app.main:app
DB_PATH ?= db/reviewpilot.db

.PHONY: sync lock run test lint format check db-init db-shell db-schema-check

sync:
	$(UV) sync --dev

lock:
	$(UV) lock

run:
	$(UV) run uvicorn $(APP_MODULE) --reload

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

check:
	$(MAKE) lint
	$(MAKE) test

db-init:
	sqlite3 $(DB_PATH) < db/schema.sql

db-shell:
	sqlite3 $(DB_PATH)

db-schema-check:
	sqlite3 :memory: < db/schema.sql
