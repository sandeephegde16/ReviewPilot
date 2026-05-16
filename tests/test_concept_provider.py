"""Unit tests for concept extraction provider adapters and schema shaping."""

from __future__ import annotations

import json

import pytest

import app.concept_provider as concept_provider
from app.schemas import get_concept_extraction_output_schema


def _build_canonical_request(
    *,
    reasoning_level: str = "high",
) -> concept_provider.CanonicalConceptExtractionRequest:
    """Build a representative canonical concept extraction request for provider tests."""
    return concept_provider.CanonicalConceptExtractionRequest(
        session_id="session-test",
        operation_name="extract_gradeable_concepts",
        session_title="Advanced MCP",
        session_topic="MCP transports and tool registration",
        session_transcript=(
            "MCP tool registration connects tools to the runtime.\n"
            "Schema validation keeps integrations reliable."
        ),
        reasoning_level=reasoning_level,
        reasoning_type=concept_provider.DEFAULT_REASONING_TYPE,
        output_mode=concept_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_concept_extraction_output_schema(),
    )


def test_concept_extraction_output_schema_is_inlined_for_provider_use() -> None:
    """Provider-facing response schema should not rely on local `$ref` definitions."""
    response_schema = get_concept_extraction_output_schema()

    assert "$defs" not in response_schema
    assert response_schema["title"] == "ConceptExtractionOutput"
    assert response_schema["additionalProperties"] is False
    assert response_schema["properties"]["concepts"]["items"]["title"] == "GradeableConcept"
    assert response_schema["properties"]["concepts"]["items"]["additionalProperties"] is False
    assert (
        response_schema["properties"]["concepts"]["items"]["properties"][
            "concept_importance"
        ]["minimum"]
        == 1
    )
    assert (
        response_schema["properties"]["concepts"]["items"]["properties"][
            "concept_importance"
        ]["maximum"]
        == 10
    )
    assert (
        response_schema["properties"]["concepts"]["items"]["properties"]["evidence"]["items"][
            "type"
        ]
        == "string"
    )


def test_select_concept_extraction_provider_returns_anthropic_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Anthropic provider selection should honor configured provider and default model."""
    monkeypatch.setenv("REVIEWPILOT_CONCEPT_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test-key")
    monkeypatch.delenv("REVIEWPILOT_CONCEPT_MODEL", raising=False)

    provider = concept_provider.select_concept_extraction_provider(
        reasoning_level="medium",
    )

    assert isinstance(provider, concept_provider.AnthropicConceptExtractionProvider)
    assert provider.provider_name == "anthropic"
    assert provider.model_name == "claude-sonnet-4-6"


def test_select_concept_extraction_provider_returns_gemini_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Gemini provider selection should honor configured provider and default model."""
    monkeypatch.setenv("REVIEWPILOT_CONCEPT_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.delenv("REVIEWPILOT_CONCEPT_MODEL", raising=False)

    provider = concept_provider.select_concept_extraction_provider(
        reasoning_level="medium",
    )

    assert isinstance(provider, concept_provider.GeminiConceptExtractionProvider)
    assert provider.provider_name == "gemini"
    assert provider.model_name == "gemini-2.5-flash"


def test_select_concept_extraction_provider_requires_real_provider_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Selecting a real provider without credentials should fail early."""
    monkeypatch.setenv("REVIEWPILOT_CONCEPT_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("REVIEWPILOT_ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(LookupError):
        concept_provider.select_concept_extraction_provider(reasoning_level="medium")


def test_anthropic_provider_uses_forced_tool_schema_and_returns_tool_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Anthropic adapter should send tool schema and parse the forced tool input."""
    captured_request: dict[str, object] = {}

    def _fake_post_json(*, provider_name: str, url: str, headers, body):
        captured_request["provider_name"] = provider_name
        captured_request["url"] = url
        captured_request["headers"] = headers
        captured_request["body"] = body
        return {
            "content": [
                {
                    "type": "tool_use",
                    "name": "extract_gradeable_concepts",
                    "input": {
                        "concepts": [
                            {
                                "name": "Tool registration",
                                "summary": "Explains how tools are exposed to the runtime.",
                                "grading_reason": "Students must wire tools correctly.",
                                "concept_importance": 9,
                                "evidence": [
                                    "MCP tool registration connects tools to the runtime."
                                ],
                            }
                        ]
                    },
                }
            ]
        }

    monkeypatch.setattr(concept_provider, "_post_json", _fake_post_json)
    provider = concept_provider.AnthropicConceptExtractionProvider(
        model_name="claude-sonnet-4-0",
        api_key="anthropic-test-key",
    )
    request = _build_canonical_request()

    result = provider.extract_concepts(request, trace_id="trace-anthropic")

    assert result["concepts"][0]["name"] == "Tool registration"
    assert captured_request["provider_name"] == "anthropic"
    assert captured_request["url"] == concept_provider.ANTHROPIC_MESSAGES_API_URL
    body = captured_request["body"]
    assert isinstance(body, dict)
    assert body["model"] == "claude-sonnet-4-0"
    assert body["tool_choice"] == {
        "type": "tool",
        "name": request.operation_name,
        "disable_parallel_tool_use": True,
    }
    assert "thinking" not in body
    assert body["tools"][0]["name"] == request.operation_name
    assert body["tools"][0]["strict"] is True
    anthropic_input_schema = body["tools"][0]["input_schema"]
    assert anthropic_input_schema["title"] == "ConceptExtractionOutput"
    assert (
        anthropic_input_schema["properties"]["concepts"]["items"]["properties"][
            "concept_importance"
        ]["type"]
        == "integer"
    )
    assert "minimum" not in anthropic_input_schema["properties"]["concepts"]["items"][
        "properties"
    ]["concept_importance"]
    assert "maximum" not in anthropic_input_schema["properties"]["concepts"]["items"][
        "properties"
    ]["concept_importance"]
    assert "Reasoning level: high" in body["system"]
    assert "concept_importance as an integer from 1 to 10" in body["system"]
    assert "Session transcript:" in body["messages"][0]["content"][0]["text"]


def test_gemini_provider_uses_structured_output_schema_and_parses_json_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Gemini adapter should send response schema and parse JSON text responses."""
    captured_request: dict[str, object] = {}

    def _fake_post_json(*, provider_name: str, url: str, headers, body):
        captured_request["provider_name"] = provider_name
        captured_request["url"] = url
        captured_request["headers"] = headers
        captured_request["body"] = body
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "concepts": [
                                            {
                                                "name": "Schema validation",
                                                "summary": (
                                                    "Explains how structured outputs stay"
                                                    " reliable."
                                                ),
                                                "grading_reason": (
                                                    "Students should preserve schema"
                                                    " contracts."
                                                ),
                                                "concept_importance": 8,
                                                "evidence": [
                                                    (
                                                        "Schema validation keeps"
                                                        " integrations reliable."
                                                    )
                                                ],
                                            }
                                        ]
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }

    monkeypatch.setattr(concept_provider, "_post_json", _fake_post_json)
    provider = concept_provider.GeminiConceptExtractionProvider(
        model_name="gemini-2.5-flash",
        api_key="gemini-test-key",
    )
    request = _build_canonical_request()

    result = provider.extract_concepts(request, trace_id="trace-gemini")

    assert result["concepts"][0]["name"] == "Schema validation"
    assert captured_request["provider_name"] == "gemini"
    assert (
        captured_request["url"]
        == "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
    )
    body = captured_request["body"]
    assert isinstance(body, dict)
    assert body["generationConfig"]["thinkingConfig"] == {
        "includeThoughts": False,
        "thinkingBudget": 2048,
    }
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert body["generationConfig"]["responseJsonSchema"] == request.response_schema
    assert "Operation: extract_gradeable_concepts" in body["contents"][0]["parts"][0]["text"]


def test_gemini_provider_uses_thinking_level_for_gemini_3_models(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Gemini 3 models should receive `thinkingLevel` instead of `thinkingBudget`."""
    captured_request: dict[str, object] = {}

    def _fake_post_json(*, provider_name: str, url: str, headers, body):
        captured_request["body"] = body
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "concepts": [
                                            {
                                                "name": "MCP transports",
                                                "summary": "Explains how MCP transports move data.",
                                                "grading_reason": (
                                                    "Students should configure transports "
                                                    "correctly."
                                                ),
                                                "concept_importance": 8,
                                                "evidence": [
                                                    "MCP transports and tool registration"
                                                ],
                                            }
                                        ]
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }

    monkeypatch.setattr(concept_provider, "_post_json", _fake_post_json)
    provider = concept_provider.GeminiConceptExtractionProvider(
        model_name="gemini-3-flash-preview",
        api_key="gemini-test-key",
    )
    request = _build_canonical_request(reasoning_level="medium")

    provider.extract_concepts(request, trace_id="trace-gemini-3")

    body = captured_request["body"]
    assert isinstance(body, dict)
    assert body["generationConfig"]["thinkingConfig"] == {
        "includeThoughts": False,
        "thinkingLevel": "medium",
    }


