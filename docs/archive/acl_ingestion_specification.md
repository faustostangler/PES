# Anti-Corruption Layer (ACL) Specification: Media Ingestion

**Target Context**: `playground/isb.ai/` → `src/cresmo/`  
**Phase**: Phase 1 — Stereoscopy  
**Status**: HISTORICAL SPECIFICATION (DECOMMISSIONED & SUPERSEDED by [`SPEC-004`](../specs/SPEC-004-native-media-ingestion.md) and [`ADR-004`](../adr/ADR-004-native-media-ingestion-decommissioning.md))  
**Governing ADR**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  
**Superseded By**: [`ADR-004: Native Media Ingestion & Legacy ISB.AI Decommissioning`](../adr/ADR-004-native-media-ingestion-decommissioning.md), [`SPEC-004`](../specs/SPEC-004-native-media-ingestion.md)  

> [!WARNING]
> **HISTORICAL / DECOMMISSIONED SPECIFICATION:**  
> This specification documents the transitional Anti-Corruption Layer initially designed to wrap legacy `playground/isb.ai/`.  
> Per [`ADR-004`](../adr/ADR-004-native-media-ingestion-decommissioning.md) and [`SPEC-004`](../specs/SPEC-004-native-media-ingestion.md):
> 1. `playground/isb.ai/` was **completely decommissioned and purged**.
> 2. `LegacyISBMediaIngestionAdapter` was replaced by `NativeMediaIngestionAdapter` (`src/cresmo/infrastructure/adapters/media_ingestion_adapter.py`) using direct `yt-dlp` and `whisper` calls with automatic scratch storage cleanup.
> 3. `RawTranscript` was **superseded by `SourceTranscript`** per [`ADR-010`](../adr/ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), and [`ADR-038`](../adr/ADR-038-pure-value-object-triad-composition.md).
> 4. For active production contracts, consult [`SPEC-004: Native Media Ingestion`](../specs/SPEC-004-native-media-ingestion.md).

---

## 1. Historical Problem Statement & Boundaries

`playground/cresmo/cresmo_ingestion.py` originally coupled directly to `playground/isb.ai/` using `sys.path.insert(0, str(ISB_DIR))` and altered global state like `downloader.RATE_LIMIT_LOG_FILE`.

To strangulate this legacy code without risking regressions in YouTube subtitle extraction or HTTP 429 mitigations, an Anti-Corruption Layer (ACL) was initially introduced before native decommissioning.

---

## 2. Port Contract (`MediaIngestionPort`)

Defined in `src/cresmo/application/ports/media.py` (modularized from `ports.py` per ADR-026; returning `SourceTranscript` per ADR-010/031/038):

```python
from abc import ABC, abstractmethod
from pathlib import Path
from cresmo.domain.entities import SourceTranscript
from cresmo.domain.value_objects import ContentId


class MediaIngestionPort(ABC):
    """Hexagonal Port interface for media ingestion and speech-to-text transcription."""

    @abstractmethod
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> SourceTranscript | None:
        """Fetch subtitles or transcribe audio for a single video.

        Returns:
            Domain SourceTranscript entity, or None if download/transcription failed.
        """
        raise NotImplementedError

    @abstractmethod
    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 365 * 2,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[SourceTranscript]:
        """Crawl channels/playlists and ingest all new videos within lookback window.

        Returns:
            List of newly ingested SourceTranscript domain entities.
        """
        raise NotImplementedError
```

---

## 3. Historical ACL Adapter Architecture (`LegacyISBMediaIngestionAdapter`)

Retained as historical record of Phase 1 strangulation. In active production, `NativeMediaIngestionAdapter` implements `MediaIngestionPort` directly without legacy dependencies.
