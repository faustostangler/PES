"""Domain Value Objects for the Cresmo Knowledge Synthesis Bounded Context.

Implements immutable, self-validating Value Objects adhering to the Doctor Stangler Method
(Zero Primitive Obsession, construction-time invariant enforcement).

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-003: §2 (Channel Sync Models & Normalization Rules)
- ADR-001 (Modular Monolith Domain Integrity)
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.taxonomy import classify_channel

_CONTENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")
_BRACKETS_PATTERN = re.compile(r"\[\[(.*?)\]\]")
_ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|%]')


class NoteType(str, Enum):
    """Canonical typology classification for Obsidian Second Brain atomic notes.

    Restricts note classification strictly to authorized categories per SPEC-001: §2.1:
    - CONCEPT: Abstract principles, mental models, theories.
    - ENTITY: Specific people, organizations, historical objects, locations.
    - EVENT: Demarcated historical or contemporary happenings.
    - PROCESS: Dynamical procedures, systemic flows, algorithmic sequences.
    """

    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    PROCESS = "process"

    @classmethod
    def from_string(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string.

        Args:
            raw: Raw typology string from LLM synthesis or frontmatter.

        Returns:
            Normalized NoteType enum member.

        Raises:
            NoteTypologyError: If the raw string does not match any valid typology.
        """
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(
            f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}"
        )


class SourceModality(str, Enum):
    """Discriminator for input batch source modality.

    Conforms to ADR-019 (Zero Primitive Obsession).
    """

    FILE = "file"
    URL = "url"


@dataclass(frozen=True)
class ChannelName:
    """Canonical domain Value Object representing a content creator or source channel.

    Conforms to ADR-019: Zero Primitive Obsession.

    Invariants:
        - Value must be non-empty and not whitespace.
        - Automatically trimmed of leading and trailing whitespace.
        - Maximum length of 120 characters.
        - Prohibits path traversal sequences ('..' or '/' or '\\').
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val:
            raise DomainValidationError("ChannelName cannot be empty or whitespace.")
        if len(val) > 120:
            raise DomainValidationError(
                f"ChannelName exceeds maximum length of 120 characters: '{val[:30]}...'"
            )
        if ".." in val or "/" in val or "\\" in val:
            raise DomainValidationError(
                f"ChannelName cannot contain path traversal or separator characters: '{val}'"
            )
        object.__setattr__(self, "value", val)

    @classmethod
    def from_string(cls, raw: str | ChannelName) -> ChannelName:
        """Ergonomic conversion factory accepting str or existing ChannelName."""
        if isinstance(raw, cls):
            return raw
        return cls(value=str(raw))

    def __str__(self) -> str:
        return self.value

    def strip(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChannelName):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ContentId:
    """Strongly-typed unique identifier for a raw media item or transcript.

    Invariants:
        Must be a non-empty string between 8 and 64 characters matching ^[a-zA-Z0-9_-]+$.
        Zero whitespace or shell/path traversal characters allowed.
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        # Security invariant: prevent directory traversal or injection in identifiers
        if not val or not _CONTENT_ID_PATTERN.match(val):
            raise DomainValidationError(
                f"Invalid ContentId '{self.value}'. Must match ^[a-zA-Z0-9_-]{{8,64}}$ without whitespace."
            )
        object.__setattr__(self, "value", val)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoteTitle:
    """Canonical title for an Atomic Note in the Obsidian Second Brain vault.

    Invariants:
        Length between 1 and 200 characters. Automatically sanitizes WikiLink brackets
        and filesystem reserved characters while rejecting generic placeholders.
    """

    value: str

    def __post_init__(self) -> None:
        raw = self.value.strip()
        # ACL sanitization: strip [[ and ]] if LLM output included raw WikiLinks
        sanitized = _BRACKETS_PATTERN.sub(r"\1", raw).strip()
        # Filesystem isolation: remove characters prohibited on POSIX and Windows
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
    """Immutable ternary attribution model of causality for an Atomic Note.

    Attributes:
        cause: The primary generating condition or preceding mechanism.
        effect: The resultant dynamic outcome or structural change.
        epistemic_attribution: Conceptual framework, thinker, or source establishing causality.

    Invariants:
        Per SPEC-001: §2.1, either both cause and effect are populated, or both are empty.
        Partial causality (cause without effect or vice-versa) is illegal.
    """

    cause: str
    effect: str
    epistemic_attribution: str = ""

    def __post_init__(self) -> None:
        c = self.cause.strip()
        e = self.effect.strip()
        ea = self.epistemic_attribution.strip()

        # Invariant enforcement: causality requires relational pairs (cause and effect)
        if (c or e) and (not c or not e):
            raise DomainValidationError(
                f"CausalMatrix requires both 'cause' and 'effect' to be non-empty. Got cause='{c}', effect='{e}'."
            )

        object.__setattr__(self, "cause", c)
        object.__setattr__(self, "effect", e)
        object.__setattr__(self, "epistemic_attribution", ea)


