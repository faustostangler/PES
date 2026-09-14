"""Unit tests for DiscoverBatchSourcesUseCase.

Verifies raw transcript lake scanning, frontmatter parsing, concurrent channel resolution,
and channel feed discovery per ADR-003 and Clean Hexagonal Architecture.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
    extract_raw_file_metadata,
)
from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
from cresmo.infrastructure.config import CresmoSettings


def _create_mock_media_item(
    content_id_str: str,
    media_url: str,
    title: str = "Test Video",
    channel_name: str = "Test Channel",
) -> DiscoveredMediaItem:
    return DiscoveredMediaItem(
        content_id=ContentId(content_id_str),
        title=title,
        published_at=datetime.now(UTC),
        media_url=media_url,
        channel_name=channel_name,
    )


class TestDiscoverBatchSourcesUseCase:
    """Test suite for DiscoverBatchSourcesUseCase."""

    def test_extract_raw_file_metadata_parses_frontmatter(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.md"
        file.write_text(
            "---\ntitle: Sample Video\nchannel: https://www.youtube.com/@channel1\nvideo_id: abc12345\n---\nBody",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(file)
        assert meta["title"] == "Sample Video"
        assert meta["channel"] == "https://www.youtube.com/@channel1"
        assert meta["video_id"] == "abc12345"

    def test_discover_sources_from_raw_lake(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        (raw_dir / "vid1.md").write_text(
            "---\ntitle: Video 1\nchannel: https://www.youtube.com/@chan1\nvideo_id: 11111111\n---\nText",
            encoding="utf-8",
        )
        (raw_dir / "vid2.md").write_text(
            "---\ntitle: Video 2\nchannel: https://www.youtube.com/@chan1\nvideo_id: 22222222\n---\nText",
            encoding="utf-8",
        )
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.discover_channel_feed.return_value = []

        settings = CresmoSettings()
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=settings,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=raw_dir,
            scan_raw=True,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert all(s.kind == "file" for s in sources)
        # Channel was discovered from frontmatter and queried exactly once
        assert mock_ingestion.discover_channel_feed.call_count == 1

    def test_discover_sources_resolves_channel_from_video_and_discovers_feed(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://www.youtube.com/watch?v=seed12345\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCDiscovered"
        )
        new_item = _create_mock_media_item(
            content_id_str="disc99999",
            media_url="https://www.youtube.com/watch?v=disc99999",
        )
        mock_ingestion.discover_channel_feed.return_value = [new_item]

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=True,
            lookback_days=365,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        mock_ingestion.extract_channel_url_from_video.assert_called_once_with(
            "https://www.youtube.com/watch?v=seed12345"
        )
        feed_query = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert feed_query.channel_url == "https://www.youtube.com/channel/UCDiscovered"
        assert feed_query.lookback_days == 365

        targets = [s.target for s in sources]
        assert "https://www.youtube.com/watch?v=seed12345" in targets
        assert "https://www.youtube.com/watch?v=disc99999" in targets

    def test_discover_sources_deduplicates_channels_across_multiple_videos(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text(
            "https://www.youtube.com/watch?v=video11111\nhttps://www.youtube.com/watch?v=video22222\n",
            encoding="utf-8",
        )

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCSameChannel"
        )
        mock_ingestion.discover_channel_feed.return_value = []

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=True,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        assert mock_ingestion.extract_channel_url_from_video.call_count == 2
        assert mock_ingestion.discover_channel_feed.call_count == 1
        assert len(sources) == 2

    def test_batch_source_display_name(self) -> None:
        file_source = BatchSource(kind="file", target="/lake/transcripts/lecture1.md")
        assert file_source.display_name == "lecture1.md"
        url_source = BatchSource(kind="url", target="https://youtube.com/watch?v=12345")
        assert url_source.display_name == "https://youtube.com/watch?v=12345"

    def test_extract_raw_file_metadata_channel_formats_and_error(self, tmp_path: Path) -> None:
        # Test @handle channel format
        f_handle = tmp_path / "handle.md"
        f_handle.write_text("---\nchannel: @TheoryCraft\n---\nBody", encoding="utf-8")
        meta_handle = extract_raw_file_metadata(f_handle)
        assert meta_handle["channel"] == "https://www.youtube.com/@TheoryCraft"

        # Test bare channel ID format
        f_bare = tmp_path / "bare.md"
        f_bare.write_text("---\nchannel_id: UCxyz123\n---\nBody", encoding="utf-8")
        meta_bare = extract_raw_file_metadata(f_bare)
        assert meta_bare["channel"] == "https://www.youtube.com/channel/UCxyz123"

        # Test unreadable / non-existent file returns empty dict
        assert extract_raw_file_metadata(tmp_path / "non_existent.md") == {}

    def test_explicit_manifest_override_and_progress_callback(self, tmp_path: Path) -> None:
        manifest = tmp_path / "custom_manifest.txt"
        manifest.write_text(
            "https://youtube.com/watch?v=explicit1\n# Comment\nhttps://youtube.com/watch?v=explicit2\n",
            encoding="utf-8",
        )

        notifications: list[str] = []
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=MagicMock(),
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(explicit_manifest=manifest)
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert [s.target for s in sources] == [
            "https://youtube.com/watch?v=explicit1",
            "https://youtube.com/watch?v=explicit2",
        ]
        assert any("Loaded 2 URLs" in msg for msg in notifications)

    def test_priority_sources(self, tmp_path: Path) -> None:
        priority_dir = tmp_path / "priority_texts"
        priority_dir.mkdir()
        (priority_dir / "prio1.md").write_text("# Priority doc", encoding="utf-8")

        priority_txt = tmp_path / "playlist-priority.txt"
        priority_txt.write_text("https://youtube.com/watch?v=prioUrl1\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        query = BatchDiscoveryQuery(
            priority_texts_dir=priority_dir,
            playlist_priority_path=priority_txt,
            playlist_path=tmp_path / "empty_playlist.txt",
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
        )
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert sources[0].kind == "file"
        assert "prio1.md" in sources[0].target
        assert sources[1].kind == "url"
        assert sources[1].target == "https://youtube.com/watch?v=prioUrl1"

    def test_channel_feed_in_playlist_and_naive_datetime_filtering(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text(
            "https://www.youtube.com/@ExplicitChannel\nhttps://youtube.com/watch?v=videoWithRawMatch\n",
            encoding="utf-8",
        )

        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        (raw_dir / "videoWithRawMatch.md").write_text(
            "---\nvideo_id: videoWithRawMatch\nchannel: https://www.youtube.com/@RawChannel\n---\nContent",
            encoding="utf-8",
        )

        mock_ingestion = MagicMock()
        now_naive = datetime.now(UTC).replace(tzinfo=None)
        old_naive = (datetime.now(UTC) - timedelta(days=400)).replace(tzinfo=None)
        mock_ingestion.discover_channel_feed.return_value = [
            DiscoveredMediaItem(
                content_id=ContentId("fresh111"),
                title="Fresh Naive Date Video",
                published_at=now_naive,
                media_url="https://youtube.com/watch?v=fresh111",
                channel_name="ExplicitChannel",
            ),
            DiscoveredMediaItem(
                content_id=ContentId("old22222"),
                title="Old Video",
                published_at=old_naive,
                media_url="https://youtube.com/watch?v=old22222",
                channel_name="ExplicitChannel",
            ),
        ]

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=raw_dir,
            scan_raw=False,
            lookback_days=30,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        targets = [s.target for s in sources]
        assert "https://youtube.com/watch?v=fresh111" in targets
        assert "https://youtube.com/watch?v=old22222" not in targets

    def test_channel_lookup_and_probe_exception_resilience(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://youtube.com/watch?v=failLookup\n", encoding="utf-8")

        notifications: list[str] = []
        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.side_effect = RuntimeError(
            "Extraction failed"
        )

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 1
        assert sources[0].target == "https://youtube.com/watch?v=failLookup"
        assert any("Warning: Failed to resolve channel" in msg for msg in notifications)

    def test_probe_single_channel_exception_handling(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://www.youtube.com/@CrashingChannel\n", encoding="utf-8")

        notifications: list[str] = []
        mock_ingestion = MagicMock()
        mock_ingestion.discover_channel_feed.side_effect = ConnectionError("Channel feed down")

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 0
        assert any("Warning: Failed to probe" in msg for msg in notifications)
