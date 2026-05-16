"""Shared routing, validation, repair, and telemetry for structured extraction endpoints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from time import perf_counter

from pydantic import BaseModel, ValidationError

import app.provider_router as provider_router
from app.schemas import ApiWarning
from app.structured_provider import (
    CanonicalStructuredExtractionRequest,
    StructuredExtractionProvider,
    StructuredExtractionRepairContext,
)
from app.telemetry import WorkflowTelemetryEmitter

MAX_SCHEMA_REPAIR_ATTEMPTS = 1

SelectPrimaryProvider = Callable[[], StructuredExtractionProvider]
BuildProvider = Callable[..., StructuredExtractionProvider]


class StructuredExtractionError(Exception):
    """Raised when structured extraction cannot produce a valid response."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        provider_name: str | None = None,
        model_name: str | None = None,
        retry_count: int = 0,
    ) -> None:
        """Store a stable error code and human-readable message."""
        super().__init__(message)
        self.code = code
        self.message = message
        self.provider_name = provider_name
        self.model_name = model_name
        self.retry_count = retry_count


class StructuredProviderCallError(StructuredExtractionError):
    """Raised when a provider call fails and the router may try another candidate."""


@dataclass(frozen=True)
class CompletedStructuredExtraction[ResponseModelT]:
    """Final extraction response plus provider metadata for request telemetry."""

    response: ResponseModelT
    provider_name: str | None
    model_name: str | None
    retry_count: int


@dataclass(frozen=True)
class ValidatedProviderOutput[OutputModelT: BaseModel]:
    """Validated structured provider output and the retry count required to reach it."""

    output: OutputModelT
    retry_count: int


@dataclass(frozen=True)
class ProviderAttemptResult[OutputModelT: BaseModel]:
    """Raw provider output plus validation details for one extraction attempt."""

    raw_output: dict[str, object]
    validated_output: OutputModelT | None
    validation_errors: list[str]


@dataclass(frozen=True)
class PreparedExtractionEvent:
    """One pre-provider telemetry event derived during canonical request preparation."""

    step_suffix: str
    validation_status: str
    retry_count: int = 0
    failure_reason: str | None = None
    details: dict[str, object] | None = None


@dataclass(frozen=True)
class StructuredExtractionSpec[OutputModelT: BaseModel, ResponseModelT]:
    """Static workflow settings for one structured extraction API."""

    step_prefix: str
    output_model: type[OutputModelT]
    schema_failure_code: str
    schema_failure_message: str
    select_primary_provider: SelectPrimaryProvider
    build_provider: BuildProvider
    build_provider_candidates: Callable[[], list[provider_router.ProviderCandidate]] | None = (
        None
    )


@dataclass(frozen=True)
class PreparedStructuredExtraction[OutputModelT: BaseModel, ResponseModelT]:
    """Canonical request plus response mapping for one extraction attempt."""

    request: CanonicalStructuredExtractionRequest
    warnings: list[ApiWarning]
    build_response: Callable[[OutputModelT, list[ApiWarning]], ResponseModelT]
    preparation_events: list[PreparedExtractionEvent] = field(default_factory=list)
    short_circuit_response: ResponseModelT | None = None
    short_circuit_event: PreparedExtractionEvent | None = None


def execute_structured_extraction[OutputModelT: BaseModel, ResponseModelT](
    *,
    spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
    prepared: PreparedStructuredExtraction[OutputModelT, ResponseModelT],
    trace_id: str,
) -> CompletedStructuredExtraction[ResponseModelT]:
    """Run the provider-agnostic extraction flow after canonical request preparation."""
    start_time = perf_counter()
    telemetry = _build_extraction_telemetry(
        trace_id=trace_id,
        spec=spec,
        request=prepared.request,
    )

    for preparation_event in prepared.preparation_events:
        telemetry.emit(
            step_suffix=preparation_event.step_suffix,
            validation_status=preparation_event.validation_status,
            retry_count=preparation_event.retry_count,
            failure_reason=preparation_event.failure_reason,
            details=preparation_event.details,
        )

    if prepared.short_circuit_response is not None:
        if prepared.short_circuit_event is not None:
            telemetry.emit(
                step_suffix=prepared.short_circuit_event.step_suffix,
                validation_status=prepared.short_circuit_event.validation_status,
                retry_count=prepared.short_circuit_event.retry_count,
                failure_reason=prepared.short_circuit_event.failure_reason,
                details=prepared.short_circuit_event.details,
            )
        telemetry.emit(
            step_suffix="completed",
            validation_status="passed",
            retry_count=0,
            elapsed_ms=round((perf_counter() - start_time) * 1000, 3),
        )
        return CompletedStructuredExtraction(
            response=prepared.short_circuit_response,
            provider_name=None,
            model_name=None,
            retry_count=0,
        )

    provider, validated_output = extract_with_provider_routing(
        request=prepared.request,
        trace_id=trace_id,
        spec=spec,
        telemetry=telemetry,
    )
    telemetry.emit(
        step_suffix="completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=validated_output.retry_count,
        elapsed_ms=round((perf_counter() - start_time) * 1000, 3),
    )
    return CompletedStructuredExtraction(
        response=prepared.build_response(validated_output.output, prepared.warnings),
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        retry_count=validated_output.retry_count,
    )