@dataclass(frozen=True)
class CrossContextRelations:
    """Immutable triad connecting a concept across historical, lateral, and consequential axes.

    Attributes:
        precursors: Ancestral intellectual, historical, or systemic conditions.
        lateral_events: Synchronous or parallel occurrences in other domains.
        aftermath: Long-term downstream repercussions or systemic legacies.
    """

    precursors: str = ""
    lateral_events: str = ""
    aftermath: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", self.precursors.strip())
        object.__setattr__(self, "lateral_events", self.lateral_events.strip())
        object.__setattr__(self, "aftermath", self.aftermath.strip())


@dataclass(frozen=True)
class AtomicEntityInventory:
    """Discovery manifest of unique named entities discovered across an Enriched Compendium.

    Attributes:
        items: Sequence of tuples pairing validated NoteTitle and NoteType.

    Invariants:
        Per SPEC-001: §2.1, inventory cannot be empty and must contain zero duplicate titles
        (case-insensitive normalization) to guarantee deterministic batch partitioning.
    """

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
    """Canonical execution and idempotency status for media items in the pipeline.

    Members:
        COMPLETED: Ingestion and all synthesis stages finished successfully.
        SKIPPED_IDEMPOTENT: ContentId already processed in ledger; execution bypassed.
        FAILED_INGESTION: Audio download or transcript crawling failed.
        FAILED_TRANSFORMATION: LLM synthesis or schema extraction failed.
        RUNNING: Currently executing active pipeline stages.
        PAUSED_BUDGET: Token or API rate budget cap reached.
    """

    COMPLETED = "COMPLETED"
    SKIPPED_IDEMPOTENT = "SKIPPED_IDEMPOTENT"
    FAILED_INGESTION = "FAILED_INGESTION"
    FAILED_TRANSFORMATION = "FAILED_TRANSFORMATION"
    RUNNING = "RUNNING"
    PAUSED_BUDGET = "PAUSED_BUDGET"


@dataclass(frozen=True)
class DiscoveredMediaItem:
    """Immutable descriptor of a media item discovered during channel polling.

    Attributes:
        content_id: Strongly-typed unique content identifier.
        title: Video or episode title.
        published_at: UTC timestamp of release.
        media_url: Canonical web URL.
        channel_name: Human-readable creator or channel name.
    """

    content_id: ContentId
    title: str
    published_at: datetime
    media_url: str
    channel_name: ChannelName | str

    def __post_init__(self) -> None:
        t = self.title.strip()
        u = self.media_url.strip()

        if not t:
            raise DomainValidationError("DiscoveredMediaItem title cannot be empty.")
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid DiscoveredMediaItem media_url '{self.media_url}'. Must start with http:// or https://"
            )
        cn = ChannelName.from_string(self.channel_name)

        object.__setattr__(self, "title", t)
        object.__setattr__(self, "media_url", u)
        object.__setattr__(self, "channel_name", cn)


