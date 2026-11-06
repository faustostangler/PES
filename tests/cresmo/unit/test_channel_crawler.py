"""Unit tests for ChannelFeedCrawlerService.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discovery.channel_crawler import (
    ChannelFeedCrawlerService,
)
from cresmo.application.use_cases.discovery.models import (
    _BatchSourceAccumulator,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    SourceModality,
    SyncFilterCriteria,
)


@dataclass
class DummyFeedItem:
    url: str
    published_at: datetime | None = None
    media_url: str | None = None


class DummyMediaIngestionAdapter(MediaIngestionPort):
    def __init__(self) -> None:
        self.video_to_channel: dict[str, str] = {}
        self.channel_feeds: dict[str, list[Any]] = {}

    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> Any:
        return None

    def extract_channel_url_from_video(self, video_url: str) -> str:
        if video_url in self.video_to_channel:
            return self.video_to_channel[video_url]
        if "error" in video_url:
            raise RuntimeError(f"Failed to fetch {video_url}")
        return "https://youtube.com/@default_channel"

    def discover_channel_feed(self, query: ChannelFeedQuery) -> list[Any]:
        if "error" in query.channel_url:
            raise RuntimeError(f"Channel error for {query.channel_url}")
        return self.channel_feeds.get(query.channel_url, [])


class TestChannelFeedCrawlerService:
    def test_init_default_notify(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter)
        crawler._notify("test log")  # Should not raise

    def test_resolve_remote_channels_empty_list(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        logs: list[str] = []
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter, notify_fn=logs.append)

        probed = set()
        channels = []
        crawler.resolve_remote_channels(
            [], workers=2, probed_channels=probed, channels_to_probe=channels
        )
        assert len(channels) == 0
        assert len(logs) == 0

    def test_resolve_remote_channels_success_and_errors(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        adapter.video_to_channel = {
            "https://youtube.com/watch?v=vid1": "https://youtube.com/@science_channel",
            "https://youtube.com/watch?v=vid2": "https://youtube.com/@math_channel",
        }
        logs: list[str] = []
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter, notify_fn=logs.append)

        probed: set[str] = {"https://youtube.com/@already_probed"}
        channels: list[str] = []

        videos = [
            "https://youtube.com/watch?v=vid1",
            "https://youtube.com/watch?v=vid2",
            "https://youtube.com/watch?v=error_vid",
        ]

        crawler.resolve_remote_channels(
            videos=videos,
            workers=2,
            probed_channels=probed,
            channels_to_probe=channels,
        )

        assert "https://youtube.com/@science_channel" in probed
        assert "https://youtube.com/@math_channel" in probed
        assert "https://youtube.com/@science_channel" in channels
        assert "https://youtube.com/@math_channel" in channels
        assert any("Failed to resolve channel" in log for log in logs)

    def test_resolve_remote_channels_stop_event(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter)

        stop = threading.Event()
        stop.set()

        probed: set[str] = set()
        channels: list[str] = []
        crawler.resolve_remote_channels(
            videos=["https://youtube.com/watch?v=vid1"],
            workers=1,
            probed_channels=probed,
            channels_to_probe=channels,
            stop_event=stop,
        )
        assert len(channels) == 0

    def test_probe_single_channel_feed_cutoff_and_attributes(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter)

        now = datetime.now(UTC)
        cutoff = now - timedelta(days=7)

        # 1. Fresh item with media_url
        item1 = DummyFeedItem(
            url="fallback_url",
            media_url="https://youtube.com/watch?v=fresh1",
            published_at=now - timedelta(days=2),
        )
        # 2. Fresh item with naive tz and url only
        item2 = DummyFeedItem(
            url="https://youtube.com/watch?v=fresh2",
            media_url=None,
            published_at=(now - timedelta(days=3)).replace(tzinfo=None),
        )
        # 3. Old item outside lookback cutoff
        item3 = DummyFeedItem(
            url="https://youtube.com/watch?v=old",
            media_url="https://youtube.com/watch?v=old",
            published_at=now - timedelta(days=10),
        )
        # 4. Item without published_at
        item4 = DummyFeedItem(
            url="https://youtube.com/watch?v=no_date",
            media_url="https://youtube.com/watch?v=no_date",
            published_at=None,
        )

        adapter.channel_feeds["https://youtube.com/@active_chan"] = [item1, item2, item3, item4]

        # Feed probe with protocol prefix
        urls = crawler.probe_single_channel_feed(
            chan_url="https://youtube.com/@active_chan",
            lookback_days=7,
            max_videos=50,
            cutoff=cutoff,
        )

        assert "https://youtube.com/watch?v=fresh1" in urls
        assert "https://youtube.com/watch?v=fresh2" in urls
        assert "https://youtube.com/watch?v=no_date" in urls
        assert "https://youtube.com/watch?v=old" not in urls

        # Feed probe without protocol prefix (auto-prepends https://)
        adapter.channel_feeds["https://youtube.com/@noprefix"] = [item1]
        urls_noprefix = crawler.probe_single_channel_feed(
            chan_url="youtube.com/@noprefix",
            lookback_days=7,
            max_videos=50,
            cutoff=cutoff,
        )
        assert "https://youtube.com/watch?v=fresh1" in urls_noprefix

        # Feed probe error returns empty list
        urls_err = crawler.probe_single_channel_feed(
            chan_url="https://error_chan",
            lookback_days=7,
            max_videos=50,
            cutoff=cutoff,
        )
        assert urls_err == []

    def test_probe_channel_feeds_integration_and_filtering(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        logs: list[str] = []
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter, notify_fn=logs.append)

        now = datetime.now(UTC)
        item1 = DummyFeedItem(
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            published_at=now - timedelta(days=1),
        )
        item2 = DummyFeedItem(
            url="https://youtube.com/watch?v=oHg5SJYRHA0",
            media_url="https://youtube.com/watch?v=oHg5SJYRHA0",
            published_at=now - timedelta(days=1),
        )

        adapter.channel_feeds["https://youtube.com/@chan1"] = [item1, item2]

        acc = _BatchSourceAccumulator()
        # Pre-register dQw4w9WgXcQ as already seen
        acc.seen_vids.add("dQw4w9WgXcQ")

        crawler.probe_channel_feeds(
            channels=["https://youtube.com/@chan1"],
            lookback_days=7,
            max_videos=10,
            workers=2,
            acc=acc,
        )

        # Only item2 should be added, item1 was already seen
        assert len(acc.sources) == 1
        assert acc.sources[0].target == "https://youtube.com/watch?v=oHg5SJYRHA0"
        assert acc.sources[0].kind is SourceModality.URL
        assert any("Stage B complete: Discovered 1 new video" in log for log in logs)

    def test_probe_channel_feeds_with_video_ids_criteria(self) -> None:
        adapter = DummyMediaIngestionAdapter()
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter)

        now = datetime.now(UTC)
        item1 = DummyFeedItem(
            url="https://youtube.com/watch?v=allowed_vid",
            media_url="https://youtube.com/watch?v=allowed_vid",
            published_at=now,
        )
        item2 = DummyFeedItem(
            url="https://youtube.com/watch?v=blocked_vid",
            media_url="https://youtube.com/watch?v=blocked_vid",
            published_at=now,
        )
        adapter.channel_feeds["https://youtube.com/@target"] = [item1, item2]

        acc = _BatchSourceAccumulator()
        criteria = SyncFilterCriteria(video_ids=("allowed_vid",))

        crawler.probe_channel_feeds(
            channels=["https://youtube.com/@target"],
            lookback_days=7,
            max_videos=10,
            workers=1,
            acc=acc,
            filter_criteria=criteria,
        )

        assert len(acc.sources) == 1
        assert "allowed_vid" in acc.sources[0].target
