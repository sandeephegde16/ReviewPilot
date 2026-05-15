# ReviewPilot Design Spec

## 1. Overview

ReviewPilot is an assignment review agent that evaluates a student or candidate submission against a structured rubric. It combines deterministic software tools with LLM reasoning to produce an evidence-backed, schema-validated, auditable review.

The system is designed to demonstrate agentic building concepts, including:

- prompt qualification
- explicit staged reasoning
- structured output
- tool calling
- separation of reasoning and tools
- conversation loops
- state tracking
- schema validation
- retries and failover
- capability-aware routing
- observability and traceability
- rubric-based evaluation
- human-in-the-loop review

This project is intentionally not a summarizer. Its core behavior is multi-step evidence collection and rubric scoring.

## 2. Product Goal

Given a submission source such as a GitHub PR, local folder, or zip upload, the system should:

1. normalize the source into a canonical review request
2. collect evidence through safe deterministic tools
3. guide an LLM through a constrained multi-step review loop
4. validate every structured response
5. produce a final auditable review report with scores, evidence, self-checks, and trace metadata

## 3. Target Users

- instructors reviewing assignment submissions
- hiring teams reviewing take-home projects
- internal reviewers auditing LLM-based evaluation workflows

## 4. Scope

### In scope

- review of code submissions using a rubric
- GitHub PR, local folder, and zip-upload inputs
- safe read-only tool execution
- multi-turn review loops
- follow-up reviewer questions after the initial review
- provider routing, retries, cooldowns, and failover
- prompt qualification and output schema validation
- structured traces for each review

### Out of scope for MVP

- autonomous merge or repository modification
- destructive shell actions
- write access to candidate repositories
- arbitrary internet browsing during review
- final decision automation without human sign-off

## 5. Design Principles

1. Deterministic tools collect facts.
2. The LLM interprets facts, not raw uncertainty.
3. Every important step must be structured and auditable.
4. The agent may reason in multiple passes, but it may not fabricate evidence.
5. Unsafe or destructive actions are not permitted.
6. Human reviewers retain final authority.

## 6. High-Level Architecture

The architecture follows the shape in the attached reference:

1. **Source adapters**
   - convert GitHub PRs, local folders, or zip uploads into a canonical submission model

2. **Structured extractors**
   - extract normalized facts from source metadata, README content, assignment requirements, and reviewer queries

3. **Canonical request builder**
   - creates one normalized `ReviewRequest` regardless of source

4. **Agent orchestrator**
   - drives the loop:
     `TOOL_REQUEST -> TOOL_RESULT -> CONTEXT_UPDATE -> ... -> FINAL_REVIEW`

5. **Tool executor**
   - executes only approved read-only tools

6. **Provider router**
   - selects an LLM provider based on required capabilities and runtime health

7. **Schema validator**
   - validates LLM outputs and system payloads with Pydantic

8. **Trace logger**
   - records tool calls, validation results, retries, failures, provider selection, and final scores

9. **Reviewer follow-up interface**
   - supports re-checks, score explanations, and limited review revisions

## 7. Core Workflow

### 7.1 Initial review

1. Client submits `POST /api/review`.
2. Source adapter resolves the submission.
3. Extractors pull structured facts:
   - repo and PR metadata
   - README content
   - assignment requirements
   - demo links
   - prompt-evaluation artifacts
4. Canonical request is assembled.
5. Router selects an LLM provider that supports required capabilities.
6. Orchestrator starts the agent loop.
7. The LLM requests tools in structured JSON.
8. Tool results are appended to review state.
9. The LLM emits context updates and requests additional tools until evidence is sufficient.
10. The LLM emits `FINAL_REVIEW`.
11. Final output is schema-validated.
12. Review report and trace are persisted.

### 7.2 Follow-up review

1. Reviewer asks a question such as:
   - why was a score reduced?
   - re-check the README for a YouTube link
   - apply updated rubric weights
2. System loads previous state and trace.
3. Orchestrator decides whether new tools are needed.
4. Agent either:
   - answers from existing evidence, or
   - performs a bounded re-check loop
5. A structured follow-up response is returned, optionally with a revised score.

## 8. Canonical API

### 8.1 Review request

`POST /api/review`

```json
{
  "source_type": "github_pr",
  "source": {
    "repo_url": "https://github.com/example/reviewpilot-student-project",
    "pr_number": 12
  },
  "rubric_id": "assignment_review_v1",
  "review_depth": "full",
  "reasoning_level": "high",
  "budget": {
    "max_tool_calls": 12,
    "max_files": 25,
    "max_runtime_seconds": 90,
    "max_retries": 2
  }
}
```

