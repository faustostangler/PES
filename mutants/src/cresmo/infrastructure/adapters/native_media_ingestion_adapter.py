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
from cresmo.domain.entities import SourceTranscript
from cresmo.domain.exceptions import (
    CresmoInfrastructureError,
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.domain.taxonomy import classify_channel
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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut: MutantDict = {}  # type: ignore


class NativeMediaIngestionAdapter(MediaIngestionPort):
    """Production Hexagonal adapter for media ingestion using pure Python libraries.

    Encapsulates yt-dlp and Whisper execution behind the MediaIngestionPort contract.
    Shields domain models from low-level subprocesses, network timeouts, and JSON schemas.

    Attributes:
        request_timeout: Socket timeout in seconds for fetching remote subtitle streams.
    """

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut)
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

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_orig(
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

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_1(
        self,
        request_timeout: float = 31.0,
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

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_2(
        self,
        request_timeout: float = 30.0,
        header_generator: RandomHeaderGenerator | None = None,
        whisper_concurrency_limit: int = 3,
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

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_3(
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
        self.request_timeout = None
        self._header_generator = header_generator or RandomHeaderGenerator()
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_4(
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
        self._header_generator = None
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_5(
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
        self._header_generator = header_generator and RandomHeaderGenerator()
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_6(
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
        self._whisper_semaphore = None
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_7(
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
        self._whisper_semaphore = threading.BoundedSemaphore(None)
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_8(
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
        self._whisper_semaphore = threading.BoundedSemaphore(max(None, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_9(
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
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, None))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_10(
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
        self._whisper_semaphore = threading.BoundedSemaphore(max(whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_11(
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
        self._whisper_semaphore = threading.BoundedSemaphore(max(1, ))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_12(
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
        self._whisper_semaphore = threading.BoundedSemaphore(max(2, whisper_concurrency_limit))
        self._cookie_file: Path | None = Path(cookie_file).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_13(
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
        self._cookie_file: Path | None = None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_14(
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
        self._cookie_file: Path | None = Path(None).resolve() if cookie_file else None
        self._js_runtime_name: str | None = js_runtime_name or self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_15(
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
        self._js_runtime_name: str | None = None
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_16(
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
        self._js_runtime_name: str | None = js_runtime_name and self._detect_js_runtime()
        ensure_yt_dlp_plugins_loaded()
        if metrics_port is None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_17(
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
        if metrics_port is not None:
            self._metrics_port: MetricsPort = NoOpMetricsAdapter()
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_18(
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
            self._metrics_port: MetricsPort = None
        else:
            self._metrics_port = metrics_port

    def xǁNativeMediaIngestionAdapterǁ__init____mutmut_19(
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
            self._metrics_port = None

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut)
    def _detect_js_runtime(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_orig(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_1(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("XXnodeXX", "deno", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_2(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("NODE", "deno", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_3(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "XXdenoXX", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_4(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "DENO", "bun"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_5(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "XXbunXX"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_6(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "BUN"):
            if shutil.which(candidate):
                return candidate
        return None

    def xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_7(self) -> str | None:
        """Auto-detect available JavaScript runtime for yt-dlp challenge solving."""
        for candidate in ("node", "deno", "bun"):
            if shutil.which(None):
                return candidate
        return None

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut)
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_orig(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_1(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = None
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_2(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(None)
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_3(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "XXhttp_headersXX" not in opts:
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_4(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "HTTP_HEADERS" not in opts:
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_5(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" in opts:
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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_6(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = None

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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_7(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["XXhttp_headersXX"] = self._header_generator.get_random_headers()

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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_8(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["HTTP_HEADERS"] = self._header_generator.get_random_headers()

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

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_9(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = self._header_generator.get_random_headers()

        # Inject Netscape authentication cookies if file exists
        if (
            self._cookie_file
            and self._cookie_file.exists() or self._cookie_file.stat().st_size > 0
        ):
            opts["cookiefile"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_10(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = self._header_generator.get_random_headers()

        # Inject Netscape authentication cookies if file exists
        if (
            self._cookie_file or self._cookie_file.exists()
            and self._cookie_file.stat().st_size > 0
        ):
            opts["cookiefile"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_11(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = self._header_generator.get_random_headers()

        # Inject Netscape authentication cookies if file exists
        if (
            self._cookie_file
            and self._cookie_file.exists()
            and self._cookie_file.stat().st_size >= 0
        ):
            opts["cookiefile"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_12(self, base_opts: dict[str, Any]) -> dict[str, Any]:
        """Construct fully-configured yt-dlp options with headers, cookies, and JS runtime."""
        opts = dict(base_opts)
        if "http_headers" not in opts:
            opts["http_headers"] = self._header_generator.get_random_headers()

        # Inject Netscape authentication cookies if file exists
        if (
            self._cookie_file
            and self._cookie_file.exists()
            and self._cookie_file.stat().st_size > 1
        ):
            opts["cookiefile"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_13(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["cookiefile"] = None

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_14(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["XXcookiefileXX"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_15(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["COOKIEFILE"] = str(self._cookie_file)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_16(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["cookiefile"] = str(None)

        # Inject JavaScript runtime for YouTube n-sig challenge solving
        if self._js_runtime_name:
            opts["js_runtimes"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_17(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["js_runtimes"] = None

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_18(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["XXjs_runtimesXX"] = {self._js_runtime_name: {}}

        return opts

    def xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_19(self, base_opts: dict[str, Any]) -> dict[str, Any]:
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
            opts["JS_RUNTIMES"] = {self._js_runtime_name: {}}

        return opts

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut)
    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = ContentId.extract_from_text(url)
        if cid:
            return cid.value
        return Path(url).stem

    def xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_orig(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = ContentId.extract_from_text(url)
        if cid:
            return cid.value
        return Path(url).stem

    def xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_1(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = None
        if cid:
            return cid.value
        return Path(url).stem

    def xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_2(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = ContentId.extract_from_text(None)
        if cid:
            return cid.value
        return Path(url).stem

    def xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_3(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        cid = ContentId.extract_from_text(url)
        if cid:
            return cid.value
        return Path(None).stem

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut)
    def _sanitize_fs_name(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_orig(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_1(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = None
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_2(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub(None, name).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_3(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", None).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_4(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub(name).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_5(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", ).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_6(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("XX_XX", name).strip()
        return cleaned or "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_7(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned and "Unknown_Channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_8(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "XXUnknown_ChannelXX"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_9(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "unknown_channel"

    def xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_10(self, name: str) -> str:
        """Sanitize channel or video title for filesystem safety."""
        cleaned = _ILLEGAL_FS_CHARS.sub("_", name).strip()
        return cleaned or "UNKNOWN_CHANNEL"

    _is_native_subtitle_url = staticmethod(is_native_subtitle_url)

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut)
    def _find_native_subtitle_url(self, info: Mapping[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        return find_native_subtitle_url(info)

    def xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut_orig(self, info: Mapping[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        return find_native_subtitle_url(info)

    def xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut_1(self, info: Mapping[str, Any]) -> str | None:
        """Search for native spoken subtitle URL, strictly rejecting tlang= translations."""
        return find_native_subtitle_url(None)

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut)
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_orig(self, url: str) -> str:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_1(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = None
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_2(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            None,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_3(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=None,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_4(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_5(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_6(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(None, timeout=self.request_timeout) as response:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_7(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=None) as response:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_8(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(timeout=self.request_timeout) as response:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_9(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, ) as response:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_10(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                raw_bytes: bytes = None
                return raw_bytes.decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_11(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                raw_bytes: bytes = response.read()
                return raw_bytes.decode(None)
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_12(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                raw_bytes: bytes = response.read()
                return raw_bytes.decode("XXutf-8XX")
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_13(self, url: str) -> str:
        """Fetch remote subtitle payload with dynamic browser headers."""
        req = urllib.request.Request(
            url,
            headers=self._header_generator.get_random_headers(),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                raw_bytes: bytes = response.read()
                return raw_bytes.decode("UTF-8")
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_14(self, url: str) -> str:
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
            if exc.code != HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceededError(
                    f"HTTP 429 Too Many Requests while fetching subtitles: {exc}"
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_15(self, url: str) -> str:
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
                    None
                ) from exc
            raise IngestionNetworkError(f"HTTP error fetching subtitles: {exc}") from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_16(self, url: str) -> str:
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
            raise IngestionNetworkError(None) from exc
        except Exception as exc:
            raise IngestionNetworkError(f"Network error fetching subtitles: {exc}") from exc

    def xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_17(self, url: str) -> str:
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
            raise IngestionNetworkError(None) from exc

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut)
    def _reconstruct_json3_paragraphs(self, data: dict[str, Any]) -> str:
        """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
        return reconstruct_json3_paragraphs(data)

    def xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut_orig(self, data: dict[str, Any]) -> str:
        """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
        return reconstruct_json3_paragraphs(data)

    def xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut_1(self, data: dict[str, Any]) -> str:
        """Reconstruct JSON3 subtitle event segments into continuous prose paragraphs."""
        return reconstruct_json3_paragraphs(None)

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut)
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_orig(self, exc: Exception) -> None:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_1(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = None
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_2(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(None)
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_3(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg and "Too Many Requests" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_4(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "XX429XX" in msg or "Too Many Requests" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_5(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" not in msg or "Too Many Requests" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_6(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "XXToo Many RequestsXX" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_7(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "too many requests" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_8(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "TOO MANY REQUESTS" in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_9(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" not in msg:
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_10(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(None) from exc
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

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_11(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg and "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_12(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "XXSign in to confirm you’re not a botXX" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_13(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_14(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "SIGN IN TO CONFIRM YOU’RE NOT A BOT" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_15(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" not in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_16(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "XXconfirm you're not a botXX" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_17(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "CONFIRM YOU'RE NOT A BOT" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_18(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" not in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_19(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                None
            ) from exc
        if any(
            term in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_20(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            None
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_21(self, exc: Exception) -> None:
        """Translate yt-dlp internal exceptions to canonical domain exception hierarchy."""
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            raise RateLimitExceededError(f"Upstream rate limit exceeded (HTTP 429): {msg}") from exc
        if "Sign in to confirm you’re not a bot" in msg or "confirm you're not a bot" in msg:
            raise IngestionNetworkError(
                f"YouTube bot-detection challenge triggered. Use active session cookies via 'cresmo export-cookies': {msg}"
            ) from exc
        if any(
            term not in msg
            for term in ("Connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_22(self, exc: Exception) -> None:
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
            for term in ("XXConnection resetXX", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_23(self, exc: Exception) -> None:
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
            for term in ("connection reset", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_24(self, exc: Exception) -> None:
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
            for term in ("CONNECTION RESET", "timed out", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_25(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "XXtimed outXX", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_26(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "TIMED OUT", "Name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_27(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "XXName or service not knownXX", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_28(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "name or service not known", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_29(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "NAME OR SERVICE NOT KNOWN", "Network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_30(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "Name or service not known", "XXNetworkXX")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_31(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "Name or service not known", "network")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_32(self, exc: Exception) -> None:
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
            for term in ("Connection reset", "timed out", "Name or service not known", "NETWORK")
        ):
            raise IngestionNetworkError(f"Ingestion network connectivity error: {msg}") from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_33(self, exc: Exception) -> None:
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
            raise IngestionNetworkError(None) from exc
        raise CresmoInfrastructureError(f"Media extraction infrastructure error: {msg}") from exc

    def xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_34(self, exc: Exception) -> None:
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
        raise CresmoInfrastructureError(None) from exc

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut)
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_orig(
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_1(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        info: Mapping[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        channel_name = None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_2(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        info: Mapping[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        channel_name = "XXUnknown_ChannelXX"
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_3(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        info: Mapping[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        channel_name = "unknown_channel"
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_4(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
        info: Mapping[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Download audio to ephemeral scratch dir, transcribe via Whisper, and clean up."""
        channel_name = "UNKNOWN_CHANNEL"
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_5(
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
            channel_name = None

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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_6(
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
                None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_7(
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
                str(None)
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_8(
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
                str(info.get("channel") or info.get("uploader") and "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_9(
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
                str(info.get("channel") and info.get("uploader") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_10(
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
                str(info.get(None) or info.get("uploader") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_11(
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
                str(info.get("XXchannelXX") or info.get("uploader") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_12(
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
                str(info.get("CHANNEL") or info.get("uploader") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_13(
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
                str(info.get("channel") or info.get(None) or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_14(
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
                str(info.get("channel") or info.get("XXuploaderXX") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_15(
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
                str(info.get("channel") or info.get("UPLOADER") or "Unknown_Channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_16(
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
                str(info.get("channel") or info.get("uploader") or "XXUnknown_ChannelXX")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_17(
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
                str(info.get("channel") or info.get("uploader") or "unknown_channel")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_18(
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
                str(info.get("channel") or info.get("uploader") or "UNKNOWN_CHANNEL")
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_19(
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

        with tempfile.TemporaryDirectory(prefix=None) as scratch_str:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_20(
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

        with tempfile.TemporaryDirectory(prefix="XXcresmo_scratch_XX") as scratch_str:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_21(
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

        with tempfile.TemporaryDirectory(prefix="CRESMO_SCRATCH_") as scratch_str:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_22(
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
            scratch_path = None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_23(
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
            scratch_path = Path(None)
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_24(
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
            ydl_opts: dict[str, Any] = None

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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_25(
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
                None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_26(
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
                    "XXformatXX": "bestaudio/best",
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_27(
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
                    "FORMAT": "bestaudio/best",
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_28(
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
                    "format": "XXbestaudio/bestXX",
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_29(
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
                    "format": "BESTAUDIO/BEST",
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_30(
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
                    "XXouttmplXX": str(scratch_path / "%(id)s.%(ext)s"),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_31(
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
                    "OUTTMPL": str(scratch_path / "%(id)s.%(ext)s"),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_32(
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
                    "outtmpl": str(None),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_33(
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
                    "outtmpl": str(scratch_path * "%(id)s.%(ext)s"),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_34(
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
                    "outtmpl": str(scratch_path / "XX%(id)s.%(ext)sXX"),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_35(
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
                    "outtmpl": str(scratch_path / "%(ID)S.%(EXT)S"),
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_36(
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
                    "XXquietXX": True,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_37(
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
                    "QUIET": True,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_38(
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
                    "quiet": False,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_39(
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
                    "XXno_warningsXX": True,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_40(
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
                    "NO_WARNINGS": True,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_41(
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
                    "no_warnings": False,
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_42(
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
                with yt_dlp.YoutubeDL(None) as ydl:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_43(
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
                with yt_dlp.YoutubeDL(cast(None, ydl_opts)) as ydl:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_44(
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
                with yt_dlp.YoutubeDL(cast(Any, None)) as ydl:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_45(
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
                with yt_dlp.YoutubeDL(cast(ydl_opts)) as ydl:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_46(
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
                with yt_dlp.YoutubeDL(cast(Any, )) as ydl:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_47(
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
                    ydl.download(None)
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_48(
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
                self._handle_yt_dlp_error(None)

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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_49(
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

            downloaded_files = None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_50(
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

            downloaded_files = list(None)
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_51(
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

            downloaded_files = list(scratch_path.glob(None))
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_52(
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

            downloaded_files = list(scratch_path.glob("XX*.*XX"))
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_53(
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
            if downloaded_files:
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_54(
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
                    None
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_55(
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

            audio_file = None

            if keep_audio:
                dest_dir = output_dir / channel_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_56(
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

            audio_file = downloaded_files[1]

            if keep_audio:
                dest_dir = output_dir / channel_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_57(
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
                dest_dir = None
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_58(
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
                dest_dir = output_dir * channel_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_59(
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
                dest_dir.mkdir(parents=None, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_60(
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
                dest_dir.mkdir(parents=True, exist_ok=None)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_61(
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
                dest_dir.mkdir(exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_62(
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
                dest_dir.mkdir(parents=True, )
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_63(
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
                dest_dir.mkdir(parents=False, exist_ok=True)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_64(
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
                dest_dir.mkdir(parents=True, exist_ok=False)
                dest_audio = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_65(
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
                dest_audio = None
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_66(
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
                dest_audio = dest_dir * audio_file.name
                shutil.copy2(audio_file, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_67(
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
                shutil.copy2(None, dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_68(
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
                shutil.copy2(audio_file, None)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_69(
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
                shutil.copy2(dest_audio)

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_70(
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
                shutil.copy2(audio_file, )

            try:
                with self._whisper_semaphore:
                    model = whisper.load_model(whisper_model)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_71(
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
                    model = None
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_72(
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
                    model = whisper.load_model(None)
                    transcription_result = model.transcribe(str(audio_file))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_73(
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
                    transcription_result = None
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_74(
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
                    transcription_result = model.transcribe(None)
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_75(
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
                    transcription_result = model.transcribe(str(None))
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_76(
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
                    body = None
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_77(
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
                    body = transcription_result.get(None, "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_78(
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
                    body = transcription_result.get("text", None).strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_79(
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
                    body = transcription_result.get("").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_80(
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
                    body = transcription_result.get("text", ).strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_81(
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
                    body = transcription_result.get("XXtextXX", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_82(
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
                    body = transcription_result.get("TEXT", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_83(
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
                    body = transcription_result.get("text", "XXXX").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_84(
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
                    body = transcription_result.get("text", "").strip()
            except Exception as exc:
                raise CresmoInfrastructureError(None) from exc

        return body, channel_name

    _parse_upload_date = staticmethod(parse_upload_date)
    _parse_published_datetime = staticmethod(parse_published_datetime)

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut)
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_orig(self, video_url: str) -> dict[str, Any] | None:
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_1(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = None
        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_2(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            None
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_3(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "XXskip_downloadXX": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_4(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "SKIP_DOWNLOAD": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_5(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": False,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_6(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "XXquietXX": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_7(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "QUIET": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_8(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": False,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_9(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "XXno_warningsXX": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_10(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "NO_WARNINGS": True,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_11(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": False,
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

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_12(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(None) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_13(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(None, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_14(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(Any, None)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_15(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_16(self, video_url: str) -> dict[str, Any] | None:
        """Extract metadata dictionary from yt-dlp without downloading media."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
            with yt_dlp.YoutubeDL(cast(Any, )) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_17(self, video_url: str) -> dict[str, Any] | None:
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
                info = None
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_18(self, video_url: str) -> dict[str, Any] | None:
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
                info = ydl.extract_info(None, download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_19(self, video_url: str) -> dict[str, Any] | None:
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
                info = ydl.extract_info(video_url, download=None)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_20(self, video_url: str) -> dict[str, Any] | None:
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
                info = ydl.extract_info(download=False)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_21(self, video_url: str) -> dict[str, Any] | None:
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
                info = ydl.extract_info(video_url, )
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_22(self, video_url: str) -> dict[str, Any] | None:
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
                info = ydl.extract_info(video_url, download=True)
        except Exception as exc:  # noqa: BLE001
            self._handle_yt_dlp_error(exc)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_23(self, video_url: str) -> dict[str, Any] | None:
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
            self._handle_yt_dlp_error(None)
            return None

        if not info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_24(self, video_url: str) -> dict[str, Any] | None:
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

        if info:
            raise IngestionNetworkError(f"yt-dlp returned no metadata for URL '{video_url}'")
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_25(self, video_url: str) -> dict[str, Any] | None:
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
            raise IngestionNetworkError(None)
        return cast("dict[str, Any] | None", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_26(self, video_url: str) -> dict[str, Any] | None:
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
        return cast(None, info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_27(self, video_url: str) -> dict[str, Any] | None:
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
        return cast("dict[str, Any] | None", None)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_28(self, video_url: str) -> dict[str, Any] | None:
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
        return cast(info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_29(self, video_url: str) -> dict[str, Any] | None:
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
        return cast("dict[str, Any] | None", )

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_30(self, video_url: str) -> dict[str, Any] | None:
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
        return cast("XXdict[str, Any] | NoneXX", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_31(self, video_url: str) -> dict[str, Any] | None:
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
        return cast("dict[str, any] | none", info)

    def xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_32(self, video_url: str) -> dict[str, Any] | None:
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
        return cast("DICT[STR, ANY] | NONE", info)

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut)
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_orig(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_1(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = None
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_2(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            None
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_3(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(None)
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_4(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") and "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_5(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") and info.get("uploader") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_6(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get(None) or info.get("uploader") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_7(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("XXchannelXX") or info.get("uploader") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_8(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("CHANNEL") or info.get("uploader") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_9(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get(None) or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_10(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("XXuploaderXX") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_11(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("UPLOADER") or "Unknown_Channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_12(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "XXUnknown_ChannelXX")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_13(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "unknown_channel")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_14(
        self,
        video_url: str,
        info: Mapping[str, Any],
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> tuple[str, str]:
        """Resolve transcript text either from native subtitles or Whisper fallback."""
        channel_name = self._sanitize_fs_name(
            str(info.get("channel") or info.get("uploader") or "UNKNOWN_CHANNEL")
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_15(
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
        actual_video_id = None

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_16(
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
        actual_video_id = str(None)

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_17(
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
        actual_video_id = str(info.get("id") and self._extract_video_id(video_url))

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_18(
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
        actual_video_id = str(info.get(None) or self._extract_video_id(video_url))

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_19(
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
        actual_video_id = str(info.get("XXidXX") or self._extract_video_id(video_url))

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_20(
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
        actual_video_id = str(info.get("ID") or self._extract_video_id(video_url))

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_21(
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
        actual_video_id = str(info.get("id") or self._extract_video_id(None))

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_22(
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
        sub_url = None
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_23(
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
        sub_url = self._find_native_subtitle_url(None)
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_24(
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
        body = None

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_25(
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
        body = "XXXX"

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_26(
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
                raw_sub = None
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_27(
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
                raw_sub = self._fetch_url_content(None)
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_28(
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
                sub_data = None
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_29(
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
                sub_data = json.loads(None)
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_30(
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
                body = None
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_31(
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
                body = self._reconstruct_json3_paragraphs(None)
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_32(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    None,
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_33(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    None,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_34(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    None,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_35(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_36(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_37(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_38(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "XXFailed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.XX",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_39(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "failed to fetch or parse native subtitles from '%s': %s. falling back to whisper.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_40(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "FAILED TO FETCH OR PARSE NATIVE SUBTITLES FROM '%S': %S. FALLING BACK TO WHISPER.",
                    sub_url,
                    exc,
                )
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_41(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = None

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_42(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = "XXXX"

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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_43(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if body:
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_44(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = None

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_45(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=None,
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_46(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=None,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_47(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=None,
                keep_audio=keep_audio,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_48(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=None,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_49(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                info=None,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_50(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
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

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_51(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_52(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                keep_audio=keep_audio,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_53(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                info=info,
            )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_54(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
                body = ""

        # If subtitles were absent, malformed, or empty, trigger Whisper fallback
        if not body:
            body, channel_name = self._transcribe_audio_fallback(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
                )

        if not body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_55(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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

        if body:
            raise DomainValidationError(
                f"Extracted transcript body is empty for video ID '{actual_video_id}'."
            )

        return body, channel_name

    def xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_56(
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
            except Exception as exc:  # noqa: BLE001 - Fallback to Whisper audio transcription
                logger.warning(
                    "Failed to fetch or parse native subtitles from '%s': %s. Falling back to Whisper.",
                    sub_url,
                    exc,
                )
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
                None
            )

        return body, channel_name

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut)
    def _build_raw_transcript_aggregate(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_orig(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_1(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = None
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_2(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(None)
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_3(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") and self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_4(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get(None) or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_5(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("XXidXX") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_6(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("ID") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_7(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(None))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_8(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = None
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_9(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) and ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_10(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(None) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_11(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            None
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_12(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = None
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_13(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(None)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_14(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = None
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_15(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(None)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_16(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = None

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_17(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(None)

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_18(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get(None))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_19(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("XXupload_dateXX"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_20(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("UPLOAD_DATE"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_21(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = None
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_22(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(None).strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_23(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") and "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_24(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") and info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_25(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get(None) or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_26(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("XXchannel_idXX") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_27(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("CHANNEL_ID") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_28(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get(None) or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_29(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("XXuploader_idXX") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_30(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("UPLOADER_ID") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_31(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "XXXX").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_32(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = None

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_33(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(None)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_34(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = None
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_35(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=None,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_36(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=None,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_37(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=None,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_38(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_39(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_40(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_41(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_42(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_43(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") and None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_44(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(None) or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_45(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") and "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_46(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get(None) or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_47(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("XXchannel_urlXX") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_48(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("CHANNEL_URL") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_49(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "XXXX") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_50(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = None
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_51(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=None,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_52(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=None,
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_53(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=None,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_54(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_55(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_56(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_57(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(None),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_58(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") and ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_59(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get(None) or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_60(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("XXdescriptionXX") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_61(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("DESCRIPTION") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_62(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or "XXXX"),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_63(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = None
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_64(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=None,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_65(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=None,
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_66(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=None,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_67(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_68(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_69(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_70(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(None),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_71(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") and ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_72(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get(None) or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_73(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("XXtitleXX") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_74(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("TITLE") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_75(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or "XXXX"),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_76(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = None
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_77(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=None,
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_78(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=None,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_79(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=None,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_80(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            provenance=provenance,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_81(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            content=content,
        )
        return transcript, ch_id

    def xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_82(
        self,
        video_url: str,
        info: Mapping[str, Any],
        body: str,
        channel_name: str,
    ) -> tuple[SourceTranscript, ChannelId | None]:
        """Construct domain SourceTranscript entity from resolved metadata and body."""
        actual_video_id = str(info.get("id") or self._extract_video_id(video_url))
        cid = ContentId.extract_from_text(actual_video_id) or ContentId.from_url_or_token(
            actual_video_id
        )
        c_name = ChannelName.from_string(channel_name)
        category, _ = classify_channel(c_name)
        upload_date = self._parse_upload_date(info.get("upload_date"))

        raw_cid = str(info.get("channel_id") or info.get("uploader_id") or "").strip()
        ch_id = ChannelId.extract_from_text(raw_cid)

        channel = Channel(
            name=c_name,
            id=ch_id,
            category=category,
            url=str(info.get("channel_url") or "") or None,
        )
        provenance = MediaProvenance.create(
            url=video_url,
            description=str(info.get("description") or ""),
            publication_date=upload_date,
        )
        content = Content.create(
            id=cid,
            title=str(info.get("title") or ""),
            body=body,
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            )
        return transcript, ch_id

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut)
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_orig(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_1(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "XXbaseXX",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_2(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "BASE",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_3(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = True,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_4(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = None
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_5(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = None
        channel_name = "Unknown_Channel"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_6(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "XXsuccessXX"
        channel_name = "Unknown_Channel"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_7(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "SUCCESS"
        channel_name = "Unknown_Channel"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_8(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = None
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_9(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "XXUnknown_ChannelXX"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_10(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "unknown_channel"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_11(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "UNKNOWN_CHANNEL"
        channel_id = ""

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_12(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = None

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_13(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = "XXXX"

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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_14(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = ""

        try:
            info = None
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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_15(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = ""

        try:
            info = self._fetch_video_metadata(None)
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

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_16(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

        Prioritizes native spoken subtitles. If unavailable, falls back to local
        Whisper transcription with RAII temporary scratch storage.
        """
        start_time = time.perf_counter()
        status = "success"
        channel_name = "Unknown_Channel"
        channel_id = ""

        try:
            info = self._fetch_video_metadata(video_url)
            if info:
                status = "failure"
                return None

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_17(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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
                status = None
                return None

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_18(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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
                status = "XXfailureXX"
                return None

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_19(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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
                status = "FAILURE"
                return None

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_20(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = None

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_21(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=None,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_22(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=None,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_23(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=None,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_24(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=None,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_25(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=None,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_26(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_27(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_28(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_29(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_30(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_31(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = None
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_32(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=None,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_33(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=None,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_34(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=None,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_35(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=None,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_36(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_37(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_38(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_39(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_40(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = None
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_41(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = None
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_42(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "XXfailureXX"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_43(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "FAILURE"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_44(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = None
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_45(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() + start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_46(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                None,
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_47(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                None,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_48(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                labels=None,
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_49(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_50(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_51(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "cresmo_media_ingestion_duration_seconds",
                elapsed,
                )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_52(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "XXcresmo_media_ingestion_duration_secondsXX",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_53(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
            return transcript
        except Exception:
            status = "failure"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._metrics_port.observe_histogram(
                "CRESMO_MEDIA_INGESTION_DURATION_SECONDS",
                elapsed,
                labels={
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_54(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "XXchannel_idXX": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_55(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "CHANNEL_ID": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_56(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "XXchannel_nameXX": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_57(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "CHANNEL_NAME": channel_name,
                    "modality": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_58(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "XXmodalityXX": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_59(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "MODALITY": "url",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_60(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "XXurlXX",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_61(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "URL",
                    "status": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_62(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "XXstatusXX": status,
                },
            )

    def xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_63(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Ingest single video into SourceTranscript domain aggregate.

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

            body, channel_name = self._resolve_transcript_body(
                video_url=video_url,
                info=info,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )

            transcript, ch_id = self._build_raw_transcript_aggregate(
                video_url=video_url,
                info=info,
                body=body,
                channel_name=channel_name,
            )
            if ch_id:
                channel_id = ch_id.value
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
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "modality": "url",
                    "STATUS": status,
                },
            )

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut)
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

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_orig(
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

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_1(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=None,
            ydl_opts=self._build_ydl_opts({}),
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_2(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=None,
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_3(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts({}),
            handle_error=None,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_4(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts({}),
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=None,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_5(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            ydl_opts=self._build_ydl_opts({}),
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_6(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_7(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts({}),
            sanitize_fs_name=self._sanitize_fs_name,
        )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_8(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts({}),
            handle_error=self._handle_yt_dlp_error,
            )

    def xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_9(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Discover media items from a YouTube channel or playlist feed."""
        return discover_channel_feed_items(
            query=query,
            ydl_opts=self._build_ydl_opts(None),
            handle_error=self._handle_yt_dlp_error,
            sanitize_fs_name=self._sanitize_fs_name,
        )

    @_mutmut_mutated(mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut)
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_orig(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_1(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = None
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_2(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            None
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_3(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "XXextract_flatXX": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_4(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "EXTRACT_FLAT": True,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_5(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": False,
                "quiet": True,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_6(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "XXquietXX": True,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_7(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "QUIET": True,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_8(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "quiet": False,
                "no_warnings": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_9(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "quiet": True,
                "XXno_warningsXX": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_10(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "quiet": True,
                "NO_WARNINGS": True,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_11(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL."""
        ydl_opts: dict[str, Any] = self._build_ydl_opts(
            {
                "extract_flat": True,
                "quiet": True,
                "no_warnings": False,
            }
        )
        try:
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

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_12(
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
            with yt_dlp.YoutubeDL(None) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_13(
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
            with yt_dlp.YoutubeDL(cast(None, ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_14(
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
            with yt_dlp.YoutubeDL(cast(Any, None)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_15(
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
            with yt_dlp.YoutubeDL(cast(ydl_opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_16(
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
            with yt_dlp.YoutubeDL(cast(Any, )) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_17(
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
                info = None
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_18(
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
                info = ydl.extract_info(None, download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_19(
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
                info = ydl.extract_info(video_url, download=None)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_20(
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
                info = ydl.extract_info(download=False)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_21(
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
                info = ydl.extract_info(video_url, )
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_22(
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
                info = ydl.extract_info(video_url, download=True)
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_23(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                None,
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_24(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                None,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_25(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                None,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_26(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_27(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_28(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_29(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "XXCould not extract channel URL from video '%s' via flat extraction: %sXX",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_30(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "could not extract channel url from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_31(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "COULD NOT EXTRACT CHANNEL URL FROM VIDEO '%S' VIA FLAT EXTRACTION: %S",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_32(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(None)

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_33(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(None, info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_34(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, None))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_35(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(info))

    def xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_36(
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
        except Exception as exc:  # noqa: BLE001 - Non-fatal discovery failure
            logger.debug(
                "Could not extract channel URL from video '%s' via flat extraction: %s",
                video_url,
                exc,
            )
            return None
        return extract_channel_url_from_info(cast(Any, ))

mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ__init____mutmut['xǁNativeMediaIngestionAdapterǁ__init____mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ__init____mutmut_19 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut['xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_detect_js_runtime__mutmut_7 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut['xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_ydl_opts__mutmut_19 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut['xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut['xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut['xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_extract_video_id__mutmut_3 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut['xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_sanitize_fs_name__mutmut_10 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut['xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_find_native_subtitle_url__mutmut_1 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_url_content__mutmut_17 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut['xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_reconstruct_json3_paragraphs__mutmut_1 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut['xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_handle_yt_dlp_error__mutmut_34 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_34 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_35'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_35 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_36'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_36 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_37'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_37 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_38'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_38 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_39'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_39 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_40'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_40 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_41'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_41 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_42'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_42 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_43'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_43 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_44'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_44 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_45'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_45 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_46'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_46 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_47'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_47 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_48'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_48 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_49'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_49 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_50'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_50 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_51'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_51 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_52'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_52 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_53'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_53 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_54'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_54 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_55'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_55 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_56'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_56 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_57'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_57 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_58'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_58 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_59'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_59 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_60'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_60 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_61'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_61 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_62'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_62 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_63'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_63 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_64'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_64 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_65'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_65 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_66'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_66 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_67'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_67 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_68'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_68 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_69'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_69 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_70'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_70 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_71'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_71 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_72'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_72 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_73'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_73 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_74'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_74 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_75'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_75 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_76'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_76 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_77'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_77 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_78'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_78 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_79'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_79 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_80'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_80 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_81'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_81 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_82'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_82 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_83'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_83 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut['xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_84'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_transcribe_audio_fallback__mutmut_84 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut['xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_fetch_video_metadata__mutmut_32 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_34 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_35'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_35 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_36'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_36 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_37'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_37 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_38'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_38 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_39'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_39 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_40'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_40 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_41'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_41 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_42'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_42 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_43'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_43 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_44'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_44 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_45'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_45 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_46'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_46 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_47'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_47 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_48'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_48 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_49'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_49 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_50'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_50 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_51'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_51 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_52'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_52 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_53'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_53 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_54'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_54 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_55'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_55 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut['xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_56'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_resolve_transcript_body__mutmut_56 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_34 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_35'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_35 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_36'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_36 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_37'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_37 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_38'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_38 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_39'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_39 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_40'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_40 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_41'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_41 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_42'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_42 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_43'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_43 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_44'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_44 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_45'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_45 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_46'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_46 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_47'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_47 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_48'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_48 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_49'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_49 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_50'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_50 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_51'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_51 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_52'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_52 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_53'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_53 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_54'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_54 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_55'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_55 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_56'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_56 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_57'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_57 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_58'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_58 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_59'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_59 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_60'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_60 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_61'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_61 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_62'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_62 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_63'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_63 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_64'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_64 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_65'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_65 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_66'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_66 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_67'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_67 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_68'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_68 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_69'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_69 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_70'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_70 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_71'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_71 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_72'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_72 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_73'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_73 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_74'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_74 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_75'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_75 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_76'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_76 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_77'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_77 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_78'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_78 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_79'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_79 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_80'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_80 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_81'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_81 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut['xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_82'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁ_build_raw_transcript_aggregate__mutmut_82 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_34 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_35'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_35 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_36'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_36 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_37'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_37 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_38'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_38 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_39'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_39 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_40'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_40 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_41'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_41 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_42'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_42 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_43'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_43 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_44'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_44 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_45'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_45 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_46'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_46 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_47'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_47 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_48'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_48 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_49'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_49 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_50'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_50 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_51'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_51 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_52'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_52 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_53'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_53 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_54'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_54 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_55'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_55 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_56'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_56 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_57'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_57 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_58'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_58 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_59'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_59 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_60'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_60 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_61'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_61 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_62'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_62 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut['xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_63'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁingest_single_video__mutmut_63 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut['xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁdiscover_channel_feed__mutmut_9 # type: ignore # mutmut generated

mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['_mutmut_orig'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_1'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_2'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_3'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_4'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_4 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_5'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_5 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_6'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_6 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_7'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_7 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_8'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_8 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_9'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_9 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_10'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_10 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_11'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_11 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_12'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_12 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_13'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_13 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_14'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_14 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_15'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_15 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_16'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_16 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_17'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_17 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_18'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_18 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_19'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_19 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_20'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_20 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_21'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_21 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_22'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_22 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_23'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_23 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_24'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_24 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_25'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_25 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_26'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_26 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_27'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_27 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_28'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_28 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_29'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_29 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_30'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_30 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_31'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_31 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_32'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_32 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_33'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_33 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_34'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_34 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_35'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_35 # type: ignore # mutmut generated
mutants_xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut['xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_36'] = NativeMediaIngestionAdapter.xǁNativeMediaIngestionAdapterǁextract_channel_url_from_video__mutmut_36 # type: ignore # mutmut generated
