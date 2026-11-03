"""Command handler for cresmo sync.

Polls and synchronizes video feeds from YouTube channels or playlists with lookback
filtering and idempotent ledger tracking per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-003: PES Production Architecture & Telemetry
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-003: Channel Synchronization Specifications
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

import typer
from pydantic import ValidationError

if TYPE_CHECKING:
    from cresmo.application.use_cases.sync_channel import SyncChannelUseCase

from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    SyncFilterCriteria,
    normalize_to_uploads_playlist_url,
)
from cresmo.presentation.composition import (
    build_sync_channel_use_case,
    resolve_shared_settings,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


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
            "--playlist",
            resolve_path=True,
            exists=True,
            help="Path to manifest or playlist text file (default: data/playlist.txt)",
        ),
    ] = None,
    lookback: Annotated[
        int,
        typer.Option(
            "--lookback",
            min=0,
            help="Days lookback window for new uploads",
        ),
    ] = 7 * 52 * 2,
    max_videos: Annotated[
        int,
        typer.Option(
            "--max-videos",
            min=1,
            help="Maximum videos to discover and process in this run (default: 250)",
        ),
    ] = 250,
    batch_size: Annotated[
        int | None,
        typer.Option(
            "--batch-size",
            min=1,
            help="Batch size override for atomic note synthesis",
        ),
    ] = None,
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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Poll and synchronize video feeds from YouTube channels or playlists."""
    _ = verbose

    class _Args:
        channels: list[str] | None
        categories: list[str] | None
        video_ids: list[str] | None
        manifest: Path | None
        lookback: int
        max_videos: int
        batch_size: int | None
        dry_run: bool
        force_refresh: bool

    args = _Args()
    args.channels = channels
    args.categories = categories
    args.video_ids = video_ids
    args.manifest = manifest
    args.lookback = lookback
    args.max_videos = max_videos
    args.batch_size = batch_size
    args.dry_run = dry_run
    args.force_refresh = force_refresh

    code = handle_sync(args)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def _build_filter_criteria(args: Any) -> SyncFilterCriteria:
    """Parse CLI argument namespace into a SyncFilterCriteria Value Object.

    Accepts comma-separated values within each flag (e.g. ``--channel Ancapsu,Mises``).

    ADR-012: Empty criteria triggers default full-pipeline flow.
    """
    return SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )


def _sync_direct_videos(
    use_case: SyncChannelUseCase,
    video_ids: Sequence[str] | set[str],
    args: Any,
) -> int:
    """Synchronize a collection of videos directly by identifier."""
    total_processed = 0
    total_failed = 0
    for video_ref in video_ids:
        target_url = (
            video_ref
            if video_ref.startswith(("http://", "https://"))
            else f"https://www.youtube.com/watch?v={video_ref}"
        )
        query = ChannelFeedQuery(
            channel_url=target_url,
            lookback_days=getattr(args, "lookback", 7 * 52 * 2),
            max_videos=1,
        )
        summary = use_case.execute(
            query=query,
            dry_run=getattr(args, "dry_run", False),
            force_refresh=getattr(args, "force_refresh", False),
        )
        total_processed += summary.processed_count
        total_failed += summary.failed_count
        sys.stdout.write(
            f"[video] {video_ref}: {summary.processed_count} processed, "
            f"{summary.skipped_count} skipped, {summary.failed_count} failed\n"
        )
    return EXIT_SUCCESS if total_failed == 0 else EXIT_INTERNAL_ERROR


def _sync_channel_list(
    use_case: SyncChannelUseCase,
    channels_to_sync: list[str],
    args: Any,
) -> int:
    """Synchronize a list of channel feeds and render summary table."""
    total_discovered = 0
    total_processed = 0
    total_skipped = 0
    total_failed = 0

    for ch_url in channels_to_sync:
        query = ChannelFeedQuery(
            channel_url=ch_url,
            lookback_days=getattr(args, "lookback", 7 * 52 * 2),
            max_videos=getattr(args, "max_videos", 250),
        )
        summary = use_case.execute(
            query=query,
            dry_run=getattr(args, "dry_run", False),
            force_refresh=getattr(args, "force_refresh", False),
        )
        total_discovered += summary.total_discovered
        total_processed += summary.processed_count
        total_skipped += summary.skipped_count
        total_failed += summary.failed_count
        sys.stdout.write(
            f"[{ch_url}] discovered={summary.total_discovered} "
            f"processed={summary.processed_count} "
            f"skipped={summary.skipped_count} "
            f"failed={summary.failed_count} "
            f"({summary.duration_seconds:.1f}s)\n"
        )

    sys.stdout.write("\nChannel Synchronization Summary:\n")
    sys.stdout.write(f"- Channels synced: {len(channels_to_sync)}\n")
    sys.stdout.write(f"- Total in Window: {total_discovered}\n")
    sys.stdout.write(f"- Processed: {total_processed}\n")
    sys.stdout.write(f"- Skipped (Idempotent): {total_skipped}\n")
    sys.stdout.write(f"- Failed: {total_failed}\n")

    return EXIT_SUCCESS if total_failed == 0 else EXIT_INTERNAL_ERROR


