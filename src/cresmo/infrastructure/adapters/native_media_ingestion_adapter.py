"""Native Media Ingestion Adapter for Cresmo.

Directly orchestrates yt-dlp and openai-whisper via official Python library APIs.
Provides robust native subtitle extraction (mitigating HTTP 429), ephemeral
scratch isolation for audio transcription, and zero legacy isb.ai coupling.
Acts as an Anti-Corruption Layer (ACL) shielding the domain from external
scraping quirks and third-party media libraries.

Conforms to:
    - ADR-004: Native Media Ingestion Decommissioning
    - SPEC-004: Native Media Ingestion Specification
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance
"""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast

import whisper
import yt_dlp

from cresmo.application.ports import MediaIngestionPort, MetricsPort
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
    ChannelId,
    ChannelName,
    ContentId,
    DiscoveredMediaItem,
)
from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.media.feed import (
    discover_channel_feed_items,
    extract_channel_url_from_info,
)
from cresmo.infrastructure.adapters.media.subtitles import (
    _ILLEGAL_FS_CHARS,
    ensure_yt_dlp_plugins_loaded,
    find_native_subtitle_url,
    is_native_subtitle_url,
    parse_published_datetime,
    parse_upload_date,
    reconstruct_json3_paragraphs,
)
from cresmo.infrastructure.adapters.noop_metrics_adapter import NoOpMetricsAdapter

logger = logging.getLogger(__name__)

# Re-exports for backwards compatibility
_ensure_yt_dlp_plugins_loaded = ensure_yt_dlp_plugins_loaded


class NativeMediaIngestionAdapter(MediaIngestionPort):
    """Production Hexagonal adapter for media ingestion using pure Python libraries.

    Encapsulates yt-dlp and Whisper execution behind the MediaIngestionPort contract.
    Shields domain models from low-level subprocesses, network timeouts, and JSON schemas.

    Attributes:
        request_timeout: Socket timeout in seconds for fetching remote subtitle streams.
    """

    def __init__(
        self,
        request_timeout: float = 30.0,
        header_generator: RandomHeaderGenerator | None = None,
        whisper_concurrency_limit: int = 2,
        cookie_file: Path | str | None = None,
        js_runtime_name: str | None = None,
        metrics_port: MetricsPort | None = None,
    ) -> None:
        """Initialize NativeMediaIngestionAdapter.

        Args:
            request_timeout: Socket timeout in seconds for subtitle HTTP requests.
            header_generator: Optional dynamic browser request header generator.
            whisper_concurrency_limit: Maximum concurrent Whisper model executions.
            cookie_file: Optional path to Netscape cookies file for YouTube authentication.
            js_runtime_name: Optional explicit JavaScript runtime name for yt-dlp ('node', 'deno', 'bun').
            metrics_port: Optional MetricsPort instance for Prometheus time-series metrics.
        """
        self.request_timeout = request_timeout
        self._header_generator = header_generator or RandomHeaderGenerator()
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def _detect_js_runtime(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def _build_ydl_opts(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = self._header_generator.get_random_headers()

        # Inject Netscape authentication cookies if file exists
        if (
            self._cookie_file
            and self._cookie_file.exists()
            and self._cookie_file.stat().st_size > 0
        ):
            opts["cookiefile"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = ContentId.extract_from_text(url)
        if cid:
            return cid.value
        return Path(url).stem

    def _sanitize_fs_name(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "Unknown_Channel"

    _is_native_subtitle_url = staticmethod(is_native_subtitle_url)

    def _find_native_subtitle_url(self, info: Mapping[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        return find_native_subtitle_url(info)

    def _fetch_url_content(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                raw_bytes: bytes = response.read()
                return raw_bytes.decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def _reconstruct_json3_paragraphs(self, data: dict[str, Any]) -> str:
        """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
        return reconstruct_json3_paragraphs(data)

    def _handle_yt_dlp_error(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
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
        info: Mapping[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        channel_name = "Unknown_Channel"
        if info:
            channel_name = self._sanitize_fs_name(
                str(info.get("channel") or info.get("uploader") or "Unknown_Channel")
            )

        with tempfile.TemporaryDirectory(prefix="cresmo_scratch_") as scratch_str:
            scratch_path = Path(scratch_str)
            ydl_opts: dict[str, Any] = self._build_ydl_opts(
                {
                    "format": "bestaudio/best",
                    "outtmpl": str(scratch_path / "%(id)s.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                }
            )

            try:
                with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
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
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = str(transcription_result.get("text", "")).strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    _parse_upload_date = staticmethod(parse_upload_date)
    _parse_published_datetime = staticmethod(parse_published_datetime)

    def _fetch_video_metadata(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def _resolve_transcript_body(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "Unknown_Channel")
        )
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))

        # Check for native subtitles (rejecting tlang=)
        sub_url = self._find_native_subtitle_url(info)
        body = ""

        if sub_url:
            try:
                raw_sub = self._fetch_url_content(sub_url)
                sub_data = json.loads(raw_sub)
                body = self._reconstruct_json3_paragraphs(sub_data)
            except RateLimitExceededError:
                raise
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

        return body, channel_name

    def _build_raw_transcript_aggregate(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[RawTranscript, ChannelId | None]:
        """Construct domain RawTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        transcript = RawTranscript(
            content_id=cid,
            channel_name=c_name,
            body=body,
            title=str(info.get("title") or ""),
            source_url=video_url,
            publication_date=upload_date,
            upload_date=upload_date,
            channel_id=ch_id,
            channel_category=category,
            video_description=str(info.get("description") or ""),
        )
        return transcript, ch_id

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
        start_time = time.perf_counter()
        status = "success"
        channel_for_metrics = "Unknown_Channel"
        channel_id_for_metrics = ""

        try:
            info = self._fetch_video_metadata(video_url)
            if not info:
                status = "failure"
                return None

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )
            channel_for_metrics = channel_name

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id_for_metrics = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id_for_metrics,
                    "channel_name": channel_for_metrics,
                    "modality": "url",
                    "status": status,
                },
            )

    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts({}),
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def extract_channel_url_from_video(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception:  # noqa: BLE001
            return None
        return extract_channel_url_from_info(cast(Any, info))
