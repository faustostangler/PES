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
from typing import Annotated, Any, Final

import typer

from cresmo.domain.value_objects import ChannelFeedQuery
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

_MIN_POLL_INTERVAL_SECONDS: Final[int] = 10
DEFAULT_WORKER_POLL_INTERVAL_SECONDS: Final[int] = 300
_MIN_LOOKBACK_DAYS: Final[int] = 0
DEFAULT_WORKER_LOOKBACK_DAYS: Final[int] = 7
_MIN_MAX_VIDEOS: Final[int] = 1
DEFAULT_WORKER_MAX_VIDEOS: Final[int] = 10
_HEARTBEAT_FILENAME: Final[str] = "cresmo_worker.heartbeat"
_UTF8_ENCODING: Final[str] = "utf-8"
_TIME_LOG_FORMAT: Final[str] = "%H:%M:%S"


def resolve_shared_settings(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import resolve_shared_settings as _factory

    return _factory(*args, **kwargs)


def build_sync_channel_use_case(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_sync_channel_use_case as _factory

    return _factory(*args, **kwargs)


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
            min=_MIN_POLL_INTERVAL_SECONDS,
            help="Polling interval in seconds between feed checks (default: 300)",
        ),
    ] = DEFAULT_WORKER_POLL_INTERVAL_SECONDS,
    lookback: Annotated[
        int,
        typer.Option(
            "--lookback",
            min=_MIN_LOOKBACK_DAYS,
            help="Days lookback window for new uploads per polling cycle (default: 7)",
        ),
    ] = DEFAULT_WORKER_LOOKBACK_DAYS,
    max_videos: Annotated[
        int,
        typer.Option(
            "--max-videos",
            min=_MIN_MAX_VIDEOS,
            help="Maximum videos per cycle (default: 10)",
        ),
    ] = DEFAULT_WORKER_MAX_VIDEOS,
    once: Annotated[
        bool,
        typer.Option(
            "--once",
            help="Execute exactly one polling cycle and terminate cleanly",
        ),
    ] = False,
) -> None:
    """Run continuous polling worker daemon with heartbeat health reporting."""
    code = handle_worker(
        channel=channel,
        poll_interval=poll_interval,
        lookback=lookback,
        max_videos=max_videos,
        once=once,
    )
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_worker(
    channel: str = "",
    poll_interval: int = DEFAULT_WORKER_POLL_INTERVAL_SECONDS,
    lookback: int = DEFAULT_WORKER_LOOKBACK_DAYS,
    max_videos: int = DEFAULT_WORKER_MAX_VIDEOS,
    once: bool = False,
) -> int:
    """Run polling daemon for continuous channel monitoring.

    Args:
        channel: Target YouTube channel or playlist URL string.
        poll_interval: Polling interval in seconds.
        lookback: Days lookback window.
        max_videos: Maximum videos per cycle.
        once: Whether to execute single cycle and terminate.

    Returns:
        Process exit code integer.
    """
    try:
        settings = resolve_shared_settings()
        use_case = build_sync_channel_use_case(settings=settings)
        query = ChannelFeedQuery(
            channel_url=channel,
            lookback_days=lookback,
            max_videos=max_videos,
        )
        heartbeat_file = Path(tempfile.gettempdir()) / _HEARTBEAT_FILENAME

        sys.stdout.write(
            f"Starting ChannelPollingDaemon for '{channel}' (interval: {poll_interval}s)...\n"
        )

        while True:
            heartbeat_file.write_text(datetime.now(UTC).isoformat(), encoding=_UTF8_ENCODING)
            summary = use_case.execute(query=query)
            sys.stdout.write(
                f"[{datetime.now(UTC).strftime(_TIME_LOG_FORMAT)}] Polled {summary.channel_url}: "
                f"processed={summary.processed_count}, skipped={summary.skipped_count}, failed={summary.failed_count}\n"
            )
            use_case.pipeline.metrics_port.flush()

            if once:
                break

            time.sleep(poll_interval)

        return EXIT_SUCCESS
    except KeyboardInterrupt:
        sys.stdout.write("Worker terminated gracefully by signal.\n")
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Worker error: {exc}\n")
        return EXIT_INTERNAL_ERROR
