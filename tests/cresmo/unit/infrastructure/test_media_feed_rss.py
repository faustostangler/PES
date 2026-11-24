"""Hermetic unit tests for YouTube Atom RSS fast-path discovery (SPEC-075.2)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ChannelName,
    ContentId,
    DiscoveredMediaItem,
)
from cresmo.infrastructure.adapters.media.feed import (
    YOUTUBE_RSS_MAX_ENTRIES,
    discover_channel_feed_items,
    extract_channel_url_from_info,
    is_rss_feed_window_complete,
    parse_youtube_atom_feed,
    resolve_youtube_rss_url,
)


def _identity_sanitize(name: str) -> str:
    return name.replace("/", "_").strip() or "Unknown_Channel"


def _build_atom_xml(
    entries: list[tuple[str, str, datetime]],
    channel_title: str = "Theory Channel",
) -> str:
    entry_blocks = []
    for vid, title, pub_dt in entries:
        iso_pub = pub_dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        entry_blocks.append(
            f"""
  <entry>
    <yt:videoId>{vid}</yt:videoId>
    <title>{title}</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v={vid}"/>
    <published>{iso_pub}</published>
  </entry>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <title>{channel_title}</title>
  <author><name>{channel_title}</name></author>
  {"".join(entry_blocks)}
</feed>"""


class TestResolveYoutubeRssUrl:
    """Tests for canonical RSS URL resolution."""

    def test_canonical_channel_uc_url(self) -> None:
        assert (
            resolve_youtube_rss_url("https://www.youtube.com/channel/UC1234567890123456789012")
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )

    def test_uploads_playlist_uu_maps_to_channel_id(self) -> None:
        assert (
            resolve_youtube_rss_url(
                "https://www.youtube.com/playlist?list=UU1234567890123456789012"
            )
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )

    def test_playlist_pl_maps_to_playlist_id(self) -> None:
        assert (
            resolve_youtube_rss_url("https://www.youtube.com/playlist?list=PLabcdef1234567890")
            == "https://www.youtube.com/feeds/videos.xml?playlist_id=PLabcdef1234567890"
        )

    def test_handle_or_non_canonical_returns_none(self) -> None:
        assert resolve_youtube_rss_url("https://www.youtube.com/@TheoryChannel") is None
        assert resolve_youtube_rss_url("https://example.com/feed") is None


class TestParseYoutubeAtomFeed:
    """Tests for stdlib Atom XML feed parsing."""

    def test_parses_valid_entries_and_skips_incomplete(self) -> None:
        pub = datetime(2026, 11, 20, 15, 30, 0, tzinfo=UTC)
        xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <title>Political / Philosophy</title>
  <entry>
    <yt:videoId>vid11111111</yt:videoId>
    <title>Pareto Elites</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=vid11111111"/>
    <published>{pub.isoformat()}</published>
  </entry>
  <entry>
    <yt:videoId></yt:videoId>
    <title>Missing Video Id</title>
  </entry>
  <entry>
    <yt:videoId>vid22222222</yt:videoId>
    <title>Mosca Ruling Class</title>
    <published>2026-11-19T10:00:00-02:00</published>
  </entry>
</feed>"""

        items = parse_youtube_atom_feed(xml_payload, _identity_sanitize)
        assert len(items) == 2
        assert items[0].content_id == ContentId("vid11111111")
        assert items[0].title == "Pareto Elites"
        assert items[0].channel_name == "Political _ Philosophy"
        assert items[0].media_url == "https://www.youtube.com/watch?v=vid11111111"
        assert items[0].published_at == pub

        assert items[1].content_id == ContentId("vid22222222")
        assert items[1].media_url == "https://www.youtube.com/watch?v=vid22222222"
        assert items[1].published_at.tzinfo == UTC
        assert items[1].published_at.hour == 12


