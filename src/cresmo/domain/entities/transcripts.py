"""Source and Fluid Transcript domain aggregates and post-processing.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- SPEC-011: Fluid Prose Detranscription Specification
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


@dataclass(frozen=True)
class SourceTranscript:
    """SourceTranscript Aggregate: Verbatim spoken transcript and origin metadata.

    Standardized canonical input contract across pipeline stages per ADR-031.
    Encapsulates raw audio transcription, native subtitle text, or canonical source text alongside channel provenance.

    Attributes:
        content_id: Strongly-typed canonical media identifier.
        channel_name: Human-readable creator or source channel name (ChannelName Value Object).
        body: Verbatim text of spoken audio or canonical source prose.
        title: Optional original video/content title.
        source_url: Canonical web URL.
        publication_date: Optional release date.
        upload_date: Backward-compatible alias for publication_date.
        channel_id: Optional platform channel ID.
        channel_category: Macro topic classification.
        video_description: Raw creator description text.
        metadata: Stage-specific or ingestion provenance metadata dictionary.

    Invariants:
        channel_name cannot be whitespace or empty (enforced by ChannelName).
        body cannot be whitespace or empty (pure audio silence is rejected per SPEC-001: §2.2).
    """

    content_id: ContentId
    channel_name: ChannelName
    body: str
    title: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    upload_date: datetime.date | None = None
    channel_id: ChannelId | None = None
    channel_category: str = ""
    video_description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Coerce channel_name to strongly-typed ChannelName Value Object (ADR-019)
        if isinstance(self.channel_name, str):
            object.__setattr__(self, "channel_name", ChannelName.from_string(self.channel_name))
        elif not isinstance(self.channel_name, ChannelName):
            object.__setattr__(self, "channel_name", ChannelName(str(self.channel_name)))

        if self.channel_id is not None and not isinstance(self.channel_id, ChannelId):
            object.__setattr__(self, "channel_id", ChannelId.from_string(str(self.channel_id)))

        # Unify publication_date and upload_date semantics
        pub_date = self.publication_date or self.upload_date
        object.__setattr__(self, "publication_date", pub_date)
        object.__setattr__(self, "upload_date", pub_date)

        # Invariant checks ensuring audio transcription payload is valid
        if not self.body.strip():
            raise DomainValidationError("SourceTranscript body cannot be empty or whitespace.")

    @property
    def channel(self) -> Channel:
        """Composite Channel Value Object encapsulating channel identity, taxonomy, and URL."""
        return Channel(
            name=self.channel_name,
            id=self.channel_id,
            category=self.channel_category,
            url=f"https://www.youtube.com/channel/{self.channel_id.value}"
            if self.channel_id
            else None,
        )

    @property
    def content(self) -> Content:
        """Composite Content Value Object encapsulating media identity, title, URL, and modality."""
        return Content(
            id=self.content_id,
            title=self.title or self.content_id.value,
            url=self.source_url,
            modality=SourceModality.URL if self.source_url else SourceModality.FILE,
            publication_date=self.publication_date,
        )


@dataclass(frozen=True)
class FluidTranscript:
    """FluidTranscript Aggregate: Detranscribed clean fluid prose without orality noise.

    Represents spoken transcripts transformed into continuous third-person neutral narrative prose
    with standardized NER spelling, ready for conceptual indexing and Socratic gap filling.

    Conforms to:
        - ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
        - SPEC-011: Fluid Prose Detranscription Specification

    Attributes:
        content_id: Strongly-typed canonical media identifier.
        channel_name: Human-readable creator or source channel name (ChannelName Value Object).
        body: Continuous fluid prose narrative free of speech noise and oralities.
        title: Clean video or document title string.
        source_url: Canonical web URL or local file URI.
        publication_date: Optional release date.
        upload_date: Backward-compatible alias for publication_date.
        channel_id: Optional platform channel ID.
        channel_category: Macro topic classification.
        video_description: Raw creator description text.

    Invariants:
        channel_name cannot be whitespace or empty.
        body cannot be empty or whitespace.
        body must be continuous prose; markdown tables are strictly forbidden per cresmo-style-guide.
    """

    content_id: ContentId
    channel_name: ChannelName
    body: str
    title: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    upload_date: datetime.date | None = None
    channel_id: ChannelId | None = None
    channel_category: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        resolved_channel_name = (
            self.channel_name
            if isinstance(self.channel_name, ChannelName)
            else ChannelName.from_string(self.channel_name)
        )
        object.__setattr__(self, "channel_name", resolved_channel_name)

        if self.channel_id is not None and not isinstance(self.channel_id, ChannelId):
            object.__setattr__(self, "channel_id", ChannelId.from_string(self.channel_id))

        pub_date = self.publication_date or self.upload_date
        object.__setattr__(self, "publication_date", pub_date)
        object.__setattr__(self, "upload_date", pub_date)

        cleaned_body = self.body.strip()
        if not cleaned_body:
            raise DomainValidationError("FluidTranscript body cannot be empty or whitespace.")

        if _TABLE_PATTERN.search(cleaned_body):
            raise CompendiumStructureError(
                "FluidTranscript body must be continuous prose and cannot contain Markdown tables."
            )

    @property
    def channel(self) -> Channel:
        """Composite Channel Value Object encapsulating channel identity, taxonomy, and URL."""
        return Channel(
            name=self.channel_name,
            id=self.channel_id,
            category=self.channel_category,
            url=f"https://www.youtube.com/channel/{self.channel_id.value}"
            if self.channel_id
            else None,
        )

    @property
    def content(self) -> Content:
        """Composite Content Value Object encapsulating media identity, title, URL, and modality."""
        return Content(
            id=self.content_id,
            title=self.title or self.content_id.value,
            url=self.source_url,
            modality=SourceModality.URL if self.source_url else SourceModality.FILE,
            publication_date=self.publication_date,
        )


def post_process_fluid_transcript(
    candidate: CandidateText | str,
    source: SourceTranscript,
) -> FluidTranscript:
    """Post-process candidate text into a validated FluidTranscript domain aggregate.

    Strips H1 headers to preserve clean heading hierarchy, removes accidental
    complementary sections, and maps provenance metadata from the source transcript.
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
        content_id=source.content_id,
        channel_name=source.channel_name,
        body=body,
        title=extracted_title,
        source_url=source.source_url,
        publication_date=source.publication_date,
        channel_id=source.channel_id,
        channel_category=source.channel_category,
        video_description=source.video_description,
    )
