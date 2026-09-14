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
from cresmo.domain.value_objects import ChannelFeedQuery
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

        Tiered streaming contract:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Tier 0: Priority text/markdown files (bypasses Stage 1 STT).
          - Tier 1: Priority URLs from playlist-priority.txt.
          - Tier 2: Existing raw transcripts in raw_dir lake.
          - Tier 3: Direct video URLs from playlist.txt.
          - Tier 4: Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()

        # Handle explicit single manifest override
        if q.explicit_manifest is not None:
            urls = read_manifest_lines(q.explicit_manifest)
            if urls:
                self._notify(
                    f"[manifest] Loaded {len(urls)} URLs from {q.explicit_manifest.name}\n"
                )
            return [BatchSource(kind="url", target=u) for u in urls]

        priority_texts_dir = q.priority_texts_dir or getattr(
            self.settings, "priority_texts_dir", None
        )
        playlist_priority_path = q.playlist_priority_path or getattr(
            self.settings, "playlist_priority_path", None
        )
        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        effective_lookback = (
            q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
        )
        workers = (
            q.discovery_workers
            if q.discovery_workers is not None
            else self.settings.channel_discovery_workers
        )

        sources: list[BatchSource] = []
        seen_vids: set[str] = set()

        def _register_video_id(target_str: str) -> None:
            m = _VIDEO_ID_REGEX.search(target_str)
            if m:
                seen_vids.add(m.group(1))
            else:
                seen_vids.add(Path(target_str).stem)

        # Tier 0: Priority text/markdown files
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            sources.append(BatchSource(kind="file", target=resolved_pf))
            _register_video_id(resolved_pf)

        # Tier 1: Priority URLs
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            sources.append(BatchSource(kind="url", target=pu))
            _register_video_id(pu)

        # Tier 2: Existing raw transcripts in data/raw/ lake & local channel mapping
        local_video_to_channel: dict[str, str] = {}
        if hasattr(raw_dir, "is_dir") and raw_dir.is_dir():
            raw_files = load_transcript_files(raw_dir)
            for rf in raw_files:
                stem = rf.stem
                meta = extract_raw_file_metadata(rf)
                vid_front = meta.get("video_id")
                chan_url = meta.get("channel")
                canonical_vid = vid_front or stem
                if chan_url:
                    local_video_to_channel[canonical_vid] = chan_url
                    local_video_to_channel[stem] = chan_url

                if q.scan_raw and stem not in seen_vids and canonical_vid not in seen_vids:
                    resolved_rf = str(rf.resolve())
                    sources.append(BatchSource(kind="file", target=resolved_rf))
                    seen_vids.add(stem)
                    seen_vids.add(canonical_vid)

        # Tier 3 & 4: Main playlist entries
        main_urls = read_manifest_lines(playlist_path)
        direct_video_urls: list[str] = []
        channel_feed_urls: list[str] = []
        all_playlist_video_urls: list[str] = []

        for mu in main_urls:
            m = _VIDEO_ID_REGEX.search(mu)
            vid = m.group(1) if m else None
            if is_channel_or_playlist_feed(mu):
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

        # Tier 4: Concurrent discovery of channel feeds
        if self.media_ingestion_port is not None and (
            channel_feed_urls or all_playlist_video_urls or local_video_to_channel
        ):
            cutoff = datetime.now(UTC) - timedelta(days=effective_lookback)

            def _discover_single(chan_url: str) -> list[str]:
                formatted_url = (
                    chan_url
                    if chan_url.startswith(("http://", "https://"))
                    else f"https://{chan_url}"
                )
                feed_query = ChannelFeedQuery(
                    channel_url=formatted_url,
                    lookback_days=effective_lookback,
                    max_videos=q.channel_max_videos,
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

            probed_channels: set[str] = set()
            channels_to_probe: list[str] = []

            # 1. Enqueue explicit channel feeds and channels discovered from raw lake
            for c_url in channel_feed_urls:
                if c_url not in probed_channels:
                    probed_channels.add(c_url)
                    channels_to_probe.append(c_url)

            for c_url in local_video_to_channel.values():
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
                self._notify(
                    f"[crawler] Resolving parent channels for {len(videos_needing_remote_lookup)} seed videos...\n"
                )
                max_res_workers = max(1, min(workers, len(videos_needing_remote_lookup)))
                with ThreadPoolExecutor(max_workers=max_res_workers) as res_executor:
                    future_to_vurl = {
                        res_executor.submit(
                            self.media_ingestion_port.extract_channel_url_from_video, vu
                        ): vu
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
                            self._notify(
                                f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                            )

            # 4. Concurrently probe all unique channels for recent uploads
            if channels_to_probe:
                self._notify(
                    f"[crawler] Discovering recent videos across {len(channels_to_probe)} channels "
                    f"(lookback: {effective_lookback}d, workers: {workers})...\n"
                )
                max_probe_workers = max(1, min(workers, len(channels_to_probe)))
                with ThreadPoolExecutor(max_workers=max_probe_workers) as probe_executor:
                    future_to_url = {
                        probe_executor.submit(_discover_single, u): u for u in channels_to_probe
                    }
                    for future in as_completed(future_to_url):
                        discovered_urls = future.result()
                        for d_url in discovered_urls:
                            m = _VIDEO_ID_REGEX.search(d_url)
                            vid = m.group(1) if m else d_url
                            if vid not in seen_vids:
                                seen_vids.add(vid)
                                sources.append(BatchSource(kind="url", target=d_url))

        return sources
