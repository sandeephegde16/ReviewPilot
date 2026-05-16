"""Request shaping and response parsing for external structured extraction providers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from app.schemas import ReasoningLevel

if TYPE_CHECKING:
    from app.structured_provider import (
        CanonicalStructuredExtractionRequest,
        StructuredExtractionRepairContext,
    )

ANTHROPIC_MESSAGES_API_URL = "https://api.anthropic.com/v1/messages"
GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
)
DEFAULT_PROVIDER_MAX_TOKENS = 2048
GEMINI_25_REASONING_BUDGET_BY_LEVEL = {
    "low": 0,
    "medium": 1024,
    "high": 2048,
}
GEMINI_3_REASONING_LEVEL_BY_LEVEL = {
    "low": "low",
    "medium": "medium",
    "high": "high",
}


class ProviderReasoningMetadata(BaseModel):
    """Telemetry-friendly description of native reasoning controls for one provider call."""

    provider_reasoning_level: str | int | None = Field(
        default=None,
        description="Native provider reasoning level or budget sent on the request.",
    )
    provider_reasoning_type: str | None = Field(
        default=None,
        description="Native provider reasoning type when the API exposes one.",
    )


def build_anthropic_request_body(
    *,
    request: CanonicalStructuredExtractionRequest,
    model_name: str,
    repair_context: StructuredExtractionRepairContext | None,
) -> dict[str, Any]:
    """Build the Anthropic Messages API request for one structured extraction."""
    request_body = {
        "model": model_name,
        "max_tokens": DEFAULT_PROVIDER_MAX_TOKENS,
        "temperature": 0,
        "system": _build_provider_system_prompt(request),
        "messages": [
            {
                "role": "user",
                "content": _build_text_content_blocks(
                    build_provider_user_prompt(
                        request=request,
                        repair_context=repair_context,
                    )
                ),
            }
        ],
        "tools": [
            {
                "name": request.operation_name,
                "description": _build_tool_description(),
                "strict": True,
                "input_schema": build_anthropic_input_schema(request.response_schema),
            }
        ],
        "tool_choice": {
            "type": "tool",
            "name": request.operation_name,
            "disable_parallel_tool_use": True,
        },
    }
    thinking_config = _build_anthropic_thinking_config(
        model_name=model_name,
        reasoning_level=request.reasoning_level,
    )
    if thinking_config is not None:
        request_body["thinking"] = thinking_config
    return request_body


def build_anthropic_input_schema(response_schema: dict[str, Any]) -> dict[str, Any]:
    """Remove JSON Schema fields that Anthropic tool schemas reject."""
    return _strip_anthropic_unsupported_schema_fields(response_schema)


def build_gemini_request_body(
    *,
    request: CanonicalStructuredExtractionRequest,
    model_name: str,
    repair_context: StructuredExtractionRepairContext | None,
) -> dict[str, Any]:
    """Build the Gemini generateContent request for structured JSON output."""
    return {
        "contents": [
            {
                "parts": [
                    {
                        "text": _build_provider_prompt(
                            request=request,
                            repair_context=repair_context,
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "thinkingConfig": _build_gemini_thinking_config(
                model_name=model_name,
                reasoning_level=request.reasoning_level,
            ),
            "responseMimeType": "application/json",
            "responseJsonSchema": request.response_schema,
        },
    }


def build_provider_user_prompt(
    *,
    request: CanonicalStructuredExtractionRequest,
    repair_context: StructuredExtractionRepairContext | None,
) -> str:
    """Build the user prompt containing labeled evidence and optional repair context."""
    prompt_sections = [f"{request.prompt_subject}:"]
    for prompt_input_field in request.prompt_input_fields:
        prompt_sections.extend([f"{prompt_input_field.label}:", prompt_input_field.value])
    if repair_context is None:
        return "\n".join(prompt_sections)

    prompt_sections.extend(
        [
            "",
            (
                "Schema check failed on the previous output. Repair the response using "
                "the same schema."
            ),
            *request.repair_guidance_lines,
            "Return a root JSON object in this shape:",
            _build_repair_output_example(request.repair_output_example),
            f"Validation errors: {'; '.join(repair_context.validation_errors)}",
            "Previous output:",
            json.dumps(repair_context.previous_output, ensure_ascii=True),
        ]
    )
    return "\n".join(prompt_sections)


def get_provider_reasoning_metadata(
    *,
    provider_name: str,
    model_name: str,
    reasoning_level: ReasoningLevel,
) -> ProviderReasoningMetadata:
    """Describe the native reasoning controls that will be sent to a provider."""
    if provider_name == "anthropic":
        return _build_anthropic_reasoning_metadata(
            model_name=model_name,
            reasoning_level=reasoning_level,
        )
    if provider_name == "gemini":
        return _build_gemini_reasoning_metadata(
            model_name=model_name,
            reasoning_level=reasoning_level,
        )
    return ProviderReasoningMetadata()


def extract_anthropic_tool_input(
    *,
    response_payload: dict[str, Any],
    operation_name: str,
) -> dict[str, Any]:
    """Extract the structured tool input emitted by Anthropic forced tool use."""
    content_blocks = response_payload.get("content")
    if not isinstance(content_blocks, list):
        raise RuntimeError("Anthropic response did not include any content blocks.")

    for block in content_blocks:
        if (
            isinstance(block, dict)
            and block.get("type") == "tool_use"
            and block.get("name") == operation_name
        ):
            tool_input = block.get("input")
            if isinstance(tool_input, dict):
                return tool_input
            raise RuntimeError("Anthropic tool response did not include a JSON object input.")

    raise RuntimeError("Anthropic response did not include the expected tool_use block.")


def extract_gemini_structured_output(
    *,
    response_payload: dict[str, Any],
) -> dict[str, Any]:
    """Parse the JSON text returned by Gemini structured-output generation."""
    candidates = response_payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("Gemini response did not include any candidates.")

    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        raise RuntimeError("Gemini response candidate payload is invalid.")
    candidate_content = first_candidate.get("content")
    if not isinstance(candidate_content, dict):
        raise RuntimeError("Gemini response did not include candidate content.")
    parts = candidate_content.get("parts")
    if not isinstance(parts, list) or not parts:
        raise RuntimeError("Gemini response did not include any content parts.")

    response_text = "".join(
        part["text"]
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ).strip()
    if not response_text:
        raise RuntimeError("Gemini response did not include structured JSON text.")

    try:
        parsed_output = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini structured output was not valid JSON.") from exc
    if not isinstance(parsed_output, dict):
        raise RuntimeError("Gemini structured output must be a JSON object.")
    return parsed_output


def _build_provider_prompt(
    *,
    request: CanonicalStructuredExtractionRequest,
    repair_context: StructuredExtractionRepairContext | None,
) -> str:
    """Build one provider-neutral prompt describing the extraction task and evidence."""
    return "\n\n".join(
        [
            _build_provider_system_prompt(request),
            build_provider_user_prompt(
                request=request,
                repair_context=repair_context,
            ),
        ]
    )


def _build_provider_system_prompt(request: CanonicalStructuredExtractionRequest) -> str:
    """Build stable task instructions shared across external providers."""
    return "\n".join(
        [
            f"Operation: {request.operation_name}",
            f"Reasoning level: {request.reasoning_level}",
            f"Reasoning type: {request.reasoning_type}",
            *request.system_instruction_lines,
            *_build_output_limit_lines(request),
        ]
    )


def _build_output_limit_lines(request: CanonicalStructuredExtractionRequest) -> list[str]:
    """Return shared prompt lines that communicate request-specific output caps."""
    output_limit_lines: list[str] = []
    if request.max_concepts is not None:
        output_limit_lines.append(f"Return no more than {request.max_concepts} concepts.")
    if request.max_assignment_requirements is not None:
        output_limit_lines.append(
            "For each assignment record, return no more than "
            f"{request.max_assignment_requirements} extracted requirements."
        )
    return output_limit_lines


def _strip_anthropic_unsupported_schema_fields(node: Any) -> Any:
    """Recursively drop schema keywords unsupported by Anthropic tool validation."""
    if isinstance(node, list):
        return [_strip_anthropic_unsupported_schema_fields(item) for item in node]
    if not isinstance(node, dict):
        return node

    normalized_node = {
        key: _strip_anthropic_unsupported_schema_fields(value) for key, value in node.items()
    }
    if normalized_node.get("type") == "integer":
        normalized_node.pop("minimum", None)
        normalized_node.pop("maximum", None)
        normalized_node.pop("exclusiveMinimum", None)
        normalized_node.pop("exclusiveMaximum", None)
    if normalized_node.get("type") == "array":
        normalized_node.pop("maxItems", None)
    return normalized_node


def _build_anthropic_thinking_config(
    *,
    model_name: str,
    reasoning_level: ReasoningLevel,
) -> dict[str, Any] | None:
    """Map canonical reasoning level onto Anthropic's native thinking controls."""
    metadata = _build_anthropic_reasoning_metadata(
        model_name=model_name,
        reasoning_level=reasoning_level,
    )
    if metadata.provider_reasoning_type == "enabled":
        return {
            "type": "enabled",
            "budget_tokens": metadata.provider_reasoning_level,
            "display": "omitted",
        }
    return None


