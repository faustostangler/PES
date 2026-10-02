"""Media Discovery and Pipeline Execution Value Objects.

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-004: §2 (Media Ingestion and Channel Feeds)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.identity import (
    ChannelId,
    ChannelName,
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
        t = self.title.strip()
        u = self.media_url.strip()

        if not t:
            raise DomainValidationError("DiscoveredMediaItem title cannot be empty.")
        if not u.startswith(("http://", "https://")):
            raise DomainValidationError(
                f"Invalid DiscoveredMediaItem media_url '{self.media_url}'. Must start with http:// or https://"
            )
        cn = ChannelName.from_string(self.channel_name)
        cid = ContentId.from_string(self.content_id)

        object.__setattr__(self, "title", t)
        object.__setattr__(self, "media_url", u)
        object.__setattr__(self, "channel_name", cn)
        object.__setattr__(self, "content_id", cid)


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

    cid = ChannelId.extract_from_text(cleaned)
    if cid and cid.uploads_playlist_url:
        return cid.uploads_playlist_url

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
