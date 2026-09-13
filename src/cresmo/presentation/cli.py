"""Humble Object Command-Line Interface (CLI) Controller for Cresmo.

Translates CLI arguments and operating system process signals into application
pipeline invocations, mapping domain exceptions to standardized process exit codes.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

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


def _read_manifest(path: Path) -> list[str]:
    """Read a manifest file and return non-empty, non-comment lines."""
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


@dataclass(frozen=True)
class BatchSource:
    """Represents a synthesis target: either a local text file or a remote media URL."""

    kind: Literal["file", "url"]
    target: str

    @property
    def display_name(self) -> str:
        if self.kind == "file":
            return Path(self.target).name
        return self.target


def _load_priority_text_files(priority_dir: Path) -> list[Path]:
    """Scan priority directory recursively for non-empty text and markdown transcripts."""
    if not priority_dir.is_dir():
        return []

    found: list[Path] = []
    # Support both .txt and .md transcripts across folder hierarchy
    for ext in ("*.txt", "*.md"):
        for path in sorted(priority_dir.rglob(ext)):
            if path.is_file() and path.stat().st_size > 0:
                found.append(path)
    return found


def _load_batch_sources(
    settings: CresmoSettings,
    *,
    explicit_manifest: Path | None = None,
) -> list[BatchSource]:
    """Build the ordered 3-tier source list for batch execution.

    When ``explicit_manifest`` is provided (user passed ``--manifest``), only
    that single file is used. Otherwise the 3-tier contract is:

    - Tier 0: Local priority text/markdown files in ``data/priority/`` (bypasses Stage 1 STT).
    - Tier 1: URLs from ``data/playlist-priority.txt`` (priority YouTube videos).
    - Tier 2: URLs from ``data/playlist.txt`` (main YouTube playlist), deduplicated
      against Tier 1.

    Returns:
        Ordered list of BatchSource items (Tier 0 -> Tier 1 -> Tier 2).
    """
    if explicit_manifest is not None:
        urls = _read_manifest(explicit_manifest)
        if urls:
            sys.stdout.write(
                f"[manifest] Loaded {len(urls)} URLs from {explicit_manifest.name}\n"
            )
        return [BatchSource(kind="url", target=u) for u in urls]

    sources: list[BatchSource] = []

    # Tier 0: Priority text/markdown files
    priority_files = _load_priority_text_files(settings.priority_texts_dir)
    if priority_files:
        sys.stdout.write(
            f"[manifest] Tier 0 (Priority Texts): {len(priority_files)} local files from {settings.priority_texts_dir.name}/\n"
        )
        for pf in priority_files:
            sources.append(BatchSource(kind="file", target=str(pf.resolve())))

    # Tier 1: Priority URLs
    priority_urls = _read_manifest(settings.playlist_priority_path)
    if priority_urls:
        sys.stdout.write(
            f"[manifest] Tier 1 (Priority URLs): {len(priority_urls)} URLs from {settings.playlist_priority_path.name}\n"
        )
        for pu in priority_urls:
            sources.append(BatchSource(kind="url", target=pu))

    # Tier 2: Main playlist URLs (deduplicated against Tier 1)
    main_urls = _read_manifest(settings.playlist_path)
    seen_urls: set[str] = set(priority_urls)
    remaining_urls = [u for u in main_urls if u not in seen_urls]

    if remaining_urls:
        sys.stdout.write(
            f"[manifest] Tier 2 (Main Playlist): {len(remaining_urls)} new URLs from {settings.playlist_path.name} "
            f"({len(main_urls) - len(remaining_urls)} duplicates skipped)\n"
        )
        for mu in remaining_urls:
            sources.append(BatchSource(kind="url", target=mu))

    return sources

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
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    # WHY: --all is kept as a no-op alias for backward compatibility with
    # existing scripts/docs, but batch mode is the default when no --url given.
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
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
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
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
    else:
        argv = list(argv)

    # Known subcommands
    known_subcommands = {"run", "check-config", "sync", "worker", "dedupe"}

    # If no arguments provided, or the first argument is an option/flag rather than
    # a known subcommand, default to inserting 'run' as the default subcommand.
    if not argv:
        argv = ["run"]
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-h", "--help")):
        argv = ["run", *argv]

    parser = _create_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    if not getattr(args, "subcommand", None):
        args.subcommand = "run"

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

            if args.url:
                if args.dry_run:
                    raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
                    if raw is None:
                        sys.stderr.write(
                            f"Dry-run ingestion returned no transcript for {args.url}\n"
                        )
                        return EXIT_INGESTION_ERROR
                    sys.stdout.write(
                        f"Dry run successful for [{raw.content_id.value}]: "
                        f"Transcript length: {len(raw.body)} characters.\n"
                    )
                    return EXIT_SUCCESS

                result = pipeline.run_for_video(
                    video_url=args.url,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
                if result.already_processed:
                    sys.stdout.write(
                        f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
                        f"in the ledger. Use --force-reprocess to bypass.\n"
                    )
                    return EXIT_SUCCESS
                if result.success:
                    sys.stdout.write(
                        f"Synthesis completed successfully for [{result.content_id.value}]: "
                        f"{len(result.synthesized_notes)} atomic notes synthesized, "
                        f"{len(result.reconciled_mocs)} MOCs reconciled, "
                        f"{result.duplicates_unified} duplicate clusters unified.\n"
                    )
                    return EXIT_SUCCESS
                else:
                    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
                    return EXIT_INTERNAL_ERROR

            # Batch execution over manifest playlist(s) and priority texts
            # WHY: Priority text files (Tier 0) are processed first, then priority
            # URLs (Tier 1), then main playlist (Tier 2). Deduplication prevents
            # re-processing URLs that appear in both manifest files.
            settings = CresmoSettings()
            sources = _load_batch_sources(settings, explicit_manifest=args.manifest)

            if not sources:
                sys.stdout.write("No synthesis targets found in manifests or priority folder.\n")
                return EXIT_SUCCESS

            sys.stdout.write(
                f"Starting batch execution for {len(sources)} items...\n"
            )

            if args.dry_run:
                ingested = 0
                for idx, src in enumerate(sources, 1):
                    if src.kind == "file":
                        fpath = Path(src.target)
                        ingested += 1
                        sys.stdout.write(
                            f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] "
                            f"({fpath.stat().st_size} bytes)\n"
                        )
                    else:
                        raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
                        if raw is not None:
                            ingested += 1
                            sys.stdout.write(
                                f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                                f"({len(raw.body)} chars)\n"
                            )
                        else:
                            sys.stderr.write(
                                f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n"
                            )
                sys.stdout.write(
                    f"Dry-run completed: {ingested}/{len(sources)} items validated.\n"
                )
                return EXIT_SUCCESS

            completed = 0
            skipped = 0
            failed = 0

            for idx, src in enumerate(sources, 1):
                try:
                    if src.kind == "file":
                        result = pipeline.run_for_text_file(
                            file_path=Path(src.target),
                            gap_filler_passes=args.passes,
                            force_reprocess=args.force_reprocess,
                        )
                    else:
                        result = pipeline.run_for_video(
                            video_url=src.target,
                            gap_filler_passes=args.passes,
                            force_reprocess=args.force_reprocess,
                        )

                    if result.already_processed:
                        skipped += 1
                        sys.stdout.write(
                            f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                        )
                    elif result.success:
                        completed += 1
                        sys.stdout.write(
                            f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                            f"{len(result.synthesized_notes)} atomic notes synthesized, "
                            f"{len(result.reconciled_mocs)} MOCs reconciled, "
                            f"{result.duplicates_unified} duplicate clusters unified.\n"
                        )
                    else:
                        failed += 1
                        sys.stderr.write(
                            f"[{idx}/{len(sources)}] [ERROR] {src.display_name}: {result.error_message}\n"
                        )
                except RateLimitExceededError as exc:
                    failed += 1
                    sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.display_name}: {exc}\n")
                except IngestionNetworkError as exc:
                    failed += 1
                    sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.display_name}: {exc}\n")
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.display_name}: {exc}\n")

            sys.stdout.write(
                f"\nBatch Synthesis Summary:\n"
                f"- Total Items: {len(sources)}\n"
                f"- Completed: {completed}\n"
                f"- Skipped (Idempotent): {skipped}\n"
                f"- Failed: {failed}\n"
            )
            return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


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
