"""Command handler for cresmo run."""

from __future__ import annotations

import argparse
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
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_discover_batch_sources_use_case,
    build_pipeline,
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
    """Register 'run' subcommand parser with argument options."""
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
    run_parser.set_defaults(handler=handle_run)



def execute_single_video_run(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
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
                pipeline.concat_master.execute_for_channel(raw.channel_name)
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
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
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
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def execute_batch_run(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0
    total_items = 0

    total_str = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for idx, src in enumerate(sources, 1):
        total_items += 1
        item_prefix = f"[{idx}{total_str}]"
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

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
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
            sys.stderr.write(f"{item_prefix} [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"{item_prefix} [FAILED] {src.target}: {exc}\n")

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
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
                f"Master consolidation complete: {total_parts} master document(s) generated across {len(master_results)} channel(s).\n"
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
    stream: bool = False,
) -> list[BatchSource] | Iterator[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
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
    if stream:
        return discovery_use_case.execute_stream(query=query)
    return discovery_use_case.execute(query=query)


def load_batch_sources_stream(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase."""
    res = load_batch_sources(query, settings, media_ingestion_port, stream=True)
    if isinstance(res, list):
        return iter(res)
    return res


def handle_run(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )


        if args.url:
            return execute_single_video_run(pipeline, args)

        enable_crawl = (
            False
            if getattr(args, "no_crawl", False)
             else getattr(settings, "enable_channel_crawler", True)
        )

        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
            enable_channel_crawler=enable_crawl,
        )

        if args.dry_run:
            sources = load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
                stream=False,
            )
            if not sources:
                manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
                sys.stdout.write(
                    f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
                )
                return EXIT_SUCCESS
            return execute_batch_dry_run(pipeline, sources)

        sources = load_batch_sources(
            query=query,
            settings=settings,
            media_ingestion_port=pipeline.media_ingestion_port,
            stream=True,
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