def test_provider_reasoning_metadata_keeps_type_null_when_provider_lacks_it() -> None:
    """Provider reasoning metadata should leave native type unset when unsupported."""
    anthropic_metadata = concept_provider.get_provider_reasoning_metadata(
        provider_name="anthropic",
        model_name="claude-sonnet-4-6",
        reasoning_level="high",
    )
    gemini_metadata = concept_provider.get_provider_reasoning_metadata(
        provider_name="gemini",
        model_name="gemini-2.5-flash",
        reasoning_level="high",
    )
    heuristic_metadata = concept_provider.get_provider_reasoning_metadata(
        provider_name="heuristic",
        model_name="heuristic-v1",
        reasoning_level="high",
    )

    assert anthropic_metadata.provider_reasoning_level is None
    assert anthropic_metadata.provider_reasoning_type is None
    assert gemini_metadata.provider_reasoning_level == 2048
    assert gemini_metadata.provider_reasoning_type is None
    assert heuristic_metadata.provider_reasoning_level is None
    assert heuristic_metadata.provider_reasoning_type is None


def test_provider_user_prompt_includes_schema_repair_context() -> None:
    """Repair prompts should include validation errors and the previous invalid output."""
    request = _build_canonical_request()
    repair_context = concept_provider.ConceptExtractionRepairContext(
        previous_output={"concepts": [{"name": "Only name"}]},
        validation_errors=["concepts.0.summary: Field required"],
    )

    prompt = concept_provider._build_provider_user_prompt(  # noqa: SLF001
        request=request,
        repair_context=repair_context,
    )

    assert "Schema check failed on the previous output." in prompt
    assert "Return a root JSON object in this shape:" in prompt
    assert '"concepts": [{"name": "Concept name"' in prompt
    assert "concepts.0.summary: Field required" in prompt
    assert '{"concepts": [{"name": "Only name"}]}' in prompt


def test_anthropic_input_schema_strips_integer_bounds_only() -> None:
    """Anthropic schema shaping should remove integer bounds while preserving shared schema."""
    response_schema = get_concept_extraction_output_schema()

    anthropic_schema = concept_provider._build_anthropic_input_schema(response_schema)  # noqa: SLF001

    assert (
        response_schema["properties"]["concepts"]["items"]["properties"][
            "concept_importance"
        ]["minimum"]
        == 1
    )
    assert (
        response_schema["properties"]["concepts"]["items"]["properties"][
            "concept_importance"
        ]["maximum"]
        == 10
    )
    assert "minimum" not in anthropic_schema["properties"]["concepts"]["items"][
        "properties"
    ]["concept_importance"]
    assert "maximum" not in anthropic_schema["properties"]["concepts"]["items"][
        "properties"
    ]["concept_importance"]
    assert anthropic_schema["properties"]["concepts"]["minItems"] == 1


def test_heuristic_provider_limits_generated_concepts_to_five() -> None:
    """Heuristic fallback should cap its generated concept list at five items."""
    provider = concept_provider.HeuristicConceptExtractionProvider(
        model_name="heuristic-v1",
    )
    request = concept_provider.CanonicalConceptExtractionRequest(
        session_id="session-many-concepts",
        operation_name="extract_gradeable_concepts",
        session_title="One / Two / Three / Four / Five / Six",
        session_topic="Alpha, Beta, Gamma, Delta, Epsilon, Zeta",
        session_transcript="Alpha connects to Beta and Gamma.",
        reasoning_level="medium",
        reasoning_type=concept_provider.DEFAULT_REASONING_TYPE,
        output_mode=concept_provider.DEFAULT_OUTPUT_MODE,
        response_schema=get_concept_extraction_output_schema(),
    )

    result = provider.extract_concepts(request, trace_id="trace-heuristic-limit")

    assert len(result["concepts"]) == concept_provider.MAX_HEURISTIC_CONCEPT_COUNT
