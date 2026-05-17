"""Planner prompt shaping and workflow specification for the orchestrator loop."""

from __future__ import annotations

import json
from dataclasses import dataclass

import app.orchestrator_provider as orchestrator_provider
from app.schemas import (
    OrchestratorPlannerTurnOutput,
    OrchestratorRefreshPolicy,
    OrchestratorToolExecutionResult,
    OrchestratorToolName,
    ReasoningLevel,
    get_orchestrator_planner_output_schema,
)
from app.structured_extraction import (
    PreparedExtractionEvent,
    PreparedStructuredExtraction,
    StructuredExtractionSpec,
)

DEFAULT_OPERATION_NAME = "run_reviewpilot_orchestrator"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = "workflow_orchestration"
DEFAULT_STEP_PREFIX = "run_reviewpilot_orchestrator"

ORCHESTRATOR_PLANNER_SPEC = StructuredExtractionSpec[
    OrchestratorPlannerTurnOutput, OrchestratorPlannerTurnOutput
](
    step_prefix=DEFAULT_STEP_PREFIX,
    output_model=OrchestratorPlannerTurnOutput,
    schema_failure_code="orchestrator_planner_schema_validation_failed",
    schema_failure_message=(
        "Unable to validate the orchestrator planner output after schema repair."
    ),
    select_primary_provider=lambda: (
        orchestrator_provider.select_orchestrator_planner_provider()
    ),
    build_provider=lambda *, provider_name, model_name: (
        orchestrator_provider.build_orchestrator_planner_provider(
            provider_name=provider_name,
            model_name=model_name,
        )
    ),
    build_provider_candidates=lambda: (
        orchestrator_provider.build_orchestrator_planner_provider_candidates()
    ),
)


@dataclass(frozen=True)
class OrchestratorPlannerPromptContext:
    """Internal prompt input used to build one planner turn request."""

    requested_operation: str
    refresh_policy: OrchestratorRefreshPolicy
    trace_id: str
    step_number: int
    max_steps_remaining: int
    completion_condition: str
    session_id: str
    session_title: str
    session_topic: str
    transcript_available: bool
    student_id: str | None
    assignment_requirement_id: str | None
    source_type: str | None
    repo_url: str | None
    local_path: str | None
    zip_path: str | None
    current_state: dict[str, object]
    available_tools: list[OrchestratorToolName]
    previous_tool_results: list[OrchestratorToolExecutionResult]
    recent_errors: list[str]


def prepare_orchestrator_planner_turn(
    *,
    prompt_context: OrchestratorPlannerPromptContext,
    reasoning_level: ReasoningLevel,
) -> PreparedStructuredExtraction[
    OrchestratorPlannerTurnOutput, OrchestratorPlannerTurnOutput
]:
    """Build the canonical planner request and identity response mapper for one turn."""
    request = orchestrator_provider.CanonicalOrchestratorPlannerRequest(
        session_id=prompt_context.session_id,
        operation_name=DEFAULT_OPERATION_NAME,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=orchestrator_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_orchestrator_planner_output_schema(),
        prompt_subject="Agent turn input",
        prompt_input_fields=[
            orchestrator_provider.PromptInputField(
                label="Requested operation",
                value=prompt_context.requested_operation,
            ),
            orchestrator_provider.PromptInputField(
                label="Refresh policy",
                value=prompt_context.refresh_policy,
            ),
            orchestrator_provider.PromptInputField(
                label="Trace and turn metadata",
                value=_format_turn_metadata(prompt_context),
            ),
            orchestrator_provider.PromptInputField(
                label="Completion condition",
                value=prompt_context.completion_condition,
            ),
            orchestrator_provider.PromptInputField(
                label="Current state",
                value=_format_current_state(prompt_context.current_state),
            ),
            orchestrator_provider.PromptInputField(
                label="Session context",
                value=_format_session_context(prompt_context),
            ),
            orchestrator_provider.PromptInputField(
                label="Submission context",
                value=_format_submission_context(prompt_context),
            ),
            orchestrator_provider.PromptInputField(
                label="Available tools",
                value=_format_available_tools(prompt_context.available_tools),
            ),
            orchestrator_provider.PromptInputField(
                label="Previous tool results",
                value=_format_previous_tool_results(prompt_context.previous_tool_results),
            ),
            orchestrator_provider.PromptInputField(
                label="Recent errors",
                value=_format_recent_errors(prompt_context.recent_errors),
            ),
        ],
        system_instruction_lines=[
            "You are ReviewPilot Orchestrator Agent.",
            (
                "Your job is to decide what to do next in a multi-turn workflow to satisfy "
                "the requested operation."
            ),
            "You do not execute tools yourself.",
            "You must use tool calls for extraction and grading work.",
            "You must base decisions only on the current state and previous tool results.",
            "Do not invent evidence, artifacts, or successful tool outcomes.",
            "Work in these stages:",
            "1. Validate required inputs.",
            "2. Inspect current_state and previous tool results.",
            "3. Decide whether stored artifacts can be reused or must be refreshed.",
            "4. Choose the smallest correct next action or terminal response.",
            "5. Run the required self-checks before returning.",
            "Reason step-by-step internally, but do not reveal hidden chain-of-thought.",
            "Return only visible reasoning_summary and the required structured fields.",
            (
                "You may return only one of these response types: TOOL_REQUEST, "
                "CONTEXT_UPDATE, FINAL_REVIEW, FALLBACK."
            ),
            "Use only tools listed in Available tools.",
            "Never request duplicate tool calls unless refresh_policy is force_refresh.",
            "Prefer the smallest next step that makes progress.",
            (
                "Respect prerequisites: grade_concepts requires concepts; "
                "grade_assignment_requirements requires assignment requirements."
            ),
            "If a tool fails, use the failure result in your next decision.",
            "If required inputs are missing and no allowed tool can recover them, return FALLBACK.",
            "Return FINAL_REVIEW only if the Completion condition is satisfied in Current state.",
            "Self-check before returning:",
            "- every tool call is allowlisted",
            "- prerequisites are already satisfied or made satisfiable by this turn",
            "- duplicate actions are avoided",
            "- the selected response is minimal for the requested operation",
            "- FALLBACK is used when progress is no longer possible",
        ],
        repair_guidance_lines=[
            "TOOL_REQUEST responses must include at least one tool_calls entry.",
            "CONTEXT_UPDATE responses must include context_update and no tool_calls.",
            "FINAL_REVIEW responses must include final_review and no tool_calls.",
            "FALLBACK responses must include error.error_code and error.message.",
            "Always return checks with all required boolean fields.",
        ],
        repair_output_example={
            "response_type": "TOOL_REQUEST",
            "reasoning_type": "prerequisite_planning",
            "reasoning_summary": (
                "Stored concepts are missing, so concept extraction must run "
                "before grading."
            ),
            "checks": {
                "inputs_sufficient": True,
                "allowed_tools_only": True,
                "prerequisites_satisfied_or_planned": True,
                "duplicate_actions_avoided": True,
                "plan_is_minimal": True,
            },
            "tool_calls": [{"tool_name": "extract_concepts"}],
            "context_update": None,
            "final_review": None,
            "warnings": [],
            "error": {
                "error_code": None,
                "message": None,
                "details": None,
            },
        },
        telemetry_details={
            "session_id": prompt_context.session_id,
            "operation_name": DEFAULT_OPERATION_NAME,
            "reasoning_level": reasoning_level,
            "reasoning_type": DEFAULT_REASONING_TYPE,
            "output_mode": orchestrator_provider.DEFAULT_OUTPUT_MODE,
            "response_schema_title": "OrchestratorPlannerTurnOutput",
            "requested_operation": prompt_context.requested_operation,
            "step_number": prompt_context.step_number,
            "max_steps_remaining": prompt_context.max_steps_remaining,
            "available_tool_count": len(prompt_context.available_tools),
            "previous_tool_result_count": len(prompt_context.previous_tool_results),
            "recent_error_count": len(prompt_context.recent_errors),
        },
    )

    return PreparedStructuredExtraction(
        request=request,
        warnings=[],
        build_response=lambda output, response_warnings: output,
        preparation_events=[
            PreparedExtractionEvent(
                step_suffix="canonical_request_built",
                validation_status="passed",
                details=request.telemetry_details,
            )
        ],
    )


