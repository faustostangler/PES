"""Command handler for cresmo run.

Orchestrates full knowledge synthesis for individual media items or prioritized
batch runs across playlists, priority texts, and channel upload feeds.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-007: Pipeline Template Method DRY
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - SPEC-001: Core Knowledge Synthesis Specifications
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
import gc
import sys
from collections.abc import Iterable, Iterator, Sized
from pathlib import Path

from pydantic import ValidationError

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
)
from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import SyncFilterCriteria, is_processable_transcript_file
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_discover_batch_sources_use_case,
    build_pipeline,
    build_preflight_checker,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options.

    Args:
        subparsers: Root CLI subparsers action object.
    """
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
        default=3,
        help="Refinement passes for gap filler (default: 3)",
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
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.add_argument(
        "--no-crawl",
        action="store_true",
        default=False,
        help="Disable crawling channel feeds and strictly process manifest seed items",
    )
    run_parser.add_argument(
        "--web-index",
        action="store_true",
        default=False,
        help="Use Gemini API for raw transcript conceptual indexing instead of local Ollama",
    )
    # ADR-012: Multi-criteria filtering flags
    run_parser.add_argument(
        "--channel",
        dest="channels",
        nargs="*",
        default=None,
        metavar="CHANNEL",
        help=(
            "Filter batch discovery to one or more channel names, handles, or URLs. "
            "Accepts comma-separated values (e.g. --channel Ancapsu,Mises)."
        ),
    )
    run_parser.add_argument(
        "--category",
        "-c",
        dest="categories",
        nargs="*",
        default=None,
        metavar="CATEGORY",
        help=(
            "Filter batch discovery by domain category or volatility type. "
            "Domain names: politics_br, tech_ai, history, philosophy, finance, "
            "engineering, architecture, health, entertainment, geopolitics. "
            "Volatility: perennial, volatile. Accepts comma-separated values."
        ),
    )
    run_parser.add_argument(
        "--video",
        dest="video_ids",
        nargs="*",
        default=None,
        metavar="VIDEO_ID",
        help=(
            "Restrict batch discovery to specific video IDs or YouTube watch URLs. "
            "Accepts comma-separated values."
        ),
    )
    run_parser.set_defaults(handler=handle_run)


def execute_single_video_run(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
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
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel_name:
                pipeline.concat_master.execute(raw.channel_name)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def execute_batch_dry_run(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind == "file":
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content_id.value}] "
                    f"({len(raw_transcript.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def execute_batch_run(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    total_items = 0

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        total_items += 1
        item_prefix = f"[{source_index}/{total_count_suffix}]"
        result = None
        try:
            if source.kind == "file":
                target_path = Path(source.target)
                if not is_processable_transcript_file(target_path):
                    skipped += 1
                    sys.stdout.write(
                        f"{item_prefix} [SKIPPED] [{target_path.name}] "
                        "Ignored internal Cresmo artifact or system index.\n"
                    )
                    continue
                result = pipeline.run_for_text_file(
                    file_path=target_path,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=source.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = source.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                    "Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"{item_prefix} [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"{item_prefix} [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        finally:
            # Memory Hygiene & Telemetry Drainage per ADR-020
            try:
                pipeline.telemetry_port.flush()
            except Exception:  # noqa: BLE001, S110
                pass
            result = None
            gc.collect()

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    if completed > 0:
        try:
            sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
            master_results = pipeline.concat_master.execute_all()
            total_parts = sum(len(parts) for parts in master_results.values())
            sys.stdout.write(
                f"Master consolidation complete: {total_parts} master document(s) generated "
                f"across {len(master_results)} channel(s).\n"
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Optional application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def handle_run(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        if not getattr(args, "web_index", False):
            pipeline.warmup()

        if args.url:
            return execute_single_video_run(pipeline, args)

        enable_crawl = (
            False
            if getattr(args, "no_crawl", False)
            else getattr(settings, "enable_channel_crawler", True)
        )

        filter_criteria = SyncFilterCriteria.from_strings(
            channels=getattr(args, "channels", None) or [],
            categories=getattr(args, "categories", None) or [],
            video_ids=getattr(args, "video_ids", None) or [],
        )

        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
            enable_channel_crawler=enable_crawl,
            filter_criteria=filter_criteria,
            queue_maxsize=settings.discovery_queue_maxsize,
        )

        if args.dry_run:
            sources = list(
                load_batch_sources(
                    query=query,
                    settings=settings,
                    media_ingestion_port=pipeline.media_ingestion_port,
                )
            )
            if not sources:
                manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
                sys.stdout.write(
                    f"No sources found to process (manifest: {manifest_display}, "
                    f"raw lake scan: {not args.no_scan_raw}).\n"
                )
                return EXIT_SUCCESS
            return execute_batch_dry_run(pipeline, sources)

        # Generator que é o resultado do método execute do discovery_use_case, objeto da classe DiscoverBatchSourcesUseCase
        sources = load_batch_sources(
            query=query,
            settings=settings,
            media_ingestion_port=pipeline.media_ingestion_port,
        )
        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR
