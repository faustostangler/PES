"""Batch Source Discovery Use Case for the Cresmo Knowledge Engine.

Orchestrates raw transcript ingestion, manifest parsing, concurrent channel resolution,
and lookback feed discovery via a streaming Producer-Consumer pattern.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-001: Modular Monolith Domain Integrity
- ADR-003: PES Production Architecture
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cresmo.application.ports import MediaIngestionPort
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ChannelId,
    ChannelName,
    ContentId,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
    normalize_to_uploads_playlist_url,
)
from cresmo.infrastructure.config import CresmoSettings


@dataclass(frozen=True)
class BatchSource:
    """Represents an atomic input item for batch processing.

    Attributes:
        kind: Source modality discriminator (SourceModality.FILE or SourceModality.URL).
        target: File path string or web URL.
        content_id: Strongly-typed canonical media identifier.
    """

    kind: SourceModality
    target: str
    content_id: ContentId | None = None

    def __post_init__(self) -> None:
        if isinstance(self.kind, str) and not isinstance(self.kind, SourceModality):
            try:
                modality = SourceModality(self.kind.strip().lower())
            except ValueError:
                raise ValueError(
                    f"Invalid BatchSource modality '{self.kind}'. Expected SourceModality.FILE or SourceModality.URL."
                )
            object.__setattr__(self, "kind", modality)
        if self.content_id is not None and not isinstance(self.content_id, ContentId):
            object.__setattr__(self, "content_id", ContentId.from_string(self.content_id))

    @property
    def vid(self) -> str | None:
        """Backward-compatible accessor for the string representation of content_id."""
        if self.content_id is None:
            return None
        return self.content_id.value if isinstance(self.content_id, ContentId) else self.content_id

    @property
    def display_name(self) -> str:
        """Human-readable representation for CLI logs."""
        if self.kind is SourceModality.FILE:
            return Path(self.target).name
        return self.target


@dataclass(frozen=True)
class BatchDiscoveryQuery:
    """Encapsulates input parameters for batch source discovery.

    Conforms to ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering.
    """

    explicit_manifest: Path | None = None
    manifest_path: Path | None = None
    priority_texts_dir: Path | None = None
    playlist_priority_path: Path | None = None
    playlist_path: Path | None = None
    raw_dir: Path | None = None
    scan_raw: bool = True
    lookback_days: int | None = None
    channel_max_videos: int = 50
    discovery_workers: int | None = None
    enable_channel_crawler: bool = True
    filter_criteria: SyncFilterCriteria = None  # type: ignore[assignment]
    queue_maxsize: int | None = None

    def __post_init__(self) -> None:
        # Ensure filter_criteria is always a valid SyncFilterCriteria (never None)
        if self.filter_criteria is None:
            object.__setattr__(self, "filter_criteria", SyncFilterCriteria())


def is_channel_or_playlist_feed(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    return ChannelId.is_channel_or_playlist_url(url)


def load_transcript_files(directory: Path | None) -> list[Path]:
    """Find all valid candidate transcript files recursively in a directory, ignoring system artifacts."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and is_processable_transcript_file(p)
    )


def read_manifest_lines(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def extract_raw_file_metadata(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def _matches_channel_target(criteria: SyncFilterCriteria, chan_target: str) -> bool:
    if chan_target.startswith(("http", "@")):
        return criteria.matches_channel(channel_url=chan_target)
    return criteria.matches_channel(channel_name=ChannelName(chan_target))


def _matches_category_target(criteria: SyncFilterCriteria, chan_target: str) -> bool:
    if chan_target.startswith(("http", "@")):
        return criteria.matches_category(channel_url=chan_target)
    return criteria.matches_category(channel_name=ChannelName(chan_target))


def _matches_video_target(
    criteria: SyncFilterCriteria,
    vid_or_url: ContentId | str | None,
    url_fallback: str | None = None,
) -> bool:
    if isinstance(vid_or_url, ContentId):
        return criteria.matches_video(video_id=vid_or_url, video_url=url_fallback)
    if isinstance(vid_or_url, str):
        if vid_or_url.startswith("http"):
            return criteria.matches_video(video_url=vid_or_url)
        return criteria.matches_video(video_id=ContentId(vid_or_url), video_url=url_fallback)
    if url_fallback:
        return criteria.matches_video(video_url=url_fallback)
    return True


class _BatchSourceAccumulator:
    """Encapsulates thread-safe deduplication and ordered accumulation of batch sources."""

    def __init__(self, on_source_added: Callable[[BatchSource], None] | None = None) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[ContentId | str] = set()
        self.on_source_added = on_source_added
        self._lock = threading.Lock()

    def add_source(
        self,
        kind: SourceModality,
        target: str,
        vid: ContentId | None = None,
        content_id: ContentId | None = None,
    ) -> BatchSource | None:
        """Append a source and register its identifier for deduplication."""
        with self._lock:
            resolved_id: ContentId | None = None
            raw_id = content_id if content_id is not None else vid
            if raw_id is not None:
                if isinstance(raw_id, ContentId):
                    resolved_id = raw_id
                else:
                    try:
                        resolved_id = ContentId.from_url_or_token(raw_id)
                    except (ValueError, TypeError):
                        resolved_id = None

            if resolved_id is None:
                try:
                    resolved_id = ContentId.from_url_or_token(target)
                except (ValueError, TypeError):
                    resolved_id = None
                if resolved_id is None:
                    try:
                        resolved_id = ContentId.from_url_or_token(Path(target).stem)
                    except (ValueError, TypeError):
                        resolved_id = None

            dedup_token: str = (
                resolved_id.value
                if resolved_id is not None
                else (str(raw_id) if raw_id is not None else Path(target).stem)
            )
            if (
                dedup_token in self.seen_vids
                or (resolved_id is not None and resolved_id in self.seen_vids)
                or (raw_id is not None and str(raw_id) in self.seen_vids)
            ):
                return None

            self.seen_vids.add(dedup_token)
            if raw_id is not None:
                self.seen_vids.add(raw_id if not isinstance(raw_id, ContentId) else raw_id.value)
            if resolved_id is not None:
                self.seen_vids.add(resolved_id)
                self.seen_vids.add(resolved_id.value)
            stem = Path(target).stem
            if stem:
                self.seen_vids.add(stem)

            src = BatchSource(kind=kind, target=target, content_id=resolved_id)
            self.sources.append(src)
            cb = self.on_source_added

        if cb is not None:
            cb(src)
        return src

    def register_identifier(self, target_str: str | ContentId) -> None:
        """Register video ID or path stem into the deduplication set."""
        with self._lock:
            if isinstance(target_str, ContentId):
                self.seen_vids.add(target_str)
                self.seen_vids.add(target_str.value)
                return
            self.seen_vids.add(target_str)
            try:
                cid = ContentId.from_url_or_token(target_str)
                self.seen_vids.add(cid)
                self.seen_vids.add(cid.value)
            except (ValueError, TypeError):
                cid = None
            stem = Path(target_str).stem
            if stem:
                self.seen_vids.add(stem)

    def has_seen(self, identifier: str | ContentId) -> bool:
        """Check if an identifier (video ID, stem, or ContentId) was already registered."""
        with self._lock:
            if identifier in self.seen_vids:
                return True
            if isinstance(identifier, ContentId):
                return identifier.value in self.seen_vids
            try:
                cid = ContentId.from_url_or_token(identifier)
                if cid in self.seen_vids or cid.value in self.seen_vids:
                    return True
            except (ValueError, TypeError):
                cid = None
            stem = Path(identifier).stem
            return stem in self.seen_vids if stem else False


class DiscoverBatchSourcesUseCase:
    """Application use case orchestrating batch discovery of files, seeds, and channel feeds."""

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings or CresmoSettings()
        self.progress_callback = progress_callback

    def _notify(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is not None:
            self.progress_callback(message)

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

        # A1: Priority items
        priority_texts_dir = (
            q.priority_texts_dir
            if q.priority_texts_dir is not None
            else getattr(self.settings, "priority_texts_dir", None)
        )
        pri_text_chans = self._collect_priority_texts(priority_texts_dir, acc, q.filter_criteria)

        # A2: Local raw lake (.md files)
        raw_dir = (
            q.raw_dir
            if q.raw_dir is not None
            else getattr(self.settings, "raw_dir", Path("data/raw"))
        )
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc, q.filter_criteria)

        playlist_priority_path = (
            q.playlist_priority_path
            if q.playlist_priority_path is not None
            else getattr(self.settings, "playlist_priority_path", None)
        )
        pri_url_chans, pri_unresolved = self._collect_priority_urls(
            playlist_priority_path, local_channels, acc, q.filter_criteria
        )

        # FAST-PATH PRIORITY SNAPSHOT:
        priority_sources = list(acc.sources)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )

        crawler_enabled = q.enable_channel_crawler

        # If crawler is disabled or media ingestion port is absent, process seeds synchronously
        if self.media_ingestion_port is None or not crawler_enabled:
            for src in priority_sources:
                yield src
            yielded_so_far = len(acc.sources)
            # ADR-012: pass filter_criteria so channel/video/category filters apply on sync path too
            self._classify_seeds(playlist_path, local_channels, acc, q.filter_criteria)
            for src in acc.sources[yielded_so_far:]:
                yield src
            return

        # OVERLAPPED STREAMING: Spawn background crawler feeding queue.Queue with bounded backpressure
        maxsize = (
            q.queue_maxsize
            if q.queue_maxsize is not None
            else getattr(self.settings, "discovery_queue_maxsize", 50)
        )
        stream_queue: queue.Queue[BatchSource | None | Exception] = queue.Queue(maxsize=maxsize)
        stop_event = threading.Event()

        # Connect accumulator callback so newly discovered sources stream directly to queue with backpressure
        def _enqueue_source(src: BatchSource) -> None:
            while not stop_event.is_set():
                try:
                    stream_queue.put(src, timeout=0.2)
                    break
                except queue.Full:
                    continue

        acc.on_source_added = _enqueue_source

        workers = (
            q.discovery_workers
            if q.discovery_workers is not None
            else self.settings.channel_discovery_workers
        )
        lookback = q.lookback_days if q.lookback_days is not None else self.settings.days_lookback

        # Field Video Detective (find new videos)
        def _crawler_producer() -> None:
            try:
                # 1. Seed parser
                channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
                    playlist_path, local_channels, acc, q.filter_criteria
                )

                for pch in pri_text_chans + pri_url_chans:
                    norm_pch = normalize_to_uploads_playlist_url(pch)
                    if norm_pch not in probed_channels:
                        probed_channels.add(norm_pch)
                        channels_to_probe.append(norm_pch)

                if stop_event.is_set():
                    return

                # 2. Seed-Channel resolver
                all_remote_seeds = list(dict.fromkeys(pri_unresolved + remote_videos))
                if all_remote_seeds:
                    self._resolve_remote_channels(
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
                    f"  - A1 (Priority): {len(set(pri_text_chans + pri_url_chans))} channel(s)\n"
                    f"  - A2 (Local Raw Lake): {len(set(local_channels.values()))} channel(s)\n"
                    f"  - A3 (Seed Playlist): {len(channels_to_probe)} total channel(s)\n"
                )

                # ADR-012: Final alphabetical sort after all channel sources are collected
                # (seeds from _classify_seeds + priority channels + remote-resolved channels)
                channels_to_probe = sorted(channels_to_probe, key=lambda c: c.lower())

                # 3. Channel Video Finder (YouTube API)
                self._probe_channel_feeds(
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
                    stream_queue.put(exc, timeout=2.0)
                except queue.Full:
                    pass
            finally:
                while not stop_event.is_set():
                    try:
                        stream_queue.put(None, timeout=0.2)
                        break
                    except queue.Full:
                        continue

        # Parallel processing workers
        crawler_thread = threading.Thread(
            target=_crawler_producer,
            name="CresmoCrawlerProducer",
            daemon=True,
        )
        # Let's Go Brandon
        crawler_thread.start()

        try:
            # Yield fast-path priority sources immediately while crawler runs concurrently!
            for src in priority_sources:
                yield src

            # SINALIZADOR VISUAL:
            if priority_sources:
                self._notify(
                    f"[stream] Fast-path complete: {len(priority_sources)} priority item(s) processed. "
                    "Awaiting crawled feed stream...\n"
                )
            # Active waiting in line
            while True:
                item = stream_queue.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    self._notify(f"[crawler] Warning: Background crawler failed: {item}\n")
                    break
                yield item
        finally:
            stop_event.set()

    def _load_explicit_manifest(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
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

    def _collect_priority_texts(
        self,
        priority_texts_dir: Path | None,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> list[str]:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        criteria = filter_criteria or SyncFilterCriteria()
        priority_channels: list[str] = []
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            if not is_processable_transcript_file(pf):
                continue
            meta = extract_raw_file_metadata(pf)
            raw_chan = meta.get("channel") or meta.get("channel_id")
            vid = meta.get("video_id") or pf.stem

            matches = True
            if not criteria.is_empty():
                if criteria.video_ids and not _matches_video_target(criteria, vid):
                    matches = False
                if criteria.channels and (
                    not raw_chan or not _matches_channel_target(criteria, raw_chan)
                ):
                    matches = False
                if criteria.categories and (
                    not raw_chan or not _matches_category_target(criteria, raw_chan)
                ):
                    matches = False

            if matches:
                resolved_pf = str(pf.resolve())
                acc.add_source(kind=SourceModality.FILE, target=resolved_pf)

            if raw_chan and (
                criteria.is_empty()
                or (
                    _matches_channel_target(criteria, raw_chan)
                    and _matches_category_target(criteria, raw_chan)
                )
            ):
                norm_chan = normalize_to_uploads_playlist_url(raw_chan)
                if norm_chan not in priority_channels:
                    priority_channels.append(norm_chan)
        return priority_channels

    def _collect_priority_urls(
        self,
        playlist_priority_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> tuple[list[str], list[str]]:
        """Collect priority URLs scheduled for immediate processing."""
        criteria = filter_criteria or SyncFilterCriteria()
        priority_channels: list[str] = []
        unresolved_videos: list[str] = []
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            if is_channel_or_playlist_feed(pu):
                if criteria.is_empty() or (
                    criteria.matches_channel(channel_url=pu)
                    and criteria.matches_category(channel_url=pu)
                ):
                    norm_chan = normalize_to_uploads_playlist_url(pu)
                    if norm_chan not in priority_channels:
                        priority_channels.append(norm_chan)
            else:
                cid = ContentId.extract_from_text(pu)
                vid_str = cid.value if cid else None
                local_chan = local_channels.get(vid_str) if vid_str else None

                matches = True
                if not criteria.is_empty():
                    if criteria.video_ids and not _matches_video_target(criteria, cid or pu, pu):
                        matches = False
                    if criteria.channels and (
                        not local_chan or not _matches_channel_target(criteria, local_chan)
                    ):
                        matches = False
                    if criteria.categories and (
                        not local_chan or not _matches_category_target(criteria, local_chan)
                    ):
                        matches = False

                if matches and not (cid and acc.has_seen(cid)):
                    acc.add_source(kind=SourceModality.URL, target=pu, content_id=cid)

                if local_chan:
                    if criteria.is_empty() or (
                        _matches_channel_target(criteria, local_chan)
                        and _matches_category_target(criteria, local_chan)
                    ):
                        norm_local = normalize_to_uploads_playlist_url(local_chan)
                        if norm_local not in priority_channels:
                            priority_channels.append(norm_local)
                elif pu not in unresolved_videos and (
                    criteria.is_empty()
                    or (
                        criteria.video_ids
                        and _matches_video_target(criteria, cid or pu, pu)
                        and not criteria.channels
                        and not criteria.categories
                    )
                ):
                    unresolved_videos.append(pu)
        return priority_channels, unresolved_videos

    def _scan_raw_lake(
        self,
        raw_dir: Path | None,
        scan_raw: bool,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        criteria = filter_criteria or SyncFilterCriteria()
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            if not is_processable_transcript_file(rf):
                continue
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem

            already_seen = acc.has_seen(stem) or acc.has_seen(canonical_vid)

            # Record in accumulator so discovered feeds know these already exist in local lake
            acc.seen_vids.add(stem)
            acc.seen_vids.add(canonical_vid)

            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not already_seen:
                matches = True
                if not criteria.is_empty():
                    if criteria.video_ids and not _matches_video_target(criteria, canonical_vid):
                        matches = False
                    if criteria.channels and (
                        not chan_url or not _matches_channel_target(criteria, chan_url)
                    ):
                        matches = False
                    if criteria.categories and (
                        not chan_url or not _matches_category_target(criteria, chan_url)
                    ):
                        matches = False
                if matches:
                    resolved_rf = str(rf.resolve())
                    if not any(s.target == resolved_rf for s in acc.sources):
                        acc.sources.append(
                            BatchSource(kind=SourceModality.FILE, target=resolved_rf)
                        )

        return local_video_to_channel

    def _classify_seeds(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups.

        ADR-012: Applies channel filter criteria and returns channels sorted alphabetically.
        """
        criteria = filter_criteria or SyncFilterCriteria()
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels and (
                criteria.is_empty()
                or (
                    criteria.matches_channel(channel_url=c_url)
                    and criteria.matches_category(channel_url=c_url)
                )
            ):
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels and (
                    criteria.is_empty()
                    or (
                        criteria.matches_channel(channel_url=mu)
                        and criteria.matches_category(channel_url=mu)
                    )
                ):
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                cid = ContentId.extract_from_text(mu)
                vid_str = cid.value if cid else None
                local_chan = local_channels.get(vid_str) if vid_str else None

                matches = True
                if not criteria.is_empty():
                    if criteria.video_ids and not _matches_video_target(criteria, cid or mu, mu):
                        matches = False
                    if criteria.channels and (
                        not local_chan or not _matches_channel_target(criteria, local_chan)
                    ):
                        matches = False
                    if criteria.categories and (
                        not local_chan or not _matches_category_target(criteria, local_chan)
                    ):
                        matches = False

                # ADR-012: apply multi-criteria filter for direct video seeds
                if matches and not (cid and acc.has_seen(cid)):
                    acc.add_source(kind=SourceModality.URL, target=mu, content_id=cid)

                if local_chan:
                    if local_chan not in probed_channels and (
                        criteria.is_empty()
                        or (
                            _matches_channel_target(criteria, local_chan)
                            and _matches_category_target(criteria, local_chan)
                        )
                    ):
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                elif mu not in remote_videos and (
                    criteria.is_empty()
                    or (
                        criteria.video_ids
                        and _matches_video_target(criteria, cid or mu, mu)
                        and not criteria.channels
                        and not criteria.categories
                    )
                ):
                    remote_videos.append(mu)

        # ADR-012: Enforce strict alphabetical ordering of channels before feed probing
        channels_to_probe = sorted(channels_to_probe, key=lambda c: c.lower())

        return channels_to_probe, remote_videos, probed_channels

    def _resolve_remote_channels(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
        filter_criteria: SyncFilterCriteria | None = None,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        criteria = filter_criteria or SyncFilterCriteria()
        if not videos:
            return

        max_workers = max(1, min(workers, len(videos)))
        self._notify(
            f"[crawler] Resolving parent channels for {len(videos)} seed videos with {max_workers} workers\n"
        )
        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="CresmoChannelResolver",
        ) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                if stop_event is not None and stop_event.is_set():
                    break
                try:
                    resolved_chan = fut.result()
                    if (
                        isinstance(resolved_chan, str)
                        and resolved_chan.strip()
                        and resolved_chan not in probed_channels
                    ):
                        chan_clean = resolved_chan.strip()
                        if criteria.is_empty() or (
                            criteria.matches_channel(channel_url=chan_clean)
                            and criteria.matches_category(channel_url=chan_clean)
                        ):
                            probed_channels.add(chan_clean)
                            channels_to_probe.append(chan_clean)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def _probe_channel_feeds(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently (Stage B).

        ADR-012: Channels are pre-sorted alphabetically by caller. Applies video ID filter
        when filter_criteria specifies video_ids.
        """
        criteria = filter_criteria or SyncFilterCriteria()
        if not channels:
            return

        self._notify(
            f"[crawler] Stage B: Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))
        discovered_count = 0

        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="CresmoFeedProber",
        ) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                if stop_event is not None and stop_event.is_set():
                    break
                try:
                    discovered_urls = future.result()
                except Exception as exc:  # noqa: BLE001
                    u = future_to_url[future]
                    self._notify(f"[crawler] Warning: Failed to probe feed for {u}: {exc}\n")
                    continue

                for d_url in discovered_urls:
                    if stop_event is not None and stop_event.is_set():
                        break
                    cid = ContentId.extract_from_text(d_url)
                    vid_token = cid or d_url
                    # Stage B: Skip if already in raw lake or already queued
                    if not acc.has_seen(vid_token):
                        # ADR-012: apply video ID filter before scheduling ingestion
                        if not _matches_video_target(criteria, cid or d_url, d_url):
                            continue
                        added = acc.add_source(
                            kind=SourceModality.URL, target=d_url, content_id=cid
                        )
                        if added is not None:
                            discovered_count += 1

        self._notify(
            f"[crawler] Stage B complete: Discovered {discovered_count} new video(s) for ingestion "
            f"(excluding items already existing in local raw lake)\n"
        )

    def _probe_single_channel_feed(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []
