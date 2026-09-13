"""Unit tests for Cresmo Composition Root.

Verifies Dependency Injection assembly, port wiring, and configuration binding
per SPEC-002 §4.4.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_pipeline,
    build_preflight_checker,
    build_sync_channel_use_case,
)


class TestCompositionRoot:
    """Hermetic unit tests for the composition root factory."""

    @pytest.fixture
    def test_settings(self, tmp_path: Path) -> CresmoSettings:
        return CresmoSettings(
            gemini_api_key=SecretStr("TEST_FAKE_KEY_FOR_COMPOSITION"),
            vault_dir=tmp_path / "vault",
            batch_size=7,
        )

    def test_build_pipeline_wires_all_ports_correctly(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings)

        assert isinstance(pipeline, CresmoPipeline)
        assert isinstance(pipeline.media_ingestion_port, NativeMediaIngestionAdapter)
        assert isinstance(pipeline.llm_port, GeminiLLMAdapter)
        assert isinstance(pipeline.vault_port, ObsidianVaultAdapter)
        assert isinstance(pipeline.ledger_port, SqliteLedgerAdapter)
        assert pipeline.synthesize_atomic_batch.batch_size == 7

    def test_build_pipeline_with_batch_size_override(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings, batch_size_override=12)

        assert pipeline.synthesize_atomic_batch.batch_size == 12

    def test_build_preflight_checker(self, test_settings: CresmoSettings) -> None:
        checker = build_preflight_checker(settings=test_settings, check_ffmpeg=False)
        assert isinstance(checker, PreflightHealthChecker)
        result = checker.check_all()
        assert result.is_healthy

    def test_build_sync_channel_use_case(self, test_settings: CresmoSettings) -> None:
        use_case = build_sync_channel_use_case(settings=test_settings, check_ffmpeg=False)
        assert isinstance(use_case, SyncChannelUseCase)
