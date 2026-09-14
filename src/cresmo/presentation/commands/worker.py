"""Command handler for cresmo worker."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from cresmo.domain.value_objects import ChannelFeedQuery
from cresmo.presentation.composition import build_sync_channel_use_case
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'worker' subcommand parser with argument options."""
    worker_parser = subparsers.add_parser(
        "worker",
        help="Run continuous polling worker daemon with heartbeat health reporting",
    )
    worker_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL to poll continuously",
    )
    worker_parser.add_argument(
        "--poll-interval",
        type=int,
        default=300,
        help="Polling interval in seconds between feed checks (default: 300)",
    )
    worker_parser.add_argument(
        "--lookback",
        type=int,
        default=7,
        help="Days lookback window for new uploads per polling cycle (default: 7)",
    )
    worker_parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Maximum videos per cycle (default: 10)",
    )
    worker_parser.add_argument(
        "--once",
        action="store_true",
        help="Execute exactly one polling cycle and terminate cleanly",
    )
    worker_parser.set_defaults(handler=handle_worker)


def handle_worker(args: argparse.Namespace) -> int:
    """Run polling daemon for continuous channel monitoring."""
    try:
        use_case = build_sync_channel_use_case()
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        heartbeat_file = Path("/tmp/cresmo_worker.heartbeat")

        sys.stdout.write(
            f"Starting ChannelPollingDaemon for '{args.channel}' (interval: {args.poll_interval}s)...\n"
        )

        while True:
            heartbeat_file.write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
            summary = use_case.execute(query=query)
            sys.stdout.write(
                f"[{datetime.now(UTC).strftime('%H:%M:%S')}] Polled {summary.channel_url}: "
                f"processed={summary.processed_count}, skipped={summary.skipped_count}, failed={summary.failed_count}\n"
            )

            if args.once:
                break

            time.sleep(args.poll_interval)

        return EXIT_SUCCESS
    except KeyboardInterrupt:
        sys.stdout.write("Worker terminated gracefully by signal.\n")
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Worker error: {exc}\n")
        return EXIT_INTERNAL_ERROR
