"""Humble Object Command-Line Interface (CLI) Controller for Cresmo.

Translates CLI arguments and operating system process signals into application
pipeline invocations, mapping domain exceptions to standardized process exit codes.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from cresmo.application.ports import MediaIngestionPort
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

_VIDEO_ID_REGEX = re.compile(r"(?:v=|\/)([a-zA-Z0-9_-]{8,64})(?:[&?]|\Z)")
_CHANNEL_ID_FRONTMATTER_REGEX = re.compile(r"^\s*channel_id:\s*([A-Za-z0-9_-]+)", re.MULTILINE)
_VIDEO_ID_FRONTMATTER_REGEX = re.compile(r"^\s*video_id:\s*([A-Za-z0-9_-]+)", re.MULTILINE)



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


def _load_transcript_files(base_dir: Path) -> list[Path]:
    """Discover all non-temporary transcript files (.txt, .md) in a directory tree."""
    if not base_dir.is_dir():
        return []
    files: list[Path] = []
    for ext in ("*.txt", "*.md"):
        for f in base_dir.rglob(ext):
            if f.is_file() and not f.name.startswith(".tmp."):
                files.append(f)
    return sorted(files)


def _extract_raw_file_metadata(file_path: Path) -> tuple[str | None, str | None]:
    """Extract video_id and canonical channel_url from raw transcript frontmatter."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(30)]
            header = "".join(lines)

            vm = _VIDEO_ID_FRONTMATTER_REGEX.search(header)
            vid = vm.group(1) if vm else file_path.stem

            cm = _CHANNEL_ID_FRONTMATTER_REGEX.search(header)
            chan_url = f"https://www.youtube.com/channel/{cm.group(1)}" if cm else None
            return vid, chan_url
    except Exception:  # noqa: BLE001
        return None, None



