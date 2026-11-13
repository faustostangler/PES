"""Post-processing helpers for enriched stage compendiums.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl
- ADR-054: Unified Stage Transcript Envelope
- ADR-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion
"""

from __future__ import annotations

import re
from typing import Any

from cresmo.domain.entities.transcripts import StageTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import Content

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*###\s+Extra\s+Info\s*$",
    re.MULTILINE,
)


def post_process_enriched_compendium(
    candidate: Any,
    source: StageTranscript,
    pass_count: int = 1,
) -> StageTranscript:
    """Post-process candidate text into a validated StageTranscript domain aggregate.

    Conforms to ADR-028, ADR-031, ADR-038, ADR-054, and ADR-057.
    Strips H1 headers to preserve clean heading hierarchy, verifies the mandatory
    '### Extra Info' section is present in the unified body, and maps
    the pure Value Object triad from the source transcript.
    """
    candidate_text = getattr(candidate, "text", candidate)
    current_text = str(candidate_text).strip()

    title_match = _TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = _TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        extracted_title = source.content.title or "Untitled Compendium"
        body = current_text

    complementary_match = _COMPLEMENTARY_REGEX.search(body)
    if not complementary_match:
        raise CompendiumStructureError(
            "Missing mandatory complementary information section '### Extra Info'."
        )

    main_body = body[: complementary_match.start()].strip()
    complementary_info = body[complementary_match.end() :].strip()

    if not main_body:
        raise CompendiumStructureError("StageTranscript body cannot be empty.")
    if not complementary_info:
        raise CompendiumStructureError(
            "StageTranscript must contain a non-empty 'Extra Info' section."
        )

    full_body = f"{main_body}\n\n### Extra Info\n\n{complementary_info}"

    return StageTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=str(extracted_title),
            text=full_body,
            session_id=source.content.session_id,
        ),
        pass_count=max(pass_count, 1),
        metadata=dict(source.metadata),
    )