class TestRssWindowCompleteness:
    """Tests for mathematical completeness guarantee of 15-entry Atom feeds."""

    def test_empty_items_returns_false(self) -> None:
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )
        assert is_rss_feed_window_complete([], query) is False

    def test_fewer_than_15_entries_is_complete(self) -> None:
        now = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
        xml = _build_atom_xml(
            [(f"vid{i:08d}", f"Title {i}", now - timedelta(hours=i)) for i in range(5)]
        )
        items = parse_youtube_atom_feed(xml, _identity_sanitize)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=30,
            max_videos=50,
        )
        assert is_rss_feed_window_complete(items, query, now=now) is True

    def test_15_entries_with_max_videos_le_15_is_complete(self) -> None:
        now = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
        xml = _build_atom_xml(
            [
                (f"vid{i:08d}", f"Title {i}", now - timedelta(hours=i))
                for i in range(YOUTUBE_RSS_MAX_ENTRIES)
            ]
        )
        items = parse_youtube_atom_feed(xml, _identity_sanitize)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=30,
            max_videos=15,
        )
        assert is_rss_feed_window_complete(items, query, now=now) is True

    def test_15_entries_all_within_lookback_and_max_gt_15_is_incomplete(self) -> None:
        now = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
        xml = _build_atom_xml(
            [
                (f"vid{i:08d}", f"Title {i}", now - timedelta(hours=i))
                for i in range(YOUTUBE_RSS_MAX_ENTRIES)
            ]
        )
        items = parse_youtube_atom_feed(xml, _identity_sanitize)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )
        assert is_rss_feed_window_complete(items, query, now=now) is False

    def test_15_entries_spanning_past_lookback_cutoff_is_complete(self) -> None:
        now = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
        entries = [(f"vid{i:08d}", f"Title {i}", now - timedelta(days=i)) for i in range(15)]
        xml = _build_atom_xml(entries)
        items = parse_youtube_atom_feed(xml, _identity_sanitize)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )
        assert is_rss_feed_window_complete(items, query, now=now) is True


class TestDiscoverChannelFeedItemsFastPath:
    """Tests for discover_channel_feed_items fast-path and yt-dlp fallback."""

    def test_rss_fast_path_hit_skips_yt_dlp(self) -> None:
        now = datetime.now(UTC)
        xml = _build_atom_xml(
            [(f"vid{i:08d}", f"Video {i}", now - timedelta(days=i)) for i in range(5)],
            channel_title="FastChannel",
        )
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=30,
            max_videos=3,
        )
        fetch_rss = MagicMock(return_value=xml)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=fetch_rss,
                enable_rss_fast_path=True,
            )

        assert len(items) == 3
        assert items[0].content_id == ContentId("vid00000000")
        assert items[0].channel_name == "FastChannel"
        fetch_rss.assert_called_once_with(
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )
        mock_ydl_cls.assert_not_called()

    def test_rss_incomplete_window_falls_back_to_yt_dlp(self) -> None:
        now = datetime.now(UTC)
        xml = _build_atom_xml(
            [(f"rss{i:08d}", f"RSS {i}", now - timedelta(hours=i)) for i in range(15)]
        )
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )
        fetch_rss = MagicMock(return_value=xml)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "title": "FallbackChan",
                "entries": [
                    {
                        "id": "ytdlp111111",
                        "title": "From YT-DLP",
                        "upload_date": now.strftime("%Y%m%d"),
                    }
                ],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=fetch_rss,
                enable_rss_fast_path=True,
            )

        assert len(items) == 1
        assert items[0].content_id == ContentId("ytdlp111111")
        mock_ydl_cls.assert_called_once()

    def test_rss_error_degrades_gracefully_to_yt_dlp(self) -> None:
        now = datetime.now(UTC)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=10,
        )
        fetch_rss = MagicMock(side_effect=RuntimeError("RSS 503"))

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "title": "FallbackChan",
                "entries": [
                    {
                        "id": "ytdlp222222",
                        "title": "Recovered Video",
                        "upload_date": now.strftime("%Y%m%d"),
                    }
                ],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=fetch_rss,
                enable_rss_fast_path=True,
            )

        assert len(items) == 1
        assert items[0].content_id == ContentId("ytdlp222222")
        mock_ydl_cls.assert_called_once()

    def test_rss_disabled_bypasses_fetch_and_calls_yt_dlp(self) -> None:
        now = datetime.now(UTC)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=10,
        )
        fetch_rss = MagicMock()

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "title": "DirectChan",
                "entries": [
                    {
                        "id": "ytdlp333333",
                        "title": "Direct YT-DLP",
                        "upload_date": now.strftime("%Y%m%d"),
                    }
                ],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=fetch_rss,
                enable_rss_fast_path=False,
            )

        fetch_rss.assert_not_called()
        assert len(items) == 1
        assert items[0].content_id == ContentId("ytdlp333333")


class TestFeedBoundaryAndFallbackContracts:
    """Tests covering boundary conditions, Atom edge cases, yt-dlp fallback, and info URL extraction."""

    def test_resolve_youtube_rss_url_uu_length_boundary(self) -> None:
        # Exactly MIN_CANONICAL_CHANNEL_ID_LENGTH (4) maps UU -> UC channel_id
        assert (
            resolve_youtube_rss_url("https://www.youtube.com/playlist?list=UU12")
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC12"
        )
        # 3 chars (below MIN_CANONICAL_CHANNEL_ID_LENGTH=4) stays playlist_id
        assert (
            resolve_youtube_rss_url("https://www.youtube.com/playlist?list=UU1")
            == "https://www.youtube.com/feeds/videos.xml?playlist_id=UU1"
        )

    def test_parse_atom_feed_edge_cases_links_authors_and_dates(self) -> None:
        xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <author><name>Author Fallback Chan</name></author>
  <entry>
    <yt:videoId>vid11111111</yt:videoId>
    <link rel="self" href="https://www.youtube.com/ignore"/>
    <link rel="alternate" href="  https://www.youtube.com/watch?v=custom_alt_1  "/>
    <author><name>Entry Author</name></author>
    <published>2026-11-20T10:00:00</published>
  </entry>
  <entry>
    <yt:videoId>vid22222222</yt:videoId>
    <title>Alt Link And Entry Author</title>
    <link rel="self" href="https://www.youtube.com/ignore"/>
    <link rel="alternate" href="  https://www.youtube.com/watch?v=custom_alt_2  "/>
    <author><name>Entry Author</name></author>
    <published>2026-11-20T10:00:00</published>
  </entry>
  <entry>
    <yt:videoId>vid33333333</yt:videoId>
    <title>Default Rel Link</title>
    <link href="https://www.youtube.com/watch?v=default_rel_3"/>
    <published>not-an-iso-date</published>
  </entry>
  <entry>
    <yt:videoId>vid44444444</yt:videoId>
    <title>Empty Href Fallback</title>
    <link rel="alternate" href="   "/>
  </entry>
  <entry>
    <yt:videoId>vid44444445</yt:videoId>
    <title>Missing Href Attr Fallback</title>
    <link rel="alternate"/>
  </entry>
</feed>"""

        items = parse_youtube_atom_feed(xml_payload, _identity_sanitize)
        assert len(items) == 4

        assert items[0].content_id == ContentId("vid22222222")
        assert items[0].media_url == "https://www.youtube.com/watch?v=custom_alt_2"
        assert items[0].channel_name == "Entry Author"
        assert items[0].published_at == datetime(2026, 11, 20, 10, 0, 0, tzinfo=UTC)

        assert items[1].content_id == ContentId("vid33333333")
        assert items[1].media_url == "https://www.youtube.com/watch?v=default_rel_3"
        assert items[1].channel_name == "Author Fallback Chan"
        assert items[1].published_at.tzinfo == UTC

        assert items[2].content_id == ContentId("vid44444444")
        assert items[2].media_url == "https://www.youtube.com/watch?v=vid44444444"
        assert items[2].published_at.tzinfo == UTC

        assert items[3].content_id == ContentId("vid44444445")
        assert items[3].media_url == "https://www.youtube.com/watch?v=vid44444445"

    def test_parse_atom_feed_unknown_channel_fallback_and_invalid_video_id(self) -> None:
        xml_unknown = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <yt:videoId>vid55555555</yt:videoId>
    <title>No Channel Name</title>
  </entry>
</feed>"""
        items = parse_youtube_atom_feed(xml_unknown, _identity_sanitize)
        assert len(items) == 1
        assert items[0].channel_name == "Unknown_Channel"

        xml_bad_id = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <title>Chan</title>
  <entry>
    <yt:videoId>bad id!</yt:videoId>
    <title>Invalid ID</title>
  </entry>
