"""Humble Object Command-Line Interface (CLI) Controller for Cresmo.

Translates CLI arguments and operating system process signals into application
pipeline invocations, mapping domain exceptions to standardized process exit codes.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import ChannelFeedQuery, PipelineStatus
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_pipeline,
    build_preflight_checker,
    build_sync_channel_use_case,
    build_unify_duplicates_use_case,
)

# Standardized Process Exit Codes (per ADR-002, ADR-003, and SPEC-003)
EXIT_SUCCESS: int = 0
EXIT_INTERNAL_ERROR: int = 1
EXIT_CONFIG_OR_USAGE_ERROR: int = 2
EXIT_DOMAIN_VALIDATION_ERROR: int = 3
EXIT_RATE_LIMIT_EXCEEDED: int = 4
EXIT_INGESTION_ERROR: int = 5


def _create_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: run
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video",
    )
    run_parser.add_argument(
        "--url",
        required=True,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=1,
        help="Refinement passes for gap filler (default: 1)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )

    # Subcommand: check-config
    subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )

    # Subcommand: sync
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
        default=7,
        help="Days lookback window for new uploads (default: 7)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=50,
        help="Maximum videos to discover and process in this run (default: 50)",
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

    # Subcommand: worker
    worker_parser = subparsers.add_parser(
        "worker",
        help="Run continuous polling worker daemon with heartbeat health reporting",
    )
    worker_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL to poll",
    )
    worker_parser.add_argument(
        "--poll-interval",
        type=int,
        default=300,
        help="Polling interval in seconds between cycles (default: 300)",
    )
    worker_parser.add_argument(
        "--lookback",
        type=int,
        default=7,
        help="Lookback window in days (default: 7)",
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

    # Subcommand: dedupe
    subparsers.add_parser(
        "dedupe",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint for Cresmo operations.

    Args:
        argv: Command-line arguments. If None, defaults to sys.argv[1:].

    Returns:
        Deterministic integer exit code matching the process exit taxonomy.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = _create_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    if not args.subcommand:
        parser.print_usage(file=sys.stderr)
        return EXIT_CONFIG_OR_USAGE_ERROR

    if args.subcommand == "check-config":
        try:
            settings = CresmoSettings()
            checker = build_preflight_checker(settings=settings)
            preflight = checker.check_all()
            if not preflight.is_healthy:
                sys.stderr.write("Preflight environmental checks failed:\n")
                for err in preflight.errors:
                    sys.stderr.write(f"- {err}\n")
                return EXIT_CONFIG_OR_USAGE_ERROR

            sys.stdout.write("Configuration and environment verified successfully:\n")
            sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
            sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
            sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
            sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
            return EXIT_SUCCESS
        except ValidationError as exc:
            sys.stderr.write(f"Configuration validation error:\n{exc}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR
        except PreflightError as exc:
            sys.stderr.write(f"Preflight error: {exc}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Unexpected configuration error: {exc}\n")
            return EXIT_INTERNAL_ERROR

    if args.subcommand == "sync":
        try:
            use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
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

    if args.subcommand == "worker":
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

    if args.subcommand == "dedupe":
        try:
            use_case = build_unify_duplicates_use_case()
            report = use_case.execute()
            sys.stdout.write("Vault Graph Deduplication Summary:\n")
            sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
            sys.stdout.write(
                f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n"
            )
            for cluster in report.clusters:
                merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
                sys.stdout.write(
                    f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                    f"({cluster.links_rewritten_count} links rewritten)\n"
                )
            return EXIT_SUCCESS
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Deduplication error: {exc}\n")
            return EXIT_INTERNAL_ERROR

    if args.subcommand == "run":
        try:
            if args.batch_size is not None:
                pipeline = build_pipeline(batch_size_override=args.batch_size)
            else:
                pipeline = build_pipeline()

            if args.dry_run:
                raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
                if raw is None:
                    sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
                    return EXIT_INGESTION_ERROR
                sys.stdout.write(
                    f"Dry run successful for [{raw.content_id.value}]: "
                    f"Transcript length: {len(raw.body)} characters.\n"
                )
                return EXIT_SUCCESS

            result = pipeline.run_for_video(
                video_url=args.url,
                gap_filler_passes=args.passes,
            )
            if result.success:
                sys.stdout.write(
                    f"Synthesis completed successfully for [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled.\n"
                )
                return EXIT_SUCCESS
            else:
                sys.stderr.write(f"Pipeline error: {result.error_message}\n")
                return EXIT_INTERNAL_ERROR

        except RateLimitExceededError as exc:
            sys.stderr.write(f"Rate limit exceeded: {exc}\n")
            return EXIT_RATE_LIMIT_EXCEEDED
        except IngestionNetworkError as exc:
            sys.stderr.write(f"Ingestion network error: {exc}\n")
            return EXIT_INGESTION_ERROR
        except (DomainValidationError, CresmoDomainError) as exc:
            sys.stderr.write(f"Domain validation error: {exc}\n")
            return EXIT_DOMAIN_VALIDATION_ERROR
        except ValidationError as exc:
            sys.stderr.write(f"Configuration error: {exc}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Unexpected internal error: {exc}\n")
            return EXIT_INTERNAL_ERROR

    return EXIT_CONFIG_OR_USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
