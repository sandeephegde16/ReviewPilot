"""Unit tests for repo config file and local `.env` loading."""

from __future__ import annotations

import os

import app.config as config


def test_load_application_config_reads_provider_routing_settings(tmp_path) -> None:
    """Config loader should parse provider routing policy from the repo config file."""
    config_path = tmp_path / ".reviewpilot.config.json"
    config_path.write_text(
        """
        {
          "concept_extraction": {
            "primary_provider": "gemini",
            "fallback_providers": ["heuristic"],
            "model_candidates": {
              "gemini": ["gemini-2.5-pro"],
              "heuristic": ["heuristic-v2"]
            },
            "cooldown_seconds": 15,
            "failures_before_cooldown": 3
          }
        }
        """.strip(),
        encoding="utf-8",
    )

    loaded_config = config.load_application_config(config_path)

    assert loaded_config.concept_extraction.primary_provider == "gemini"
    assert loaded_config.concept_extraction.fallback_providers == ["heuristic"]
    assert loaded_config.concept_extraction.model_candidates.gemini == ["gemini-2.5-pro"]
    assert loaded_config.concept_extraction.cooldown_seconds == 15
    assert loaded_config.concept_extraction.failures_before_cooldown == 3


def test_load_environment_file_sets_provider_api_keys(
    monkeypatch,
    tmp_path,
) -> None:
    """Environment loader should populate API key variables from a local `.env` file."""
    environment_path = tmp_path / ".env"
    environment_path.write_text(
        "ANTHROPIC_API_KEY=test-anthropic-key\nGEMINI_API_KEY=test-gemini-key\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    config.load_environment_file(environment_path)

    assert os.getenv("ANTHROPIC_API_KEY") == "test-anthropic-key"
    assert os.getenv("GEMINI_API_KEY") == "test-gemini-key"
