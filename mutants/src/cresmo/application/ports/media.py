"""Hexagonal Media Ingestion Port.

Conforms to:
- ADR-004: Native Media Ingestion Decommissioning & Pure Python Adapter
- SPEC-004: Native Media Ingestion Specifications
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cresmo.domain.entities import SourceTranscript
from cresmo.domain.value_objects import ChannelFeedQuery, DiscoveredMediaItem


class MediaIngestionPort(ABC):
    """Hexagonal Port for media crawling, audio downloading, and subtitle/transcript ingestion.

    Conforms to ADR-004 and SPEC-004. Abstracts external tools (yt-dlp, whisper) behind
    pure domain aggregates (SourceTranscript).
    """

    @abstractmethod
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Fetch transcript or transcribe audio for a single video.

        Args:
            video_url: Target YouTube or media item URL.
            output_dir: Directory where raw text and audio scratch files reside.
            whisper_model: Whisper model checkpoint name (tiny, base, small, medium).
            keep_audio: If True, preserves downloaded audio; otherwise cleans up.

        Returns:
            SourceTranscript domain aggregate if successful, or None if extraction fails.

        Raises:
            RateLimitExceededError: If upstream provider returns HTTP 429.
            IngestionNetworkError: If socket timeout or network failure occurs.
        """
        raise NotImplementedError("Implement single video ingestion contract.")

    @abstractmethod
    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Query and discover media items from a channel or playlist feed within constraints.

        Args:
            query: Feed query containing channel URL, lookback window, and count limits.

        Returns:
            List of DiscoveredMediaItem value objects.
        """
        raise NotImplementedError("Implement discover channel feed contract.")

    @abstractmethod
    def extract_channel_url_from_video(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL.

        Extracts channel/uploader metadata without downloading video or audio streams.

        Args:
            video_url: Canonical or short video URL.

        Returns:
            Canonical channel URL (e.g. https://www.youtube.com/channel/{channel_id})
            or None if resolution fails.
        """
        raise NotImplementedError("Implement video channel resolution contract.")
