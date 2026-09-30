"""Channel feed discovery and channel URL extraction utilities.

Conforms to:
- ADR-004: Native Media Ingestion Decommissioning
- SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, cast

import yt_dlp

from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ChannelId,
    ChannelName,
    ContentId,
    DiscoveredMediaItem,
    normalize_to_uploads_playlist_url,
)
from cresmo.infrastructure.adapters.media.subtitles import parse_published_datetime

logger = logging.getLogger(__name__)


def discover_channel_feed_items(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = normalize_to_uploads_playlist_url(query.channel_url)
    opts = dict(ydl_opts)
    opts.update(
        {
            "extract_flat": True,
            "playlistend": query.max_videos,
            "quiet": True,
            "no_warnings": True,
        }
    )

    try:
        with yt_dlp.YoutubeDL(cast(Any, opts)) as ydl:
            info = ydl.extract_info(target_url, download=False)
            # Fallback to original channel_url if uploads playlist returned empty
            if (not info or not info.get("entries")) and target_url != query.channel_url:
                info = ydl.extract_info(query.channel_url, download=False)
    except Exception as exc:  # noqa: BLE001
        handle_error(exc)
        return []

    if not info:
        return []

    entries = info.get("entries") or []
    channel_title = sanitize_fs_name(
        str(info.get("title") or info.get("uploader") or "Unknown_Channel")
    )
    items: list[DiscoveredMediaItem] = []

    for entry in entries:
        if not entry or not isinstance(entry, dict):
            continue

        raw_vid = str(entry.get("id") or "").strip()
        title = str(entry.get("title") or "").strip()
        if not raw_vid or not title:
            continue

        cid = ContentId.extract_from_text(raw_vid) or ContentId.from_url_or_token(raw_vid)
        url = str(entry.get("url") or f"https://www.youtube.com/watch?v={cid.value}").strip()
        raw_channel = str(entry.get("channel") or entry.get("uploader") or channel_title)
        channel_name = ChannelName.from_string(sanitize_fs_name(raw_channel))

        pub_date = parse_published_datetime(entry.get("upload_date"))

        items.append(
            DiscoveredMediaItem(
                content_id=cid,
                title=title,
                published_at=pub_date,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def extract_channel_url_from_info(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None
