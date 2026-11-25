"""Humble Object CLI command handler for cresmo run.

Parses Typer CLI flags into RunSynthesisRequest, delegates orchestration to
RunSynthesisUseCase via bootstrap, and renders events/outcomes to terminal streams.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-010: Zero Legacy Shims & Streaming-First Unification
    - ADR-053 / ADR-067: Lazy Presentation CLI & Run/Sync Use Cases
    - SPEC-002 / SPEC-067: CLI Controller & Exit Codes
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from cresmo.application.use_cases.run_synthesis import (
    BatchItemEvent,
    BatchItemEventKind,
    RunExitStatus,
    RunSynthesisOutcome,
    RunSynthesisRequest,
)
from cresmo.bootstrap.composition import build_run_synthesis_use_case
from cresmo.presentation.error_handler import handle_cli_exception
from cresmo.presentation.exit_codes import (
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)

_STATUS_TO_EXIT_CODE: dict[RunExitStatus, int] = {
    RunExitStatus.SUCCESS: EXIT_SUCCESS,
    RunExitStatus.RATE_LIMITED: EXIT_RATE_LIMIT_EXCEEDED,
    RunExitStatus.INGESTION_ERROR: EXIT_INGESTION_ERROR,
    RunExitStatus.INTERNAL_ERROR: EXIT_INTERNAL_ERROR,
}

_STDERR_EVENT_KINDS: frozenset[BatchItemEventKind] = frozenset(
    {
        BatchItemEventKind.DRY_RUN_FAILED,
        BatchItemEventKind.ITEM_RATE_LIMITED,
        BatchItemEventKind.ITEM_NETWORK_ERROR,
        BatchItemEventKind.ITEM_FAILED,
        BatchItemEventKind.QUOTA_ABORT,
        BatchItemEventKind.MASTER_WARNING,
    }
)


def run(
    url: Annotated[
        str | None,
        typer.Option("--url", help="Target YouTube or media video URL"),
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
    passes: Annotated[
        int | None,
        typer.Option(
            "--passes",
            min=1,
            max=10,
            help="Refinement passes override for expansion stages (default: configured per-stage)",
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
    scan_raw: Annotated[
        bool,
        typer.Option(
            "--scan-raw",
            help="Scan local raw transcript lake for unprocessed files (default: False)",
        ),
    ] = False,
    crawl: Annotated[
        bool,
        typer.Option(
            "--crawl",
            help="Enable crawling remote channel feeds for new uploads (default: False for fast execution)",
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
) -> None:
    """Run end-to-end knowledge synthesis for a video or manifest playlist."""
    request = RunSynthesisRequest(
        url=url,
        manifest=manifest,
        passes=passes,
        dry_run=dry_run,
        force_reprocess=force_reprocess,
        lookback=lookback,
        channel_max_videos=channel_max_videos,
        scan_raw=scan_raw,
        crawl=crawl,
        web_index=web_index,
        channels=tuple(channels or ()),
        categories=tuple(categories or ()),
        video_ids=tuple(video_ids or ()),
    )
    code = handle_run(request)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def _render_event(event: BatchItemEvent) -> None:
    """Render structured synthesis progress events to stdout or stderr."""
    if event.kind is BatchItemEventKind.DISCOVERY_PROGRESS:
        sys.stdout.write(event.message)
    elif event.kind is BatchItemEventKind.MASTER_CONSOLIDATED:
        sys.stdout.write(f"\nConsolidating master compendiums for RAG...\n{event.message}\n")
    elif event.kind in _STDERR_EVENT_KINDS:
        sys.stderr.write(f"{event.message}\n")
    else:
        sys.stdout.write(f"{event.message}\n")


def _render_outcome(outcome: RunSynthesisOutcome) -> int:
    """Render terminal synthesis summary and return canonical exit code."""
    if outcome.mode == "single":
        if outcome.dry_run:
            if outcome.status is RunExitStatus.INGESTION_ERROR:
                sys.stderr.write(
                    f"Dry-run ingestion returned no transcript for {outcome.single_dry_run_url}\n"
                )
            else:
                sys.stdout.write(
                    f"Dry run successful for [{outcome.single_content_id}]: "
                    f"Transcript length: {outcome.single_dry_run_chars} characters.\n"
                )
        elif outcome.skipped > 0:
            sys.stdout.write(
                f"[SKIPPED] Content [{outcome.single_content_id}] was already marked as COMPLETED "
                "in the ledger. Use --force-reprocess to bypass.\n"
            )
        else:
            stages_label = ", ".join(outcome.single_stages_completed) or "none"
            sys.stdout.write(
                f"Synthesis completed successfully for [{outcome.single_content_id}]: "
                f"{len(outcome.single_stages_completed)} stage(s) completed ({stages_label}), "
                f"{outcome.single_final_chars} chars.\n"
            )
        return _STATUS_TO_EXIT_CODE[outcome.status]

    if outcome.empty_sources:
        sys.stdout.write(
            f"No sources found to process (manifest: {outcome.manifest_display}, "
            f"raw lake scan: {outcome.scan_raw}).\n"
        )
        return _STATUS_TO_EXIT_CODE[outcome.status]

    if outcome.dry_run:
        sys.stdout.write(
            f"Dry-run completed: {outcome.dry_run_validated}/{outcome.dry_run_total} "
            "items validated.\n"
        )
        return _STATUS_TO_EXIT_CODE[outcome.status]

    batch_label = outcome.batch_id.value if outcome.batch_id is not None else "unknown"
    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_label}]:\n"
        f"- Total Items: {outcome.total_items}\n"
        f"- Completed: {outcome.completed}\n"
        f"- Skipped (Idempotent): {outcome.skipped}\n"
        f"- Failed: {outcome.failed}\n"
    )
    return _STATUS_TO_EXIT_CODE[outcome.status]


def handle_run(request: RunSynthesisRequest) -> int:
    """Delegate knowledge synthesis execution to RunSynthesisUseCase."""
    try:
        use_case = build_run_synthesis_use_case(
            lookback_override=request.lookback,
            web_index=request.web_index,
            check_ffmpeg=True,
        )
        outcome = use_case.execute(request, on_event=_render_event)
        return _render_outcome(outcome)
    except Exception as exc:  # noqa: BLE001
        return handle_cli_exception(exc)