Supported `source_type` values:

- `github_pr`
- `local_folder`
- `zip_upload`

### 8.2 Follow-up request

`POST /api/review/{review_id}/question`

```json
{
  "question": "Why did Tool Calling receive 6/10?",
  "allow_recheck": true
}
```

### 8.3 Trace retrieval

`GET /api/traces/{trace_id}`

Returns a structured trace of provider selection, tool calls, validation results, retries, and final decision artifacts.

## 9. Source Adapters

Source adapters normalize different input types behind one interface.

### 9.1 GitHub PR adapter

Inputs:

- repository URL
- pull request number

Responsibilities:

- fetch PR metadata
- list changed files
- load README and key source files
- capture CI or test artifacts where available

### 9.2 Local folder adapter

Inputs:

- local filesystem path

Responsibilities:

- enumerate files
- locate README, configs, tests, artifacts, demo links
- run approved local analysis tools

### 9.3 Zip upload adapter

Inputs:

- archive file reference

Responsibilities:

- unpack into isolated review workspace
- delegate analysis to local-folder flow

## 10. Structured Extractors

Before LLM reasoning begins, the system should produce normalized intermediate outputs.

### 10.1 Submission link extractor

Extracts:

- student name or identifier
- repository URL
- GitHub username
- YouTube demo link
- LinkedIn link if required

### 10.2 Course/session concept extractor

Extracts:

- covered concepts
- required architectural patterns
- grading expectations

### 10.3 Assignment requirements extractor

Extracts:

- mandatory deliverables
- forbidden project types
- scoring criteria
- evidence expectations

### 10.4 Reviewer query extractor

Extracts:

- whether the reviewer wants explanation, re-check, or rubric adjustment
- whether new tool use is required

## 11. Tooling Model

The LLM is never allowed to inspect the filesystem or run commands directly. It can only request approved tools.

### 11.1 Tool contract

Each tool must define:

- `tool_name`
- argument schema
- return schema
- authorization level
- failure modes

### 11.2 MVP tool list

- `list_project_files`
- `read_readme`
- `read_file`
- `search_code`
- `detect_api_endpoints`
- `detect_tool_definitions`
- `run_tests`
- `extract_demo_links`
- `validate_prompt_evaluation_json`
- `detect_schema_validation`
- `detect_trace_logging`
- `detect_provider_routing`
- `detect_failover_logic`
- `detect_prompt_caching`

### 11.3 Safety model

Allowed:

- reading files
- searching code
- running approved tests or static analysis
- parsing JSON artifacts

Disallowed:

- deleting files
- editing repositories under review
- network actions outside approved adapters
- arbitrary shell execution

## 12. Agent Protocol

The LLM communicates through a strict message protocol.

### 12.1 Response types

- `TOOL_REQUEST`
- `TOOL_RESULT`
- `CONTEXT_UPDATE`
- `FINAL_REVIEW`
- `FALLBACK`

### 12.2 TOOL_REQUEST schema

```json
{
  "response_type": "TOOL_REQUEST",
  "step_number": 1,
  "reasoning_type": "evidence_lookup",
  "reasoning_summary": "Need README and file inventory before scoring.",
  "tool_calls": [
    {
      "tool_name": "read_readme",
      "arguments": {
        "submission_id": "candidate_001"
      }
    },
    {
      "tool_name": "list_project_files",
      "arguments": {
        "submission_id": "candidate_001",
        "limit": 200
      }
    }
  ]
}
```

### 12.3 CONTEXT_UPDATE schema

```json
{
  "response_type": "CONTEXT_UPDATE",
  "step_number": 2,
  "reasoning_type": "code_inspection",
  "knowledge_state": {
    "readme_checked": true,
    "files_indexed": true,
    "api_detected": false,
    "tests_run": false
  },
  "next_goal": "Verify canonical API and schema validation implementation."
}
```

### 12.4 FINAL_REVIEW schema

```json
{
  "response_type": "FINAL_REVIEW",
  "candidate_id": "candidate_001",
  "overall_score": 82,
  "rubric_scores": [
    {
      "criterion": "Canonical API",
      "score": 8,
      "max_score": 10,
      "evidence": [
        "POST /api/review endpoint detected in app/api/review.py"
      ]
    }
  ],
  "missing_requirements": [
    "YouTube demo link missing"
  ],
  "self_check": {
    "readme_checked": true,
    "tests_run": true,
    "source_files_inspected": true,
    "rubric_applied": true,
    "scores_have_evidence": true,
    "no_unverified_claims": true
  },
  "trace_id": "REV-001"
}
```

### 12.5 FALLBACK schema

```json
{
  "response_type": "FALLBACK",
  "reason": "Repository could not be accessed",
  "missing_information": [
    "source files",
    "README content",
    "test results"
  ],
  "recommended_next_step": "Ask the student to provide a valid repository or zip upload.",
  "trace_id": "REV-001"
}
```

## 13. Review State Model

The orchestrator maintains a `ReviewSessionState` object containing:

- request metadata
- normalized source metadata
- extracted assignment requirements
- completed tool calls
- tool results
- known evidence map
- current reasoning step
- validation status
- budget usage
- provider attempt history
- trace ID

This state is appended after every tool result and every LLM response.

## 14. Prompt Design

### 14.1 System prompt responsibilities

The system prompt must explicitly define:

- the role as an assignment review agent
- that the model must work step-by-step
- that it may only use listed tools
- that it must not invent evidence
- exact allowed response schemas
- reasoning type tags
- self-check requirements
- fallback behavior when evidence is missing
- constraints for reviewer follow-up handling

### 14.2 Prompt qualification

The final production prompt should be evaluated by a separate prompt-evaluation assistant against criteria such as:

- explicit reasoning instructions
- structured output
- tool separation
- conversation loop support
- instructional framing
- internal self-checks
- reasoning type awareness
- fallbacks
- overall clarity

The evaluation result should be stored as a JSON artifact in the repository.

### 14.3 Prompt caching

Cache stable prompt segments:

- system prompt
- rubric definition
- tool definitions
- schema definitions
- review rules

Do not cache variable submission evidence.

## 15. Reasoning Controls

The request may specify a reasoning level:

- `low`: shallow checks such as README presence or link extraction
- `medium`: normal rubric scoring
- `high`: deeper code architecture and evidence consistency review

Provider-specific reasoning parameters should be mapped internally without leaking provider-specific details into the public API.

## 16. Budget Controls

Each review must enforce limits:

- maximum tool calls
- maximum files inspected
- maximum retries
- maximum review runtime
- optional token or cost ceiling

When a budget is exhausted, the system returns a partial review or fallback with clearly marked missing evidence.

## 17. Capability-Aware Routing

Providers are selected based on required capabilities such as:

- tool use
- structured JSON output
- code reasoning quality
- retryable rate-limit behavior

Example provider registry fields:

- provider name
- tools support
- schema-constrained output support
- reasoning control support
- cooldown state
- health score

Selection logic:

1. filter providers by required capabilities
2. remove providers in cooldown unless no alternative exists
3. sort by health, latency, or configured priority
4. attempt the best provider
5. fail over if request or validation fails

## 18. Failover and Cooldown

### Failover cases

- rate limit
- server error
- malformed model output
- unsupported structured output

### Cooldown behavior

If a provider fails due to a transient system issue, mark it unavailable for a bounded period such as 60 seconds.

The trace should record:

- provider
- error type
- cooldown duration
- next attempted provider

## 19. Schema Validation and Retry

All structured responses must be validated with Pydantic models.

### Retry triggers

- invalid JSON
- missing required fields
- unsupported enum values
- malformed tool arguments
- final review missing evidence for a score

### Retry policy

1. reject invalid output
2. return validation errors to the provider-specific wrapper
3. retry up to the configured maximum
4. if retries are exhausted, return a clean `FALLBACK` or system error

## 20. Rubric Model

The rubric must be explicit and machine-readable.

Example criteria:

- prompt qualification
- canonical API
- structured output
- tool calling
- tool and reasoning separation
- conversation loop support
- context/state tracking
- self-checks
- error handling and fallbacks
- routing and failover
- observability and traces
- README quality and demo evidence

Each rubric item must include:

- criterion name
- description
- max score
- required evidence types
- disqualifiers if any

## 21. Evidence-Backed Scoring

Every score must be grounded in collected evidence.

A score entry should include:

- criterion
- awarded score
- maximum score
- evidence citations
- deduction rationale

The final review must reject unsupported statements such as:

- "tests probably pass"
- "provider failover appears implemented"

If evidence is absent, the report must say evidence is missing.

## 22. Internal Self-Checks

Before emitting `FINAL_REVIEW`, the model must verify:

- README was checked
- key source files were inspected
- tests were run or explicitly marked unavailable
- rubric was fully applied
- every score cites evidence
- missing requirements were called out
- unsupported claims were avoided

