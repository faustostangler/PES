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
    ChannelName,
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
            patch("cresmo.presentation.commands.run.build_pipeline"),
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[]),
        ):
            assert main([]) == EXIT_SUCCESS

    def test_cli_invalid_subcommand_returns_code_2(self) -> None:
        assert main(["invalid-command"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_run_without_args_runs_batch(self) -> None:
        with (
            patch("cresmo.presentation.commands.run.build_pipeline"),
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[]),
        ):
            assert main(["run"]) == EXIT_SUCCESS

    def test_cli_check_config_success_returns_code_0(self) -> None:
        with (
            patch("cresmo.presentation.commands.check_config.CresmoSettings") as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.check_config.build_preflight_checker"
            ) as mock_checker_builder,
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
            patch("cresmo.presentation.commands.check_config.CresmoSettings") as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.check_config.build_preflight_checker"
            ) as mock_checker_builder,
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

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
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
            "cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline
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
            mock_builder.assert_called_once()
            call_kwargs = mock_builder.call_args.kwargs
            assert call_kwargs["batch_size_override"] == 9
            assert isinstance(call_kwargs["settings"], CresmoSettings)
            mock_pipeline.run_for_video.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                gap_filler_passes=3,
                force_reprocess=False,
            )

    def test_cli_run_dry_run_invokes_only_ingest(self) -> None:
        mock_pipeline = MagicMock()
        mock_raw = RawTranscript(
            content_id=ContentId("dQw4w9WgXcQ"),
            channel_name=ChannelName("TestChannel"),
            body="Verbatim transcript content.",
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
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

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
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
            channel_name=ChannelName("TestChan"),
            body="Content",
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--all", "--dry-run", "--manifest", str(manifest_file)])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=video11111111"
            )
            mock_pipeline.run_for_video.assert_not_called()

    def test_cli_run_all_missing_manifest_returns_code_0(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "non_existent.txt"
        with patch("cresmo.presentation.commands.run.build_pipeline"):
            exit_code = main(["run", "--all", "--manifest", str(missing_file)])
        assert exit_code == EXIT_SUCCESS

    def test_cli_maps_domain_validation_error_to_code_3(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = DomainValidationError("Invalid domain entity")

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_DOMAIN_VALIDATION_ERROR

    def test_cli_maps_rate_limit_error_to_code_4(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RateLimitExceededError(
            "HTTP 429 Too Many Requests"
        )

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_maps_ingestion_error_to_code_5(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = IngestionNetworkError("Whisper failed")

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_maps_unexpected_error_to_code_1(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RuntimeError("Fatal crash")

        with patch("cresmo.presentation.commands.run.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_INTERNAL_ERROR

    def test_cli_sync_without_flags_executes_default_manifest_sync(self, tmp_path: Path) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@default",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=1.0,
            status=PipelineStatus.COMPLETED,
        )
        fake_manifest = tmp_path / "playlist.txt"
        fake_manifest.write_text("https://youtube.com/@default\n", encoding="utf-8")
        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--manifest", str(fake_manifest)])
            assert exit_code == EXIT_SUCCESS
            mock_use_case.execute.assert_called_once()

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
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
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
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
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
            mock_builder.assert_called_once()
            call_kwargs = mock_builder.call_args.kwargs
            assert call_kwargs["batch_size_override"] == 7
            assert isinstance(call_kwargs["settings"], CresmoSettings)
            mock_use_case.execute.assert_called_once_with(
                query=ChannelFeedQuery(
                    channel_url="https://youtube.com/@test",
                    lookback_days=14,
                    max_videos=20,
                ),
                dry_run=True,
                force_refresh=True,
            )

    def test_cli_sync_with_category_filter(self, tmp_path: Path) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@ancapsu",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=1.0,
            status=PipelineStatus.COMPLETED,
        )
        fake_manifest = tmp_path / "playlist.txt"
        fake_manifest.write_text(
            "https://youtube.com/@ancapsu\nhttps://youtube.com/@other\n",
            encoding="utf-8",
        )
        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(
                ["sync", "--manifest", str(fake_manifest), "--category", "politics_br"]
            )
            assert exit_code == EXIT_SUCCESS
            assert mock_use_case.execute.call_count == 1

    def test_cli_sync_with_video_direct_filter(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=1.0,
            status=PipelineStatus.COMPLETED,
        )
        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--video", "dQw4w9WgXcQ,9IbNJ0EsTxI"])
            assert exit_code == EXIT_SUCCESS
            assert mock_use_case.execute.call_count == 2

    def test_cli_sync_with_multiple_comma_separated_channels(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@a",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=1.0,
            status=PipelineStatus.COMPLETED,
        )
        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@b,https://youtube.com/@a"])
            assert exit_code == EXIT_SUCCESS
            assert mock_use_case.execute.call_count == 2
            # ADR-012: Ensure channels were called in alphabetical order: @a then @b
            calls = mock_use_case.execute.call_args_list
            assert calls[0].kwargs["query"].channel_url == "https://youtube.com/@a"
            assert calls[1].kwargs["query"].channel_url == "https://youtube.com/@b"

    def test_cli_run_with_filter_criteria_propagated(self) -> None:
        with (
            patch("cresmo.presentation.commands.run.build_pipeline"),
            patch(
                "cresmo.presentation.commands.run.load_batch_sources", return_value=[]
            ) as mock_load,
        ):
            exit_code = main(
                [
                    "run",
                    "--dry-run",
                    "--channel",
                    "Ancapsu,Mises",
                    "--category",
                    "politics_br",
                    "--video",
                    "dQw4w9WgXcQ",
                ]
            )
            assert exit_code == EXIT_SUCCESS
            mock_load.assert_called_once()
            query = mock_load.call_args.kwargs["query"]
            assert query.filter_criteria.channels == ("ancapsu", "mises")
            assert query.filter_criteria.categories == ("politics_br",)
            assert query.filter_criteria.video_ids == ("dQw4w9WgXcQ",)

    def test_cli_sync_rate_limit_error_returns_code_4(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RateLimitExceededError("Quota exhausted")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_sync_ingestion_error_returns_code_5(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = IngestionNetworkError("Network down")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_sync_security_violation_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = SecurityViolationError("Traversal detected")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_sync_preflight_error_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = PreflightError("Missing tool ffmpeg")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
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
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
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
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
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
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
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
            "cresmo.presentation.commands.dedupe.build_unify_duplicates_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["dedupe"])
            assert exit_code == EXIT_SUCCESS
            mock_use_case.execute.assert_called_once()

    def test_settings_concurrency_pools_and_lookback_defaults(self) -> None:
        """Verify default lookback is 365 days and worker pools use proportional multiples."""
        settings = CresmoSettings(_env_file=None)
        assert settings.days_lookback == 365
        assert settings.whisper_workers == 1
        assert settings.subtitle_workers == 5
        assert settings.channel_discovery_workers == 10

    def test_settings_concurrency_pools_multiples_scaled(self) -> None:
        """Verify worker pools auto-scale when whisper_workers is configured."""
        settings = CresmoSettings(whisper_workers=2, _env_file=None)
        assert settings.whisper_workers == 2
        assert settings.subtitle_workers == 10
        assert settings.channel_discovery_workers == 20

    def test_settings_concurrency_pools_explicit_override(self) -> None:
        """Verify explicit worker settings override calculated multiples."""
        settings = CresmoSettings(whisper_workers=3, subtitle_workers=7, _env_file=None)
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
        from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery
        from cresmo.presentation.commands.run import load_batch_sources

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

        query = BatchDiscoveryQuery(scan_raw=True)
        sources = list(load_batch_sources(query=query, settings=settings))
        targets = [s.target for s in sources]
        assert str(raw_file.resolve()) in targets
        raw_src = next(s for s in sources if s.target == str(raw_file.resolve()))
        assert raw_src.kind == "file"

    def test_load_batch_sources_concurrent_channel_discovery(self, tmp_path: Path) -> None:
        """Verify channel URLs in playlist.txt trigger discover_channel_feed with lookback window."""
        from datetime import UTC, datetime, timedelta

        from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery
        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.commands.run import load_batch_sources

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
        settings.playlist_path.write_text(
            "https://www.youtube.com/@MarceloAndrade\n", encoding="utf-8"
        )

        mock_ingestion = MagicMock()
        now = datetime.now(UTC)
        recent_item = DiscoveredMediaItem(
            content_id=ContentId("recent123"),
            title="Recent Video",
            published_at=now - timedelta(days=10),
            media_url="https://www.youtube.com/watch?v=recent123",
            channel_name=ChannelName("Marcelo Andrade"),
        )
        old_item = DiscoveredMediaItem(
            content_id=ContentId("old123456"),
            title="Old Video",
            published_at=now - timedelta(days=400),
            media_url="https://www.youtube.com/watch?v=old123456",
            channel_name=ChannelName("Marcelo Andrade"),
        )
        mock_ingestion.discover_channel_feed.return_value = [recent_item, old_item]

        query = BatchDiscoveryQuery(scan_raw=False)
        sources = list(
            load_batch_sources(query=query, settings=settings, media_ingestion_port=mock_ingestion)
        )
        urls = [s.target for s in sources if s.kind == "url"]
        assert "https://www.youtube.com/watch?v=recent123" in urls
        assert "https://www.youtube.com/watch?v=old123456" not in urls
        mock_ingestion.discover_channel_feed.assert_called_once()

    def test_load_batch_sources_resolves_channel_from_video_and_discovers_feed(
        self, tmp_path: Path
    ) -> None:
        """Verify video URLs in playlist.txt resolve parent channel and query its feed."""
        from datetime import UTC, datetime, timedelta

        from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery
        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.commands.run import load_batch_sources

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
        settings.playlist_path.write_text(
            "https://www.youtube.com/watch?v=seed1234\n", encoding="utf-8"
        )

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
            channel_name=ChannelName("Parent Channel"),
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        query = BatchDiscoveryQuery(scan_raw=False)
        sources = list(
            load_batch_sources(query=query, settings=settings, media_ingestion_port=mock_ingestion)
        )
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

        from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery
        from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
        from cresmo.presentation.commands.run import load_batch_sources

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
            channel_name=ChannelName("Same Channel"),
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        query = BatchDiscoveryQuery(scan_raw=False)
        sources = list(
            load_batch_sources(query=query, settings=settings, media_ingestion_port=mock_ingestion)
        )
        urls = [s.target for s in sources if s.kind == "url"]

        assert "https://www.youtube.com/watch?v=videoA1234" in urls
        assert "https://www.youtube.com/watch?v=videoB1234" in urls
        assert "https://www.youtube.com/watch?v=discNew_item" in urls
        # Crucial: discover_channel_feed must be called exactly ONCE for UCSameChannel
        assert mock_ingestion.discover_channel_feed.call_count == 1

    def test_load_batch_sources_uses_local_raw_frontmatter_channel(self, tmp_path: Path) -> None:
        """Verify channel is extracted from local raw frontmatter without remote resolution call."""
        from datetime import UTC, datetime, timedelta

        from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery
        from cresmo.domain.value_objects import ChannelName, ContentId, DiscoveredMediaItem
        from cresmo.presentation.commands.run import load_batch_sources

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

        settings.playlist_path.write_text(
            "https://www.youtube.com/watch?v=vidLocal1\n", encoding="utf-8"
        )

        mock_ingestion = MagicMock()
        now = datetime.now(UTC)
        discovered_item = DiscoveredMediaItem(
            content_id=ContentId("discLocalCh_item"),
            title="Discovered From Local Raw Channel",
            published_at=now - timedelta(days=1),
            media_url="https://www.youtube.com/watch?v=discLocalCh_item",
            channel_name=ChannelName("Local Channel"),
        )
        mock_ingestion.discover_channel_feed.return_value = [discovered_item]

        query = BatchDiscoveryQuery(scan_raw=True)
        sources = list(
            load_batch_sources(query=query, settings=settings, media_ingestion_port=mock_ingestion)
        )
        urls = [s.target for s in sources if s.kind == "url"]

        assert "https://www.youtube.com/watch?v=discLocalCh_item" in urls
        # extract_channel_url_from_video should NOT be called because it was resolved from raw frontmatter
        mock_ingestion.extract_channel_url_from_video.assert_not_called()
        mock_ingestion.discover_channel_feed.assert_called_once()

        call_query = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert call_query.channel_url == "https://www.youtube.com/channel/UCLocal123"

    def test_execute_single_video_dry_run_ingestion_none_returns_error(self) -> None:
        from argparse import Namespace

        from cresmo.presentation.commands.run import execute_single_video_run

        pipeline = MagicMock()
        pipeline.ingest_raw_transcript.execute.return_value = None

        args = Namespace(dry_run=True, url="https://youtube.com/watch?v=missingTranscript")
        code = execute_single_video_run(pipeline, args)
        assert code == EXIT_INGESTION_ERROR

    def test_execute_single_video_run_already_processed_skipped(self) -> None:
        from argparse import Namespace

        from cresmo.presentation.commands.run import execute_single_video_run

        pipeline = MagicMock()
        fake_result = MagicMock()
        fake_result.already_processed = True
        fake_result.content_id.value = "alreadyDone123"
        pipeline.run_for_video.return_value = fake_result

        args = Namespace(
            dry_run=False,
            url="https://youtube.com/watch?v=alreadyDone123",
            passes=1,
            force_reprocess=False,
        )
        code = execute_single_video_run(pipeline, args)
        assert code == EXIT_SUCCESS

    def test_execute_single_video_run_pipeline_error_returns_internal_error(self) -> None:
        from argparse import Namespace

        from cresmo.presentation.commands.run import execute_single_video_run

        pipeline = MagicMock()
        fake_result = MagicMock()
        fake_result.already_processed = False
        fake_result.success = False
        fake_result.error_message = "LLM synthesis crashed"
        pipeline.run_for_video.return_value = fake_result

        args = Namespace(
            dry_run=False,
            url="https://youtube.com/watch?v=errorVid123",
            passes=1,
            force_reprocess=False,
        )
        code = execute_single_video_run(pipeline, args)
        assert code == EXIT_INTERNAL_ERROR

    def test_execute_batch_dry_run_with_text_file_and_failed_url(self, tmp_path: Path) -> None:
        from cresmo.application.use_cases.discover_batch_sources import BatchSource
        from cresmo.domain.value_objects import SourceModality
        from cresmo.presentation.commands.run import execute_batch_dry_run

        doc_file = tmp_path / "text_doc.md"
        doc_file.write_text("Markdown content for dry-run", encoding="utf-8")

        sources = [
            BatchSource(kind=SourceModality.FILE, target=str(doc_file)),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=failIngest"),
        ]

        pipeline = MagicMock()
        pipeline.ingest_raw_transcript.execute.return_value = None

        code = execute_batch_dry_run(pipeline, sources)
        assert code == EXIT_SUCCESS

    def test_execute_batch_run_with_file_and_exceptions(self, tmp_path: Path) -> None:
        from argparse import Namespace

        from cresmo.application.use_cases.discover_batch_sources import BatchSource
        from cresmo.domain.value_objects import SourceModality
        from cresmo.presentation.commands.run import execute_batch_run

        doc_file = tmp_path / "text_doc.md"
        doc_file.write_text("Text", encoding="utf-8")

        sources = [
            BatchSource(kind=SourceModality.FILE, target=str(doc_file)),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=rateLimit"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=networkError"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=genericError"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=skippedVid"),
            BatchSource(
                kind=SourceModality.URL, target="https://youtube.com/watch?v=unsuccessfulVid"
            ),
        ]

        pipeline = MagicMock()
        # File succeeds
        file_res = MagicMock()
        file_res.already_processed = False
        file_res.success = True
        file_res.content_id.value = "textDoc"
        file_res.synthesized_notes = []
        file_res.reconciled_mocs = []
        file_res.duplicates_unified = 0
        pipeline.run_for_text_file.return_value = file_res

        # Video calls
        skipped_res = MagicMock(already_processed=True)
        skipped_res.content_id.value = "skippedVid"

        unsuccessful_res = MagicMock(
            already_processed=False, success=False, error_message="Some step failed"
        )

        def side_effect_video(video_url: str, **kwargs):
            if "rateLimit" in video_url:
                raise RateLimitExceededError("Rate limit hit")
            elif "networkError" in video_url:
                raise IngestionNetworkError("Network failure")
            elif "genericError" in video_url:
                raise RuntimeError("Unexpected boom")
            elif "skippedVid" in video_url:
                return skipped_res
            elif "unsuccessfulVid" in video_url:
                return unsuccessful_res
            return file_res

        pipeline.run_for_video.side_effect = side_effect_video

        args = Namespace(passes=1, force_reprocess=False)
        code = execute_batch_run(pipeline, sources, args)
        assert code == EXIT_INTERNAL_ERROR

    def test_handle_run_preflight_and_validation_errors(self) -> None:
        from argparse import Namespace

        from cresmo.presentation.commands.run import handle_run

        with patch(
            "cresmo.presentation.commands.run.build_pipeline",
            side_effect=PreflightError("Preflight failed"),
        ):
            args = Namespace(
                url=None,
                manifest=None,
                dry_run=False,
                no_scan_raw=True,
                batch_size=None,
                lookback=10,
                channel_max_videos=50,
            )
            assert handle_run(args) == EXIT_CONFIG_OR_USAGE_ERROR

        with patch("cresmo.presentation.commands.run.build_pipeline") as mock_build:
            from pydantic import BaseModel, ValidationError

            class Dummy(BaseModel):
                val: int

            try:
                Dummy(val="not_an_int")  # type: ignore[arg-type]
            except ValidationError as ve:
                mock_build.side_effect = ve
            args = Namespace(
                url=None,
                manifest=None,
                dry_run=False,
                no_scan_raw=True,
                batch_size=None,
                lookback=None,
                channel_max_videos=50,
            )
            assert handle_run(args) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_handle_run_lookback_override(self) -> None:
        from argparse import Namespace

        from cresmo.application.services.preflight import PreflightResult
        from cresmo.presentation.commands.run import handle_run

        with (
            patch("cresmo.presentation.commands.run.build_pipeline"),
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[]),
            patch("cresmo.presentation.commands.run.CresmoSettings") as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.run.build_preflight_checker"
            ) as mock_checker_builder,
        ):
            mock_checker = MagicMock()
            mock_checker.check_all.return_value = PreflightResult(
                is_healthy=True, errors=(), warnings=()
            )
            mock_checker_builder.return_value = mock_checker
            mock_settings = MagicMock()
            mock_settings_cls.return_value = mock_settings
            args = Namespace(
                url=None,
                manifest=None,
                dry_run=False,
                no_scan_raw=True,
                batch_size=None,
                lookback=14,
                channel_max_videos=10,
            )
            code = handle_run(args)
            assert code == EXIT_SUCCESS
            assert mock_settings.days_lookback == 14

    def test_handle_run_crawl_defaults_and_no_crawl_flag(self) -> None:
        from argparse import Namespace

        from cresmo.application.services.preflight import PreflightResult
        from cresmo.presentation.commands.run import handle_run

        with (
            patch("cresmo.presentation.commands.run.build_pipeline"),
            patch(
                "cresmo.presentation.commands.run.load_batch_sources", return_value=[]
            ) as mock_load,
            patch("cresmo.presentation.commands.run.CresmoSettings") as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.run.build_preflight_checker"
            ) as mock_checker_builder,
        ):
            mock_checker = MagicMock()
            mock_checker.check_all.return_value = PreflightResult(
                is_healthy=True, errors=(), warnings=()
            )
            mock_checker_builder.return_value = mock_checker
            mock_settings = MagicMock()
            mock_settings.enable_channel_crawler = True
            mock_settings.days_lookback = 365
            mock_settings.channel_discovery_workers = 30
            mock_settings_cls.return_value = mock_settings

            # Case 1: Default run without --no-crawl (crawling is enabled)
            args_default = Namespace(
                url=None,
                manifest=None,
                dry_run=False,
                no_scan_raw=False,
                batch_size=None,
                lookback=None,
                channel_max_videos=50,
                no_crawl=False,
            )
            assert handle_run(args_default) == EXIT_SUCCESS
            query_default = mock_load.call_args[1]["query"]
            assert query_default.enable_channel_crawler is True

            # Case 2: User supplies --no-crawl (crawling is disabled)
            args_no_crawl = Namespace(
                url=None,
                manifest=None,
                dry_run=False,
                no_scan_raw=False,
                batch_size=None,
                lookback=None,
                channel_max_videos=50,
                no_crawl=True,
            )
            assert handle_run(args_no_crawl) == EXIT_SUCCESS
            query_no_crawl = mock_load.call_args[1]["query"]
            assert query_no_crawl.enable_channel_crawler is False

    def test_check_config_telemetry_masked_and_exceptions(self) -> None:
        from argparse import Namespace

        from pydantic import SecretStr

        from cresmo.presentation.commands.check_config import handle_check_config

        # 1. Langfuse public key and secret key configured
        with (
            patch("cresmo.presentation.commands.check_config.CresmoSettings") as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.check_config.build_preflight_checker"
            ) as mock_checker_builder,
        ):
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings.vault_dir = Path("/tmp/vault")
            mock_settings.sqlite_ledger_path = Path("/tmp/vault/cresmo_ledger.db")
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.batch_size = 5
            mock_settings.langfuse_public_key = "pk-lf-1234567890abcdef"
            mock_settings.langfuse_secret_key = SecretStr("sk-lf-secret")
            mock_settings.langfuse_host = "https://cloud.langfuse.com"
            mock_settings_cls.return_value = mock_settings

            mock_checker = MagicMock()
            mock_checker.check_all.return_value = MagicMock(is_healthy=True, errors=())
            mock_checker_builder.return_value = mock_checker

            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS

        # 2. PreflightError
        with patch(
            "cresmo.presentation.commands.check_config.CresmoSettings",
            side_effect=PreflightError("Vault missing"),
        ):
            code = handle_check_config(Namespace())
            assert code == EXIT_CONFIG_OR_USAGE_ERROR

        # 3. ValidationError
        with patch("cresmo.presentation.commands.check_config.CresmoSettings") as mock_s:
            from pydantic import BaseModel, ValidationError

            class Dummy(BaseModel):
                num: int

            try:
                Dummy(num="invalid")  # type: ignore[arg-type]
            except ValidationError as ve:
                mock_s.side_effect = ve
            code = handle_check_config(Namespace())
            assert code == EXIT_CONFIG_OR_USAGE_ERROR

        # 4. Generic unexpected exception
        with patch(
            "cresmo.presentation.commands.check_config.CresmoSettings",
            side_effect=RuntimeError("Hardware fault"),
        ):
            code = handle_check_config(Namespace())
            assert code == EXIT_INTERNAL_ERROR

    def test_cli_help_flag_returns_exit_success(self) -> None:
        """Verify that -h / --help exits cleanly with EXIT_SUCCESS (0)."""
        assert main(["--help"]) == EXIT_SUCCESS
        assert main(["-h"]) == EXIT_SUCCESS
        assert main(["run", "--help"]) == EXIT_SUCCESS

    def test_cli_argv_none_uses_sys_argv(self) -> None:
        """Verify that passing argv=None defaults to reading sys.argv[1:]."""
        with (
            patch("sys.argv", ["cresmo", "--help"]),
        ):
            assert main(None) == EXIT_SUCCESS

    def test_cli_parser_missing_handler_returns_usage_error(self) -> None:
        """Verify that args without handler attribute returns EXIT_CONFIG_OR_USAGE_ERROR."""
        from argparse import Namespace

        with patch("cresmo.presentation.cli._create_parser") as mock_create:
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = Namespace()  # no handler attribute
            mock_create.return_value = mock_parser

            assert main(["run"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_dedupe_exception_returns_internal_error(self) -> None:
        """Verify that unhandled exception in dedupe returns EXIT_INTERNAL_ERROR (1)."""
        with patch(
            "cresmo.presentation.commands.dedupe.build_unify_duplicates_use_case",
            side_effect=RuntimeError("Graph corruption"),
        ):
            assert main(["dedupe"]) == EXIT_INTERNAL_ERROR

    def test_cli_sync_domain_validation_error_returns_code_3(self) -> None:
        """Verify that DomainValidationError in sync returns EXIT_DOMAIN_VALIDATION_ERROR (3)."""
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = DomainValidationError("Invalid sync domain rule")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            assert (
                main(["sync", "--channel", "https://youtube.com/@test"])
                == EXIT_DOMAIN_VALIDATION_ERROR
            )

    def test_cli_sync_validation_error_returns_code_2(self) -> None:
        """Verify that pydantic ValidationError in sync returns EXIT_CONFIG_OR_USAGE_ERROR (2)."""
        from pydantic import BaseModel, ValidationError

        class Dummy(BaseModel):
            n: int

        mock_use_case = MagicMock()
        try:
            Dummy(n="bad")  # type: ignore[arg-type]
        except ValidationError as ve:
            mock_use_case.execute.side_effect = ve

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            assert (
                main(["sync", "--channel", "https://youtube.com/@test"])
                == EXIT_CONFIG_OR_USAGE_ERROR
            )

    def test_cli_sync_generic_exception_returns_internal_error(self) -> None:
        """Verify that unexpected exception in sync returns EXIT_INTERNAL_ERROR (1)."""
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RuntimeError("Sync explosion")

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            assert main(["sync", "--channel", "https://youtube.com/@test"]) == EXIT_INTERNAL_ERROR

    def test_cli_sync_zero_processed_zero_failed_non_completed_returns_success(self) -> None:
        """Verify that sync with 0 discovered, 0 processed, 0 failed returns EXIT_SUCCESS (0)."""
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=0,
            processed_count=0,
            skipped_count=0,
            failed_count=0,
            duration_seconds=0.1,
            status=PipelineStatus.RUNNING,
        )

        with patch(
            "cresmo.presentation.commands.sync.build_sync_channel_use_case",
            return_value=mock_use_case,
        ):
            assert main(["sync", "--channel", "https://youtube.com/@test"]) == EXIT_SUCCESS

    def test_cli_worker_loop_sleep_and_generic_exception(self) -> None:
        """Verify worker sleeping during polling loop and unexpected exception handling."""
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@test",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=1.0,
            status=PipelineStatus.COMPLETED,
        )

        with (
            patch(
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
            patch("pathlib.Path.write_text"),
            patch("time.sleep", side_effect=[None, KeyboardInterrupt]),
        ):
            # Test that it executes sleep then breaks gracefully via KeyboardInterrupt
            code = main(
                ["worker", "--channel", "https://youtube.com/@test", "--poll-interval", "5"]
            )
            assert code == EXIT_SUCCESS

        with (
            patch(
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                side_effect=RuntimeError("Worker crash"),
            ),
        ):
            code = main(["worker", "--channel", "https://youtube.com/@test"])
            assert code == EXIT_INTERNAL_ERROR

    def test_cli_concat_master_all_channels(self) -> None:
        mock_uc = MagicMock()
        mock_uc.execute_all.return_value = {
            "ChannelA": [
                MagicMock(
                    channel_name=ChannelName("ChannelA"),
                    channel_category="tech",
                    part_number=1,
                    word_count=5000,
                    document_count=3,
                    output_path=Path("/tmp/master/tech/ChannelA_001.md"),
                )
            ]
        }
        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_uc,
        ):
            assert main(["concat-master"]) == EXIT_SUCCESS
            mock_uc.execute_all.assert_called_once_with(max_words=None)

    def test_cli_concat_master_specific_channel(self) -> None:
        mock_uc = MagicMock()
        mock_uc.execute.return_value = [
            MagicMock(
                channel_name=ChannelName("Fabio Akita"),
                channel_category="tech_ai",
                part_number=1,
                word_count=12000,
                document_count=5,
                output_path=Path("/tmp/master/tech_ai/Fabio_Akita_001.md"),
            )
        ]
        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_uc,
        ):
            code = main(["concat-master", "--channel", "Fabio Akita", "--max-words", "300000"])
            assert code == EXIT_SUCCESS
            mock_uc.execute.assert_called_once_with(
                channel_name=ChannelName("Fabio Akita"), max_words=300000
            )

    def test_cli_concat_master_error_handling(self) -> None:
        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            side_effect=RuntimeError("Disk failure"),
        ):
            code = main(["concat-master"])
            assert code == EXIT_INTERNAL_ERROR

    def test_cli_index_raw_all_channels(self) -> None:
        mock_uc = MagicMock()
        mock_uc.index_all_channels.return_value = {"Canal 1": [MagicMock()]}
        with patch(
            "cresmo.presentation.commands.index_raw.build_index_raw_use_case",
            return_value=mock_uc,
        ) as mock_builder:
            code = main(["index-raw"])
            assert code == EXIT_SUCCESS
            mock_builder.assert_called_once()
            mock_uc.index_all_channels.assert_called_once_with(force=False)

    def test_cli_index_raw_specific_channel_with_flags(self) -> None:
        mock_uc = MagicMock()
        mock_uc.index_channel.return_value = [MagicMock()]
        with patch(
            "cresmo.presentation.commands.index_raw.build_index_raw_use_case",
            return_value=mock_uc,
        ) as mock_builder:
            code = main(
                [
                    "index-raw",
                    "--channel",
                    "Canal Teste",
                    "--web-index",
                    "--model",
                    "custom-model",
                    "--force",
                ]
            )
            assert code == EXIT_SUCCESS
            mock_builder.assert_called_once()
            assert mock_builder.call_args[1]["web_index"] is True
            assert mock_builder.call_args[1]["model_override"] == "custom-model"
            mock_uc.index_channel.assert_called_once_with("Canal Teste", force=True)

    def test_cli_index_raw_error_handling(self) -> None:
        with patch(
            "cresmo.presentation.commands.index_raw.build_index_raw_use_case",
            side_effect=RuntimeError("Ollama failed"),
        ):
            code = main(["index-raw"])
            assert code == EXIT_INTERNAL_ERROR

    def test_cli_index_raw_ollama_probe_failure_exits_config_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_checker = MagicMock()
        mock_checker.check_ollama_probe.return_value = False

        with patch(
            "cresmo.presentation.commands.index_raw.build_preflight_checker",
            return_value=mock_checker,
        ):
            code = main(["index-raw"])
            assert code == EXIT_CONFIG_OR_USAGE_ERROR
            captured = capsys.readouterr()
            assert "unreachable" in captured.err
            assert "ollama serve" in captured.err
