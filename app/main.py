"""HTTP entrypoints for the ReviewPilot API."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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
from app.assignment_requirement_store import (
    StoredAssignmentRequirementNotFoundError,
    save_assignment_requirement_requirements_json,
    save_session_assignment_requirements_document,
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
from app.concept_grading_spec import (
    CONCEPT_GRADING_SPEC,
    prepare_concept_grading,
)
from app.concept_grading_spec import (
    DEFAULT_REASONING_TYPE as DEFAULT_CONCEPT_GRADING_REASONING_TYPE,
)
from app.concept_grading_spec import (
    DEFAULT_STEP_PREFIX as DEFAULT_CONCEPT_GRADING_STEP_PREFIX,
)
from app.concept_grading_spec import (
    DEFAULT_TOOL_NAME as DEFAULT_CONCEPT_GRADING_TOOL_NAME,
)
from app.config import get_database_path
from app.logging_config import configure_logging
from app.project_evidence import (
    ProjectEvidenceCollectionError,
    collect_project_evidence,
)
from app.schemas import (
    ApiError,
    ApiErrorResponse,
    ConceptGradingSource,
    ExtractAssignmentRequirementsRequest,
    ExtractAssignmentRequirementsResponse,
    ExtractConceptsRequest,
    ExtractConceptsResponse,
    GradeConceptsRequest,
    GradeConceptsResponse,
    SessionAssignmentRequirementsResponse,
    SessionConceptsResponse,
    SessionSubmission,
    SessionSummary,
    StudentSubmission,
    UpdateSessionAssignmentRequirementsRequest,
    UpdateSessionConceptsRequest,
)
from app.session_content_store import save_session_concepts_json
from app.session_store import (
    AmbiguousStudentSubmissionError,
    SessionNotFoundError,
    StudentNotFoundError,
    StudentSubmissionNotFoundError,
    get_concept_grading_context,
    get_session_assignment_requirements,
    get_session_concepts,
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
from app.student_grade_store import save_student_concept_scores
from app.telemetry import WorkflowTelemetryEmitter, emit_event
from app.ui_routes import get_ui_static_directory, ui_router

configure_logging()

app = FastAPI(title="ReviewPilot", version="0.1.0")
app.mount("/static", StaticFiles(directory=get_ui_static_directory()), name="static")
app.include_router(ui_router)


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
    reasoning_level: str | None,
    reasoning_type: str | None,
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
    persist_response: Callable[[ResponseModelT], None] | None = None,
    persisted_step_suffix: str | None = None,
    persistence_failure_code: str | None = None,
    persistence_failure_message: str | None = None,
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

    if persist_response is not None:
        try:
            persist_response(extraction_result.response)
        except SessionNotFoundError:
            request_telemetry.emit(
                step_suffix="request_failed",
                provider_name=extraction_result.provider_name,
                model_name=extraction_result.model_name,
                validation_status="failed",
                retry_count=extraction_result.retry_count,
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
                provider_name=extraction_result.provider_name,
                model_name=extraction_result.model_name,
                validation_status="failed",
                retry_count=extraction_result.retry_count,
                elapsed_ms=_elapsed_ms(start_time),
                failure_reason=persistence_failure_code,
            )
            return _build_error_response(
                status_code=500,
                code=persistence_failure_code or source_query_failure_code,
                message=persistence_failure_message or source_query_failure_message,
                trace_id=trace_id,
            )

        if persisted_step_suffix is not None:
            request_telemetry.emit(
                step_suffix=persisted_step_suffix,
                provider_name=extraction_result.provider_name,
                model_name=extraction_result.model_name,
                validation_status="passed",
                retry_count=extraction_result.retry_count,
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
    """Extract gradeable concepts and persist them to the session content row."""
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
        persist_response=lambda response: save_session_concepts_json(
            database_path=get_database_path(),
            session_id=session_id,
            concepts=response.concepts,
            trace_id=trace_id,
        ),
        persisted_step_suffix="concepts_persisted",
        persistence_failure_code="session_concepts_persistence_failed",
        persistence_failure_message="Unable to save extracted concepts for the session.",
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
    """Extract assignment requirements and persist them to assignment_requirement rows."""
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
        persist_response=lambda response: save_assignment_requirement_requirements_json(
            database_path=get_database_path(),
            session_id=session_id,
            assignment_requirements=response.assignment_requirements,
            trace_id=trace_id,
        ),
        persisted_step_suffix="assignment_requirements_persisted",
        persistence_failure_code="assignment_requirements_persistence_failed",
        persistence_failure_message="Unable to save extracted assignment requirements.",
    )


@app.get(
    "/sessions/{session_id}/concepts",
    response_model=SessionConceptsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def get_stored_session_concepts(
    session_id: str,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> SessionConceptsResponse | JSONResponse:
    """Return the stored concepts document for one session."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=session_id,
        tool_name="get_session_concepts",
        reasoning_level=None,
        reasoning_type=None,
        step_prefix="get_session_concepts",
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
    )

    try:
        concepts_document = get_session_concepts(
            database_path=get_database_path(),
            session_id=session_id,
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
    except (sqlite3.Error, ValueError):
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="session_concepts_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="session_concepts_query_failed",
            message="Unable to fetch the stored concepts for the session.",
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="session_concepts_fetched",
        validation_status="passed",
        retry_count=0,
        details={"concept_count": len(concepts_document.concepts)},
    )
    request_telemetry.emit(
        step_suffix="request_completed",
        validation_status="passed",
        retry_count=0,
        elapsed_ms=_elapsed_ms(start_time),
    )
    return concepts_document


