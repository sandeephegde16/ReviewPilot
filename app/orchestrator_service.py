"""Conversation-loop orchestrator engine built on top of coarse ReviewPilot workflows."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from app.orchestrator_spec import (
    DEFAULT_REASONING_TYPE as DEFAULT_ORCHESTRATOR_REASONING_TYPE,
)
from app.orchestrator_spec import (
    DEFAULT_STEP_PREFIX as DEFAULT_ORCHESTRATOR_STEP_PREFIX,
)
from app.orchestrator_spec import (
    DEFAULT_TOOL_NAME as DEFAULT_ORCHESTRATOR_TOOL_NAME,
)
from app.orchestrator_spec import (
    ORCHESTRATOR_PLANNER_SPEC,
    OrchestratorPlannerPromptContext,
    prepare_orchestrator_planner_turn,
)
from app.project_evidence import ProjectEvidenceCollectionError
from app.review_workflows import (
    run_assignment_requirement_extraction_workflow,
    run_assignment_requirement_grading_workflow,
    run_concept_extraction_workflow,
    run_concept_grading_workflow,
)
from app.schemas import (
    ApiWarning,
    AssignmentRequirementGradingCriterion,
    AssignmentRequirementScoreResult,
    ExtractAssignmentRequirementsResponse,
    ExtractConceptsResponse,
    GradeAssignmentRequirementsRequest,
    GradeAssignmentRequirementsResponse,
    GradeConceptsRequest,
    GradeConceptsResponse,
    OrchestratorPlannerContextUpdate,
    OrchestratorPlannerError,
    OrchestratorPlannerReasoningType,
    OrchestratorPlannerTurnOutput,
    OrchestratorPlannerTurnRecord,
    OrchestratorToolExecutionResult,
    OrchestratorToolName,
    ReviewOrchestratorExecutionResult,
    RunReviewOrchestratorRequest,
    RunReviewOrchestratorResponse,
    SessionAssignmentRequirementsResponse,
    SessionConceptsResponse,
    SessionSubmission,
    StoredAssignmentRequirementResult,
)
from app.session_store import (
    AmbiguousStudentSubmissionError,
    AssignmentRequirementNotFoundError,
    SessionNotFoundError,
    StudentNotFoundError,
    StudentSubmissionNotFoundError,
    get_session_assignment_requirements,
    get_session_concepts,
    get_session_extraction_source,
    list_session_submissions,
)
from app.structured_extraction import StructuredExtractionError, execute_structured_extraction
from app.telemetry import WorkflowTelemetryEmitter
from app.transcript_parser import normalize_transcript_text

MAX_CONSECUTIVE_CONTEXT_UPDATES = 2
AVAILABLE_ORCHESTRATOR_TOOLS: list[OrchestratorToolName] = [
    "extract_concepts",
    "extract_assignment_requirements",
    "grade_concepts",
    "grade_assignment_requirements",
]


class OrchestratorToolExecutionFailure(Exception):
    """Raised when a coarse orchestrator tool cannot make progress safely."""

    def __init__(self, *, code: str, message: str) -> None:
        """Store a stable failure code and human-readable message."""
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class OrchestratorState:
    """Mutable state carried across planner turns in the orchestrator loop."""

    request: RunReviewOrchestratorRequest
    session_title: str
    session_topic: str
    transcript_available: bool
    session_concepts_document: SessionConceptsResponse
    assignment_requirements_document: SessionAssignmentRequirementsResponse
    extract_concepts_response: ExtractConceptsResponse | None = None
    extract_assignment_requirements_response: ExtractAssignmentRequirementsResponse | None = None
    grade_concepts_response: GradeConceptsResponse | None = None
    grade_assignment_requirements_response: GradeAssignmentRequirementsResponse | None = None
    planner_turns: list[OrchestratorPlannerTurnRecord] = field(default_factory=list)
    tool_results: list[OrchestratorToolExecutionResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recent_errors: list[str] = field(default_factory=list)
    concept_extraction_completed: bool = False
    assignment_requirement_extraction_completed: bool = False
    concept_grading_completed: bool = False
    assignment_requirement_grading_completed: bool = False
    state_version: int = 0
    last_tool_state_version: dict[OrchestratorToolName, int] = field(default_factory=dict)


def run_review_orchestrator(
    *,
    database_path: Path,
    request: RunReviewOrchestratorRequest,
    trace_id: str,
) -> RunReviewOrchestratorResponse:
    """Run the conversation-loop orchestrator until it reaches a final or failed turn."""
    start_time = perf_counter()
    request_telemetry = _build_orchestrator_telemetry(
        trace_id=trace_id,
        session_id=request.session_id,
        reasoning_level=request.reasoning_level,
    )
    request_telemetry.emit(
        step_suffix="request_received",
        validation_status="pending",
        retry_count=0,
        details={"requested_operation": request.operation},
    )
    state = _load_initial_state(
        database_path=database_path,
        request=request,
        trace_id=trace_id,
    )
    request_telemetry.emit(
        step_suffix="initial_state_loaded",
        validation_status="passed",
        retry_count=0,
        details=_build_state_snapshot(state),
    )

    if request.operation == "grade_rubrics":
        request_telemetry.emit(
            step_suffix="request_completed",
            validation_status="failed",
            retry_count=0,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason="rubric_grading_not_implemented",
        )
        return _build_failed_run_response(
            trace_id=trace_id,
            request=request,
            state=state,
            reasoning_type="failure_handling",
            reasoning_summary="Rubric grading is not implemented in the orchestrator yet.",
            error=OrchestratorPlannerError(
                error_code="rubric_grading_not_implemented",
                message="Rubric grading is not implemented in the orchestrator yet.",
            ),
        )

    consecutive_context_updates = 0
    for turn_number in range(1, request.max_turns + 1):
        request_telemetry.emit(
            step_suffix="planner_turn_started",
            validation_status="pending",
            retry_count=0,
            details={
                "turn_number": turn_number,
                "max_steps_remaining": request.max_turns - turn_number + 1,
            },
        )
        prepared = prepare_orchestrator_planner_turn(
            prompt_context=_build_planner_prompt_context(
                state=state,
                trace_id=trace_id,
                turn_number=turn_number,
                max_steps_remaining=request.max_turns - turn_number + 1,
            ),
            reasoning_level=request.reasoning_level,
        )
        planner_result = execute_structured_extraction(
            spec=ORCHESTRATOR_PLANNER_SPEC,
            prepared=prepared,
            trace_id=trace_id,
        )
        planner_turn = planner_result.response
        state.warnings.extend(planner_turn.warnings)
        state.planner_turns.append(
            OrchestratorPlannerTurnRecord(
                turn_number=turn_number,
                response_type=planner_turn.response_type,
                reasoning_type=planner_turn.reasoning_type,
                reasoning_summary=planner_turn.reasoning_summary,
                checks=planner_turn.checks,
                tool_calls=planner_turn.tool_calls,
                context_update=planner_turn.context_update,
                warnings=planner_turn.warnings,
                error=planner_turn.error,
            )
        )
        request_telemetry.emit(
            step_suffix="planner_turn_completed",
            provider_name=planner_result.provider_name,
            model_name=planner_result.model_name,
            validation_status="passed",
            retry_count=planner_result.retry_count,
            details={
                "turn_number": turn_number,
                "response_type": planner_turn.response_type,
                "reasoning_type": planner_turn.reasoning_type,
            },
        )

        if planner_turn.response_type == "TOOL_REQUEST":
            consecutive_context_updates = 0
            _execute_planner_tool_calls(
                database_path=database_path,
                state=state,
                planner_turn=planner_turn,
                trace_id=trace_id,
                request_telemetry=request_telemetry,
            )
            continue

        if planner_turn.response_type == "CONTEXT_UPDATE":
            consecutive_context_updates += 1
            _apply_context_update(
                state=state,
                context_update=planner_turn.context_update,
            )
            request_telemetry.emit(
                step_suffix="context_update_applied",
                provider_name=planner_result.provider_name,
                model_name=planner_result.model_name,
                validation_status="passed",
                retry_count=planner_result.retry_count,
                details={
                    "turn_number": turn_number,
                    "next_goal": (
                        planner_turn.context_update.next_goal
                        if planner_turn.context_update is not None
                        else None
                    ),
                },
            )
            if consecutive_context_updates > MAX_CONSECUTIVE_CONTEXT_UPDATES:
                return _build_failed_run_response(
                    trace_id=trace_id,
                    request=request,
                    state=state,
                    reasoning_type="failure_handling",
                    reasoning_summary=(
                        "Planner returned too many context updates without requesting "
                        "tools or finalizing."
                    ),
                    error=OrchestratorPlannerError(
                        error_code="planner_stalled",
                        message=(
                            "Planner stalled without making progress after repeated "
                            "context updates."
                        ),
                    ),
                )
            continue

        if planner_turn.response_type == "FINAL_REVIEW":
            if _can_finalize(state=state, requested_operation=request.operation):
                request_telemetry.emit(
                    step_suffix="request_completed",
                    provider_name=planner_result.provider_name,
                    model_name=planner_result.model_name,
                    validation_status="passed",
                    retry_count=planner_result.retry_count,
                    elapsed_ms=_elapsed_ms(start_time),
                )
                return RunReviewOrchestratorResponse(
                    trace_id=trace_id,
                    requested_operation=request.operation,
                    status=planner_turn.final_review.status,
                    reasoning_type=planner_turn.reasoning_type,
                    reasoning_summary=planner_turn.final_review.summary,
                    planner_turns=state.planner_turns,
                    tool_results=state.tool_results,
                    result=_build_execution_result(state),
                    warnings=_deduplicate_preserving_order(state.warnings),
                    error=planner_turn.error,
                )
            state.recent_errors.append(
                "Planner attempted to finalize before the completion condition was met."
            )
            request_telemetry.emit(
                step_suffix="finalization_blocked",
                provider_name=planner_result.provider_name,
                model_name=planner_result.model_name,
                validation_status="failed",
                retry_count=planner_result.retry_count,
                failure_reason="completion_condition_not_met",
                details={"turn_number": turn_number},
            )
            continue

        request_telemetry.emit(
            step_suffix="request_completed",
            provider_name=planner_result.provider_name,
            model_name=planner_result.model_name,
            validation_status="failed",
            retry_count=planner_result.retry_count,
            elapsed_ms=_elapsed_ms(start_time),
            failure_reason=planner_turn.error.error_code,
        )
        return _build_failed_run_response(
            trace_id=trace_id,
            request=request,
            state=state,
            reasoning_type=planner_turn.reasoning_type,
            reasoning_summary=planner_turn.reasoning_summary,
            error=planner_turn.error,
        )

    request_telemetry.emit(
        step_suffix="request_completed",
        validation_status="failed",
        retry_count=0,
        elapsed_ms=_elapsed_ms(start_time),
        failure_reason="planner_max_turns_exceeded",
    )
    return _build_failed_run_response(
        trace_id=trace_id,
        request=request,
        state=state,
        reasoning_type="failure_handling",
        reasoning_summary="Planner exceeded the maximum number of allowed turns.",
        error=OrchestratorPlannerError(
            error_code="planner_max_turns_exceeded",
            message="Planner exceeded the maximum number of allowed turns.",
        ),
    )


def _build_orchestrator_telemetry(
    *,
    trace_id: str,
    session_id: str,
    reasoning_level: str,
) -> WorkflowTelemetryEmitter:
    """Build the shared telemetry emitter for the orchestrator loop."""
    return WorkflowTelemetryEmitter(
        trace_id=trace_id,
        review_id=None,
        session_id=session_id,
        tool_name=DEFAULT_ORCHESTRATOR_TOOL_NAME,
        data_store="sqlite",
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_ORCHESTRATOR_REASONING_TYPE,
        step_prefix=DEFAULT_ORCHESTRATOR_STEP_PREFIX,
    )


def _elapsed_ms(start_time: float) -> float:
    """Return elapsed wall-clock time in milliseconds for orchestrator telemetry."""
    return round((perf_counter() - start_time) * 1000, 3)


def _load_initial_state(
    *,
    database_path: Path,
    request: RunReviewOrchestratorRequest,
    trace_id: str,
) -> OrchestratorState:
    """Load reusable stored artifacts and grade state before the first planner turn."""
    session_source = get_session_extraction_source(
        database_path=database_path,
        session_id=request.session_id,
        trace_id=trace_id,
    )
    session_concepts_document, concept_document_warning = _load_reusable_concepts_document(
        database_path=database_path,
        session_id=request.session_id,
        trace_id=trace_id,
    )
    (
        assignment_requirements_document,
        requirement_document_warning,
    ) = _load_reusable_assignment_requirements_document(
        database_path=database_path,
        session_id=request.session_id,
        trace_id=trace_id,
    )
    transcript_available = normalize_transcript_text(session_source.session_transcript) is not None
    state = OrchestratorState(
        request=request,
        session_title=session_source.session_title,
        session_topic=session_source.session_topic,
        transcript_available=transcript_available,
        session_concepts_document=session_concepts_document,
        assignment_requirements_document=assignment_requirements_document,
        extract_concepts_response=_build_extract_concepts_response(
            session_id=request.session_id,
            concepts_document=session_concepts_document,
        ),
        extract_assignment_requirements_response=(
            _build_extract_assignment_requirements_response(
                session_id=request.session_id,
                assignment_requirements_document=assignment_requirements_document,
            )
        ),
    )
    for warning in (concept_document_warning, requirement_document_warning):
        if warning is not None:
            state.warnings.append(warning)
            state.recent_errors.append(warning)
    state.concept_extraction_completed = state.extract_concepts_response is not None
    state.assignment_requirement_extraction_completed = (
        state.extract_assignment_requirements_response is not None
        and (
            _count_assignment_requirements(
                assignment_requirements_document=assignment_requirements_document
            )
            > 0
        )
    )

    if request.student_id is None:
        return state

    session_submissions = list_session_submissions(
        database_path=database_path,
        session_id=request.session_id,
        trace_id=trace_id,
    )
    resolved_submission = _resolve_submission_for_request(
        request=request,
        session_submissions=session_submissions,
    )
    if resolved_submission is None:
        return state

    if resolved_submission.concept_scores:
        state.grade_concepts_response = GradeConceptsResponse(
            student_id=resolved_submission.student_id,
            student_code=resolved_submission.student_code,
            student_full_name=resolved_submission.student_full_name,
            session_id=request.session_id,
            source_type=resolved_submission.source_type,
            repo_url=resolved_submission.repo_url,
            local_path=resolved_submission.local_path,
            zip_path=resolved_submission.zip_path,
            concept_scores=resolved_submission.concept_scores,
            warnings=[],
        )
        state.concept_grading_completed = True

    if (
        request.assignment_requirement_id is not None
        and resolved_submission.assignment_requirement_scores
    ):
        state.grade_assignment_requirements_response = GradeAssignmentRequirementsResponse(
            student_id=resolved_submission.student_id,
            student_code=resolved_submission.student_code,
            student_full_name=resolved_submission.student_full_name,
            session_id=request.session_id,
            assignment_requirement_id=resolved_submission.assignment_requirement_id,
            assignment_title=resolved_submission.assignment_title,
            source_type=resolved_submission.source_type,
            repo_url=resolved_submission.repo_url,
            local_path=resolved_submission.local_path,
            zip_path=resolved_submission.zip_path,
            assignment_requirement_scores=[
                AssignmentRequirementScoreResult.model_validate(score_item)
                for score_item in resolved_submission.assignment_requirement_scores
            ],
            warnings=[],
        )
        state.assignment_requirement_grading_completed = True

    return state


def _load_reusable_concepts_document(
    *,
    database_path: Path,
    session_id: str,
    trace_id: str,
) -> tuple[SessionConceptsResponse, str | None]:
    """Load stored concepts for orchestrator reuse, degrading cleanly on legacy JSON."""
    try:
        return (
            get_session_concepts(
                database_path=database_path,
                session_id=session_id,
                trace_id=trace_id,
            ),
            None,
        )
    except ValueError:
        return (
            SessionConceptsResponse(session_id=session_id, concepts=[]),
            (
                "Stored concepts could not be reused because the stored JSON does not match "
                "the gradeable-concepts schema."
            ),
        )


def _load_reusable_assignment_requirements_document(
    *,
    database_path: Path,
    session_id: str,
    trace_id: str,
) -> tuple[SessionAssignmentRequirementsResponse, str | None]:
    """Load stored requirements for orchestrator reuse, degrading cleanly on bad JSON."""
    try:
        return (
            get_session_assignment_requirements(
                database_path=database_path,
                session_id=session_id,
                trace_id=trace_id,
            ),
            None,
        )
    except ValueError:
        return (
            SessionAssignmentRequirementsResponse(
                session_id=session_id,
                assignment_requirements=[],
            ),
            (
                "Stored assignment requirements could not be reused because the stored JSON "
                "does not match the assignment-requirements schema."
            ),
        )


def _build_extract_concepts_response(
    *,
    session_id: str,
    concepts_document: SessionConceptsResponse,
) -> ExtractConceptsResponse | None:
    """Build a reusable extraction response from stored concepts when possible."""
    if not concepts_document.concepts:
        return None
    return ExtractConceptsResponse(
        session_id=session_id,
        concepts=concepts_document.concepts,
        warnings=[],
    )


def _build_extract_assignment_requirements_response(
    *,
    session_id: str,
    assignment_requirements_document: SessionAssignmentRequirementsResponse,
) -> ExtractAssignmentRequirementsResponse | None:
    """Build a reusable extraction response from stored assignment requirements."""
    if (
        _count_assignment_requirements(
            assignment_requirements_document=assignment_requirements_document
        )
        == 0
    ):
        return None
    return ExtractAssignmentRequirementsResponse(
        session_id=session_id,
        assignment_requirements=[
            assignment_requirement.model_dump(mode="json")
            for assignment_requirement in (
                assignment_requirements_document.assignment_requirements
            )
        ],
        warnings=[],
    )


def _count_assignment_requirements(
    *,
    assignment_requirements_document: SessionAssignmentRequirementsResponse,
) -> int:
    """Return the total stored assignment-requirement item count."""
    return sum(
        len(assignment.requirements)
        for assignment in assignment_requirements_document.assignment_requirements
    )


def _resolve_submission_for_request(
    *,
    request: RunReviewOrchestratorRequest,
    session_submissions: list[SessionSubmission],
) -> SessionSubmission | None:
    """Resolve one stored submission for grade reuse based on request context."""
    if request.student_id is None:
        return None

    matching_submissions = [
        submission
        for submission in session_submissions
        if submission.student_id == request.student_id
    ]
    if request.assignment_requirement_id is not None:
        matching_submissions = [
            submission
            for submission in matching_submissions
            if submission.assignment_requirement_id == request.assignment_requirement_id
        ]
    if len(matching_submissions) == 1:
        return matching_submissions[0]

    source_matched_submissions = [
        submission
        for submission in matching_submissions
        if submission.source_type == request.source_type
        and submission.repo_url == request.repo_url
        and submission.local_path == request.local_path
        and submission.zip_path == request.zip_path
    ]
    if len(source_matched_submissions) == 1:
        return source_matched_submissions[0]
    return None


def _build_planner_prompt_context(
    *,
    state: OrchestratorState,
    trace_id: str,
    turn_number: int,
    max_steps_remaining: int,
) -> OrchestratorPlannerPromptContext:
    """Build the planner prompt context from the current orchestrator state."""
    request = state.request
    return OrchestratorPlannerPromptContext(
        requested_operation=request.operation,
        refresh_policy=request.refresh_policy,
        trace_id=trace_id,
        step_number=turn_number,
        max_steps_remaining=max_steps_remaining,
        completion_condition=_build_completion_condition_text(request.operation),
        session_id=request.session_id,
        session_title=state.session_title,
        session_topic=state.session_topic,
        transcript_available=state.transcript_available,
        student_id=request.student_id,
        assignment_requirement_id=request.assignment_requirement_id,
        source_type=request.source_type,
        repo_url=request.repo_url,
        local_path=request.local_path,
        zip_path=request.zip_path,
        current_state=_build_state_snapshot(state),
        available_tools=_get_available_tools_for_operation(request.operation),
        previous_tool_results=state.tool_results,
        recent_errors=state.recent_errors,
    )


def _build_completion_condition_text(requested_operation: str) -> str:
    """Return the explicit completion rule shown to the planner each turn."""
    if requested_operation == "synthesize_concepts":
        return "Completion is satisfied only when concept_extraction_completed is true."
    if requested_operation == "synthesize_assignment_requirements":
        return (
            "Completion is satisfied only when "
            "assignment_requirement_extraction_completed is true."
        )
    if requested_operation == "grade_concepts":
        return "Completion is satisfied only when concept_grading_completed is true."
    if requested_operation == "grade_assignment_requirements":
        return (
            "Completion is satisfied only when "
            "assignment_requirement_grading_completed is true."
        )
    if requested_operation == "grade_rubrics":
        return "Completion is satisfied only when rubric grading is implemented."
    return (
        "Completion is satisfied only when concept_grading_completed is true and "
        "assignment_requirement_grading_completed is true."
    )


def _build_state_snapshot(state: OrchestratorState) -> dict[str, object]:
    """Return a planner-visible snapshot of current orchestrator state."""
    return {
        "concepts_present": bool(state.session_concepts_document.concepts),
        "assignment_requirements_present": (
            _count_assignment_requirements(
                assignment_requirements_document=state.assignment_requirements_document
            )
            > 0
        ),
        "concept_scores_present": state.grade_concepts_response is not None,
        "assignment_requirement_scores_present": (
            state.grade_assignment_requirements_response is not None
        ),
        "concept_extraction_completed": state.concept_extraction_completed,
        "assignment_requirement_extraction_completed": (
            state.assignment_requirement_extraction_completed
        ),
        "concept_grading_completed": state.concept_grading_completed,
        "assignment_requirement_grading_completed": (
            state.assignment_requirement_grading_completed
        ),
        "stored_concept_count": len(state.session_concepts_document.concepts),
        "stored_assignment_group_count": len(
            state.assignment_requirements_document.assignment_requirements
        ),
        "stored_assignment_requirement_count": _count_assignment_requirements(
            assignment_requirements_document=state.assignment_requirements_document
        ),
        "tool_result_count": len(state.tool_results),
    }


def _get_available_tools_for_operation(
    requested_operation: str,
) -> list[OrchestratorToolName]:
    """Return the minimal coarse workflow tool set for one requested operation."""
    if requested_operation == "synthesize_concepts":
        return ["extract_concepts"]
    if requested_operation == "synthesize_assignment_requirements":
        return ["extract_assignment_requirements"]
    if requested_operation == "grade_concepts":
        return ["extract_concepts", "grade_concepts"]
    if requested_operation == "grade_assignment_requirements":
        return [
            "extract_assignment_requirements",
            "grade_assignment_requirements",
        ]
    return AVAILABLE_ORCHESTRATOR_TOOLS


def _execute_planner_tool_calls(
    *,
    database_path: Path,
    state: OrchestratorState,
    planner_turn: OrchestratorPlannerTurnOutput,
    trace_id: str,
    request_telemetry: WorkflowTelemetryEmitter,
) -> None:
    """Execute the allowlisted coarse tools requested by the planner turn."""
    seen_tool_names: set[OrchestratorToolName] = set()
    for tool_call in planner_turn.tool_calls:
        if tool_call.tool_name in seen_tool_names:
            tool_result = OrchestratorToolExecutionResult(
                tool_name=tool_call.tool_name,
                status="failed",
                output_summary="Planner requested the same tool more than once in one turn.",
                error_code="duplicate_tool_request",
                error_message="Duplicate tool requests are not allowed in the same turn.",
            )
            state.tool_results.append(tool_result)
            state.recent_errors.append(tool_result.error_message or tool_result.output_summary)
            state.state_version += 1
            continue
        seen_tool_names.add(tool_call.tool_name)

        if (
            state.request.refresh_policy != "force_refresh"
            and state.last_tool_state_version.get(tool_call.tool_name) == state.state_version
        ):
            tool_result = OrchestratorToolExecutionResult(
                tool_name=tool_call.tool_name,
                status="failed",
                output_summary=(
                    "Planner requested the same tool without any intervening state "
                    "change."
                ),
                error_code="duplicate_tool_request",
                error_message=(
                    "Tool was already attempted in the current state; the planner must "
                    "choose a different next step."
                ),
            )
            state.tool_results.append(tool_result)
            state.recent_errors.append(tool_result.error_message or tool_result.output_summary)
            state.state_version += 1
            state.last_tool_state_version[tool_call.tool_name] = state.state_version
            continue

        request_telemetry.emit(
            step_suffix="tool_execution_started",
            validation_status="pending",
            retry_count=0,
            tool_name=tool_call.tool_name,
            details={"tool_name": tool_call.tool_name},
        )
        tool_result = _execute_single_tool(
            database_path=database_path,
            state=state,
            tool_name=tool_call.tool_name,
            trace_id=trace_id,
        )
        state.tool_results.append(tool_result)
        state.state_version += 1
        state.last_tool_state_version[tool_call.tool_name] = state.state_version
        if tool_result.status == "failed":
            state.recent_errors.append(tool_result.error_message or tool_result.output_summary)
            request_telemetry.emit(
                step_suffix="tool_execution_completed",
                validation_status="failed",
                retry_count=0,
                tool_name=tool_call.tool_name,
                failure_reason=tool_result.error_code,
                details={"tool_name": tool_call.tool_name},
            )
        else:
            request_telemetry.emit(
                step_suffix="tool_execution_completed",
                validation_status="passed",
                retry_count=0,
                tool_name=tool_call.tool_name,
                details={"tool_name": tool_call.tool_name},
            )


def _execute_single_tool(
    *,
    database_path: Path,
    state: OrchestratorState,
    tool_name: OrchestratorToolName,
    trace_id: str,
) -> OrchestratorToolExecutionResult:
    """Execute one allowlisted coarse tool and update orchestrator state on success."""
    try:
        if tool_name == "extract_concepts":
            response = run_concept_extraction_workflow(
                database_path=database_path,
                session_id=state.request.session_id,
                reasoning_level=state.request.reasoning_level,
                trace_id=trace_id,
            )
            state.warnings.extend(
                _format_api_warnings(
                    prefix="extract_concepts",
                    warnings=response.warnings,
                )
            )
            state.extract_concepts_response = response
            state.session_concepts_document = SessionConceptsResponse(
                session_id=response.session_id,
                concepts=response.concepts,
            )
            state.concept_extraction_completed = True
            return OrchestratorToolExecutionResult(
                tool_name=tool_name,
                status="success",
                output_summary=f"Extracted {len(response.concepts)} concepts.",
            )

        if tool_name == "extract_assignment_requirements":
            response = run_assignment_requirement_extraction_workflow(
                database_path=database_path,
                session_id=state.request.session_id,
                reasoning_level=state.request.reasoning_level,
                trace_id=trace_id,
            )
            state.warnings.extend(
                _format_api_warnings(
                    prefix="extract_assignment_requirements",
                    warnings=response.warnings,
                )
            )
            state.extract_assignment_requirements_response = response
            state.assignment_requirements_document = SessionAssignmentRequirementsResponse(
                session_id=response.session_id,
                assignment_requirements=[
                    StoredAssignmentRequirementResult(
                        assignment_requirement_id=assignment.assignment_requirement_id,
                        assignment_title=assignment.assignment_title,
                        requirements=assignment.requirements,
                    )
                    for assignment in response.assignment_requirements
                ],
            )
            state.assignment_requirement_extraction_completed = True
            requirement_count = sum(
                len(assignment.requirements)
                for assignment in response.assignment_requirements
            )
            return OrchestratorToolExecutionResult(
                tool_name=tool_name,
                status="success",
                output_summary=(
                    "Extracted "
                    f"{requirement_count} assignment requirements across "
                    f"{len(response.assignment_requirements)} assignments."
                ),
            )

        if tool_name == "grade_concepts":
            concepts_document = _require_concepts_document(state)
            response = run_concept_grading_workflow(
                database_path=database_path,
                request=GradeConceptsRequest(
                    student_id=state.request.student_id or "",
                    session_id=state.request.session_id,
                    source_type=state.request.source_type,
                    repo_url=state.request.repo_url,
                    local_path=state.request.local_path,
                    zip_path=state.request.zip_path,
                    reasoning_level=state.request.reasoning_level,
                    concepts=[
                        {
                            "concept_name": concept.name,
                            "summary": concept.summary,
                            "grading_reason": concept.grading_reason,
                            "max_score": concept.concept_importance,
                        }
                        for concept in concepts_document.concepts
                    ],
                ),
                trace_id=trace_id,
            )
            state.warnings.extend(
                _format_api_warnings(
                    prefix="grade_concepts",
                    warnings=response.warnings,
                )
            )
            state.grade_concepts_response = response
            state.concept_grading_completed = True
            return OrchestratorToolExecutionResult(
                tool_name=tool_name,
                status="success",
                output_summary=f"Saved {len(response.concept_scores)} concept scores.",
            )

        requirements_document = _require_assignment_requirements_document(state)
        matching_assignment = next(
            (
                assignment
                for assignment in requirements_document.assignment_requirements
                if assignment.assignment_requirement_id == state.request.assignment_requirement_id
            ),
            None,
        )
        if matching_assignment is None:
            raise OrchestratorToolExecutionFailure(
                code="assignment_requirement_not_found",
                message=(
                    "Stored assignment requirements do not include the requested "
                    "assignment requirement id."
                ),
            )
        response = run_assignment_requirement_grading_workflow(
            database_path=database_path,
            request=GradeAssignmentRequirementsRequest(
                student_id=state.request.student_id or "",
                session_id=state.request.session_id,
                assignment_requirement_id=state.request.assignment_requirement_id or "",
                source_type=state.request.source_type,
                repo_url=state.request.repo_url,
                local_path=state.request.local_path,
                zip_path=state.request.zip_path,
                reasoning_level=state.request.reasoning_level,
                requirements=[
                    AssignmentRequirementGradingCriterion(
                        requirement_type=requirement.requirement_type,
                        title=requirement.title,
                        summary=requirement.summary,
                        evidence=requirement.evidence,
                        max_score=(
                            state.request.grading_policy.default_assignment_requirement_max_score
                        ),
                    )
                    for requirement in matching_assignment.requirements
                ],
            ),
            trace_id=trace_id,
        )
        state.warnings.extend(
                _format_api_warnings(
                    prefix="grade_assignment_requirements",
                    warnings=response.warnings,
                )
            )
        state.grade_assignment_requirements_response = response
        state.assignment_requirement_grading_completed = True
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="success",
            output_summary=(
                "Saved "
                f"{len(response.assignment_requirement_scores)} assignment requirement scores."
            ),
        )
    except OrchestratorToolExecutionFailure as exc:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary=exc.message,
            error_code=exc.code,
            error_message=exc.message,
        )
    except SessionNotFoundError:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Unable to find the requested session.",
            error_code="session_not_found",
            error_message="Unable to find the requested session.",
        )
    except StudentNotFoundError:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Unable to find the requested student.",
            error_code="student_not_found",
            error_message="Unable to find the requested student.",
        )
    except AssignmentRequirementNotFoundError:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Unable to find the requested assignment requirement.",
            error_code="assignment_requirement_not_found",
            error_message="Unable to find the requested assignment requirement.",
        )
    except StudentSubmissionNotFoundError:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Unable to find the student's submission required for grading.",
            error_code="student_submission_not_found",
            error_message="Unable to find the student's submission required for grading.",
        )
    except AmbiguousStudentSubmissionError:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Unable to resolve a unique student submission for grading.",
            error_code="student_submission_ambiguous",
            error_message="Unable to resolve a unique student submission for grading.",
        )
    except ProjectEvidenceCollectionError as exc:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary=exc.message,
            error_code=exc.code,
            error_message=exc.message,
        )
    except StructuredExtractionError as exc:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary=exc.message,
            error_code=exc.code,
            error_message=exc.message,
        )
    except ValidationError as exc:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="Tool input validation failed before execution.",
            error_code="tool_input_validation_failed",
            error_message=str(exc),
        )
    except sqlite3.Error as exc:
        return OrchestratorToolExecutionResult(
            tool_name=tool_name,
            status="failed",
            output_summary="A database error interrupted tool execution.",
            error_code="sqlite_error",
            error_message=str(exc),
        )


def _require_concepts_document(state: OrchestratorState) -> SessionConceptsResponse:
    """Return stored concepts or raise a tool failure when they are unavailable."""
    if not state.session_concepts_document.concepts:
        raise OrchestratorToolExecutionFailure(
            code="stored_concepts_not_available",
            message="No stored concepts are available for concept grading.",
        )
    return state.session_concepts_document


def _require_assignment_requirements_document(
    state: OrchestratorState,
) -> SessionAssignmentRequirementsResponse:
    """Return stored assignment requirements or raise when they are unavailable."""
    if (
        _count_assignment_requirements(
            assignment_requirements_document=state.assignment_requirements_document
        )
        == 0
    ):
        raise OrchestratorToolExecutionFailure(
            code="stored_assignment_requirements_not_available",
            message="No stored assignment requirements are available for grading.",
        )
    return state.assignment_requirements_document


def _apply_context_update(
    *,
    state: OrchestratorState,
    context_update: OrchestratorPlannerContextUpdate | None,
) -> None:
    """Apply planner-provided context update notes to orchestrator warnings."""
    if context_update is None:
        return
    state.warnings.append(
        f"Planner context update: {context_update.next_goal}"
    )


def _can_finalize(*, state: OrchestratorState, requested_operation: str) -> bool:
    """Return whether the current orchestrator state satisfies the requested operation."""
    if requested_operation == "synthesize_concepts":
        return state.concept_extraction_completed
    if requested_operation == "synthesize_assignment_requirements":
        return state.assignment_requirement_extraction_completed
    if requested_operation == "grade_concepts":
        return state.concept_grading_completed
    if requested_operation == "grade_assignment_requirements":
        return state.assignment_requirement_grading_completed
    if requested_operation == "grade_rubrics":
        return False
    return state.concept_grading_completed and state.assignment_requirement_grading_completed


def _build_execution_result(state: OrchestratorState) -> ReviewOrchestratorExecutionResult:
    """Build the aggregated execution result payload returned by the endpoint."""
    return ReviewOrchestratorExecutionResult(
        extract_concepts_response=state.extract_concepts_response,
        extract_assignment_requirements_response=state.extract_assignment_requirements_response,
        grade_concepts_response=state.grade_concepts_response,
        grade_assignment_requirements_response=(
            state.grade_assignment_requirements_response
        ),
    )


def _build_failed_run_response(
    *,
    trace_id: str,
    request: RunReviewOrchestratorRequest,
    state: OrchestratorState,
    reasoning_type: OrchestratorPlannerReasoningType,
    reasoning_summary: str,
    error: OrchestratorPlannerError,
) -> RunReviewOrchestratorResponse:
    """Build a terminal failed response while preserving partial tool outputs."""
    return RunReviewOrchestratorResponse(
        trace_id=trace_id,
        requested_operation=request.operation,
        status="failed",
        reasoning_type=reasoning_type,
        reasoning_summary=reasoning_summary,
        planner_turns=state.planner_turns,
        tool_results=state.tool_results,
        result=_build_execution_result(state),
        warnings=_deduplicate_preserving_order(state.warnings),
        error=error,
    )


def _deduplicate_preserving_order(values: list[str]) -> list[str]:
    """Return one list with duplicate string values removed in first-seen order."""
    deduplicated_values: list[str] = []
    for value in values:
        if value not in deduplicated_values:
            deduplicated_values.append(value)
    return deduplicated_values


def _format_api_warnings(*, prefix: str, warnings: list[ApiWarning]) -> list[str]:
    """Format API warnings into stable orchestrator-visible strings."""
    return [f"{prefix}: {warning.code} - {warning.message}" for warning in warnings]
