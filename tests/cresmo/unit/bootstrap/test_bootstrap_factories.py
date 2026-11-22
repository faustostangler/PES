"""Unit tests for presentation factory modules.

Verifies adapter, judge, telemetry, settings, and use case factory wiring
in isolation adhering to Hexagonal Architecture and Humble Object presentation pattern.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discovery import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.indexing import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.bootstrap.factories.adapter_factory import (
    _resolve_cookie_file,
    build_embedding_adapter,
    build_indexing_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_vault_adapter,
)
from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
from cresmo.bootstrap.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.bootstrap.factories.telemetry_factory import (
    _build_mask_hook,
    _build_should_export_span,
    _clean_langfuse_env,
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
    probe_langfuse_ready,
)
from cresmo.bootstrap.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_sync_channel_use_case,
    build_unify_duplicates_use_case,
)
from cresmo.infrastructure.adapters.anonymization.anonymizer_adapter import (
    NoOpAnonymizerAdapter,
    RegexAnonymizerAdapter,
)
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.langfuse_decorator import LangfuseJudgeDecorator
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter
from cresmo.infrastructure.adapters.metrics.noop_metrics_adapter import NoOpMetricsAdapter
from cresmo.infrastructure.adapters.metrics.prometheus_metrics_adapter import (
    PrometheusMetricsAdapter,
)
from cresmo.infrastructure.adapters.obsidian import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompts import (
    JsonPromptProvider,
    LangfusePromptProvider,
)
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import NoOpTelemetryAdapter
from cresmo.infrastructure.config import CresmoSettings


@pytest.fixture
def mock_settings(tmp_path: Path) -> CresmoSettings:
    """Provide isolated test settings instance."""
    return CresmoSettings(
        gemini_api_keys=[SecretStr("test-key-1")],
        typesafe_api_key=SecretStr("test-typesafe-key"),
        langfuse_public_key="pk-test",
        langfuse_secret_key=SecretStr("sk-test"),
        langfuse_host="http://localhost:3000",
        vault_dir=tmp_path / "vault",
        data_dir=tmp_path / "data",
        raw_transcripts_dir=tmp_path / "data" / "raw",
        fluid_transcripts_dir=tmp_path / "data" / "fluid",
        enriched_transcripts_dir=tmp_path / "data" / "enriched",
    )


class TestSettingsFactory:
    """Hermetic unit tests for settings factory."""

    def test_resolve_shared_settings(self, mock_settings: CresmoSettings) -> None:
        reset_shared_settings()
        # When passed explicitly, returns the passed instance
        resolved = resolve_shared_settings(mock_settings)
        assert resolved is mock_settings

        # When None, returns shared instance
        shared = resolve_shared_settings(None)
        assert isinstance(shared, CresmoSettings)

    def test_get_and_reset_shared_settings(self) -> None:
        reset_shared_settings()
        s1 = get_shared_settings()
        s2 = get_shared_settings()
        assert s1 is s2
        reset_shared_settings()


class TestTelemetryFactory:
    """Hermetic unit tests for telemetry factory."""

    def test_probe_langfuse_ready_success_and_fallback(self) -> None:
        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_http_endpoint"
        ) as mock_probe:
            mock_probe.side_effect = [False, True]
            res = probe_langfuse_ready("http://localhost:3000")
            assert res is True
            assert mock_probe.call_count == 2

    def test_clean_langfuse_env(self) -> None:
        os.environ["LANGFUSE_PUBLIC_KEY"] = "pk"
        os.environ["LANGFUSE_SECRET_KEY"] = "sk"
        os.environ["LANGFUSE_HOST"] = "host"
        _clean_langfuse_env()
        assert "LANGFUSE_PUBLIC_KEY" not in os.environ
        assert "LANGFUSE_SECRET_KEY" not in os.environ
        assert "LANGFUSE_HOST" not in os.environ

    def test_build_should_export_span(self, capsys: pytest.CaptureFixture[str]) -> None:
        predicate = _build_should_export_span()
        span_mock = MagicMock()
        span_mock.instrumentation_scope.name = "cresmo.pipeline"
        assert predicate(span_mock) is True
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_build_mask_hook(self) -> None:
        assert _build_mask_hook(None) is None
        anonymizer = RegexAnonymizerAdapter()
        hook = _build_mask_hook(anonymizer)
        assert hook is not None

    def test_build_anonymizer_adapter(self, mock_settings: CresmoSettings) -> None:
        mock_settings.anonymization_enabled = False
        assert isinstance(build_anonymizer_adapter(mock_settings), NoOpAnonymizerAdapter)

        mock_settings.anonymization_enabled = True
        assert isinstance(build_anonymizer_adapter(mock_settings), RegexAnonymizerAdapter)

    def test_build_metrics_adapter(self, mock_settings: CresmoSettings) -> None:
        mock_settings.prometheus_enabled = False
        assert isinstance(build_metrics_adapter(mock_settings), NoOpMetricsAdapter)

        mock_settings.prometheus_enabled = True
        assert isinstance(build_metrics_adapter(mock_settings), PrometheusMetricsAdapter)

    def test_build_telemetry_adapter_disabled(self, mock_settings: CresmoSettings) -> None:
        mock_settings.langfuse_public_key = ""
        adapter = build_telemetry_adapter(mock_settings)
        assert isinstance(adapter, NoOpTelemetryAdapter)

    def test_build_telemetry_adapter_wires_dynamic_version_and_git_sha(
        self, mock_settings: CresmoSettings
    ) -> None:
        from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import (
            OpenTelemetryAdapter,
        )

        mock_settings.git_sha = "12345678abcdef"
        mock_langfuse = MagicMock()
        adapter = build_telemetry_adapter(mock_settings, langfuse_client=mock_langfuse)
        assert isinstance(adapter, OpenTelemetryAdapter)
        assert adapter._pipeline_version == mock_settings.pipeline_version
        assert adapter._git_sha == "12345678"


class TestAdapterFactory:
    """Hermetic unit tests for adapter factory."""

    def test_resolve_cookie_file(self, tmp_path: Path, mock_settings: CresmoSettings) -> None:
        mock_settings.cookies_file = None
        # None when not found
        assert _resolve_cookie_file(mock_settings) is None

        # Existing cookies.txt in data_dir
        cookie_file = tmp_path / "data" / "cookies.txt"
        cookie_file.parent.mkdir(parents=True, exist_ok=True)
        cookie_file.write_text("test cookies", encoding="utf-8")
        assert _resolve_cookie_file(mock_settings) == cookie_file

    def test_build_vault_adapter(self, mock_settings: CresmoSettings) -> None:
        vault = build_vault_adapter(mock_settings)
        assert isinstance(vault, ObsidianVaultAdapter)

    def test_build_indexing_adapter(self, mock_settings: CresmoSettings) -> None:
        indexing = build_indexing_adapter(mock_settings)
        assert indexing is not None

    def test_build_prompt_provider_json(self, mock_settings: CresmoSettings) -> None:
        provider = build_prompt_provider(mock_settings)
        assert isinstance(provider, LangfusePromptProvider)
        assert isinstance(provider._fallback, JsonPromptProvider)

    def test_build_preflight_checker(self, mock_settings: CresmoSettings) -> None:
        checker = build_preflight_checker(mock_settings)
        assert isinstance(checker, PreflightHealthChecker)

    def test_build_gemini_credential_pool_uses_settings_and_handles_empty_keys(
        self, tmp_path: Path
    ) -> None:
        """Verify SPEC-1: build_gemini_credential_pool uses configured keys/timeout or returns None."""
        from cresmo.bootstrap.factories.adapter_factory import build_gemini_credential_pool
        from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

        settings = CresmoSettings(
            gemini_api_keys=[SecretStr("KEY_A"), SecretStr("KEY_B")],
            vault_dir=tmp_path / "vault",
            gemini_timeout_seconds=240.0,
        )
        pool = build_gemini_credential_pool(settings)
        assert isinstance(pool, GeminiCredentialPool)
        assert pool.key_count == 2
        assert pool.timeout == 240.0

        empty_settings = CresmoSettings(
            gemini_api_key=SecretStr(""),
            gemini_api_keys=[],
            vault_dir=tmp_path / "vault_empty",
        )
        assert build_gemini_credential_pool(empty_settings) is None

    def test_factories_reuse_injected_credential_pool(self, tmp_path: Path) -> None:
        """Verify SPEC-2: synthesis, indexing, and judge factories reuse injected credential_pool."""
        from cresmo.bootstrap.factories.adapter_factory import build_gemini_synthesis_adapter
        from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter
        from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

        settings = CresmoSettings(
            gemini_api_key=SecretStr("KEY_1,KEY_2"),
            vault_dir=tmp_path / "vault",
            judge_provider="gemini",
        )
        shared_pool = GeminiCredentialPool(keys=["KEY_1", "KEY_2"], timeout=120.0)

        synth = build_gemini_synthesis_adapter(settings, credential_pool=shared_pool)
        assert isinstance(synth, GeminiLLMAdapter)
        assert synth._pool is shared_pool

        indexing = build_indexing_adapter(settings, web_index=True, credential_pool=shared_pool)
        assert isinstance(indexing, GeminiLLMAdapter)
        assert indexing._pool is shared_pool

        judge = build_llm_judge_adapter(
            settings, enable_fallback=False, credential_pool=shared_pool
        )
        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, GeminiJudgeAdapter)
        assert judge._inner_judge._inner_judge._pool is shared_pool

    def test_factories_propagate_thinking_level_and_max_output_tokens(self, tmp_path: Path) -> None:
        """Verify synthesis, indexing, and judge factories propagate thinking_level and max_output_tokens."""
        from cresmo.bootstrap.factories.adapter_factory import build_gemini_synthesis_adapter
        from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

        settings = CresmoSettings(
            gemini_api_key=SecretStr("KEY_THINKING_1"),
            vault_dir=tmp_path / "vault",
            judge_provider="gemini",
            gemini_thinking_level="minimal",
            judge_gemini_thinking_level="medium",
            gemini_max_output_tokens=16_384,
        )

        synth = build_gemini_synthesis_adapter(settings)
        assert isinstance(synth, GeminiLLMAdapter)
        assert synth.thinking_level == "minimal"
        assert synth.max_output_tokens == 16_384

        indexing = build_indexing_adapter(
            settings, web_index=True, model_override="gemini-3.6-flash"
        )
        assert isinstance(indexing, GeminiLLMAdapter)
        assert indexing.thinking_level == "minimal"
        assert indexing.max_output_tokens == 16_384

        judge = build_llm_judge_adapter(settings, enable_fallback=False)
        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        primary_judge = judge._inner_judge._inner_judge
        assert isinstance(primary_judge, GeminiJudgeAdapter)
        assert primary_judge.thinking_level == "medium"
        assert primary_judge.max_output_tokens == 16_384


class TestJudgeFactory:
    """Hermetic unit tests for judge factory."""

    def test_build_llm_judge_adapter_gemini(self, mock_settings: CresmoSettings) -> None:
        mock_settings.judge_provider = "gemini"
        judge = build_llm_judge_adapter(mock_settings, enable_fallback=False)
        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, GeminiJudgeAdapter)

    def test_build_llm_judge_adapter_ollama(self, mock_settings: CresmoSettings) -> None:
        mock_settings.judge_provider = "ollama"
        judge = build_llm_judge_adapter(mock_settings, enable_fallback=False)
        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_typesafe(self, mock_settings: CresmoSettings) -> None:
        mock_settings.judge_provider = "typesafe"
        judge = build_llm_judge_adapter(mock_settings, enable_fallback=False)
        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, TypeSafeJudgeAdapter)

    def test_build_llm_judge_adapter_with_telemetry(self, mock_settings: CresmoSettings) -> None:
        mock_settings.judge_provider = "gemini"
        langfuse_mock = MagicMock()
        judge = build_llm_judge_adapter(
            mock_settings, langfuse_client=langfuse_mock, enable_fallback=False
        )
        assert isinstance(judge, LangfuseJudgeDecorator)


class TestUseCaseFactory:
    """Hermetic unit tests for use case factory."""

    def test_build_index_raw_use_case(self, mock_settings: CresmoSettings) -> None:
        use_case = build_index_raw_use_case(settings=mock_settings)
        assert isinstance(use_case, IndexRawTranscriptsUseCase)

    def test_build_index_raw_use_case_shares_gemini_credential_pool(self, tmp_path: Path) -> None:
        """Verify SPEC-4: build_index_raw_use_case shares one GeminiCredentialPool across indexing and judge."""
        from cresmo.infrastructure.adapters.judges.composite_judge import (
            ResilientCompositeJudgeAdapter,
        )
        from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

        settings = CresmoSettings(
            gemini_api_key=SecretStr("KEY_IDX_1,KEY_IDX_2"),
            vault_dir=tmp_path / "vault",
            judge_provider="gemini",
            langfuse_enabled=False,
        )
        use_case = build_index_raw_use_case(settings=settings, web_index=True)

        assert isinstance(use_case.llm_indexing_port, GeminiLLMAdapter)
        assert isinstance(use_case.llm_judge_port, LangfuseJudgeDecorator)
        preflight = use_case.llm_judge_port._inner_judge
        assert isinstance(preflight, MechanicalPreflightJudgeDecorator)
        composite = preflight._inner_judge
        assert isinstance(composite, ResilientCompositeJudgeAdapter)
        assert isinstance(composite._primary, GeminiJudgeAdapter)
        assert use_case.llm_indexing_port._pool is composite._primary._pool

    def test_build_concat_master_use_case(self, mock_settings: CresmoSettings) -> None:
        use_case = build_concat_master_use_case(settings=mock_settings)
        assert isinstance(use_case, ConcatMasterUseCase)

    def test_build_unify_duplicates_use_case(self, mock_settings: CresmoSettings) -> None:
        use_case = build_unify_duplicates_use_case(settings=mock_settings)
        assert isinstance(use_case, UnifyDuplicateNotesUseCase)

    def test_build_discover_batch_sources_use_case(self, mock_settings: CresmoSettings) -> None:
        use_case = build_discover_batch_sources_use_case(settings=mock_settings)
        assert isinstance(use_case, DiscoverBatchSourcesUseCase)

    def test_build_sync_channel_use_case(self, mock_settings: CresmoSettings) -> None:
        mock_pipeline = MagicMock()
        use_case = build_sync_channel_use_case(settings=mock_settings, pipeline=mock_pipeline)
        assert isinstance(use_case, SyncChannelUseCase)

    def test_build_embedding_adapter_wires_timeouts_and_providers(self, tmp_path: Path) -> None:
        from cresmo.infrastructure.adapters.embeddings import (
            GeminiEmbeddingAdapter,
            OllamaEmbeddingAdapter,
            ResilientEmbeddingAdapter,
            TfidfEmbeddingAdapter,
        )

        gemini_settings = CresmoSettings(
            _env_file=None,
            vault_dir=tmp_path / "vault",
            embedding_provider="gemini",
            gemini_api_keys=[SecretStr("key-emb-1")],
            gemini_timeout_seconds=45.0,
        )
        gemini_wrapped = build_embedding_adapter(settings=gemini_settings)
        assert isinstance(gemini_wrapped, ResilientEmbeddingAdapter)
        assert isinstance(gemini_wrapped.primary, GeminiEmbeddingAdapter)
        assert gemini_wrapped.primary.timeout_seconds == 45.0

        ollama_settings = CresmoSettings(
            _env_file=None,
            vault_dir=tmp_path / "vault",
            embedding_provider="ollama",
            ollama_timeout_seconds=12.5,
        )
        ollama_wrapped = build_embedding_adapter(settings=ollama_settings)
        assert isinstance(ollama_wrapped, ResilientEmbeddingAdapter)
        assert isinstance(ollama_wrapped.primary, OllamaEmbeddingAdapter)
        assert ollama_wrapped.primary.timeout_seconds == 12.5

        tfidf_settings = CresmoSettings(
            _env_file=None,
            vault_dir=tmp_path / "vault",
            embedding_provider="tfidf",
        )
        assert isinstance(build_embedding_adapter(settings=tfidf_settings), TfidfEmbeddingAdapter)
