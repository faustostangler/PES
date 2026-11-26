"""Manifest and file reading helpers for batch source discovery.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from cresmo.application.ports import ChannelTaxonomyPort
from cresmo.application.services.frontmatter import read_frontmatter_header
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    SyncFilterCriteria,
    is_processable_transcript_file,
)
from cresmo.domain.value_objects.identity import YOUTUBE_CHANNEL_ID_PREFIX
from cresmo.domain.value_objects.media import ALLOWED_URL_SCHEMES

RECURSIVE_GLOB_ALL: Final[str] = "*"
DEFAULT_ENCODING: Final[str] = "utf-8"
MANIFEST_COMMENT_PREFIX: Final[str] = "#"
RAW_HEADER_SCAN_MAX_LINES: Final[int] = 50
FRONTMATTER_QUOTE_CHARS: Final[str] = "\"'"
CHANNEL_HANDLE_PREFIX: Final[str] = "@"
YOUTUBE_BASE_URL: Final[str] = "https://www.youtube.com/"
YOUTUBE_CHANNEL_URL_PREFIX: Final[str] = "https://www.youtube.com/channel/"
HTTP_SCHEME_PREFIX: Final[str] = "http"

_META_KEY_CHANNEL_ID: Final[str] = "channel_id"
_META_KEY_CHANNEL: Final[str] = "channel"
_META_KEY_CHANNEL_NAME: Final[str] = "channel_name"


def is_channel_or_playlist_feed(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    return ChannelId.is_channel_or_playlist_url(url)


def load_transcript_files(directory: Path | None) -> list[Path]:
    """Find all valid candidate transcript files recursively in a directory, ignoring system artifacts."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.rglob(RECURSIVE_GLOB_ALL)
        if p.is_file() and is_processable_transcript_file(p)
    )


def read_manifest_lines(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding=DEFAULT_ENCODING).splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith(MANIFEST_COMMENT_PREFIX):
            lines.append(cleaned)
    return lines


def extract_raw_file_metadata(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    loaded = read_frontmatter_header(path, max_lines=RAW_HEADER_SCAN_MAX_LINES)
    if not loaded:
        return {}

    metadata: dict[str, str] = {
        str(k).strip(): str(v).strip().strip(FRONTMATTER_QUOTE_CHARS)
        for k, v in loaded.items()
        if v is not None
    }
    raw_chan = (
        metadata.get(_META_KEY_CHANNEL_ID)
        or metadata.get(_META_KEY_CHANNEL)
        or metadata.get(_META_KEY_CHANNEL_NAME)
    )
    if raw_chan:
        if raw_chan.startswith(ALLOWED_URL_SCHEMES):
            metadata[_META_KEY_CHANNEL] = raw_chan
        elif raw_chan.startswith(CHANNEL_HANDLE_PREFIX):
            metadata[_META_KEY_CHANNEL] = f"{YOUTUBE_BASE_URL}{raw_chan}"
        elif raw_chan.startswith(YOUTUBE_CHANNEL_ID_PREFIX):
            metadata[_META_KEY_CHANNEL] = f"{YOUTUBE_CHANNEL_URL_PREFIX}{raw_chan}"
        else:
            metadata[_META_KEY_CHANNEL] = raw_chan
    return metadata


def matches_channel_target(criteria: SyncFilterCriteria, chan_target: str) -> bool:
    """Evaluate whether a channel identifier or URL matches the filter criteria."""
    if chan_target.startswith((HTTP_SCHEME_PREFIX, CHANNEL_HANDLE_PREFIX)):
        return criteria.matches_channel(channel_url=chan_target)
    return criteria.matches_channel(channel_name=ChannelName(chan_target))


def matches_category_target(
    criteria: SyncFilterCriteria,
    chan_target: str,
    taxonomy_port: ChannelTaxonomyPort | None = None,
) -> bool:
    """Evaluate whether a channel's category matches the filter criteria."""
    classifier = taxonomy_port.classify if taxonomy_port is not None else None
    if chan_target.startswith((HTTP_SCHEME_PREFIX, CHANNEL_HANDLE_PREFIX)):
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
        if vid_or_url.startswith(HTTP_SCHEME_PREFIX):
            return criteria.matches_video(video_url=vid_or_url)
        return criteria.matches_video(video_id=ContentId(vid_or_url), video_url=url_fallback)
    if url_fallback:
        return criteria.matches_video(video_url=url_fallback)
    return True
