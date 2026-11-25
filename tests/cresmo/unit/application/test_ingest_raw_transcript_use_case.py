"""Unit tests for IngestRawTranscriptUseCase.

Verifies media crawling and STT orchestration, parameter propagation,
and conditional persistence into VaultRepositoryPort.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.application.use_cases.ingest_raw_transcript import IngestRawTranscriptUseCase
from cresmo.domain.entities import StageTranscript
from cresmo.domain.value_objects import Channel, Content, ContentId, MediaProvenance
from tests.doubles.mock_adapters import InMemoryVaultAdapter


class TestIngestRawTranscriptUseCase:
    """Hermetic unit tests for IngestRawTranscriptUseCase."""

    def test_init_attributes_and_defaults(self) -> None:
        """Verify port assignment and zero storage leakage."""
        ingestion_port = MagicMock(spec=MediaIngestionPort)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        assert use_case.ingestion_port is ingestion_port
        assert use_case.vault_port is vault_port

    def test_execute_success_and_url_forwarding(self) -> None:
        """Verify video URL is forwarded to ingestion port and saved in vault."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        canned = StageTranscript(
            channel=Channel(name="Science Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid12345"),
            content=Content(
                id=ContentId("vid12345"), title="Science Channel", text="Raw audio text transcript."
            ),
        )
        mock_ingestion.ingest_single_video.return_value = canned
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(
            mock_ingestion,
            vault_port,
        )
        result = use_case.execute(
            video_url="https://youtube.com/watch?v=vid12345",
        )

        assert result is canned
        assert vault_port.get_stage_transcript("raw", ContentId("vid12345")) == canned
        mock_ingestion.ingest_single_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=vid12345",
        )

    def test_execute_default_parameters(self) -> None:
        """Verify positional URL execution forwards strictly video_url."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        canned = StageTranscript(
            channel=Channel(name="Default Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_default_01"),
            content=Content(
                id=ContentId("vid_default_01"),
                title="Default Channel",
                text="Default transcript body.",
            ),
        )
        mock_ingestion.ingest_single_video.return_value = canned
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(mock_ingestion, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=vid_default_01")

        assert result is canned
        mock_ingestion.ingest_single_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=vid_default_01",
        )

    def test_execute_none_returns_none_and_does_not_save(self) -> None:
        """Verify that when ingestion fails and returns None, nothing is saved to the vault."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_ingestion.ingest_single_video.return_value = None
        mock_vault = MagicMock(spec=VaultRepositoryPort)

        use_case = IngestRawTranscriptUseCase(mock_ingestion, mock_vault)
        result = use_case.execute("https://youtube.com/watch?v=missing")

        assert result is None
        mock_vault.save_stage_transcript.assert_not_called()
