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
_YOUTUBE_FEED_CHANNEL_URL_PREFIX: Final[str] = (
    "https://www.youtube.com/feeds/videos.xml?channel_id="
)
_YOUTUBE_FEED_PLAYLIST_URL_PREFIX: Final[str] = (
    "https://www.youtube.com/feeds/videos.xml?playlist_id="
)
_YOUTUBE_WATCH_URL_PREFIX: Final[str] = "https://www.youtube.com/watch?v="
_UPLOADS_PLAYLIST_PREFIX: Final[str] = "UU"
_CANONICAL_CHANNEL_ID_PREFIX: Final[str] = "UC"
_UPLOADS_PREFIX_OFFSET: Final[int] = 2
_UNKNOWN_CHANNEL_NAME: Final[str] = "Unknown_Channel"
_ATOM_LINK_REL_ATTR: Final[str] = "rel"
_ATOM_LINK_HREF_ATTR: Final[str] = "href"
_ATOM_LINK_REL_ALTERNATE: Final[str] = "alternate"
_ATOM_TAG_TITLE: Final[str] = f"{_ATOM_NS}title"
_ATOM_TAG_AUTHOR_NAME: Final[str] = f"{_ATOM_NS}author/{_ATOM_NS}name"
_ATOM_TAG_ENTRY: Final[str] = f"{_ATOM_NS}entry"
_ATOM_TAG_LINK: Final[str] = f"{_ATOM_NS}link"
_ATOM_TAG_PUBLISHED: Final[str] = f"{_ATOM_NS}published"
_YT_TAG_VIDEO_ID: Final[str] = f"{_YT_NS}videoId"
_KEY_ID: Final[str] = "id"
_KEY_TITLE: Final[str] = "title"
_KEY_URL: Final[str] = "url"
_KEY_ENTRIES: Final[str] = "entries"
_KEY_UPLOADER: Final[str] = "uploader"
_KEY_CHANNEL: Final[str] = "channel"
_KEY_UPLOAD_DATE: Final[str] = "upload_date"
_KEY_CHANNEL_ID: Final[str] = "channel_id"
_KEY_UPLOADER_ID: Final[str] = "uploader_id"
_KEY_CHANNEL_URL: Final[str] = "channel_url"
_KEY_UPLOADER_URL: Final[str] = "uploader_url"
_YTDLP_OPT_EXTRACT_FLAT: Final[str] = "extract_flat"
_YTDLP_OPT_PLAYLISTEND: Final[str] = "playlistend"
_YTDLP_OPT_QUIET: Final[str] = "quiet"
_YTDLP_OPT_NO_WARNINGS: Final[str] = "no_warnings"


def resolve_youtube_rss_url(channel_url: str) -> str | None:
    """Resolve canonical YouTube channel/playlist URL to Atom RSS feed URL if possible."""
    cleaned = channel_url.strip()
    if not cleaned:
        return None

    channel_id = ChannelId.extract_from_text(cleaned)
    if channel_id and channel_id.is_youtube_canonical:
        return f"{_YOUTUBE_FEED_CHANNEL_URL_PREFIX}{channel_id.value}"

    playlist_match = _PLAYLIST_ID_REGEX.search(cleaned)
    if playlist_match:
        list_id = playlist_match.group(1).strip()
        if (
            list_id.startswith(_UPLOADS_PLAYLIST_PREFIX)
            and len(list_id) >= MIN_CANONICAL_CHANNEL_ID_LENGTH
        ):
            canonical_channel_id = f"{_CANONICAL_CHANNEL_ID_PREFIX}{list_id[_UPLOADS_PREFIX_OFFSET:]}"
            return f"{_YOUTUBE_FEED_CHANNEL_URL_PREFIX}{canonical_channel_id}"
        return f"{_YOUTUBE_FEED_PLAYLIST_URL_PREFIX}{list_id}"

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
        root.findtext(_ATOM_TAG_TITLE)
        or root.findtext(_ATOM_TAG_AUTHOR_NAME)
        or _UNKNOWN_CHANNEL_NAME
    )
    default_channel_name = ChannelName.from_string(sanitize_fs_name(raw_feed_title))

    items: list[DiscoveredMediaItem] = []
    for entry in root.findall(_ATOM_TAG_ENTRY):
        raw_vid = (entry.findtext(_YT_TAG_VIDEO_ID) or "").strip()
        title = (entry.findtext(_ATOM_TAG_TITLE) or "").strip()
        if not raw_vid or not title:
            continue

        cid = ContentId.extract_from_text(raw_vid) or ContentId.from_url_or_token(raw_vid)

        media_url = ""
        for link in entry.findall(_ATOM_TAG_LINK):
            if link.attrib.get(_ATOM_LINK_REL_ATTR, _ATOM_LINK_REL_ALTERNATE) == _ATOM_LINK_REL_ALTERNATE:
                href = link.attrib.get(_ATOM_LINK_HREF_ATTR, "").strip()
                if href:
                    media_url = href
                    break
        if not media_url:
            media_url = f"{_YOUTUBE_WATCH_URL_PREFIX}{cid.value}"

        entry_author = (entry.findtext(_ATOM_TAG_AUTHOR_NAME) or "").strip()
        channel_name = (
            ChannelName.from_string(sanitize_fs_name(entry_author))
            if entry_author
            else default_channel_name
        )
        pub_date = _parse_atom_published_datetime(entry.findtext(_ATOM_TAG_PUBLISHED))

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
            _YTDLP_OPT_EXTRACT_FLAT: True,
            _YTDLP_OPT_PLAYLISTEND: query.max_videos,
            _YTDLP_OPT_QUIET: True,
            _YTDLP_OPT_NO_WARNINGS: True,
        }
    )

    try:
        import yt_dlp

        with yt_dlp.YoutubeDL(cast(Any, opts)) as ydl:
            info = ydl.extract_info(target_url, download=False)
            # Fallback to original channel_url if uploads playlist returned empty
            if (not info or not info.get(_KEY_ENTRIES)) and target_url != query.channel_url:
                info = ydl.extract_info(query.channel_url, download=False)
    except Exception as exc:  # noqa: BLE001
        handle_error(exc)
        return []

    if not info:
        return []

    entries = info.get(_KEY_ENTRIES) or []
    channel_title = sanitize_fs_name(
        str(info.get(_KEY_TITLE) or info.get(_KEY_UPLOADER) or _UNKNOWN_CHANNEL_NAME)
    )
    items: list[DiscoveredMediaItem] = []

    for entry in entries:
        if not entry or not isinstance(entry, dict):
            continue

        raw_vid = str(entry.get(_KEY_ID) or "").strip()
        title = str(entry.get(_KEY_TITLE) or "").strip()
        if not raw_vid or not title:
            continue

        cid = ContentId.extract_from_text(raw_vid) or ContentId.from_url_or_token(raw_vid)
        url = str(entry.get(_KEY_URL) or f"{_YOUTUBE_WATCH_URL_PREFIX}{cid.value}").strip()
        raw_channel = str(entry.get(_KEY_CHANNEL) or entry.get(_KEY_UPLOADER) or channel_title)
        channel_name = ChannelName.from_string(sanitize_fs_name(raw_channel))

        pub_date = parse_published_datetime(entry.get(_KEY_UPLOAD_DATE))

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

    channel_id = info.get(_KEY_CHANNEL_ID) or info.get(_KEY_UPLOADER_ID)
    if channel_id:
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get(_KEY_CHANNEL_URL) or info.get(_KEY_UPLOADER_URL)
    if channel_url:
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None
