"""Subtitle and caption utilities for native media ingestion.

Conforms to:
- ADR-004: Native Media Ingestion Decommissioning
- SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import re
import threading
from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any, Final

import structlog

logger = structlog.get_logger(__name__)

SENTENCES_PER_PARAGRAPH_THRESHOLD: Final[int] = 4
ISO_DATE_COMPACT_LENGTH: Final[int] = 8
_ILLEGAL_FS_CHARS = re.compile(r'[\\/*?:"<>|%]')
_PLUGINS_LOCK = threading.Lock()
_PLUGINS_LOADED = False
_PARAGRAPH_SEPARATOR: Final[str] = "\n\n"
_SENTENCE_JOINER: Final[str] = " "
_SENTENCE_END_PUNCTUATION: Final[tuple[str, ...]] = (".", "!", "?")
_TRANSLATED_SUBTITLE_QUERY_MARKER: Final[str] = "tlang="
_SUBTITLE_EXT_JSON3: Final[str] = "json3"
_AUTO_CAPTION_ORIG_SUFFIX: Final[str] = "-orig"
_AUTO_CAPTION_ORIG_KEY: Final[str] = "orig"
_LANG_CODE_PT: Final[str] = "pt"
_LANG_CODE_EN: Final[str] = "en"
_PT_PRIORITY_LANGS: Final[tuple[str, ...]] = (
    "pt-orig",
    "pt-BR",
    "pt",
    "pt-PT",
    "en-orig",
    "en",
    "en-US",
)
_DEFAULT_PRIORITY_LANGS: Final[tuple[str, ...]] = (
    "en-orig",
    "en",
    "en-US",
    "pt-orig",
    "pt-BR",
    "pt",
    "pt-PT",
)
_COMPACT_DATE_FORMAT: Final[str] = "%Y%m%d"
_KEY_EVENTS: Final[str] = "events"
_KEY_SEGS: Final[str] = "segs"
_KEY_A_APPEND: Final[str] = "aAppend"
_KEY_UTF8: Final[str] = "utf8"
_KEY_URL: Final[str] = "url"
_KEY_EXT: Final[str] = "ext"
_KEY_SUBTITLES: Final[str] = "subtitles"
_KEY_AUTOMATIC_CAPTIONS: Final[str] = "automatic_captions"
_KEY_LANGUAGE: Final[str] = "language"


def _reset_yt_dlp_plugins_cache() -> None:
    """Reset one-shot yt-dlp plugin loading cache (intended for hermetic unit tests)."""
    global _PLUGINS_LOADED
    with _PLUGINS_LOCK:
        _PLUGINS_LOADED = False


def ensure_yt_dlp_plugins_loaded() -> None:
    """Load yt-dlp plugins once per process to prevent importlib lock deadlocks (ADR-055/ADR-075)."""
    global _PLUGINS_LOADED
    if _PLUGINS_LOADED:
        return
    with _PLUGINS_LOCK:
        if _PLUGINS_LOADED:
            return
        try:
            import yt_dlp.plugins

            yt_dlp.plugins.load_all_plugins()
            _PLUGINS_LOADED = True
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to load yt-dlp plugins: %s", exc)


def reconstruct_json3_paragraphs(data: dict[str, Any]) -> str:
    """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
    events: list[dict[str, Any]] = data.get(_KEY_EVENTS, [])
    paragraphs: list[str] = []
    current_sentences: list[str] = []

    for event in events:
        if _KEY_SEGS in event and not event.get(_KEY_A_APPEND):
            seg_text = "".join(str(s.get(_KEY_UTF8, "")) for s in event[_KEY_SEGS]).strip()
            if seg_text:
                current_sentences.append(seg_text)
                if len(current_sentences) >= SENTENCES_PER_PARAGRAPH_THRESHOLD or seg_text.endswith(
                    _SENTENCE_END_PUNCTUATION
                ):
                    paragraphs.append(_SENTENCE_JOINER.join(current_sentences))
                    current_sentences = []

    if current_sentences:
        paragraphs.append(_SENTENCE_JOINER.join(current_sentences))

    return _PARAGRAPH_SEPARATOR.join(paragraphs).strip()


def is_native_subtitle_url(url: str | None) -> bool:
    """Validate that subtitle URL is native and not an on-the-fly machine translation."""
    if not url:
        return False
    # Strictly reject on-the-fly machine-translated subtitles that cause YouTube HTTP 429
    return _TRANSLATED_SUBTITLE_QUERY_MARKER not in url


def find_matching_format_url(formats: list[dict[str, Any]]) -> str | None:
    """Scan subtitle format candidates for valid non-translated json3 track."""
    for format_candidate in formats:
        url = format_candidate.get(_KEY_URL)
        if format_candidate.get(_KEY_EXT) == _SUBTITLE_EXT_JSON3 and is_native_subtitle_url(url):
            return str(url)
    return None


def find_in_manual_subtitles(
    subtitles: dict[str, list[dict[str, Any]]],
    ordered_langs: tuple[str, ...] | list[str],
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
    ordered_langs: tuple[str, ...] | list[str],
    is_pt_video: bool,
) -> str | None:
    """Search in automatic captions prioritizing explicit original tracks (*-orig)."""
    original_keys = [
        key
        for key in auto_captions
        if key.endswith(_AUTO_CAPTION_ORIG_SUFFIX) or key == _AUTO_CAPTION_ORIG_KEY
    ]
    original_keys.sort(
        key=lambda key: (
            0
            if (is_pt_video and _LANG_CODE_PT in key)
            or (not is_pt_video and _LANG_CODE_EN in key)
            else 1
        )
    )
    for lang in original_keys:
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
    subtitles: dict[str, list[dict[str, Any]]] = info.get(_KEY_SUBTITLES) or {}
    auto_captions: dict[str, list[dict[str, Any]]] = info.get(_KEY_AUTOMATIC_CAPTIONS) or {}

    video_lang = str(info.get(_KEY_LANGUAGE) or "").lower()
    is_pt_video = video_lang.startswith(_LANG_CODE_PT)

    ordered_langs = _PT_PRIORITY_LANGS if is_pt_video else _DEFAULT_PRIORITY_LANGS

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
            return datetime.strptime(date_str, _COMPACT_DATE_FORMAT).replace(tzinfo=UTC).date()
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
            return datetime.strptime(date_str, _COMPACT_DATE_FORMAT).replace(tzinfo=UTC)
        except ValueError:
            return datetime.now(UTC)
    return datetime.now(UTC)