_CHANNEL_ID_PATTERN = re.compile(r"(?:^|/channel/|/user/|/c/)(UC[a-zA-Z0-9_-]{2,64})")


def normalize_to_uploads_playlist_url(channel_ref: str) -> str:
    """Transform YouTube channel reference to its canonical uploads playlist URL (UU prefix).

    YouTube automatically maintains an 'Uploads from <Channel>' playlist for every channel,
    where the playlist ID is identical to the channel ID but with the 'UC' prefix swapped to 'UU'.
    Querying this playlist URL via yt-dlp flat extraction is significantly faster, strictly
    reverse-chronological, and avoids web scrapers navigating dynamic UI tabs.

    Args:
        channel_ref: Raw channel URL, handle, or channel ID.

    Returns:
        Canonical YouTube uploads playlist URL or sanitized /videos endpoint.
    """
    cleaned = channel_ref.strip()
    if not cleaned:
        return cleaned

    # Direct pass-through if already a playlist URL
    if "playlist?list=" in cleaned or "list=UU" in cleaned or "list=PL" in cleaned:
        return cleaned if cleaned.startswith(("http://", "https://")) else f"https://{cleaned}"

    m = _CHANNEL_ID_PATTERN.search(cleaned)
    if m:
        # YouTube convention: replace channel prefix 'UC' with uploads playlist prefix 'UU'
        channel_id = m.group(1)
        uploads_playlist_id = "UU" + channel_id[2:]
        return f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

    formatted = cleaned if cleaned.startswith(("http://", "https://")) else f"https://{cleaned}"
    if "/@" in formatted and not formatted.endswith(
        ("/videos", "/shorts", "/streams", "/playlists")
    ):
        return f"{formatted.rstrip('/')}/videos"

    if formatted.startswith("https://@"):
        handle = formatted.replace("https://@", "")
        return f"https://www.youtube.com/@{handle}/videos"

    return formatted


@dataclass(frozen=True)
class ChannelFeedQuery:
    """Encapsulates query constraints for discovering uningested media items.

    Attributes:
        channel_url: HTTP(S) URL of the target channel or playlist.
        lookback_days: Temporal discovery window in days (must be positive).
        max_videos: Maximum number of items to crawl in a single execution pass.
    """

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
class SyncFilterCriteria:
    """Immutable multi-criteria filter for channel synchronization and batch discovery.

    Conforms to ADR-012.

    Attributes:
        channels: Tuple of target channel names, handles, or URLs (normalized lowercase).
        categories: Tuple of target domain categories or volatility types (normalized lowercase).
        video_ids: Tuple of target video IDs or URLs.
    """

    channels: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    video_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        norm_channels: list[str] = []
        for ch in self.channels:
            cleaned = ch.strip().lower()
            if not cleaned:
                raise DomainValidationError("Channel filter token cannot be empty.")
            norm_channels.append(cleaned)

        norm_categories: list[str] = []
        for cat in self.categories:
            cleaned = cat.strip().lower()
            if not cleaned:
                raise DomainValidationError("Category filter token cannot be empty.")
            norm_categories.append(cleaned)

        norm_vids: list[str] = []
        for vid in self.video_ids:
            cleaned = vid.strip()
            if not cleaned:
                raise DomainValidationError("Video filter token cannot be empty.")
            norm_vids.append(cleaned)

        object.__setattr__(self, "channels", tuple(norm_channels))
        object.__setattr__(self, "categories", tuple(norm_categories))
        object.__setattr__(self, "video_ids", tuple(norm_vids))

    @classmethod
    def from_strings(
        cls,
        channels: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        video_ids: Iterable[str] | None = None,
    ) -> SyncFilterCriteria:
        """Parse multi-value strings (including comma-separated lists) into a SyncFilterCriteria."""

        def _parse_tokens(items: Iterable[str] | None) -> tuple[str, ...]:
            if not items:
                return ()
            tokens: list[str] = []
            for item in items:
                if not item:
                    continue
                for part in item.split(","):
                    p = part.strip()
                    if p:
                        tokens.append(p)
            return tuple(tokens)

        return cls(
            channels=_parse_tokens(channels),
            categories=_parse_tokens(categories),
            video_ids=_parse_tokens(video_ids),
        )

    def is_empty(self) -> bool:
        """Return True if no filter criteria are specified (full pipeline flow)."""
        return not self.channels and not self.categories and not self.video_ids

    def matches_channel(self, channel_name: str, channel_url: str | None = None) -> bool:
        """Evaluate whether a channel matches the configured channel criteria."""
        if not self.channels:
            return True

        c_name = channel_name.strip().lower()
        c_url = (channel_url or "").strip().lower()

        for target in self.channels:
            if target in c_name or c_name in target:
                return True
            if c_url and target in c_url:
                return True
            if target.startswith("@") and target[1:] in c_name:
                return True
            if f"@{target}" in c_url or f"@{target}" in c_name:
                return True

        return False

    def matches_category(self, channel_name: str) -> bool:
        """Evaluate whether a channel matches the configured category criteria.

        Per ADR-012, checks both domain name (e.g. 'politics_br') and volatility type
        (e.g. 'volatile' or 'perennial') returned by classify_channel.
        """
        if not self.categories:
            return True

        domain, cat_type = classify_channel(channel_name)
        domain_lower = domain.lower()
        cat_lower = cat_type.lower()

        return domain_lower in self.categories or cat_lower in self.categories

    def matches_video(self, video_id: str, video_url: str | None = None) -> bool:
        """Evaluate whether a video matches the configured video ID/URL criteria."""
        if not self.video_ids:
            return True

        vid_clean = video_id.strip()
        vurl_clean = (video_url or "").strip()

        for target in self.video_ids:
            if target == vid_clean or target in vurl_clean:
                return True
            if vid_clean and vid_clean in target:
                return True

        return False


