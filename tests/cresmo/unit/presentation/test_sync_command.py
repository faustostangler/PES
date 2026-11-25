"""Hermetic unit tests for Humble Object 'cresmo sync' command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-002 / SPEC-003 / SPEC-067: CLI Controller & Channel Sync Contracts
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.use_cases.sync_batch import (
    SyncBatchOutcome,
    SyncBatchRequest,
    SyncTargetEvent,
    SyncTargetEventKind,
)
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.presentation.cli import main
from cresmo.presentation.commands.sync import _render_sync_event, _render_sync_outcome, handle_sync
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class TestSyncCommand:
    """Hermetic unit tests for Humble Object sync CLI controller."""

    def test_sync_cli_help(self) -> None:
        """Verify sync CLI displays help and options."""
        assert main(["sync", "--help"]) == EXIT_SUCCESS

    def test_handle_sync_delegates_to_use_case_and_renders_summary(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        mock_uc = MagicMock()
        mock_uc.execute.return_value = SyncBatchOutcome(
            channels_synced=2,
            total_discovered=5,
            total_processed=3,
            total_skipped=2,
            total_failed=0,
            manifest_path=tmp_path / "playlist.txt",
        )
        req = SyncBatchRequest(channels=("@alpha",), lookback=14, max_videos=20)

        with patch(
            "cresmo.presentation.commands.sync.build_sync_batch_use_case",
            return_value=mock_uc,
        ) as mock_builder:
            code = handle_sync(req)

        assert code == EXIT_SUCCESS
        mock_builder.assert_called_once_with()
        mock_uc.execute.assert_called_once()
        assert mock_uc.execute.call_args.args[0] == req
        out = capsys.readouterr().out
        assert "Channel Synchronization Summary:" in out
        assert "- Channels synced: 2" in out
        assert "- Processed: 3" in out

    def test_render_sync_event_and_empty_or_failed_outcomes(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        _render_sync_event(
            SyncTargetEvent(
                kind=SyncTargetEventKind.VIDEO,
                target="vid1",
                total_discovered=1,
                processed=1,
                skipped=0,
                failed=0,
                duration_seconds=0.2,
            )
        )
        _render_sync_event(
            SyncTargetEvent(
                kind=SyncTargetEventKind.CHANNEL,
                target="https://youtube.com/@mises",
                total_discovered=3,
                processed=2,
                skipped=1,
                failed=0,
                duration_seconds=1.5,
            )
        )

        manifest = tmp_path / "empty.txt"
        empty_code = _render_sync_outcome(
            SyncBatchOutcome(
                no_matching_channels=True,
                mode_description="categories=unknown",
                manifest_path=manifest,
            )
        )
        assert empty_code == EXIT_SUCCESS

        failed_code = _render_sync_outcome(SyncBatchOutcome(direct_video_mode=True, total_failed=1))
        assert failed_code == EXIT_INTERNAL_ERROR

        out = capsys.readouterr().out
        assert "[video] vid1: 1 processed, 0 skipped, 0 failed" in out
        assert (
            "[https://youtube.com/@mises] discovered=3 processed=2 skipped=1 failed=0 (1.5s)" in out
        )
        assert (
            f"No channels found matching filter (categories=unknown). Verify manifest at '{manifest}' and filter criteria."
            in out
        )

    @pytest.mark.parametrize(
        ("exc", "expected_code", "expected_prefix"),
        [
            (
                RateLimitExceededError("429 Too Many Requests"),
                EXIT_RATE_LIMIT_EXCEEDED,
                "Rate limit exceeded:",
            ),
            (
                IngestionNetworkError("Socket closed"),
                EXIT_INGESTION_ERROR,
                "Ingestion network error:",
            ),
            (PreflightError("Ollama offline"), EXIT_CONFIG_OR_USAGE_ERROR, "Preflight error:"),
            (
                DomainValidationError("Invalid schema"),
                EXIT_DOMAIN_VALIDATION_ERROR,
                "Domain validation error:",
            ),
            (RuntimeError("Unknown bug"), EXIT_INTERNAL_ERROR, "Unexpected sync error:"),
        ],
    )
    def test_handle_sync_exceptions_mapped_to_exit_codes(
        self,
        capsys: pytest.CaptureFixture[str],
        exc: BaseException,
        expected_code: int,
        expected_prefix: str,
    ) -> None:
        with patch(
            "cresmo.presentation.commands.sync.build_sync_batch_use_case",
            side_effect=exc,
        ):
            code = handle_sync(SyncBatchRequest(channels=("https://youtube.com/@test",)))
        assert code == expected_code
        assert expected_prefix in capsys.readouterr().err
