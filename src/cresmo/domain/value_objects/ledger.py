"""Ledger, Indexing, and Master Document Value Objects.

Conforms to:
- ADR-003: Idempotent Content Ledger
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.identity import ChannelName, ContentId
from cresmo.domain.value_objects.media import PipelineStatus


@dataclass(frozen=True)
class LedgerEntry:
    """Immutable transactional audit and idempotency record persisted in SQLite WAL.

    Attributes:
        content_id: Unique content identifier.
        media_url: Web source URL.
        title: Episode or video title.
        channel_name: Human-readable creator channel name (cognitive key, used for directory layout).
        status: Current pipeline lifecycle status.
        notes_count: Total atomic notes synthesized.
        error_message: Optional failure reason if execution failed.
        started_at: UTC timestamp when ingestion commenced.
        completed_at: UTC timestamp when synthesis finished.
    """

    content_id: ContentId
    media_url: str
    title: str
    channel_name: ChannelName
    status: PipelineStatus
    notes_count: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        cleaned_media_url = self.media_url.strip()
        cleaned_title = self.title.strip()
        resolved_channel_name = ChannelName.from_string(self.channel_name)
        resolved_content_id = ContentId.from_string(self.content_id)

        if not cleaned_media_url.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid LedgerEntry media_url '{self.media_url}'. Must start with http:// or https://"
            )
        if not cleaned_title:
            raise DomainValidationError("LedgerEntry title cannot be empty.")
        if self.notes_count < 0:
            raise DomainValidationError(
                f"LedgerEntry notes_count cannot be negative. Got: {self.notes_count}"
            )

        object.__setattr__(self, "content_id", resolved_content_id)
        object.__setattr__(self, "channel_name", resolved_channel_name)
        object.__setattr__(self, "media_url", cleaned_media_url)
        object.__setattr__(self, "title", cleaned_title)


@dataclass(frozen=True)
class MasterDocumentResult:
    """Immutable report representing a consolidated master document for RAG ingestion.

    Attributes:
        channel_name: Creator/channel name (ChannelName Value Object).
        channel_category: Macro taxonomy category.
        output_path: Filesystem path to the generated master Markdown file.
        part_number: 1-based index when splitting by token/word limits.
        word_count: Total word count in the compiled document.
        document_count: Number of individual transcripts consolidated.
        video_ids: Tuple of all source ContentIds merged.
    """

    channel_name: ChannelName
    channel_category: str
    output_path: Path
    part_number: int
    word_count: int
    document_count: int
    video_ids: tuple[ContentId, ...] = ()

    def __post_init__(self) -> None:
        resolved_channel_name = ChannelName.from_string(self.channel_name)
        cleaned_category = self.channel_category.strip()
        if not cleaned_category:
            raise DomainValidationError("MasterDocumentResult channel_category cannot be empty.")
        if self.part_number < 1:
            raise DomainValidationError(
                f"MasterDocumentResult part_number must be >= 1. Got: {self.part_number}"
            )
        if self.word_count < 0:
            raise DomainValidationError(
                f"MasterDocumentResult word_count cannot be negative. Got: {self.word_count}"
            )
        if self.document_count < 0:
            raise DomainValidationError(
                f"MasterDocumentResult document_count cannot be negative. Got: {self.document_count}"
            )
        coerced_content_ids = tuple(
            ContentId.from_string(target_id) if not isinstance(target_id, ContentId) else target_id
            for target_id in self.video_ids
        )
        object.__setattr__(self, "channel_name", resolved_channel_name)
        object.__setattr__(self, "channel_category", cleaned_category)
        object.__setattr__(self, "video_ids", coerced_content_ids)


@dataclass(frozen=True)
class RawIndexEntry:
    """Immutable Value Object representing a single conceptual index entry for a raw transcript.

    Encapsulates canonical video metadata, distilled 2-to-4 word key concept, and paratactic
    synthesis paragraph for indexing and RAG retrieval.

    Attributes:
        video_id: Canonical ContentId.
        url: Canonical web URL.
        title: Episode title.
        channel_name: Creator channel name (ChannelName Value Object).
        key_concept: Distilled 2-4 word concept descriptor.
        synthesis: Paratactic summary paragraph.
    """

    video_id: ContentId
    url: str
    title: str
    channel_name: ChannelName
    key_concept: str
    synthesis: str
    channel_category: str = ""
    summary: str = ""
    excerpt: str = ""

    def __post_init__(self) -> None:
        resolved_content_id = ContentId.from_string(self.video_id)
        object.__setattr__(self, "video_id", resolved_content_id)
        cleaned_url = self.url.strip()
        cleaned_title = self.title.strip()
        resolved_channel_name = ChannelName.from_string(self.channel_name)
        cleaned_key_concept = " ".join(self.key_concept.split())
        cleaned_synthesis = self.synthesis.strip()
        cleaned_channel_category = (self.channel_category or "").strip()
        cleaned_summary = self.summary.strip()
        cleaned_excerpt = self.excerpt.strip()

        if not cleaned_url:
            raise DomainValidationError("RawIndexEntry url cannot be empty.")
        if not cleaned_title:
            raise DomainValidationError("RawIndexEntry title cannot be empty.")
        if not cleaned_key_concept:
            raise DomainValidationError("RawIndexEntry key_concept cannot be empty.")
        if not cleaned_synthesis:
            raise DomainValidationError("RawIndexEntry synthesis cannot be empty.")

        object.__setattr__(self, "url", cleaned_url)
        object.__setattr__(self, "title", cleaned_title)
        object.__setattr__(self, "channel_name", resolved_channel_name)
        object.__setattr__(self, "key_concept", cleaned_key_concept)
        object.__setattr__(self, "synthesis", cleaned_synthesis)
        object.__setattr__(self, "channel_category", cleaned_channel_category)
        object.__setattr__(self, "summary", cleaned_summary)
        object.__setattr__(self, "excerpt", cleaned_excerpt)

    def to_markdown_block(self) -> str:
        """Format entry as a rich Markdown block with title link, ID, concept, and paratactic paragraph."""
        return (
            f"### [{self.title}]({self.url})\n"
            f"- **Video ID**: `{self.video_id.value}` | **Conceito**: {self.key_concept}\n\n"
            f"{self.synthesis}\n"
        )

    def to_csv_row(self) -> list[str]:
        """Format entry as a 5-element row for brain.csv: [channel_category, channel_name, filename, concept, collapsed_synthesis]."""
        clean_synthesis = " ".join(self.synthesis.split())
        return [
            self.channel_category,
            str(self.channel_name),
            f"{self.video_id.value}.md",
            self.key_concept,
            clean_synthesis,
        ]
