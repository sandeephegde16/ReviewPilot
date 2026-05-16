"""Unit tests for concept extraction provider routing and cooldown policy."""

from __future__ import annotations

import app.provider_router as provider_router


def test_build_provider_candidates_uses_default_routing_order(
    monkeypatch,
) -> None:
    """Router should default to anthropic, then gemini, then heuristic."""
    monkeypatch.delenv("REVIEWPILOT_CONCEPT_PROVIDER", raising=False)
    monkeypatch.delenv("REVIEWPILOT_CONCEPT_FALLBACK_PROVIDERS", raising=False)
    monkeypatch.delenv("REVIEWPILOT_CONCEPT_MODEL", raising=False)
    monkeypatch.delenv("REVIEWPILOT_ANTHROPIC_CONCEPT_MODELS", raising=False)
    monkeypatch.delenv("REVIEWPILOT_GEMINI_CONCEPT_MODELS", raising=False)
    monkeypatch.delenv("REVIEWPILOT_HEURISTIC_CONCEPT_MODELS", raising=False)

    candidates = provider_router.build_provider_candidates()

    assert [(candidate.provider_name, candidate.model_name) for candidate in candidates] == [
        ("anthropic", "claude-sonnet-4-6"),
        ("gemini", "gemini-2.5-flash"),
        ("heuristic", "heuristic-v1"),
    ]


def test_build_provider_candidates_orders_primary_fallbacks_and_models(
    monkeypatch,
) -> None:
    """Router should expand primary and fallback providers into ordered model candidates."""
    monkeypatch.setenv("REVIEWPILOT_CONCEPT_PROVIDER", "anthropic")
    monkeypatch.setenv("REVIEWPILOT_CONCEPT_FALLBACK_PROVIDERS", "gemini,heuristic")
    monkeypatch.setenv(
        "REVIEWPILOT_ANTHROPIC_CONCEPT_MODELS",
        "claude-sonnet-4-6,claude-haiku-4-5-20251001",
    )
    monkeypatch.setenv(
        "REVIEWPILOT_GEMINI_CONCEPT_MODELS",
        "gemini-2.5-flash,gemini-2.5-flash-lite",
    )

    candidates = provider_router.build_provider_candidates()

    assert [(candidate.provider_name, candidate.model_name) for candidate in candidates] == [
        ("anthropic", "claude-sonnet-4-6"),
        ("anthropic", "claude-haiku-4-5-20251001"),
        ("gemini", "gemini-2.5-flash"),
        ("gemini", "gemini-2.5-flash-lite"),
        ("heuristic", "heuristic-v1"),
    ]


def test_record_candidate_failure_activates_cooldown_after_threshold(
    monkeypatch,
) -> None:
    """Router should activate cooldown only after the configured failure threshold."""
    monkeypatch.setenv("REVIEWPILOT_PROVIDER_FAILURES_BEFORE_COOLDOWN", "2")
    monkeypatch.setenv("REVIEWPILOT_PROVIDER_COOLDOWN_SECONDS", "60")
    candidate = provider_router.ProviderCandidate(
        provider_name="anthropic",
        model_name="claude-sonnet-4-6",
    )

    first_status = provider_router.record_candidate_failure(candidate)
    second_status = provider_router.record_candidate_failure(candidate)

    assert first_status.consecutive_failures == 1
    assert first_status.cooldown_until == 0.0
    assert second_status.consecutive_failures == 0
    assert second_status.cooldown_until > 0.0
    assert provider_router.is_candidate_in_cooldown(candidate) is True
    assert provider_router.get_candidate_cooldown_remaining_seconds(candidate) > 0.0
