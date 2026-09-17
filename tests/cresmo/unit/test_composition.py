"""Unit tests for Cresmo Composition Root.

Verifies Dependency Injection assembly, port wiring, and configuration binding
per SPEC-002 §4.4.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discover_batch_sources import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_pipeline,
    build_preflight_checker,
    build_sync_channel_use_case,
    build_unify_duplicates_use_case,
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

    def test_build_unify_duplicates_use_case(self, test_settings: CresmoSettings) -> None:
        use_case = build_unify_duplicates_use_case(settings=test_settings)
        assert isinstance(use_case, UnifyDuplicateNotesUseCase)
        assert isinstance(use_case.vault_port, ObsidianVaultAdapter)

    def test_build_discover_batch_sources_use_case(self, test_settings: CresmoSettings) -> None:
        cb = MagicMock()
        use_case = build_discover_batch_sources_use_case(
            settings=test_settings,
            progress_callback=cb,
        )
        assert isinstance(use_case, DiscoverBatchSourcesUseCase)
        assert isinstance(use_case.media_ingestion_port, NativeMediaIngestionAdapter)
        assert use_case.progress_callback is cb

    def test_factory_functions_fallback_to_default_settings(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.presentation.composition.CresmoSettings", return_value=test_settings):
            p = build_pipeline(settings=None)
            assert isinstance(p, CresmoPipeline)

            c = build_preflight_checker(settings=None, check_ffmpeg=False)
            assert isinstance(c, PreflightHealthChecker)

            s = build_sync_channel_use_case(settings=None, check_ffmpeg=False)
            assert isinstance(s, SyncChannelUseCase)

            u = build_unify_duplicates_use_case(settings=None)
            assert isinstance(u, UnifyDuplicateNotesUseCase)

            d = build_discover_batch_sources_use_case(settings=None)
            assert isinstance(d, DiscoverBatchSourcesUseCase)

    def test_build_pipeline_with_langfuse_configured(self, tmp_path: Path) -> None:
        settings_with_langfuse = CresmoSettings(
            gemini_api_key=SecretStr("TEST_KEY"),
            vault_dir=tmp_path / "vault",
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key=SecretStr("sk-lf-test"),
            langfuse_host="https://cloud.langfuse.com",
        )

        mock_langfuse_instance = MagicMock()
        mock_langfuse_cls = MagicMock(return_value=mock_langfuse_instance)

        with patch.dict("sys.modules", {"langfuse": MagicMock(Langfuse=mock_langfuse_cls)}):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.llm_port, GeminiLLMAdapter)
            assert pipeline.llm_port._langfuse is mock_langfuse_instance

    def test_build_pipeline_with_langfuse_import_or_init_error(self, tmp_path: Path) -> None:
        settings_with_langfuse = CresmoSettings(
            gemini_api_key=SecretStr("TEST_KEY"),
            vault_dir=tmp_path / "vault",
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key=SecretStr("sk-lf-test"),
            langfuse_host="https://cloud.langfuse.com",
        )

        with patch("langfuse.Langfuse", side_effect=RuntimeError("Langfuse init failed")):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.llm_port, GeminiLLMAdapter)
            assert pipeline.llm_port._langfuse is None

    def test_build_concat_master_use_case(self, test_settings: CresmoSettings) -> None:
        uc = build_concat_master_use_case(settings=test_settings)
        assert isinstance(uc, ConcatMasterUseCase)
        assert uc.settings is test_settings
