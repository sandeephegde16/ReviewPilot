"""HTTP entrypoints for the ReviewPilot API."""

from __future__ import annotations

import sqlite3
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse

from app.concept_orchestrator import (
    DEFAULT_REASONING_TYPE,
    DEFAULT_TOOL_NAME,
    ConceptExtractionError,
    extract_concepts_for_session,
)
from app.config import get_database_path
from app.logging_config import configure_logging
from app.schemas import (
    ApiError,
    ApiErrorResponse,
    ExtractConceptsRequest,
    ExtractConceptsResponse,
    SessionSubmission,
    SessionSummary,
    StudentSubmission,
)
from app.session_store import (
    SessionNotFoundError,
    StudentNotFoundError,
    get_session_extraction_source,
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


@app.post(
    "/sessions/{session_id}/extract-concepts",
    response_model=ExtractConceptsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def extract_session_concepts(
    session_id: str,
    request: Annotated[ExtractConceptsRequest | None, Body()] = None,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> ExtractConceptsResponse | JSONResponse:
    """Extract gradeable concepts for a session using normalized session evidence."""
    trace_id = x_trace_id or uuid4().hex
    extraction_request = request or ExtractConceptsRequest()
    start_time = perf_counter()
    emit_event(
        trace_id=trace_id,
        review_id=None,
        session_id=session_id,
        step_name="extract_session_concepts.request_received",
        tool_name=DEFAULT_TOOL_NAME,
        data_store="sqlite",
        provider_name=None,
        model_name=None,
        reasoning_level=extraction_request.reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        validation_status="pending",
        retry_count=0,
    )
    try:
        session_source = get_session_extraction_source(
            database_path=get_database_path(),
            session_id=session_id,
            trace_id=trace_id,
        )
        emit_event(
            trace_id=trace_id,
            review_id=None,
            session_id=session_source.id,
            step_name="extract_session_concepts.session_fetched",
            tool_name=DEFAULT_TOOL_NAME,
            data_store="sqlite",
            provider_name=None,
            model_name=None,
            reasoning_level=extraction_request.reasoning_level,
            reasoning_type=DEFAULT_REASONING_TYPE,
            validation_status="passed",
            retry_count=0,
        )
        extraction_result = extract_concepts_for_session(
            session_source=session_source,
            reasoning_level=extraction_request.reasoning_level,
            trace_id=trace_id,
        )
    except SessionNotFoundError:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            session_id=session_id,
            step_name="extract_session_concepts.request_failed",
            tool_name=DEFAULT_TOOL_NAME,
            data_store="sqlite",
            provider_name=None,
            model_name=None,
            reasoning_level=extraction_request.reasoning_level,
            reasoning_type=DEFAULT_REASONING_TYPE,
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
            session_id=session_id,
            step_name="extract_session_concepts.request_failed",
            tool_name=DEFAULT_TOOL_NAME,
            data_store="sqlite",
            provider_name=None,
            model_name=None,
            reasoning_level=extraction_request.reasoning_level,
            reasoning_type=DEFAULT_REASONING_TYPE,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
            failure_reason="session_extraction_source_query_failed",
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code="session_extraction_source_query_failed",
                message="Unable to fetch the session data required for concept extraction.",
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())
    except ConceptExtractionError as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        emit_event(
            trace_id=trace_id,
            review_id=None,
            session_id=session_id,
            step_name="extract_session_concepts.request_failed",
            tool_name=DEFAULT_TOOL_NAME,
            data_store="sqlite",
            provider_name=exc.provider_name,
            model_name=exc.model_name,
            reasoning_level=extraction_request.reasoning_level,
            reasoning_type=DEFAULT_REASONING_TYPE,
            validation_status="failed",
            retry_count=exc.retry_count,
            elapsed_ms=elapsed_ms,
            failure_reason=exc.code,
        )
        error_response = ApiErrorResponse(
            error=ApiError(
                code=exc.code,
                message=exc.message,
                trace_id=trace_id,
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    emit_event(
        trace_id=trace_id,
        review_id=None,
        session_id=session_id,
        step_name="extract_session_concepts.request_completed",
        tool_name=DEFAULT_TOOL_NAME,
        data_store="sqlite",
        provider_name=extraction_result.provider_name,
        model_name=extraction_result.model_name,
        reasoning_level=extraction_request.reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        validation_status="passed",
        retry_count=extraction_result.retry_count,
        elapsed_ms=elapsed_ms,
    )
    return extraction_result.response


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