@dataclass(frozen=True)
class SyncSummary:
    """Immutable batch execution report aggregating outcomes for a channel sync run.

    Attributes:
        channel_url: Canonical target channel URL.
        total_discovered: Total count of items retrieved from channel crawler.
        processed_count: Count of items successfully processed and persisted.
        skipped_count: Count of items bypassed due to idempotency ledger matches.
        failed_count: Count of items that failed ingestion or synthesis.
        duration_seconds: Wall-clock duration of the sync run.
        status: Overall pipeline execution termination status.
    """

    channel_url: str
    total_discovered: int
    processed_count: int
    skipped_count: int
    failed_count: int
    duration_seconds: float
    status: PipelineStatus


@dataclass(frozen=True)
class LedgerEntry:
    """Immutable transactional audit and idempotency record persisted in SQLite WAL.

    Attributes:
        content_id: Unique content identifier.
        media_url: Web source URL.
        title: Episode or video title.
        channel_name: Channel identifier.
        status: Current pipeline lifecycle status.
        notes_count: Total atomic notes synthesized.
        error_message: Optional failure reason if execution failed.
        started_at: UTC timestamp when ingestion commenced.
        completed_at: UTC timestamp when synthesis finished.
    """

    content_id: ContentId
    media_url: str
    title: str
    channel_name: ChannelName | str
    status: PipelineStatus
    notes_count: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        u = self.media_url.strip()
        t = self.title.strip()
        cn = ChannelName.from_string(self.channel_name)
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid LedgerEntry media_url '{self.media_url}'. Must start with http:// or https://"
            )
        if not t:
            raise DomainValidationError("LedgerEntry title cannot be empty.")
        if self.notes_count < 0:
            raise DomainValidationError(
                f"LedgerEntry notes_count cannot be negative. Got: {self.notes_count}"
            )

        object.__setattr__(self, "media_url", u)
        object.__setattr__(self, "title", t)
        object.__setattr__(self, "channel_name", cn)


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

    channel_name: ChannelName | str
    channel_category: str
    output_path: Path
    part_number: int
    word_count: int
    document_count: int
    video_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        cn = ChannelName.from_string(self.channel_name)
        cat = self.channel_category.strip()
        if not cat:
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
        object.__setattr__(self, "channel_name", cn)
        object.__setattr__(self, "channel_category", cat)


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
    channel_name: ChannelName | str
    key_concept: str
    synthesis: str
    channel_category: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.video_id, ContentId):
            raise DomainValidationError(
                f"RawIndexEntry video_id must be a ContentId instance. Got: {type(self.video_id)}"
            )
        u = self.url.strip()
        t = self.title.strip()
        cn = ChannelName.from_string(self.channel_name)
        kc = " ".join(self.key_concept.split())
        s = self.synthesis.strip()
        cat = (self.channel_category or "").strip()

        if not u:
            raise DomainValidationError("RawIndexEntry url cannot be empty.")
        if not t:
            raise DomainValidationError("RawIndexEntry title cannot be empty.")
        if not kc:
            raise DomainValidationError("RawIndexEntry key_concept cannot be empty.")
        if not s:
            raise DomainValidationError("RawIndexEntry synthesis cannot be empty.")

        object.__setattr__(self, "url", u)
        object.__setattr__(self, "title", t)
        object.__setattr__(self, "channel_name", cn)
        object.__setattr__(self, "key_concept", kc)
        object.__setattr__(self, "synthesis", s)
        object.__setattr__(self, "channel_category", cat)

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


