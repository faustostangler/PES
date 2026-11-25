"""Manifest and file reading helpers for batch source discovery.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports import ChannelTaxonomyPort
from cresmo.application.services.frontmatter import read_frontmatter_header
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    SyncFilterCriteria,
    is_processable_transcript_file,
)


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
    loaded = read_frontmatter_header(path, max_lines=50)
    if not loaded:
        return {}

    metadata: dict[str, str] = {
        str(k).strip(): str(v).strip().strip("\"'")
        for k, v in loaded.items()
        if v is not None
    }
    raw_chan = metadata.get("channel_id") or metadata.get("channel") or metadata.get("channel_name")
    if raw_chan:
        if raw_chan.startswith(("http://", "https://")):
            metadata["channel"] = raw_chan
        elif raw_chan.startswith("@"):
            metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
        elif raw_chan.startswith("UC"):
            metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
        else:
            metadata["channel"] = raw_chan
    return metadata


def matches_channel_target(criteria: SyncFilterCriteria, chan_target: str) -> bool:
    """Evaluate whether a channel identifier or URL matches the filter criteria."""
    if chan_target.startswith(("http", "@")):
        return criteria.matches_channel(channel_url=chan_target)
    return criteria.matches_channel(channel_name=ChannelName(chan_target))


def matches_category_target(
    criteria: SyncFilterCriteria,
    chan_target: str,
    taxonomy_port: ChannelTaxonomyPort | None = None,
) -> bool:
    """Evaluate whether a channel's category matches the filter criteria."""
    classifier = taxonomy_port.classify if taxonomy_port is not None else None
    if chan_target.startswith(("http", "@")):
        return criteria.matches_category(channel_url=chan_target, classifier=classifier)
    return criteria.matches_category(
        channel_name=ChannelName(chan_target),
        classifier=classifier,
    )


def matches_video_target(
    criteria: SyncFilterCriteria,
    vid_or_url: ContentId | str | None,
    url_fallback: str | None = None,
) -> bool:
    """Evaluate whether a video identifier or URL matches the filter criteria."""
    if isinstance(vid_or_url, ContentId):
        return criteria.matches_video(video_id=vid_or_url, video_url=url_fallback)
    if isinstance(vid_or_url, str):
        if vid_or_url.startswith("http"):
            return criteria.matches_video(video_url=vid_or_url)
        return criteria.matches_video(video_id=ContentId(vid_or_url), video_url=url_fallback)
    if url_fallback:
        return criteria.matches_video(video_url=url_fallback)
    return True
