"""Command handler for cresmo worker.

Runs a continuous polling worker daemon with periodic heartbeat health reporting
suitable for Kubernetes/Docker containerized operation per 12-Factor principles.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-003: PES Production Architecture & Telemetry
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - SPEC-003: Channel Synchronization Specifications
"""

from __future__ import annotations

import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer

from cresmo.domain.value_objects import ChannelFeedQuery
from cresmo.presentation.composition import (
    build_sync_channel_use_case,
    resolve_shared_settings,
)
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def worker(
    channel: Annotated[
        str,
        typer.Option(
            "--channel",
            help="Target YouTube channel or playlist URL to poll continuously",
        ),
    ],
    poll_interval: Annotated[
        int,
        typer.Option(
            "--poll-interval",
            min=10,
            help="Polling interval in seconds between feed checks (default: 300)",
        ),
    ] = 300,
    lookback: Annotated[
        int,
        typer.Option(
            "--lookback",
            min=0,
            help="Days lookback window for new uploads per polling cycle (default: 7)",
        ),
    ] = 7,
    max_videos: Annotated[
        int,
        typer.Option(
            "--max-videos",
            min=1,
            help="Maximum videos per cycle (default: 10)",
        ),
    ] = 10,
    once: Annotated[
        bool,
        typer.Option(
            "--once",
            help="Execute exactly one polling cycle and terminate cleanly",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Run continuous polling worker daemon with heartbeat health reporting."""
    _ = verbose
    code = handle_worker(
        None,
        channel=channel,
        poll_interval=poll_interval,
        lookback=lookback,
        max_videos=max_videos,
        once=once,
    )
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_worker(
    args: Any = None,
    channel: str | None = None,
    poll_interval: int = 300,
    lookback: int = 7,
    max_videos: int = 10,
    once: bool = False,
) -> int:
    """Run polling daemon for continuous channel monitoring.

    Args:
        args: Parsed CLI argument namespace or None.
        channel: Target YouTube channel or playlist URL string.
        poll_interval: Polling interval in seconds.
        lookback: Days lookback window.
        max_videos: Maximum videos per cycle.
        once: Whether to execute single cycle and terminate.

    Returns:
        Process exit code integer.
    """
    target_channel = getattr(args, "channel", channel) if args is not None else channel
    target_poll_interval = (
        getattr(args, "poll_interval", poll_interval) if args is not None else poll_interval
    )
    target_lookback = getattr(args, "lookback", lookback) if args is not None else lookback
    target_max_videos = getattr(args, "max_videos", max_videos) if args is not None else max_videos
    target_once = getattr(args, "once", once) if args is not None else once

    try:
        settings = resolve_shared_settings()
        use_case = build_sync_channel_use_case(settings=settings)
        query = ChannelFeedQuery(
            channel_url=target_channel or "",
            lookback_days=target_lookback,
            max_videos=target_max_videos,
        )
        heartbeat_file = Path(tempfile.gettempdir()) / "cresmo_worker.heartbeat"

        sys.stdout.write(
            f"Starting ChannelPollingDaemon for '{target_channel}' (interval: {target_poll_interval}s)...\n"
        )

        while True:
            heartbeat_file.write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
            summary = use_case.execute(query=query)
            sys.stdout.write(
                f"[{datetime.now(UTC).strftime('%H:%M:%S')}] Polled {summary.channel_url}: "
                f"processed={summary.processed_count}, skipped={summary.skipped_count}, failed={summary.failed_count}\n"
            )

            if target_once:
                break

            time.sleep(target_poll_interval)

        return EXIT_SUCCESS
    except KeyboardInterrupt:
        sys.stdout.write("Worker terminated gracefully by signal.\n")
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Worker error: {exc}\n")
        return EXIT_INTERNAL_ERROR
