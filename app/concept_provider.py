"""Provider interfaces and implementations for concept extraction."""

from __future__ import annotations

import json
import re
from typing import Any, Literal, Protocol
from urllib import error as urllib_error
from urllib import request as urllib_request

from pydantic import BaseModel, Field

from app.config import (
    get_anthropic_api_key,
    get_concept_extraction_model_name,
    get_concept_extraction_provider_name,
    get_gemini_api_key,
)
from app.schemas import ReasoningLevel

DEFAULT_REASONING_TYPE = "structured_extraction"
DEFAULT_OUTPUT_MODE = "json_schema_strict"
OutputMode = Literal["json_schema_strict"]
ANTHROPIC_MESSAGES_API_URL = "https://api.anthropic.com/v1/messages"
GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
)
DEFAULT_PROVIDER_MAX_TOKENS = 2048
HTTP_REQUEST_TIMEOUT_SECONDS = 60
ANTHROPIC_REASONING_BUDGET_BY_LEVEL = {
    "medium": 1024,
    "high": 1536,
}
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


class CanonicalConceptExtractionRequest(BaseModel):
    """Provider-agnostic request for structured gradeable concept extraction."""

    session_id: str = Field(description="Unique identifier for the session.")
    operation_name: str = Field(description="Canonical internal operation name.")
    session_title: str = Field(description="Stored title for the session.")
    session_topic: str = Field(description="Stored topic summary for the session.")
    session_transcript: str | None = Field(
        default=None,
        description="Normalized transcript text used for concept extraction.",
    )
    reasoning_level: ReasoningLevel = Field(description="Requested reasoning depth.")
    reasoning_type: str = Field(description="Canonical extraction mode.")
    output_mode: OutputMode = Field(description="Requested structured output mode.")
    response_schema: dict[str, Any] = Field(
        description="JSON schema defining the structured output required from the provider.",
    )


class ConceptExtractionRepairContext(BaseModel):
    """Repair metadata returned to the provider after schema validation fails."""

    schema_check_failed: bool = Field(
        default=True,
        description="Whether the previous model response failed schema validation.",
    )
    previous_output: dict[str, Any] = Field(
        description="Previous structured output sent back for repair.",
    )
    validation_errors: list[str] = Field(
        description="Schema validation errors returned to the provider on repair.",
    )


