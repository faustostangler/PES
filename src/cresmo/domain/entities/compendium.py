"""EnrichedCompendium domain aggregate.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl
- ADR-054: Unified Stage Transcript Envelope and Stage-Invariant Polymorphism
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import Any

from cresmo.domain.entities.transcripts import _TABLE_PATTERN, StageTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    NoteTitle,
)


@dataclass(frozen=True, slots=True, init=False)
class EnrichedCompendium(StageTranscript):
    """EnrichedCompendium Aggregate: Multi-pass enriched fluid prose compendium.

    Conforms to ADR-028, ADR-031, ADR-038, and ADR-054 (Pure 3-VO Triad Composition).
    Inherits the 3-VO Triad from StageTranscript:
    1. channel: Channel
    2. provenance: MediaProvenance
    3. content: Content
    4. metadata: dict[str, Any]

    Stage-specific payload:
        complementary_info: Encyclopedic context, dates, mini-biographies.
        pass_count: Number of enrichment passes executed (must be >= 1).
    """

    complementary_info: str = ""
    pass_count: int = 1

    def __init__(
        self,
        channel: Channel | None = None,
        provenance: MediaProvenance | None = None,
        content: Content | None = None,
        *,
        complementary_info: str = "",
        pass_count: int = 1,
        metadata: dict[str, Any] | None = None,
        content_id: ContentId | str | None = None,
        channel_name: ChannelName | str | None = None,
        body: str | None = None,
        title: NoteTitle | str = "",
        source_url: str = "",
        publication_date: datetime.date | datetime.datetime | str | None = None,
        upload_date: datetime.date | datetime.datetime | str | None = None,
        video_date: str = "",
        channel_id: ChannelId | str | None = None,
        channel_category: str = "",
        video_description: str = "",
    ) -> None:
        if pass_count < 1:
            raise CompendiumStructureError("pass_count must be at least 1.")

        object.__setattr__(self, "complementary_info", complementary_info or "")
        object.__setattr__(self, "pass_count", pass_count)

        # Harmonize publication_date and video_date
        resolved_date = publication_date or upload_date
        resolved_video_date = video_date
        if resolved_date is None and video_date:
            try:
                raw_video_date = video_date.strip()
                if raw_video_date:
                    resolved_date = datetime.date.fromisoformat(raw_video_date[:10])
            except (ValueError, TypeError):
                resolved_date = None
        if not resolved_video_date and isinstance(resolved_date, datetime.date):
            resolved_video_date = resolved_date.isoformat()

        meta = dict(metadata or {})
        if resolved_video_date:
            meta["video_date"] = resolved_video_date

        effective_title = title.value if isinstance(title, NoteTitle) else (title or "")

        StageTranscript.__init__(
            self,
            channel=channel,
            provenance=provenance,
            content=content,
            metadata=meta,
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=effective_title,
            source_url=source_url,
            publication_date=resolved_date,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def _validate_stage_invariants(self) -> None:
        cleaned_body = self.content.body.strip()
        cleaned_complementary_info = self.complementary_info.strip()

        if not cleaned_body:
            raise CompendiumStructureError("EnrichedCompendium body cannot be empty.")
        if not cleaned_complementary_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Extra Info' section."
            )
        if _TABLE_PATTERN.search(cleaned_body):
            raise CompendiumStructureError(
                "EnrichedCompendium body must be continuous prose and cannot contain Markdown tables."
            )

    @property
    def title(self) -> NoteTitle:
        """Validated NoteTitle of the compendium."""
        return NoteTitle(self.content.title)

    @property
    def channel_name(self) -> ChannelName:
        """Canonical ChannelName Value Object."""
        return ChannelName.from_string(self.channel.name)

    @property
    def channel_id(self) -> ChannelId | None:
        """Canonical ChannelId Value Object."""
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
        """Backward-compatible timestamp string."""
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


_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*###\s+Extra\s+Info\s*$",
    re.MULTILINE,
)


def post_process_enriched_compendium(
    candidate: Any,
    source: Any,
    pass_count: int = 1,
) -> EnrichedCompendium:
    """Post-process candidate text into a validated EnrichedCompendium domain aggregate.

    Conforms to ADR-028, ADR-031, ADR-038, and ADR-054.
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
        raise CompendiumStructureError("EnrichedCompendium body cannot be empty.")
    if not complementary_info:
        raise CompendiumStructureError(
            "EnrichedCompendium must contain a non-empty 'Extra Info' section."
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

    return EnrichedCompendium(
        channel=channel,
        provenance=provenance,
        content=Content(
            id=content_id,
            title=extracted_title,
            body=main_body,
        ),
        complementary_info=complementary_info,
        pass_count=max(pass_count, 1),
    )
