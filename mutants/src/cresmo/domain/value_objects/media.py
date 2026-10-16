"""Media Discovery and Pipeline Execution Value Objects.

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-004: §2 (Media Ingestion and Channel Feeds)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.identity import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
)


class PipelineStatus(str, Enum):
    """Canonical execution and idempotency status for media items in the pipeline.

    Members:
        COMPLETED: Ingestion and all synthesis stages finished successfully.
        SKIPPED_IDEMPOTENT: ContentId already processed in ledger; execution bypassed.
        FAILED_INGESTION: Audio download or transcript crawling failed.
        FAILED_TRANSFORMATION: LLM synthesis or schema extraction failed.
        RUNNING: Currently executing active pipeline stages.
        PAUSED_BUDGET: Token or API rate budget cap reached.
        QUARANTINED: Quality gate evaluation failed after maximum retries; item quarantined.
    """

    COMPLETED = "COMPLETED"
    SKIPPED_IDEMPOTENT = "SKIPPED_IDEMPOTENT"
    FAILED_INGESTION = "FAILED_INGESTION"
    FAILED_TRANSFORMATION = "FAILED_TRANSFORMATION"
    RUNNING = "RUNNING"
    PAUSED_BUDGET = "PAUSED_BUDGET"
    QUARANTINED = "QUARANTINED"


DEFAULT_FEED_LOOKBACK_DAYS: int = 7
DEFAULT_FEED_MAX_VIDEOS: int = 50


@dataclass(frozen=True, slots=True)
class MediaProvenance:
    """Canonical domain Value Object encapsulating media origin and acquisition provenance.

    Conforms to ADR-038: Pure Value Object Triad Composition.

    Attributes:
        url: Canonical web URL or storage URI of source media.
        description: Raw description or metadata summary provided by the creator.
        publication_date: Immutable release date of the media content.
    """

    url: str = ""
    description: str = ""
    publication_date: date | None = None

    def __post_init__(self) -> None:
        clean_url = self.url.strip()
        clean_desc = self.description.strip()
        pub_date = self.publication_date
        if isinstance(pub_date, datetime):
            pub_date = pub_date.date()

        object.__setattr__(self, "url", clean_url)
        object.__setattr__(self, "description", clean_desc)
        object.__setattr__(self, "publication_date", pub_date)

    @classmethod
    def create(
        cls,
        url: str = "",
        description: str = "",
        publication_date: date | datetime | str | None = None,
    ) -> MediaProvenance:
        """Ergonomic factory parsing dates and normalizing strings."""
        parsed_date: date | None = None
        if isinstance(publication_date, datetime):
            parsed_date = publication_date.date()
        elif isinstance(publication_date, date):
            parsed_date = publication_date
        elif isinstance(publication_date, str) and publication_date.strip():
            try:
                parsed_date = date.fromisoformat(publication_date.strip())
            except ValueError:
                parsed_date = None
        return cls(url=url, description=description, publication_date=parsed_date)

    @classmethod
    def empty(cls) -> MediaProvenance:
        """Default empty provenance for synthetic or unit testing scenarios."""
        return cls()


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
    channel_name: ChannelName

    def __post_init__(self) -> None:
        cleaned_title = self.title.strip()
        cleaned_media_url = self.media_url.strip()

        if not cleaned_title:
            raise DomainValidationError("DiscoveredMediaItem title cannot be empty.")
        if not cleaned_media_url.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid DiscoveredMediaItem media_url '{self.media_url}'. Must start with http:// or https://"
            )
        resolved_channel_name = ChannelName.from_string(self.channel_name)
        resolved_content_id = ContentId.from_string(self.content_id)

        object.__setattr__(self, "title", cleaned_title)
        object.__setattr__(self, "media_url", cleaned_media_url)
        object.__setattr__(self, "channel_name", resolved_channel_name)
        object.__setattr__(self, "content_id", resolved_content_id)

    @property
    def channel(self) -> Channel:
        """Composite Channel Value Object."""
        return Channel.from_name(name=self.channel_name)

    @property
    def provenance(self) -> MediaProvenance:
        """Composite MediaProvenance Value Object."""
        return MediaProvenance(
            url=self.media_url,
            publication_date=self.published_at.date() if self.published_at else None,
        )

    @property
    def content(self) -> Content:
        """Composite Content Value Object."""
        return Content.create(
            id=self.content_id,
            title=self.title,
        )


CHANNEL_TAB_ENDINGS: tuple[str, ...] = ("/videos", "/shorts", "/streams", "/playlists")


def normalize_to_uploads_playlist_url(channel_ref: str | ChannelId) -> str:
    """Transform YouTube channel reference to its canonical uploads playlist URL (UU prefix).

    YouTube automatically maintains an 'Uploads from <Channel>' playlist for every channel,
    where the playlist ID is identical to the channel ID but with the 'UC' prefix swapped to 'UU'.
    Querying this playlist URL via yt-dlp flat extraction is significantly faster, strictly
    reverse-chronological, and avoids web scrapers navigating dynamic UI tabs.

    Args:
        channel_ref: Raw channel URL, handle, or channel ID (str or ChannelId).

    Returns:
        Canonical YouTube uploads playlist URL or sanitized /videos endpoint.
    """
    if isinstance(channel_ref, ChannelId):
        return channel_ref.uploads_playlist_url or channel_ref.canonical_url

    cleaned = channel_ref.strip()
    if not cleaned:
        return cleaned

    # Direct pass-through if already a playlist URL
    if "playlist?list=" in cleaned or "list=UU" in cleaned or "list=PL" in cleaned:
        return cleaned if cleaned.startswith(("http://", "https://")) else f"https://{cleaned}"

    extracted_channel_id = ChannelId.extract_from_text(cleaned)
    if extracted_channel_id and extracted_channel_id.uploads_playlist_url:
        return extracted_channel_id.uploads_playlist_url

    formatted = cleaned if cleaned.startswith(("http://", "https://")) else f"https://{cleaned}"
    formatted = formatted.rstrip("/")

    if formatted.startswith("https://@"):
        handle = formatted.removeprefix("https://@")
        if handle.endswith(CHANNEL_TAB_ENDINGS):
            return f"https://www.youtube.com/@{handle}"
        return f"https://www.youtube.com/@{handle}/videos"

    if "/@" in formatted and not formatted.endswith(CHANNEL_TAB_ENDINGS):
        return f"{formatted}/videos"

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
    lookback_days: int = DEFAULT_FEED_LOOKBACK_DAYS
    max_videos: int = DEFAULT_FEED_MAX_VIDEOS

    def __post_init__(self) -> None:
        cleaned_channel_url = self.channel_url.strip()
        if not cleaned_channel_url.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid ChannelFeedQuery channel_url '{self.channel_url}'. Must start with http:// or https://"
            )
        if self.lookback_days <= 0:
            raise DomainValidationError(
                f"lookback_days must be positive. Got: {self.lookback_days}"
            )
        if self.max_videos <= 0:
            raise DomainValidationError(f"max_videos must be positive. Got: {self.max_videos}")
        object.__setattr__(self, "channel_url", cleaned_channel_url)
