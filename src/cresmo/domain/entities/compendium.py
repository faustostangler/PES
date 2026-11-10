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
from cresmo.domain.value_objects import (
    Channel,
    Content,
    ContentId,
    MediaProvenance,
)

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*###\s+Extra\s+Info\s*$",
    re.MULTILINE,
)


def post_process_enriched_compendium(
    candidate: Any,
    source: Any,
    pass_count: int = 1,
) -> StageTranscript:
    """Post-process candidate text into a validated StageTranscript domain aggregate.

    Conforms to ADR-028, ADR-031, ADR-038, ADR-054, and ADR-057.
    Strips H1 headers to preserve clean heading hierarchy, segregates the main continuous
    prose body from the mandatory '### Extra Info' section, and maps
    the pure Value Object triad from the source transcript.
    """
    candidate_text = getattr(candidate, "text", candidate)
    current_text = str(candidate_text).strip()

    title_match = _TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = _TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        source_content = getattr(source, "content", None)
        extracted_title = (
            getattr(source_content, "title", None)
            or getattr(source, "title", None)
            or "Untitled Compendium"
        )
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

    # Resolve triad attributes from source
    source_channel = getattr(source, "channel", None)
    source_provenance = getattr(source, "provenance", None)
    source_content = getattr(source, "content", None)

    channel = (
        source_channel
        if isinstance(source_channel, Channel)
        else Channel(
            name=getattr(source, "channel_name", "Unknown Channel"),
            id=getattr(source, "channel_id", None),
            category=getattr(source, "channel_category", ""),
        )
    )

    provenance = (
        source_provenance
        if isinstance(source_provenance, MediaProvenance)
        else MediaProvenance.create(
            url=getattr(source, "source_url", ""),
            description=getattr(source, "video_description", ""),
            publication_date=getattr(source, "publication_date", None),
        )
    )

    content_id = (
        getattr(source_content, "id", None)
        or getattr(source, "content_id", None)
        or ContentId("unknown")
    )
    if isinstance(content_id, str):
        content_id = ContentId.from_string(content_id)

    return StageTranscript(
        channel=channel,
        provenance=provenance,
        content=Content(
            id=content_id,
            title=str(getattr(extracted_title, "value", extracted_title)),
            body=main_body,
        ),
        complementary_info=complementary_info,
        pass_count=max(pass_count, 1),
    )
