# ADR-056: Native Media Ingestion Channel Name Deduplication and Domain Triad Simplification

## Status
ACCEPTED (Turn 3 — Green + Refactor)

## Context
1. **Ingestion Duplication & Telemetry Drift**:
   In `NativeMediaIngestionAdapter`, channel extraction and sanitization (`self._sanitize_fs_name(str(info.get("channel") or info.get("uploader") or "Unknown_Channel"))`) was duplicated between `_resolve_transcript_body` and `_transcribe_audio_fallback`.
   Both methods redundantly returned `tuple[str, str]` (`body, channel_name`) to `ingest_single_video`.
   Moreover, if transcription resolution failed, `ingest_single_video` logged `"Unknown_Channel"` in Prometheus duration metrics even when `info` had already resolved the channel name.
2. **Domain Triad Redundancy & Lack of Invariant Guards**:
   In the 3-VO Triad (`Channel`, `MediaProvenance`, `Content`):
   - `Channel.url`: Stored redundant URL strings identical to `https://www.youtube.com/channel/{channel.id.value}` when no custom handle existed.
   - `Content.create` & `StageTranscript.create`: Required explicit duplicate `content_id` even when `source_url` already contained the extractable ID.
   - `SourceTranscript`: Lacked invariant enforcement ensuring `content.id` and `provenance.url` refer to the same media item.

---

## Decision

### 1. Ingestion Adapter Clean Refactoring (No Backwards Compatibility)
- Add `_extract_channel_name(self, info: Mapping[str, Any]) -> str` to `NativeMediaIngestionAdapter`.
- In `ingest_single_video`, extract `channel_name` immediately after `_fetch_video_metadata` to guarantee accurate telemetry in `finally:`.
- Simplify `_resolve_transcript_body` and `_transcribe_audio_fallback` signatures to return only `str` (body payload). No legacy tuple return shims.

### 2. Dynamic Channel URL Fallback (`Channel` Value Object)
- In `Channel`, store explicit URL in `_url: str | None`.
- Expose `@property def url(self) -> str | None`:
  If `_url` is provided (e.g. `@handle`), return it.
  Otherwise, if `self.id` is present, derive canonical URL: `f"https://www.youtube.com/channel/{self.id.value}"`.

### 3. Automatic Content ID Inference (`Content.create` & `StageTranscript`)
- In `Content.create(id=None, title="", body="", *, url="")`:
  If `id` is omitted, automatically extract it from `url` using `ContentId.extract_from_text(url)`.
- In `StageTranscript.__init__`:
  If `content_id` is omitted or None, automatically infer it from `source_url` if present before falling back to `"unknown"`.

### 4. SourceTranscript Invariant Validation
- In `SourceTranscript._validate_stage_invariants()`:
  Validate that when `self.provenance.url` contains an extractable video ID, it must match `self.content.id`. Raise `DomainValidationError` on mismatch.

---

## Consequences

### Positive
- Zero duplication of channel name resolution logic.
- Robust Prometheus telemetry recording actual channel names even during fatal transcription failures.
- Zero boilerplate in `Content` and `Channel` instantiation: URLs and IDs cross-infer cleanly.
- Domain integrity guaranteed by invariant enforcement between provenance and content identity.
- Clean modern codebase with zero obsolete backwards compatibility shims.

### Negative / Trade-offs
- Callers and tests expecting `tuple[str, str]` from private adapter methods must use `str`.
