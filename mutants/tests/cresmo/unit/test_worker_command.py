"""Unit tests for 'cresmo worker' presentation command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-003: PES Production Architecture & Telemetry
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-003: Channel Synchronization Specifications
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.value_objects import ChannelFeedQuery, PipelineStatus, SyncSummary
from cresmo.presentation.cli import main
from cresmo.presentation.commands.worker import (
    handle_worker,
    register_subparser,
)
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


class TestWorkerCommand:
    """Test suite for cresmo worker CLI command."""

    def test_register_subparser_options_and_defaults(self) -> None:
        """Verify worker subparser arguments, choices, types, defaults, and helps."""
        mock_subparsers = MagicMock()
        mock_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_parser

        register_subparser(mock_subparsers)

        mock_subparsers.add_parser.assert_called_once_with(
            "worker",
            help="Run continuous polling worker daemon with heartbeat health reporting",
        )

        expected_arguments = [
            (
                ("--channel",),
                {
                    "required": True,
                    "help": "Target YouTube channel or playlist URL to poll continuously",
                },
            ),
            (
                ("--poll-interval",),
                {
                    "type": int,
                    "default": 300,
                    "help": "Polling interval in seconds between feed checks (default: 300)",
                },
            ),
            (
                ("--lookback",),
                {
                    "type": int,
                    "default": 7,
                    "help": "Days lookback window for new uploads per polling cycle (default: 7)",
                },
            ),
            (
                ("--max-videos",),
                {
                    "type": int,
                    "default": 10,
                    "help": "Maximum videos per cycle (default: 10)",
                },
            ),
            (
                ("--once",),
                {
                    "action": "store_true",
                    "help": "Execute exactly one polling cycle and terminate cleanly",
                },
            ),
        ]

        assert mock_parser.add_argument.call_count == len(expected_arguments)
        for args, kwargs in expected_arguments:
            mock_parser.add_argument.assert_any_call(*args, **kwargs)

        mock_parser.set_defaults.assert_called_once_with(handler=handle_worker)

    def test_worker_once_successful_cycle(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify worker executes single cycle with --once, writes heartbeat, logs summary, and exits 0."""
        mock_settings = MagicMock()
        mock_use_case = MagicMock()
        mock_summary = SyncSummary(
            channel_url="https://youtube.com/@cresmo",
            total_discovered=5,
            processed_count=3,
            skipped_count=2,
            failed_count=0,
            duration_seconds=1.5,
            status=PipelineStatus.COMPLETED,
        )
        mock_use_case.execute.return_value = mock_summary

        args = argparse.Namespace(
            channel="https://youtube.com/@cresmo",
            poll_interval=120,
            lookback=14,
            max_videos=25,
            once=True,
        )

        fake_temp_dir = tmp_path / "temp"
        fake_temp_dir.mkdir()
        heartbeat_file = fake_temp_dir / "cresmo_worker.heartbeat"

        with (
            patch(
                "cresmo.presentation.commands.worker.resolve_shared_settings",
                return_value=mock_settings,
            ) as mock_resolve_settings,
            patch(
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
            ) as mock_build_uc,
            patch("tempfile.gettempdir", return_value=str(fake_temp_dir)),
        ):
            code = handle_worker(args)
            assert code == EXIT_SUCCESS
            mock_resolve_settings.assert_called_once()
            mock_build_uc.assert_called_once_with(settings=mock_settings)

            mock_use_case.execute.assert_called_once()
            call_query = mock_use_case.execute.call_args.kwargs["query"]
            assert isinstance(call_query, ChannelFeedQuery)
            assert call_query.channel_url == "https://youtube.com/@cresmo"
            assert call_query.lookback_days == 14
            assert call_query.max_videos == 25

            # Assert heartbeat file was written
            assert heartbeat_file.exists()
            content = heartbeat_file.read_text(encoding="utf-8")
            assert len(content) > 0
            # Validate valid ISO format
            assert datetime.fromisoformat(content) is not None

            captured = capsys.readouterr()
            assert (
                "Starting ChannelPollingDaemon for 'https://youtube.com/@cresmo' (interval: 120s)...\n"
                in captured.out
            )
            assert (
                "Polled https://youtube.com/@cresmo: processed=3, skipped=2, failed=0\n"
                in captured.out
            )
            assert captured.err == ""

    def test_worker_polling_loop_sleep_and_keyboard_interrupt(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify worker enters polling loop, sleeps for configured interval, and handles KeyboardInterrupt cleanly."""
        mock_settings = MagicMock()
        mock_use_case = MagicMock()
        mock_summary = SyncSummary(
            channel_url="https://youtube.com/@loop",
            total_discovered=1,
            processed_count=1,
            skipped_count=0,
            failed_count=0,
            duration_seconds=0.5,
            status=PipelineStatus.COMPLETED,
        )
        mock_use_case.execute.return_value = mock_summary

        args = argparse.Namespace(
            channel="https://youtube.com/@loop",
            poll_interval=45,
            lookback=7,
            max_videos=10,
            once=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.worker.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
            patch("tempfile.gettempdir", return_value=str(tmp_path)),
            patch("time.sleep", side_effect=KeyboardInterrupt) as mock_sleep,
        ):
            code = handle_worker(args)
            assert code == EXIT_SUCCESS
            mock_sleep.assert_called_once_with(45)

            captured = capsys.readouterr()
            assert "Worker terminated gracefully by signal.\n" in captured.out
            assert captured.err == ""

    def test_worker_unhandled_exception_returns_internal_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify unhandled exception during polling outputs error to stderr and returns EXIT_INTERNAL_ERROR (1)."""
        args = argparse.Namespace(
            channel="https://youtube.com/@broken",
            poll_interval=300,
            lookback=7,
            max_videos=10,
            once=True,
        )

        with (
            patch(
                "cresmo.presentation.commands.worker.resolve_shared_settings",
                side_effect=RuntimeError("Fatal database connection loss"),
            ),
            patch("tempfile.gettempdir", return_value=str(tmp_path)),
        ):
            code = handle_worker(args)
            assert code == EXIT_INTERNAL_ERROR

            captured = capsys.readouterr()
            assert captured.out == ""
            assert captured.err == "Worker error: Fatal database connection loss\n"

    def test_worker_cli_main_dispatch(self, tmp_path: Path) -> None:
        """Verify 'cresmo worker --channel ... --once' dispatches via root CLI main entrypoint."""
        mock_settings = MagicMock()
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = SyncSummary(
            channel_url="https://youtube.com/@main",
            total_discovered=0,
            processed_count=0,
            skipped_count=0,
            failed_count=0,
            duration_seconds=0.1,
            status=PipelineStatus.COMPLETED,
        )

        with (
            patch(
                "cresmo.presentation.commands.worker.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.worker.build_sync_channel_use_case",
                return_value=mock_use_case,
            ),
            patch("tempfile.gettempdir", return_value=str(tmp_path)),
        ):
            exit_code = main(["worker", "--channel", "https://youtube.com/@main", "--once"])
            assert exit_code == EXIT_SUCCESS
