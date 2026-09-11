"""Domain Value Objects for the Cresmo Knowledge Synthesis context.

Implements immutable, self-validating Value Objects adhering to the Doctor Stangler Method
(Zero Primitive Obsession, construction-time invariant enforcement).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError

_CONTENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")
_BRACKETS_PATTERN = re.compile(r"\[\[(.*?)\]\]")
_ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|%]')


class NoteType(str, Enum):
    """Canonical typology classification for Obsidian Second Brain atomic notes."""

    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    PROCESS = "process"

    @classmethod
    def from_string(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(
            f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}"
        )


@dataclass(frozen=True)
class ContentId:
    """Strongly-typed unique identifier for a raw media item or transcript."""

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val or not _CONTENT_ID_PATTERN.match(val):
            raise DomainValidationError(
                f"Invalid ContentId '{self.value}'. Must match ^[a-zA-Z0-9_-]{{8,64}}$ without whitespace."
            )
        object.__setattr__(self, "value", val)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoteTitle:
    """Canonical title for an Atomic Note in the Second Brain vault."""

    value: str

    def __post_init__(self) -> None:
        raw = self.value.strip()
        # Strip [[ and ]] if present
        sanitized = _BRACKETS_PATTERN.sub(r"\1", raw).strip()
        # Strip illegal filesystem characters
        sanitized = _ILLEGAL_CHARS_PATTERN.sub("", sanitized).strip()

        if not sanitized or len(sanitized) > 200:
            raise DomainValidationError(
                f"NoteTitle must be between 1 and 200 characters. Got: '{self.value}' (sanitized: '{sanitized}')"
            )

        if sanitized.lower() in {"untitled", "untitled_note"}:
            raise DomainValidationError(f"Generic placeholder title '{self.value}' is prohibited.")

        object.__setattr__(self, "value", sanitized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CausalMatrix:
    """Immutable ternary attribution model of causality for an Atomic Note."""

    cause: str
    effect: str
    epistemic_attribution: str = ""

    def __post_init__(self) -> None:
        c = self.cause.strip()
        e = self.effect.strip()
        ea = self.epistemic_attribution.strip()

        if (c or e) and (not c or not e):
            raise DomainValidationError(
                f"CausalMatrix requires both 'cause' and 'effect' to be non-empty. Got cause='{c}', effect='{e}'."
            )

        object.__setattr__(self, "cause", c)
        object.__setattr__(self, "effect", e)
        object.__setattr__(self, "epistemic_attribution", ea)


@dataclass(frozen=True)
class CrossContextRelations:
    """Immutable triad connecting a concept across historical, lateral, and consequential axes."""

    precursors: str = ""
    lateral_events: str = ""
    aftermath: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", self.precursors.strip())
        object.__setattr__(self, "lateral_events", self.lateral_events.strip())
        object.__setattr__(self, "aftermath", self.aftermath.strip())


@dataclass(frozen=True)
class AtomicEntityInventory:
    """Discovery manifest of unique named entities discovered across an Enriched Compendium."""

    items: tuple[tuple[NoteTitle, NoteType], ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise DomainValidationError("AtomicEntityInventory cannot be empty.")

        seen_titles: set[str] = set()
        for title, _ in self.items:
            key = title.value.lower()
            if key in seen_titles:
                raise DomainValidationError(
                    f"Duplicate title '{title.value}' detected in AtomicEntityInventory."
                )
            seen_titles.add(key)


class PipelineStatus(str, Enum):
    """Canonical execution and idempotency status for media items in the pipeline."""

    COMPLETED = "COMPLETED"
    SKIPPED_IDEMPOTENT = "SKIPPED_IDEMPOTENT"
    FAILED_INGESTION = "FAILED_INGESTION"
    FAILED_TRANSFORMATION = "FAILED_TRANSFORMATION"
    RUNNING = "RUNNING"
    PAUSED_BUDGET = "PAUSED_BUDGET"


@dataclass(frozen=True)
class DiscoveredMediaItem:
    """Immutable descriptor of a media item discovered during channel polling."""

    content_id: ContentId
    title: str
    published_at: datetime
    media_url: str
    channel_name: str

    def __post_init__(self) -> None:
        t = self.title.strip()
        u = self.media_url.strip()
        c = self.channel_name.strip()

        if not t:
            raise DomainValidationError("DiscoveredMediaItem title cannot be empty.")
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid DiscoveredMediaItem media_url '{self.media_url}'. Must start with http:// or https://"
            )
        if not c:
            raise DomainValidationError("DiscoveredMediaItem channel_name cannot be empty.")

        object.__setattr__(self, "title", t)
        object.__setattr__(self, "media_url", u)
        object.__setattr__(self, "channel_name", c)


@dataclass(frozen=True)
class ChannelFeedQuery:
    """Encapsulates query constraints for discovering uningested media items."""

    channel_url: str
    lookback_days: int = 7
    max_videos: int = 50

    def __post_init__(self) -> None:
        u = self.channel_url.strip()
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid ChannelFeedQuery channel_url '{self.channel_url}'. Must start with http:// or https://"
            )
        if self.lookback_days <= 0:
            raise DomainValidationError(
                f"lookback_days must be positive. Got: {self.lookback_days}"
            )
        if self.max_videos <= 0:
            raise DomainValidationError(f"max_videos must be positive. Got: {self.max_videos}")
        object.__setattr__(self, "channel_url", u)


@dataclass(frozen=True)
class SyncSummary:
    """Immutable batch execution report aggregating outcomes for a channel sync run."""

    channel_url: str
    total_discovered: int
    processed_count: int
    skipped_count: int
    failed_count: int
    duration_seconds: float
    status: PipelineStatus


@dataclass(frozen=True)
class LedgerEntry:
    """Immutable transactional audit and idempotency record persisted in SQLite WAL."""

    content_id: ContentId
    media_url: str
    title: str
    channel_name: str
    status: PipelineStatus
    notes_count: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        u = self.media_url.strip()
        t = self.title.strip()
        c = self.channel_name.strip()
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid LedgerEntry media_url '{self.media_url}'. Must start with http:// or https://"
            )
        if not t:
            raise DomainValidationError("LedgerEntry title cannot be empty.")
        if not c:
            raise DomainValidationError("LedgerEntry channel_name cannot be empty.")
        if self.notes_count < 0:
            raise DomainValidationError(
                f"LedgerEntry notes_count cannot be negative. Got: {self.notes_count}"
            )

        object.__setattr__(self, "media_url", u)
        object.__setattr__(self, "title", t)
        object.__setattr__(self, "channel_name", c)