RESERVED_SYSTEM_FILENAMES: frozenset[str] = frozenset(
    {
        "_canal.md",
        "brain.csv",
        "cresmo_ledger.db",
        "cresmo_ledger.db-wal",
        "cresmo_ledger.db-shm",
        "playlist.txt",
        "playlist-priority.txt",
        "_index.json",
    }
)

RESERVED_DERIVED_DIRS: frozenset[str] = frozenset(
    {
        "enriched",
        "master",
        "vault",
        ".venv",
        "tests",
        "__pycache__",
    }
)


def is_processable_transcript_file(path: Path | str) -> bool:
    """Validate whether a path represents a candidate raw transcript and not a system artifact or index.

    Adheres to ADR-015:
    1. Suffix must strictly be .md or .txt (case-insensitive).
    2. Filename cannot start with '_' or '.' (hidden or system catalog).
    3. None of the directory components in path.parts may start with '_' or '.'.
    4. Filename cannot belong to RESERVED_SYSTEM_FILENAMES.
    5. Temporary, backup, or editor swap files (.tmp, .bak, .swp, ~) are excluded.
    6. Files residing inside derived output roots (enriched, master, vault) are excluded.

    Args:
        path: Path object or string path to validate.

    Returns:
        True if the file is an eligible raw transcript, False if it is a system artifact/index.
    """
    p = Path(path)
    name = p.name
    name_lower = name.lower()

    # Rule 1: Suffix must be .md or .txt
    suffix = p.suffix.lower()
    if suffix not in {".md", ".txt"}:
        return False

    # Rule 2: Filename cannot start with '_' or '.'
    if name.startswith(("_", ".")):
        return False

    # Rule 3: Hidden or system directory components (e.g. .git, .obsidian, _trash)
    for part in p.parts[:-1]:
        if part and part != "/" and part.startswith(("_", ".")):
            return False

    # Rule 4: Reserved system filenames
    if name_lower in RESERVED_SYSTEM_FILENAMES:
        return False

    # Rule 5: Temporary / backup / editor swap suffixes
    if name_lower.endswith((".tmp", ".bak", ".swp")) or name.endswith("~"):
        return False

    # Rule 6: Derived artifact directories when path is relative or encompasses multiple roots
    dir_parts_lower = {part.lower() for part in p.parts[:-1]}
    return not bool(dir_parts_lower.intersection(RESERVED_DERIVED_DIRS))
