"""Deterministic fallback provider for structured extraction workflows."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.structured_provider import (
        CanonicalStructuredExtractionRequest,
        StructuredExtractionRepairContext,
    )

MAX_HEURISTIC_CONCEPT_COUNT = 5
MAX_HEURISTIC_ASSIGNMENT_REQUIREMENT_COUNT = 5
ASSIGNMENT_REQUIREMENT_TYPE_ORDER = [
    "mandatory_deliverable",
    "forbidden_project_type",
    "scoring_criterion",
    "evidence_expectation",
]


class HeuristicStructuredExtractionProvider:
    """Deterministic fallback provider for supported structured extraction operations."""

    provider_name = "heuristic"

    def __init__(self, *, model_name: str) -> None:
        """Store the configured internal model name for telemetry."""
        self.model_name = model_name

    def extract_structured_output(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Produce a structured payload from normalized evidence without an external LLM."""
        del trace_id
        if request.operation_name == "extract_assignment_requirements":
            return self._extract_assignment_requirements(
                request=request,
                repair_context=repair_context,
            )
        if request.operation_name != "extract_gradeable_concepts":
            raise RuntimeError(
                "Heuristic structured extraction does not support the requested operation."
            )
        return self._extract_concepts(
            request=request,
            repair_context=repair_context,
        )

    def extract_concepts(
        self,
        request: CanonicalStructuredExtractionRequest,
        *,
        trace_id: str,
        repair_context: StructuredExtractionRepairContext | None = None,
    ) -> dict[str, Any]:
        """Compatibility wrapper for older concept-specific callers."""
        return self.extract_structured_output(
            request,
            trace_id=trace_id,
            repair_context=repair_context,
        )

    def _extract_concepts(
        self,
        *,
        request: CanonicalStructuredExtractionRequest,
        repair_context: StructuredExtractionRepairContext | None,
    ) -> dict[str, Any]:
        """Produce a structured concept extraction payload from normalized evidence."""
        evidence_segments = _build_evidence_segments(request)
        if repair_context is not None:
            repaired_output = self._repair_previous_output(
                previous_output=repair_context.previous_output,
                evidence_segments=evidence_segments,
                session_title=request.session_title,
                session_topic=request.session_topic,
                max_concepts=self._get_max_concepts(request),
            )
            if repaired_output is not None:
                return repaired_output

        concepts = self._build_concepts(
            session_title=request.session_title,
            session_topic=request.session_topic,
            evidence_segments=evidence_segments,
            max_concepts=self._get_max_concepts(request),
        )
        return {"concepts": concepts}

    def _extract_assignment_requirements(
        self,
        *,
        request: CanonicalStructuredExtractionRequest,
        repair_context: StructuredExtractionRepairContext | None,
    ) -> dict[str, Any]:
        """Produce deterministic assignment requirements from stored assignment text."""
        if repair_context is not None:
            repaired_output = self._repair_previous_assignment_output(
                previous_output=repair_context.previous_output,
                assignment_sources=request.assignment_sources,
                max_assignment_requirements=self._get_max_assignment_requirements(request),
            )
            if repaired_output is not None:
                return repaired_output

        assignment_requirements: list[dict[str, Any]] = []
        for assignment_source in request.assignment_sources:
            assignment_requirements.append(
                {
                    "assignment_requirement_id": assignment_source.assignment_requirement_id,
                    "assignment_title": assignment_source.assignment_title,
                    "requirements": self._build_assignment_requirement_items(
                        assignment_title=assignment_source.assignment_title,
                        assignment_description=assignment_source.assignment_description,
                        max_assignment_requirements=self._get_max_assignment_requirements(
                            request
                        ),
                    ),
                }
            )
        return {"assignment_requirements": assignment_requirements}

    def _repair_previous_output(
        self,
        *,
        previous_output: dict[str, Any],
        evidence_segments: list[str],
        session_title: str,
        session_topic: str,
        max_concepts: int,
    ) -> dict[str, Any] | None:
        """Attempt to coerce a previously invalid payload into the required concept schema."""
        raw_concepts = previous_output.get("concepts")
        if not isinstance(raw_concepts, list) or not raw_concepts:
            return None

        repaired_concepts: list[dict[str, Any]] = []
        for index, raw_concept in enumerate(raw_concepts):
            if index >= max_concepts:
                break
            if isinstance(raw_concept, dict):
                concept_name = self._normalize_concept_name(
                    str(raw_concept.get("name") or raw_concept.get("concept") or "")
                )
                summary = str(raw_concept.get("summary") or "").strip()
                grading_reason = str(raw_concept.get("grading_reason") or "").strip()
                concept_importance = self._normalize_concept_importance(
                    raw_concept.get("concept_importance")
                )
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
                concept_importance = None
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
            if concept_importance is None:
                concept_importance = self._score_concept_importance(
                    concept_name=concept_name,
                    session_title=session_title,
                    session_topic=session_topic,
                    evidence_segments=evidence_segments,
                )

            repaired_concepts.append(
                {
                    "name": concept_name,
                    "summary": summary,
                    "grading_reason": grading_reason,
                    "concept_importance": concept_importance,
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
        max_concepts: int,
    ) -> list[dict[str, Any]]:
        """Derive a small set of gradeable concepts from session evidence."""
        concept_candidates = self._extract_candidates(
            session_title=session_title,
            session_topic=session_topic,
        )
        if not concept_candidates:
            concept_candidates = [
                self._normalize_concept_name(session_topic or session_title or "Core Concept")
            ]

        concepts: list[dict[str, Any]] = []
        for concept_name in concept_candidates[:max_concepts]:
            normalized_name = self._normalize_concept_name(concept_name)
            if not normalized_name:
                continue
            concept_importance = self._score_concept_importance(
                concept_name=normalized_name,
                session_title=session_title,
                session_topic=session_topic,
                evidence_segments=evidence_segments,
            )
            concepts.append(
                {
                    "name": normalized_name,
                    "summary": f"Covers the session idea of {normalized_name.lower()}.",
                    "grading_reason": (
                        f"Students can be graded on how well they apply {normalized_name.lower()}."
                    ),
                    "concept_importance": concept_importance,
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
                    f"Students can be graded on how well they apply {fallback_name.lower()}."
                ),
                "concept_importance": self._score_concept_importance(
                    concept_name=fallback_name,
                    session_title=session_title,
                    session_topic=session_topic,
                    evidence_segments=evidence_segments,
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

    def _score_concept_importance(
        self,
        *,
        concept_name: str,
        session_title: str,
        session_topic: str,
        evidence_segments: list[str],
    ) -> int:
        """Assign a deterministic 1-10 score based on concept prominence in the session."""
        normalized_name = concept_name.lower()
        score = 5
        if normalized_name in session_topic.lower():
            score += 2
        if normalized_name in session_title.lower():
            score += 1
        score += min(2, self._count_matching_segments(evidence_segments, normalized_name))
        return max(1, min(10, score))

    def _count_matching_segments(
        self,
        evidence_segments: list[str],
        normalized_name: str,
    ) -> int:
        """Count evidence segments that mention any concept term."""
        concept_terms = {term for term in normalized_name.split() if term}
        match_count = 0
        for segment in evidence_segments:
            lowered_segment = segment.lower()
            if concept_terms and any(term in lowered_segment for term in concept_terms):
                match_count += 1
        return match_count

    def _normalize_concept_importance(self, value: Any) -> int | None:
        """Coerce provider output into a valid concept importance score when possible."""
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            normalized_value = value
        elif isinstance(value, str) and value.strip().isdigit():
            normalized_value = int(value.strip())
        else:
            return None
        if 1 <= normalized_value <= 10:
            return normalized_value
        return None

    def _repair_previous_assignment_output(
        self,
        *,
        previous_output: dict[str, Any],
        assignment_sources: list[Any],
        max_assignment_requirements: int,
    ) -> dict[str, Any] | None:
        """Attempt to coerce a previously invalid assignment payload into the schema."""
        raw_assignments = previous_output.get("assignment_requirements")
        if not isinstance(raw_assignments, list):
            return None

        source_by_id = {
            source.assignment_requirement_id: source for source in assignment_sources
        }
        repaired_assignments: list[dict[str, Any]] = []
        for index, raw_assignment in enumerate(raw_assignments):
            if not isinstance(raw_assignment, dict):
                continue
            assignment_id = str(raw_assignment.get("assignment_requirement_id") or "").strip()
            assignment_title = str(raw_assignment.get("assignment_title") or "").strip()
            source = source_by_id.get(assignment_id)
            if source is None and index < len(assignment_sources):
                source = assignment_sources[index]
            if source is None:
                continue

            if not assignment_id:
                assignment_id = source.assignment_requirement_id
            if not assignment_title:
                assignment_title = source.assignment_title

            raw_requirements = raw_assignment.get("requirements")
            repaired_requirements = self._repair_assignment_requirement_items(
                raw_requirements=raw_requirements,
                assignment_title=source.assignment_title,
                assignment_description=source.assignment_description,
                max_assignment_requirements=max_assignment_requirements,
            )
            if not repaired_requirements:
                repaired_requirements = self._build_assignment_requirement_items(
                    assignment_title=source.assignment_title,
                    assignment_description=source.assignment_description,
                    max_assignment_requirements=max_assignment_requirements,
                )

            repaired_assignments.append(
                {
                    "assignment_requirement_id": assignment_id,
                    "assignment_title": assignment_title,
                    "requirements": repaired_requirements,
                }
            )

        if not repaired_assignments:
            return None
        return {"assignment_requirements": repaired_assignments}

    def _repair_assignment_requirement_items(
        self,
        *,
        raw_requirements: Any,
        assignment_title: str,
        assignment_description: str,
        max_assignment_requirements: int,
    ) -> list[dict[str, Any]]:
        """Repair one assignment's requirement items when the previous payload is close."""
        if not isinstance(raw_requirements, list) or not raw_requirements:
            return []

        repaired_requirements: list[dict[str, Any]] = []
        for raw_requirement in raw_requirements:
            if len(repaired_requirements) >= max_assignment_requirements:
                break
            if isinstance(raw_requirement, dict):
                requirement_type = self._normalize_requirement_type(
                    raw_requirement.get("requirement_type")
                )
                title = str(raw_requirement.get("title") or "").strip()
                summary = str(raw_requirement.get("summary") or "").strip()
                evidence = raw_requirement.get("evidence")
                if isinstance(evidence, list):
                    normalized_evidence = [
                        str(item).strip() for item in evidence if str(item).strip()
                    ]
                else:
                    normalized_evidence = []
            else:
                requirement_type = None
                title = str(raw_requirement).strip()
                summary = ""
                normalized_evidence = []

            if not title:
                title = self._build_requirement_title(assignment_description)
            if not summary:
                summary = "Requirement inferred directly from the stored assignment text."
            if not normalized_evidence:
                normalized_evidence = [self._select_assignment_evidence(assignment_description)]
            if requirement_type is None:
                requirement_type = self._infer_requirement_type(
                    title=title,
                    description=assignment_description,
                )

            repaired_requirements.append(
                {
                    "requirement_type": requirement_type,
                    "title": title,
                    "summary": summary,
                    "evidence": normalized_evidence,
                }
            )

        return repaired_requirements

    def _build_assignment_requirement_items(
        self,
        *,
        assignment_title: str,
        assignment_description: str,
        max_assignment_requirements: int,
    ) -> list[dict[str, Any]]:
        """Derive a few requirement items from assignment title and description."""
        description_sentences = _split_sentences(assignment_description)
        requirements: list[dict[str, Any]] = []
        for sentence in description_sentences:
            if len(requirements) >= max_assignment_requirements:
                break
            requirement_type = self._infer_requirement_type(
                title=assignment_title,
                description=sentence,
            )
            requirement = {
                "requirement_type": requirement_type,
                "title": self._build_requirement_title(sentence),
                "summary": self._build_requirement_summary(
                    requirement_type=requirement_type,
                    assignment_title=assignment_title,
                ),
                "evidence": [sentence],
            }
            if requirement not in requirements:
                requirements.append(requirement)

        if not requirements:
            requirements.append(
                {
                    "requirement_type": "mandatory_deliverable",
                    "title": self._build_requirement_title(assignment_description),
                    "summary": self._build_requirement_summary(
                        requirement_type="mandatory_deliverable",
                        assignment_title=assignment_title,
                    ),
                    "evidence": [self._select_assignment_evidence(assignment_description)],
                }
            )

        return requirements

    def _get_max_concepts(self, request: CanonicalStructuredExtractionRequest) -> int:
        """Return the concept cap used by the heuristic provider."""
        return request.max_concepts or MAX_HEURISTIC_CONCEPT_COUNT

    def _get_max_assignment_requirements(
        self,
        request: CanonicalStructuredExtractionRequest,
    ) -> int:
        """Return the assignment requirement cap used by the heuristic provider."""
        return (
            request.max_assignment_requirements
            or MAX_HEURISTIC_ASSIGNMENT_REQUIREMENT_COUNT
        )

    def _infer_requirement_type(self, *, title: str, description: str) -> str:
        """Infer the closest requirement category from one assignment text fragment."""
        normalized_text = f"{title} {description}".lower()
        if any(term in normalized_text for term in ("must not", "do not", "don't", "avoid")):
            return "forbidden_project_type"
        if any(term in normalized_text for term in ("score", "points", "criteria", "quality")):
            return "scoring_criterion"
        if any(term in normalized_text for term in ("evidence", "show", "demonstrate", "proof")):
            return "evidence_expectation"
        return "mandatory_deliverable"

    def _normalize_requirement_type(self, value: Any) -> str | None:
        """Coerce provider output into a valid assignment requirement type when possible."""
        if not isinstance(value, str):
            return None
        normalized_value = value.strip().lower()
        if normalized_value in ASSIGNMENT_REQUIREMENT_TYPE_ORDER:
            return normalized_value
        return None

    def _build_requirement_title(self, sentence: str) -> str:
        """Build a short stable requirement title from one sentence."""
        normalized = re.sub(r"\s+", " ", sentence.strip(" .:-"))
        if not normalized:
            return "Assignment requirement"
        words = normalized.split()
        return " ".join(words[:8])[:80]

    def _build_requirement_summary(
        self,
        *,
        requirement_type: str,
        assignment_title: str,
    ) -> str:
        """Build a deterministic summary for one extracted assignment requirement."""
        if requirement_type == "mandatory_deliverable":
            return (
                f"{assignment_title.strip() or 'This assignment'} "
                "requires the described deliverable."
            )
        if requirement_type == "forbidden_project_type":
            return "The assignment explicitly restricts this type of submission."
        if requirement_type == "scoring_criterion":
            return "The assignment description names this as a scoring or quality expectation."
        return "The assignment expects the student to provide evidence for this work."

    def _select_assignment_evidence(self, assignment_description: str) -> str:
        """Choose one stable evidence snippet from the assignment description."""
        sentences = _split_sentences(assignment_description)
        if sentences:
            return sentences[0]
        return assignment_description.strip() or "Assignment description not available."


def _build_evidence_segments(request: CanonicalStructuredExtractionRequest) -> list[str]:
    """Build provider evidence segments from the canonical concept extraction request."""
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


def _split_sentences(value: str) -> list[str]:
    """Split assignment text into compact sentence-like segments."""
    normalized = re.sub(r"\s+", " ", value.strip())
    if not normalized:
        return []

    parts = re.split(r"(?<=[.!?])\s+|;\s+|\n+", normalized)
    return [part.strip(" .") for part in parts if part.strip(" .")]


HeuristicConceptExtractionProvider = HeuristicStructuredExtractionProvider
