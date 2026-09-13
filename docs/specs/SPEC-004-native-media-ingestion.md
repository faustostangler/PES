# SPEC-004: Native Media Ingestion Adapter & ISB.AI Decommissioning

**Status:** APPROVED  
**Date:** 2026-09-11  
**Author:** Doctor Stangler Architecture Committee  
**Governing ADR:** [`ADR-004: Native Media Ingestion & Legacy ISB.AI Decommissioning`](../adr/ADR-004-native-media-ingestion-decommissioning.md)  
**Port Contract:** [`MediaIngestionPort`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/application/ports.py)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)

---

## 1. Specification Overview

This specification establishes the exact behavioral contracts, boundary invariants, and test verification suite for `NativeMediaIngestionAdapter` in `src/cresmo/infrastructure/adapters/native_media_ingestion_adapter.py`.

It fulfills `MediaIngestionPort` directly using `yt-dlp` and `openai-whisper` Python library APIs, eliminating runtime `sys.path` tampering, preventing intermediate audio file leakage on disk via RAII temporary scratch directories, and allowing the clean decommissioning of `playground/isb.ai/`.

---

## 2. Acceptance Criteria & Behavioral Scenarios

### Scenario 1: Native Subtitles Discovery & Extraction
- **Given**: A video URL whose metadata contains native spoken subtitles (e.g. `pt-orig`, `pt-BR`, `pt`, `en-orig`, `en`).
- **When**: `adapter.ingest_single_video(video_url, output_dir)` is executed.
- **Then**:
  1. The adapter downloads the subtitle payload (`json3` format preferred) directly via HTTP.
  2. Reconstructs text events into readable, coherent paragraph prose.
  3. Returns a valid `RawTranscript` domain entity with `content_id`, `channel_name`, and `body`.
  4. **No audio download** is triggered, saving bandwidth and compute.
  5. The transcript is optionally cached to `output_dir/[Channel]/[content_id].txt`.

### Scenario 2: Rejection of Machine-Translated Captions (`tlang=`)
- **Given**: A video URL whose subtitle metadata only contains on-the-fly machine translations (indicated by `tlang=` query parameter in format URLs).
- **When**: The subtitle finder parses available caption tracks.
- **Then**:
  1. All tracks containing `tlang=` are filtered out and rejected to mitigate YouTube HTTP 429 rate-limiting.
  2. If no valid native subtitle remains, the adapter gracefully falls back to Scenario 3 (Whisper Fallback).

### Scenario 3: Whisper Local Transcription Fallback with Ephemeral Scratch Cleanup
- **Given**: A video URL with no valid native subtitle tracks available.
- **When**: `adapter.ingest_single_video(video_url, output_dir, whisper_model="base", keep_audio=False)` is executed.
- **Then**:
  1. The adapter creates an isolated temporary directory via `tempfile.TemporaryDirectory()`.
  2. `yt-dlp` extracts and downloads the audio stream into the temporary directory (e.g., `scratch/audio.m4a`).
  3. `whisper.load_model(whisper_model).transcribe(audio_path)` transcribes the audio into verbatim text.
  4. The temporary directory and downloaded audio are completely destroyed upon exiting the context block, leaving **zero orphaned audio files on disk**.
  5. If `keep_audio=True`, the audio file is preserved inside `output_dir/[Channel]/`.
  6. Returns a valid `RawTranscript` domain entity.

### Scenario 4: Fast Channel Feed Discovery (`discover_channel_feed`)
- **Given**: A `ChannelFeedQuery` containing `channel_url`, `lookback_days`, and `max_videos`.
- **When**: `adapter.discover_channel_feed(query)` is executed.
- **Then**:
  1. `yt-dlp` executes flat playlist extraction (`extract_flat=True`, `playlistend=max_videos`).
  2. Extracts metadata (`id`, `title`, `upload_date` or `timestamp`, `url`, `channel`).
  3. Returns a list of strongly-typed `DiscoveredMediaItem` value objects.
  4. Total execution time is <2 seconds (no media downloads).

### Scenario 5: Error Translation & Boundary Protection
- **Given**: An upstream network partition or YouTube server failure.
- **When**: `yt-dlp` raises an exception during ingestion or extraction.
- **Then**:
  1. If the exception message or HTTP code indicates `429` or `Too Many Requests`: Translated to `RateLimitExceededError`.
  2. If connection timeout, DNS failure, or socket error: Translated to `IngestionNetworkError`.
  3. Any other unrecoverable media formatting failure: Translated to `CresmoInfrastructureError`.
  4. No raw `yt_dlp` internal exceptions leak outside the adapter boundary.

---

## 3. Boundary Conditions & Resource Invariants

1. **Deterministic Scratch Lifecycles**:
   - `tempfile.TemporaryDirectory(prefix="cresmo_scratch_")` must be used as a context manager.
   - Handlers for `KeyboardInterrupt` and general exceptions must guarantee that temp files are purged.
2. **Channel Name Sanitization**:
   - Channel names from metadata must be sanitized of illegal directory characters (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) before constructing output paths.
3. **Empty Output Validation**:
   - Transcripts resulting in empty or pure whitespace bodies raise `DomainValidationError("Extracted transcript body cannot be empty.")`.

---

## 4. Testing Strategy (Hermetic & Deterministic)

Unit tests in `tests/cresmo/unit/test_native_media_ingestion_adapter.py` will mock external boundaries to guarantee fast, deterministic execution (<1s test suite):
- `patch("yt_dlp.YoutubeDL")`: Mock metadata extraction, subtitle downloads, and audio extraction without touching network or YouTube.
- `patch("whisper.load_model")`: Mock Whisper neural network loading and `transcribe()` to return deterministic text dictionaries (`{"text": "Sample transcript"}`).
- Test coverage must include:
  - Native subtitle extraction path.
  - Rejection of `tlang=` URL format tracks.
  - Whisper fallback path and verification of temporary directory cleanup.
  - Error translation: HTTP 429 $\rightarrow$ `RateLimitExceededError`, network drop $\rightarrow$ `IngestionNetworkError`.
  - Channel feed flat discovery with query limits.

---

## 5. Decommissioning & Archival Gate

- [x] `NativeMediaIngestionAdapter` implemented and verified with 100% test pass.
- [x] `src/cresmo/presentation/composition.py` switched to `build_ingestion_adapter() -> NativeMediaIngestionAdapter`.
- [x] `LegacyIsbIngestionAdapter` and `tests/cresmo/unit/test_legacy_ingestion_adapter.py` removed.
- [x] `pyproject.toml` updated to remove `playground/isb.ai` from `extraPaths`.
- [x] `playground/isb.ai/` marked as archived legacy code.
- [x] Zero regressions across the workspace test suite (`uv run pytest`).
- [x] Static typing passes cleanly: `uv run mypy --strict src/cresmo`.
- [x] Linter & formatter clean: `uvx ruff check src/cresmo tests/cresmo`.
