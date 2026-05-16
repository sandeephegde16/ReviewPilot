"""Concept extraction orchestration for grading workflows."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from pydantic import ValidationError

import app.concept_provider as concept_provider
import app.provider_router as provider_router
from app.schemas import (
    ApiWarning,
    ConceptExtractionOutput,
    ExtractConceptsResponse,
    ReasoningLevel,
    SessionExtractionSource,
    get_concept_extraction_output_schema,
)
from app.telemetry import emit_event
from app.transcript_parser import normalize_transcript_text

DEFAULT_OPERATION_NAME = "extract_gradeable_concepts"
DEFAULT_TOOL_NAME = DEFAULT_OPERATION_NAME
DEFAULT_REASONING_TYPE = concept_provider.DEFAULT_REASONING_TYPE
TRANSCRIPT_WARNING = ApiWarning(
    code="session_transcript_not_available",
    message="Session transcript not available, synthesized concepts are based on session topic.",
)
MAX_SCHEMA_REPAIR_ATTEMPTS = 1


class ConceptExtractionError(Exception):
    """Raised when concept extraction cannot produce a valid response."""

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


class ConceptProviderCallError(ConceptExtractionError):
    """Raised when a provider call fails and the router may try another candidate."""


@dataclass(frozen=True)
class PreparedCanonicalRequest:
    """Canonical extraction request and any fallback warnings for the response."""

    request: concept_provider.CanonicalConceptExtractionRequest
    warnings: list[ApiWarning]


@dataclass(frozen=True)
class CompletedConceptExtraction:
    """Final extraction response plus provider metadata for request telemetry."""

    response: ExtractConceptsResponse
    provider_name: str
    model_name: str
    retry_count: int


@dataclass(frozen=True)
class ValidatedProviderOutput:
    """Validated structured provider output and the retry count required to reach it."""

    output: ConceptExtractionOutput
    retry_count: int


def extract_concepts_for_session(
    *,
    session_source: SessionExtractionSource,
    reasoning_level: ReasoningLevel,
    trace_id: str,
) -> CompletedConceptExtraction:
    """Extract gradeable concepts for one session with schema repair fallback."""
    start_time = perf_counter()
    prepared_request = _prepare_canonical_request(
        session_source=session_source,
        reasoning_level=reasoning_level,
        trace_id=trace_id,
    )
    provider, validated_output = _extract_with_provider_routing(
        reasoning_level=reasoning_level,
        request=prepared_request.request,
        trace_id=trace_id,
    )
    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    _emit_extraction_event(
        request=prepared_request.request,
        trace_id=trace_id,
        step_name="extract_session_concepts.completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=validated_output.retry_count,
        elapsed_ms=elapsed_ms,
    )
    response = ExtractConceptsResponse(
        session_id=session_source.id,
        concepts=validated_output.output.concepts,
        warnings=prepared_request.warnings,
    )
    return CompletedConceptExtraction(
        response=response,
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        retry_count=validated_output.retry_count,
    )


def _extract_with_provider_routing(
    *,
    reasoning_level: ReasoningLevel,
    request: concept_provider.CanonicalConceptExtractionRequest,
    trace_id: str,
) -> tuple[concept_provider.ConceptExtractionProvider, ValidatedProviderOutput]:
    """Try ordered provider candidates, including failover and cooldown handling."""
    start_time = perf_counter()
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.provider_selection_started",
        validation_status="pending",
        retry_count=0,
    )
    candidates = provider_router.build_provider_candidates()
    last_error: ConceptExtractionError | None = None
    for attempt_index, candidate in enumerate(candidates, start=1):
        if provider_router.is_candidate_in_cooldown(candidate):
            _emit_extraction_event(
                request=request,
                trace_id=trace_id,
                step_name="extract_session_concepts.provider_candidate_skipped",
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
            _emit_extraction_event(
                request=request,
                trace_id=trace_id,
                step_name="extract_session_concepts.provider_failover_started",
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
                reasoning_level=reasoning_level,
                use_primary_selector=(attempt_index == 1),
            )
        except LookupError as exc:
            _emit_extraction_event(
                request=request,
                trace_id=trace_id,
                step_name="extract_session_concepts.provider_candidate_skipped",
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

        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.provider_selection_completed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="passed",
            retry_count=0,
            elapsed_ms=elapsed_ms,
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
            )
        except ConceptProviderCallError as exc:
            last_error = exc
            cooldown_status = provider_router.record_candidate_failure(candidate)
            _emit_extraction_event(
                request=request,
                trace_id=trace_id,
                step_name="extract_session_concepts.provider_candidate_failed",
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
        except ConceptExtractionError:
            raise

        provider_router.record_candidate_success(candidate)
        return provider, output

    if last_error is not None:
        raise last_error
    raise ConceptExtractionError(
        code="no_provider_available",
        message="No concept extraction provider is available for the current configuration.",
    )


def _build_provider_from_candidate(
    *,
    candidate: provider_router.ProviderCandidate,
    reasoning_level: ReasoningLevel,
    use_primary_selector: bool,
) -> concept_provider.ConceptExtractionProvider:
    """Build a provider instance for one router candidate."""
    if use_primary_selector:
        return concept_provider.select_concept_extraction_provider(
            reasoning_level=reasoning_level
        )
    return concept_provider.build_concept_extraction_provider(
        provider_name=candidate.provider_name,
        model_name=candidate.model_name,
    )


def _prepare_canonical_request(
    *,
    session_source: SessionExtractionSource,
    reasoning_level: ReasoningLevel,
    trace_id: str,
) -> PreparedCanonicalRequest:
    """Build the canonical provider-agnostic request for concept extraction."""
    warnings: list[ApiWarning] = []
    session_transcript = normalize_transcript_text(session_source.session_transcript)
    if session_transcript is None:
        warnings.append(TRANSCRIPT_WARNING)

    if not session_source.session_title.strip() and not session_source.session_topic.strip():
        raise ConceptExtractionError(
            code="concept_extraction_failed",
            message="Unable to prepare usable session evidence for concept extraction.",
        )
    request = concept_provider.CanonicalConceptExtractionRequest(
        session_id=session_source.id,
        operation_name=DEFAULT_OPERATION_NAME,
        session_title=session_source.session_title,
        session_topic=session_source.session_topic,
        session_transcript=session_transcript,
        reasoning_level=reasoning_level,
        reasoning_type=DEFAULT_REASONING_TYPE,
        output_mode=concept_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_concept_extraction_output_schema(),
    )
    if warnings:
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.transcript_fallback_used",
            validation_status="passed",
            retry_count=0,
            failure_reason=TRANSCRIPT_WARNING.code,
        )
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.canonical_request_built",
        validation_status="passed",
        retry_count=0,
        details=_build_canonical_request_telemetry_details(
            request=request,
            used_transcript_fallback=bool(warnings),
        ),
    )
    return PreparedCanonicalRequest(request=request, warnings=warnings)


def _call_provider_and_validate(
    *,
    provider: concept_provider.ConceptExtractionProvider,
    request: concept_provider.CanonicalConceptExtractionRequest,
    trace_id: str,
) -> ValidatedProviderOutput:
    """Call the provider, validate the response, and retry once on schema failure."""
    raw_output = _invoke_provider(
        provider=provider,
        request=request,
        trace_id=trace_id,
        retry_count=0,
    )
    validation_start_time = perf_counter()
    try:
        validated_output = ConceptExtractionOutput.model_validate(raw_output)
    except ValidationError as exc:
        validation_errors = _format_validation_errors(exc)
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.schema_validation_failed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=0,
            elapsed_ms=round((perf_counter() - validation_start_time) * 1000, 3),
            failure_reason="; ".join(validation_errors),
        )
    else:
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.schema_validation_passed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="passed",
            retry_count=0,
            elapsed_ms=round((perf_counter() - validation_start_time) * 1000, 3),
        )
        return ValidatedProviderOutput(output=validated_output, retry_count=0)

    repair_context = concept_provider.ConceptExtractionRepairContext(
        previous_output=raw_output,
        validation_errors=validation_errors,
    )
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.repair_started",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="pending",
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        details={"validation_errors": validation_errors},
    )
    repair_start_time = perf_counter()
    repaired_output = _invoke_provider(
        provider=provider,
        request=request,
        trace_id=trace_id,
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        repair_context=repair_context,
    )
    repair_validation_start_time = perf_counter()
    try:
        validated_output = ConceptExtractionOutput.model_validate(repaired_output)
    except ValidationError as exc:
        validation_errors = _format_validation_errors(exc)
        repair_elapsed_ms = round((perf_counter() - repair_start_time) * 1000, 3)
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.repair_completed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
            elapsed_ms=repair_elapsed_ms,
            failure_reason="; ".join(validation_errors),
            details={"validation_errors": validation_errors},
        )
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.schema_repair_failed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
            failure_reason="; ".join(validation_errors),
        )
        raise ConceptExtractionError(
            code="concept_schema_validation_failed",
            message="Unable to validate the extracted concepts after schema repair.",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        ) from exc
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.schema_validation_passed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        elapsed_ms=round((perf_counter() - repair_validation_start_time) * 1000, 3),
    )
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.repair_completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
        elapsed_ms=round((perf_counter() - repair_start_time) * 1000, 3),
    )
    return ValidatedProviderOutput(
        output=validated_output,
        retry_count=MAX_SCHEMA_REPAIR_ATTEMPTS,
    )


def _invoke_provider(
    *,
    provider: concept_provider.ConceptExtractionProvider,
    request: concept_provider.CanonicalConceptExtractionRequest,
    trace_id: str,
    retry_count: int,
    repair_context: concept_provider.ConceptExtractionRepairContext | None = None,
) -> dict[str, object]:
    """Invoke the selected provider and emit structured telemetry around the call."""
    start_time = perf_counter()
    provider_reasoning_metadata = concept_provider.get_provider_reasoning_metadata(
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        reasoning_level=request.reasoning_level,
    )
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.provider_call_started",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="pending",
        retry_count=retry_count,
        details=provider_reasoning_metadata.model_dump(),
    )
    try:
        response = provider.extract_concepts(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )
    except Exception as exc:
        elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
        _emit_extraction_event(
            request=request,
            trace_id=trace_id,
            step_name="extract_session_concepts.provider_call_failed",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            validation_status="failed",
            retry_count=retry_count,
            elapsed_ms=elapsed_ms,
            failure_reason=str(exc),
            details=provider_reasoning_metadata.model_dump(),
        )
        raise ConceptProviderCallError(
            code="concept_extraction_failed",
            message="The concept extraction provider was unable to produce a response.",
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            retry_count=retry_count,
        ) from exc

    elapsed_ms = round((perf_counter() - start_time) * 1000, 3)
    _emit_extraction_event(
        request=request,
        trace_id=trace_id,
        step_name="extract_session_concepts.provider_call_completed",
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        validation_status="passed",
        retry_count=retry_count,
        elapsed_ms=elapsed_ms,
        details=provider_reasoning_metadata.model_dump(),
    )
    return response


def _format_validation_errors(error: ValidationError) -> list[str]:
    """Format Pydantic validation errors into compact strings for repair prompts."""
    formatted_errors: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        formatted_errors.append(f"{location}: {item['msg']}")
    return formatted_errors


def _build_canonical_request_telemetry_details(
    *,
    request: concept_provider.CanonicalConceptExtractionRequest,
    used_transcript_fallback: bool,
) -> dict[str, object]:
    """Return safe metadata about the canonical request for production telemetry."""
    return {
        "session_id": request.session_id,
        "operation_name": request.operation_name,
        "reasoning_level": request.reasoning_level,
        "reasoning_type": request.reasoning_type,
        "output_mode": request.output_mode,
        "response_schema_title": str(request.response_schema.get("title") or ""),
        "has_session_transcript": request.session_transcript is not None,
        "session_transcript_length": len(request.session_transcript or ""),
        "used_transcript_fallback": used_transcript_fallback,
        "session_title_present": bool(request.session_title.strip()),
        "session_topic_present": bool(request.session_topic.strip()),
    }


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


def _emit_extraction_event(
    *,
    request: concept_provider.CanonicalConceptExtractionRequest,
    trace_id: str,
    step_name: str,
    validation_status: str,
    retry_count: int,
    provider_name: str | None = None,
    model_name: str | None = None,
    elapsed_ms: float | None = None,
    failure_reason: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    """Emit one extraction event with consistent canonical request metadata."""
    emit_event(
        trace_id=trace_id,
        review_id=None,
        session_id=request.session_id,
        step_name=step_name,
        tool_name=request.operation_name,
        data_store=None,
        provider_name=provider_name,
        model_name=model_name,
        reasoning_level=request.reasoning_level,
        reasoning_type=request.reasoning_type,
        validation_status=validation_status,
        retry_count=retry_count,
        elapsed_ms=elapsed_ms,
        failure_reason=failure_reason,
        details=details,
    )
