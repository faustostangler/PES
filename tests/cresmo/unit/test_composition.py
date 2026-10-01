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
from cresmo.application.use_cases.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.anonymizer_adapter import (
    NoOpAnonymizerAdapter,
    RegexAnonymizerAdapter,
)
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.noop_metrics_adapter import NoOpMetricsAdapter
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.ollama_llm_adapter import OllamaLLMAdapter
from cresmo.infrastructure.adapters.opentelemetry_adapter import (
    NoOpTelemetryAdapter,
    OpenTelemetryAdapter,
)
from cresmo.infrastructure.adapters.prometheus_metrics_adapter import (
    PrometheusMetricsAdapter,
)
from cresmo.infrastructure.adapters.prompt_provider import (
    JsonPromptProvider,
    LangfusePromptProvider,
)
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_anonymizer_adapter,
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_gemini_synthesis_adapter,
    build_index_raw_use_case,
    build_indexing_adapter,
    build_metrics_adapter,
    build_pipeline,
    build_preflight_checker,
    build_prompt_provider,
    build_sync_channel_use_case,
    build_telemetry_adapter,
    build_unify_duplicates_use_case,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
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
        assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
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

        with (
            patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=True),
            patch.dict("sys.modules", {"langfuse": MagicMock(Langfuse=mock_langfuse_cls)}),
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
            assert pipeline.llm_synthesis_port._langfuse is mock_langfuse_instance

    def test_build_pipeline_skips_langfuse_when_probe_fails(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        settings_with_langfuse = CresmoSettings(
            gemini_api_key=SecretStr("TEST_KEY"),
            vault_dir=tmp_path / "vault",
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key=SecretStr("sk-lf-test"),
            langfuse_host="http://localhost:3000",
        )

        with patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=False):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
            assert pipeline.llm_synthesis_port._langfuse is None

        captured = capsys.readouterr()
        assert (
            "unreachable" in captured.err
            or "unreachable" in captured.out
            or "Langfuse" in captured.err
        )

    def test_build_pipeline_with_langfuse_import_or_init_error(self, tmp_path: Path) -> None:
        settings_with_langfuse = CresmoSettings(
            gemini_api_key=SecretStr("TEST_KEY"),
            vault_dir=tmp_path / "vault",
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key=SecretStr("sk-lf-test"),
            langfuse_host="https://cloud.langfuse.com",
        )

        with (
            patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=True),
            patch("langfuse.Langfuse", side_effect=RuntimeError("Langfuse init failed")),
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
            assert pipeline.llm_synthesis_port._langfuse is None

    def test_probe_langfuse_ready_url_construction(self) -> None:
        from cresmo.presentation.composition import probe_langfuse_ready

        with patch(
            "cresmo.presentation.composition.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000", timeout_seconds=0.5) is True
            mock_probe.assert_called_once_with(
                "http://localhost:3000/api/public/health",
                timeout_seconds=0.5,
            )

    def test_probe_langfuse_ready_strips_trailing_slash(self) -> None:
        from cresmo.presentation.composition import probe_langfuse_ready

        with patch(
            "cresmo.presentation.composition.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000/", timeout_seconds=0.5) is True
            mock_probe.assert_called_once_with(
                "http://localhost:3000/api/public/health",
                timeout_seconds=0.5,
            )

    def test_build_concat_master_use_case(self, test_settings: CresmoSettings) -> None:

        uc = build_concat_master_use_case(settings=test_settings)
        assert isinstance(uc, ConcatMasterUseCase)
        assert uc.settings is test_settings

    def test_build_index_raw_use_case_default_ollama(self, test_settings: CresmoSettings) -> None:
        uc = build_index_raw_use_case(settings=test_settings, web_index=False)
        assert isinstance(uc, IndexRawTranscriptsUseCase)
        assert isinstance(uc.llm, OllamaLLMAdapter)
        assert isinstance(uc.llm_indexing_port, OllamaLLMAdapter)
        assert isinstance(uc.vault_repo, ObsidianVaultAdapter)
        assert isinstance(uc.vault_port, ObsidianVaultAdapter)

    def test_build_index_raw_use_case_web_index_gemini(self, test_settings: CresmoSettings) -> None:
        uc = build_index_raw_use_case(settings=test_settings, web_index=True)
        assert isinstance(uc, IndexRawTranscriptsUseCase)
        assert isinstance(uc.llm, GeminiLLMAdapter)
        assert isinstance(uc.llm_indexing_port, GeminiLLMAdapter)
        assert isinstance(uc.vault_repo, ObsidianVaultAdapter)
        assert isinstance(uc.vault_port, ObsidianVaultAdapter)

    def test_build_pipeline_with_web_index(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings, web_index=True)
        assert isinstance(pipeline, CresmoPipeline)
        assert isinstance(pipeline.index_raw.llm, GeminiLLMAdapter)
        assert isinstance(pipeline.index_raw.llm_indexing_port, GeminiLLMAdapter)

    def test_build_sync_channel_use_case_raises_runtime_error_when_ledger_port_missing(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.presentation.composition.build_pipeline") as mock_build_pipeline:
            mock_pipeline = MagicMock(spec=CresmoPipeline)
            mock_pipeline.ledger_port = None
            mock_build_pipeline.return_value = mock_pipeline

            with pytest.raises(RuntimeError, match="Ledger port must be wired for channel sync"):
                build_sync_channel_use_case(settings=test_settings)

    def test_resolve_shared_settings_respects_injected_instance(
        self, test_settings: CresmoSettings
    ) -> None:
        resolved = resolve_shared_settings(test_settings)
        assert resolved is test_settings

    def test_shared_settings_singleton_memoization_and_reset(self) -> None:
        reset_shared_settings()
        s1 = get_shared_settings()
        s2 = get_shared_settings()
        assert s1 is s2

        reset_shared_settings()
        s3 = get_shared_settings()
        assert s3 is not s1
        assert s3 == s1
        reset_shared_settings()

    def test_build_anonymizer_adapter_enabled_and_disabled(self, tmp_path: Path) -> None:
        settings_enabled = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v1",
            anonymization_enabled=True,
        )
        assert isinstance(build_anonymizer_adapter(settings_enabled), RegexAnonymizerAdapter)

        settings_disabled = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v2",
            anonymization_enabled=False,
        )
        assert isinstance(build_anonymizer_adapter(settings_disabled), NoOpAnonymizerAdapter)

    def test_build_telemetry_adapter_with_and_without_client(
        self, test_settings: CresmoSettings
    ) -> None:
        mock_client = MagicMock()
        adapter = build_telemetry_adapter(test_settings, langfuse_client=mock_client)
        assert isinstance(adapter, OpenTelemetryAdapter)

        noop = build_telemetry_adapter(test_settings, langfuse_client=None)
        assert isinstance(noop, NoOpTelemetryAdapter)

    def test_build_metrics_adapter_enabled_and_disabled(self, tmp_path: Path) -> None:
        settings_enabled = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v1",
            prometheus_enabled=True,
        )
        assert isinstance(build_metrics_adapter(settings_enabled), PrometheusMetricsAdapter)

        settings_disabled = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v2",
            prometheus_enabled=False,
        )
        assert isinstance(build_metrics_adapter(settings_disabled), NoOpMetricsAdapter)

    def test_build_prompt_provider(self, test_settings: CresmoSettings) -> None:
        provider = build_prompt_provider(test_settings, langfuse_client=None)
        assert isinstance(provider, LangfusePromptProvider)
        assert isinstance(provider._fallback, JsonPromptProvider)

    def test_build_gemini_synthesis_adapter(self, test_settings: CresmoSettings) -> None:
        adapter = build_gemini_synthesis_adapter(test_settings, langfuse_client=None)
        assert isinstance(adapter, GeminiLLMAdapter)
        assert adapter.model_name == test_settings.gemini_model

    def test_build_indexing_adapter_selection(self, test_settings: CresmoSettings) -> None:
        ollama_adapter = build_indexing_adapter(test_settings, web_index=False)
        assert isinstance(ollama_adapter, OllamaLLMAdapter)

        gemini_adapter = build_indexing_adapter(test_settings, web_index=True)
        assert isinstance(gemini_adapter, GeminiLLMAdapter)

        mock_synthesis = MagicMock(spec=GeminiLLMAdapter)
        reused = build_indexing_adapter(
            test_settings, synthesis_adapter=mock_synthesis, web_index=True
        )
        assert reused is mock_synthesis
