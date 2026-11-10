"""Source and Fluid Transcript domain aggregates and pure Value Object triad composition.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-019: SOTA-KISS Nomenclature & Value Objects
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-034: Algorithmic (ID-ID) and Cognitive (TXT-TXT) Parity Standard
- ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from typing import Any, Self

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

# Regex matching Markdown tables (| header | header | \n | --- | --- |)
_TABLE_PATTERN = re.compile(r"\|.*\|.*\n\|[\s:-]+\|", re.MULTILINE)
# Matches Markdown H1 title header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
# Matches any accidental complementary information section headers
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Extra\s+Info|Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class StageTranscript:
    """Base domain envelope for transcripts across pipeline stages.

    Conforms to ADR-038 (Pure Value Object Triad Composition) and ADR-054
    (Unified Stage Transcript Envelope and Stage-Invariant Polymorphism).
    Composed of the Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)
    4. metadata: dict[str, Any] (Stage Provenance & Lineage)
    """

    channel: Channel
    provenance: MediaProvenance
    content: Content
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        channel: Channel | None = None,
        provenance: MediaProvenance | None = None,
        content: Content | None = None,
        *,
        metadata: dict[str, Any] | None = None,
        content_id: ContentId | str | None = None,
        channel_name: ChannelName | str | None = None,
        body: str | None = None,
        title: str = "",
        source_url: str = "",
        publication_date: datetime.date | datetime.datetime | str | None = None,
        upload_date: datetime.date | datetime.datetime | str | None = None,
        channel_id: ChannelId | str | None = None,
        channel_category: str = "",
        video_description: str = "",
    ) -> None:
        """Construct StageTranscript with pure Triad Value Objects or ergonomic factory parameters."""
        resolved_date = publication_date or upload_date

        if channel is not None:
            resolved_channel = channel
        else:
            resolved_channel_name = channel_name or ""
            resolved_channel = Channel(
                name=resolved_channel_name,
                id=channel_id,
                category=channel_category,
            )

        if provenance is not None:
            resolved_provenance = provenance
        else:
            resolved_provenance = MediaProvenance.create(
                url=source_url,
                description=video_description,
                publication_date=resolved_date,
            )

        if content is not None:
            resolved_content = content
        else:
            if content_id:
                resolved_content_id = ContentId.from_string(content_id)
            elif source_url:
                extracted = ContentId.extract_from_text(source_url)
                resolved_content_id = extracted if extracted else ContentId("unknown")
            else:
                resolved_content_id = ContentId("unknown")

            resolved_content = Content(
                id=resolved_content_id,
                title=title,
                body=body or "",
            )

        object.__setattr__(self, "channel", resolved_channel)
        object.__setattr__(self, "provenance", resolved_provenance)
        object.__setattr__(self, "content", resolved_content)
        object.__setattr__(self, "metadata", metadata or {})

        self._validate_stage_invariants()

    def _validate_stage_invariants(self) -> None:
        """Template hook for concrete stage invariant enforcement."""

    @property
    def body(self) -> str:
        """Textual payload of the transcript stage."""
        return self.content.body

    @property
    def title(self) -> NoteTitle | str:
        """Cognitive title of the content payload."""
        return self.content.title

    @property
    def content_id(self) -> ContentId:
        """Algorithmic ContentId identifier."""
        return self.content.id

    @property
    def channel_name(self) -> ChannelName | str:
        """Cognitive channel/creator name."""
        return self.channel.name

    @property
    def channel_id(self) -> ChannelId | None:
        """Algorithmic channel/creator identifier."""
        return self.channel.id

    @classmethod
    def create(
        cls: type[Self],
        *,
        channel_name: str | ChannelName,
        content_id: str | ContentId,
        body: str,
        title: str = "",
        channel_id: str | ChannelId | None = None,
        channel_category: str = "",
        source_url: str = "",
        publication_date: datetime.date | datetime.datetime | str | None = None,
        video_description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        """Factory constructing StageTranscript from primitive parameters."""
        channel_vo = Channel(
            name=channel_name,
            id=channel_id,
            category=channel_category,
        )
        provenance_vo = MediaProvenance.create(
            url=source_url,
            description=video_description,
            publication_date=publication_date,
        )
        content_vo = Content(
            id=ContentId.from_string(content_id),
            title=title,
            body=body,
        )
        return cls(
            channel=channel_vo,
            provenance=provenance_vo,
            content=content_vo,
            metadata=metadata or {},
        )


@dataclass(frozen=True, slots=True, init=False)
class SourceTranscript(StageTranscript):
    """SourceTranscript Aggregate: Verbatim spoken transcript and origin metadata.

    Conforms to ADR-038: Pure Value Object Triad Composition and ADR-054.
    Strictly composed of the Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)

    Invariants:
        content.body cannot be whitespace or empty (pure audio silence rejected per SPEC-001: §2.2).
    """

    def _validate_stage_invariants(self) -> None:
        if not self.content.body.strip():
            raise DomainValidationError("SourceTranscript body cannot be empty or whitespace.")
        if self.provenance.url:
            extracted_cid = ContentId.extract_from_text(self.provenance.url)
            if extracted_cid is not None and extracted_cid != self.content.id:
                raise DomainValidationError(
                    f"ContentId mismatch: content.id '{self.content.id.value}' does not match "
                    f"ID extracted from provenance.url '{self.provenance.url}' ('{extracted_cid.value}')."
                )


@dataclass(frozen=True, slots=True, init=False)
class FluidTranscript(StageTranscript):
    """FluidTranscript Aggregate: Detranscribed clean fluid prose without orality noise.

    Conforms to ADR-028, ADR-031, ADR-038, and ADR-054.
    Strictly composed of the Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)

    Invariants:
        content.body cannot be empty or whitespace.
        content.body must be continuous prose without Markdown tables (| ... |).
    """

    def _validate_stage_invariants(self) -> None:
        cleaned_body = self.content.body.strip()
        if not cleaned_body:
            raise DomainValidationError("FluidTranscript body cannot be empty or whitespace.")

        if _TABLE_PATTERN.search(cleaned_body):
            raise CompendiumStructureError(
                "FluidTranscript body must be continuous prose and cannot contain Markdown tables."
            )


@dataclass(frozen=True, slots=True)
class Transcript:
    """Transcript Aggregate Root: Full lifecycle container from source to fluid synthesis.

    Conforms to ADR-038: Pure Value Object Triad Composition.
    """

    source: SourceTranscript | None = None
    fluid: FluidTranscript | None = None

    @property
    def channel(self) -> Channel | None:
        """Composite Channel Value Object."""
        if self.fluid is not None:
            return self.fluid.channel
        if self.source is not None:
            return self.source.channel
        return None

    @property
    def provenance(self) -> MediaProvenance | None:
        """Composite MediaProvenance Value Object."""
        if self.fluid is not None:
            return self.fluid.provenance
        if self.source is not None:
            return self.source.provenance
        return None

    @property
    def content(self) -> Content | None:
        """Composite Content Value Object."""
        if self.fluid is not None:
            return self.fluid.content
        if self.source is not None:
            return self.source.content
        return None


def post_process_fluid_transcript(
    candidate: CandidateText | str,
    source: SourceTranscript,
) -> FluidTranscript:
    """Post-process candidate text into a validated FluidTranscript domain aggregate.

    Strips H1 headers to preserve clean heading hierarchy, removes accidental
    complementary sections, and maps the pure Value Object triad from the source transcript.
    Conforms to ADR-038.
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

    return FluidTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=extracted_title,
            body=body,
        ),
    )
