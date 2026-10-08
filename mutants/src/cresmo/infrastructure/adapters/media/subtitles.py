"""Subtitle and caption utilities for native media ingestion.

Conforms to:
- ADR-004: Native Media Ingestion Decommissioning
- SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

import yt_dlp.plugins

logger = logging.getLogger(__name__)

SENTENCES_PER_PARAGRAPH_THRESHOLD: int = 4
ISO_DATE_COMPACT_LENGTH: int = 8
_ILLEGAL_FS_CHARS = re.compile(r'[\\/*?:"<>|%]')


def ensure_yt_dlp_plugins_loaded() -> None:
    """Eagerly load yt-dlp plugins to prevent background thread importlib lock deadlocks."""
    try:
        yt_dlp.plugins.load_all_plugins()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to load yt-dlp plugins: %s", exc)


def reconstruct_json3_paragraphs(data: dict[str, Any]) -> str:
    """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
    events: list[dict[str, Any]] = data.get("events", [])
    paragraphs: list[str] = []
    current_sentences: list[str] = []

    for event in events:
        if "segs" in event and not event.get("aAppend"):
            seg_text = "".join(str(s.get("utf8", "")) for s in event["segs"]).strip()
            if seg_text and seg_text != "\n":
                current_sentences.append(seg_text)
                if len(current_sentences) >= SENTENCES_PER_PARAGRAPH_THRESHOLD or seg_text.endswith(
                    (".", "!", "?")
                ):
                    paragraphs.append(" ".join(current_sentences))
                    current_sentences = []

    if current_sentences:
        paragraphs.append(" ".join(current_sentences))

    return "\n\n".join(paragraphs).strip()


def is_native_subtitle_url(url: str | None) -> bool:
    """Validate that subtitle URL is native and not an on-the-fly machine translation."""
    if not url:
        return False
    # Strictly reject on-the-fly machine-translated subtitles that cause YouTube HTTP 429
    return "tlang=" not in url


def find_matching_format_url(formats: list[dict[str, Any]]) -> str | None:
    """Scan subtitle format candidates for valid non-translated json3 track."""
    for fmt in formats:
        url = fmt.get("url")
        if fmt.get("ext") == "json3" and is_native_subtitle_url(url):
            return str(url)
    return None


def find_in_manual_subtitles(
    subtitles: dict[str, list[dict[str, Any]]],
    ordered_langs: list[str],
) -> str | None:
    """Search in manual subtitles with prioritized language order, then fallback to any."""
    for lang in ordered_langs:
        if lang in subtitles:
            url = find_matching_format_url(subtitles[lang])
            if url:
                return url
    for formats in subtitles.values():
        url = find_matching_format_url(formats)
        if url:
            return url
    return None


def find_in_auto_captions(
    auto_captions: dict[str, list[dict[str, Any]]],
    ordered_langs: list[str],
    is_pt_video: bool,
) -> str | None:
    """Search in automatic captions prioritizing explicit original tracks (*-orig)."""
    orig_keys = [k for k in auto_captions if k.endswith("-orig") or k == "orig"]
    orig_keys.sort(
        key=lambda k: 0 if (is_pt_video and "pt" in k) or (not is_pt_video and "en" in k) else 1
    )
    for lang in orig_keys:
        url = find_matching_format_url(auto_captions[lang])
        if url:
            return url
    for lang in ordered_langs:
        if lang in auto_captions:
            url = find_matching_format_url(auto_captions[lang])
            if url:
                return url
    for formats in auto_captions.values():
        url = find_matching_format_url(formats)
        if url:
            return url
    return None


def find_native_subtitle_url(info: Mapping[str, Any]) -> str | None:
    """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
    subtitles: dict[str, list[dict[str, Any]]] = info.get("subtitles") or {}
    auto_captions: dict[str, list[dict[str, Any]]] = info.get("automatic_captions") or {}

    video_lang = str(info.get("language") or "").lower()
    is_pt_video = video_lang.startswith("pt")

    if is_pt_video:
        ordered_langs = ["pt-orig", "pt-BR", "pt", "pt-PT", "en-orig", "en", "en-US"]
    else:
        ordered_langs = ["en-orig", "en", "en-US", "pt-orig", "pt-BR", "pt", "pt-PT"]

    return find_in_manual_subtitles(subtitles, ordered_langs) or find_in_auto_captions(
        auto_captions, ordered_langs, is_pt_video
    )


def parse_upload_date(raw_date: Any) -> date | None:
    """Parse yt-dlp upload_date string (YYYYMMDD) into UTC date at ACL boundary."""
    if not raw_date:
        return None
    date_str = str(raw_date).strip()
    if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC).date()
        except ValueError:
            return None
    return None


def parse_published_datetime(raw_date: Any) -> datetime:
    """Parse yt-dlp upload_date string (YYYYMMDD) into UTC datetime at ACL boundary."""
    if not raw_date:
        return datetime.now(UTC)
    date_str = str(raw_date).strip()
    if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC)
        except ValueError:
            return datetime.now(UTC)
    return datetime.now(UTC)
