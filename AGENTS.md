# ReviewPilot Repo Instructions

These instructions apply to the entire repository unless a deeper `AGENTS.md` overrides them.

## Project intent

This repository implements `ReviewPilot`, an assignment review agent. The system should remain:

- evidence-backed
- schema-driven
- observable
- simple to understand

Prefer vertical slices that produce a working end-to-end path over broad framework-heavy scaffolding.

## Code style

- Keep code simple and readable.
- Keep classes small. Do not create large, multi-purpose classes. Max allowed lines 250 per class; rare exceptions allowed.
- Prefer small functions with explicit inputs and outputs.
- Prefer composition over growing one class with many responsibilities.
- Prefer straightforward control flow over clever abstractions.
- Use descriptive names. Avoid unnecessary shortening.
- Add type hints for public functions and important internal boundaries.
- Keep modules focused on one responsibility.

## Comments and docstrings

- Add enough comments for every function and class.
- Every function and class should have a short docstring that explains its purpose.
- Add inline comments for non-obvious logic, assumptions, or review-specific rules.
- Do not add noisy comments that restate obvious code line by line.

## Telemetry and observability

- Always add enough telemetry/observability for every step.
- Any multi-step workflow should emit structured logs or trace events.
- At minimum, record:
  - `trace_id`
  - `review_id` when available
  - current step name
  - tool name when a tool is invoked
  - provider name when an LLM is invoked
  - validation status
  - retry count
  - elapsed time for important operations
  - failure reason when something goes wrong
- Prefer structured events over free-form log strings.
- Do not hide failures. Record them explicitly.

## Architecture constraints

- Keep reasoning and tool execution separate.
- Tools collect facts; the LLM interprets facts.
- Do not let the LLM claim evidence that was not collected.
- Prefer Pydantic schemas at all external and orchestration boundaries.
- Keep the canonical request/response shapes stable.
- Favor safe, read-only tool behavior unless the user explicitly asks for write behavior.

## Data and schema rules

- Validate JSON-like fields at the boundary before using them.
- Keep database schema changes minimal and intentional.
- If a schema changes, update:
  - schema definitions
  - seed data if relevant
  - tests or validation checks
  - documentation when behavior changes

## API rules

- Keep API payloads predictable and machine-readable.
- Return structured error responses instead of ad hoc strings.
- Whenever an API is created or updated, create or update the OpenAPI spec file in the same change so the documented contract matches the implementation.
- Preserve the canonical review flow:
  - `TOOL_REQUEST`
  - `TOOL_RESULT`
  - `CONTEXT_UPDATE`
  - `FINAL_REVIEW`
  - `FALLBACK`

## Testing and verification

- Run the relevant checks after making changes.
- For this repo, prefer these commands when applicable:
  - `make db-schema-check`
  - `make lint`
  - `make test`
- If a change affects API contracts, add or update tests for request/response validation.
- If a change affects the database schema, validate the schema script.

## Implementation preferences

- Build the smallest complete slice first.
- Avoid premature generalization for providers, tools, or persistence.
- Keep mock data realistic enough to exercise rubric scoring and missing-evidence paths.
- When adding new behavior, prefer one clear path that works before adding configuration branches.

## Suggested defaults for new work

- Add docstrings when creating new functions and classes.
- Add trace/log events for each major orchestrator step.
- Add a small test for new schema or endpoint behavior.
- Keep new files and modules easy to scan.
