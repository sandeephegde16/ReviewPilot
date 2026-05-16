"""Helpers for normalizing stored session transcripts into evidence segments."""

from __future__ import annotations

import json
import re
from typing import Any

MAX_TRANSCRIPT_SEGMENT_LENGTH = 240
TIMESTAMP_ARTIFACT_PATTERN = re.compile(
    r"\b\d+:\d+\d*\s*(?:minutes?,\s*\d+\s*seconds|minute,\s*\d+\s*seconds|seconds)"
    r"(?=[A-Za-z]|\s|$|[.,!?])",
    re.IGNORECASE,
)


def parse_transcript_segments(transcript_payload: str | None) -> list[str]:
    """Parse a stored transcript payload into a list of text evidence segments."""
    if transcript_payload is None or not transcript_payload.strip():
        return []

    try:
        parsed_payload = json.loads(transcript_payload)
    except json.JSONDecodeError:
        return _normalize_text_segments([transcript_payload])

    extracted_segments = _collect_text_segments(parsed_payload)
    if not extracted_segments:
        return _normalize_text_segments([transcript_payload])

    return _normalize_text_segments(extracted_segments)


def normalize_transcript_text(transcript_payload: str | None) -> str | None:
    """Return a normalized transcript text string, or None when no usable text exists."""
    segments = parse_transcript_segments(transcript_payload)
    if not segments:
        return None
    return "\n".join(segments)


def _normalize_text_segments(segments: list[str]) -> list[str]:
    """Normalize transcript strings into deduplicated evidence segments."""
    normalized_segments: list[str] = []
    for segment in segments:
        cleaned_segment = _clean_transcript_segment(segment)
        for chunk in _split_segment_chunks(cleaned_segment):
            if chunk and chunk not in normalized_segments:
                normalized_segments.append(chunk)
    return normalized_segments


def _collect_text_segments(value: Any) -> list[str]:
    """Recursively collect human-readable strings from a JSON transcript payload."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        segments: list[str] = []
        for item in value:
            segments.extend(_collect_text_segments(item))
        return segments
    if isinstance(value, dict):
        preferred_keys = ("text", "content", "message", "summary", "transcript")
        segments: list[str] = []
        for key in preferred_keys:
            if key in value:
                segments.extend(_collect_text_segments(value[key]))
        if segments:
            return segments
        for item in value.values():
            segments.extend(_collect_text_segments(item))
        return segments
    return []


def _clean_transcript_segment(segment: str) -> str:
    """Remove timestamp noise and normalize whitespace inside a transcript segment."""
    without_timestamps = TIMESTAMP_ARTIFACT_PATTERN.sub(" ", segment)
    return re.sub(r"\s+", " ", without_timestamps.strip())


def _split_segment_chunks(segment: str) -> list[str]:
    """Split a cleaned transcript segment into bounded chunks for downstream prompts."""
    if not segment:
        return []

    sentence_candidates = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", segment)
        if part.strip()
    ]
    if not sentence_candidates:
        sentence_candidates = [segment]

    chunks: list[str] = []
    current_chunk = ""
    for candidate in sentence_candidates:
        if len(candidate) > MAX_TRANSCRIPT_SEGMENT_LENGTH:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            chunks.extend(_split_long_segment(candidate))
            continue

        proposed_chunk = (
            candidate if not current_chunk else f"{current_chunk} {candidate}"
        )
        if len(proposed_chunk) <= MAX_TRANSCRIPT_SEGMENT_LENGTH:
            current_chunk = proposed_chunk
            continue

        chunks.append(current_chunk)
        current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def _split_long_segment(segment: str) -> list[str]:
    """Split a very long transcript span into word-bounded chunks."""
    words = segment.split()
    if not words:
        return []

    chunks: list[str] = []
    current_chunk = words[0]
    for word in words[1:]:
        proposed_chunk = f"{current_chunk} {word}"
        if len(proposed_chunk) <= MAX_TRANSCRIPT_SEGMENT_LENGTH:
            current_chunk = proposed_chunk
            continue
        chunks.append(current_chunk)
        current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)
    return chunks