class ConceptExtractionProvider(Protocol):
    """Protocol implemented by any structured concept extraction provider."""

    provider_name: str
    model_name: str

    def extract_concepts(
        self,
        request: CanonicalConceptExtractionRequest,
        *,
        trace_id: str,
        repair_context: ConceptExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Return a JSON-like structured payload for concept extraction."""


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


class HeuristicConceptExtractionProvider:
    """Deterministic fallback provider for extracting gradeable concepts."""

    provider_name = "heuristic"

    def __init__(self, *, model_name: str) -> None:
        """Store the configured internal model name for telemetry."""
        self.model_name = model_name

    def extract_concepts(
        self,
        request: CanonicalConceptExtractionRequest,
        *,
        trace_id: str,
        repair_context: ConceptExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Produce a structured concept extraction payload from normalized evidence."""
        del trace_id
        evidence_segments = _build_evidence_segments(request)
        if repair_context is not None:
            repaired_output = self._repair_previous_output(
                previous_output=repair_context.previous_output,
                evidence_segments=evidence_segments,
                session_topic=request.session_topic,
            )
            if repaired_output is not None:
                return repaired_output

        concepts = self._build_concepts(
            session_title=request.session_title,
            session_topic=request.session_topic,
            evidence_segments=evidence_segments,
        )
        return {"concepts": concepts}

    def _repair_previous_output(
        self,
        *,
        previous_output: dict[str, Any],
        evidence_segments: list[str],
        session_topic: str,
    ) -> dict[str, Any] | None:
        """Attempt to coerce a previously invalid payload into the required schema."""
        raw_concepts = previous_output.get("concepts")
        if not isinstance(raw_concepts, list) or not raw_concepts:
            return None

        repaired_concepts: list[dict[str, Any]] = []
        for index, raw_concept in enumerate(raw_concepts):
            if isinstance(raw_concept, dict):
                concept_name = self._normalize_concept_name(
                    str(raw_concept.get("name") or raw_concept.get("concept") or "")
                )
                summary = str(raw_concept.get("summary") or "").strip()
                grading_reason = str(raw_concept.get("grading_reason") or "").strip()
                evidence = raw_concept.get("evidence")
                if isinstance(evidence, list):
                    normalized_evidence = [
                        str(item).strip() for item in evidence if str(item).strip()
                    ]
                else:
                    normalized_evidence = []
            else:
                concept_name = self._normalize_concept_name(str(raw_concept))
                summary = ""
                grading_reason = ""
                normalized_evidence = []

            if not concept_name:
                concept_name = self._normalize_concept_name(session_topic) or (
                    f"Concept {index + 1}"
                )
            if not summary:
                summary = f"Highlights the session focus on {concept_name.lower()}."
            if not grading_reason:
                grading_reason = (
                    f"Understanding {concept_name.lower()} is directly relevant for grading."
                )
            if not normalized_evidence:
                normalized_evidence = [self._select_evidence(evidence_segments, concept_name)]

            repaired_concepts.append(
                {
                    "name": concept_name,
                    "summary": summary,
                    "grading_reason": grading_reason,
                    "evidence": normalized_evidence,
                }
            )

        return {"concepts": repaired_concepts}

    def _build_concepts(
        self,
        *,
        session_title: str,
        session_topic: str,
        evidence_segments: list[str],
    ) -> list[dict[str, Any]]:
        """Derive a small set of gradeable concepts from session evidence."""
        concept_candidates = self._extract_candidates(
            session_title=session_title,
            session_topic=session_topic,
        )
        if not concept_candidates:
            concept_candidates = [
                self._normalize_concept_name(
                    session_topic or session_title or "Core Concept"
                )
            ]

        concepts: list[dict[str, Any]] = []
        for concept_name in concept_candidates[:3]:
            normalized_name = self._normalize_concept_name(concept_name)
            if not normalized_name:
                continue
            concepts.append(
                {
                    "name": normalized_name,
                    "summary": f"Covers the session idea of {normalized_name.lower()}.",
                    "grading_reason": (
                        f"Students can be graded on how well they apply "
                        f"{normalized_name.lower()}."
                    ),
                    "evidence": [self._select_evidence(evidence_segments, normalized_name)],
                }
            )

        if concepts:
            return concepts

        fallback_name = self._normalize_concept_name(
            session_topic or session_title or "Core Concept"
        )
        return [
            {
                "name": fallback_name,
                "summary": f"Covers the session idea of {fallback_name.lower()}.",
                "grading_reason": (
                    f"Students can be graded on how well they apply "
                    f"{fallback_name.lower()}."
                ),
                "evidence": [self._select_evidence(evidence_segments, fallback_name)],
            }
        ]

    def _extract_candidates(self, *, session_title: str, session_topic: str) -> list[str]:
        """Extract a few concept candidates from the title and topic text."""
        raw_candidates = [session_topic, session_title]
        candidates: list[str] = []
        for value in raw_candidates:
            for part in re.split(r",| and |/|;|:", value):
                normalized = self._normalize_concept_name(part)
                if normalized and normalized not in candidates:
                    candidates.append(normalized)
        return candidates

    def _normalize_concept_name(self, value: str) -> str:
        """Normalize a candidate concept label into a stable short phrase."""
        normalized = re.sub(r"\s+", " ", value.strip(" .:-"))
        if not normalized:
            return ""
        if len(normalized) <= 2:
            return ""
        return normalized[:80]

    def _select_evidence(self, evidence_segments: list[str], concept_name: str) -> str:
        """Choose one evidence snippet that best matches the concept name."""
        concept_terms = {term.lower() for term in concept_name.split()}
        for segment in evidence_segments:
            lowered_segment = segment.lower()
            if concept_terms and any(term in lowered_segment for term in concept_terms):
                return segment
        return evidence_segments[0]


class AnthropicConceptExtractionProvider:
    """Anthropic-backed provider using forced tool use for structured output."""

    provider_name = "anthropic"

    def __init__(self, *, model_name: str, api_key: str) -> None:
        """Store the configured Anthropic model and API key."""
        self.model_name = model_name
        self.api_key = api_key

    def extract_concepts(
        self,
        request: CanonicalConceptExtractionRequest,
        *,
        trace_id: str,
        repair_context: ConceptExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Call Anthropic Messages API and extract the forced tool input payload."""
        del trace_id
        response_payload = _post_json(
            provider_name=self.provider_name,
            url=ANTHROPIC_MESSAGES_API_URL,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            body=_build_anthropic_request_body(
                request=request,
                model_name=self.model_name,
                repair_context=repair_context,
            ),
        )
        return _extract_anthropic_tool_input(
            response_payload=response_payload,
            operation_name=request.operation_name,
        )


class GeminiConceptExtractionProvider:
    """Gemini-backed provider using native structured JSON schema output."""

    provider_name = "gemini"

    def __init__(self, *, model_name: str, api_key: str) -> None:
        """Store the configured Gemini model and API key."""
        self.model_name = model_name
        self.api_key = api_key

    def extract_concepts(
        self,
        request: CanonicalConceptExtractionRequest,
        *,
        trace_id: str,
        repair_context: ConceptExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Call Gemini generateContent API and parse the structured JSON response."""
        del trace_id
        response_payload = _post_json(
            provider_name=self.provider_name,
            url=GEMINI_GENERATE_CONTENT_API_URL_TEMPLATE.format(model_name=self.model_name),
            headers={
                "content-type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            body=_build_gemini_request_body(
                request=request,
                model_name=self.model_name,
                repair_context=repair_context,
            ),
        )
        return _extract_gemini_structured_output(response_payload=response_payload)


def select_concept_extraction_provider(
    *,
    reasoning_level: ReasoningLevel,
) -> ConceptExtractionProvider:
    """Choose a provider for concept extraction based on the configured routing policy."""
    del reasoning_level
    provider_name = get_concept_extraction_provider_name()
    return build_concept_extraction_provider(
        provider_name=provider_name,
        model_name=get_concept_extraction_model_name(provider_name),
    )


def build_concept_extraction_provider(
    *,
    provider_name: str,
    model_name: str,
) -> ConceptExtractionProvider:
    """Build a concept extraction provider for one explicit provider/model pair."""
    if provider_name == "heuristic":
        return HeuristicConceptExtractionProvider(
            model_name=model_name,
        )
    if provider_name == "anthropic":
        anthropic_api_key = get_anthropic_api_key()
        if anthropic_api_key is None:
            raise LookupError("Anthropic provider is selected but no API key is configured.")
        return AnthropicConceptExtractionProvider(
            model_name=model_name,
            api_key=anthropic_api_key,
        )
    if provider_name == "gemini":
        gemini_api_key = get_gemini_api_key()
        if gemini_api_key is None:
            raise LookupError("Gemini provider is selected but no API key is configured.")
        return GeminiConceptExtractionProvider(
            model_name=model_name,
            api_key=gemini_api_key,
        )

    raise LookupError(
        "No concept extraction provider is available for the current configuration."
    )


def _build_evidence_segments(
    request: CanonicalConceptExtractionRequest,
) -> list[str]:
    """Build provider evidence segments from the canonical extraction request."""
    evidence_segments = [
        f"Session title: {request.session_title}",
        f"Session topic: {request.session_topic}",
    ]
    if request.session_transcript:
        evidence_segments.extend(
            segment.strip()
            for segment in request.session_transcript.splitlines()
            if segment.strip()
        )
    return evidence_segments


def _build_anthropic_request_body(
    *,
    request: CanonicalConceptExtractionRequest,
    model_name: str,
    repair_context: ConceptExtractionRepairContext | None,
) -> dict[str, Any]:
    """Build the Anthropic Messages API request for structured concept extraction."""
    request_body = {
        "model": model_name,
        "max_tokens": DEFAULT_PROVIDER_MAX_TOKENS,
        "temperature": 0,
        "system": _build_provider_system_prompt(request),
        "messages": [
            {
                "role": "user",
                "content": _build_text_content_blocks(
                    _build_provider_user_prompt(
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
                "input_schema": request.response_schema,
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


def _build_gemini_request_body(
    *,
    request: CanonicalConceptExtractionRequest,
    model_name: str,
    repair_context: ConceptExtractionRepairContext | None,
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


def _build_provider_prompt(
    *,
    request: CanonicalConceptExtractionRequest,
    repair_context: ConceptExtractionRepairContext | None,
) -> str:
    """Build one provider-neutral prompt describing the extraction task and evidence."""
    return "\n\n".join(
        [
            _build_provider_system_prompt(request),
            _build_provider_user_prompt(
                request=request,
                repair_context=repair_context,
            ),
        ]
    )


def _build_provider_system_prompt(request: CanonicalConceptExtractionRequest) -> str:
    """Build stable task instructions shared across external providers."""
    return "\n".join(
        [
            f"Operation: {request.operation_name}",
            f"Reasoning level: {request.reasoning_level}",
            f"Reasoning type: {request.reasoning_type}",
            "Extract the most gradeable concepts from the session evidence.",
            "A gradeable concept must be specific enough to evaluate in student work.",
            "Use only concepts that are directly supported by the session evidence.",
            "Do not invent evidence or concepts that are absent from the session.",
        ]
    )


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


def _anthropic_model_supports_thinking(model_name: str) -> bool:
    """Return whether the configured Anthropic model should receive thinking controls."""
    if model_name.startswith("claude-opus-4-7"):
        return False
    return True


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


def _build_provider_user_prompt(
    *,
    request: CanonicalConceptExtractionRequest,
    repair_context: ConceptExtractionRepairContext | None,
) -> str:
    """Build the user prompt containing session evidence and optional repair context."""
    prompt_sections = [
        "Session evidence:",
        f"Session ID: {request.session_id}",
        f"Session title: {request.session_title}",
        f"Session topic: {request.session_topic}",
        "Session transcript:",
        request.session_transcript or "(Not available. Use session title and topic only.)",
    ]
    if repair_context is None:
        return "\n".join(prompt_sections)

    prompt_sections.extend(
        [
            "",
            (
                "Schema check failed on the previous output. Repair the response using "
                "the same schema."
            ),
            f"Validation errors: {'; '.join(repair_context.validation_errors)}",
            "Previous output:",
            json.dumps(repair_context.previous_output, ensure_ascii=True),
        ]
    )
    return "\n".join(prompt_sections)


def _build_tool_description() -> str:
    """Describe the structured extraction tool used by Anthropic tool forcing."""
    return (
        "Return the final gradeable concepts as structured JSON that matches the provided "
        "schema. Each concept must include a name, summary, grading reason, and evidence."
    )


def _build_text_content_blocks(text: str) -> list[dict[str, str]]:
    """Wrap plain text into the content-block shape expected by Anthropic Messages API."""
    return [{"type": "text", "text": text}]


def _extract_anthropic_tool_input(
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


def _extract_gemini_structured_output(
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


def _post_json(
    *,
    provider_name: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any],
) -> dict[str, Any]:
    """POST a JSON body and return the decoded JSON response."""
    encoded_body = json.dumps(body).encode("utf-8")
    request = urllib_request.Request(
        url=url,
        data=encoded_body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib_request.urlopen(
            request,
            timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
        ) as response:
            raw_response = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{provider_name} API request failed with status {exc.code}: {error_body}"
        ) from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"{provider_name} API request failed: {exc.reason}") from exc

    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{provider_name} API returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{provider_name} API returned a non-object JSON payload.")
    return payload
