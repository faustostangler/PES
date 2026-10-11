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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_discover_channel_feed_items__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_discover_channel_feed_items__mutmut)
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


def x_discover_channel_feed_items__mutmut_orig(
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


def x_discover_channel_feed_items__mutmut_1(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = None
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


def x_discover_channel_feed_items__mutmut_2(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = normalize_to_uploads_playlist_url(None)
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


def x_discover_channel_feed_items__mutmut_3(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = normalize_to_uploads_playlist_url(query.channel_url)
    opts = None
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


def x_discover_channel_feed_items__mutmut_4(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = normalize_to_uploads_playlist_url(query.channel_url)
    opts = dict(None)
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


def x_discover_channel_feed_items__mutmut_5(
    query: ChannelFeedQuery,
    ydl_opts: dict[str, Any],
    handle_error: Callable[[Exception], None],
    sanitize_fs_name: Callable[[str], str],
) -> list[DiscoveredMediaItem]:
    """Discover media items from a YouTube channel or playlist feed via yt-dlp."""
    target_url = normalize_to_uploads_playlist_url(query.channel_url)
    opts = dict(ydl_opts)
    opts.update(
        None
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


def x_discover_channel_feed_items__mutmut_6(
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
            "XXextract_flatXX": True,
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


def x_discover_channel_feed_items__mutmut_7(
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
            "EXTRACT_FLAT": True,
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


def x_discover_channel_feed_items__mutmut_8(
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
            "extract_flat": False,
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


def x_discover_channel_feed_items__mutmut_9(
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
            "XXplaylistendXX": query.max_videos,
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


def x_discover_channel_feed_items__mutmut_10(
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
            "PLAYLISTEND": query.max_videos,
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


def x_discover_channel_feed_items__mutmut_11(
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
            "XXquietXX": True,
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


def x_discover_channel_feed_items__mutmut_12(
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
            "QUIET": True,
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


def x_discover_channel_feed_items__mutmut_13(
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
            "quiet": False,
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


def x_discover_channel_feed_items__mutmut_14(
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
            "XXno_warningsXX": True,
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


def x_discover_channel_feed_items__mutmut_15(
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
            "NO_WARNINGS": True,
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


def x_discover_channel_feed_items__mutmut_16(
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
            "no_warnings": False,
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


def x_discover_channel_feed_items__mutmut_17(
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
        with yt_dlp.YoutubeDL(None) as ydl:
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


def x_discover_channel_feed_items__mutmut_18(
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
        with yt_dlp.YoutubeDL(cast(None, opts)) as ydl:
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


def x_discover_channel_feed_items__mutmut_19(
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
        with yt_dlp.YoutubeDL(cast(Any, None)) as ydl:
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


def x_discover_channel_feed_items__mutmut_20(
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
        with yt_dlp.YoutubeDL(cast(opts)) as ydl:
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


def x_discover_channel_feed_items__mutmut_21(
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
        with yt_dlp.YoutubeDL(cast(Any, )) as ydl:
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


def x_discover_channel_feed_items__mutmut_22(
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
            info = None
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


def x_discover_channel_feed_items__mutmut_23(
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
            info = ydl.extract_info(None, download=False)
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


def x_discover_channel_feed_items__mutmut_24(
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
            info = ydl.extract_info(target_url, download=None)
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


def x_discover_channel_feed_items__mutmut_25(
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
            info = ydl.extract_info(download=False)
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


def x_discover_channel_feed_items__mutmut_26(
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
            info = ydl.extract_info(target_url, )
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


def x_discover_channel_feed_items__mutmut_27(
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
            info = ydl.extract_info(target_url, download=True)
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


def x_discover_channel_feed_items__mutmut_28(
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
            if (not info or not info.get("entries")) or target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_29(
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
            if (not info and not info.get("entries")) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_30(
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
            if (info or not info.get("entries")) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_31(
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
            if (not info or info.get("entries")) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_32(
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
            if (not info or not info.get(None)) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_33(
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
            if (not info or not info.get("XXentriesXX")) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_34(
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
            if (not info or not info.get("ENTRIES")) and target_url != query.channel_url:
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


def x_discover_channel_feed_items__mutmut_35(
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
            if (not info or not info.get("entries")) and target_url == query.channel_url:
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


def x_discover_channel_feed_items__mutmut_36(
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
                info = None
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


def x_discover_channel_feed_items__mutmut_37(
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
                info = ydl.extract_info(None, download=False)
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


def x_discover_channel_feed_items__mutmut_38(
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
                info = ydl.extract_info(query.channel_url, download=None)
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


def x_discover_channel_feed_items__mutmut_39(
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
                info = ydl.extract_info(download=False)
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


def x_discover_channel_feed_items__mutmut_40(
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
                info = ydl.extract_info(query.channel_url, )
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


def x_discover_channel_feed_items__mutmut_41(
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
                info = ydl.extract_info(query.channel_url, download=True)
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


def x_discover_channel_feed_items__mutmut_42(
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
        handle_error(None)
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


def x_discover_channel_feed_items__mutmut_43(
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

    if info:
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


def x_discover_channel_feed_items__mutmut_44(
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

    entries = None
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


def x_discover_channel_feed_items__mutmut_45(
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

    entries = info.get("entries") and []
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


def x_discover_channel_feed_items__mutmut_46(
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

    entries = info.get(None) or []
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


def x_discover_channel_feed_items__mutmut_47(
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

    entries = info.get("XXentriesXX") or []
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


def x_discover_channel_feed_items__mutmut_48(
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

    entries = info.get("ENTRIES") or []
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


def x_discover_channel_feed_items__mutmut_49(
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
    channel_title = None
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


def x_discover_channel_feed_items__mutmut_50(
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
        None
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


def x_discover_channel_feed_items__mutmut_51(
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
        str(None)
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


def x_discover_channel_feed_items__mutmut_52(
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
        str(info.get("title") or info.get("uploader") and "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_53(
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
        str(info.get("title") and info.get("uploader") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_54(
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
        str(info.get(None) or info.get("uploader") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_55(
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
        str(info.get("XXtitleXX") or info.get("uploader") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_56(
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
        str(info.get("TITLE") or info.get("uploader") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_57(
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
        str(info.get("title") or info.get(None) or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_58(
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
        str(info.get("title") or info.get("XXuploaderXX") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_59(
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
        str(info.get("title") or info.get("UPLOADER") or "Unknown_Channel")
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


def x_discover_channel_feed_items__mutmut_60(
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
        str(info.get("title") or info.get("uploader") or "XXUnknown_ChannelXX")
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


def x_discover_channel_feed_items__mutmut_61(
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
        str(info.get("title") or info.get("uploader") or "unknown_channel")
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


def x_discover_channel_feed_items__mutmut_62(
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
        str(info.get("title") or info.get("uploader") or "UNKNOWN_CHANNEL")
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


def x_discover_channel_feed_items__mutmut_63(
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
    items: list[DiscoveredMediaItem] = None

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


def x_discover_channel_feed_items__mutmut_64(
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
        if not entry and not isinstance(entry, dict):
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


def x_discover_channel_feed_items__mutmut_65(
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
        if entry or not isinstance(entry, dict):
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


def x_discover_channel_feed_items__mutmut_66(
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
        if not entry or isinstance(entry, dict):
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


def x_discover_channel_feed_items__mutmut_67(
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
            break

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


def x_discover_channel_feed_items__mutmut_68(
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

        raw_vid = None
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


def x_discover_channel_feed_items__mutmut_69(
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

        raw_vid = str(None).strip()
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


def x_discover_channel_feed_items__mutmut_70(
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

        raw_vid = str(entry.get("id") and "").strip()
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


def x_discover_channel_feed_items__mutmut_71(
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

        raw_vid = str(entry.get(None) or "").strip()
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


def x_discover_channel_feed_items__mutmut_72(
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

        raw_vid = str(entry.get("XXidXX") or "").strip()
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


def x_discover_channel_feed_items__mutmut_73(
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

        raw_vid = str(entry.get("ID") or "").strip()
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


def x_discover_channel_feed_items__mutmut_74(
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

        raw_vid = str(entry.get("id") or "XXXX").strip()
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


def x_discover_channel_feed_items__mutmut_75(
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
        title = None
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


def x_discover_channel_feed_items__mutmut_76(
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
        title = str(None).strip()
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


def x_discover_channel_feed_items__mutmut_77(
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
        title = str(entry.get("title") and "").strip()
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


def x_discover_channel_feed_items__mutmut_78(
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
        title = str(entry.get(None) or "").strip()
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


def x_discover_channel_feed_items__mutmut_79(
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
        title = str(entry.get("XXtitleXX") or "").strip()
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


def x_discover_channel_feed_items__mutmut_80(
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
        title = str(entry.get("TITLE") or "").strip()
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


def x_discover_channel_feed_items__mutmut_81(
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
        title = str(entry.get("title") or "XXXX").strip()
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


def x_discover_channel_feed_items__mutmut_82(
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
        if not raw_vid and not title:
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


def x_discover_channel_feed_items__mutmut_83(
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
        if raw_vid or not title:
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


def x_discover_channel_feed_items__mutmut_84(
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
        if not raw_vid or title:
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


def x_discover_channel_feed_items__mutmut_85(
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
            break

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


def x_discover_channel_feed_items__mutmut_86(
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

        cid = None
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


def x_discover_channel_feed_items__mutmut_87(
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

        cid = ContentId.extract_from_text(raw_vid) and ContentId.from_url_or_token(raw_vid)
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


def x_discover_channel_feed_items__mutmut_88(
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

        cid = ContentId.extract_from_text(None) or ContentId.from_url_or_token(raw_vid)
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


def x_discover_channel_feed_items__mutmut_89(
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

        cid = ContentId.extract_from_text(raw_vid) or ContentId.from_url_or_token(None)
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


def x_discover_channel_feed_items__mutmut_90(
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
        url = None
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


def x_discover_channel_feed_items__mutmut_91(
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
        url = str(None).strip()
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


def x_discover_channel_feed_items__mutmut_92(
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
        url = str(entry.get("url") and f"https://www.youtube.com/watch?v={cid.value}").strip()
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


def x_discover_channel_feed_items__mutmut_93(
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
        url = str(entry.get(None) or f"https://www.youtube.com/watch?v={cid.value}").strip()
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


def x_discover_channel_feed_items__mutmut_94(
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
        url = str(entry.get("XXurlXX") or f"https://www.youtube.com/watch?v={cid.value}").strip()
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


def x_discover_channel_feed_items__mutmut_95(
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
        url = str(entry.get("URL") or f"https://www.youtube.com/watch?v={cid.value}").strip()
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


def x_discover_channel_feed_items__mutmut_96(
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
        raw_channel = None
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


def x_discover_channel_feed_items__mutmut_97(
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
        raw_channel = str(None)
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


def x_discover_channel_feed_items__mutmut_98(
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
        raw_channel = str(entry.get("channel") or entry.get("uploader") and channel_title)
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


def x_discover_channel_feed_items__mutmut_99(
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
        raw_channel = str(entry.get("channel") and entry.get("uploader") or channel_title)
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


def x_discover_channel_feed_items__mutmut_100(
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
        raw_channel = str(entry.get(None) or entry.get("uploader") or channel_title)
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


def x_discover_channel_feed_items__mutmut_101(
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
        raw_channel = str(entry.get("XXchannelXX") or entry.get("uploader") or channel_title)
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


def x_discover_channel_feed_items__mutmut_102(
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
        raw_channel = str(entry.get("CHANNEL") or entry.get("uploader") or channel_title)
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


def x_discover_channel_feed_items__mutmut_103(
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
        raw_channel = str(entry.get("channel") or entry.get(None) or channel_title)
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


def x_discover_channel_feed_items__mutmut_104(
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
        raw_channel = str(entry.get("channel") or entry.get("XXuploaderXX") or channel_title)
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


def x_discover_channel_feed_items__mutmut_105(
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
        raw_channel = str(entry.get("channel") or entry.get("UPLOADER") or channel_title)
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


def x_discover_channel_feed_items__mutmut_106(
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
        channel_name = None

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


def x_discover_channel_feed_items__mutmut_107(
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
        channel_name = ChannelName.from_string(None)

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


def x_discover_channel_feed_items__mutmut_108(
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
        channel_name = ChannelName.from_string(sanitize_fs_name(None))

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


def x_discover_channel_feed_items__mutmut_109(
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

        pub_date = None

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


def x_discover_channel_feed_items__mutmut_110(
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

        pub_date = parse_published_datetime(None)

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


def x_discover_channel_feed_items__mutmut_111(
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

        pub_date = parse_published_datetime(entry.get(None))

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


def x_discover_channel_feed_items__mutmut_112(
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

        pub_date = parse_published_datetime(entry.get("XXupload_dateXX"))

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


def x_discover_channel_feed_items__mutmut_113(
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

        pub_date = parse_published_datetime(entry.get("UPLOAD_DATE"))

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


def x_discover_channel_feed_items__mutmut_114(
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
            None
        )

    return items


def x_discover_channel_feed_items__mutmut_115(
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
                content_id=None,
                title=title,
                published_at=pub_date,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_116(
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
                title=None,
                published_at=pub_date,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_117(
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
                published_at=None,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_118(
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
                media_url=None,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_119(
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
                channel_name=None,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_120(
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
                title=title,
                published_at=pub_date,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_121(
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
                published_at=pub_date,
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_122(
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
                media_url=url,
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_123(
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
                channel_name=channel_name,
            )
        )

    return items


def x_discover_channel_feed_items__mutmut_124(
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
                )
        )

    return items

mutants_x_discover_channel_feed_items__mutmut['_mutmut_orig'] = x_discover_channel_feed_items__mutmut_orig # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_1'] = x_discover_channel_feed_items__mutmut_1 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_2'] = x_discover_channel_feed_items__mutmut_2 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_3'] = x_discover_channel_feed_items__mutmut_3 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_4'] = x_discover_channel_feed_items__mutmut_4 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_5'] = x_discover_channel_feed_items__mutmut_5 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_6'] = x_discover_channel_feed_items__mutmut_6 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_7'] = x_discover_channel_feed_items__mutmut_7 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_8'] = x_discover_channel_feed_items__mutmut_8 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_9'] = x_discover_channel_feed_items__mutmut_9 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_10'] = x_discover_channel_feed_items__mutmut_10 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_11'] = x_discover_channel_feed_items__mutmut_11 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_12'] = x_discover_channel_feed_items__mutmut_12 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_13'] = x_discover_channel_feed_items__mutmut_13 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_14'] = x_discover_channel_feed_items__mutmut_14 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_15'] = x_discover_channel_feed_items__mutmut_15 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_16'] = x_discover_channel_feed_items__mutmut_16 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_17'] = x_discover_channel_feed_items__mutmut_17 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_18'] = x_discover_channel_feed_items__mutmut_18 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_19'] = x_discover_channel_feed_items__mutmut_19 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_20'] = x_discover_channel_feed_items__mutmut_20 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_21'] = x_discover_channel_feed_items__mutmut_21 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_22'] = x_discover_channel_feed_items__mutmut_22 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_23'] = x_discover_channel_feed_items__mutmut_23 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_24'] = x_discover_channel_feed_items__mutmut_24 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_25'] = x_discover_channel_feed_items__mutmut_25 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_26'] = x_discover_channel_feed_items__mutmut_26 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_27'] = x_discover_channel_feed_items__mutmut_27 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_28'] = x_discover_channel_feed_items__mutmut_28 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_29'] = x_discover_channel_feed_items__mutmut_29 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_30'] = x_discover_channel_feed_items__mutmut_30 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_31'] = x_discover_channel_feed_items__mutmut_31 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_32'] = x_discover_channel_feed_items__mutmut_32 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_33'] = x_discover_channel_feed_items__mutmut_33 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_34'] = x_discover_channel_feed_items__mutmut_34 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_35'] = x_discover_channel_feed_items__mutmut_35 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_36'] = x_discover_channel_feed_items__mutmut_36 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_37'] = x_discover_channel_feed_items__mutmut_37 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_38'] = x_discover_channel_feed_items__mutmut_38 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_39'] = x_discover_channel_feed_items__mutmut_39 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_40'] = x_discover_channel_feed_items__mutmut_40 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_41'] = x_discover_channel_feed_items__mutmut_41 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_42'] = x_discover_channel_feed_items__mutmut_42 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_43'] = x_discover_channel_feed_items__mutmut_43 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_44'] = x_discover_channel_feed_items__mutmut_44 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_45'] = x_discover_channel_feed_items__mutmut_45 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_46'] = x_discover_channel_feed_items__mutmut_46 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_47'] = x_discover_channel_feed_items__mutmut_47 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_48'] = x_discover_channel_feed_items__mutmut_48 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_49'] = x_discover_channel_feed_items__mutmut_49 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_50'] = x_discover_channel_feed_items__mutmut_50 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_51'] = x_discover_channel_feed_items__mutmut_51 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_52'] = x_discover_channel_feed_items__mutmut_52 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_53'] = x_discover_channel_feed_items__mutmut_53 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_54'] = x_discover_channel_feed_items__mutmut_54 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_55'] = x_discover_channel_feed_items__mutmut_55 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_56'] = x_discover_channel_feed_items__mutmut_56 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_57'] = x_discover_channel_feed_items__mutmut_57 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_58'] = x_discover_channel_feed_items__mutmut_58 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_59'] = x_discover_channel_feed_items__mutmut_59 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_60'] = x_discover_channel_feed_items__mutmut_60 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_61'] = x_discover_channel_feed_items__mutmut_61 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_62'] = x_discover_channel_feed_items__mutmut_62 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_63'] = x_discover_channel_feed_items__mutmut_63 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_64'] = x_discover_channel_feed_items__mutmut_64 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_65'] = x_discover_channel_feed_items__mutmut_65 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_66'] = x_discover_channel_feed_items__mutmut_66 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_67'] = x_discover_channel_feed_items__mutmut_67 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_68'] = x_discover_channel_feed_items__mutmut_68 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_69'] = x_discover_channel_feed_items__mutmut_69 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_70'] = x_discover_channel_feed_items__mutmut_70 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_71'] = x_discover_channel_feed_items__mutmut_71 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_72'] = x_discover_channel_feed_items__mutmut_72 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_73'] = x_discover_channel_feed_items__mutmut_73 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_74'] = x_discover_channel_feed_items__mutmut_74 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_75'] = x_discover_channel_feed_items__mutmut_75 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_76'] = x_discover_channel_feed_items__mutmut_76 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_77'] = x_discover_channel_feed_items__mutmut_77 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_78'] = x_discover_channel_feed_items__mutmut_78 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_79'] = x_discover_channel_feed_items__mutmut_79 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_80'] = x_discover_channel_feed_items__mutmut_80 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_81'] = x_discover_channel_feed_items__mutmut_81 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_82'] = x_discover_channel_feed_items__mutmut_82 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_83'] = x_discover_channel_feed_items__mutmut_83 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_84'] = x_discover_channel_feed_items__mutmut_84 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_85'] = x_discover_channel_feed_items__mutmut_85 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_86'] = x_discover_channel_feed_items__mutmut_86 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_87'] = x_discover_channel_feed_items__mutmut_87 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_88'] = x_discover_channel_feed_items__mutmut_88 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_89'] = x_discover_channel_feed_items__mutmut_89 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_90'] = x_discover_channel_feed_items__mutmut_90 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_91'] = x_discover_channel_feed_items__mutmut_91 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_92'] = x_discover_channel_feed_items__mutmut_92 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_93'] = x_discover_channel_feed_items__mutmut_93 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_94'] = x_discover_channel_feed_items__mutmut_94 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_95'] = x_discover_channel_feed_items__mutmut_95 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_96'] = x_discover_channel_feed_items__mutmut_96 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_97'] = x_discover_channel_feed_items__mutmut_97 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_98'] = x_discover_channel_feed_items__mutmut_98 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_99'] = x_discover_channel_feed_items__mutmut_99 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_100'] = x_discover_channel_feed_items__mutmut_100 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_101'] = x_discover_channel_feed_items__mutmut_101 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_102'] = x_discover_channel_feed_items__mutmut_102 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_103'] = x_discover_channel_feed_items__mutmut_103 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_104'] = x_discover_channel_feed_items__mutmut_104 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_105'] = x_discover_channel_feed_items__mutmut_105 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_106'] = x_discover_channel_feed_items__mutmut_106 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_107'] = x_discover_channel_feed_items__mutmut_107 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_108'] = x_discover_channel_feed_items__mutmut_108 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_109'] = x_discover_channel_feed_items__mutmut_109 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_110'] = x_discover_channel_feed_items__mutmut_110 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_111'] = x_discover_channel_feed_items__mutmut_111 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_112'] = x_discover_channel_feed_items__mutmut_112 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_113'] = x_discover_channel_feed_items__mutmut_113 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_114'] = x_discover_channel_feed_items__mutmut_114 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_115'] = x_discover_channel_feed_items__mutmut_115 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_116'] = x_discover_channel_feed_items__mutmut_116 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_117'] = x_discover_channel_feed_items__mutmut_117 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_118'] = x_discover_channel_feed_items__mutmut_118 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_119'] = x_discover_channel_feed_items__mutmut_119 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_120'] = x_discover_channel_feed_items__mutmut_120 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_121'] = x_discover_channel_feed_items__mutmut_121 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_122'] = x_discover_channel_feed_items__mutmut_122 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_123'] = x_discover_channel_feed_items__mutmut_123 # type: ignore # mutmut generated
mutants_x_discover_channel_feed_items__mutmut['x_discover_channel_feed_items__mutmut_124'] = x_discover_channel_feed_items__mutmut_124 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_extract_channel_url_from_info__mutmut)
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


def x_extract_channel_url_from_info__mutmut_orig(info: dict[str, Any] | None) -> str | None:
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


def x_extract_channel_url_from_info__mutmut_1(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info and not isinstance(info, dict):
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


def x_extract_channel_url_from_info__mutmut_2(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if info or not isinstance(info, dict):
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


def x_extract_channel_url_from_info__mutmut_3(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or isinstance(info, dict):
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


def x_extract_channel_url_from_info__mutmut_4(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = None
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


def x_extract_channel_url_from_info__mutmut_5(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") and info.get("uploader_id")
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


def x_extract_channel_url_from_info__mutmut_6(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get(None) or info.get("uploader_id")
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


def x_extract_channel_url_from_info__mutmut_7(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("XXchannel_idXX") or info.get("uploader_id")
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


def x_extract_channel_url_from_info__mutmut_8(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("CHANNEL_ID") or info.get("uploader_id")
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


def x_extract_channel_url_from_info__mutmut_9(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get(None)
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


def x_extract_channel_url_from_info__mutmut_10(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("XXuploader_idXX")
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


def x_extract_channel_url_from_info__mutmut_11(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("UPLOADER_ID")
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


def x_extract_channel_url_from_info__mutmut_12(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = None
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


def x_extract_channel_url_from_info__mutmut_13(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(None)
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


def x_extract_channel_url_from_info__mutmut_14(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(None).strip())
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


def x_extract_channel_url_from_info__mutmut_15(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch or ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_16(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(None)

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_17(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(None).strip())

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_18(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = None
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_19(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") and info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_20(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get(None) or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_21(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("XXchannel_urlXX") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_22(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("CHANNEL_URL") or info.get("uploader_url")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_23(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get(None)
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_24(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get("XXuploader_urlXX")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_25(info: dict[str, Any] | None) -> str | None:
    """Resolve YouTube channel uploads playlist URL from yt-dlp info dictionary."""
    if not info or not isinstance(info, dict):
        return None

    channel_id = info.get("channel_id") or info.get("uploader_id")
    if channel_id:
        ch = ChannelId.extract_from_text(str(channel_id).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_id).strip())

    channel_url = info.get("channel_url") or info.get("UPLOADER_URL")
    if channel_url:
        ch = ChannelId.extract_from_text(str(channel_url).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_26(info: dict[str, Any] | None) -> str | None:
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
        ch = None
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_27(info: dict[str, Any] | None) -> str | None:
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
        ch = ChannelId.extract_from_text(None)
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_28(info: dict[str, Any] | None) -> str | None:
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
        ch = ChannelId.extract_from_text(str(None).strip())
        if ch and ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_29(info: dict[str, Any] | None) -> str | None:
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
        if ch or ch.uploads_playlist_url:
            return ch.uploads_playlist_url
        return normalize_to_uploads_playlist_url(str(channel_url).strip())

    return None


def x_extract_channel_url_from_info__mutmut_30(info: dict[str, Any] | None) -> str | None:
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
        return normalize_to_uploads_playlist_url(None)

    return None


def x_extract_channel_url_from_info__mutmut_31(info: dict[str, Any] | None) -> str | None:
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
        return normalize_to_uploads_playlist_url(str(None).strip())

    return None

mutants_x_extract_channel_url_from_info__mutmut['_mutmut_orig'] = x_extract_channel_url_from_info__mutmut_orig # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_1'] = x_extract_channel_url_from_info__mutmut_1 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_2'] = x_extract_channel_url_from_info__mutmut_2 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_3'] = x_extract_channel_url_from_info__mutmut_3 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_4'] = x_extract_channel_url_from_info__mutmut_4 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_5'] = x_extract_channel_url_from_info__mutmut_5 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_6'] = x_extract_channel_url_from_info__mutmut_6 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_7'] = x_extract_channel_url_from_info__mutmut_7 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_8'] = x_extract_channel_url_from_info__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_9'] = x_extract_channel_url_from_info__mutmut_9 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_10'] = x_extract_channel_url_from_info__mutmut_10 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_11'] = x_extract_channel_url_from_info__mutmut_11 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_12'] = x_extract_channel_url_from_info__mutmut_12 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_13'] = x_extract_channel_url_from_info__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_14'] = x_extract_channel_url_from_info__mutmut_14 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_15'] = x_extract_channel_url_from_info__mutmut_15 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_16'] = x_extract_channel_url_from_info__mutmut_16 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_17'] = x_extract_channel_url_from_info__mutmut_17 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_18'] = x_extract_channel_url_from_info__mutmut_18 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_19'] = x_extract_channel_url_from_info__mutmut_19 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_20'] = x_extract_channel_url_from_info__mutmut_20 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_21'] = x_extract_channel_url_from_info__mutmut_21 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_22'] = x_extract_channel_url_from_info__mutmut_22 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_23'] = x_extract_channel_url_from_info__mutmut_23 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_24'] = x_extract_channel_url_from_info__mutmut_24 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_25'] = x_extract_channel_url_from_info__mutmut_25 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_26'] = x_extract_channel_url_from_info__mutmut_26 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_27'] = x_extract_channel_url_from_info__mutmut_27 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_28'] = x_extract_channel_url_from_info__mutmut_28 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_29'] = x_extract_channel_url_from_info__mutmut_29 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_30'] = x_extract_channel_url_from_info__mutmut_30 # type: ignore # mutmut generated
mutants_x_extract_channel_url_from_info__mutmut['x_extract_channel_url_from_info__mutmut_31'] = x_extract_channel_url_from_info__mutmut_31 # type: ignore # mutmut generated