</feed>"""
        with pytest.raises(DomainValidationError, match="bad id!"):
            parse_youtube_atom_feed(xml_bad_id, _identity_sanitize)

    def test_is_rss_feed_window_complete_boundaries_and_naive_datetimes(self) -> None:
        now_utc = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )

        # Boundary: oldest == cutoff (now - 7 days) is NOT strictly older -> False
        exact_cutoff_items = [
            DiscoveredMediaItem(
                content_id=ContentId(f"vid{i:08d}"),
                title=f"T{i}",
                published_at=now_utc - timedelta(days=7 if i == 14 else 1),
                media_url=f"https://www.youtube.com/watch?v=vid{i:08d}",
                channel_name=ChannelName("Chan"),
            )
            for i in range(YOUTUBE_RSS_MAX_ENTRIES)
        ]
        assert is_rss_feed_window_complete(exact_cutoff_items, query, now=now_utc) is False

        # Naive `now` and naive `published_at` older than cutoff -> True
        naive_published = datetime(2026, 11, 1, 12, 0, tzinfo=UTC).replace(tzinfo=None)
        naive_now = datetime(2026, 11, 23, 12, 0, tzinfo=UTC).replace(tzinfo=None)
        naive_items = [
            DiscoveredMediaItem(
                content_id=ContentId(f"vid{i:08d}"),
                title=f"T{i}",
                published_at=naive_published,
                media_url=f"https://www.youtube.com/watch?v=vid{i:08d}",
                channel_name=ChannelName("Chan"),
            )
            for i in range(YOUTUBE_RSS_MAX_ENTRIES)
        ]
        assert is_rss_feed_window_complete(naive_items, query, now=naive_now) is True
        # Default now=None uses current UTC time
        with patch("cresmo.infrastructure.adapters.media.feed.datetime", wraps=datetime) as mock_dt:
            assert is_rss_feed_window_complete(naive_items, query) is True
            mock_dt.now.assert_called_once_with(UTC)

    def test_discover_channel_feed_items_default_flag_15_entries_and_logs(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        now = datetime.now(UTC)
        xml_15 = _build_atom_xml(
            [(f"vid{i:08d}", f"V{i}", now - timedelta(hours=i)) for i in range(15)]
        )
        query_15 = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=15,
        )
        fetch_rss = MagicMock(return_value=xml_15)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            items = discover_channel_feed_items(
                query=query_15,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=fetch_rss,
            )

        assert len(items) == 15
        mock_ydl_cls.assert_not_called()
        success_records = [
            r for r in caplog.records if r.getMessage() == "YouTube Atom RSS fast-path succeeded"
        ]
        assert len(success_records) == 1
        assert (
            getattr(success_records[0], "rss_url", None)
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )
        assert getattr(success_records[0], "entries_count", None) == 15

    def test_discover_channel_feed_items_logs_incomplete_and_error_fallbacks(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        now = datetime.now(UTC)
        xml_15 = _build_atom_xml(
            [(f"vid{i:08d}", f"V{i}", now - timedelta(hours=i)) for i in range(15)]
        )
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=50,
        )
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"entries": []}
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=MagicMock(return_value=xml_15),
            )

        incomplete_records = [
            r
            for r in caplog.records
            if r.getMessage() == "YouTube Atom RSS window incomplete; falling back to yt-dlp"
        ]
        assert len(incomplete_records) == 1
        rec = incomplete_records[0]
        assert (
            getattr(rec, "rss_url", None)
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )
        assert getattr(rec, "entries_count", None) == 15
        assert getattr(rec, "max_videos", None) == 50
        assert getattr(rec, "lookback_days", None) == 7

        caplog.clear()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"entries": []}
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                fetch_rss_xml=MagicMock(side_effect=RuntimeError("RSS 503")),
            )

        error_records = [
            r
            for r in caplog.records
            if r.getMessage()
            == "YouTube Atom RSS fast-path failed (RSS 503); falling back to yt-dlp."
        ]
        assert len(error_records) == 1
        assert (
            getattr(error_records[0], "rss_url", None)
            == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890123456789012"
        )

    def test_discover_channel_feed_items_yt_dlp_opts_retry_filtering_and_errors(self) -> None:
        handle_url = "https://www.youtube.com/@TheoryChannel"
        expected_uploads_url = "https://www.youtube.com/@TheoryChannel/videos"
        query = ChannelFeedQuery(channel_url=handle_url, lookback_days=30, max_videos=25)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            # First call to /videos returns empty -> triggers retry on original channel_url
            mock_ydl.extract_info.side_effect = [
                {"entries": []},
                {
                    "uploader": "UploaderFallbackChan",
                    "entries": [
                        None,
                        "invalid_string_entry",
                        {"id": "", "title": "Empty ID"},
                        {"id": "vid00000000", "title": ""},
                        {
                            "id": "vid11111111",
                            "title": "First Valid",
                            "upload_date": "20261110",
                        },
                        {
                            "id": "vid22222222",
                            "title": "Second Valid",
                            "uploader": "EntryUploader",
                            "url": "https://www.youtube.com/shorts/vid22222222",
                        },
                    ],
                },
            ]
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = discover_channel_feed_items(
                query=query,
                ydl_opts={"cookiefile": "/tmp/c.txt"},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
            )

        opts = mock_ydl_cls.call_args[0][0]
        assert opts["extract_flat"] is True
        assert opts["playlistend"] == 25
        assert opts["quiet"] is True
        assert opts["no_warnings"] is True
        assert opts["cookiefile"] == "/tmp/c.txt"
        assert mock_ydl.extract_info.call_args_list == [
            ((expected_uploads_url,), {"download": False}),
            ((handle_url,), {"download": False}),
        ]

        assert len(items) == 2
        assert items[0].content_id == ContentId("vid11111111")
        assert items[0].media_url == "https://www.youtube.com/watch?v=vid11111111"
        assert items[0].channel_name == "UploaderFallbackChan"
        assert items[0].published_at == datetime(2026, 11, 10, 0, 0, tzinfo=UTC)

        assert items[1].channel_name == "EntryUploader"
        assert items[1].media_url == "https://www.youtube.com/shorts/vid22222222"
        assert items[1].published_at.tzinfo == UTC

        # Non-empty first extract_info result with target_url != query.channel_url must NOT retry
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "title": "InfoTitleChan",
                "uploader": "IgnoredUploader",
                "entries": [{"id": "vid44444444", "title": "Single Hit"}],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            hit_items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
            )
            mock_ydl.extract_info.assert_called_once_with(expected_uploads_url, download=False)
            assert len(hit_items) == 1
            assert hit_items[0].channel_name == "InfoTitleChan"

    def test_discover_channel_feed_items_yt_dlp_no_retry_when_same_url_and_defaults(self) -> None:
        same_url = "https://www.youtube.com/@TheoryChannel/videos"
        query = ChannelFeedQuery(channel_url=same_url, lookback_days=7, max_videos=10)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = None
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            assert (
                discover_channel_feed_items(
                    query=query,
                    ydl_opts={},
                    handle_error=MagicMock(),
                    sanitize_fs_name=_identity_sanitize,
                    enable_rss_fast_path=False,
                )
                == []
            )
            mock_ydl.extract_info.assert_called_once_with(same_url, download=False)

        # Fallback channel_title="Unknown_Channel" and invalid entry id
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "entries": [{"id": "vid33333333", "title": "Default Chan Video"}],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=MagicMock(),
                sanitize_fs_name=_identity_sanitize,
                enable_rss_fast_path=False,
            )
            assert len(items) == 1
            assert items[0].channel_name == "Unknown_Channel"

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "entries": [{"id": "bad id!", "title": "Bad ID"}],
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(DomainValidationError, match="bad id!"):
                discover_channel_feed_items(
                    query=query,
                    ydl_opts={},
                    handle_error=MagicMock(),
                    sanitize_fs_name=_identity_sanitize,
                    enable_rss_fast_path=False,
                )

        # yt_dlp exception delegates exact exc to handle_error and returns []
        err = RuntimeError("yt-dlp failure")
        handle_error = MagicMock()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = err
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            res = discover_channel_feed_items(
                query=query,
                ydl_opts={},
                handle_error=handle_error,
                sanitize_fs_name=_identity_sanitize,
                enable_rss_fast_path=False,
            )
        assert res == []
        handle_error.assert_called_once_with(err)

    def test_extract_channel_url_from_info_variants(self) -> None:
        assert extract_channel_url_from_info(None) is None
        assert extract_channel_url_from_info({}) is None
        non_dict: Any = "not-a-dict"
        assert extract_channel_url_from_info(non_dict) is None

        assert (
            extract_channel_url_from_info({"uploader_id": "UC1234567890123456789012"})
            == "https://www.youtube.com/playlist?list=UU1234567890123456789012"
        )
        assert (
            extract_channel_url_from_info({"channel_id": "@CustomHandle"})
            == "https://www.youtube.com/@CustomHandle/videos"
        )
        assert (
            extract_channel_url_from_info(
                {"uploader_url": "https://www.youtube.com/@UploaderHandle"}
            )
            == "https://www.youtube.com/@UploaderHandle/videos"
        )
        assert (
            extract_channel_url_from_info(
                {"channel_url": "https://www.youtube.com/channel/UC1234567890123456789012"}
            )
            == "https://www.youtube.com/playlist?list=UU1234567890123456789012"
        )