def extract_with_provider_routing[OutputModelT: BaseModel, ResponseModelT](
    *,
    request: CanonicalStructuredExtractionRequest,
    trace_id: str,
    spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
    telemetry: WorkflowTelemetryEmitter,
) -> tuple[StructuredExtractionProvider, ValidatedProviderOutput[OutputModelT]]:
    """Try ordered provider candidates, including failover and cooldown handling."""
    start_time = perf_counter()
    telemetry.emit(
        step_suffix="provider_selection_started",
        validation_status="pending",
        retry_count=0,
    )
    candidates = (
        spec.build_provider_candidates()
        if spec.build_provider_candidates is not None
        else provider_router.build_provider_candidates()
    )
    last_error: StructuredExtractionError | None = None
    for attempt_index, candidate in enumerate(candidates, start=1):
        if provider_router.is_candidate_in_cooldown(candidate):
            telemetry.emit(
                step_suffix="provider_candidate_skipped",
                provider_name=candidate.provider_name,
                model_name=candidate.model_name,
                validation_status="skipped",
                retry_count=0,
                failure_reason="candidate_in_cooldown",
                details=_build_provider_candidate_details(
                    candidate=candidate,
                    attempt_index=attempt_index,
                    cooldown_remaining_seconds=(
                        provider_router.get_candidate_cooldown_remaining_seconds(candidate)
                    ),
                ),
            )
            continue

        if attempt_index > 1:
            telemetry.emit(
                step_suffix="provider_failover_started",
                provider_name=candidate.provider_name,
                model_name=candidate.model_name,
                validation_status="pending",
                retry_count=0,
                details=_build_provider_candidate_details(
                    candidate=candidate,
                    attempt_index=attempt_index,
                ),
            )

        try:
            provider = _build_provider_from_candidate(
                candidate=candidate,
                attempt_index=attempt_index,
                spec=spec,
            )
        except LookupError as exc:
            telemetry.emit(
                step_suffix="provider_candidate_skipped",
                provider_name=candidate.provider_name,
                model_name=candidate.model_name,
                validation_status="skipped",
                retry_count=0,
                failure_reason=str(exc),
                details=_build_provider_candidate_details(
                    candidate=candidate,
                    attempt_index=attempt_index,
                ),
            )
            continue

        telemetry.emit(
            step_suffix="provider_selection_completed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="passed",
            retry_count=0,
            elapsed_ms=round((perf_counter() - start_time) * 1000, 3),
            details=_build_provider_candidate_details(
                candidate=candidate,
                attempt_index=attempt_index,
            ),
        )
        try:
            output = _call_provider_and_validate(
                provider=provider,
                request=request,
                trace_id=trace_id,
                spec=spec,
                telemetry=telemetry,
            )
        except StructuredProviderCallError as exc:
            last_error = exc
            cooldown_status = provider_router.record_candidate_failure(candidate)
            telemetry.emit(
                step_suffix="provider_candidate_failed",
                provider_name=provider.provider_name,
                model_name=provider.model_name,
                validation_status="failed",
                retry_count=exc.retry_count,
                failure_reason=exc.code,
                details=_build_provider_candidate_details(
                    candidate=candidate,
                    attempt_index=attempt_index,
                    cooldown_remaining_seconds=(
                        provider_router.get_candidate_cooldown_remaining_seconds(candidate)
                    ),
                    consecutive_failures=cooldown_status.consecutive_failures,
                ),
            )
            continue
        except StructuredExtractionError:
            raise

        provider_router.record_candidate_success(candidate)
        return provider, output

    if last_error is not None:
        raise last_error
    raise StructuredExtractionError(
        code="no_provider_available",
        message="No structured extraction provider is available for the current configuration.",
    )


