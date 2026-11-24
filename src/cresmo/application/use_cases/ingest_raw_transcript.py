"""Use Case: Ingest Raw Transcript.

Orchestrates media crawling and audio/subtitle transcription through MediaIngestionPort
and persists the resulting StageTranscript domain aggregate into the vault raw storage.

Conforms to:
- SPEC-001: §1 (Raw Transcript Ingestion)
- SPEC-004: Native Media Ingestion Specifications
- ADR-004: Native Media Ingestion Decommissioning
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.domain.entities import StageTranscript


class IngestRawTranscriptUseCase:
    """Media Ingestion & Speech-to-Text Orchestrator."""

    def __init__(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
        default_whisper_model: str = "base",
    ) -> None:
        """Initialize use case with required Hexagonal ports.

        Args:
            ingestion_port: Port providing access to yt-dlp/whisper ingestion.
            vault_port: Port providing raw storage persistence.
            raw_storage_dir: Directory where raw text transcripts and audio scratch reside.
            default_whisper_model: Default Whisper STT checkpoint name from settings.
        """
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("raw")
        self.default_whisper_model = default_whisper_model

    def execute(
        self,
        video_url: str,
        whisper_model: str | None = None,
        keep_audio: bool = False,
    ) -> StageTranscript | None:
        """Execute raw ingestion for a target media item.

        Args:
            video_url: Target media URL.
            whisper_model: Optional Whisper model checkpoint override.
            keep_audio: If True, preserves downloaded audio; otherwise cleans scratch.

        Returns:
            StageTranscript domain aggregate if ingestion succeeded, or None on failure.
        """
        resolved_whisper_model = whisper_model or self.default_whisper_model
        raw = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            output_dir=self.raw_storage_dir,
            whisper_model=resolved_whisper_model,
            keep_audio=keep_audio,
        )
        if raw is not None:
            self.vault_port.save_stage_transcript("raw", raw)
        return raw
