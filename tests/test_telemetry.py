"""Tests for structured telemetry formatting."""

from __future__ import annotations

import io
import logging

from app.telemetry import emit_event, logger


def test_emit_event_pretty_prints_json_payload() -> None:
    """Structured telemetry events should be logged as indented JSON blocks."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    original_handlers = list(logger.handlers)
    original_level = logger.level
    original_propagate = logger.propagate
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        emit_event(
            trace_id="trace-123",
            review_id=None,
            session_id="session-123",
            step_name="example.step",
            tool_name="example_tool",
            data_store="sqlite",
            provider_name=None,
            model_name=None,
            reasoning_level="medium",
            reasoning_type="workflow_orchestration",
            validation_status="passed",
            retry_count=0,
            elapsed_ms=1.25,
            failure_reason=None,
            details={"artifact_count": 2},
        )
    finally:
        handler.flush()
        logger.handlers = original_handlers
        logger.setLevel(original_level)
        logger.propagate = original_propagate

    assert stream.getvalue() == (
        '{\n'
        '  "trace_id": "trace-123",\n'
        '  "review_id": null,\n'
        '  "session_id": "session-123",\n'
        '  "step_name": "example.step",\n'
        '  "tool_name": "example_tool",\n'
        '  "data_store": "sqlite",\n'
        '  "provider_name": null,\n'
        '  "model_name": null,\n'
        '  "reasoning_level": "medium",\n'
        '  "reasoning_type": "workflow_orchestration",\n'
        '  "validation_status": "passed",\n'
        '  "retry_count": 0,\n'
        '  "elapsed_ms": 1.25,\n'
        '  "failure_reason": null,\n'
        '  "details": {\n'
        '    "artifact_count": 2\n'
        '  }\n'
        '}\n'
    )
