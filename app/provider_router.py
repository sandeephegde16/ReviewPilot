"""Provider routing helpers for concept extraction failover and cooldown policy."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from app.config import (
    get_concept_extraction_fallback_provider_names,
    get_concept_extraction_model_names,
    get_concept_extraction_provider_name,
    get_provider_cooldown_seconds,
    get_provider_failures_before_cooldown,
)


@dataclass(frozen=True)
class ProviderCandidate:
    """One provider/model candidate that can be attempted for concept extraction."""

    provider_name: str
    model_name: str

    @property
    def key(self) -> str:
        """Return the stable key used for cooldown tracking."""
        return f"{self.provider_name}:{self.model_name}"


@dataclass
class ProviderCooldownStatus:
    """Mutable cooldown tracking state for one provider/model candidate."""

    consecutive_failures: int = 0
    cooldown_until: float = 0.0


_COOLDOWN_STATE: dict[str, ProviderCooldownStatus] = {}


def build_provider_candidates() -> list[ProviderCandidate]:
    """Return the ordered provider/model candidates for one extraction attempt."""
    primary_provider_name = get_concept_extraction_provider_name()
    ordered_provider_names = [primary_provider_name]
    ordered_provider_names.extend(
        get_concept_extraction_fallback_provider_names(primary_provider_name)
    )

    candidates: list[ProviderCandidate] = []
    for provider_name in ordered_provider_names:
        for model_name in get_concept_extraction_model_names(provider_name):
            candidate = ProviderCandidate(
                provider_name=provider_name,
                model_name=model_name,
            )
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates


def is_candidate_in_cooldown(candidate: ProviderCandidate) -> bool:
    """Return whether the candidate is currently in cooldown."""
    cooldown_status = _COOLDOWN_STATE.get(candidate.key)
    if cooldown_status is None:
        return False
    if cooldown_status.cooldown_until <= monotonic():
        cooldown_status.cooldown_until = 0.0
        return False
    return True


def get_candidate_cooldown_remaining_seconds(candidate: ProviderCandidate) -> float:
    """Return the remaining cooldown time in seconds for a candidate."""
    cooldown_status = _COOLDOWN_STATE.get(candidate.key)
    if cooldown_status is None:
        return 0.0
    remaining_seconds = cooldown_status.cooldown_until - monotonic()
    return max(round(remaining_seconds, 3), 0.0)


def record_candidate_success(candidate: ProviderCandidate) -> None:
    """Clear cooldown state after a successful provider/model attempt."""
    _COOLDOWN_STATE[candidate.key] = ProviderCooldownStatus()


def record_candidate_failure(candidate: ProviderCandidate) -> ProviderCooldownStatus:
    """Update cooldown state after a failed provider/model attempt."""
    cooldown_status = _COOLDOWN_STATE.setdefault(candidate.key, ProviderCooldownStatus())
    cooldown_status.consecutive_failures += 1
    if cooldown_status.consecutive_failures >= get_provider_failures_before_cooldown():
        cooldown_status.cooldown_until = monotonic() + get_provider_cooldown_seconds()
        cooldown_status.consecutive_failures = 0
    return ProviderCooldownStatus(
        consecutive_failures=cooldown_status.consecutive_failures,
        cooldown_until=cooldown_status.cooldown_until,
    )


def clear_router_state() -> None:
    """Reset router cooldown state, primarily for tests."""
    _COOLDOWN_STATE.clear()