def _build_anthropic_reasoning_metadata(
    *,
    model_name: str,
    reasoning_level: ReasoningLevel,
) -> ProviderReasoningMetadata:
    """Describe Anthropic thinking controls for the selected model and reasoning level."""
    del model_name, reasoning_level
    # Forced tool choice is incompatible with Anthropic extended thinking.
    return ProviderReasoningMetadata(
        provider_reasoning_level=None,
        provider_reasoning_type=None,
    )


def _build_gemini_thinking_config(
    *,
    model_name: str,
    reasoning_level: ReasoningLevel,
) -> dict[str, Any]:
    """Map canonical reasoning level onto Gemini's native thinking controls."""
    metadata = _build_gemini_reasoning_metadata(
        model_name=model_name,
        reasoning_level=reasoning_level,
    )
    thinking_config: dict[str, Any] = {"includeThoughts": False}
    if isinstance(metadata.provider_reasoning_level, str):
        thinking_config["thinkingLevel"] = metadata.provider_reasoning_level
        return thinking_config
    if isinstance(metadata.provider_reasoning_level, int):
        thinking_config["thinkingBudget"] = metadata.provider_reasoning_level
        return thinking_config
    return thinking_config


def _build_gemini_reasoning_metadata(
    *,
    model_name: str,
    reasoning_level: ReasoningLevel,
) -> ProviderReasoningMetadata:
    """Describe Gemini thinking controls for the selected model and reasoning level."""
    if model_name.startswith("gemini-3"):
        return ProviderReasoningMetadata(
            provider_reasoning_level=GEMINI_3_REASONING_LEVEL_BY_LEVEL[reasoning_level],
            provider_reasoning_type=None,
        )
    return ProviderReasoningMetadata(
        provider_reasoning_level=GEMINI_25_REASONING_BUDGET_BY_LEVEL[reasoning_level],
        provider_reasoning_type=None,
    )


def _build_tool_description() -> str:
    """Describe the structured extraction tool used by Anthropic tool forcing."""
    return (
        "Return the final structured extraction result as JSON that matches the provided "
        "schema and is fully supported by the evidence."
    )


def _build_repair_output_example(example: dict[str, Any]) -> str:
    """Return a compact valid output example for schema-repair prompts."""
    return json.dumps(example, ensure_ascii=True)


def _build_text_content_blocks(text: str) -> list[dict[str, str]]:
    """Wrap plain text into the content-block shape expected by Anthropic Messages API."""
    return [{"type": "text", "text": text}]
