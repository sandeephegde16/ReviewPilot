"""Thin assignment requirement provider aliases over the shared structured provider stack."""

from app.structured_provider import (
    DEFAULT_OUTPUT_MODE,
    DEFAULT_REASONING_TYPE,
    OutputMode,
    PromptInputField,
    get_provider_reasoning_metadata,
)
from app.structured_provider import (
    CanonicalStructuredExtractionRequest as CanonicalAssignmentRequirementExtractionRequest,
)
from app.structured_provider import (
    StructuredExtractionProvider as AssignmentRequirementExtractionProvider,
)
from app.structured_provider import (
    StructuredExtractionRepairContext as AssignmentRequirementExtractionRepairContext,
)
from app.structured_provider import (
    build_structured_extraction_provider as build_assignment_requirement_extraction_provider,
)
from app.structured_provider import (
    select_structured_extraction_provider as select_assignment_requirement_extraction_provider,
)

__all__ = [
    "AssignmentRequirementExtractionProvider",
    "AssignmentRequirementExtractionRepairContext",
    "CanonicalAssignmentRequirementExtractionRequest",
    "DEFAULT_OUTPUT_MODE",
    "DEFAULT_REASONING_TYPE",
    "OutputMode",
    "PromptInputField",
    "build_assignment_requirement_extraction_provider",
    "get_provider_reasoning_metadata",
    "select_assignment_requirement_extraction_provider",
]
