"""Command handler for cresmo run.

Orchestrates full knowledge synthesis for individual media items or prioritized
batch runs across playlists, priority texts, and channel upload feeds.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-007: Pipeline Template Method DRY
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - SPEC-001: Core Knowledge Synthesis Specifications
    - SPEC-002: CLI Controller & Exit Codes
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance
"""

from __future__ import annotations

import gc
import logging
import sys
from collections.abc import Iterable, Iterator, Sized
from pathlib import Path
from typing import Annotated, Any

import typer
from opentelemetry import trace
from pydantic import ValidationError

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
)
from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    BatchId,
    ChannelName,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.system import get_process_rss_bytes
from cresmo.presentation.composition import (
    build_concat_master_use_case,
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

logger = logging.getLogger(__name__)


def run(
    url: Annotated[
        str | None,
        typer.Option("--url", help="Target YouTube or media video URL"),
    ] = None,
    all_videos: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Run full pipeline for all videos in the manifest playlists",
        ),
    ] = True,
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
    passes: Annotated[
        int,
        typer.Option(
            "--passes",
            min=1,
            max=10,
            help="Refinement passes for text expansion (default: 5)",
        ),
    ] = 5,
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
            help="Ingest raw transcript without executing generative LLM synthesis",
        ),
    ] = False,
    force_reprocess: Annotated[
        bool,
        typer.Option(
            "--force-reprocess",
            help="Bypass ledger idempotency guard and re-synthesize even if already completed",
        ),
    ] = False,
    lookback: Annotated[
        int | None,
        typer.Option(
            "--lookback",
            min=0,
            help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
        ),
    ] = None,
    channel_max_videos: Annotated[
        int,
        typer.Option(
            "--channel-max-videos",
            min=1,
            help="Maximum candidate videos to inspect per channel feed (default: 50)",
        ),
    ] = 50,
    no_scan_raw: Annotated[
        bool,
        typer.Option(
            "--no-scan-raw",
            help="Skip scanning existing local markdown transcripts in data/raw/",
        ),
    ] = False,
    no_crawl: Annotated[
        bool,
        typer.Option(
            "--no-crawl",
            help="Disable crawling channel feeds and strictly process manifest seed items",
        ),
    ] = False,
    web_index: Annotated[
        bool,
        typer.Option(
            "--web-index",
            help="Use Gemini API for raw transcript conceptual indexing instead of local Ollama",
        ),
    ] = False,
    channels: Annotated[
        list[str] | None,
        typer.Option(
            "--channel",
            help="Filter batch discovery to one or more channel names, handles, or URLs.",
        ),
    ] = None,
    categories: Annotated[
        list[str] | None,
        typer.Option(
            "--category",
            "-c",
            help="Filter batch discovery by domain category or volatility type.",
        ),
    ] = None,
    video_ids: Annotated[
        list[str] | None,
        typer.Option(
            "--video",
            help="Restrict batch discovery to specific video IDs or YouTube watch URLs.",
        ),
    ] = None,
    device: Annotated[
        str | None,
        typer.Option(
            "--device",
            help="Inference device accelerator (auto, cuda, cpu, mps)",
        ),
    ] = None,
    concurrency: Annotated[
        int | None,
        typer.Option(
            "--concurrency",
            min=1,
            help="Concurrency limit for synthesis workers",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging output"),
    ] = False,
) -> None:
    """Run end-to-end knowledge synthesis for a video or manifest playlist."""
    _ = (all_videos, device, concurrency, verbose)

    class _Args:
        url: str | None
        manifest: Path | None
        passes: int
        batch_size: int | None
        dry_run: bool
        force_reprocess: bool
        lookback: int | None
        channel_max_videos: int
        no_scan_raw: bool
        no_crawl: bool
        web_index: bool
        channels: list[str] | None
        categories: list[str] | None
        video_ids: list[str] | None

    args = _Args()
    args.url = url
    args.manifest = manifest
    args.passes = passes
    args.batch_size = batch_size
    args.dry_run = dry_run
    args.force_reprocess = force_reprocess
    args.lookback = lookback
    args.channel_max_videos = channel_max_videos
    args.no_scan_raw = no_scan_raw
    args.no_crawl = no_crawl
    args.web_index = web_index
    args.channels = channels
    args.categories = categories
    args.video_ids = video_ids

    try:
        code = handle_run(args)
        if code != EXIT_SUCCESS:
            raise typer.Exit(code=code)
    except typer.Exit:
        raise
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        raise typer.Exit(code=EXIT_RATE_LIMIT_EXCEEDED) from exc
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        raise typer.Exit(code=EXIT_INGESTION_ERROR) from exc
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        raise typer.Exit(code=EXIT_CONFIG_OR_USAGE_ERROR) from exc
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        raise typer.Exit(code=EXIT_DOMAIN_VALIDATION_ERROR) from exc
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        raise typer.Exit(code=EXIT_CONFIG_OR_USAGE_ERROR) from exc
    except Exception as exc:
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        raise typer.Exit(code=EXIT_INTERNAL_ERROR) from exc


def handle_run(args: Any) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    tracer = trace.get_tracer("cresmo.cli")
    with tracer.start_as_current_span("cresmo.run"):
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

            return _execute_run_pipeline(args, settings, pipeline)
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


def _execute_run_pipeline(
    args: Any,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

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

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def execute_single_video_run(pipeline: CresmoPipeline, args: Any) -> int:
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
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
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


def execute_batch_run(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: Any,
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
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


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
        if source.kind is SourceModality.FILE:
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
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def _build_batch_discovery_query(
    args: Any,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
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

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def _process_single_batch_item(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: Any,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def _consolidate_master_if_needed(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def _drain_telemetry_and_memory(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)
