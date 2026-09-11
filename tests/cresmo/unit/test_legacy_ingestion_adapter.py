"""Unit tests for LegacyIsbIngestionAdapter ACL.

Validates that legacy isb.ai calls are cleanly wrapped and translated into
domain entities without leaking sys.path or global state.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cresmo.domain.exceptions import IngestionNetworkError, RateLimitExceededError
from cresmo.domain.value_objects import ContentId
from cresmo.infrastructure.adapters.legacy_isb_ingestion_adapter import (
    LegacyIsbIngestionAdapter,
)


class TestLegacyIsbIngestionAdapter:
    """Hermetic unit tests for legacy media ingestion ACL."""

    def test_ingest_single_video_success(self, tmp_path: Path) -> None:
        raw_output_file = tmp_path / "Political Theory" / "dQw4w9WgXcQ.txt"
        raw_output_file.parent.mkdir(parents=True, exist_ok=True)
        raw_output_file.write_text(
            "---\nid: dQw4w9WgXcQ\nchannel: Political Theory\n---\nRaw spoken transcript body.",
            encoding="utf-8",
        )

        adapter = LegacyIsbIngestionAdapter(isb_dir=tmp_path)
        with patch.object(adapter, "_call_legacy_sync_single", return_value=raw_output_file):
            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
            )

        assert transcript is not None
        assert transcript.content_id == ContentId("dQw4w9WgXcQ")
        assert transcript.channel_name == "Political Theory"
        assert "Raw spoken transcript body." in transcript.body

    def test_ingest_single_video_rate_limit_translation(self, tmp_path: Path) -> None:
        adapter = LegacyIsbIngestionAdapter(isb_dir=tmp_path)
        with (
            patch.object(
                adapter,
                "_call_legacy_sync_single",
                side_effect=Exception("HTTP Error 429: Too Many Requests"),
            ),
            pytest.raises(RateLimitExceededError),
        ):
            adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
            )

    def test_ingest_single_video_generic_error_translation(self, tmp_path: Path) -> None:
        adapter = LegacyIsbIngestionAdapter(isb_dir=tmp_path)
        with (
            patch.object(
                adapter,
                "_call_legacy_sync_single",
                side_effect=Exception("Network connection failed"),
            ),
            pytest.raises(IngestionNetworkError),
        ):
            adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
            )

    def test_discover_channel_feed_success(self, tmp_path: Path) -> None:
        from cresmo.domain.value_objects import ChannelFeedQuery

        adapter = LegacyIsbIngestionAdapter(isb_dir=tmp_path)

        mock_entries = [
            {
                "id": "vid00000001",
                "title": "Quantum Mechanics Intro",
                "url": "https://youtube.com/watch?v=vid00000001",
                "timestamp": 1726000000,
            },
            {
                "id": "vid00000002",
                "title": "Quantum Entanglement",
                "url": "https://youtube.com/watch?v=vid00000002",
                "timestamp": 1726001000,
            },
        ]
        mock_info = {
            "channel": "Quantum Channel",
            "entries": mock_entries,
        }

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = mock_ydl_cls.return_value.__enter__.return_value
            mock_ydl.extract_info.return_value = mock_info

            query = ChannelFeedQuery(channel_url="https://youtube.com/@QuantumChannel")
            items = adapter.discover_channel_feed(query)

            assert len(items) == 2
            assert items[0].content_id.value == "vid00000001"
            assert items[0].title == "Quantum Mechanics Intro"
            assert items[0].channel_name == "Quantum Channel"
            assert items[1].content_id.value == "vid00000002"
