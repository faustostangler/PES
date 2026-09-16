"""Batch source discovery use case for Cresmo Knowledge Engine.

Orchestrates raw transcript ingestion, manifest parsing, concurrent channel resolution,
and lookback feed discovery per ADR-003 and Clean Hexagonal Architecture.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cresmo.application.ports import MediaIngestionPort
from cresmo.domain.value_objects import ChannelFeedQuery, normalize_to_uploads_playlist_url
from cresmo.infrastructure.config import CresmoSettings

_CHANNEL_REGEX = re.compile(r"youtube\.com/(?:@|c/|channel/|user/|playlist\?list=)", re.IGNORECASE)
_VIDEO_ID_REGEX = re.compile(
    r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/|/live/|^)([a-zA-Z0-9_-]{8,64})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BatchSource:
    """Represents an atomic input item for batch processing."""

    kind: str  # "file" | "url"
    target: str

    @property
    def display_name(self) -> str:
        """Human-readable representation for CLI logs."""
        if self.kind == "file":
            return Path(self.target).name
        return self.target


@dataclass(frozen=True)
class BatchDiscoveryQuery:
    """Encapsulates input parameters for batch source discovery."""

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
    enable_channel_crawler: bool | None = None


def is_channel_or_playlist_feed(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def load_transcript_files(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
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


class _BatchSourceAccumulator:
    """Encapsulates deduplication and ordered accumulation of batch sources."""

    def __init__(self) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[str] = set()

    def add_source(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def register_identifier(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def has_seen(self, identifier: str) -> bool:
        """Check if an identifier (video ID or stem) was already registered."""
        return identifier in self.seen_vids


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

    def execute(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Two-stage discovery pipeline:
        Stage A: Canais para Sync (Discover unique channels to synchronize)
          A1: Priority sources (priority_texts_dir and playlist_priority_path)
          A2: Local raw lake (all channels from existing data/raw/**/*.md files)
          A3: Seed playlist videos (all channels of videos in data/playlist.txt)
             - Resolved in O(1) from local lake if already ingested
             - Resolved concurrently via yt-dlp if new seed video

        Stage B: Vídeos para baixar legenda (Discover recent uploads to ingest)
          - For each unique channel discovered in Stage A:
            - Query uploads playlist (UU...) within lookback_days
            - Filter: If video_id already exists in local raw lake (.md), SKIP!
            - If video_id does NOT exist in local raw lake, add to download queue.
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()

        # A1: Priority items
        priority_texts_dir = q.priority_texts_dir or getattr(
            self.settings, "priority_texts_dir", None
        )
        pri_text_chans = self._collect_priority_texts(priority_texts_dir, acc)

        # A2: Local raw lake (.md files)
        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_priority_path = q.playlist_priority_path or getattr(
            self.settings, "playlist_priority_path", None
        )
        pri_url_chans, pri_unresolved = self._collect_priority_urls(
            playlist_priority_path, local_channels, acc
        )

        # A3: Seed playlist
        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        # Incorporate priority channels into channels_to_probe
        for pch in pri_text_chans + pri_url_chans:
            norm_pch = normalize_to_uploads_playlist_url(pch)
            if norm_pch not in probed_channels:
                probed_channels.add(norm_pch)
                channels_to_probe.append(norm_pch)

        crawler_enabled = (
            q.enable_channel_crawler
            if q.enable_channel_crawler is not None
            else getattr(self.settings, "enable_channel_crawler", True)
        )

        if self.media_ingestion_port is not None and crawler_enabled:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            all_remote_seeds = list(dict.fromkeys(pri_unresolved + remote_videos))
            if all_remote_seeds:
                self._resolve_remote_channels(
                    all_remote_seeds, workers, probed_channels, channels_to_probe
                )

            self._notify(
                f"[crawler] Stage A complete: {len(channels_to_probe)} unique channel(s) identified for sync\n"
                f"  - A1 (Priority): {len(set(pri_text_chans + pri_url_chans))} channel(s)\n"
                f"  - A2 (Local Raw Lake): {len(set(local_channels.values()))} channel(s)\n"
                f"  - A3 (Seed Playlist): {len(channels_to_probe)} total channel(s)\n"
            )

            # Stage B: Vídeos para baixar legenda
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def _load_explicit_manifest(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    def _collect_priority_texts(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> list[str]:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_channels: list[str] = []
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=resolved_pf)
            meta = extract_raw_file_metadata(pf)
            raw_chan = meta.get("channel") or meta.get("channel_id")
            if raw_chan:
                norm_chan = normalize_to_uploads_playlist_url(raw_chan)
                if norm_chan not in priority_channels:
                    priority_channels.append(norm_chan)
        return priority_channels

    def _collect_priority_urls(
        self,
        playlist_priority_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str]]:
        """Collect priority URLs scheduled for immediate processing."""
        priority_channels: list[str] = []
        unresolved_videos: list[str] = []
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            if is_channel_or_playlist_feed(pu):
                norm_chan = normalize_to_uploads_playlist_url(pu)
                if norm_chan not in priority_channels:
                    priority_channels.append(norm_chan)
            else:
                m = _VIDEO_ID_REGEX.search(pu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=pu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    norm_local = normalize_to_uploads_playlist_url(local_chan)
                    if norm_local not in priority_channels:
                        priority_channels.append(norm_local)
                elif pu not in unresolved_videos:
                    unresolved_videos.append(pu)
        return priority_channels, unresolved_videos

    def _scan_raw_lake(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
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
                resolved_rf = str(rf.resolve())
                if not any(s.target == resolved_rf for s in acc.sources):
                    acc.sources.append(BatchSource(kind="file", target=resolved_rf))

        return local_video_to_channel

    def _classify_seeds(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def _resolve_remote_channels(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        max_workers = max(1, min(workers, len(videos)))
        self._notify(
            f"[crawler] Resolving parent channels for {len(videos)} seed videos with {max_workers} workers\n"
        )
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
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
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently (Stage B)."""
        if not channels:
            return

        self._notify(
            f"[crawler] Stage B: Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))
        discovered_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    # Stage B: Skip if already in raw lake or already queued
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)
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
