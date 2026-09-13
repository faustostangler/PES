"""Unit tests for Cresmo Humble Object CLI Controller.

Verifies argument parsing, flag overrides, environment checks, and standardized
process exit codes per SPEC-002 §4.1 & §4.2.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline import PipelineResult
from cresmo.domain.entities import RawTranscript
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    PipelineStatus,
    SyncSummary,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.cli import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
    main,
)


class TestCresmoCLI:
    """Hermetic unit tests for CLI entrypoint and exit codes."""

    def test_cli_no_args_defaults_to_run_batch(self) -> None:
        with (
            patch("cresmo.presentation.cli.build_pipeline"),
            patch("cresmo.presentation.cli._load_batch_sources", return_value=[]),
        ):
            assert main([]) == EXIT_SUCCESS

    def test_cli_invalid_subcommand_returns_code_2(self) -> None:
        assert main(["invalid-command"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_run_without_args_runs_batch(self) -> None:
        with (
            patch("cresmo.presentation.cli.build_pipeline"),
            patch("cresmo.presentation.cli._load_batch_sources", return_value=[]),
        ):
            assert main(["run"]) == EXIT_SUCCESS

    def test_cli_check_config_success_returns_code_0(self) -> None:
        with (
            patch("cresmo.presentation.cli.CresmoSettings") as mock_settings_cls,
            patch("cresmo.presentation.cli.build_preflight_checker") as mock_checker_builder,
        ):
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings.vault_dir = Path("/tmp/vault")
            mock_settings.sqlite_ledger_path = Path("/tmp/vault/cresmo_ledger.db")
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.batch_size = 5
            mock_settings_cls.return_value = mock_settings

            mock_checker = MagicMock()
            mock_checker.check_all.return_value = MagicMock(is_healthy=True, errors=())
            mock_checker_builder.return_value = mock_checker

            exit_code = main(["check-config"])
            assert exit_code == EXIT_SUCCESS

    def test_cli_check_config_preflight_failure_returns_code_2(self) -> None:
        with (
            patch("cresmo.presentation.cli.CresmoSettings") as mock_settings_cls,
            patch("cresmo.presentation.cli.build_preflight_checker") as mock_checker_builder,
        ):
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings_cls.return_value = mock_settings

            mock_checker = MagicMock()
            mock_checker.check_all.return_value = MagicMock(
                is_healthy=False, errors=("Missing GEMINI_API_KEY",)
            )
            mock_checker_builder.return_value = mock_checker

            exit_code = main(["check-config"])
            assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_run_success_returns_code_0(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("dQw4w9WgXcQ"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.run_for_video.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                gap_filler_passes=3,
                force_reprocess=False,
            )

    def test_cli_run_with_flag_overrides(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("dQw4w9WgXcQ"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with patch(
            "cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline
        ) as mock_builder:
            exit_code = main(
                [
                    "run",
                    "--url",
                    "https://youtube.com/watch?v=dQw4w9WgXcQ",
                    "--passes",
                    "3",
                    "--batch-size",
                    "9",
                ]
            )

            assert exit_code == EXIT_SUCCESS
            mock_builder.assert_called_once_with(batch_size_override=9)
            mock_pipeline.run_for_video.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                gap_filler_passes=3,
                force_reprocess=False,
            )

    def test_cli_run_dry_run_invokes_only_ingest(self) -> None:
        mock_pipeline = MagicMock()
        mock_raw = RawTranscript(
            content_id=ContentId("dQw4w9WgXcQ"),
            channel_name="TestChannel",
            body="Verbatim transcript content.",
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(
                ["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ", "--dry-run"]
            )

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ"
            )
            mock_pipeline.run_for_video.assert_not_called()

    def test_cli_run_all_with_manifest_success(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "test_playlist.txt"
        manifest_file.write_text(
            "# Comment line\n"
            "https://youtube.com/watch?v=video11111111\n"
            "\n"
            "https://youtube.com/watch?v=video22222222\n",
            encoding="utf-8",
        )

        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("video11111111"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--all", "--manifest", str(manifest_file)])

            assert exit_code == EXIT_SUCCESS
            assert mock_pipeline.run_for_video.call_count == 2

    def test_cli_run_all_dry_run(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "test_playlist.txt"
        manifest_file.write_text(
            "https://youtube.com/watch?v=video11111111\n",
            encoding="utf-8",
        )

        mock_pipeline = MagicMock()
        mock_raw = RawTranscript(
            content_id=ContentId("video11111111"),
            channel_name="TestChan",
            body="Content",
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--all", "--dry-run", "--manifest", str(manifest_file)])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=video11111111"
            )
            mock_pipeline.run_for_video.assert_not_called()

    def test_cli_run_all_missing_manifest_returns_code_0(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "non_existent.txt"
        exit_code = main(["run", "--all", "--manifest", str(missing_file)])
        assert exit_code == EXIT_SUCCESS

    def test_cli_maps_domain_validation_error_to_code_3(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = DomainValidationError("Invalid domain entity")

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_DOMAIN_VALIDATION_ERROR

    def test_cli_maps_rate_limit_error_to_code_4(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RateLimitExceededError(
            "HTTP 429 Too Many Requests"
        )

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_maps_ingestion_error_to_code_5(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = IngestionNetworkError("Whisper failed")

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_maps_unexpected_error_to_code_1(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RuntimeError("Fatal crash")

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_INTERNAL_ERROR

    def test_cli_sync_missing_channel_returns_code_2(self) -> None:
        assert main(["sync"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_sync_success_returns_code_0(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=5,
            processed_count=3,
            skipped_count=2,
            failed_count=0,
            duration_seconds=12.5,
            status=PipelineStatus.COMPLETED,
        )

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_SUCCESS

    def test_cli_sync_with_flags_propagated(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=2,
            processed_count=2,
            skipped_count=0,
            failed_count=0,
            duration_seconds=4.0,
            status=PipelineStatus.COMPLETED,
        )

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ) as mock_builder:
            exit_code = main(
                [
                    "sync",
                    "--channel",
                    "https://youtube.com/@test",
                    "--lookback",
                    "14",
                    "--max-videos",
                    "20",
                    "--batch-size",
                    "7",
                    "--dry-run",
                    "--force-refresh",
                ]
            )
            assert exit_code == EXIT_SUCCESS
            mock_builder.assert_called_once_with(batch_size_override=7)
            mock_use_case.execute.assert_called_once_with(
                query=ChannelFeedQuery(
                    channel_url="https://youtube.com/@test",
                    lookback_days=14,
                    max_videos=20,
                ),
                dry_run=True,
                force_refresh=True,
            )

    def test_cli_sync_rate_limit_error_returns_code_4(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RateLimitExceededError("Quota exhausted")

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_sync_ingestion_error_returns_code_5(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = IngestionNetworkError("Network down")

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_sync_security_violation_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = SecurityViolationError("Traversal detected")

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_sync_preflight_error_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = PreflightError("Missing tool ffmpeg")

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_sync_all_failed_returns_code_1(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=3,
            processed_count=0,
            skipped_count=0,
            failed_count=3,
            duration_seconds=5.0,
            status=PipelineStatus.FAILED_TRANSFORMATION,
        )

        with patch(
            "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_INTERNAL_ERROR

    def test_cli_worker_missing_channel_returns_code_2(self) -> None:
        assert main(["worker"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_worker_once_success_returns_code_0(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=2.0,
            status=PipelineStatus.COMPLETED,
        )

        with (
            patch(
                "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
            ),
            patch("pathlib.Path.write_text") as mock_heartbeat,
        ):
            exit_code = main(["worker", "--channel", "https://youtube.com/@test", "--once"])
            assert exit_code == EXIT_SUCCESS
            mock_heartbeat.assert_called()
            mock_use_case.execute.assert_called_once()

    def test_cli_worker_keyboard_interrupt_returns_code_0(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = KeyboardInterrupt()

        with (
            patch(
                "cresmo.presentation.cli.build_sync_channel_use_case", return_value=mock_use_case
            ),
            patch("pathlib.Path.write_text"),
        ):
            exit_code = main(["worker", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_SUCCESS

    def test_cli_dedupe_success_returns_code_0(self) -> None:
        from cresmo.application.use_cases.unify_duplicate_notes import (
            DeduplicationReport,
            DuplicateCluster,
        )
        from cresmo.domain.value_objects import NoteTitle

        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = DeduplicationReport(
            clusters=(
                DuplicateCluster(
                    canonical_title=NoteTitle("Dom Afonso Henriques"),
                    merged_titles=(NoteTitle("D. Afonso Henriques"),),
                    links_rewritten_count=3,
                ),
            )
        )

        with patch(
            "cresmo.presentation.cli.build_unify_duplicates_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["dedupe"])
            assert exit_code == EXIT_SUCCESS
            mock_use_case.execute.assert_called_once()

    def test_settings_concurrency_pools_and_lookback_defaults(self) -> None:
        """Verify default lookback is 365 days and worker pools use proportional multiples."""
        settings = CresmoSettings()
        assert settings.days_lookback == 365
        assert settings.whisper_workers == 1
        assert settings.subtitle_workers == 5
        assert settings.channel_discovery_workers == 10

    def test_settings_concurrency_pools_multiples_scaled(self) -> None:
        """Verify worker pools auto-scale when whisper_workers is configured."""
        settings = CresmoSettings(whisper_workers=2)
        assert settings.whisper_workers == 2
        assert settings.subtitle_workers == 10
        assert settings.channel_discovery_workers == 20

    def test_settings_concurrency_pools_explicit_override(self) -> None:
        """Verify explicit worker settings override calculated multiples."""
        settings = CresmoSettings(whisper_workers=3, subtitle_workers=7)
        assert settings.whisper_workers == 3
        assert settings.subtitle_workers == 7
        assert settings.channel_discovery_workers == 30

    def test_cli_worker_flags_removed(self) -> None:
        """Verify that --subtitle-workers, --whisper-workers, and --discovery-workers are removed."""
        from cresmo.presentation.cli import _create_parser

        parser = _create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["run", "--subtitle-workers", "5"])
        with pytest.raises(SystemExit):
            parser.parse_args(["run", "--whisper-workers", "2"])
        with pytest.raises(SystemExit):
            parser.parse_args(["run", "--discovery-workers", "10"])



    def test_load_batch_sources_includes_raw_directory(self, tmp_path: Path) -> None:
        """Verify local raw transcript lake files are loaded into Tier 2."""
        from cresmo.presentation.cli import _load_batch_sources

        settings = MagicMock(spec=CresmoSettings)
        settings.priority_texts_dir = tmp_path / "priority"
        settings.priority_texts_dir.mkdir()
        settings.playlist_priority_path = tmp_path / "playlist-priority.txt"
        settings.playlist_path = tmp_path / "playlist.txt"
        settings.raw_dir = tmp_path / "raw"
        settings.raw_dir.mkdir()
        settings.days_lookback = 365
        settings.channel_discovery_workers = 2

        # Create raw transcript file
        chan_dir = settings.raw_dir / "Marcelo_Andrade"
        chan_dir.mkdir()
        raw_file = chan_dir / "vid123.md"
        raw_file.write_text("---\nvideo_title: 'Test'\n---\nTranscript body", encoding="utf-8")

        sources = _load_batch_sources(settings)
        targets = [s.target for s in sources]
        assert str(raw_file.resolve()) in targets
        raw_src = next(s for s in sources if s.target == str(raw_file.resolve()))
        assert raw_src.kind == "file"

    def test_load_batch_sources_concurrent_channel_discovery(self, tmp_path: Path) -> None:
        """Verify channel URLs in playlist.txt trigger discover_channel_feed with lookback window."""
        from datetime import UTC, datetime, timedelta

        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.cli import _load_batch_sources

        settings = MagicMock(spec=CresmoSettings)
        settings.priority_texts_dir = tmp_path / "priority"
        settings.priority_texts_dir.mkdir()
        settings.playlist_priority_path = tmp_path / "playlist-priority.txt"
        settings.raw_dir = tmp_path / "raw"
        settings.raw_dir.mkdir()
        settings.playlist_path = tmp_path / "playlist.txt"
        settings.days_lookback = 365
        settings.channel_discovery_workers = 2

        # playlist.txt with a channel URL
        settings.playlist_path.write_text("https://www.youtube.com/@MarceloAndrade\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        now = datetime.now(UTC)
        recent_item = DiscoveredMediaItem(
            content_id=ContentId("recent123"),
            title="Recent Video",
            published_at=now - timedelta(days=10),
            media_url="https://www.youtube.com/watch?v=recent123",
            channel_name="Marcelo Andrade",
        )
        old_item = DiscoveredMediaItem(
            content_id=ContentId("old123456"),
            title="Old Video",
            published_at=now - timedelta(days=400),
            media_url="https://www.youtube.com/watch?v=old123456",
            channel_name="Marcelo Andrade",
        )
        mock_ingestion.discover_channel_feed.return_value = [recent_item, old_item]

        sources = _load_batch_sources(settings, media_ingestion_port=mock_ingestion)
        urls = [s.target for s in sources if s.kind == "url"]
        assert "https://www.youtube.com/watch?v=recent123" in urls
        assert "https://www.youtube.com/watch?v=old123456" not in urls
        mock_ingestion.discover_channel_feed.assert_called_once()

    def test_load_batch_sources_resolves_channel_from_video_and_discovers_feed(
        self, tmp_path: Path
    ) -> None:
        """Verify video URLs in playlist.txt resolve parent channel and query its feed."""
        from datetime import UTC, datetime, timedelta

        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.cli import _load_batch_sources

        settings = MagicMock(spec=CresmoSettings)
        settings.priority_texts_dir = tmp_path / "priority"
        settings.priority_texts_dir.mkdir()
        settings.playlist_priority_path = tmp_path / "playlist-priority.txt"
        settings.raw_dir = tmp_path / "raw"
        settings.raw_dir.mkdir()
        settings.playlist_path = tmp_path / "playlist.txt"
        settings.days_lookback = 365
        settings.channel_discovery_workers = 2

        # playlist.txt with a direct video URL (not channel handle)
        settings.playlist_path.write_text("https://www.youtube.com/watch?v=seed1234\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCchan1"
        )
        now = datetime.now(UTC)
        discovered_item = DiscoveredMediaItem(
            content_id=ContentId("disc999_item"),
            title="Discovered From Parent Channel",
            published_at=now - timedelta(days=5),
            media_url="https://www.youtube.com/watch?v=disc999_item",
            channel_name="Parent Channel",
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        sources = _load_batch_sources(settings, media_ingestion_port=mock_ingestion)
        urls = [s.target for s in sources if s.kind == "url"]

        # Both seed video and discovered channel video should be present in sources
        assert "https://www.youtube.com/watch?v=seed1234" in urls
        assert "https://www.youtube.com/watch?v=disc999_item" in urls
        mock_ingestion.extract_channel_url_from_video.assert_called_with(
            "https://www.youtube.com/watch?v=seed1234"
        )
        mock_ingestion.discover_channel_feed.assert_called_once()
        call_query = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert call_query.channel_url == "https://www.youtube.com/channel/UCchan1"

    def test_load_batch_sources_deduplicates_channels_across_multiple_videos(
        self, tmp_path: Path
    ) -> None:
        """Verify multiple videos from the same channel trigger channel feed query only once."""
        from datetime import UTC, datetime, timedelta

        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.cli import _load_batch_sources

        settings = MagicMock(spec=CresmoSettings)
        settings.priority_texts_dir = tmp_path / "priority"
        settings.priority_texts_dir.mkdir()
        settings.playlist_priority_path = tmp_path / "playlist-priority.txt"
        settings.raw_dir = tmp_path / "raw"
        settings.raw_dir.mkdir()
        settings.playlist_path = tmp_path / "playlist.txt"
        settings.days_lookback = 365
        settings.channel_discovery_workers = 2

        # Two different videos in playlist
        settings.playlist_path.write_text(
            "https://www.youtube.com/watch?v=videoA1234\nhttps://www.youtube.com/watch?v=videoB1234\n",
            encoding="utf-8",
        )

        mock_ingestion = MagicMock()
        # Both resolve to the same channel
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCSameChannel"
        )
        now = datetime.now(UTC)
        discovered_item = DiscoveredMediaItem(
            content_id=ContentId("discNew_item"),
            title="New Video",
            published_at=now - timedelta(days=2),
            media_url="https://www.youtube.com/watch?v=discNew_item",
            channel_name="Same Channel",
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        sources = _load_batch_sources(settings, media_ingestion_port=mock_ingestion)
        urls = [s.target for s in sources if s.kind == "url"]

        assert "https://www.youtube.com/watch?v=videoA1234" in urls
        assert "https://www.youtube.com/watch?v=videoB1234" in urls
        assert "https://www.youtube.com/watch?v=discNew_item" in urls
        # Crucial: discover_channel_feed must be called exactly ONCE for UCSameChannel
        assert mock_ingestion.discover_channel_feed.call_count == 1

    def test_load_batch_sources_uses_local_raw_frontmatter_channel(
        self, tmp_path: Path
    ) -> None:
        """Verify channel is extracted from local raw frontmatter without remote resolution call."""
        from datetime import UTC, datetime, timedelta

        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.cli import _load_batch_sources

        settings = MagicMock(spec=CresmoSettings)
        settings.priority_texts_dir = tmp_path / "priority"
        settings.priority_texts_dir.mkdir()
        settings.playlist_priority_path = tmp_path / "playlist-priority.txt"
        settings.playlist_path = tmp_path / "playlist.txt"
        settings.raw_dir = tmp_path / "raw"
        settings.raw_dir.mkdir()
        settings.days_lookback = 365
        settings.channel_discovery_workers = 2

        # Create raw transcript file with frontmatter containing channel_id
        chan_dir = settings.raw_dir / "TestChannel"
        chan_dir.mkdir()
        raw_file = chan_dir / "vidLocal1.md"
        raw_file.write_text(
            "---\nvideo_title: 'Local'\nvideo_id: vidLocal1\nchannel_id: UCLocal123\n---\nBody",
            encoding="utf-8",
        )

        settings.playlist_path.write_text("https://www.youtube.com/watch?v=vidLocal1\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        now = datetime.now(UTC)
        discovered_item = DiscoveredMediaItem(
            content_id=ContentId("discLocalCh_item"),
            title="Discovered From Local Raw Channel",
            published_at=now - timedelta(days=1),
            media_url="https://www.youtube.com/watch?v=discLocalCh_item",
            channel_name="Local Channel",
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        sources = _load_batch_sources(settings, media_ingestion_port=mock_ingestion)
        urls = [s.target for s in sources if s.kind == "url"]

        assert "https://www.youtube.com/watch?v=discLocalCh_item" in urls
        # extract_channel_url_from_video should NOT be called because it was resolved from raw frontmatter
        mock_ingestion.extract_channel_url_from_video.assert_not_called()
        mock_ingestion.discover_channel_feed.assert_called_once()
        call_query = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert call_query.channel_url == "https://www.youtube.com/channel/UCLocal123"



