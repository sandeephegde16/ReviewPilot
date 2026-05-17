"""Provider aliases for the orchestrator planner over the shared structured stack."""

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
    CanonicalStructuredExtractionRequest as CanonicalOrchestratorPlannerRequest,
)
from app.structured_provider import (
    StructuredExtractionProvider as OrchestratorPlannerProvider,
)
from app.structured_provider import (
    StructuredExtractionRepairContext as OrchestratorPlannerRepairContext,
)
from app.structured_provider import (
    build_structured_extraction_provider as build_orchestrator_planner_provider,
)


def select_orchestrator_planner_provider() -> OrchestratorPlannerProvider:
    """Build the configured primary provider for orchestrator planning."""
    provider_name = get_concept_grading_provider_name()
    return build_structured_extraction_provider(
        provider_name=provider_name,
        model_name=get_concept_grading_model_name(provider_name),
    )


def build_orchestrator_planner_provider_candidates() -> list[ProviderCandidate]:
    """Return ordered non-heuristic provider/model candidates for planner turns."""
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
    "CanonicalOrchestratorPlannerRequest",
    "DEFAULT_OUTPUT_MODE",
    "DEFAULT_REASONING_TYPE",
    "OrchestratorPlannerProvider",
    "OrchestratorPlannerRepairContext",
    "OutputMode",
    "PromptInputField",
    "build_orchestrator_planner_provider",
    "build_orchestrator_planner_provider_candidates",
    "get_provider_reasoning_metadata",
    "select_orchestrator_planner_provider",
]