def handle_sync(args: Any) -> int:
    """Synchronize recent video uploads from one or more YouTube channel feeds.

    Execution modes (ADR-012):
    1. ``--video <id>``     → direct single/multi-video sync, bypasses channel discovery.
    2. ``--channel <name>`` → filtered channel sync (alphabetical order).
    3. ``--category <cat>`` → category-scoped manifest sync.
    4. (no flags)           → full manifest sync from data/playlist.txt (default).

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = resolve_shared_settings()
        settings.ensure_directories()
        filter_criteria = _build_filter_criteria(args)

        use_case = build_sync_channel_use_case(
            settings=settings,
            batch_size_override=args.batch_size,
        )

        # --- Mode 1: Single/multi-video direct sync ---
        if filter_criteria.video_ids:
            return _sync_direct_videos(use_case, filter_criteria.video_ids, args)

        # --- Mode 2 / 3 / 4: Channel/category/manifest sync ---
        # Resolve the manifest: explicit flag → default data/playlist.txt
        manifest_path = args.manifest or settings.playlist_path

        # Collect target channel URLs
        channels_to_sync = _resolve_channels_for_sync(
            manifest_path=manifest_path,
            filter_criteria=filter_criteria,
        )

        if not channels_to_sync:
            mode_description = _describe_mode(filter_criteria)
            sys.stdout.write(
                f"No channels found matching filter ({mode_description}). "
                f"Verify manifest at '{manifest_path}' and filter criteria.\n"
            )
            return EXIT_SUCCESS

        # ADR-012: process channels in strict alphabetical order
        channels_to_sync = sorted(channels_to_sync, key=str.lower)
        return _sync_channel_list(use_case, channels_to_sync, args)

    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


# ---------------------------------------------------------------------------
# Helpers (private – presentation layer only)
# ---------------------------------------------------------------------------


def _describe_mode(criteria: SyncFilterCriteria) -> str:
    """Return a human-readable description of the active filter mode for CLI output."""
    parts: list[str] = []
    if criteria.channels:
        parts.append(f"channels={','.join(criteria.channels)}")
    if criteria.categories:
        parts.append(f"categories={','.join(criteria.categories)}")
    if criteria.video_ids:
        parts.append(f"videos={','.join(criteria.video_ids)}")
    return ", ".join(parts) if parts else "full manifest"


def _read_manifest_lines(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def _resolve_channels_for_sync(
    manifest_path: Path | None,
    filter_criteria: SyncFilterCriteria,
) -> list[str]:
    """Collect channel URLs from manifest applying filter_criteria.

    When filter_criteria.channels is non-empty, each token is treated as a direct
    channel reference (name, handle, or URL).  When filter_criteria.categories is
    non-empty, every manifest entry is evaluated against the domain taxonomy.
    When no criteria are set, all manifest channels are returned.

    ADR-012: Returned list is **not** yet sorted; the caller enforces alphabetical order.
    """
    # Mode: explicit --channel tokens are treated as direct target URLs/handles
    if filter_criteria.channels:
        return [
            ch if ch.startswith(("http://", "https://")) else normalize_to_uploads_playlist_url(ch)
            for ch in filter_criteria.channels
        ]

    # Mode: category or full manifest — read from manifest and filter
    lines = _read_manifest_lines(manifest_path)
    channels: list[str] = []
    for line in lines:
        norm = normalize_to_uploads_playlist_url(line)
        if filter_criteria.is_empty() or filter_criteria.matches_category(channel_url=line):
            channels.append(norm)
    return channels
