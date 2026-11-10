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

import datetime
import re
from dataclasses import dataclass, field
from typing import Any

from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
)
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    NoteTitle,
)

# Matches Markdown H1 title header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
# Matches any accidental complementary information section headers
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Extra\s+Info|Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class StageTranscript:
    """Monomorphic domain envelope for transcripts across all pipeline stages.

    Conforms to ADR-038 (Pure Value Object Triad Composition), ADR-054, and ADR-057.
    Composed of the pure Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)
    4. metadata: dict[str, Any] (Stage Provenance & Lineage)
    5. complementary_info: str (Encyclopedic context, dates, mini-biographies)
    6. pass_count: int | None (Number of enrichment passes executed, >= 1 when present)
    """

    channel: Channel
    provenance: MediaProvenance
    content: Content
    metadata: dict[str, Any] = field(default_factory=dict)
    complementary_info: str = ""
    pass_count: int | None = None

    def __post_init__(self) -> None:
        """Enforce domain invariants and type validity on pure triad components."""
        if not isinstance(self.channel, Channel):
            raise TypeError(f"channel must be an instance of Channel, got {type(self.channel).__name__}")
        if not isinstance(self.provenance, MediaProvenance):
            raise TypeError(
                f"provenance must be an instance of MediaProvenance, got {type(self.provenance).__name__}"
            )
        if not isinstance(self.content, Content):
            raise TypeError(f"content must be an instance of Content, got {type(self.content).__name__}")

        if not self.content.body.strip():
            raise DomainValidationError("StageTranscript content.body cannot be empty or whitespace.")

        if self.pass_count is not None:
            if not isinstance(self.pass_count, int):
                raise CompendiumStructureError("pass_count must be an integer.")
            if self.pass_count < 1:
                raise CompendiumStructureError("pass_count must be at least 1.")

    @property
    def body(self) -> str:
        """Textual payload of the transcript stage."""
        return self.content.body

    @property
    def title(self) -> NoteTitle:
        """Validated NoteTitle of the transcript payload."""
        return NoteTitle(self.content.title) if self.content.title.strip() else NoteTitle("Untitled Compendium")

    @property
    def content_id(self) -> ContentId:
        """Algorithmic ContentId identifier."""
        return self.content.id

    @property
    def channel_name(self) -> ChannelName:
        """Canonical ChannelName Value Object."""
        return ChannelName.from_string(self.channel.name)

    @property
    def channel_id(self) -> ChannelId | None:
        """Algorithmic channel/creator identifier."""
        return self.channel.id

    @property
    def channel_category(self) -> str:
        """Macro topic classification."""
        return self.channel.category

    @property
    def source_url(self) -> str:
        """Origin web URL."""
        return self.provenance.url or ""

    @property
    def publication_date(self) -> datetime.date | None:
        """Release date."""
        return self.provenance.publication_date

    @property
    def video_date(self) -> str:
        """Formatted timestamp string."""
        return str(
            self.metadata.get("video_date")
            or (
                self.provenance.publication_date.isoformat()
                if self.provenance.publication_date
                else ""
            )
        )

    @property
    def video_description(self) -> str:
        """Original creator description."""
        return self.provenance.description or ""


def post_process_fluid_transcript(
    candidate: CandidateText | str,
    source: StageTranscript,
) -> StageTranscript:
    """Post-process candidate text into a validated StageTranscript domain aggregate.

    Strips H1 headers to preserve clean heading hierarchy, removes accidental
    complementary sections, and maps the pure Value Object triad from the source transcript.
    Conforms to ADR-038 and ADR-057.
    """
    current_text = (
        candidate.text.strip() if isinstance(candidate, CandidateText) else candidate.strip()
    )

    title_match = _TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = _TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        extracted_title = source.content.title or "Untitled Compendium"
        body = current_text

    complementary_match = _COMPLEMENTARY_REGEX.search(body)
    if complementary_match:
        body = body[: complementary_match.start()].strip()

    if not body:
        raise CompendiumStructureError(
            f"Generated fluid prose body is empty for '{source.content.id.value}'."
        )

    return StageTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=extracted_title,
            body=body,
        ),
        metadata=dict(source.metadata),
    )
