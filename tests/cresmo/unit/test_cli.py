"""Unit tests for Cresmo Humble Object CLI Controller.

Verifies argument parsing, flag overrides, environment checks, and standardized
process exit codes per SPEC-002 §4.1 & §4.2.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

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
