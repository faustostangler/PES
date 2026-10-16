"""Unit tests for 'cresmo sync' presentation command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-003: PES Production Architecture & Telemetry
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-003: Channel Synchronization Specifications
"""

from pathlib import Path
from types import SimpleNamespace as Namespace
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    PipelineStatus,
    SyncFilterCriteria,
    SyncSummary,
)
from cresmo.presentation.cli import main
from cresmo.presentation.commands.sync import (
    _describe_mode,
    _read_manifest_lines,
    _resolve_channels_for_sync,
    _sync_channel_list,
    _sync_direct_videos,
    handle_sync,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class TestSyncCommand:
    """Test suite for cresmo sync command and private helpers."""

    def test_sync_cli_help(self) -> None:
        """Verify sync CLI displays help and options."""
        assert main(["sync", "--help"]) == EXIT_SUCCESS

    def test_describe_mode(self) -> None:
        """Verify _describe_mode produces exact descriptive strings for all filter criteria combinations."""
        assert _describe_mode(SyncFilterCriteria()) == "full manifest"

        c1 = SyncFilterCriteria(channels=("ancapsu", "mises"))
        assert _describe_mode(c1) == "channels=ancapsu,mises"

        c2 = SyncFilterCriteria(categories=("politics_br", "tech_ai"))
        assert _describe_mode(c2) == "categories=politics_br,tech_ai"

        c3 = SyncFilterCriteria(video_ids=("vid1", "vid2"))
        assert _describe_mode(c3) == "videos=vid1,vid2"

        c4 = SyncFilterCriteria(
            channels=("ch1",),
            categories=("cat1",),
            video_ids=("v1",),
        )
        assert _describe_mode(c4) == "channels=ch1, categories=cat1, videos=v1"

    def test_read_manifest_lines(self, tmp_path: Path) -> None:
        """Verify _read_manifest_lines strips whitespace, ignores empty lines, comments, and handles invalid paths."""
        assert _read_manifest_lines(None) == []
        assert _read_manifest_lines(tmp_path / "nonexistent.txt") == []

        manifest_file = tmp_path / "playlist.txt"
        manifest_file.write_text(
            "# Comment line 1\n"
            "   \n"
            "https://youtube.com/@channel1\n"
            "# Comment line 2\n"
            "https://youtube.com/@channel2   \n"
            "\n"
            "# Another comment\n"
            "https://youtube.com/@channel3\n",
            encoding="utf-8",
        )
        lines = _read_manifest_lines(manifest_file)
        assert lines == [
            "https://youtube.com/@channel1",
            "https://youtube.com/@channel2",
            "https://youtube.com/@channel3",
        ]

    def test_resolve_channels_for_sync(self, tmp_path: Path) -> None:
        """Verify _resolve_channels_for_sync handles explicit tokens (URL vs handle) and manifest reading."""
        # 1. Explicit tokens: http, https, and bare handle
        criteria_explicit = SyncFilterCriteria(
            channels=("http://custom.org/feed", "https://youtube.com/@ancapsu", "@mises")
        )
        resolved = _resolve_channels_for_sync(None, criteria_explicit)
        assert resolved[0] == "http://custom.org/feed"
        assert resolved[1] == "https://youtube.com/@ancapsu"
        assert resolved[2] == "https://www.youtube.com/@mises/videos"

        # 2. Manifest reading with empty criteria
        manifest = tmp_path / "manifest.txt"
        manifest.write_text(
            "https://www.youtube.com/@FabioAkita\nhttps://www.youtube.com/@ancapsu\n",
            encoding="utf-8",
        )
        all_channels = _resolve_channels_for_sync(manifest, SyncFilterCriteria())
        assert len(all_channels) == 2
        assert "https://www.youtube.com/@FabioAkita/videos" in all_channels
        assert "https://www.youtube.com/@ancapsu/videos" in all_channels

    def test_sync_direct_videos_success_and_failure(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify _sync_direct_videos formats URLs, constructs queries with max_videos=1, and respects exit codes."""
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = [
            SyncSummary(
                channel_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                total_discovered=1,
                processed_count=1,
                skipped_count=0,
                failed_count=0,
                duration_seconds=1.0,
                status=PipelineStatus.COMPLETED,
            ),
            SyncSummary(
                channel_url="https://youtube.com/watch?v=alreadyHttp",
                total_discovered=1,
                processed_count=0,
                skipped_count=1,
                failed_count=0,
                duration_seconds=0.5,
                status=PipelineStatus.COMPLETED,
            ),
        ]

        args = Namespace(
            lookback=30,
            dry_run=True,
            force_refresh=False,
        )

        code = _sync_direct_videos(
            use_case=mock_use_case,
            video_ids=["dQw4w9WgXcQ", "https://youtube.com/watch?v=alreadyHttp"],
            args=args,
        )
        assert code == EXIT_SUCCESS
        assert mock_use_case.execute.call_count == 2

        # Verify first call constructed full watch URL
        q1 = mock_use_case.execute.call_args_list[0].kwargs["query"]
        assert q1.channel_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert q1.max_videos == 1
        assert q1.lookback_days == 30

        captured = capsys.readouterr()
        assert "[video] dQw4w9WgXcQ: 1 processed, 0 skipped, 0 failed\n" in captured.out
        assert (
            "[video] https://youtube.com/watch?v=alreadyHttp: 0 processed, 1 skipped, 0 failed\n"
            in captured.out
        )

        # Test failure case returns EXIT_INTERNAL_ERROR (1)
        mock_use_case.reset_mock()
        mock_use_case.execute.side_effect = None
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://www.youtube.com/watch?v=failVid",
            total_discovered=1,
            processed_count=0,
            skipped_count=0,
            failed_count=1,
            duration_seconds=1.0,
            status=PipelineStatus.FAILED_INGESTION,
        )
        code_fail = _sync_direct_videos(
            use_case=mock_use_case,
            video_ids=["failVid"],
            args=args,
        )
        assert code_fail == EXIT_INTERNAL_ERROR

    def test_sync_channel_list_summary_and_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify _sync_channel_list executes channels, logs table, and returns EXIT_SUCCESS or EXIT_INTERNAL_ERROR."""
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = [
            SyncSummary(
                channel_url="https://youtube.com/@alpha",
                total_discovered=5,
                processed_count=3,
                skipped_count=2,
                failed_count=0,
                duration_seconds=2.4,
                status=PipelineStatus.COMPLETED,
            ),
            SyncSummary(
                channel_url="https://youtube.com/@beta",
                total_discovered=2,
                processed_count=1,
                skipped_count=1,
                failed_count=0,
                duration_seconds=1.2,
                status=PipelineStatus.COMPLETED,
            ),
        ]

        args = Namespace(
            lookback=60,
            max_videos=50,
            dry_run=False,
            force_refresh=True,
        )

        channels = ["https://youtube.com/@alpha", "https://youtube.com/@beta"]
        code = _sync_channel_list(mock_use_case, channels, args)
        assert code == EXIT_SUCCESS

        captured = capsys.readouterr()
        assert (
            "[https://youtube.com/@alpha] discovered=5 processed=3 skipped=2 failed=0 (2.4s)\n"
            in captured.out
        )
        assert (
            "[https://youtube.com/@beta] discovered=2 processed=1 skipped=1 failed=0 (1.2s)\n"
            in captured.out
        )
        assert "Channel Synchronization Summary:\n" in captured.out
        assert "- Channels synced: 2\n" in captured.out
        assert "- Total in Window: 7\n" in captured.out
        assert "- Processed: 4\n" in captured.out
        assert "- Skipped (Idempotent): 3\n" in captured.out
        assert "- Failed: 0\n" in captured.out

        # Failure return test
        mock_use_case.reset_mock()
        mock_use_case.execute.side_effect = None
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@fail",
            total_discovered=1,
            processed_count=0,
            skipped_count=0,
            failed_count=1,
            duration_seconds=0.5,
            status=PipelineStatus.FAILED_INGESTION,
        )
        assert (
            _sync_channel_list(mock_use_case, ["https://youtube.com/@fail"], args)
            == EXIT_INTERNAL_ERROR
        )

    def test_handle_sync_empty_matching_channels(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        """Verify handle_sync with no matching channels outputs guidance and returns EXIT_SUCCESS (0)."""
        manifest = tmp_path / "empty_manifest.txt"
        manifest.write_text("", encoding="utf-8")

        mock_settings = MagicMock()
        mock_settings.playlist_path = manifest

        args = Namespace(
            channels=[],
            categories=["unknown_cat"],
            video_ids=[],
            manifest=manifest,
            batch_size=None,
            lookback=30,
            max_videos=10,
            dry_run=False,
            force_refresh=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.sync.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch("cresmo.presentation.commands.sync.build_sync_channel_use_case"),
        ):
            code = handle_sync(args)
            assert code == EXIT_SUCCESS

            captured = capsys.readouterr()
            assert (
                f"No channels found matching filter (categories=unknown_cat). Verify manifest at '{manifest}' and filter criteria.\n"
                in captured.out
            )

    def test_handle_sync_exceptions_mapped_to_exit_codes(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify all domain, network, validation, and generic exceptions map to canonical exit codes."""
        mock_settings = MagicMock()
        args = Namespace(
            channels=["https://youtube.com/@test"],
            categories=[],
            video_ids=[],
            manifest=None,
            batch_size=None,
            lookback=30,
            max_videos=10,
            dry_run=False,
            force_refresh=False,
        )

        exception_map = [
            (
                RateLimitExceededError("429 Too Many Requests"),
                EXIT_RATE_LIMIT_EXCEEDED,
                "Rate limit exceeded:",
            ),
            (
                IngestionNetworkError("Network socket closed"),
                EXIT_INGESTION_ERROR,
                "Ingestion network error:",
            ),
            (PreflightError("Ollama offline"), EXIT_CONFIG_OR_USAGE_ERROR, "Preflight error:"),
            (
                DomainValidationError("Invalid schema"),
                EXIT_DOMAIN_VALIDATION_ERROR,
                "Domain validation error:",
            ),
            (
                SecurityViolationError("Path traversal attack"),
                EXIT_CONFIG_OR_USAGE_ERROR,
                "Security boundary violation:",
            ),
            (RuntimeError("Unknown bug"), EXIT_INTERNAL_ERROR, "Unexpected sync error:"),
        ]

        for exc, expected_code, expected_msg_prefix in exception_map:
            with (
                patch(
                    "cresmo.presentation.commands.sync.resolve_shared_settings",
                    return_value=mock_settings,
                ),
                patch(
                    "cresmo.presentation.commands.sync.build_sync_channel_use_case", side_effect=exc
                ),
            ):
                code = handle_sync(args)
                assert code == expected_code
                captured = capsys.readouterr()
                assert expected_msg_prefix in captured.err
