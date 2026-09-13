"""Native Media Ingestion Adapter for Cresmo.

Directly orchestrates yt-dlp and openai-whisper via official Python library APIs.
Provides robust native subtitle extraction (mitigating HTTP 429), ephemeral
scratch isolation for audio transcription, and zero legacy isb.ai coupling (ADR-004 & SPEC-004).
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yt_dlp

from cresmo.application.ports import MediaIngestionPort
from cresmo.domain.entities import RawTranscript
from cresmo.domain.exceptions import (
    CresmoInfrastructureError,
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    DiscoveredMediaItem,
)
from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator

_VIDEO_ID_REGEX = re.compile(r"(?:v=|\/)([a-zA-Z0-9_-]{8,64})(?:[&?]|\Z)")
_ILLEGAL_FS_CHARS = re.compile(r'[\\/*?:"<>|%]')


class NativeMediaIngestionAdapter(MediaIngestionPort):
    """Production Hexagonal adapter for media ingestion using pure Python libraries."""

    def __init__(
        self,
        request_timeout: float = 30.0,
        header_generator: RandomHeaderGenerator | None = None,
    ) -> None:
        """Initialize NativeMediaIngestionAdapter.

        Args:
            request_timeout: Socket timeout in seconds for subtitle HTTP requests.
            header_generator: Optional dynamic browser request header generator.
        """
        self.request_timeout = request_timeout
        self._header_generator = header_generator or RandomHeaderGenerator()

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        match = _VIDEO_ID_REGEX.search(url)
        if match:
            return match.group(1)
        return Path(url).stem

    def _sanitize_fs_name(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "Unknown_Channel"

    def _is_native_subtitle_url(self, url: str | None) -> bool:
        """Validate that subtitle URL is native and not an on-the-fly machine translation."""
        if not url:
            return False
        # Strictly reject on-the-fly machine-translated subtitles that cause YouTube HTTP 429
        return "tlang=" not in url

    def _find_native_subtitle_url(self, info: dict[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        subtitles: dict[str, list[dict[str, Any]]] = info.get("subtitles") or {}
        auto_captions: dict[str, list[dict[str, Any]]] = info.get("automatic_captions") or {}

        video_lang = str(info.get("language") or "").lower()
        is_pt_video = video_lang.startswith("pt")

        if is_pt_video:
            ordered_langs = ["pt-orig", "pt-BR", "pt", "pt-PT", "en-orig", "en", "en-US"]
        else:
            ordered_langs = ["en-orig", "en", "en-US", "pt-orig", "pt-BR", "pt", "pt-PT"]

        # 1. Search in manual subtitles in preferred language order (ext: json3)
        for lang in ordered_langs:
            if lang in subtitles:
                for fmt in subtitles[lang]:
                    url = fmt.get("url")
                    if fmt.get("ext") == "json3" and self._is_native_subtitle_url(url):
                        return str(url)

        # 2. Search manual subtitles in any language
        for formats in subtitles.values():
            for fmt in formats:
                url = fmt.get("url")
                if fmt.get("ext") == "json3" and self._is_native_subtitle_url(url):
                    return str(url)

        # 3. Automatic captions: Prioritize explicit original tracks (*-orig)
        orig_keys = [k for k in auto_captions if k.endswith("-orig") or k == "orig"]
        orig_keys.sort(
            key=lambda k: 0 if (is_pt_video and "pt" in k) or (not is_pt_video and "en" in k) else 1
        )
        for lang in orig_keys:
            for fmt in auto_captions[lang]:
                url = fmt.get("url")
                if fmt.get("ext") == "json3" and self._is_native_subtitle_url(url):
                    return str(url)

        # 4. Automatic captions matching preferred language order without tlang
        for lang in ordered_langs:
            if lang in auto_captions:
                for fmt in auto_captions[lang]:
                    url = fmt.get("url")
                    if fmt.get("ext") == "json3" and self._is_native_subtitle_url(url):
                        return str(url)

        # 5. Any automatic caption track without tlang
        for formats in auto_captions.values():
            for fmt in formats:
                url = fmt.get("url")
                if fmt.get("ext") == "json3" and self._is_native_subtitle_url(url):
                    return str(url)

        return None

    def _fetch_url_content(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                raw_bytes: bytes = resp.read()
                return raw_bytes.decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def _reconstruct_json3_paragraphs(self, data: dict[str, Any]) -> str:
        """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
        events: list[dict[str, Any]] = data.get("events", [])
        paragraphs: list[str] = []
        current_sentences: list[str] = []

        for event in events:
            if "segs" in event and not event.get("aAppend"):
                seg_text = "".join(str(s.get("utf8", "")) for s in event["segs"]).strip()
                if seg_text and seg_text != "\n":
                    current_sentences.append(seg_text)
                    # Group into paragraphs roughly every 4 sentences or punctuation pauses
                    if len(current_sentences) >= 4 or seg_text.endswith((".", "!", "?")):
                        paragraphs.append(" ".join(current_sentences))
                        current_sentences = []

        if current_sentences:
            paragraphs.append(" ".join(current_sentences))

        return "\n\n".join(paragraphs).strip()

    def _handle_yt_dlp_error(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def _transcribe_audio_fallback(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        info: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        import whisper

        channel_name = "Unknown_Channel"
        if info:
            channel_name = self._sanitize_fs_name(
                str(info.get("channel") or info.get("uploader") or "Unknown_Channel")
            )

        with tempfile.TemporaryDirectory(prefix="cresmo_scratch_") as scratch_str:
            scratch_path = Path(scratch_str)
            ydl_opts: dict[str, Any] = {
                "format": "bestaudio/best",
                "outtmpl": str(scratch_path / "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "http_headers": self._header_generator.get_random_headers(),
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as exc:  # noqa: BLE001
                self._handle_yt_dlp_error(exc)

            downloaded_files = list(scratch_path.glob("*.*"))
            if not downloaded_files:
                raise IngestionNetworkError(
                    f"yt-dlp completed audio download but no file was found in {scratch_path}"
                )

            audio_file = downloaded_files[0]

            if keep_audio:
                dest_dir = output_dir / channel_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                model = whisper.load_model(whisper_model)
                transcription_result = model.transcribe(str(audio_file))
                body = str(transcription_result.get("text", "")).strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Ingest single video into RawTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        video_id = self._extract_video_id(video_url)

        ydl_opts: dict[str, Any] = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "http_headers": self._header_generator.get_random_headers(),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")

        actual_video_id = str(info.get("id") or video_id)
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "Unknown_Channel")
        )

        # Check for native subtitles (rejecting tlang=)
        sub_url = self._find_native_subtitle_url(info)
        body = ""

        if sub_url:
            raw_sub = self._fetch_url_content(sub_url)
            try:
                sub_data = json.loads(raw_sub)
                body = self._reconstruct_json3_paragraphs(sub_data)
            except Exception:  # noqa: BLE001
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        category, _ = classify_channel(channel_name)
        date_str = str(info.get("upload_date") or "")
        upload_date = None
        if len(date_str) == 8 and date_str.isdigit():
            try:
                upload_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC).date()
            except ValueError:
                pass

        return RawTranscript(
            content_id=ContentId(actual_video_id),
            channel_name=channel_name,
            body=body,
            title=str(info.get("title") or ""),
            source_url=video_url,
            upload_date=upload_date,
            channel_id=str(info.get("channel_id") or "unknown_channel"),
            channel_category=category,
            video_description=str(info.get("description") or ""),
        )

    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        ydl_opts: dict[str, Any] = {
            "extract_flat": True,
            "playlistend": query.max_videos,
            "quiet": True,
            "no_warnings": True,
            "http_headers": self._header_generator.get_random_headers(),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query.channel_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return []

        if not info:
            return []

        entries = info.get("entries") or []
        channel_title = str(info.get("title") or info.get("uploader") or "Unknown_Channel")
        items: list[DiscoveredMediaItem] = []

        for entry in entries:
            if not entry or not isinstance(entry, dict):
                continue

            vid = str(entry.get("id") or "").strip()
            title = str(entry.get("title") or "").strip()
            if not vid or not title:
                continue

            url = str(entry.get("url") or f"https://www.youtube.com/watch?v={vid}").strip()
            channel = str(entry.get("channel") or entry.get("uploader") or channel_title).strip()

            raw_date = entry.get("upload_date")
            pub_date = datetime.now(UTC)
            if raw_date and isinstance(raw_date, str) and len(raw_date) == 8:
                try:
                    pub_date = datetime.strptime(raw_date, "%Y%m%d").replace(tzinfo=UTC)
                except ValueError:
                    pass

            items.append(
                DiscoveredMediaItem(
                    content_id=ContentId(vid),
                    title=title,
                    published_at=pub_date,
                    media_url=url,
                    channel_name=channel,
                )
            )

        return items

    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        """Ingest videos from playlists sequentially or in parallel batches."""
        transcripts: list[RawTranscript] = []
        for url in playlist_urls:
            raw = self.ingest_single_video(
                video_url=url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )
            if raw:
                transcripts.append(raw)
        return transcripts