def _build_provider_from_candidate[OutputModelT: BaseModel, ResponseModelT](
    *,
    candidate: provider_router.ProviderCandidate,
    attempt_index: int,
    spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
) -> StructuredExtractionProvider:
    """Build a provider instance for one router candidate."""
    if attempt_index == 1 and spec.build_provider_candidates is None:
        return spec.select_primary_provider()
    return spec.build_provider(
        provider_name=candidate.provider_name,
        model_name=candidate.model_name,
    )


def _call_provider_and_validate[OutputModelT: BaseModel, ResponseModelT](
    *,
    provider: StructuredExtractionProvider,
    request: CanonicalStructuredExtractionRequest,
    trace_id: str,
    spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
    telemetry: WorkflowTelemetryEmitter,
) -> ValidatedProviderOutput[OutputModelT]:
    """Call the provider, validate the response, and retry once on schema failure."""
    initial_attempt = _run_provider_attempt(
        provider=provider,
        request=request,
        trace_id=trace_id,
        retry_count=0,
        output_model=spec.output_model,
        telemetry=telemetry,
        emit_validation_failure_event=True,
    )
    if initial_attempt.validated_output is not None:
        return ValidatedProviderOutput(output=initial_attempt.validated_output, retry_count=0)

    repair_context = StructuredExtractionRepairContext(
        previous_output=initial_attempt.raw_output,
        validation_errors=initial_attempt.validation_errors,
    )
    telemetry.emit(
        step_suffix="repair_started",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="pending",
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        details={"validation_errors": initial_attempt.validation_errors},
    )
    repair_start_time = perf_counter()
    repair_attempt = _run_provider_attempt(
        provider=provider,
        request=request,
        trace_id=trace_id,
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        output_model=spec.output_model,
        telemetry=telemetry,
        repair_context=repair_context,
        emit_validation_failure_event=False,
    )
    if repair_attempt.validated_output is None:
        telemetry.emit(
            step_suffix="repair_completed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
            elapsed_ms=round((perf_counter() - repair_start_time) * 1000, 3),
            failure_reason="; ".join(repair_attempt.validation_errors),
            details={"validation_errors": repair_attempt.validation_errors},
        )
        telemetry.emit(
            step_suffix="schema_repair_failed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
            failure_reason="; ".join(repair_attempt.validation_errors),
        )
        raise StructuredExtractionError(
            code=spec.schema_failure_code,
            message=spec.schema_failure_message,
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        )
    telemetry.emit(
        step_suffix="repair_completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        elapsed_ms=round((perf_counter() - repair_start_time) * 1000, 3),
    )
    return ValidatedProviderOutput(
        output=repair_attempt.validated_output,
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
    )


def _run_provider_attempt[OutputModelT: BaseModel](
    *,
    provider: StructuredExtractionProvider,
    request: CanonicalStructuredExtractionRequest,
    trace_id: str,
    retry_count: int,
    output_model: type[OutputModelT],
    telemetry: WorkflowTelemetryEmitter,
    emit_validation_failure_event: bool,
    repair_context: StructuredExtractionRepairContext | None = None,
) -> ProviderAttemptResult[OutputModelT]:
    """Run one provider attempt, including transport telemetry and schema validation."""
    raw_output = _invoke_provider(
        provider=provider,
        request=request,
        trace_id=trace_id,
        retry_count=retry_count,
        telemetry=telemetry,
        repair_context=repair_context,
    )
    validated_output, validation_errors = _validate_provider_output(
        provider=provider,
        request=request,
        raw_output=raw_output,
        trace_id=trace_id,
        retry_count=retry_count,
        output_model=output_model,
        telemetry=telemetry,
        emit_failure_event=emit_validation_failure_event,
    )
    return ProviderAttemptResult(
        raw_output=raw_output,
        validated_output=validated_output,
        validation_errors=validation_errors,
    )


