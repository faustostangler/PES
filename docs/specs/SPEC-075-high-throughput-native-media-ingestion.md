# SPEC-075: High-Throughput Native Media Ingestion Specifications

- **Related ADR:** [ADR-075](../adr/ADR-075-high-throughput-native-media-ingestion.md)
- **Status:** Accepted
- **Date:** 2026-11-23

---

## 1. `SPEC-075.1` — `yt-dlp` Metadata Manifest Pruning & One-Shot Plugin Loading

### Acceptance Criteria
1. `NativeMediaIngestionAdapter._fetch_video_metadata` configures `yt_dlp.YoutubeDL` with:
   - `"skip_download": True`
   - `"ignore_no_formats_error": True`
   - `"extractor_args": {"youtube": {"skip": ["dash", "hls", "translated_subs"]}}`
2. `NativeMediaIngestionAdapter._transcribe_audio_fallback` must **not** inject `"skip": ["dash", "hls", ...]` or `"ignore_no_formats_error"` so `"format": "bestaudio/best"` continues selecting and downloading audio streams cleanly.
3. `ensure_yt_dlp_plugins_loaded()` in `src/cresmo/infrastructure/adapters/media/subtitles.py` uses a module-level lock (`_PLUGINS_LOCK`) and boolean cache (`_PLUGINS_LOADED`) so `yt_dlp.plugins.load_all_plugins()` executes once per process after succeeding; if `load_all_plugins()` raises an exception, `_PLUGINS_LOADED` stays `False` so a subsequent call may retry. Provide `_reset_yt_dlp_plugins_cache()` for hermetic tests.

### Test Mapping
- `test_fetch_video_metadata_options_and_success` asserts `ignore_no_formats_error` and `extractor_args`.
- `test_transcribe_audio_fallback_keep_audio_and_cleanup` asserts `"extractor_args"` is absent from audio download `ydl_opts`.
- Dedicated test verifies `ensure_yt_dlp_plugins_loaded()` invokes `load_all_plugins()` only once across multiple invocations.

---

## 2. `SPEC-075.2` — YouTube Atom RSS Feed Fast-Path (`feed.py`)

### Acceptance Criteria
1. `YOUTUBE_RSS_MAX_ENTRIES: Final[int] = 15`.
2. `resolve_youtube_rss_url(channel_url: str) -> str | None`:
   - Extracts canonical `UC...` ID via `ChannelId.extract_from_text` -> returns `https://www.youtube.com/feeds/videos.xml?channel_id={UC...}`.
   - Detects `list=(UU...|PL...)` query parameter:
     - `UU...` with canonical YouTube length (`>= 24`) maps `UU` -> `UC` and returns `https://www.youtube.com/feeds/videos.xml?channel_id=UC...`.
     - `PL...` (or non-canonical list ID) returns `https://www.youtube.com/feeds/videos.xml?playlist_id={id}`.
   - `@Handle` URLs, non-YouTube URLs, and arbitrary strings without an extractable ID return `None`.
3. `parse_youtube_atom_feed(xml_payload: str, sanitize_fs_name: Callable[[str], str]) -> list[DiscoveredMediaItem]`:
   - Parses Atom XML via `xml.etree.ElementTree.fromstring`.
   - Extracts `yt:videoId`, `title`, `link[@rel="alternate"]` (falling back to `https://www.youtube.com/watch?v={vid}`), `published` (ISO-8601 normalized to UTC `datetime`), and feed `<title>` / `<author>/<name>` sanitized via `sanitize_fs_name`.
   - Skips entries missing video ID or title cleanly.
4. `is_rss_feed_window_complete(items: list[DiscoveredMediaItem], query: ChannelFeedQuery, now: datetime | None = None) -> bool`:
   - Returns `False` when `items` is empty.
   - Returns `True` if `len(items) < YOUTUBE_RSS_MAX_ENTRIES`.
   - Returns `True` if `query.max_videos <= YOUTUBE_RSS_MAX_ENTRIES`.
   - Returns `True` if `min(item.published_at for item in items) < resolved_now - timedelta(days=query.lookback_days)` (RSS window already spans past the lookback cutoff).
   - Otherwise returns `False` (window may be truncated beyond 15 recent videos; requires `yt-dlp` fallback).
5. `discover_channel_feed_items(..., fetch_rss_xml: Callable[[str], str] | None = None, enable_rss_fast_path: bool = True)`:
   - Attempts RSS fast-path when `enable_rss_fast_path=True`, `fetch_rss_xml is not None`, and `resolve_youtube_rss_url(query.channel_url)` is non-`None`.
   - When `is_rss_feed_window_complete(...)` holds, returns `items[:query.max_videos]` without invoking `yt_dlp.YoutubeDL`.
   - On any fetch/XML exception, empty feed, or incomplete window, logs via `structlog` and falls back seamlessly to `yt-dlp` flat playlist extraction.
