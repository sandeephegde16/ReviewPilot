"""Structured telemetry helpers for API workflows."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("reviewpilot")


def emit_event(
    *,
    trace_id: str,
    step_name: str,
    review_id: str | None,
    session_id: str | None = None,
    validation_status: str,
    retry_count: int,
    elapsed_ms: float | None = None,
    tool_name: str | None = None,
    data_store: str | None = None,
    provider_name: str | None = None,
    model_name: str | None = None,
    reasoning_level: str | None = None,
    reasoning_type: str | None = None,
    failure_reason: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Emit a structured telemetry event for request processing."""
    payload = {
        "trace_id": trace_id,
        "review_id": review_id,
        "session_id": session_id,
        "step_name": step_name,
        "tool_name": tool_name,
        "data_store": data_store,
        "provider_name": provider_name,
        "model_name": model_name,
        "reasoning_level": reasoning_level,
        "reasoning_type": reasoning_type,
        "validation_status": validation_status,
        "retry_count": retry_count,
        "elapsed_ms": elapsed_ms,
        "failure_reason": failure_reason,
        "details": details,
    }
    logger.info(json.dumps(payload))


@dataclass(frozen=True)
class WorkflowTelemetryEmitter:
    """Emit workflow events while reusing shared telemetry fields."""

    trace_id: str
    review_id: str | None
    session_id: str | None = None
    tool_name: str | None = None
    data_store: str | None = None
    reasoning_level: str | None = None
    reasoning_type: str | None = None
    step_prefix: str | None = None

    def emit(
        self,
        *,
        validation_status: str,
        retry_count: int,
        step_name: str | None = None,
        step_suffix: str | None = None,
        session_id: str | None = None,
        tool_name: str | None = None,
        data_store: str | None = None,
        provider_name: str | None = None,
        model_name: str | None = None,
        reasoning_level: str | None = None,
        reasoning_type: str | None = None,
        elapsed_ms: float | None = None,
        failure_reason: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Emit one event using either an explicit step name or the configured prefix."""
        if step_name is None:
            if self.step_prefix is None or step_suffix is None:
                raise ValueError("A step name or step suffix is required for telemetry events.")
            step_name = f"{self.step_prefix}.{step_suffix}"

        emit_event(
            trace_id=self.trace_id,
            review_id=self.review_id,
            session_id=self.session_id if session_id is None else session_id,
            step_name=step_name,
            tool_name=self.tool_name if tool_name is None else tool_name,
            data_store=self.data_store if data_store is None else data_store,
            provider_name=provider_name,
            model_name=model_name,
            reasoning_level=(
                self.reasoning_level if reasoning_level is None else reasoning_level
            ),
            reasoning_type=self.reasoning_type if reasoning_type is None else reasoning_type,
            validation_status=validation_status,
            retry_count=retry_count,
            elapsed_ms=elapsed_ms,
            failure_reason=failure_reason,
            details=details,
        )
