# ADR-075: High-Throughput Native Media Ingestion (Metadata Pruning, Atom RSS Fast-Path, Pooled HTTPX & Faster-Whisper)

| Field          | Value                                                                                      |
|----------------|--------------------------------------------------------------------------------------------|
| **Status**     | ACCEPTED                                                                                   |
| **Date**       | 2026-11-23                                                                                 |
| **Authors**    | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)            |
| **Scope**      | Cresmo Knowledge Synthesis Bounded Context — Infrastructure Media ACL, Config & Bootstrap  |
| **Refines**    | ADR-004, ADR-053, ADR-056                                                                  |
| **Relates**    | ADR-000, ADR-004, ADR-010, ADR-020, ADR-026, ADR-053, ADR-055, ADR-056, ADR-074            |

---

## 1. Context & Architectural Motivation

While [ADR-004](ADR-004-native-media-ingestion-decommissioning.md) established `NativeMediaIngestionAdapter` using `yt-dlp` and `openai-whisper`, keeping `yt-dlp` (+ `yt-dlp-ejs`) remains the SOTA-KISS choice because it absorbs YouTube `n-sig` JS challenges, Netscape session cookies, and multi-platform extraction in one dependency. However, profiling the ingestion pipeline exposed four internal bottlenecks:

1. **Redundant Media Manifest Parsing & Repeated Plugin Scans:** `_fetch_video_metadata` calls `yt_dlp.YoutubeDL.extract_info(..., download=False)` without pruning DASH/HLS manifests or translated caption tracks, triggering unnecessary JavaScript challenge work and format resolution when only video metadata and native subtitles are needed. Additionally, `ensure_yt_dlp_plugins_loaded()` re-scans plugin entrypoints on every call.
2. **Heavyweight `yt-dlp` Extraction for Recent Channel Feeds:** `discover_channel_feed` invokes `yt-dlp` flat playlist extraction even for routine recent channel checks where YouTube's public Atom RSS feed (`/feeds/videos.xml`) serves the latest 15 items in sub-200ms without JS runtime or anti-bot overhead.
3. **Unpooled `urllib.request` Connections:** `_fetch_url_content` opens fresh TCP/TLS connections via `urllib.request.urlopen` on every subtitle download, missing connection pooling, keep-alive reuse, and HTTP/2 multiplexing.
4. **Slow PyTorch `openai-whisper` Fallback & Per-Call Model Reloading:** `_transcribe_audio_fallback` loads `openai-whisper` via PyTorch and re-instantiates `whisper.load_model()` on every fallback call, inflating latency (4x–8x slower than CTranslate2) and memory footprint.

---

## 2. Decision

We will retain `yt-dlp` as the extraction engine and optimize `NativeMediaIngestionAdapter` across four cohesive Infrastructure pillars while keeping `MediaIngestionPort` and Domain models completely unchanged:

### Pillar 1: `MetadataManifestPruning` & Idempotent Plugin Loading
1. `_fetch_video_metadata` passes `"ignore_no_formats_error": True` and `"extractor_args": {"youtube": {"skip": ["dash", "hls", "translated_subs"]}}`. Audio fallback (`_transcribe_audio_fallback`) does **not** set these skip arguments so `bestaudio/best` stream selection remains intact.
2. `ensure_yt_dlp_plugins_loaded()` is guarded by a thread-safe one-shot cache (`_PLUGINS_LOCK` + `_PLUGINS_LOADED`), caching success so `yt_dlp.plugins.load_all_plugins()` runs once per process.

### Pillar 2: `AtomRssFeedFastPath` with Completeness-Guaranteed Fallback
1. `discover_channel_feed_items` resolves canonical YouTube channel IDs (`UC...` or `list=UU...` mapped to `UC...`) to `https://www.youtube.com/feeds/videos.xml?channel_id={UC...}` and playlist IDs (`list=PL...`) to `https://www.youtube.com/feeds/videos.xml?playlist_id={PL...}`. Non-canonical URLs (such as `@Handle` URLs without an ID) return `None` and skip directly to `yt-dlp`.
2. RSS XML payloads are fetched through the adapter's pooled HTTP client and parsed with stdlib `xml.etree.ElementTree` into `DiscoveredMediaItem` objects (UTC `published_at`, sanitized `ChannelName`, `ContentId`).
3. Fast-path results are returned **only** when window completeness is mathematically guaranteed: non-empty entries AND (`len(items) < 15` OR `query.max_videos <= 15` OR `min(published_at) < now_utc - timedelta(days=query.lookback_days)`).
4. If the fast-path is disabled (`enable_rss_fast_path=False`), URL resolution yields `None`, the window is incomplete, or any HTTP/XML error occurs, discovery logs the fallback via `structlog` and falls back transparently to `yt-dlp` flat playlist extraction.

### Pillar 3: Pooled, Deferred `httpx.Client` (HTTP/2-Enabled)
1. Remove `urllib.request` and `urllib.error` completely (`ADR-010`).
2. Lazily initialize (`ADR-055`) a shared thread-safe `httpx.Client` with `httpx.Limits(max_connections=20, max_keepalive_connections=10)`, `follow_redirects=True`, `timeout=self.request_timeout`, and `http2=True` when `h2` is installed (`httpx[http2]`).
3. Support optional injected `http_client: httpx.Client | None = None` for testability and deterministic lifecycle cleanup via `close()` and `__enter__`/`__exit__` (closing only owned clients).
4. Preserve exact domain error translation: HTTP `429` -> `RateLimitExceededError`; all other `httpx.HTTPStatusError`, `httpx.HTTPError`, or transport errors -> `IngestionNetworkError`.

