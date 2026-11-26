"""Humble Object CLI command handler for cresmo sync.

Parses Typer CLI options into SyncBatchRequest, delegates orchestration to
SyncBatchUseCase via bootstrap, and renders events and summary output.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-002 / SPEC-003 / SPEC-067: CLI Controller & Channel Sync Contracts
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any, Final

import typer

from cresmo.application.use_cases.sync_batch import (
    SyncBatchOutcome,
    SyncBatchRequest,
    SyncTargetEvent,
    SyncTargetEventKind,
)
from cresmo.presentation.error_handler import handle_cli_exception
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

_MIN_LOOKBACK_DAYS: Final[int] = 0
DEFAULT_SYNC_LOOKBACK_DAYS: Final[int] = 7 * 52 * 2
_MIN_MAX_VIDEOS: Final[int] = 1
DEFAULT_SYNC_MAX_VIDEOS: Final[int] = 250
_FALLBACK_SYNC_ERROR_PREFIX: Final[str] = "Unexpected sync error"


def build_sync_batch_use_case(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_sync_batch_use_case as _factory

    return _factory(*args, **kwargs)


def sync(
    channels: Annotated[
        list[str] | None,
        typer.Option(
            "--channel",
            help="One or more target YouTube channel names, handles, or URLs.",
        ),
    ] = None,
    categories: Annotated[
        list[str] | None,
        typer.Option(
            "--category",
            "-c",
            help="Filter by domain category or volatility type.",
        ),
    ] = None,
    video_ids: Annotated[
        list[str] | None,
        typer.Option(
            "--video",
            help="One or more video IDs or YouTube watch URLs to sync directly.",
        ),
    ] = None,
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            resolve_path=True,
            exists=True,
            help="Path to manifest text file (default: data/playlist.txt)",
        ),
    ] = None,
    lookback: Annotated[
        int,
        typer.Option(
            "--lookback",
            min=_MIN_LOOKBACK_DAYS,
            help="Days lookback window for new uploads",
        ),
    ] = DEFAULT_SYNC_LOOKBACK_DAYS,
    max_videos: Annotated[
        int,
        typer.Option(
            "--max-videos",
            min=_MIN_MAX_VIDEOS,
            help="Maximum videos to discover and process in this run (default: 250)",
        ),
    ] = DEFAULT_SYNC_MAX_VIDEOS,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Discover and filter feed without executing LLM synthesis or ledger updates",
        ),
    ] = False,
    force_refresh: Annotated[
        bool,
        typer.Option(
            "--force-refresh",
            help="Force re-synthesis even if content is already marked completed in ledger",
        ),
    ] = False,
) -> None:
    """Poll and synchronize video feeds from YouTube channels or playlists."""
    request = SyncBatchRequest(
        channels=tuple(channels or ()),
        categories=tuple(categories or ()),
        video_ids=tuple(video_ids or ()),
        manifest=manifest,
        lookback=lookback,
        max_videos=max_videos,
        dry_run=dry_run,
        force_refresh=force_refresh,
    )
    code = handle_sync(request)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def _render_sync_event(event: SyncTargetEvent) -> None:
    """Render per-target synchronization status to stdout."""
    if event.kind is SyncTargetEventKind.VIDEO:
        sys.stdout.write(
            f"[video] {event.target}: {event.processed} processed, "
            f"{event.skipped} skipped, {event.failed} failed\n"
        )
        return
    sys.stdout.write(
        f"[{event.target}] discovered={event.total_discovered} "
        f"processed={event.processed} "
        f"skipped={event.skipped} "
        f"failed={event.failed} "
        f"({event.duration_seconds:.1f}s)\n"
    )


def _render_sync_outcome(outcome: SyncBatchOutcome) -> int:
    """Render batch sync summary to stdout and return canonical exit code."""
    if outcome.no_matching_channels:
        sys.stdout.write(
            f"No channels found matching filter ({outcome.mode_description}). "
            f"Verify manifest at '{outcome.manifest_path}' and filter criteria.\n"
        )
        return EXIT_SUCCESS

    if not outcome.direct_video_mode:
        sys.stdout.write("\nChannel Synchronization Summary:\n")
        sys.stdout.write(f"- Channels synced: {outcome.channels_synced}\n")
        sys.stdout.write(f"- Total in Window: {outcome.total_discovered}\n")
        sys.stdout.write(f"- Processed: {outcome.total_processed}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {outcome.total_skipped}\n")
        sys.stdout.write(f"- Failed: {outcome.total_failed}\n")

    return EXIT_SUCCESS if outcome.success else EXIT_INTERNAL_ERROR


def handle_sync(request: SyncBatchRequest) -> int:
    """Delegate channel/video synchronization batch to SyncBatchUseCase."""
    try:
        use_case = build_sync_batch_use_case()
        outcome = use_case.execute(request, on_event=_render_sync_event)
        return _render_sync_outcome(outcome)
    except Exception as exc:  # noqa: BLE001
        return handle_cli_exception(exc, fallback_prefix=_FALLBACK_SYNC_ERROR_PREFIX)
