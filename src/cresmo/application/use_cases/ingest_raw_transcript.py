"""Stage 1 Use Case: Ingest Raw Transcript.

Orchestrates media crawling and audio/subtitle transcription through MediaIngestionPort.
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.domain.entities import RawTranscript


class IngestRawTranscriptUseCase:
    """Stage 1: Media Ingestion & Speech-to-Text Orchestration."""

    def __init__(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("raw")

    def execute(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            output_dir=self.raw_storage_dir,
            whisper_model=whisper_model,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript
