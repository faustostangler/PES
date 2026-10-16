"""Unit tests for IngestRawTranscriptUseCase.

Verifies media crawling and STT orchestration, parameter propagation,
and conditional persistence into VaultRepositoryPort.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.application.use_cases.ingest_raw_transcript import IngestRawTranscriptUseCase
from cresmo.domain.entities import SourceTranscript
from cresmo.domain.value_objects import ChannelName, ContentId
from tests.doubles.mock_adapters import InMemoryVaultAdapter


class TestIngestRawTranscriptUseCase:
    """Hermetic unit tests for IngestRawTranscriptUseCase."""

    def test_init_attributes_and_defaults(self) -> None:
        """Verify storage directory resolution and port assignment."""
        ingestion_port = MagicMock(spec=MediaIngestionPort)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        assert use_case.ingestion_port is ingestion_port
        assert use_case.vault_port is vault_port
        assert use_case.raw_storage_dir == Path("raw")

        custom_dir = Path("custom/storage/dir")
        use_case_custom = IngestRawTranscriptUseCase(
            ingestion_port,
            vault_port,
            raw_storage_dir=custom_dir,
        )
        assert use_case_custom.raw_storage_dir == custom_dir

    def test_execute_success_and_kwargs_forwarding(self) -> None:
        """Verify explicit parameters are forwarded to ingestion port and saved in vault."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        canned = SourceTranscript(
            content_id=ContentId("vid12345"),
            channel_name=ChannelName("Science Channel"),
            body="Raw audio text transcript.",
        )
        mock_ingestion.ingest_single_video.return_value = canned
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(
            mock_ingestion,
            vault_port,
            raw_storage_dir=Path("custom_raw"),
        )
        result = use_case.execute(
            video_url="https://youtube.com/watch?v=vid12345",
            whisper_model="large-v3",
            keep_audio=True,
        )

        assert result is canned
        assert vault_port.get_raw_transcript(ContentId("vid12345")) == canned
        mock_ingestion.ingest_single_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=vid12345",
            output_dir=Path("custom_raw"),
            whisper_model="large-v3",
            keep_audio=True,
        )

    def test_execute_default_parameters(self) -> None:
        """Verify default parameters (whisper_model='base', keep_audio=False, output_dir=Path('raw'))."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        canned = SourceTranscript(
            content_id=ContentId("vid_default_01"),
            channel_name=ChannelName("Default Channel"),
            body="Default transcript body.",
        )
        mock_ingestion.ingest_single_video.return_value = canned
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(mock_ingestion, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=vid_default_01")

        assert result is canned
        mock_ingestion.ingest_single_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=vid_default_01",
            output_dir=Path("raw"),
            whisper_model="base",
            keep_audio=False,
        )

    def test_execute_none_returns_none_and_does_not_save(self) -> None:
        """Verify that when ingestion fails and returns None, nothing is saved to the vault."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_ingestion.ingest_single_video.return_value = None
        mock_vault = MagicMock(spec=VaultRepositoryPort)

        use_case = IngestRawTranscriptUseCase(mock_ingestion, mock_vault)
        result = use_case.execute("https://youtube.com/watch?v=missing")

        assert result is None
        mock_vault.save_transcript.assert_not_called()
