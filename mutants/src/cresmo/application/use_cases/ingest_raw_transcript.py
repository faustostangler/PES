"""Stage 1 Use Case: Ingest Raw Transcript.

Orchestrates media crawling and audio/subtitle transcription through MediaIngestionPort.
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.domain.entities import RawTranscript


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class IngestRawTranscriptUseCase:
    """Stage 1: Media Ingestion & Speech-to-Text Orchestration."""

    @_mutmut_mutated(mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut)
    def __init__(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("raw")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_orig(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("raw")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_1(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = None
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("raw")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_2(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = None
        self.raw_storage_dir = raw_storage_dir or Path("raw")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_3(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = None

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_4(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir and Path("raw")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_5(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path(None)

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_6(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("XXrawXX")

    def xǁIngestRawTranscriptUseCaseǁ__init____mutmut_7(
        self,
        ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        raw_storage_dir: Path | None = None,
    ) -> None:
        self.ingestion_port = ingestion_port
        self.vault_port = vault_port
        self.raw_storage_dir = raw_storage_dir or Path("RAW")

    @_mutmut_mutated(mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut)
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

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_orig(
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

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_1(
        self,
        video_url: str,
        whisper_model: str = "XXbaseXX",
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

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_2(
        self,
        video_url: str,
        whisper_model: str = "BASE",
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

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_3(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = True,
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

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_4(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = None
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_5(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=None,
            output_dir=self.raw_storage_dir,
            whisper_model=whisper_model,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_6(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            output_dir=None,
            whisper_model=whisper_model,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_7(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            output_dir=self.raw_storage_dir,
            whisper_model=None,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_8(
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
            keep_audio=None,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_9(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            output_dir=self.raw_storage_dir,
            whisper_model=whisper_model,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_10(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            whisper_model=whisper_model,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_11(
        self,
        video_url: str,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Execute Stage 1 raw ingestion for a target media item."""
        transcript = self.ingestion_port.ingest_single_video(
            video_url=video_url,
            output_dir=self.raw_storage_dir,
            keep_audio=keep_audio,
        )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_12(
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
            )
        if transcript is not None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_13(
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
        if transcript is None:
            self.vault_port.save_raw_transcript(transcript)
        return transcript

    def xǁIngestRawTranscriptUseCaseǁexecute__mutmut_14(
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
            self.vault_port.save_raw_transcript(None)
        return transcript

mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['_mutmut_orig'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_1'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_2'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_3'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_4'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_5'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_6'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁ__init____mutmut['xǁIngestRawTranscriptUseCaseǁ__init____mutmut_7'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁ__init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['_mutmut_orig'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_1'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_2'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_3'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_4'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_5'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_6'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_7'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_8'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_9'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_10'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_11'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_12'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_13'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁIngestRawTranscriptUseCaseǁexecute__mutmut['xǁIngestRawTranscriptUseCaseǁexecute__mutmut_14'] = IngestRawTranscriptUseCase.xǁIngestRawTranscriptUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
