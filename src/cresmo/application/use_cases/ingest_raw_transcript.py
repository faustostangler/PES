"""Use Case: Ingest Raw Transcript.

Orchestrates media crawling and audio/subtitle transcription through MediaIngestionPort
and persists the resulting StageTranscript domain aggregate into the vault raw storage.

Conforms to:
- SPEC-001: §1 (Raw Transcript Ingestion)
- SPEC-004: Native Media Ingestion Specifications
- ADR-004: Native Media Ingestion Decommissioning
"""

from __future__ import annotations

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.domain.entities import StageTranscript
from cresmo.domain.stage_registry import StageName


class IngestRawTranscriptUseCase:
    """Media Ingestion & Speech-to-Text Orchestrator."""

    def __init__(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
    ) -> None:
        """Initialize use case with required Hexagonal ports.

        Args:
            ingestion_port: Port providing access to yt-dlp/whisper ingestion.
            vault_port: Port providing raw storage persistence.
        """
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port

    def execute(self, video_url: str) -> StageTranscript | None:
        """Execute raw ingestion for a target media item.

        Args:
            video_url: Target media URL.

        Returns:
            StageTranscript domain aggregate if ingestion succeeded, or None on failure.
        """
        raw = self.ingestion_port.ingest_single_video(video_url=video_url)
        if raw is not None:
            self.vault_port.save_stage_transcript(StageName.RAW, raw)
        return raw
