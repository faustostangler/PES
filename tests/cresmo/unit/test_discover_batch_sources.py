"""Unit tests for DiscoverBatchSourcesUseCase.

Verifies raw transcript lake scanning, frontmatter parsing, concurrent channel resolution,
and channel feed discovery per ADR-003 and Clean Hexagonal Architecture.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
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