def _is_channel_or_playlist_feed(url: str) -> bool:
    """Determine if a URL targets a channel feed or playlist rather than a single video."""
    url_lower = url.lower()
    return any(
        pattern in url_lower
        for pattern in (
            "/@",
            "/channel/",
            "/c/",
            "/user/",
            "/playlist",
            "list=",
            "/videos",
        )
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def _load_batch_sources(
    settings: CresmoSettings,
    *,
    explicit_manifest: Path | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
    lookback_days: int | None = None,
    channel_max_videos: int = 50,
    include_raw_lake: bool = True,
) -> list[BatchSource]:
    """Build the ordered tiered source list for batch execution.

    When ``explicit_manifest`` is provided (user passed ``--manifest``), only
    that single file is used. Otherwise the tiered streaming contract is:

    - Tier 0: Local priority text/markdown files in ``data/priority/`` (bypasses Stage 1 STT).
    - Tier 1: URLs from ``data/playlist-priority.txt`` (priority YouTube videos).
    - Tier 2: Existing raw transcripts in ``data/raw/`` lake (bypasses Stage 1 STT).
    - Tier 3: Direct video URLs from ``data/playlist.txt`` (main YouTube playlist).
    - Tier 4: Concurrent discovery of recent videos from channel/playlist feeds in ``data/playlist.txt``.

    Returns:
        Ordered list of BatchSource items (Tier 0 -> Tier 1 -> Tier 2 -> Tier 3 -> Tier 4).
    """
    if explicit_manifest is not None:
        urls = _read_manifest(explicit_manifest)
        if urls:
            sys.stdout.write(f"[manifest] Loaded {len(urls)} URLs from {explicit_manifest.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    sources: list[BatchSource] = []
    seen_vids: set[str] = set()

    def _register_video_id(target_str: str) -> None:
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            seen_vids.add(m.group(1))
        else:
            stem = Path(target_str).stem
            seen_vids.add(stem)

    # Tier 0: Priority text/markdown files
    priority_files = _load_transcript_files(settings.priority_texts_dir)
    if priority_files:
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            sources.append(BatchSource(kind="file", target=resolved_pf))
            _register_video_id(resolved_pf)

    # Tier 1: Priority URLs
    priority_urls = _read_manifest(settings.playlist_priority_path)
    if priority_urls:
        for pu in priority_urls:
            sources.append(BatchSource(kind="url", target=pu))
            _register_video_id(pu)

    # Tier 2: Existing raw transcripts in data/raw/ lake & local channel mapping
    local_video_to_channel: dict[str, str] = {}
    if hasattr(settings, "raw_dir") and settings.raw_dir.is_dir():
        raw_files = _load_transcript_files(settings.raw_dir)
        for rf in raw_files:
            stem = rf.stem
            vid_front, chan_url = _extract_raw_file_metadata(rf)
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if include_raw_lake and stem not in seen_vids and canonical_vid not in seen_vids:
                resolved_rf = str(rf.resolve())
                sources.append(BatchSource(kind="file", target=resolved_rf))
                seen_vids.add(stem)
                seen_vids.add(canonical_vid)

    # Tier 3 & 4: Main playlist entries (split direct videos vs channel feeds)
    main_urls = _read_manifest(settings.playlist_path)
    direct_video_urls: list[str] = []
    channel_feed_urls: list[str] = []
    all_playlist_video_urls: list[str] = []

    for mu in main_urls:
        m = _VIDEO_ID_REGEX.search(mu)
        vid = m.group(1) if m else None
        if _is_channel_or_playlist_feed(mu):
            channel_feed_urls.append(mu)
        else:
            all_playlist_video_urls.append(mu)
            if not (vid and vid in seen_vids):
                direct_video_urls.append(mu)
                if vid:
                    seen_vids.add(vid)

    # Append direct video URLs (Tier 3)
    for u in direct_video_urls:
        sources.append(BatchSource(kind="url", target=u))

    # Tier 4: Concurrent discovery of channel feeds (explicit + discovered by videos)
    effective_lookback = lookback_days if lookback_days is not None else settings.days_lookback
    if media_ingestion_port is not None and (channel_feed_urls or all_playlist_video_urls):
        workers = getattr(settings, "channel_discovery_workers", 10)
        cutoff = datetime.now(UTC) - timedelta(days=effective_lookback)

        def _discover_single(chan_url: str) -> list[str]:
            q = ChannelFeedQuery(
                channel_url=chan_url,
                lookback_days=effective_lookback,
                max_videos=channel_max_videos,
            )
            try:
                discovered = media_ingestion_port.discover_channel_feed(q)
                in_window: list[str] = []
                for item in discovered:
                    pub = item.published_at
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub >= cutoff:
                        in_window.append(item.media_url)
                return in_window
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
                return []

        probed_channels: set[str] = set()
        channels_to_probe: list[str] = []

        # 1. Enqueue explicit channel feeds
        for c_url in channel_feed_urls:
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        # 2. Identify parent channel for each video URL
        videos_needing_remote_lookup: list[str] = []
        for v_url in all_playlist_video_urls:
            m = _VIDEO_ID_REGEX.search(v_url)
            vid = m.group(1) if m else None
            local_chan = local_video_to_channel.get(vid) if vid else None
            if local_chan:
                if local_chan not in probed_channels:
                    probed_channels.add(local_chan)
                    channels_to_probe.append(local_chan)
            else:
                videos_needing_remote_lookup.append(v_url)


        # 3. Concurrently resolve channels for videos without local raw metadata
        if videos_needing_remote_lookup:
            sys.stdout.write(
                f"[crawler] Resolving parent channels for {len(videos_needing_remote_lookup)} seed videos...\n"
            )
            max_res_workers = max(1, min(workers, len(videos_needing_remote_lookup)))
            with ThreadPoolExecutor(max_workers=max_res_workers) as res_executor:
                future_to_vurl = {
                    res_executor.submit(media_ingestion_port.extract_channel_url_from_video, vu): vu
                    for vu in videos_needing_remote_lookup
                }
                for fut in as_completed(future_to_vurl):
                    try:
                        resolved_chan = fut.result()
                        if resolved_chan and resolved_chan not in probed_channels:
                            probed_channels.add(resolved_chan)
                            channels_to_probe.append(resolved_chan)
                    except Exception as exc:  # noqa: BLE001
                        failed_vu = future_to_vurl[fut]
                        sys.stderr.write(
                            f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                        )

        # 4. Concurrently probe all unique channels for recent uploads
        if channels_to_probe:
            sys.stdout.write(
                f"[crawler] Discovering recent videos across {len(channels_to_probe)} channels "
                f"(lookback: {effective_lookback}d, workers: {workers})...\n"
            )
            max_probe_workers = max(1, min(workers, len(channels_to_probe)))
            with ThreadPoolExecutor(max_workers=max_probe_workers) as executor:
                future_to_url = {executor.submit(_discover_single, u): u for u in channels_to_probe}
                for future in as_completed(future_to_url):
                    discovered_urls = future.result()
                    for d_url in discovered_urls:
                        m = _VIDEO_ID_REGEX.search(d_url)
                        vid = m.group(1) if m else d_url
                        if vid not in seen_vids:
                            seen_vids.add(vid)
                            sources.append(BatchSource(kind="url", target=d_url))

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
            lf_pk = getattr(settings, "langfuse_public_key", "")
            lf_sk = getattr(settings, "langfuse_secret_key", None)
            lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
            if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
                pk_masked = lf_pk[:10] + "..."
                sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
            else:
                sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
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
            # If any tier is missing or empty, it gracefully falls through to the next.
            settings = CresmoSettings()
            if args.lookback is not None:
                settings.days_lookback = args.lookback

            settings.ensure_directories()
            sources = _load_batch_sources(
                settings,
                explicit_manifest=args.manifest,
                media_ingestion_port=pipeline.media_ingestion_port,
                lookback_days=settings.days_lookback,
                channel_max_videos=args.channel_max_videos,
                include_raw_lake=not args.no_scan_raw,
            )


            if not sources:
                sys.stdout.write(
                    "No synthesis targets found in manifests or priority folder.\n"
                    "\nBatch Synthesis Summary:\n"
                    "- Total Items: 0\n"
                    "- Completed: 0\n"
                    "- Skipped (Idempotent): 0\n"
                    "- Failed: 0\n"
                )
                return EXIT_SUCCESS

            lf_pk = getattr(settings, "langfuse_public_key", "")
            lf_sk = getattr(settings, "langfuse_secret_key", None)
            lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
            if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
                sys.stdout.write(f"Langfuse telemetry active: {lf_host}\n")
            sys.stdout.write(f"Starting batch execution for {len(sources)} items...\n")

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
                sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
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
                    sys.stderr.write(
                        f"[{idx}/{len(sources)}] [RATE LIMIT] {src.display_name}: {exc}\n"
                    )
                except IngestionNetworkError as exc:
                    failed += 1
                    sys.stderr.write(
                        f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.display_name}: {exc}\n"
                    )
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
