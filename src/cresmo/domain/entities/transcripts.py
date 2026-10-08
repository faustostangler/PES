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
    SourceModality,
)

# Regex matching Markdown tables (| header | header | \n | --- | --- |)
_TABLE_PATTERN = re.compile(r"\|.*\|.*\n\|[\s:-]+\|", re.MULTILINE)
# Matches Markdown H1 title header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
# Matches any accidental complementary information section headers
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class SourceTranscript:
    """SourceTranscript Aggregate: Verbatim spoken transcript and origin metadata.

    Conforms to ADR-038: Pure Value Object Triad Composition.
    Strictly composed of the Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)

    Invariants:
        content.body cannot be whitespace or empty (pure audio silence rejected per SPEC-001: §2.2).
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
        content_id: ContentId | str | None = None,
        channel_name: ChannelName | str | None = None,
        body: str | None = None,
        title: str = "",
        source_url: str = "",
        publication_date: datetime.date | datetime.datetime | None = None,
        upload_date: datetime.date | datetime.datetime | None = None,
        channel_id: ChannelId | str | None = None,
        channel_category: str = "",
        video_description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Construct SourceTranscript with either pure Triad Value Objects or ergonomic kwargs."""
        resolved_date = publication_date or upload_date

        if channel is not None:
            resolved_channel = channel
        else:
            resolved_channel_name = channel_name or ""
            resolved_channel = Channel(
                name=resolved_channel_name,
                id=channel_id,
                category=channel_category,
                url=f"https://www.youtube.com/channel/{channel_id}" if channel_id else None,
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
            cid = ContentId.from_string(content_id) if content_id else ContentId("unknown")
            resolved_content = Content(
                id=cid,
                title=title,
                body=body or "",
                url=resolved_provenance.url,
                modality=SourceModality.URL if resolved_provenance.url else SourceModality.FILE,
                publication_date=resolved_provenance.publication_date,
            )

        if not resolved_content.body.strip():
            raise DomainValidationError("SourceTranscript body cannot be empty or whitespace.")

        object.__setattr__(self, "channel", resolved_channel)
        object.__setattr__(self, "provenance", resolved_provenance)
        object.__setattr__(self, "content", resolved_content)
        object.__setattr__(self, "metadata", metadata or {})

    # =========================================================================
    # Symmetrical Parity & Ergonomic Accessors (ADR-034 / ADR-038)
    # =========================================================================

    @property
    def body(self) -> str:
        """Canonical verbatim transcript body text."""
        return self.content.body

    @property
    def title(self) -> str:
        """Cognitive content title (TXT - TXT Parity)."""
        return self.content.title

    @property
    def content_title(self) -> str:
        """Cognitive content title (channel_name - content_title Parity)."""
        return self.content.title

    @property
    def content_id(self) -> ContentId:
        """Algorithmic media identifier (ID - ID Parity)."""
        return self.content.id

    @property
    def channel_name(self) -> ChannelName:
        """Cognitive channel creator name (TXT - TXT Parity)."""
        return ChannelName.from_string(self.channel.name)

    @property
    def channel_id(self) -> ChannelId | None:
        """Algorithmic channel identifier (ID - ID Parity)."""
        return self.channel.id

    @property
    def source_url(self) -> str:
        """Canonical provenance web URL."""
        return self.provenance.url

    @property
    def publication_date(self) -> datetime.date | None:
        """Canonical publication date."""
        return self.provenance.publication_date

    @property
    def upload_date(self) -> datetime.date | None:
        """Backward-compatible alias for publication date."""
        return self.provenance.publication_date

    @property
    def channel_category(self) -> str:
        """Channel taxonomy category."""
        return self.channel.category

    @property
    def video_description(self) -> str:
        """Original creator description."""
        return self.provenance.description


@dataclass(frozen=True, slots=True)
class FluidTranscript:
    """FluidTranscript Aggregate: Detranscribed clean fluid prose without orality noise.

    Conforms to ADR-028, ADR-031, and ADR-038 (Pure Value Object Triad Composition).
    Strictly composed of the Value Object triad:
    1. channel: Channel (Origin / Creator - channel_id & channel_name)
    2. provenance: MediaProvenance (Acquisition & Temporal Context)
    3. content: Content (Textual Artifact & Payload - content_id, content_title, body)

    Invariants:
        content.body cannot be empty or whitespace.
        content.body must be continuous prose without Markdown tables (| ... |).
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
        content_id: ContentId | str | None = None,
        channel_name: ChannelName | str | None = None,
        body: str | None = None,
        title: str = "",
        source_url: str = "",
        publication_date: datetime.date | datetime.datetime | None = None,
        upload_date: datetime.date | datetime.datetime | None = None,
        channel_id: ChannelId | str | None = None,
        channel_category: str = "",
        video_description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Construct FluidTranscript with either pure Triad Value Objects or ergonomic kwargs."""
        resolved_date = publication_date or upload_date

        if channel is not None:
            resolved_channel = channel
        else:
            resolved_channel_name = channel_name or ""
            resolved_channel = Channel(
                name=resolved_channel_name,
                id=channel_id,
                category=channel_category,
                url=f"https://www.youtube.com/channel/{channel_id}" if channel_id else None,
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
            cid = ContentId.from_string(content_id) if content_id else ContentId("unknown")
            resolved_content = Content(
                id=cid,
                title=title,
                body=body or "",
                url=resolved_provenance.url,
                modality=SourceModality.URL if resolved_provenance.url else SourceModality.FILE,
                publication_date=resolved_provenance.publication_date,
            )

        cleaned_body = resolved_content.body.strip()
        if not cleaned_body:
            raise DomainValidationError("FluidTranscript body cannot be empty or whitespace.")

        if _TABLE_PATTERN.search(cleaned_body):
            raise CompendiumStructureError(
                "FluidTranscript body must be continuous prose and cannot contain Markdown tables."
            )

        object.__setattr__(self, "channel", resolved_channel)
        object.__setattr__(self, "provenance", resolved_provenance)
        object.__setattr__(self, "content", resolved_content)
        object.__setattr__(self, "metadata", metadata or {})

    # =========================================================================
    # Symmetrical Parity & Ergonomic Accessors (ADR-034 / ADR-038)
    # =========================================================================

    @property
    def body(self) -> str:
        """Canonical synthesized fluid prose body text."""
        return self.content.body

    @property
    def title(self) -> str:
        """Cognitive content title (TXT - TXT Parity)."""
        return self.content.title

    @property
    def content_title(self) -> str:
        """Cognitive content title (channel_name - content_title Parity)."""
        return self.content.title

    @property
    def content_id(self) -> ContentId:
        """Algorithmic media identifier (ID - ID Parity)."""
        return self.content.id

    @property
    def channel_name(self) -> ChannelName:
        """Cognitive channel creator name (TXT - TXT Parity)."""
        return ChannelName.from_string(self.channel.name)

    @property
    def channel_id(self) -> ChannelId | None:
        """Algorithmic channel identifier (ID - ID Parity)."""
        return self.channel.id

    @property
    def source_url(self) -> str:
        """Canonical provenance web URL."""
        return self.provenance.url

    @property
    def publication_date(self) -> datetime.date | None:
        """Canonical publication date."""
        return self.provenance.publication_date

    @property
    def upload_date(self) -> datetime.date | None:
        """Backward-compatible alias for publication date."""
        return self.provenance.publication_date

    @property
    def channel_category(self) -> str:
        """Channel taxonomy category."""
        return self.channel.category

    @property
    def video_description(self) -> str:
        """Original creator description."""
        return self.provenance.description


@dataclass(frozen=True, slots=True)
class Transcript:
    """Transcript Aggregate Root: Full lifecycle container from source to fluid synthesis.

    Conforms to ADR-038: Pure Value Object Triad Composition.
    """

    source: SourceTranscript | None = None
    fluid: FluidTranscript | None = None

    @property
    def content_id(self) -> ContentId | None:
        """Algorithmic content identifier from active transcript representation."""
        if self.fluid is not None:
            return self.fluid.content_id
        if self.source is not None:
            return self.source.content_id
        return None

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

    @property
    def channel_id(self) -> ChannelId | None:
        """Algorithmic channel identifier (channel_id - content_id Parity)."""
        return self.channel.id if self.channel else None

    @property
    def channel_name(self) -> ChannelName | None:
        """Cognitive channel creator name (channel_name - content_title Parity)."""
        return ChannelName.from_string(self.channel.name) if self.channel else None

    @property
    def content_title(self) -> str:
        """Cognitive content title (channel_name - content_title Parity)."""
        return self.content.title if self.content else ""

    @property
    def title(self) -> str:
        """Cognitive content title alias."""
        return self.content_title


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
        extracted_title = source.title or "Untitled Compendium"
        body = current_text

    comp_match = _COMPLEMENTARY_REGEX.search(body)
    if comp_match:
        body = body[: comp_match.start()].strip()

    if not body:
        raise CompendiumStructureError(
            f"Generated fluid prose body is empty for '{source.content_id.value}'."
        )

    return FluidTranscript(
        channel=source.channel,
        provenance=source.provenance,
        content=Content(
            id=source.content.id,
            title=extracted_title,
            body=body,
            url=source.provenance.url,
            publication_date=source.provenance.publication_date,
        ),
    )