def _invoke_provider(
    *,
    provider: StructuredExtractionProvider,
    request: CanonicalStructuredExtractionRequest,
    trace_id: str,
    retry_count: int,
    telemetry: WorkflowTelemetryEmitter,
    repair_context: StructuredExtractionRepairContext | None = None,
) -> dict[str, object]:
    """Invoke the selected provider and emit structured telemetry around the call."""
    start_time = perf_counter()
    provider_reasoning_metadata = _get_provider_reasoning_metadata(
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        reasoning_level=request.reasoning_level,
    )
    telemetry.emit(
        step_suffix="provider_call_started",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="pending",
        retry_count=retry_count,
        details=provider_reasoning_metadata.model_dump(),
    )
    try:
        response = provider.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )
    except Exception as exc:
        telemetry.emit(
            step_suffix="provider_call_failed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=retry_count,
            elapsed_ms=round((perf_counter() - start_time) * 1000, 3),
            failure_reason=str(exc),
            details=provider_reasoning_metadata.model_dump(),
        )
        raise StructuredProviderCallError(
            code="structured_extraction_failed",
            message="The structured extraction provider was unable to produce a response.",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            retry_count=retry_count,
        ) from exc

    telemetry.emit(
        step_suffix="provider_call_completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=retry_count,
        elapsed_ms=round((perf_counter() - start_time) * 1000, 3),
        details=provider_reasoning_metadata.model_dump(),
    )
    return response


def _validate_provider_output[OutputModelT: BaseModel](
    *,
    provider: StructuredExtractionProvider,
    request: CanonicalStructuredExtractionRequest,
    raw_output: dict[str, object],
    trace_id: str,
    retry_count: int,
    output_model: type[OutputModelT],
    telemetry: WorkflowTelemetryEmitter,
    emit_failure_event: bool,
) -> tuple[OutputModelT | None, list[str]]:
    """Validate provider output and emit the shared schema-validation telemetry."""
    del request, trace_id
    validation_start_time = perf_counter()
    try:
        validated_output = output_model.model_validate(raw_output)
    except ValidationError as exc:
        validation_errors = _format_validation_errors(exc)
        if emit_failure_event:
            telemetry.emit(
                step_suffix="schema_validation_failed",
                provider_name=provider.provider_name,
                model_name=provider.model_name,
                validation_status="failed",
                retry_count=retry_count,
                elapsed_ms=round((perf_counter() - validation_start_time) * 1000, 3),
                failure_reason="; ".join(validation_errors),
            )
        return None, validation_errors

    telemetry.emit(
        step_suffix="schema_validation_passed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=retry_count,
        elapsed_ms=round((perf_counter() - validation_start_time) * 1000, 3),
    )
    return validated_output, []


def _format_validation_errors(error: ValidationError) -> list[str]:
    """Format Pydantic validation errors into compact strings for repair prompts."""
    formatted_errors: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        formatted_errors.append(f"{location}: {item['msg']}")
    return formatted_errors


def _build_provider_candidate_details(
    *,
    candidate: provider_router.ProviderCandidate,
    attempt_index: int,
    cooldown_remaining_seconds: float = 0.0,
    consecutive_failures: int | None = None,
) -> dict[str, object]:
    """Return safe telemetry details for one routed provider/model candidate."""
    details: dict[str, object] = {
        "provider_name": candidate.provider_name,
        "model_name": candidate.model_name,
        "attempt_index": attempt_index,
        "cooldown_remaining_seconds": cooldown_remaining_seconds,
    }
    if consecutive_failures is not None:
        details["consecutive_failures"] = consecutive_failures
    return details


def _build_extraction_telemetry[OutputModelT: BaseModel, ResponseModelT](
    *,
    trace_id: str,
    spec: StructuredExtractionSpec[OutputModelT, ResponseModelT],
    request: CanonicalStructuredExtractionRequest,
) -> WorkflowTelemetryEmitter:
    """Build the shared telemetry emitter for one structured extraction workflow."""
    return WorkflowTelemetryEmitter(
        trace_id=trace_id,
        review_id=None,
        session_id=request.session_id,
        tool_name=request.operation_name,
        data_store=None,
        reasoning_level=request.reasoning_level,
        reasoning_type=request.reasoning_type,
        step_prefix=spec.step_prefix,
    )


def _get_provider_reasoning_metadata(*, provider_name: str, model_name: str, reasoning_level: str):
    """Avoid a circular import by loading provider metadata lazily."""
    from app.structured_provider import get_provider_reasoning_metadata

    return get_provider_reasoning_metadata(
        provider_name=provider_name,
        model_name=model_name,
        reasoning_level=reasoning_level,
    )
