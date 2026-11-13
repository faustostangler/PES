# SPEC-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion

**Status:** ACCEPTED  
**Date:** 2026-11-10  
**Governing ADRs:** [`ADR-054`](../adr/ADR-054-unified-stage-transcript-envelope.md), [`ADR-056`](../adr/ADR-056-native-media-ingestion-channel-name-deduplication.md), [`ADR-057`](../adr/ADR-057-monomorphic-stage-transcript-envelope-and-pure-triad-ingestion.md)  
**Domain Layer:** `cresmo.domain.entities`, `cresmo.infrastructure.adapters.native_media_ingestion_adapter`

---

## 1. Specification Requirements

1. **Monomorphic `StageTranscript` Envelope (`transcripts.py`, `compendium.py`):**
   - Composed strictly of the 3-VO Triad (`channel: Channel`, `provenance: MediaProvenance`, `content: Content`), `metadata: dict[str, Any]`, `complementary_info: str = ""`, and `pass_count: int | None = None`.
   - Zero loose primitive keyword arguments in `__init__`.
   - Validates `isinstance` on `Channel`, `MediaProvenance`, and `Content`, non-empty `content.body`, and `pass_count >= 1` when provided.
   - Zero Markdown table regex (`_TABLE_PATTERN`) in domain entity invariants.
2. **Transparent Specialized Envelopes:**
   - `SourceTranscript`, `FluidTranscript`, and `EnrichedCompendium` inherit directly from `StageTranscript` with monomorphic constructors.
3. **Ingestion Channel Deduplication & Dynamic URL (`native_media_ingestion_adapter.py`, `channel.py`):**
   - `NativeMediaIngestionAdapter._extract_channel_name` centralizes channel name sanitization prior to subtitle/audio extraction.
   - `Channel.url` derives `https://www.youtube.com/channel/{self.id.value}` when explicit `_url` is absent and `id` is canonical.
   - `Content.create` infers `ContentId` from `url` when `id` is omitted.

