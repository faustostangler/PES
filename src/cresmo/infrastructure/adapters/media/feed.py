"""Channel feed discovery and channel URL extraction utilities.

Conforms to:
- ADR-004: Native Media Ingestion Decommissioning
- ADR-075: High-Throughput Native Media Ingestion (Atom RSS Fast-Path)
- SPEC-004: Native Media Ingestion Specification
- SPEC-075: High-Throughput Native Media Ingestion Specifications
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any, Final, cast
from xml.etree import ElementTree

import structlog

from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ChannelId,
    ChannelName,
    ContentId,
    DiscoveredMediaItem,
    normalize_to_uploads_playlist_url,
)
from cresmo.domain.value_objects.constants import MIN_CANONICAL_CHANNEL_ID_LENGTH
from cresmo.infrastructure.adapters.media.subtitles import parse_published_datetime

logger = structlog.get_logger(__name__)

YOUTUBE_RSS_MAX_ENTRIES: Final[int] = 15
_ATOM_NS: Final[str] = "{http://www.w3.org/2005/Atom}"
_YT_NS: Final[str] = "{http://www.youtube.com/xml/schemas/2015}"
_PLAYLIST_ID_REGEX = re.compile(r"[?&]list=([a-zA-Z0-9_-]+)")


def resolve_youtube_rss_url(channel_url: str) -> str | None:
    """Resolve canonical YouTube channel/playlist URL to Atom RSS feed URL if possible."""
    cleaned = channel_url.strip()
    if not cleaned:
        return None

    channel_id = ChannelId.extract_from_text(cleaned)
    if channel_id and channel_id.is_youtube_canonical:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id.value}"

    playlist_match = _PLAYLIST_ID_REGEX.search(cleaned)
    if playlist_match:
        list_id = playlist_match.group(1).strip()
        if list_id.startswith("UU") and len(list_id) >= MIN_CANONICAL_CHANNEL_ID_LENGTH:
            canonical_channel_id = f"UC{list_id[2:]}"
            return f"https://www.youtube.com/feeds/videos.xml?channel_id={canonical_channel_id}"
        return f"https://www.youtube.com/feeds/videos.xml?playlist_id={list_id}"

    return None


def _parse_atom_published_datetime(raw_value: str | None) -> datetime:
    """Parse ISO-8601 Atom published timestamp into timezone-aware UTC datetime."""
    if not raw_value or not raw_value.strip():
        return datetime.now(UTC)
    try:
        parsed = datetime.fromisoformat(raw_value.strip())
    except ValueError:
        return datetime.now(UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_youtube_atom_feed(
    xml_payload: str,
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Parse YouTube Atom XML feed payload into DiscoveredMediaItem value objects."""
    root = ElementTree.fromstring(xml_payload)
    raw_feed_title = (
        root.findtext(f"{_ATOM_NS}title")
        or root.findtext(f"{_ATOM_NS}author/{_ATOM_NS}name")
        or "Unknown_Channel"
    )
    default_channel_name = ChannelName.from_string(sanitize_fs_name(raw_feed_title))

    items: list[DiscoveredMediaItem] = []
    for entry in root.findall(f"{_ATOM_NS}entry"):
        raw_vid = (entry.findtext(f"{_YT_NS}videoId") or "").strip()
        title = (entry.findtext(f"{_ATOM_NS}title") or "").strip()
        if not raw_vid or not title:
            continue

        cid = ContentId.extract_from_text(raw_vid) or ContentId.from_url_or_token(raw_vid)

        media_url = ""
        for link in entry.findall(f"{_ATOM_NS}link"):
            if link.attrib.get("rel", "alternate") == "alternate":
                href = link.attrib.get("href", "").strip()
                if href:
                    media_url = href
                    break
        if not media_url:
            media_url = f"https://www.youtube.com/watch?v={cid.value}"

        entry_author = (entry.findtext(f"{_ATOM_NS}author/{_ATOM_NS}name") or "").strip()
        channel_name = (
            ChannelName.from_string(sanitize_fs_name(entry_author))
            if entry_author
            else default_channel_name
        )
        pub_date = _parse_atom_published_datetime(entry.findtext(f"{_ATOM_NS}published"))

        items.append(
            DiscoveredMediaItem(
                content_id=cid,
                title=title,
                published_at=pub_date,
                media_url=media_url,
                channel_name=channel_name,
            )
        )

    return items


def is_rss_feed_window_complete(
    items: list[DiscoveredMediaItem],
    query: ChannelFeedQuery,
    now: datetime | None = None,
) -> bool:
    """Verify whether the 15-item RSS window completely covers the requested query."""
    if not items:
        return False
    if len(items) < YOUTUBE_RSS_MAX_ENTRIES or query.max_videos <= YOUTUBE_RSS_MAX_ENTRIES:
        return True

    resolved_now = now if now is not None else datetime.now(UTC)
    if resolved_now.tzinfo is None:
        resolved_now = resolved_now.replace(tzinfo=UTC)
    cutoff = resolved_now - timedelta(days=query.lookback_days)

    oldest_published = min(
        item.published_at
        if item.published_at.tzinfo is not None
        else item.published_at.replace(tzinfo=UTC)
        for item in items
    )
    return oldest_published < cutoff


def discover_channel_feed_items(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
    fetch_rss_xml: Callable[[str], str] | None = None,
    enable_rss_fast_path: bool = True,
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel via Atom RSS fast-path or yt-dlp."""
    if enable_rss_fast_path and fetch_rss_xml is not None:
        rss_url = resolve_youtube_rss_url(query.channel_url)
        if rss_url is not None:
            try:
                xml_payload = fetch_rss_xml(rss_url)
                rss_items = parse_youtube_atom_feed(xml_payload, sanitize_fs_name)
                if is_rss_feed_window_complete(rss_items, query):
                    logger.debug(
                        "YouTube Atom RSS fast-path succeeded",
                        rss_url=rss_url,
                        entries_count=len(rss_items),
                    )
                    return rss_items[: query.max_videos]
                logger.debug(
                    "YouTube Atom RSS window incomplete; falling back to yt-dlp",
                    rss_url=rss_url,
                    entries_count=len(rss_items),
                    max_videos=query.max_videos,
                    lookback_days=query.lookback_days,
                )
            except Exception as exc:  # noqa: BLE001 - Graceful fallback to yt-dlp
                logger.warning(
                    "YouTube Atom RSS fast-path failed (%s); falling back to yt-dlp.",
                    exc,
                    rss_url=rss_url,
                )

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
        import yt_dlp

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
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if channel_url:
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None
