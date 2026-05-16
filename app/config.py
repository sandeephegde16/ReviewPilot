"""Configuration helpers for the ReviewPilot app."""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "db" / "reviewpilot.db"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / ".reviewpilot.config.json"
DEFAULT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
DEFAULT_CONCEPT_EXTRACTION_PROVIDER = "anthropic"
DEFAULT_CONCEPT_GRADING_PROVIDER = "anthropic"
DEFAULT_CONCEPT_EXTRACTION_MODEL = "heuristic-v1"
DEFAULT_ANTHROPIC_CONCEPT_MODEL = "claude-sonnet-4-6"
DEFAULT_GEMINI_CONCEPT_MODEL = "gemini-2.5-flash"
DEFAULT_PROVIDER_COOLDOWN_SECONDS = 60
DEFAULT_PROVIDER_FAILURES_BEFORE_COOLDOWN = 2


class ProviderModelCandidates(BaseModel):
    """Provider-specific model candidate lists loaded from the repo config file."""

    anthropic: list[str] = Field(default_factory=list)
    gemini: list[str] = Field(default_factory=list)
    heuristic: list[str] = Field(default_factory=list)


class ConceptExtractionConfig(BaseModel):
    """Provider routing settings for concept extraction."""

    primary_provider: str = DEFAULT_CONCEPT_EXTRACTION_PROVIDER
    fallback_providers: list[str] = Field(default_factory=list)
    model_candidates: ProviderModelCandidates = Field(
        default_factory=ProviderModelCandidates
    )
    cooldown_seconds: int = DEFAULT_PROVIDER_COOLDOWN_SECONDS
    failures_before_cooldown: int = DEFAULT_PROVIDER_FAILURES_BEFORE_COOLDOWN


class ConceptGradingConfig(BaseModel):
    """Provider routing settings for concept grading."""

    primary_provider: str = DEFAULT_CONCEPT_GRADING_PROVIDER
    fallback_providers: list[str] = Field(default_factory=list)
    model_candidates: ProviderModelCandidates = Field(
        default_factory=ProviderModelCandidates
    )
    cooldown_seconds: int = DEFAULT_PROVIDER_COOLDOWN_SECONDS
    failures_before_cooldown: int = DEFAULT_PROVIDER_FAILURES_BEFORE_COOLDOWN


class ReviewPilotConfig(BaseModel):
    """Top-level application config loaded from the repo config file."""

    concept_extraction: ConceptExtractionConfig = Field(
        default_factory=ConceptExtractionConfig
    )
    concept_grading: ConceptGradingConfig = Field(default_factory=ConceptGradingConfig)


def load_environment_file(environment_path: Path | None = None) -> None:
    """Load local environment variables from the repo `.env` file when present."""
    target_path = environment_path or Path(
        os.getenv("REVIEWPILOT_ENV_PATH", DEFAULT_ENV_PATH)
    )
    load_dotenv(target_path, override=False)


