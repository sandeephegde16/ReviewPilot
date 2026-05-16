"""HTTP entrypoints for the ReviewPilot API."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.assignment_requirement_extraction_spec import (
    ASSIGNMENT_REQUIREMENT_EXTRACTION_SPEC,
    prepare_assignment_requirement_extraction,
)
from app.assignment_requirement_extraction_spec import (
    DEFAULT_REASONING_TYPE as DEFAULT_ASSIGNMENT_REASONING_TYPE,
)
from app.assignment_requirement_extraction_spec import (
    DEFAULT_STEP_PREFIX as DEFAULT_ASSIGNMENT_STEP_PREFIX,
)
from app.assignment_requirement_extraction_spec import (
    DEFAULT_TOOL_NAME as DEFAULT_ASSIGNMENT_TOOL_NAME,
)
from app.concept_extraction_spec import (
    CONCEPT_EXTRACTION_SPEC,
    prepare_concept_extraction,
)
from app.concept_extraction_spec import (
    DEFAULT_REASONING_TYPE as DEFAULT_CONCEPT_REASONING_TYPE,
)
from app.concept_extraction_spec import (
    DEFAULT_STEP_PREFIX as DEFAULT_CONCEPT_STEP_PREFIX,
)
from app.concept_extraction_spec import (
    DEFAULT_TOOL_NAME as DEFAULT_CONCEPT_TOOL_NAME,
)
from app.config import get_database_path
from app.logging_config import configure_logging
from app.schemas import (
    ApiError,
    ApiErrorResponse,
    ExtractAssignmentRequirementsRequest,
    ExtractAssignmentRequirementsResponse,
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
    list_session_assignment_requirement_sources,
    list_session_submissions,
    list_session_summaries,
    list_student_submissions,
)
from app.structured_extraction import (
    PreparedStructuredExtraction,
    StructuredExtractionError,
    StructuredExtractionSpec,
    execute_structured_extraction,
)
from app.telemetry import WorkflowTelemetryEmitter, emit_event

configure_logging()

app = FastAPI(title="ReviewPilot", version="0.1.0")


def _elapsed_ms(start_time: float) -> float:
    """Return elapsed wall-clock time in milliseconds for API telemetry."""
    return round((perf_counter() - start_time) * 1000, 3)


def _build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    trace_id: str,
) -> JSONResponse:
    """Return one structured API error response."""
    error_response = ApiErrorResponse(
        error=ApiError(
            code=code,
            message=message,
            trace_id=trace_id,
        )
    )
    return JSONResponse(status_code=status_code, content=error_response.model_dump())


def _emit_request_failed_event(
    *,
    trace_id: str,
    step_name: str,
    start_time: float,
    failure_reason: str,
    tool_name: str | None,
    session_id: str | None = None,
    provider_name: str | None = None,
    model_name: str | None = None,
    reasoning_level: str | None = None,
    reasoning_type: str | None = None,
    retry_count: int = 0,
) -> None:
    """Emit one API request failure event with consistent shared fields."""
    emit_event(
        trace_id=trace_id,
        review_id=None,
        session_id=session_id,
        step_name=step_name,
        tool_name=tool_name,
        data_store="sqlite",
        provider_name=provider_name,
        model_name=model_name,
        reasoning_level=reasoning_level,
        reasoning_type=reasoning_type,
        validation_status="failed",
        retry_count=retry_count,
        elapsed_ms=_elapsed_ms(start_time),
        failure_reason=failure_reason,
    )


def _build_request_telemetry(
    *,
    trace_id: str,
    session_id: str,
    tool_name: str,
    reasoning_level: str,
    reasoning_type: str,
    step_prefix: str,
) -> WorkflowTelemetryEmitter:
    """Build a request-scoped telemetry emitter for one extraction endpoint."""
    return WorkflowTelemetryEmitter(
        trace_id=trace_id,
        review_id=None,
        session_id=session_id,
        tool_name=tool_name,
        data_store="sqlite",
        reasoning_level=reasoning_level,
        reasoning_type=reasoning_type,
        step_prefix=step_prefix,
    )


def _run_session_structured_extraction_endpoint[
    SourceT,
    OutputModelT: BaseModel,
    ResponseModelT,
](
    *,
    session_id: str,
    trace_id: str,
    reasoning_level: str,
    tool_name: str,
    reasoning_type: str,
    step_prefix: str,
    source_fetched_step_suffix: str,
    source_query_failure_code: str,
    source_query_failure_message: str,
    fetch_source: Callable[[], SourceT],
    prepare_extraction: Callable[
        [SourceT, str], PreparedStructuredExtraction[OutputModelT, ResponseModelT]
    ],
    extraction_spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
) -> ResponseModelT | JSONResponse:
    """Run the shared request flow for one session-scoped structured extraction API."""
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=session_id,
        tool_name=tool_name,
        reasoning_level=reasoning_level,
        reasoning_type=reasoning_type,
        step_prefix=step_prefix,
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
    )

    try:
        source = fetch_source()
        request_telemetry.emit(
            step_suffix=source_fetched_step_suffix,
            validation_status="passed",
            retry_count=0,
        )
        prepared_extraction = prepare_extraction(source, reasoning_level)
        extraction_result = execute_structured_extraction(
            spec=extraction_spec,
            prepared=prepared_extraction,
            trace_id=trace_id,
        )
    except SessionNotFoundError:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="session_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="session_not_found",
            message="Unable to find the requested session.",
            trace_id=trace_id,
        )
    except sqlite3.Error:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason=source_query_failure_code,
        )
        return _build_error_response(
            status_code=500,
            code=source_query_failure_code,
            message=source_query_failure_message,
            trace_id=trace_id,
        )
    except StructuredExtractionError as exc:
        request_telemetry.emit(
            step_suffix="request_failed",
            provider_name=exc.provider_name,
            model_name=exc.model_name,
            validation_status="failed",
            retry_count=exc.retry_count,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason=exc.code,
        )
        return _build_error_response(
            status_code=500,
            code=exc.code,
            message=exc.message,
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="request_completed",
        provider_name=extraction_result.provider_name,
        model_name=extraction_result.model_name,
        validation_status="passed",
        retry_count=extraction_result.retry_count,
        elapsed_ms=_elapsed_ms(start_time),
    )
    return extraction_result.response


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
    return _run_session_structured_extraction_endpoint(
        session_id=session_id,
        trace_id=trace_id,
        reasoning_level=extraction_request.reasoning_level,
        tool_name=DEFAULT_CONCEPT_TOOL_NAME,
        reasoning_type=DEFAULT_CONCEPT_REASONING_TYPE,
        step_prefix=DEFAULT_CONCEPT_STEP_PREFIX,
        source_fetched_step_suffix="session_fetched",
        source_query_failure_code="session_extraction_source_query_failed",
        source_query_failure_message=(
            "Unable to fetch the session data required for concept extraction."
        ),
        fetch_source=lambda: get_session_extraction_source(
            database_path=get_database_path(),
            session_id=session_id,
            trace_id=trace_id,
        ),
        prepare_extraction=lambda session_source, reasoning_level: prepare_concept_extraction(
            session_source=session_source,
            reasoning_level=reasoning_level,
        ),
        extraction_spec=CONCEPT_EXTRACTION_SPEC,
    )


@app.post(
    "/sessions/{session_id}/extract-assignment-requirements",
    response_model=ExtractAssignmentRequirementsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def extract_session_assignment_requirements(
    session_id: str,
    request: Annotated[ExtractAssignmentRequirementsRequest | None, Body()] = None,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> ExtractAssignmentRequirementsResponse | JSONResponse:
    """Extract assignment requirements for a session from stored assignment evidence."""
    trace_id = x_trace_id or uuid4().hex
    extraction_request = request or ExtractAssignmentRequirementsRequest()
    return _run_session_structured_extraction_endpoint(
        session_id=session_id,
        trace_id=trace_id,
        reasoning_level=extraction_request.reasoning_level,
        tool_name=DEFAULT_ASSIGNMENT_TOOL_NAME,
        reasoning_type=DEFAULT_ASSIGNMENT_REASONING_TYPE,
        step_prefix=DEFAULT_ASSIGNMENT_STEP_PREFIX,
        source_fetched_step_suffix="assignment_sources_fetched",
        source_query_failure_code="assignment_requirement_extraction_source_query_failed",
        source_query_failure_message=(
            "Unable to fetch the assignment data required for requirement extraction."
        ),
        fetch_source=lambda: list_session_assignment_requirement_sources(
            database_path=get_database_path(),
            session_id=session_id,
            trace_id=trace_id,
        ),
        prepare_extraction=lambda assignment_sources, reasoning_level: (
            prepare_assignment_requirement_extraction(
                session_id=session_id,
                assignment_sources=assignment_sources,
                reasoning_level=reasoning_level,
            )
        ),
        extraction_spec=ASSIGNMENT_REQUIREMENT_EXTRACTION_SPEC,
    )


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
        _emit_request_failed_event(
            trace_id=trace_id,
            step_name="get_all_sessions.request_failed",
            tool_name=None,
            start_time=start_time,
            failure_reason="session_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="session_query_failed",
            message="Unable to fetch session summaries.",
            trace_id=trace_id,
        )

    elapsed_ms = _elapsed_ms(start_time)
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
        _emit_request_failed_event(
            trace_id=trace_id,
            step_name="get_session_submissions.request_failed",
            tool_name=None,
            start_time=start_time,
            failure_reason="session_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="session_not_found",
            message="Unable to find the requested session.",
            trace_id=trace_id,
        )
    except sqlite3.Error:
        _emit_request_failed_event(
            trace_id=trace_id,
            step_name="get_session_submissions.request_failed",
            tool_name=None,
            start_time=start_time,
            failure_reason="session_submission_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="session_submission_query_failed",
            message="Unable to fetch session submissions.",
            trace_id=trace_id,
        )

    elapsed_ms = _elapsed_ms(start_time)
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
        _emit_request_failed_event(
            trace_id=trace_id,
            step_name="get_student_submissions.request_failed",
            tool_name=None,
            start_time=start_time,
            failure_reason="student_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="student_not_found",
            message="Unable to find the requested student.",
            trace_id=trace_id,
        )
    except sqlite3.Error:
        _emit_request_failed_event(
            trace_id=trace_id,
            step_name="get_student_submissions.request_failed",
            tool_name=None,
            start_time=start_time,
            failure_reason="student_submission_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="student_submission_query_failed",
            message="Unable to fetch student submissions.",
            trace_id=trace_id,
        )

    elapsed_ms = _elapsed_ms(start_time)
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
