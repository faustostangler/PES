"""Hermetic unit tests for Zero-Read Lake Scanning and Deferred Adapter Initialization.

Conforms to:
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - ADR-047: Discovery Lake I/O Optimization and Lazy Scan
    - ADR-055: Comprehensive Presentation CLI Lazy Dispatching, Zero-Read Lake Scanning, and Deferred Adapter Initialization
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cresmo.application.use_cases.discovery import (
    BatchDiscoveryQuery,
    DiscoverBatchSourcesUseCase,
    LakeScannerService,
    _BatchSourceAccumulator,
)


class TestZeroReadLakeScanner:
    """Test suite asserting zero file reads during lake scanning."""

    def test_scan_raw_lake_extracts_metadata_without_file_open(self, tmp_path: Path) -> None:
        """Verify scan_raw_lake extracts video_id and channel without opening any .md files on disk."""
        raw_dir = tmp_path / "raw"
        chan_dir = raw_dir / "ChannelNameAlpha"
        chan_dir.mkdir(parents=True, exist_ok=True)

        vid_file = chan_dir / "dQw4w9WgXcQ.md"
        vid_file.write_text(
            "---\nvideo_id: dQw4w9WgXcQ\nchannel: https://www.youtube.com/@ChannelNameAlpha\n---\nBody",
            encoding="utf-8",
        )

        acc = _BatchSourceAccumulator()

        with patch.object(
            Path,
            "open",
            side_effect=AssertionError("Path.open should not be called in zero-read scan"),
        ):
            local_map = LakeScannerService.scan_raw_lake(
                raw_dir=raw_dir,
                scan_raw=True,
                acc=acc,
                extract_frontmatter=False,
            )

        assert "dQw4w9WgXcQ" in local_map
        assert "ChannelNameAlpha" in local_map["dQw4w9WgXcQ"]
        assert "dQw4w9WgXcQ" in acc.seen_vids

    def test_discover_batch_sources_skips_lake_scan_when_scan_raw_and_crawler_disabled(
        self, tmp_path: Path
    ) -> None:
        """Verify DiscoverBatchSourcesUseCase does not scan raw lake when scan_raw=False and crawler is disabled."""
        q = BatchDiscoveryQuery(
            scan_raw=False,
            enable_channel_crawler=False,
            raw_dir=tmp_path / "raw",
            playlist_priority_path=tmp_path / "priority.txt",
            playlist_path=tmp_path / "playlist.txt",
        )
        use_case = DiscoverBatchSourcesUseCase()

        with patch.object(LakeScannerService, "scan_raw_lake") as mock_scan:
            # Consume generator
            _ = list(use_case.execute(query=q))
            mock_scan.assert_not_called()
