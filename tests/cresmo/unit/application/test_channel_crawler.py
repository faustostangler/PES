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
    ContentId,
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
        # 2. Fresh item with naive tz
        item2 = DummyFeedItem(
            url="https://youtube.com/watch?v=fresh2",
            media_url="https://youtube.com/watch?v=fresh2",
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

    def test_resolve_remote_channels_filters_criteria_taxonomy_and_pool_config(
        self, monkeypatch: Any
    ) -> None:
        from concurrent.futures import ThreadPoolExecutor as RealThreadPoolExecutor
        from unittest.mock import MagicMock

        import cresmo.application.use_cases.discovery.channel_crawler as crawler_mod

        pool_calls: list[tuple[int | None, str | None]] = []

        def _spy_executor(*args: Any, **kwargs: Any) -> RealThreadPoolExecutor:
            pool_calls.append((kwargs.get("max_workers"), kwargs.get("thread_name_prefix")))
            return RealThreadPoolExecutor(*args, **kwargs)

        monkeypatch.setattr(crawler_mod, "ThreadPoolExecutor", _spy_executor)

        adapter = DummyMediaIngestionAdapter()
        adapter.video_to_channel = {
            "https://youtube.com/watch?v=v1": "https://youtube.com/@kept_chan",
            "https://youtube.com/watch?v=v2": "https://youtube.com/@wrong_chan",
            "https://youtube.com/watch?v=v3": "https://youtube.com/@wrong_cat_chan",
            "https://youtube.com/watch?v=err_vid": "",
        }

        def _err_or_resolve(video_url: str) -> str:
            if video_url.endswith("err_vid"):
                raise RuntimeError("network timeout")
            return adapter.video_to_channel[video_url]

        monkeypatch.setattr(adapter, "extract_channel_url_from_video", _err_or_resolve)

        taxonomy = MagicMock()
        taxonomy.classify.side_effect = lambda target: (
            ("science", "perennial")
            if "kept_chan" in str(target)
            else ("entertainment", "volatile")
        )
        logs: list[str] = []
        crawler = ChannelFeedCrawlerService(
            media_ingestion_port=adapter,
            notify_fn=logs.append,
            taxonomy_port=taxonomy,
        )

        # Single video with workers=4 exercises max(1, min(4, 1)) == 1
        probed: set[str] = set()
        channels: list[str] = []
        crawler.resolve_remote_channels(
            videos=["https://youtube.com/watch?v=v1"],
            workers=4,
            probed_channels=probed,
            channels_to_probe=channels,
            filter_criteria=SyncFilterCriteria(
                channels=("kept_chan", "wrong_cat_chan"),
                categories=("perennial",),
            ),
        )
        assert pool_calls == [(1, "CresmoChannelResolver")]
        assert channels == ["https://youtube.com/@kept_chan"]
        assert any("with 1 workers" in msg for msg in logs)

        # Mixed videos verify channel AND category filtering + exact failed_vu in warning
        probed2: set[str] = set()
        channels2: list[str] = []
        crawler.resolve_remote_channels(
            videos=[
                "https://youtube.com/watch?v=v1",
                "https://youtube.com/watch?v=v2",
                "https://youtube.com/watch?v=v3",
                "https://youtube.com/watch?v=err_vid",
            ],
            workers=2,
            probed_channels=probed2,
            channels_to_probe=channels2,
            filter_criteria=SyncFilterCriteria(
                channels=("kept_chan", "wrong_cat_chan"),
                categories=("perennial",),
            ),
        )
        assert channels2 == ["https://youtube.com/@kept_chan"]
        assert any(
            "Failed to resolve channel for https://youtube.com/watch?v=err_vid: network timeout"
            in msg
            for msg in logs
        )

    def test_probe_channel_feeds_stop_event_errors_filtering_and_boundary(
        self, monkeypatch: Any
    ) -> None:
        from concurrent.futures import ThreadPoolExecutor as RealThreadPoolExecutor

        import cresmo.application.use_cases.discovery.channel_crawler as crawler_mod

        pool_calls: list[tuple[int | None, str | None]] = []

        def _spy_executor(*args: Any, **kwargs: Any) -> RealThreadPoolExecutor:
            pool_calls.append((kwargs.get("max_workers"), kwargs.get("thread_name_prefix")))
            return RealThreadPoolExecutor(*args, **kwargs)

        monkeypatch.setattr(crawler_mod, "ThreadPoolExecutor", _spy_executor)

        adapter = DummyMediaIngestionAdapter()
        now = datetime(2026, 1, 10, 12, 0, 0, tzinfo=UTC)
        cutoff = now - timedelta(days=7)

        # http:// prefix preserved and exact cutoff == published_at included
        adapter.channel_feeds["http://youtube.com/@http_chan"] = [
            DummyFeedItem(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                media_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                published_at=cutoff,
            )
        ]
        crawler = ChannelFeedCrawlerService(media_ingestion_port=adapter)
        urls_http = crawler.probe_single_channel_feed(
            chan_url="http://youtube.com/@http_chan",
            lookback_days=7,
            max_videos=10,
            cutoff=cutoff,
        )
        assert urls_http == ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]

        # probe_channel_feeds: 1 failure + 1 success (blocked item before 2 allowed items)
        logs: list[str] = []
        crawler_logged = ChannelFeedCrawlerService(
            media_ingestion_port=adapter, notify_fn=logs.append
        )

        def _fake_probe(
            chan_url: str, lookback_days: int, max_videos: int, _cutoff: datetime
        ) -> list[str]:
            _ = (lookback_days, max_videos)
            if "broken_chan" in chan_url:
                raise RuntimeError("feed crash")
            return [
                "https://www.youtube.com/watch?v=blockedVid1",
                "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL777",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ]

        monkeypatch.setattr(crawler_logged, "probe_single_channel_feed", _fake_probe)
        acc = _BatchSourceAccumulator()
        # Cross-host video_ids criteria: matches ContentId('dQw4w9WgXcQ') in youtu.be URL
        # AND matches 'list=PL777' via url_fallback, while skipping 'blockedVid1' via continue
        criteria = SyncFilterCriteria(
            video_ids=("https://youtu.be/dQw4w9WgXcQ", "list=PL777"),
        )
        crawler_logged.probe_channel_feeds(
            channels=["https://youtube.com/@broken_chan", "https://youtube.com/@good_chan"],
            lookback_days=7,
            max_videos=10,
            workers=5,
            acc=acc,
            filter_criteria=criteria,
        )
        assert pool_calls[-1] == (2, "CresmoFeedProber")
        assert len(acc.sources) == 2
        assert {s.content_id for s in acc.sources} == {
            ContentId("oHg5SJYRHA0"),
            ContentId("dQw4w9WgXcQ"),
        }
        assert any(
            "Warning: Failed to probe feed for https://youtube.com/@broken_chan: feed crash" in msg
            for msg in logs
        )
        assert any("Stage B complete: Discovered 2 new video(s)" in msg for msg in logs)

        # Single channel with workers=5 -> max_workers=1
        pool_calls.clear()
        acc_single = _BatchSourceAccumulator()
        crawler_logged.probe_channel_feeds(
            channels=["https://youtube.com/@good_chan"],
            lookback_days=7,
            max_videos=10,
            workers=5,
            acc=acc_single,
        )
        assert pool_calls == [(1, "CresmoFeedProber")]

        # stop_event set mid-loop / pre-loop still executes post-loop Stage B complete notification
        logs_stop: list[str] = []
        crawler_stop = ChannelFeedCrawlerService(
            media_ingestion_port=adapter, notify_fn=logs_stop.append
        )
        stop = threading.Event()
        stop.set()
        crawler_stop.probe_channel_feeds(
            channels=["https://youtube.com/@good_chan"],
            lookback_days=7,
            max_videos=10,
            workers=1,
            acc=_BatchSourceAccumulator(),
            stop_event=stop,
        )
        assert any("Stage B complete: Discovered 0 new video(s)" in msg for msg in logs_stop)

        # stop_event triggered inside discovered_urls loop still emits Stage B complete
        logs_inner_stop: list[str] = []
        crawler_inner = ChannelFeedCrawlerService(
            media_ingestion_port=adapter, notify_fn=logs_inner_stop.append
        )
        inner_stop = threading.Event()
        acc_inner = _BatchSourceAccumulator()
        orig_has_seen = acc_inner.has_seen

        def _has_seen_then_stop(token: Any) -> bool:
            inner_stop.set()
            return orig_has_seen(token)

        monkeypatch.setattr(acc_inner, "has_seen", _has_seen_then_stop)
        monkeypatch.setattr(
            crawler_inner,
            "probe_single_channel_feed",
            lambda *_args: [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://www.youtube.com/watch?v=oHg5SJYRHA0",
            ],
        )
        crawler_inner.probe_channel_feeds(
            channels=["https://youtube.com/@good_chan"],
            lookback_days=7,
            max_videos=10,
            workers=1,
            acc=acc_inner,
            stop_event=inner_stop,
        )
        assert len(acc_inner.sources) == 1
        assert any("Stage B complete: Discovered 1 new video(s)" in msg for msg in logs_inner_stop)
