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

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

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
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_sync_channel_use_case
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options.

    Supports three targeting modes (ADR-012):
    - Single channel: ``cresmo sync --channel <url>``
    - Category filter: ``cresmo sync --category politics_br,tech_ai``
    - Video filter:    ``cresmo sync --video <id_or_url>``
    - Default (no flags): full manifest sync from data/playlist.txt

    Args:
        subparsers: Root CLI subparsers action object.
    """
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from YouTube channels or playlists",
    )
    sync_parser.add_argument(
        "--channel",
        dest="channels",
        nargs="*",
        default=None,
        metavar="CHANNEL",
        help=(
            "One or more target YouTube channel names, handles (@ancapsu), or URLs. "
            "Accepts comma-separated values or multiple flags. "
            "When omitted, all channels in the manifest are synced."
        ),
    )
    sync_parser.add_argument(
        "--category",
        "-c",
        dest="categories",
        nargs="*",
        default=None,
        metavar="CATEGORY",
        help=(
            "Filter by domain category or volatility type. "
            "Domain categories: politics_br, tech_ai, history, philosophy, finance, "
            "engineering, architecture, health, entertainment, geopolitics. "
            "Volatility types: perennial, volatile. "
            "Accepts comma-separated values (e.g. --category politics_br,tech_ai)."
        ),
    )
    sync_parser.add_argument(
        "--video",
        dest="video_ids",
        nargs="*",
        default=None,
        metavar="VIDEO_ID",
        help=(
            "One or more video IDs or YouTube watch URLs to sync directly. "
            "Accepts comma-separated values. When specified, skips channel feed crawling."
        ),
    )
    sync_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        dest="manifest",
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def _build_filter_criteria(args: argparse.Namespace) -> SyncFilterCriteria:
    """Parse CLI argument namespace into a SyncFilterCriteria Value Object.

    Accepts comma-separated values within each flag (e.g. ``--channel Ancapsu,Mises``).

    ADR-012: Empty criteria triggers default full-pipeline flow.
    """
    return SyncFilterCriteria.from_strings(
        channels=args.channels or [],
        categories=args.categories or [],
        video_ids=args.video_ids or [],
    )


def handle_sync(args: argparse.Namespace) -> int:
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
        settings = CresmoSettings()
        settings.ensure_directories()
        filter_criteria = _build_filter_criteria(args)

        use_case = build_sync_channel_use_case(
            settings=settings,
            batch_size_override=args.batch_size,
        )

        # --- Mode 1: Single/multi-video direct sync ---
        if filter_criteria.video_ids:
            total_processed = 0
            total_failed = 0
            for video_ref in filter_criteria.video_ids:
                target_url = (
                    video_ref
                    if video_ref.startswith(("http://", "https://"))
                    else f"https://www.youtube.com/watch?v={video_ref}"
                )
                query = ChannelFeedQuery(
                    channel_url=target_url,
                    lookback_days=args.lookback,
                    max_videos=1,
                )
                summary = use_case.execute(
                    query=query,
                    dry_run=args.dry_run,
                    force_refresh=args.force_refresh,
                )
                total_processed += summary.processed_count
                total_failed += summary.failed_count
                sys.stdout.write(
                    f"[video] {video_ref}: {summary.processed_count} processed, "
                    f"{summary.skipped_count} skipped, {summary.failed_count} failed\n"
                )
            return EXIT_SUCCESS if total_failed == 0 else EXIT_INTERNAL_ERROR

        # --- Mode 2 / 3 / 4: Channel/category/manifest sync ---
        # Resolve the manifest: explicit flag → default data/playlist.txt
        manifest_path = args.manifest or settings.playlist_path

        # Collect target channel URLs
        channels_to_sync = _resolve_channels_for_sync(
            manifest_path=manifest_path,
            filter_criteria=filter_criteria,
            settings=settings,
            lookback=args.lookback,
            max_videos=args.max_videos,
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

        total_discovered = 0
        total_processed = 0
        total_skipped = 0
        total_failed = 0

        for ch_url in channels_to_sync:
            query = ChannelFeedQuery(
                channel_url=ch_url,
                lookback_days=args.lookback,
                max_videos=args.max_videos,
            )
            summary = use_case.execute(
                query=query,
                dry_run=args.dry_run,
                force_refresh=args.force_refresh,
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
    settings: CresmoSettings,
    lookback: int,
    max_videos: int,
) -> list[str]:
    """Collect channel URLs from manifest applying filter_criteria.

    When filter_criteria.channels is non-empty, each token is treated as a direct
    channel reference (name, handle, or URL).  When filter_criteria.categories is
    non-empty, every manifest entry is evaluated against the domain taxonomy.
    When no criteria are set, all manifest channels are returned.

    ADR-012: Returned list is **not** yet sorted; the caller enforces alphabetical order.
    """
    from cresmo.domain.value_objects import normalize_to_uploads_playlist_url

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