6. `NativeMediaIngestionAdapter.discover_channel_feed` wires `fetch_rss_xml=self._fetch_url_content` and `enable_rss_fast_path=self._enable_rss_fast_path`.

---

## 3. `SPEC-075.3` — Pooled, Deferred `httpx.Client` (HTTP/2-Enabled)

### Acceptance Criteria
1. `NativeMediaIngestionAdapter` removes all `urllib.request` / `urllib.error` imports (`ADR-010`).
2. `__init__` accepts `http_client: httpx.Client | None = None` without eagerly instantiating a client when `None` (`ADR-055`).
3. `_get_http_client()` lazily constructs (under `threading.Lock`) an `httpx.Client` with:
   - `timeout=self.request_timeout`
   - `limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)`
   - `follow_redirects=True`
   - `http2=importlib.util.find_spec("h2") is not None`
4. `close()`, `__enter__()`, and `__exit__()` deterministically close only owned `httpx.Client` instances (`_owns_http_client=True`). Injected clients are never closed by the adapter.
5. `_fetch_url_content(url: str) -> str`:
   - Calls `client.get(url, headers=self._header_generator.get_random_headers())` and `response.raise_for_status()`.
   - Maps `httpx.HTTPStatusError` with status `429` -> `RateLimitExceededError`.
   - Maps all other `httpx.HTTPStatusError`, `httpx.HTTPError`, and unexpected transport exceptions -> `IngestionNetworkError`.

---

## 4. `SPEC-075.4` — `FasterWhisperEngine` (`faster-whisper` / CTranslate2)

### Acceptance Criteria
1. Module `src/cresmo/infrastructure/adapters/media/transcriber.py` defines `FasterWhisperEngine`:
   - `__init__(self, concurrency_limit: int = 2, device: str = "auto", compute_type: str = "auto", vad_filter: bool = True)`.
   - Zero top-level imports of `faster_whisper` or `ctranslate2`.
2. `resolve_device() -> str`:
   - Returns explicit device when `device != "auto"`.
   - When `device == "auto"`, lazily imports `ctranslate2`; returns `"cuda"` if `ctranslate2.get_cuda_device_count() > 0`, otherwise `"cpu"` (including if probing raises an exception).
3. `resolve_compute_type(resolved_device: str) -> str`:
   - Returns explicit compute type when `compute_type != "auto"`.
   - When `compute_type == "auto"`, returns `"float16"` for `"cuda"` and `"int8"` for all other devices.
4. Thread-safe model cache (`dict[tuple[str, str, str], Any]` protected by `threading.Lock`) caches `WhisperModel(model_name, device=resolved_device, compute_type=resolved_compute_type)` across repeated `transcribe()` calls; `clear_cache()` empties the cache.
5. `transcribe(audio_path: Path, model_name: str) -> str`:
   - Acquires `threading.BoundedSemaphore(max(1, concurrency_limit))`.
   - Calls `model.transcribe(str(audio_path), vad_filter=self._vad_filter)` and joins non-empty stripped `segment.text` strings with `" "`, stripping outer whitespace.
   - Wraps any load or inference exception in `CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc`.
6. `NativeMediaIngestionAdapter` accepts optional `transcriber: FasterWhisperEngine | None = None`, defaulting to an instance configured from `whisper_concurrency_limit`, `whisper_device`, `whisper_compute_type`, and `whisper_vad_filter`, and delegates `_transcribe_audio_fallback` STT execution to it.

---

## 5. `SPEC-075.5` — `IngestionSettings` & Bootstrap Wiring

### Acceptance Criteria
1. `IngestionSettings` (`src/cresmo/infrastructure/config/ingestion.py`) adds frozen fields:
   - `whisper_device: Literal["auto", "cpu", "cuda"] = "auto"`
   - `whisper_compute_type: Literal["auto", "int8", "int8_float16", "float16", "float32"] = "auto"`
   - `whisper_vad_filter: bool = True`
   - `enable_rss_fast_path: bool = True`
2. `build_media_ingestion_adapter` (`src/cresmo/bootstrap/factories/adapter_factory.py`) wires all four settings from `resolved.ingestion` into `NativeMediaIngestionAdapter`.
3. `.env.example` documents commented `CRESMO_INGESTION__WHISPER_DEVICE`, `CRESMO_INGESTION__WHISPER_COMPUTE_TYPE`, `CRESMO_INGESTION__WHISPER_VAD_FILTER`, and `CRESMO_INGESTION__ENABLE_RSS_FAST_PATH` keys.

---

## 6. `SPEC-075.6` — Lazy Import Hygiene

### Acceptance Criteria
1. Importing `cresmo.presentation.cli` or `NativeMediaIngestionAdapter` in a fresh Python subprocess must **not** import `"faster_whisper"`, `"ctranslate2"`, `"whisper"`, or `"torch"`.