If any self-check fails, the model must request more tools or emit a fallback.

## 23. Error Handling

### Tool failure

If a tool fails:

- capture the error
- tag missing evidence
- decide whether another tool can substitute
- continue when possible

### Missing files

If README, tests, or artifacts are missing:

- record this explicitly
- treat it as evidence of incompleteness, not silent failure

### Invalid follow-up request

If a reviewer asks for unsupported actions:

- reject safely
- explain supported follow-up operations

## 24. Observability and Traceability

Each review produces a trace record with:

- trace ID
- request ID
- source type
- provider selected
- provider attempts
- tools called
- tool durations
- validation results
- retries
- cooldown actions
- final score
- fallback usage

Trace example:

```json
{
  "trace_id": "REV-001",
  "selected_provider": "openai",
  "source_type": "github_pr",
  "tools_called": [
    "read_readme",
    "list_project_files",
    "detect_api_endpoints",
    "run_tests"
  ],
  "schema_validation": {
    "status": "passed",
    "retry_count": 1
  },
  "fallback_used": false,
  "final_score": 82
}
```

## 25. Human-in-the-Loop Model

The system recommends, the human decides.

Human reviewer capabilities:

- inspect the final report
- inspect the trace
- ask why a score was given
- request targeted re-checks
- adjust rubric weights for a rerun
- override the final disposition externally

The human may not bypass evidence or force unsupported claims into the report.

## 26. Security Constraints

- all tool actions must be allowlisted
- no destructive commands
- no repository mutation
- no arbitrary shell access from the LLM
- temporary workspaces must be isolated and disposable
- external provider secrets must be stored outside the prompt and trace payloads

## 27. Suggested Tech Stack

### Backend

- Python 3.12
- FastAPI for HTTP APIs
- Pydantic for schemas and validation

### Orchestration

- internal review orchestrator module
- provider abstraction layer
- tool registry with typed arguments

### Storage

- lightweight JSON trace store for MVP
- optional SQLite or Postgres later

### Testing

- pytest
- fixture repos or sample submissions

## 28. Proposed Repository Layout

```text
app/
  api/
    review.py
    followup.py
    traces.py
  adapters/
    github_pr.py
    local_folder.py
    zip_upload.py
  orchestrator/
    engine.py
    state.py
    router.py
    retry.py
  prompts/
    system_prompt.md
    rubric_prompt.md
  providers/
    base.py
    openai_provider.py
    gemini_provider.py
  schemas/
    request.py
    protocol.py
    review.py
    trace.py
  tools/
    registry.py
    readme.py
    files.py
    tests.py
    analysis.py
  scoring/
    rubric.py
    evidence.py
  traces/
    store.py
tests/
  fixtures/
  test_api.py
  test_schemas.py
  test_router.py
  test_review_loop.py
evals/
  prompt_qualification/
    final_prompt_review.json
README.md
DESIGN_SPEC.md
```

## 29. MVP Milestones

### Milestone 1: skeletal API and schemas

- define Pydantic models
- implement `POST /api/review`
- implement local-folder adapter

### Milestone 2: tool loop

- implement tool registry
- implement `TOOL_REQUEST` and `CONTEXT_UPDATE` flow
- add safe tools for files, README, endpoint detection, and tests

### Milestone 3: scoring and final review

- implement rubric application
- implement evidence-backed `FINAL_REVIEW`
- add self-check enforcement

### Milestone 4: robustness features

- schema validation retries
- provider routing
- failover and cooldown
- trace logging

### Milestone 5: assignment-ready artifacts

- README with architecture and demo
- prompt qualification artifact
- sample review output
- YouTube demo link

## 30. Success Criteria

The project is successful if it demonstrates:

1. one canonical review API across multiple source types
2. a real multi-step tool-driven agent loop
3. strict structured outputs with validation
4. evidence-backed rubric scoring
5. safe and explicit failure handling
6. observable traces for every review
7. follow-up review capability after the initial report

## 31. Open Questions

- Should MVP support only local-folder reviews first, then add GitHub PR support later?
- Should test execution be mandatory for a passing review when tests exist?
- Should reviewer follow-up allow rubric reweighting or only evidence re-checks?
- Which provider should be primary for the first implementation?

## 32. Recommended MVP Decision

Build the first working version with:

- FastAPI
- local-folder input
- one provider plus one fallback provider abstraction
- 6 to 8 read-only tools
- one rubric
- full trace logging
- follow-up question endpoint

That is enough to satisfy the assignment's agentic-building concepts without turning the first version into a framework project.
