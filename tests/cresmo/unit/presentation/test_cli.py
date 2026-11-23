"""Unit tests for Cresmo Humble Object CLI Controller.

Verifies argument parsing, flag overrides, environment checks, and standardized
process exit codes per SPEC-002 §4.1 & §4.2.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline import PipelineResult
from cresmo.application.services.preflight import PreflightResult
from cresmo.application.use_cases.run_synthesis import RunSynthesisRequest
from cresmo.domain.entities import StageTranscript
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    Channel,
    ChannelFeedQuery,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    PipelineStatus,
    SyncSummary,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.cli import (
    app,
    main,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class TestCresmoCLI:
    """Hermetic unit tests for CLI entrypoint and exit codes."""

    def test_typer_app_registered_commands(self) -> None:
        """Verify that all 8 subcommands are registered in Typer app."""
        registered_commands = {cmd.name for cmd in app.registered_commands if cmd.name}
        expected_commands = {
            "run",
            "check-config",
            "sync",
            "worker",
            "dedupe",
            "export-cookies",
            "concat-master",
            "seed-prompts",
        }
        assert registered_commands == expected_commands

    def test_cli_public_all_interface(self) -> None:
        """Verify that cli.__all__ strictly exposes only published entrypoint primitives."""
        import cresmo.presentation.cli as cli_mod

        assert cli_mod.__all__ == ["app", "main"]

    def test_exit_codes_public_all_interface(self) -> None:
        """Verify that exit_codes.__all__ defines the complete canonical taxonomy."""
        import cresmo.presentation.exit_codes as exit_codes_mod

        assert exit_codes_mod.__all__ == [
            "EXIT_CONFIG_OR_USAGE_ERROR",
            "EXIT_DOMAIN_VALIDATION_ERROR",
            "EXIT_INGESTION_ERROR",
            "EXIT_INTERNAL_ERROR",
            "EXIT_RATE_LIMIT_EXCEEDED",
            "EXIT_SUCCESS",
        ]

    def test_cli_no_args_defaults_to_run(self) -> None:
        """Verify running main([]) defaults to dispatching 'run' per CLI entrypoint."""
        with patch(
            "cresmo.presentation.commands.run.handle_run", return_value=EXIT_SUCCESS
        ) as mock_handle:
            assert main([]) == EXIT_SUCCESS
            mock_handle.assert_called_once_with(RunSynthesisRequest())

    def test_cli_none_argv_defaults_to_sys_argv(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_discover = MagicMock()
        mock_discover.execute.return_value = []
        with (
            patch("sys.argv", ["cresmo", "run"]),
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline"),
            patch(
                "cresmo.bootstrap.composition.build_discover_batch_sources_use_case",
                return_value=mock_discover,
            ),
        ):
            assert main(None) == EXIT_SUCCESS

    def test_cli_disallows_implicit_run_routing_with_flags(self) -> None:
        """Verify passing flags without subcommand returns usage error per ADR-042."""
        exit_code = main(["--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
        assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_help_flag_handling(self) -> None:
        assert main(["-h"]) == EXIT_SUCCESS
        assert main(["--help"]) == EXIT_SUCCESS

    def test_cli_invalid_subcommand_returns_code_2(self) -> None:
        assert main(["invalid-command"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_run_without_args_runs_batch(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_discover = MagicMock()
        mock_discover.execute.return_value = []
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline"),
            patch(
                "cresmo.bootstrap.composition.build_discover_batch_sources_use_case",
                return_value=mock_discover,
            ),
        ):
            assert main(["run"]) == EXIT_SUCCESS

    def test_cli_check_config_success_returns_code_0(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with (
            patch(
                "cresmo.presentation.commands.check_config.load_fresh_settings"
            ) as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.check_config.build_preflight_checker"
            ) as mock_checker_builder,
        ):
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings.vault_dir = Path("/tmp/vault")
            mock_settings.sqlite_ledger_path = Path("/tmp/vault/cresmo_ledger.db")
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.batch_size = 5
            mock_settings.langfuse_public_key = ""
            mock_settings.langfuse_secret_key = None
            mock_settings.langfuse_host = "https://cloud.langfuse.com"
            mock_settings_cls.return_value = mock_settings

            mock_checker = MagicMock()
            mock_checker.check_all.return_value = PreflightResult(is_healthy=True, errors=())
            mock_checker_builder.return_value = mock_checker

            exit_code = main(["check-config"])
            assert exit_code == EXIT_SUCCESS
            mock_checker_builder.assert_called_once_with(settings=mock_settings)
            captured = capsys.readouterr()
            assert "Configuration and environment verified successfully:\n" in captured.out
            assert "- Vault Root: /tmp/vault\n" in captured.out
            assert "- SQLite Ledger: /tmp/vault/cresmo_ledger.db\n" in captured.out
            assert "- Gemini Model: gemini-2.5-flash\n" in captured.out
            assert "- Batch Size: 5\n" in captured.out
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

    def test_cli_check_config_preflight_failure_returns_code_2(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with (
            patch(
                "cresmo.presentation.commands.check_config.load_fresh_settings"
            ) as mock_settings_cls,
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
            mock_checker_builder.assert_called_once_with(settings=mock_settings)
            captured = capsys.readouterr()
            assert "Preflight environmental checks failed:\n" in captured.err
            assert "- Missing GEMINI_API_KEY\n" in captured.err

    def test_cli_run_success_returns_code_0(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("dQw4w9WgXcQ"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
            patch("cresmo.bootstrap.composition.build_concat_master_use_case"),
        ):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.run_for_video.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                gap_filler_passes=3,
                force_reprocess=False,
            )

    def test_cli_run_with_flag_overrides(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("dQw4w9WgXcQ"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch(
                "cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline
            ) as mock_builder,
            patch("cresmo.bootstrap.composition.build_concat_master_use_case"),
        ):
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
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_raw = StageTranscript(
            channel=Channel(name=ChannelName("TestChannel")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=ContentId("dQw4w9WgXcQ"),
                title="Test Title",
                text="Verbatim transcript content.",
            ),
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
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

        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("video11111111"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
            patch("cresmo.bootstrap.composition.build_concat_master_use_case"),
        ):
            exit_code = main(["run", "--manifest", str(manifest_file)])

            assert exit_code == EXIT_SUCCESS
            assert mock_pipeline.run_for_video.call_count == 2

    def test_cli_run_all_dry_run(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "test_playlist.txt"
        manifest_file.write_text(
            "https://youtube.com/watch?v=video11111111\n",
            encoding="utf-8",
        )

        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_raw = StageTranscript(
            channel=Channel(name=ChannelName("TestChan")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=video11111111"),
            content=Content(
                id=ContentId("video11111111"),
                title="Test Title",
                text="Content",
            ),
        )
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
            exit_code = main(["run", "--dry-run", "--manifest", str(manifest_file)])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=video11111111"
            )
            mock_pipeline.run_for_video.assert_not_called()

    def test_cli_run_all_missing_manifest_returns_usage_error(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "non_existent.txt"
        with patch("cresmo.bootstrap.composition.build_pipeline"):
            exit_code = main(["run", "--manifest", str(missing_file)])
        assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_maps_domain_validation_error_to_code_3(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = DomainValidationError("Invalid domain entity")

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_DOMAIN_VALIDATION_ERROR

    def test_cli_maps_rate_limit_error_to_code_4(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RateLimitExceededError(
            "HTTP 429 Too Many Requests"
        )

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_maps_ingestion_error_to_code_5(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = IngestionNetworkError("Whisper failed")

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_maps_unexpected_error_to_code_1(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RuntimeError("Fatal crash")

        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
        ):
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
        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ) as mock_builder,
        ):
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
        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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
        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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
        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@b,https://youtube.com/@a"])
            assert exit_code == EXIT_SUCCESS
            assert mock_use_case.execute.call_count == 2
            # ADR-012: Ensure channels were called in alphabetical order: @a then @b
            calls = mock_use_case.execute.call_args_list
            assert calls[0].kwargs["query"].channel_url == "https://youtube.com/@a"
            assert calls[1].kwargs["query"].channel_url == "https://youtube.com/@b"

    def test_cli_run_with_filter_criteria_propagated(self) -> None:
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_discover = MagicMock()
        mock_discover.execute.return_value = []
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline"),
            patch(
                "cresmo.bootstrap.composition.build_discover_batch_sources_use_case",
                return_value=mock_discover,
            ),
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
            mock_discover.execute.assert_called_once()
            query = mock_discover.execute.call_args.kwargs["query"]
            assert query.filter_criteria.channels == ("ancapsu", "mises")
            assert query.filter_criteria.categories == ("politics_br",)
            assert query.filter_criteria.video_ids == ("dQw4w9WgXcQ",)

    def test_cli_sync_rate_limit_error_returns_code_4(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RateLimitExceededError("Quota exhausted")

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_cli_sync_ingestion_error_returns_code_5(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = IngestionNetworkError("Network down")

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_INGESTION_ERROR

    def test_cli_sync_security_violation_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = SecurityViolationError("Traversal detected")

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
        ):
            exit_code = main(["sync", "--channel", "https://youtube.com/@test"])
            assert exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_sync_preflight_error_returns_code_2(self) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = PreflightError("Missing tool ffmpeg")

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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

    def test_cli_dedupe_success_returns_code_0(self, capsys: pytest.CaptureFixture[str]) -> None:
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
                    merged_titles=(NoteTitle("D. Afonso Henriques"), NoteTitle("Rei Fundador")),
                    links_rewritten_count=3,
                ),
            )
        )

        mock_settings = MagicMock()
        with (
            patch(
                "cresmo.presentation.commands.dedupe.resolve_shared_settings",
                return_value=mock_settings,
            ) as mock_resolve_settings,
            patch(
                "cresmo.presentation.commands.dedupe.build_unify_duplicates_use_case",
                return_value=mock_use_case,
            ) as mock_builder,
        ):
            exit_code = main(["dedupe"])
            assert exit_code == EXIT_SUCCESS
            mock_resolve_settings.assert_called_once()
            mock_builder.assert_called_once_with(settings=mock_settings)
            mock_use_case.execute.assert_called_once()
            captured = capsys.readouterr()
            assert captured.out.startswith("Vault Graph Deduplication Summary:\n")
            assert "- Duplicate Clusters Unified: 1\n" in captured.out
            assert "- Total Inbound WikiLinks Rewritten: 3\n" in captured.out
            assert (
                "  • Unified into [[Dom Afonso Henriques]]: [[D. Afonso Henriques]], [[Rei Fundador]] (3 links rewritten)\n"
                in captured.out
            )

    def test_cli_dedupe_with_vault_flags_and_verbose(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        from cresmo.application.use_cases.unify_duplicate_notes import DeduplicationReport

        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = DeduplicationReport(clusters=())

        custom_vault = tmp_path / "custom_vault"
        custom_vault.mkdir()

        mock_settings = MagicMock()
        mock_copied_settings = MagicMock()
        mock_copied_settings.vault_dir = custom_vault
        mock_settings.model_copy.return_value = mock_copied_settings

        with (
            patch(
                "cresmo.presentation.commands.dedupe.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.dedupe.build_unify_duplicates_use_case",
                return_value=mock_use_case,
            ) as mock_builder,
        ):
            exit_code = main(["dedupe", "--vault", str(custom_vault), "--verbose"])
            assert exit_code == EXIT_SUCCESS
            mock_settings.model_copy.assert_called_once_with(
                update={"vault_dir": custom_vault.resolve()}
            )
            mock_builder.assert_called_once_with(settings=mock_copied_settings)
            captured = capsys.readouterr()
            assert f"Vault directory: {custom_vault}" in captured.out

    def test_cli_dedupe_exception_returns_code_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RuntimeError("Graph corruption")

        with patch(
            "cresmo.presentation.commands.dedupe.build_unify_duplicates_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["dedupe"])
            assert exit_code == EXIT_INTERNAL_ERROR
            captured = capsys.readouterr()
            assert "Deduplication error: Graph corruption\n" in captured.err

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
        """Verify that --subtitle-workers, --whisper-workers, and --discovery-workers are rejected."""
        assert main(["run", "--subtitle-workers", "5"]) == EXIT_CONFIG_OR_USAGE_ERROR
        assert main(["run", "--whisper-workers", "2"]) == EXIT_CONFIG_OR_USAGE_ERROR
        assert main(["run", "--discovery-workers", "10"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_check_config_telemetry_masked_and_exceptions(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from types import SimpleNamespace as Namespace

        from pydantic import SecretStr

        from cresmo.presentation.commands.check_config import handle_check_config

        # 1. Langfuse public key and secret key configured
        with (
            patch(
                "cresmo.presentation.commands.check_config.load_fresh_settings"
            ) as mock_settings_cls,
            patch(
                "cresmo.presentation.commands.check_config.build_preflight_checker"
            ) as mock_checker_builder,
        ):
            # 1a. Custom host
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings.vault_dir = Path("/tmp/vault")
            mock_settings.sqlite_ledger_path = Path("/tmp/vault/cresmo_ledger.db")
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.batch_size = 5
            mock_settings.langfuse_public_key = "pk-lf-1234567890abcdef"
            mock_settings.langfuse_secret_key = SecretStr("sk-lf-secret")
            mock_settings.langfuse_host = "http://custom-host:3000"
            mock_settings.langfuse_environment = "production"
            mock_settings_cls.return_value = mock_settings

            mock_checker = MagicMock()
            mock_checker.check_all.return_value = PreflightResult(is_healthy=True, errors=())
            mock_checker_builder.return_value = mock_checker

            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert (
                "- Langfuse Telemetry: Enabled (http://custom-host:3000, env=production, pk-lf-1234...)\n"
                in captured.out
            )

            # 1b. Missing langfuse_host and langfuse_environment attributes exercise defaults
            del mock_settings.langfuse_host
            del mock_settings.langfuse_environment
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert (
                "- Langfuse Telemetry: Enabled (https://cloud.langfuse.com, env=staging, pk-lf-1234...)\n"
                in captured.out
            )

            # 1c. Secret without get_secret_value
            mock_settings.langfuse_secret_key = "plain-string-no-method"
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

            # 1d. Secret with empty get_secret_value
            mock_settings.langfuse_secret_key = SecretStr("")
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

            # 1e. None secret
            mock_settings.langfuse_secret_key = None
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

            # 1f. Empty public key with valid secret
            mock_settings.langfuse_public_key = ""
            mock_settings.langfuse_secret_key = SecretStr("sk-valid")
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

            # 1g. Missing public key attribute
            del mock_settings.langfuse_public_key
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

            # 1h. Missing secret key attribute
            del mock_settings.langfuse_secret_key
            code = handle_check_config(Namespace())
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "- Langfuse Telemetry: Disabled (no credentials configured)\n" in captured.out

        # 2. PreflightError
        with patch(
            "cresmo.presentation.commands.check_config.load_fresh_settings",
            side_effect=PreflightError("Vault missing"),
        ):
            code = handle_check_config(Namespace())
            assert code == EXIT_CONFIG_OR_USAGE_ERROR
            captured = capsys.readouterr()
            assert "Preflight error: Vault missing\n" in captured.err

        # 3. ValidationError
        with patch("cresmo.presentation.commands.check_config.load_fresh_settings") as mock_s:
            from pydantic import BaseModel, ValidationError

            class Dummy(BaseModel):
                num: int

            try:
                Dummy.model_validate({"num": "invalid"})
            except ValidationError as ve:
                mock_s.side_effect = ve
            code = handle_check_config(Namespace())
            assert code == EXIT_CONFIG_OR_USAGE_ERROR
            captured = capsys.readouterr()
            assert "Configuration error:" in captured.err

        # 4. Generic unexpected exception
        with patch(
            "cresmo.presentation.commands.check_config.load_fresh_settings",
            side_effect=RuntimeError("Hardware fault"),
        ):
            code = handle_check_config(Namespace())
            assert code == EXIT_INTERNAL_ERROR
            captured = capsys.readouterr()
            assert "Unexpected configuration error: Hardware fault\n" in captured.err

    def test_cli_help_flag_returns_exit_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify that -h / --help prints root help and exits cleanly with EXIT_SUCCESS (0)."""
        code = main(["--help"])
        assert code == EXIT_SUCCESS
        out, _ = capsys.readouterr()
        assert "cresmo" in out.lower()

        code_short = main(["-h"])
        assert code_short == EXIT_SUCCESS

        code_run_help = main(["run", "--help"])
        assert code_run_help == EXIT_SUCCESS
        out_run, _ = capsys.readouterr()
        assert "batch-size" in out_run

    def test_cli_argv_none_uses_sys_argv(self) -> None:
        """Verify that passing argv=None defaults to reading sys.argv[1:]."""
        with (
            patch("sys.argv", ["cresmo", "check-config"]),
            patch("cresmo.presentation.commands.check_config.handle_check_config") as mock_check,
        ):
            mock_check.return_value = EXIT_SUCCESS
            code = main(None)
            assert code == EXIT_SUCCESS
            assert mock_check.called

    def test_cli_empty_argv_routes_to_default_run(self) -> None:
        """Verify passing explicit empty list argv=[] routes to default run subcommand."""
        with patch(
            "cresmo.presentation.commands.run.handle_run", return_value=EXIT_SUCCESS
        ) as mock_handle:
            code = main([])
            assert code == EXIT_SUCCESS
            mock_handle.assert_called_once_with(RunSynthesisRequest())

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

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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
            Dummy.model_validate({"n": "bad"})
        except ValidationError as ve:
            mock_use_case.execute.side_effect = ve

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
        ):
            assert (
                main(["sync", "--channel", "https://youtube.com/@test"])
                == EXIT_CONFIG_OR_USAGE_ERROR
            )

    def test_cli_sync_generic_exception_returns_internal_error(self) -> None:
        """Verify that unexpected exception in sync returns EXIT_INTERNAL_ERROR (1)."""
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = RuntimeError("Sync explosion")

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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

        with (
            patch("cresmo.bootstrap.composition.ensure_runtime_directories"),
            patch(
                "cresmo.bootstrap.composition.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
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
                ["worker", "--channel", "https://youtube.com/@test", "--poll-interval", "10"]
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

    # SPEC-042 Test Suites (Refractometry - Phase 2)
    def test_root_cli_help_displays_all_subcommands(self) -> None:
        """Verify root help via CliRunner renders all 8 expected subcommands."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        expected = [
            "run",
            "check-config",
            "sync",
            "worker",
            "dedupe",
            "export-cookies",
            "concat-master",
            "seed-prompts",
        ]
        for cmd in expected:
            assert cmd in result.output

    def test_root_cli_no_args_displays_help_and_exits(self) -> None:
        """Verify invoking root app without arguments displays help and exits with code 2."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        result = runner.invoke(app, [])
        assert result.exit_code in (0, 2)
        assert "Usage: " in result.output

    def test_invalid_subcommand_returns_exit_config_or_usage_error(self) -> None:
        """Verify invalid subcommand via CliRunner returns code 2."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["nonexistent-command"])
        assert result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_run_command_validates_passes_boundary(self) -> None:
        """Verify --passes enforces [1, 10] bounds fail-fast."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        res_min = runner.invoke(app, ["run", "--passes", "0"])
        assert res_min.exit_code == EXIT_CONFIG_OR_USAGE_ERROR

        res_max = runner.invoke(app, ["run", "--passes", "15"])
        assert res_max.exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_run_command_validates_nonexistent_manifest_file(self) -> None:
        """Verify --manifest enforces file existence fail-fast."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["run", "--manifest", "/nonexistent/manifest.txt"])
        assert result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_run_command_maps_rate_limit_exceeded_to_exit_code_4(self) -> None:
        """Verify RateLimitExceededError maps to EXIT_RATE_LIMIT_EXCEEDED (4)."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch(
                "cresmo.bootstrap.composition.build_pipeline",
                side_effect=RateLimitExceededError("Rate limit reached"),
            ),
        ):
            result = runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])
            assert result.exit_code == EXIT_RATE_LIMIT_EXCEEDED

    def test_run_command_maps_ingestion_error_to_exit_code_5(self) -> None:
        """Verify IngestionNetworkError maps to EXIT_INGESTION_ERROR (5)."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch(
                "cresmo.bootstrap.composition.build_pipeline",
                side_effect=IngestionNetworkError("Ingestion failure"),
            ),
        ):
            result = runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])
            assert result.exit_code == EXIT_INGESTION_ERROR

    def test_run_command_maps_domain_validation_error_to_exit_code_3(self) -> None:
        """Verify DomainValidationError maps to EXIT_DOMAIN_VALIDATION_ERROR (3)."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch(
                "cresmo.bootstrap.composition.build_pipeline",
                side_effect=DomainValidationError("Invalid domain state"),
            ),
        ):
            result = runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])
            assert result.exit_code == EXIT_DOMAIN_VALIDATION_ERROR

    def test_run_command_maps_preflight_error_to_exit_code_2(self) -> None:
        """Verify PreflightError maps to EXIT_CONFIG_OR_USAGE_ERROR (2)."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        mock_checker = MagicMock()
        mock_checker.check_all.side_effect = PreflightError("Preflight check failure")
        with patch(
            "cresmo.bootstrap.composition.build_preflight_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])
            assert result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR

    def test_run_command_translates_channel_option_to_channel_name_vo(self) -> None:
        """Verify --channel argument is translated to ChannelName in BatchDiscoveryQuery."""
        from typer.testing import CliRunner

        from cresmo.presentation.cli import app

        runner = CliRunner()
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = PreflightResult(
            is_healthy=True, errors=(), warnings=()
        )
        mock_pipeline = MagicMock()
        mock_discover = MagicMock()
        mock_discover.execute.return_value = []
        with (
            patch(
                "cresmo.bootstrap.composition.build_preflight_checker", return_value=mock_checker
            ),
            patch("cresmo.bootstrap.composition.build_pipeline", return_value=mock_pipeline),
            patch(
                "cresmo.bootstrap.composition.build_discover_batch_sources_use_case",
                return_value=mock_discover,
            ),
        ):
            result = runner.invoke(app, ["run", "--channel", "Spotniks", "--dry-run"])
            assert result.exit_code == EXIT_SUCCESS
            mock_discover.execute.assert_called_once()
            query = mock_discover.execute.call_args.kwargs["query"]
            assert ChannelName("Spotniks").value.lower() in query.filter_criteria.channels