def _format_turn_metadata(prompt_context: OrchestratorPlannerPromptContext) -> str:
    """Format stable planner-turn metadata for the user prompt."""
    return "\n".join(
        [
            f"trace_id: {prompt_context.trace_id}",
            f"step_number: {prompt_context.step_number}",
            f"max_steps_remaining: {prompt_context.max_steps_remaining}",
        ]
    )


def _format_current_state(current_state: dict[str, object]) -> str:
    """Format the current state snapshot as stable JSON."""
    return json.dumps(current_state, ensure_ascii=True, sort_keys=True, indent=2)


def _format_session_context(prompt_context: OrchestratorPlannerPromptContext) -> str:
    """Format stable session metadata for the planner prompt."""
    return "\n".join(
        [
            f"session_id: {prompt_context.session_id}",
            f"session_title: {prompt_context.session_title}",
            f"session_topic: {prompt_context.session_topic}",
            f"transcript_available: {str(prompt_context.transcript_available).lower()}",
        ]
    )


def _format_submission_context(prompt_context: OrchestratorPlannerPromptContext) -> str:
    """Format submission metadata and source locators for the planner prompt."""
    return "\n".join(
        [
            f"student_id: {prompt_context.student_id or '(not provided)'}",
            (
                "assignment_requirement_id: "
                f"{prompt_context.assignment_requirement_id or '(not provided)'}"
            ),
            f"source_type: {prompt_context.source_type or '(not provided)'}",
            f"repo_url: {prompt_context.repo_url or '(not provided)'}",
            f"local_path: {prompt_context.local_path or '(not provided)'}",
            f"zip_path: {prompt_context.zip_path or '(not provided)'}",
        ]
    )


def _format_available_tools(available_tools: list[OrchestratorToolName]) -> str:
    """Format allowlisted tool names into stable prompt text."""
    return "\n".join(f"- {tool_name}" for tool_name in available_tools)


def _format_previous_tool_results(
    previous_tool_results: list[OrchestratorToolExecutionResult],
) -> str:
    """Format bounded prior tool results into stable planner-visible text."""
    if not previous_tool_results:
        return "(none)"

    formatted_results: list[str] = []
    for index, tool_result in enumerate(previous_tool_results, start=1):
        formatted_results.extend(
            [
                f"{index}. tool_name: {tool_result.tool_name}",
                f"   status: {tool_result.status}",
                f"   output_summary: {tool_result.output_summary}",
                f"   error_code: {tool_result.error_code or '(none)'}",
                f"   error_message: {tool_result.error_message or '(none)'}",
            ]
        )
    return "\n".join(formatted_results)


def _format_recent_errors(recent_errors: list[str]) -> str:
    """Format recent orchestrator errors into stable prompt text."""
    if not recent_errors:
        return "(none)"
    return "\n".join(f"- {error_message}" for error_message in recent_errors)
