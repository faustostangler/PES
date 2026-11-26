"""Post-processing helpers for expanded conveyor stage transcripts.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl
- ADR-054: Unified Stage Transcript Envelope
- ADR-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion
- ADR-073: Sequential Conveyor Integration of Long and Wide Expander Stages
"""

from __future__ import annotations

from typing import Final

from cresmo.domain.entities.transcripts import StageTranscript
from cresmo.domain.exceptions import StageTranscriptStructureError
from cresmo.domain.value_objects import (
    EXTRA_INFO_HEADING_PATTERN,
    TITLE_H1_PATTERN,
    CandidateText,
    Content,
)

METADATA_KEY_PASSES_EXECUTED: Final[str] = "passes_executed"
DEFAULT_PASS_COUNT: Final[int] = 1
DEFAULT_TRANSCRIPT_TITLE: Final[str] = "Untitled Transcript"
EXTRA_INFO_HEADING: Final[str] = "### Extra Info"


def _resolve_effective_pass_count(candidate: CandidateText) -> int:
    """Resolve executed pass count from candidate metadata, defaulting to 1."""
    raw_passes = candidate.metadata.get(METADATA_KEY_PASSES_EXECUTED, DEFAULT_PASS_COUNT)
    if isinstance(raw_passes, int) and not isinstance(raw_passes, bool):
        return max(raw_passes, DEFAULT_PASS_COUNT)
    return DEFAULT_PASS_COUNT


def post_process_expanded_transcript(
    candidate: CandidateText,
    source: StageTranscript,
) -> StageTranscript:
    """Post-process expanded stage candidate into a validated StageTranscript aggregate.

    Conforms to ADR-028, ADR-031, ADR-038, ADR-054, ADR-057, ADR-073, and ADR-077.
    Strips H1 headers to preserve clean heading hierarchy, verifies the mandatory
    '### Extra Info' section is present in the unified body, propagates executed
    multi-pass counts from candidate metadata, and preserves the pure VO triad.
    """
    current_text = candidate.text.strip()

    title_match = TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        extracted_title = source.content.title or DEFAULT_TRANSCRIPT_TITLE
        body = current_text

    complementary_match = EXTRA_INFO_HEADING_PATTERN.search(body)
    if not complementary_match:
        raise StageTranscriptStructureError(
            "Missing mandatory complementary information section '### Extra Info'."
        )

    main_body = body[: complementary_match.start()].strip()
    complementary_info = body[complementary_match.end() :].strip()

    if not main_body:
        raise StageTranscriptStructureError("StageTranscript body cannot be empty.")
    if not complementary_info:
        raise StageTranscriptStructureError(
            "StageTranscript must contain a non-empty 'Extra Info' section."
        )

    full_body = f"{main_body}\n\n{EXTRA_INFO_HEADING}\n\n{complementary_info}"
    effective_pass_count = _resolve_effective_pass_count(candidate)

    return StageTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=str(extracted_title),
            text=full_body,
            session_id=source.content.session_id,
        ),
        pass_count=effective_pass_count,
        metadata=dict(source.metadata),
    )
