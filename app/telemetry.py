"""Structured telemetry helpers for API workflows."""

from __future__ import annotations

import json
import logging

logger = logging.getLogger("reviewpilot")


def emit_event(
    *,
    trace_id: str,
    step_name: str,
    review_id: str | None,
    validation_status: str,
    retry_count: int,
    elapsed_ms: float | None = None,
    tool_name: str | None = None,
    data_store: str | None = None,
    provider_name: str | None = None,
    failure_reason: str | None = None,
) -> None:
    """Emit a structured telemetry event for request processing."""
    payload = {
        "trace_id": trace_id,
        "review_id": review_id,
        "step_name": step_name,
        "tool_name": tool_name,
        "data_store": data_store,
        "provider_name": provider_name,
        "validation_status": validation_status,
        "retry_count": retry_count,
        "elapsed_ms": elapsed_ms,
        "failure_reason": failure_reason,
    }
    logger.info(json.dumps(payload))