@app.put(
    "/sessions/{session_id}/concepts",
    response_model=SessionConceptsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def update_stored_session_concepts(
    session_id: str,
    request: Annotated[UpdateSessionConceptsRequest, Body()],
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> SessionConceptsResponse | JSONResponse:
    """Replace the stored concepts document for one session."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=session_id,
        tool_name="update_session_concepts",
        reasoning_level=None,
        reasoning_type=None,
        step_prefix="update_session_concepts",
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
        details={"concept_count": len(request.concepts)},
    )

    try:
        save_session_concepts_json(
            database_path=get_database_path(),
            session_id=session_id,
            concepts=request.concepts,
            trace_id=trace_id,
        )
        concepts_document = get_session_concepts(
            database_path=get_database_path(),
            session_id=session_id,
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
    except (sqlite3.Error, ValueError):
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="session_concepts_persistence_failed",
        )
        return _build_error_response(
            status_code=500,
            code="session_concepts_persistence_failed",
            message="Unable to save the stored concepts for the session.",
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="session_concepts_persisted",
        validation_status="passed",
        retry_count=0,
        details={"concept_count": len(concepts_document.concepts)},
    )
    request_telemetry.emit(
        step_suffix="request_completed",
        validation_status="passed",
        retry_count=0,
        elapsed_ms=_elapsed_ms(start_time),
    )
    return concepts_document


@app.get(
    "/sessions/{session_id}/assignment-requirements",
    response_model=SessionAssignmentRequirementsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def get_stored_session_assignment_requirements(
    session_id: str,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> SessionAssignmentRequirementsResponse | JSONResponse:
    """Return the stored assignment requirements document for one session."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=session_id,
        tool_name="get_session_assignment_requirements",
        reasoning_level=None,
        reasoning_type=None,
        step_prefix="get_session_assignment_requirements",
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
    )

    try:
        assignment_requirements_document = get_session_assignment_requirements(
            database_path=get_database_path(),
            session_id=session_id,
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
    except (sqlite3.Error, ValueError):
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="assignment_requirements_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="assignment_requirements_query_failed",
            message="Unable to fetch the stored assignment requirements for the session.",
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="assignment_requirements_fetched",
        validation_status="passed",
        retry_count=0,
        details={
            "assignment_requirement_count": len(
                assignment_requirements_document.assignment_requirements
            )
        },
    )
    request_telemetry.emit(
        step_suffix="request_completed",
        validation_status="passed",
        retry_count=0,
        elapsed_ms=_elapsed_ms(start_time),
    )
    return assignment_requirements_document


@app.put(
    "/sessions/{session_id}/assignment-requirements",
    response_model=SessionAssignmentRequirementsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["sessions"],
)
def update_stored_session_assignment_requirements(
    session_id: str,
    request: Annotated[UpdateSessionAssignmentRequirementsRequest, Body()],
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> SessionAssignmentRequirementsResponse | JSONResponse:
    """Replace the stored assignment requirements document for one session."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=session_id,
        tool_name="update_session_assignment_requirements",
        reasoning_level=None,
        reasoning_type=None,
        step_prefix="update_session_assignment_requirements",
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
        details={
            "assignment_requirement_count": len(request.assignment_requirements),
        },
    )

    try:
        save_session_assignment_requirements_document(
            database_path=get_database_path(),
            session_id=session_id,
            assignment_requirements=request.assignment_requirements,
            trace_id=trace_id,
        )
        assignment_requirements_document = get_session_assignment_requirements(
            database_path=get_database_path(),
            session_id=session_id,
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
    except StoredAssignmentRequirementNotFoundError:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="assignment_requirement_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="assignment_requirement_not_found",
            message="Unable to find one or more assignment requirements for the session.",
            trace_id=trace_id,
        )
    except (sqlite3.Error, ValueError):
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="assignment_requirements_persistence_failed",
        )
        return _build_error_response(
            status_code=500,
            code="assignment_requirements_persistence_failed",
            message="Unable to save the stored assignment requirements for the session.",
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="assignment_requirements_persisted",
        validation_status="passed",
        retry_count=0,
        details={
            "assignment_requirement_count": len(
                assignment_requirements_document.assignment_requirements
            )
        },
    )
    request_telemetry.emit(
        step_suffix="request_completed",
        validation_status="passed",
        retry_count=0,
        elapsed_ms=_elapsed_ms(start_time),
    )
    return assignment_requirements_document


@app.post(
    "/grade/concepts",
    response_model=GradeConceptsResponse,
    responses={404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
    tags=["grading"],
)
def grade_submission_concepts(
    request: Annotated[GradeConceptsRequest, Body()],
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> GradeConceptsResponse | JSONResponse:
    """Grade a student's project against requested concepts using collected project evidence."""
    trace_id = x_trace_id or uuid4().hex
    start_time = perf_counter()
    request_telemetry = _build_request_telemetry(
        trace_id=trace_id,
        session_id=request.session_id,
        tool_name=DEFAULT_CONCEPT_GRADING_TOOL_NAME,
        reasoning_level=request.reasoning_level,
        reasoning_type=DEFAULT_CONCEPT_GRADING_REASONING_TYPE,
        step_prefix=DEFAULT_CONCEPT_GRADING_STEP_PREFIX,
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
    )

    try:
        grading_context = get_concept_grading_context(
            database_path=get_database_path(),
            student_id=request.student_id,
            session_id=request.session_id,
            source_type=request.source_type,
            repo_url=request.repo_url,
            local_path=request.local_path,
            zip_path=request.zip_path,
            trace_id=trace_id,
        )
        request_telemetry.emit(
            step_suffix="grading_context_fetched",
            validation_status="passed",
            retry_count=0,
        )
        request_telemetry.emit(
            step_suffix="project_evidence_collection_started",
            validation_status="pending",
            retry_count=0,
        )
        project_evidence = collect_project_evidence(
            source_type=request.source_type,
            repo_url=request.repo_url,
            local_path=request.local_path,
            zip_path=request.zip_path,
        )
        request_telemetry.emit(
            step_suffix="project_evidence_collected",
            validation_status="passed",
            retry_count=0,
            details={
                "project_file_count": len(project_evidence.file_inventory),
                "documentation_snippet_count": len(project_evidence.documentation_snippets),
                "implementation_snippet_count": len(project_evidence.implementation_snippets),
                "test_snippet_count": len(project_evidence.test_snippets),
            },
        )
        grading_source = ConceptGradingSource(
            **grading_context.model_dump(),
            concepts=request.concepts,
            project_evidence=project_evidence,
        )
        prepared_extraction = prepare_concept_grading(
            grading_source=grading_source,
            reasoning_level=request.reasoning_level,
        )
        extraction_result = execute_structured_extraction(
            spec=CONCEPT_GRADING_SPEC,
            prepared=prepared_extraction,
            trace_id=trace_id,
        )
    except StudentNotFoundError:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="student_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="student_not_found",
            message="Unable to find the requested student.",
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
    except StudentSubmissionNotFoundError:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="student_submission_not_found",
        )
        return _build_error_response(
            status_code=404,
            code="student_submission_not_found",
            message="Unable to find the student's submission for the requested session.",
            trace_id=trace_id,
        )
    except AmbiguousStudentSubmissionError:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="student_submission_ambiguous",
        )
        return _build_error_response(
            status_code=500,
            code="student_submission_ambiguous",
            message="Unable to resolve a unique student submission for the requested session.",
            trace_id=trace_id,
        )
    except sqlite3.Error:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="concept_grading_context_query_failed",
        )
        return _build_error_response(
            status_code=500,
            code="concept_grading_context_query_failed",
            message="Unable to fetch the student and session data required for concept grading.",
            trace_id=trace_id,
        )
    except ProjectEvidenceCollectionError as exc:
        request_telemetry.emit(
            step_suffix="request_failed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason=exc.code,
        )
        return _build_error_response(
            status_code=500,
            code=exc.code,
            message=exc.message,
            trace_id=trace_id,
        )
    except StructuredExtractionError as exc:
        response_code = exc.code
        response_message = exc.message
        if exc.code in {"structured_extraction_failed", "no_provider_available"}:
            response_code = "concept_grading_provider_failed"
            response_message = (
                "Unable to grade the requested concepts with the configured providers."
            )
        request_telemetry.emit(
            step_suffix="request_failed",
            provider_name=exc.provider_name,
            model_name=exc.model_name,
            validation_status="failed",
            retry_count=exc.retry_count,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason=response_code,
        )
        return _build_error_response(
            status_code=500,
            code=response_code,
            message=response_message,
            trace_id=trace_id,
        )

    try:
        save_student_concept_scores(
            database_path=get_database_path(),
            session_id=grading_context.session_id,
            submission_id=grading_context.submission_id,
            concept_scores=extraction_result.response.concept_scores,
            trace_id=trace_id,
        )
    except sqlite3.Error:
        request_telemetry.emit(
            step_suffix="request_failed",
            provider_name=extraction_result.provider_name,
            model_name=extraction_result.model_name,
            validation_status="failed",
            retry_count=extraction_result.retry_count,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="concept_grading_persistence_failed",
        )
        return _build_error_response(
            status_code=500,
            code="concept_grading_persistence_failed",
            message="Unable to save concept grading for the student submission.",
            trace_id=trace_id,
        )

    request_telemetry.emit(
        step_suffix="concept_scores_persisted",
        provider_name=extraction_result.provider_name,
        model_name=extraction_result.model_name,
        validation_status="passed",
        retry_count=extraction_result.retry_count,
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
