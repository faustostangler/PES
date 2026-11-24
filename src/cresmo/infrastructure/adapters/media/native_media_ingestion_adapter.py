"""Native Media Ingestion Adapter for Cresmo.

Directly orchestrates yt-dlp, pooled HTTPX, YouTube Atom RSS discovery, and
FasterWhisperEngine (CTranslate2) via official Python library APIs.
Provides manifest-pruned metadata extraction, native subtitle prioritization
(mitigating HTTP 429), and ephemeral scratch isolation for audio transcription.
Acts as an Anti-Corruption Layer (ACL) shielding the domain from external
scraping quirks and third-party media libraries.

Conforms to:
    - ADR-004: Native Media Ingestion Decommissioning
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance
    - ADR-075: High-Throughput Native Media Ingestion
    - SPEC-004 / SPEC-075
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import threading
import time
from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path
from types import TracebackType
from typing import Any, Final, Self, cast

import httpx
import structlog

from cresmo.application.ports import (
    MediaIngestionPort,
    MetricName,
    MetricsPort,
    NoOpMetricsPort,
)
from cresmo.application.ports.taxonomy import ChannelTaxonomyPort
from cresmo.domain.entities import StageTranscript
from cresmo.domain.exceptions import (
    CresmoInfrastructureError,
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    Channel,
    ChannelFeedQuery,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    DiscoveredMediaItem,
    MediaProvenance,
)
from cresmo.infrastructure.adapters.media.feed import (
    discover_channel_feed_items,
    extract_channel_url_from_info,
)
from cresmo.infrastructure.adapters.media.subtitles import (
    _ILLEGAL_FS_CHARS,
    ensure_yt_dlp_plugins_loaded,
    find_native_subtitle_url,
    parse_upload_date,
    reconstruct_json3_paragraphs,
)
from cresmo.infrastructure.adapters.media.transcriber import FasterWhisperEngine
from cresmo.infrastructure.adapters.scrapers.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.taxonomy.json_taxonomy_adapter import JsonTaxonomyCatalogAdapter

logger = structlog.get_logger(__name__)

YTDLP_METADATA_SKIP_MANIFESTS: Final[tuple[str, ...]] = ("dash", "hls", "translated_subs")
DEFAULT_HTTP_MAX_CONNECTIONS: Final[int] = 20
DEFAULT_HTTP_MAX_KEEPALIVE_CONNECTIONS: Final[int] = 10


class NativeMediaIngestionAdapter(MediaIngestionPort):
    """Production Hexagonal adapter for media ingestion using pure Python libraries.

    Encapsulates yt-dlp, pooled HTTPX, and FasterWhisperEngine behind MediaIngestionPort.
    Shields domain models from low-level subprocesses, network timeouts, and JSON schemas.

    Attributes:
        request_timeout: Socket timeout in seconds for fetching remote subtitle and RSS streams.
    """

    def __init__(
        self,
        request_timeout: float = 30.0,
        header_generator: RandomHeaderGenerator | None = None,
        whisper_concurrency_limit: int = 2,
        cookie_file: Path | str | None = None,
        js_runtime_name: str | None = None,
        metrics_port: MetricsPort | None = None,
        taxonomy_port: ChannelTaxonomyPort | None = None,
        whisper_device: str = "auto",
        whisper_compute_type: str = "auto",
        whisper_vad_filter: bool = True,
        enable_rss_fast_path: bool = True,
        http_client: httpx.Client | None = None,
        transcriber: FasterWhisperEngine | None = None,
    ) -> None:
        """Initialize NativeMediaIngestionAdapter.

        Args:
            request_timeout: Socket timeout in seconds for subtitle and RSS HTTP requests.
            header_generator: Optional dynamic browser request header generator.
            whisper_concurrency_limit: Maximum concurrent Whisper model executions.
            cookie_file: Optional path to Netscape cookies file for YouTube authentication.
            js_runtime_name: Optional explicit JavaScript runtime name for yt-dlp ('node', 'deno', 'bun').
            metrics_port: Optional MetricsPort instance for Prometheus time-series metrics.
            taxonomy_port: Optional taxonomy classifier port (defaults to bundled JsonTaxonomyCatalogAdapter).
            whisper_device: Target inference device for FasterWhisperEngine ('auto', 'cpu', 'cuda').
            whisper_compute_type: CTranslate2 compute type ('auto', 'int8', 'float16', etc.).
            whisper_vad_filter: Whether to enable Silero VAD speech filtering during transcription.
            enable_rss_fast_path: Whether to attempt YouTube Atom RSS discovery before yt-dlp.
            http_client: Optional externally managed httpx.Client for connection pooling or testing.
            transcriber: Optional FasterWhisperEngine instance for audio transcription fallback.
        """
        self.request_timeout = request_timeout
        self._header_generator = header_generator or RandomHeaderGenerator()
        self._transcriber = transcriber or FasterWhisperEngine(
            concurrency_limit=whisper_concurrency_limit,
            device=whisper_device,
            compute_type=whisper_compute_type,
            vad_filter=whisper_vad_filter,
        )
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsPort()
        else:
            self._metrics_port = metrics_port
        self._taxonomy_port: ChannelTaxonomyPort = taxonomy_port or JsonTaxonomyCatalogAdapter()
        self._enable_rss_fast_path = enable_rss_fast_path
        self._http_client: httpx.Client | None = http_client
        self._owns_http_client = http_client is None
        self._http_client_lock = threading.Lock()

    def _get_http_client(self) -> httpx.Client:
        """Lazily construct and return a pooled, HTTP/2-capable httpx.Client."""
        if self._http_client is not None:
            return self._http_client
        with self._http_client_lock:
            if self._http_client is None:
                http2_available = importlib.util.find_spec("h2") is not None
                self._http_client = httpx.Client(
                    timeout=self.request_timeout,
                    limits=httpx.Limits(
                        max_connections=DEFAULT_HTTP_MAX_CONNECTIONS,
                        max_keepalive_connections=DEFAULT_HTTP_MAX_KEEPALIVE_CONNECTIONS,
                    ),
                    follow_redirects=True,
                    http2=http2_available,
                )
            return self._http_client

    def close(self) -> None:
        """Close the adapter-owned httpx.Client connection pool if initialized."""
        with self._http_client_lock:
            if self._http_client is not None and self._owns_http_client:
                self._http_client.close()
                self._http_client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

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

    def _find_native_subtitle_url(self, info: Mapping[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        return find_native_subtitle_url(info)

    def _fetch_url_content(self, url: str) -> str:
        """Fetch remote subtitle or RSS payload via pooled HTTPX client with dynamic headers."""
        client = self._get_http_client()
        try:
            response = client.get(url, headers=self._header_generator.get_random_headers())
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching URL: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching URL: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching URL: {exc}") from exc

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

    def _extract_channel_name(self, info: Mapping[str, Any]) -> str:
        """Extract and sanitize channel/uploader name from yt-dlp metadata."""
        return self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "Unknown_Channel")
        )

    def _transcribe_audio_fallback(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        channel_name: str = "Unknown_Channel",
    ) -> str:
        """Download audio to ephemeral scratch dir, transcribe via FasterWhisperEngine, and clean up."""
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
                import yt_dlp

                ensure_yt_dlp_plugins_loaded()
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

            body = self._transcriber.transcribe(audio_file, model_name=whisper_model)

        return str(body)

    _parse_upload_date = staticmethod(parse_upload_date)

    def _fetch_video_metadata(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp while pruning DASH/HLS manifest parsing."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "ignore_no_formats_error": True,
                "extractor_args": {
                    "youtube": {"skip": list(YTDLP_METADATA_SKIP_MANIFESTS)},
                },
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            import yt_dlp

            ensure_yt_dlp_plugins_loaded()
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
        channel_name: str = "Unknown_Channel",
    ) -> str:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                channel_name=channel_name,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return str(body)

    @staticmethod
    def _extract_channel_id(info: Mapping[str, Any]) -> ChannelId | None:
        """Extract canonical ChannelId from yt-dlp video metadata if present."""
        raw_channel_id = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        return ChannelId.extract_from_text(raw_channel_id)

    def _build_raw_transcript_aggregate(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[StageTranscript, ChannelId | None]:
        """Construct domain StageTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        content_id = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        resolved_channel_name = ChannelName.from_string(channel_name)
        category, _ = self._taxonomy_port.classify(resolved_channel_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        resolved_channel_id = self._extract_channel_id(info)

        channel = Channel(
            name=resolved_channel_name,
            id=resolved_channel_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=content_id,
            title=str(info.get("title") or ""),
            text=body,
        )
        transcript = StageTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, resolved_channel_id

    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> StageTranscript | None:
        """Ingest single video into StageTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = ""

        try:
            info = self._fetch_video_metadata(video_url)
            if not info:
                status = "failure"
                return None

            channel_name = self._extract_channel_name(info)
            early_channel_id = self._extract_channel_id(info)
            if early_channel_id:
                channel_id = early_channel_id.value

            body = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                channel_name=channel_name,
            )

            transcript, resolved_channel_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if resolved_channel_id:
                channel_id = resolved_channel_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                MetricName.MEDIA_INGESTION_DURATION,
                elapsed,
                labels={
                    "channel_id": channel_id,
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
            fetch_rss_xml=self._fetch_url_content,
            enable_rss_fast_path=self._enable_rss_fast_path,
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
            import yt_dlp

            ensure_yt_dlp_plugins_loaded()
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))
