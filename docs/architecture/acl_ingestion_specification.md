# Anti-Corruption Layer (ACL) Specification: Media Ingestion

**Target Context**: `playground/isb.ai/` → `src/cresmo/`  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION  
**Governing ADR**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  

---

## 1. Problem Statement & Boundaries

`playground/cresmo/cresmo_ingestion.py` currently couples directly to `playground/isb.ai/` using `sys.path.insert(0, str(ISB_DIR))` and alters global state like `downloader.RATE_LIMIT_LOG_FILE`.

To strangulate this legacy code without risking regressions in YouTube subtitle extraction or HTTP 429 mitigations, an Anti-Corruption Layer (ACL) is mandatory.

---

## 2. Port Contract (`MediaIngestionPort`)

Defined in `src/cresmo/application/ports.py`:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from cresmo.domain.entities import RawTranscript
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
    ) -> RawTranscript | None:
        """Fetch subtitles or transcribe audio for a single video.

        Returns:
            Domain RawTranscript entity, or None if download/transcription failed.
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
    ) -> list[RawTranscript]:
        """Crawl channels/playlists and ingest all new videos within lookback window.

        Returns:
            List of newly ingested RawTranscript domain entities.
        """
        raise NotImplementedError
```

---

## 3. ACL Adapter Architecture (`LegacyISBMediaIngestionAdapter`)

Defined in `src/cresmo/infrastructure/adapters/legacy_isb_ingestion_adapter.py`:

### 3.1 Cognitive & Process Isolation
1. **Isolated Import Execution**:
   - The adapter manages `sys.path` locally during initialization or subprocess execution, ensuring `sys.path` tampering NEVER pollutes the clean Domain or Application layers.
2. **Global State Encapsulation**:
   - The adapter intercepts global variables (like `downloader.RATE_LIMIT_LOG_FILE`) and sets them from `CresmoConfig` before executing legacy methods.
3. **Data Translation Boundary**:
   - Converts legacy YAML headers and text dumps into pure `RawTranscript` domain entities with strongly-typed `ContentId`.
   - Strips legacy file paths and internal metadata.
4. **Exception Shielding**:
   - Catches legacy exceptions (`yt_dlp.utils.DownloadError`, `urllib.error.HTTPError`) and translates them into domain exceptions (`IngestionNetworkError`, `RateLimitExceededError`).
