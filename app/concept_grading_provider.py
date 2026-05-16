"""Thin concept grading provider aliases over the shared structured provider stack."""

from app.config import (
    get_concept_grading_fallback_provider_names,
    get_concept_grading_model_name,
    get_concept_grading_model_names,
    get_concept_grading_provider_name,
)
from app.provider_router import ProviderCandidate
from app.structured_provider import (
    DEFAULT_OUTPUT_MODE,
    DEFAULT_REASONING_TYPE,
    OutputMode,
    PromptInputField,
    build_structured_extraction_provider,
    get_provider_reasoning_metadata,
)
from app.structured_provider import (
    CanonicalStructuredExtractionRequest as CanonicalConceptGradingRequest,
)
from app.structured_provider import (
    StructuredExtractionProvider as ConceptGradingProvider,
)
from app.structured_provider import (
    StructuredExtractionRepairContext as ConceptGradingRepairContext,
)
from app.structured_provider import (
    build_structured_extraction_provider as build_concept_grading_provider,
)


def select_concept_grading_provider() -> ConceptGradingProvider:
    """Build the configured primary provider for concept grading."""
    provider_name = get_concept_grading_provider_name()
    return build_structured_extraction_provider(
        provider_name=provider_name,
        model_name=get_concept_grading_model_name(provider_name),
    )


def build_concept_grading_provider_candidates() -> list[ProviderCandidate]:
    """Return ordered non-heuristic provider/model candidates for concept grading."""
    primary_provider_name = get_concept_grading_provider_name()
    ordered_provider_names = [primary_provider_name]
    ordered_provider_names.extend(
        get_concept_grading_fallback_provider_names(primary_provider_name)
    )

    candidates: list[ProviderCandidate] = []
    for provider_name in ordered_provider_names:
        if provider_name == "heuristic":
            continue
        for model_name in get_concept_grading_model_names(provider_name):
            candidate = ProviderCandidate(
                provider_name=provider_name,
                model_name=model_name,
            )
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates


__all__ = [
    "CanonicalConceptGradingRequest",
    "ConceptGradingProvider",
    "ConceptGradingRepairContext",
    "DEFAULT_OUTPUT_MODE",
    "DEFAULT_REASONING_TYPE",
    "OutputMode",
    "PromptInputField",
    "build_concept_grading_provider",
    "build_concept_grading_provider_candidates",
    "get_provider_reasoning_metadata",
    "select_concept_grading_provider",
]
