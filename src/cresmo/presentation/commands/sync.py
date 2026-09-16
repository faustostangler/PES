"""Command handler for cresmo sync."""

from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import ChannelFeedQuery, PipelineStatus
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
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
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


def handle_sync(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        settings = CresmoSettings()
        use_case = build_sync_channel_use_case(
            settings=settings,
            batch_size_override=args.batch_size,
        )
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
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
