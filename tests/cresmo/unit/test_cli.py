"""Unit tests for Cresmo Humble Object CLI Controller.

Verifies argument parsing, flag overrides, environment checks, and standardized
process exit codes per SPEC-002 §4.1 & §4.2.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from cresmo.application.pipeline import PipelineResult
from cresmo.domain.entities import RawTranscript
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import ContentId
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

    def test_cli_no_args_returns_code_2(self) -> None:
        assert main([]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_invalid_subcommand_returns_code_2(self) -> None:
        assert main(["invalid-command"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_run_missing_url_returns_code_2(self) -> None:
        assert main(["run"]) == EXIT_CONFIG_OR_USAGE_ERROR

    def test_cli_check_config_success_returns_code_0(self) -> None:
        with patch("cresmo.presentation.cli.CresmoSettings") as mock_settings_cls:
            mock_settings = MagicMock(spec=CresmoSettings)
            mock_settings.vault_dir = "/tmp/vault"
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.batch_size = 5
            mock_settings_cls.return_value = mock_settings

            exit_code = main(["check-config"])
            assert exit_code == EXIT_SUCCESS

    def test_cli_check_config_validation_error_returns_code_2(self) -> None:
        from pydantic import ValidationError

        with patch("cresmo.presentation.cli.CresmoSettings", side_effect=ValidationError.from_exception_data(
            title="CresmoSettings", line_errors=[]
        )):
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
                gap_filler_passes=1,
            )

    def test_cli_run_with_flag_overrides(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("dQw4w9WgXcQ"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline) as mock_builder:
            exit_code = main([
                "run",
                "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "--passes", "3",
                "--batch-size", "9",
            ])

            assert exit_code == EXIT_SUCCESS
            mock_builder.assert_called_once_with(batch_size_override=9)
            mock_pipeline.run_for_video.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                gap_filler_passes=3,
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
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ", "--dry-run"])

            assert exit_code == EXIT_SUCCESS
            mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ"
            )
            mock_pipeline.run_for_video.assert_not_called()

    def test_cli_maps_domain_validation_error_to_code_3(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = DomainValidationError("Invalid domain entity")

        with patch("cresmo.presentation.cli.build_pipeline", return_value=mock_pipeline):
            exit_code = main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])
            assert exit_code == EXIT_DOMAIN_VALIDATION_ERROR

    def test_cli_maps_rate_limit_error_to_code_4(self) -> None:
        mock_pipeline = MagicMock()
        mock_pipeline.run_for_video.side_effect = RateLimitExceededError("HTTP 429 Too Many Requests")

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
