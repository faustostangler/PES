"""Batch Source Discovery Use Case orchestrator for the Cresmo Knowledge Engine.

Orchestrates raw transcript ingestion, manifest parsing, concurrent channel resolution,
and lookback feed discovery via a streaming Producer-Consumer pattern.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-010: Streaming-First Unification
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from cresmo.application.ports import (
    DefaultPipelineSettings,
    MediaIngestionPort,
    PipelineSettingsProtocol,
)
from cresmo.application.use_cases.discovery.channel_crawler import ChannelFeedCrawlerService
from cresmo.application.use_cases.discovery.lake_scanner import LakeScannerService
from cresmo.application.use_cases.discovery.manifests import (
    read_manifest_lines as _read_manifest_lines,
)
from cresmo.application.use_cases.discovery.models import (
    BatchDiscoveryQuery,
    BatchSource,
    _BatchSourceAccumulator,
)
from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    normalize_to_uploads_playlist_url,
)

logger = logging.getLogger(__name__)

_DEFAULT_STREAM_QUEUE_TIMEOUT_SECONDS: float = 0.2
_DEFAULT_STREAM_ERROR_TIMEOUT_SECONDS: float = 2.0


@dataclass(frozen=True)
class _FastPathDiscoveryState:
    priority_sources: list[BatchSource]
    local_video_channel_map: dict[str, str]
    priority_text_channels: list[str]
    priority_url_channels: list[str]
    unresolved_priority_video_seeds: list[str]
    playlist_path: Path


class DiscoverBatchSourcesUseCase:
    """Application use case orchestrating batch discovery of files, seeds, and channel feeds."""

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort | None = None,
        settings: PipelineSettingsProtocol | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings or DefaultPipelineSettings()
        self.progress_callback = progress_callback
        self._crawler_service = ChannelFeedCrawlerService(
            media_ingestion_port=self.media_ingestion_port,  # type: ignore[arg-type]
            notify_fn=self._notify,
        )

    def _notify(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is not None:
            self.progress_callback(message)

    def _collect_fast_path_sources(
        self,
        q: BatchDiscoveryQuery,
        acc: _BatchSourceAccumulator,
    ) -> _FastPathDiscoveryState:
        """Collect and return fast-path priority sources and initial channel lookups."""
        priority_texts_dir = (
            q.priority_texts_dir
            if q.priority_texts_dir is not None
            else self.settings.priority_texts_dir
        )
        priority_text_channels = LakeScannerService.collect_priority_texts(
            priority_texts_dir, acc, q.filter_criteria
        )

        raw_dir = (
            q.raw_dir
            if q.raw_dir is not None
            else self.settings.raw_dir
        )
        local_video_channel_map = LakeScannerService.scan_raw_lake(
            raw_dir, q.scan_raw, acc, q.filter_criteria
        )

        playlist_priority_path = (
            q.playlist_priority_path
            if q.playlist_priority_path is not None
            else self.settings.playlist_priority_path
        )
        priority_url_channels, unresolved_priority_video_seeds = (
            LakeScannerService.collect_priority_urls(
                playlist_priority_path, local_video_channel_map, acc, q.filter_criteria
            )
        )

        priority_sources = list(acc.sources)
        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or self.settings.playlist_path
        )

        return _FastPathDiscoveryState(
            priority_sources=priority_sources,
            local_video_channel_map=local_video_channel_map,
            priority_text_channels=priority_text_channels,
            priority_url_channels=priority_url_channels,
            unresolved_priority_video_seeds=unresolved_priority_video_seeds,
            playlist_path=playlist_path,
        )

    def _execute_sync_fallback(
        self,
        q: BatchDiscoveryQuery,
        acc: _BatchSourceAccumulator,
        state: _FastPathDiscoveryState,
    ) -> Iterator[BatchSource]:
        """Execute synchronous fallback discovery when background crawler is disabled."""
        for src in state.priority_sources:
            yield src
        yielded_so_far = len(acc.sources)
        LakeScannerService.classify_seeds(
            state.playlist_path, state.local_video_channel_map, acc, q.filter_criteria
        )
        for src in acc.sources[yielded_so_far:]:
            yield src

    def _run_crawler_producer(
        self,
        q: BatchDiscoveryQuery,
        acc: _BatchSourceAccumulator,
        state: _FastPathDiscoveryState,
        stream_queue: queue.Queue[BatchSource | None | Exception],
        stop_event: threading.Event,
    ) -> None:
        """Background thread worker probing channels and streaming discovered sources."""
        workers = (
            q.discovery_workers
            if q.discovery_workers is not None
            else self.settings.channel_discovery_workers
        )
        lookback = q.lookback_days if q.lookback_days is not None else self.settings.days_lookback

        try:
            channels_to_probe, remote_videos, probed_channels = LakeScannerService.classify_seeds(
                state.playlist_path, state.local_video_channel_map, acc, q.filter_criteria
            )

            for pch in state.priority_text_channels + state.priority_url_channels:
                norm_pch = normalize_to_uploads_playlist_url(pch)
                if norm_pch not in probed_channels:
                    probed_channels.add(norm_pch)
                    channels_to_probe.append(norm_pch)

            if stop_event.is_set():
                return

            all_remote_seeds = list(
                dict.fromkeys(state.unresolved_priority_video_seeds + remote_videos)
            )
            if all_remote_seeds:
                self._crawler_service.resolve_remote_channels(
                    all_remote_seeds,
                    workers,
                    probed_channels,
                    channels_to_probe,
                    filter_criteria=q.filter_criteria,
                    stop_event=stop_event,
                )

            if stop_event.is_set():
                return

            self._notify(
                f"[crawler] Stage A complete: {len(channels_to_probe)} unique channel(s) identified for sync\n"
                f"  - A1 (Priority): {len(set(state.priority_text_channels + state.priority_url_channels))} channel(s)\n"
                f"  - A2 (Local Raw Lake): {len(set(state.local_video_channel_map.values()))} channel(s)\n"
                f"  - A3 (Seed Playlist): {len(channels_to_probe)} total channel(s)\n"
            )

            channels_to_probe = sorted(channels_to_probe, key=str.casefold)

            self._crawler_service.probe_channel_feeds(
                channels_to_probe,
                lookback,
                q.channel_max_videos,
                workers,
                acc,
                filter_criteria=q.filter_criteria,
                stop_event=stop_event,
            )
        except Exception as exc:  # noqa: BLE001
            try:
                stream_queue.put(exc, timeout=_DEFAULT_STREAM_ERROR_TIMEOUT_SECONDS)
            except queue.Full:
                logger.warning(
                    "[crawler] Failed to put error into stream_queue (queue full): %s", exc
                )
        finally:
            while not stop_event.is_set():
                try:
                    stream_queue.put(None, timeout=_DEFAULT_STREAM_QUEUE_TIMEOUT_SECONDS)
                    return
                except queue.Full:
                    pass

    def _consume_stream_queue(
        self,
        priority_sources: list[BatchSource],
        stream_queue: queue.Queue[BatchSource | None | Exception],
        stop_event: threading.Event,
    ) -> Iterator[BatchSource]:
        """Consume streamed items from queue yielding priority sources first."""
        try:
            yield from priority_sources

            if priority_sources:
                self._notify(
                    f"[stream] Fast-path complete: {len(priority_sources)} priority item(s) processed. "
                    "Awaiting crawled feed stream...\n"
                )
            while True:
                item = stream_queue.get()
                if item is None:
                    return
                if isinstance(item, Exception):
                    self._notify(f"[crawler] Warning: Background crawler failed: {item}\n")
                    return
                yield item
        finally:
            stop_event.set()

    def execute(self, query: BatchDiscoveryQuery | None = None) -> Iterator[BatchSource]:
        """Discover batch sources with streaming queue for overlapped producer-consumer execution.

        Yields high-priority local texts and priority playlist items immediately in the fast path
        (millisecond latency), while launching channel feed crawling in a concurrent background thread.
        Conforms to ADR-010 (Streaming-First Unification).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            yield from self._load_explicit_manifest(q.explicit_manifest)
            return

        acc = _BatchSourceAccumulator()
        state = self._collect_fast_path_sources(q, acc)

        if self.media_ingestion_port is None or not q.enable_channel_crawler:
            yield from self._execute_sync_fallback(q, acc, state)
            return

        maxsize = (
            q.queue_maxsize
            if q.queue_maxsize is not None
            else getattr(self.settings, "discovery_queue_maxsize", 50)
        )
        stream_queue: queue.Queue[BatchSource | None | Exception] = queue.Queue(maxsize=maxsize)
        stop_event = threading.Event()

        def _enqueue_source(src: BatchSource) -> None:
            while not stop_event.is_set():
                try:
                    stream_queue.put(src, timeout=_DEFAULT_STREAM_QUEUE_TIMEOUT_SECONDS)
                    return
                except queue.Full:
                    pass

        acc.on_source_added = _enqueue_source

        crawler_thread = threading.Thread(
            target=self._run_crawler_producer,
            args=(q, acc, state, stream_queue, stop_event),
            name="CresmoCrawlerProducer",
            daemon=True,
        )
        crawler_thread.start()

        yield from self._consume_stream_queue(state.priority_sources, stream_queue, stop_event)

    def _load_explicit_manifest(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = _read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        sources: list[BatchSource] = []
        for u in urls:
            try:
                cid = ContentId.from_url_or_token(u)
            except (ValueError, TypeError):
                cid = None
            sources.append(BatchSource(kind=SourceModality.URL, target=u, content_id=cid))
        return sources
