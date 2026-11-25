"""Monomorphic StageTranscript domain aggregate and pure Value Object triad composition.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-019: SOTA-KISS Nomenclature & Value Objects
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-034: Algorithmic (ID-ID) and Cognitive (TXT-TXT) Parity Standard
- ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl
- ADR-054: Unified Stage Transcript Envelope
- ADR-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from cresmo.domain.exceptions import (
    DomainValidationError,
    StageTranscriptStructureError,
)
from cresmo.domain.value_objects import (
    TITLE_H1_PATTERN,
    CandidateText,
    Channel,
    Content,
    MediaProvenance,
)

# Matches any accidental complementary information section headers
_ACCIDENTAL_COMPLEMENTARY_HEADING_PATTERN = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Extra\s+Info|Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class StageTranscript:
    """Monomorphic domain envelope for transcripts across all pipeline stages.

    Conforms to ADR-038 (Pure Value Object Triad Composition), ADR-054, and ADR-057.
    Composed strictly of the pure Value Object triad without duplicate property aliases:
    1. channel: Channel (Origin / Creator - id, name, category, url)
    2. provenance: MediaProvenance (Acquisition & Temporal Context - url, description, publication_date)
    3. content: Content (Textual Artifact & Payload - id, title, text)
    4. pass_count: int | None (Number of enrichment passes executed, >= 1 when present)
    5. metadata: dict[str, Any] (Stage Provenance & Lineage)
    """

    channel: Channel
    provenance: MediaProvenance
    content: Content
    pass_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforce domain invariants and type validity on pure triad components."""
        if not isinstance(self.channel, Channel):
            raise TypeError(
                f"channel must be an instance of Channel, got {type(self.channel).__name__}"
            )
        if not isinstance(self.provenance, MediaProvenance):
            raise TypeError(
                f"provenance must be an instance of MediaProvenance, got {type(self.provenance).__name__}"
            )
        if not isinstance(self.content, Content):
            raise TypeError(
                f"content must be an instance of Content, got {type(self.content).__name__}"
            )

        if not self.content.text.strip():
            raise DomainValidationError(
                "StageTranscript content.text cannot be empty or whitespace."
            )

        if not self.content.session_id:
            ch_token = self.channel.id.value if self.channel.id else self.channel.name
            object.__setattr__(
                self,
                "content",
                Content(
                    id=self.content.id,
                    title=self.content.title,
                    text=self.content.text,
                    session_id=f"{ch_token}:{self.content.id.value}",
                ),
            )

        if self.pass_count is not None:
            if not isinstance(self.pass_count, int):
                raise StageTranscriptStructureError("pass_count must be an integer.")
            if self.pass_count < 1:
                raise StageTranscriptStructureError("pass_count must be at least 1.")


def extract_source_text(source: StageTranscript | CandidateText | str) -> str:
    """Extract canonical textual payload from a StageTranscript, CandidateText, or string."""
    if isinstance(source, StageTranscript):
        return source.content.text
    if isinstance(source, CandidateText):
        return source.text
    return str(source)


def post_process_fluid_transcript(
    candidate: CandidateText,
    source: StageTranscript,
) -> StageTranscript:
    """Post-process candidate text into a validated StageTranscript domain aggregate.

    Strips H1 headers to preserve clean heading hierarchy, removes accidental
    complementary sections, and maps the pure Value Object triad from the source transcript.
    Conforms to ADR-038, ADR-057, and ADR-077.
    """
    current_text = candidate.text.strip()

    title_match = TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        extracted_title = source.content.title or "Untitled Compendium"
        body = current_text

    complementary_match = _ACCIDENTAL_COMPLEMENTARY_HEADING_PATTERN.search(body)
    if complementary_match:
        body = body[: complementary_match.start()].strip()

    if not body:
        raise StageTranscriptStructureError(
            f"Generated fluid prose body is empty for '{source.content.id.value}'."
        )

    return StageTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=extracted_title,
            text=body,
            session_id=source.content.session_id,
        ),
        metadata=dict(source.metadata),
    )
