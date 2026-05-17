"""Reusable extraction and grading workflows shared by API endpoints and the orchestrator."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from time import perf_counter

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
from app.assignment_requirement_grading_spec import (
    ASSIGNMENT_REQUIREMENT_GRADING_SPEC,
    prepare_assignment_requirement_grading,
)
from app.assignment_requirement_grading_spec import (
    DEFAULT_REASONING_TYPE as DEFAULT_ASSIGNMENT_GRADING_REASONING_TYPE,
)
from app.assignment_requirement_grading_spec import (
    DEFAULT_STEP_PREFIX as DEFAULT_ASSIGNMENT_GRADING_STEP_PREFIX,
)
from app.assignment_requirement_grading_spec import (
    DEFAULT_TOOL_NAME as DEFAULT_ASSIGNMENT_GRADING_TOOL_NAME,
)
from app.assignment_requirement_store import save_assignment_requirement_requirements_json
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
from app.project_evidence import collect_project_evidence
from app.schemas import (
    AssignmentRequirementGradingSource,
    ConceptGradingSource,
    ExtractAssignmentRequirementsResponse,
    ExtractConceptsResponse,
    GradeAssignmentRequirementsRequest,
    GradeAssignmentRequirementsResponse,
    GradeConceptsRequest,
    GradeConceptsResponse,
    ReasoningLevel,
)
from app.session_content_store import save_session_concepts_json
from app.session_store import (
    get_assignment_requirement_grading_context,
    get_concept_grading_context,
    get_session_extraction_source,
    list_session_assignment_requirement_sources,
)
from app.structured_extraction import (
    PreparedStructuredExtraction,
    StructuredExtractionSpec,
    execute_structured_extraction,
)
from app.student_grade_store import (
    save_student_assignment_requirement_scores,
    save_student_concept_scores,
)
from app.telemetry import WorkflowTelemetryEmitter


def _elapsed_ms(start_time: float) -> float:
    """Return elapsed wall-clock time in milliseconds for workflow telemetry."""
    return round((perf_counter() - start_time) * 1000, 3)


def _build_workflow_telemetry(
    *,
    trace_id: str,
    session_id: str,
    tool_name: str,
    reasoning_level: str | None,
    reasoning_type: str | None,
    step_prefix: str,
) -> WorkflowTelemetryEmitter:
    """Build a workflow-scoped telemetry emitter shared by reusable workflow helpers."""
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


def run_concept_extraction_workflow(
    *,
    database_path: Path,
    session_id: str,
    reasoning_level: ReasoningLevel,
    trace_id: str,
) -> ExtractConceptsResponse:
    """Extract and persist gradeable concepts for one session."""
    return _run_session_structured_extraction_workflow(
        session_id=session_id,
        trace_id=trace_id,
        reasoning_level=reasoning_level,
        tool_name=DEFAULT_CONCEPT_TOOL_NAME,
        reasoning_type=DEFAULT_CONCEPT_REASONING_TYPE,
        step_prefix=DEFAULT_CONCEPT_STEP_PREFIX,
        fetch_source=lambda: get_session_extraction_source(
            database_path=database_path,
            session_id=session_id,
            trace_id=trace_id,
        ),
        prepare_extraction=lambda session_source, selected_reasoning_level: (
            prepare_concept_extraction(
                session_source=session_source,
                reasoning_level=selected_reasoning_level,
            )
        ),
        extraction_spec=CONCEPT_EXTRACTION_SPEC,
        persist_response=lambda response: save_session_concepts_json(
            database_path=database_path,
            session_id=session_id,
            concepts=response.concepts,
            trace_id=trace_id,
        ),
        source_fetched_step_suffix="session_fetched",
        persisted_step_suffix="concepts_persisted",
    )


def run_assignment_requirement_extraction_workflow(
    *,
    database_path: Path,
    session_id: str,
    reasoning_level: ReasoningLevel,
    trace_id: str,
) -> ExtractAssignmentRequirementsResponse:
    """Extract and persist assignment requirements for one session."""
    return _run_session_structured_extraction_workflow(
        session_id=session_id,
        trace_id=trace_id,
        reasoning_level=reasoning_level,
        tool_name=DEFAULT_ASSIGNMENT_TOOL_NAME,
        reasoning_type=DEFAULT_ASSIGNMENT_REASONING_TYPE,
        step_prefix=DEFAULT_ASSIGNMENT_STEP_PREFIX,
        fetch_source=lambda: list_session_assignment_requirement_sources(
            database_path=database_path,
            session_id=session_id,
            trace_id=trace_id,
        ),
        prepare_extraction=lambda assignment_sources, selected_reasoning_level: (
            prepare_assignment_requirement_extraction(
                session_id=session_id,
                assignment_sources=assignment_sources,
                reasoning_level=selected_reasoning_level,
            )
        ),
        extraction_spec=ASSIGNMENT_REQUIREMENT_EXTRACTION_SPEC,
        persist_response=lambda response: save_assignment_requirement_requirements_json(
            database_path=database_path,
            session_id=session_id,
            assignment_requirements=response.assignment_requirements,
            trace_id=trace_id,
        ),
        source_fetched_step_suffix="assignment_sources_fetched",
        persisted_step_suffix="assignment_requirements_persisted",
    )


def _run_session_structured_extraction_workflow[
    SourceT,
    OutputModelT: BaseModel,
    ResponseModelT,
](
    *,
    session_id: str,
    trace_id: str,
    reasoning_level: ReasoningLevel,
    tool_name: str,
    reasoning_type: str,
    step_prefix: str,
    fetch_source: Callable[[], SourceT],
    prepare_extraction: Callable[
        [SourceT, ReasoningLevel], PreparedStructuredExtraction[OutputModelT, ResponseModelT]
    ],
    extraction_spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
    persist_response: Callable[[ResponseModelT], None],
    source_fetched_step_suffix: str,
    persisted_step_suffix: str,
) -> ResponseModelT:
    """Run one reusable session-scoped extraction workflow with shared telemetry."""
    start_time = perf_counter()
    request_telemetry = _build_workflow_telemetry(
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
    persist_response(extraction_result.response)
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


def run_concept_grading_workflow(
    *,
    database_path: Path,
    request: GradeConceptsRequest,
    trace_id: str,
) -> GradeConceptsResponse:
    """Grade one submission against requested concepts and persist the result."""
    start_time = perf_counter()
    request_telemetry = _build_workflow_telemetry(
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

    grading_context = get_concept_grading_context(
        database_path=database_path,
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
    prepared_extraction = prepare_concept_grading(
        grading_source=ConceptGradingSource(
            **grading_context.model_dump(),
            concepts=request.concepts,
            project_evidence=project_evidence,
        ),
        reasoning_level=request.reasoning_level,
    )
    extraction_result = execute_structured_extraction(
        spec=CONCEPT_GRADING_SPEC,
        prepared=prepared_extraction,
        trace_id=trace_id,
    )
    save_student_concept_scores(
        database_path=database_path,
        session_id=grading_context.session_id,
        submission_id=grading_context.submission_id,
        concept_scores=extraction_result.response.concept_scores,
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


def run_assignment_requirement_grading_workflow(
    *,
    database_path: Path,
    request: GradeAssignmentRequirementsRequest,
    trace_id: str,
) -> GradeAssignmentRequirementsResponse:
    """Grade one submission against requested assignment requirements and persist it."""
    start_time = perf_counter()
    request_telemetry = _build_workflow_telemetry(
        trace_id=trace_id,
        session_id=request.session_id,
        tool_name=DEFAULT_ASSIGNMENT_GRADING_TOOL_NAME,
        reasoning_level=request.reasoning_level,
        reasoning_type=DEFAULT_ASSIGNMENT_GRADING_REASONING_TYPE,
        step_prefix=DEFAULT_ASSIGNMENT_GRADING_STEP_PREFIX,
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
    )

    grading_context = get_assignment_requirement_grading_context(
        database_path=database_path,
        student_id=request.student_id,
        session_id=request.session_id,
        assignment_requirement_id=request.assignment_requirement_id,
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
    grading_source = AssignmentRequirementGradingSource(
        **grading_context.model_dump(),
        requirements=request.requirements,
        project_evidence=project_evidence,
    )
    prepared_extraction = prepare_assignment_requirement_grading(
        grading_source=grading_source,
        reasoning_level=request.reasoning_level,
    )
    extraction_result = execute_structured_extraction(
        spec=ASSIGNMENT_REQUIREMENT_GRADING_SPEC,
        prepared=prepared_extraction,
        trace_id=trace_id,
    )
    save_student_assignment_requirement_scores(
        database_path=database_path,
        session_id=grading_context.session_id,
        submission_id=grading_context.submission_id,
        assignment_requirement_scores=(
            extraction_result.response.assignment_requirement_scores
        ),
        trace_id=trace_id,
    )
    request_telemetry.emit(
        step_suffix="assignment_requirement_scores_persisted",
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
