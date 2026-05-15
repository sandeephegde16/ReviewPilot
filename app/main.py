"""HTTP entrypoints for the ReviewPilot API."""

from __future__ import annotations

import sqlite3
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

from app.config import get_database_path
from app.logging_config import configure_logging
from app.schemas import (
    ApiError,
    ApiErrorResponse,
    SessionSubmission,
    SessionSummary,
    StudentSubmission,
)
from app.session_store import (
    SessionNotFoundError,
    StudentNotFoundError,
    list_session_submissions,
    list_session_summaries,
    list_student_submissions,
)
from app.telemetry import emit_event

configure_logging()

app = FastAPI(title="ReviewPilot", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple health response for the API."""
    return {"status": "ok"}


@app.get(
    "/allsessions",
    response_model=list[SessionSummary],
    responses={500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def get_all_sessions(
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> list[SessionSummary] | JSONResponse:
    """Return all stored session titles and topics."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_all_sessions.request_received",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    try:
        session_summaries = list_session_summaries(
            database_path=get_database_path(),
            trace_id=trace_id,
        )
    except sqlite3.Error:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            step_name="get_all_sessions.request_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="session_query_failed",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="session_query_failed",
                message="Unable to fetch session summaries.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_all_sessions.request_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return session_summaries


@app.get(
    "/sessions/{session_id}/submissions",
    response_model=list[SessionSubmission],
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["submissions"],
)
def get_session_submissions(
    session_id: str,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> list[SessionSubmission] | JSONResponse:
    """Return all assignment submissions associated with a session."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_session_submissions.request_received",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    try:
        session_submissions = list_session_submissions(
            database_path=get_database_path(),
            session_id=session_id,
            trace_id=trace_id,
        )
    except SessionNotFoundError:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            step_name="get_session_submissions.request_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="session_not_found",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="session_not_found",
                message="Unable to find the requested session.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=404, content=error_response.model_dump())
    except sqlite3.Error:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            step_name="get_session_submissions.request_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="session_submission_query_failed",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="session_submission_query_failed",
                message="Unable to fetch session submissions.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_session_submissions.request_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return session_submissions


@app.get(
    "/students/{student_id}/submissions",
    response_model=list[StudentSubmission],
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["submissions"],
)
def get_student_submissions(
    student_id: str,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> list[StudentSubmission] | JSONResponse:
    """Return all assignment submissions associated with a student."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_student_submissions.request_received",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="pending",
        retry_count=0,
    )
    try:
        student_submissions = list_student_submissions(
            database_path=get_database_path(),
            student_id=student_id,
            trace_id=trace_id,
        )
    except StudentNotFoundError:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            step_name="get_student_submissions.request_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="student_not_found",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="student_not_found",
                message="Unable to find the requested student.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=404, content=error_response.model_dump())
    except sqlite3.Error:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            step_name="get_student_submissions.request_failed",
            tool_name=None,
            data_store="sqlite",
            provider_name=None,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="student_submission_query_failed",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="student_submission_query_failed",
                message="Unable to fetch student submissions.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=None,
        step_name="get_student_submissions.request_completed",
        tool_name=None,
        data_store="sqlite",
        provider_name=None,
        validation_status="passed",
        retry_count=0,
        elapsed_ms=elapsed_ms,
    )
    return student_submissions