@cache
def load_application_config(config_path: Path | None = None) -> ReviewPilotConfig:
    """Load the repo config file that defines provider routing policy."""
    target_path = config_path or Path(
        os.getenv("REVIEWPILOT_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    )
    if not target_path.exists():
        return ReviewPilotConfig()

    with target_path.open("r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)
    return ReviewPilotConfig.model_validate(raw_config)


def _get_application_config() -> ReviewPilotConfig:
    """Return the cached application config using the configured repo path."""
    configured_path = Path(os.getenv("REVIEWPILOT_CONFIG_PATH", DEFAULT_CONFIG_PATH))
    return load_application_config(configured_path)


def get_database_path() -> Path:
    """Return the configured SQLite database path."""
    configured_path = os.getenv("REVIEWPILOT_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DATABASE_PATH


def get_concept_extraction_provider_name() -> str:
    """Return the configured concept extraction provider name."""
    configured_provider_name = os.getenv("REVIEWPILOT_CONCEPT_PROVIDER")
    if configured_provider_name:
        return configured_provider_name
    return _get_application_config().concept_extraction.primary_provider


def get_concept_grading_provider_name() -> str:
    """Return the configured concept grading provider name."""
    configured_provider_name = os.getenv("REVIEWPILOT_CONCEPT_GRADING_PROVIDER")
    if configured_provider_name:
        return configured_provider_name
    return _get_application_config().concept_grading.primary_provider


def get_concept_extraction_fallback_provider_names(
    primary_provider_name: str | None = None,
) -> list[str]:
    """Return the ordered fallback providers for concept extraction."""
    configured_fallbacks = os.getenv("REVIEWPILOT_CONCEPT_FALLBACK_PROVIDERS")
    if configured_fallbacks:
        return _parse_csv_config(configured_fallbacks)

    config_fallbacks = _get_application_config().concept_extraction.fallback_providers
    if config_fallbacks:
        return config_fallbacks

    primary_provider_name = primary_provider_name or get_concept_extraction_provider_name()
    if primary_provider_name == "anthropic":
        return ["gemini", "heuristic"]
    if primary_provider_name == "gemini":
        return ["anthropic", "heuristic"]
    return ["anthropic", "gemini"]


def get_concept_grading_fallback_provider_names(
    primary_provider_name: str | None = None,
) -> list[str]:
    """Return the ordered fallback providers for concept grading."""
    configured_fallbacks = os.getenv("REVIEWPILOT_CONCEPT_GRADING_FALLBACK_PROVIDERS")
    if configured_fallbacks:
        return _parse_csv_config(configured_fallbacks)

    config_fallbacks = _get_application_config().concept_grading.fallback_providers
    if config_fallbacks:
        return config_fallbacks

    primary_provider_name = primary_provider_name or get_concept_grading_provider_name()
    if primary_provider_name == "anthropic":
        return ["gemini"]
    if primary_provider_name == "gemini":
        return ["anthropic"]
    return ["anthropic", "gemini"]


def get_concept_extraction_model_name(provider_name: str | None = None) -> str:
    """Return the configured concept extraction model name."""
    configured_model_name = os.getenv("REVIEWPILOT_CONCEPT_MODEL")
    if configured_model_name:
        return configured_model_name

    provider_name = (provider_name or get_concept_extraction_provider_name()).strip().lower()
    configured_model_candidates = _get_configured_model_candidates(provider_name)
    if configured_model_candidates:
        return configured_model_candidates[0]

    if provider_name == "anthropic":
        return DEFAULT_ANTHROPIC_CONCEPT_MODEL
    if provider_name == "gemini":
        return DEFAULT_GEMINI_CONCEPT_MODEL
    return DEFAULT_CONCEPT_EXTRACTION_MODEL


def get_concept_grading_model_name(provider_name: str | None = None) -> str:
    """Return the configured concept grading model name."""
    configured_model_name = os.getenv("REVIEWPILOT_CONCEPT_GRADING_MODEL")
    if configured_model_name:
        return configured_model_name

    provider_name = (provider_name or get_concept_grading_provider_name()).strip().lower()
    configured_model_candidates = _get_concept_grading_configured_model_candidates(provider_name)
    if configured_model_candidates:
        return configured_model_candidates[0]

    if provider_name == "anthropic":
        return DEFAULT_ANTHROPIC_CONCEPT_MODEL
    if provider_name == "gemini":
        return DEFAULT_GEMINI_CONCEPT_MODEL
    return DEFAULT_ANTHROPIC_CONCEPT_MODEL


def get_concept_extraction_model_names(provider_name: str) -> list[str]:
    """Return the ordered model candidates for one provider."""
    provider_name = provider_name.strip().lower()
    if provider_name == "anthropic":
        configured_models = os.getenv("REVIEWPILOT_ANTHROPIC_CONCEPT_MODELS")
        default_model = DEFAULT_ANTHROPIC_CONCEPT_MODEL
    elif provider_name == "gemini":
        configured_models = os.getenv("REVIEWPILOT_GEMINI_CONCEPT_MODELS")
        default_model = DEFAULT_GEMINI_CONCEPT_MODEL
    else:
        configured_models = os.getenv("REVIEWPILOT_HEURISTIC_CONCEPT_MODELS")
        default_model = DEFAULT_CONCEPT_EXTRACTION_MODEL

    if configured_models:
        model_names = _parse_csv_config(configured_models)
    else:
        model_names = _get_configured_model_candidates(provider_name)
    if provider_name == get_concept_extraction_provider_name():
        configured_primary_model_name = os.getenv("REVIEWPILOT_CONCEPT_MODEL")
        if configured_primary_model_name:
            model_names.insert(0, configured_primary_model_name)
    model_names.append(default_model)
    return _deduplicate_preserving_order(model_names)


def get_concept_grading_model_names(provider_name: str) -> list[str]:
    """Return the ordered concept grading model candidates for one provider."""
    provider_name = provider_name.strip().lower()
    if provider_name == "anthropic":
        configured_models = os.getenv("REVIEWPILOT_ANTHROPIC_CONCEPT_GRADING_MODELS")
        default_model = DEFAULT_ANTHROPIC_CONCEPT_MODEL
    elif provider_name == "gemini":
        configured_models = os.getenv("REVIEWPILOT_GEMINI_CONCEPT_GRADING_MODELS")
        default_model = DEFAULT_GEMINI_CONCEPT_MODEL
    else:
        configured_models = None
        default_model = DEFAULT_ANTHROPIC_CONCEPT_MODEL

    if configured_models:
        model_names = _parse_csv_config(configured_models)
    else:
        model_names = _get_concept_grading_configured_model_candidates(provider_name)
    if provider_name == get_concept_grading_provider_name():
        configured_primary_model_name = os.getenv("REVIEWPILOT_CONCEPT_GRADING_MODEL")
        if configured_primary_model_name:
            model_names.insert(0, configured_primary_model_name)
    model_names.append(default_model)
    return _deduplicate_preserving_order(model_names)


def get_provider_cooldown_seconds() -> int:
    """Return the cooldown duration used after repeated provider failures."""
    configured_seconds = os.getenv("REVIEWPILOT_PROVIDER_COOLDOWN_SECONDS")
    if configured_seconds is not None:
        return max(int(configured_seconds), 0)
    return max(_get_application_config().concept_extraction.cooldown_seconds, 0)


def get_provider_failures_before_cooldown() -> int:
    """Return the failure threshold required before a cooldown is activated."""
    configured_threshold = os.getenv("REVIEWPILOT_PROVIDER_FAILURES_BEFORE_COOLDOWN")
    if configured_threshold is not None:
        return max(int(configured_threshold), 1)
    return max(_get_application_config().concept_extraction.failures_before_cooldown, 1)


def get_anthropic_api_key() -> str | None:
    """Return the configured Anthropic API key, if present."""
    return os.getenv("REVIEWPILOT_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


def get_gemini_api_key() -> str | None:
    """Return the configured Gemini API key, if present."""
    return os.getenv("REVIEWPILOT_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")


def _parse_csv_config(configured_value: str | None) -> list[str]:
    """Split a comma-delimited configuration value into trimmed entries."""
    if configured_value is None:
        return []
    return [part.strip() for part in configured_value.split(",") if part.strip()]


def _get_configured_model_candidates(provider_name: str) -> list[str]:
    """Return provider model candidates from the repo config file."""
    configured_models = _get_application_config().concept_extraction.model_candidates
    if provider_name == "anthropic":
        return configured_models.anthropic.copy()
    if provider_name == "gemini":
        return configured_models.gemini.copy()
    return configured_models.heuristic.copy()


def _get_concept_grading_configured_model_candidates(provider_name: str) -> list[str]:
    """Return concept grading model candidates from the repo config file."""
    configured_models = _get_application_config().concept_grading.model_candidates
    if provider_name == "anthropic":
        return configured_models.anthropic.copy()
    if provider_name == "gemini":
        return configured_models.gemini.copy()
    return configured_models.heuristic.copy()


def _deduplicate_preserving_order(values: list[str]) -> list[str]:
    """Remove duplicates from a list while preserving the original order."""
    deduplicated_values: list[str] = []
    for value in values:
        if value not in deduplicated_values:
            deduplicated_values.append(value)
    return deduplicated_values


load_environment_file()