### Pillar 4: `FasterWhisperEngine` (`faster-whisper` / CTranslate2)
1. Replace `openai-whisper` with `faster-whisper` (`CTranslate2`) encapsulated in `src/cresmo/infrastructure/adapters/media/transcriber.py`.
2. Enforce strict lazy imports (`ADR-053`): `faster_whisper` and `ctranslate2` are imported only inside `FasterWhisperEngine` methods, never at module import time.
3. Hardware auto-detection (`whisper_device="auto"`, `whisper_compute_type="auto"`): selects `cuda` + `float16` when `ctranslate2.get_cuda_device_count() > 0`, degrading gracefully to `cpu` + `int8`. Explicit overrides remain supported.
4. Enable Silero VAD filtering by default (`whisper_vad_filter=True`), cache loaded `WhisperModel` instances thread-safely by `(model_name, device, compute_type)`, and guard concurrent transcription via `threading.BoundedSemaphore`.
5. Expose `whisper_device`, `whisper_compute_type`, `whisper_vad_filter`, and `enable_rss_fast_path` on frozen `IngestionSettings` (`ADR-074`) and wire them in `build_media_ingestion_adapter`.

---

## 3. Bounded Context & Domain Model Impact

- **Bounded Context:** Cresmo Knowledge Synthesis (`src/cresmo/`). Changes are strictly confined to Infrastructure (`adapters/media/`, `config/ingestion.py`), `bootstrap/factories/adapter_factory.py`, `pyproject.toml`, and `.env.example`.
- **Domain & Application Purity:** Zero modifications to `src/cresmo/domain/` or `MediaIngestionPort` (`src/cresmo/application/ports/media.py`). `DiscoveredMediaItem`, `ChannelFeedQuery`, and `StageTranscript` contracts remain invariant.

---

## 4. Alternatives Considered

1. **Replace `yt-dlp` with `pytubefix`:**
   - Rejected: YouTube-only scope and frequent breakages around PO-token / bot-detection changes; loses multi-platform resilience and `yt-dlp-ejs` maintenance.
2. **Replace `yt-dlp` with `youtube-transcript-api` + YouTube Data API v3:**
   - Rejected: `youtube-transcript-api` cannot extract full video metadata (`description`, `upload_date`, `channel_url`) or download audio for Whisper fallback; Data API v3 introduces API key provisioning and daily quota ceilings.
3. **Retain `openai-whisper` (PyTorch) with Manual Model Caching:**
   - Rejected: PyTorch Whisper inference runs 4x–8x slower on CPU/GPU than CTranslate2 INT8/FP16 and lacks built-in Silero VAD filtering, keeping fallback transcription a latency and RAM bottleneck.

---

## 5. Consequences, Observability, Security & LGPD

- **Positive:**
  - Faster single-video metadata/subtitle extraction via DASH/HLS manifest pruning and pooled HTTP/2 `httpx.Client`.
  - Sub-200ms channel feed checks for recent uploads via YouTube Atom RSS without hitting `yt-dlp` JS runtimes.
  - 4x–8x faster audio fallback transcription with lower RAM overhead and zero repeated model reloads.
  - Preserves instant CLI startup (`ADR-053` / `ADR-055`) via deferred `httpx.Client` and lazy `faster_whisper` loading.
- **Negative / Trade-offs:**
  - `httpx[http2]` adds `h2` as a lightweight dependency; `faster-whisper` replaces `openai-whisper` in `pyproject.toml` (breaking `import whisper` callers, mitigated by keeping all STT behind `FasterWhisperEngine` ACL).
- **Observability:** Preserves `cresmo_media_ingestion_duration_seconds` Prometheus histogram; RSS fast-path hits/fallbacks emit structured `structlog` debug/warning events without PII.
- **Security & LGPD:** Atom XML parsing uses Python stdlib `xml.etree.ElementTree` (immune to external entity expansion); `httpx.Client` applies `request_timeout` and dynamic browser headers; no cookies or credentials are written to RSS requests.

---

## 6. Test & Mutation Strategy

- **Unit Tests:** Hermetic suites covering `FasterWhisperEngine` (auto hardware probe, explicit overrides, `(model, device, compute_type)` caching, semaphore concurrency, VAD forwarding, error wrapping), `feed.py` RSS resolution/parsing/completeness/fallback, `NativeMediaIngestionAdapter` (`httpx` pooling/lifecycle, metadata skip args vs. audio download args, idempotent plugin loading), `IngestionSettings` validation, and subprocess lazy-import verification (`faster_whisper`, `ctranslate2`, `whisper`, `torch` absent on CLI/adapter import).
- **Verification Gate:** Targeted infrastructure/config/bootstrap/lazy-CLI `pytest` suites green, `ruff check` & `ruff format --check` clean, `mypy --strict` zero errors.

