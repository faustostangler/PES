"""Unit tests for presentation factory modules.

Verifies adapter, judge, telemetry, settings, and use case factory wiring
in isolation adhering to Hexagonal Architecture and Humble Object presentation pattern.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.ports import NoOpTelemetryPort
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discovery import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.indexing import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.bootstrap.factories.adapter_factory import (
    _resolve_cookie_file,
    build_embedding_adapter,
    build_gemini_credential_pool,
    build_gemini_synthesis_adapter,
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
from cresmo.infrastructure.adapters.embeddings import (
    GeminiEmbeddingAdapter,
    OllamaEmbeddingAdapter,
    ResilientEmbeddingAdapter,
    TfidfEmbeddingAdapter,
)
from cresmo.infrastructure.adapters.judges.composite_judge import (
    ResilientCompositeJudgeAdapter,
)
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter
from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool
from cresmo.infrastructure.adapters.metrics.noop_metrics_adapter import NoOpMetricsAdapter
from cresmo.infrastructure.adapters.metrics.prometheus_metrics_adapter import (
    PrometheusMetricsAdapter,
)
from cresmo.infrastructure.adapters.obsidian import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompts import (
    JsonPromptProvider,
    LangfusePromptProvider,
)
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import (
    OpenTelemetryAdapter,
)
from cresmo.infrastructure.config import (
    CookieSettings,
    CresmoSettings,
    EmbeddingSettings,
    GeminiSettings,
    JudgeGeminiSettings,
    JudgeSettings,
    LangfuseSettings,
    LlmSettings,
    ObservabilitySettings,
    OllamaSettings,
    PrometheusSettings,
    RuntimeTelemetrySettings,
    StorageSettings,
    TypeSafeSettings,
)


@pytest.fixture
def mock_settings(tmp_path: Path) -> CresmoSettings:
    """Provide isolated hierarchical test settings instance."""
    return CresmoSettings(
        _env_file=None,
        llm=LlmSettings(
            gemini=GeminiSettings(api_keys=(SecretStr("test-key-1"),)),
        ),
        judge=JudgeSettings(
            typesafe=TypeSafeSettings(api_key=SecretStr("test-typesafe-key")),
        ),
        observability=ObservabilitySettings(
            langfuse=LangfuseSettings(
                public_key="pk-test",
                secret_key=SecretStr("sk-test"),
                host="http://localhost:3000",
            ),
        ),
        storage=StorageSettings(
            vault_dir=tmp_path / "vault",
            data_dir=tmp_path / "data",
        ),
    )


class TestSettingsFactory:
    """Hermetic unit tests for settings factory."""

    def test_resolve_shared_settings(self, mock_settings: CresmoSettings) -> None:
        reset_shared_settings()
        resolved = resolve_shared_settings(mock_settings)
        assert resolved is mock_settings

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

    def test_probe_langfuse_ready_localhost_fallback(self) -> None:
        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_http_endpoint",
            side_effect=[False, True],
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000/") is True
            assert mock_probe.call_count == 2
            mock_probe.assert_any_call(
                "http://localhost:3000/api/public/health", timeout_seconds=2.0
            )
            mock_probe.assert_any_call(
                "http://127.0.0.1:3000/api/public/health", timeout_seconds=2.0
            )

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_http_endpoint",
            return_value=False,
        ) as mock_probe_remote:
            assert probe_langfuse_ready("https://cloud.langfuse.com") is False
            mock_probe_remote.assert_called_once_with(
                "https://cloud.langfuse.com/api/public/health", timeout_seconds=2.0
            )

    def test_clean_langfuse_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in (
            "LANGFUSE_PUBLIC_KEY",
            "LANGFUSE_SECRET_KEY",
            "LANGFUSE_HOST",
            "LANGFUSE_TRACING_ENVIRONMENT",
            "OTEL_EXPORTER_OTLP_TIMEOUT",
        ):
            monkeypatch.setenv(var, "dummy")
        _clean_langfuse_env()
        import os

        for var in (
            "LANGFUSE_PUBLIC_KEY",
            "LANGFUSE_SECRET_KEY",
            "LANGFUSE_HOST",
            "LANGFUSE_TRACING_ENVIRONMENT",
            "OTEL_EXPORTER_OTLP_TIMEOUT",
        ):
            assert var not in os.environ

    def test_build_should_export_span(self) -> None:
        predicate = _build_should_export_span()
        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.is_default_export_span",
            return_value=False,
        ):
            cresmo_span = MagicMock()
            cresmo_span.instrumentation_scope.name = "cresmo.pipeline"
            assert predicate(cresmo_span) is True

            other_span = MagicMock()
            other_span.instrumentation_scope.name = "httpx"
            assert predicate(other_span) is False

    def test_build_mask_hook(self) -> None:
        assert _build_mask_hook(None) is None
        anonymizer = RegexAnonymizerAdapter()
        hook = _build_mask_hook(anonymizer)
        assert hook is not None

    def test_build_anonymizer_adapter(self) -> None:
        disabled = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(anonymization_enabled=False)
        )
        assert isinstance(build_anonymizer_adapter(disabled), NoOpAnonymizerAdapter)

        enabled = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(anonymization_enabled=True)
        )
        assert isinstance(build_anonymizer_adapter(enabled), RegexAnonymizerAdapter)

    def test_build_metrics_adapter(self) -> None:
        disabled = ObservabilitySettings(prometheus=PrometheusSettings(enabled=False))
        assert isinstance(build_metrics_adapter(disabled), NoOpMetricsAdapter)

        enabled = ObservabilitySettings(prometheus=PrometheusSettings(enabled=True))
        assert isinstance(build_metrics_adapter(enabled), PrometheusMetricsAdapter)

    def test_build_telemetry_adapter_disabled(self, mock_settings: CresmoSettings) -> None:
        adapter = build_telemetry_adapter(mock_settings.observability)
        assert isinstance(adapter, NoOpTelemetryPort)

    def test_build_telemetry_adapter_wires_dynamic_version_and_git_sha(self) -> None:
        obs = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(git_sha="12345678abcdef"),
        )
        mock_langfuse = MagicMock()
        adapter = build_telemetry_adapter(obs, langfuse_client=mock_langfuse)
        assert isinstance(adapter, OpenTelemetryAdapter)
        assert adapter._pipeline_version == obs.runtime.pipeline_version
        assert adapter._git_sha == "12345678"


class TestAdapterFactory:
    """Hermetic unit tests for adapter factory."""

    def test_resolve_cookie_file(self, tmp_path: Path, mock_settings: CresmoSettings) -> None:
        cookies = CookieSettings(file=None)
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir(parents=True, exist_ok=True)

        with patch(
            "cresmo.bootstrap.factories.adapter_factory.find_workspace_root",
            return_value=workspace_root,
        ):
            assert _resolve_cookie_file(mock_settings.storage, cookies) is None

            ws_cookies = workspace_root / ".yt_dlp_cookies.txt"
            ws_cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
            assert _resolve_cookie_file(mock_settings.storage, cookies) == ws_cookies

            cookie_file = tmp_path / "data" / "cookies.txt"
            cookie_file.parent.mkdir(parents=True, exist_ok=True)
            cookie_file.write_text("test cookies", encoding="utf-8")
            assert _resolve_cookie_file(mock_settings.storage, cookies) == cookie_file

    def test_segregated_settings_accepted_by_isp_factories(self, tmp_path: Path) -> None:
        """Verify segregated sub-settings work without instantiating full CresmoSettings (ADR-074)."""
        storage = StorageSettings(
            data_dir=tmp_path / "data",
            vault_dir=tmp_path / "vault",
        )
        llm = LlmSettings(
            gemini=GeminiSettings(api_keys=(SecretStr("isp-key-1"),)),
        )
        obs = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(anonymization_enabled=False),
            prometheus=PrometheusSettings(enabled=False),
            langfuse=LangfuseSettings(public_key=""),
        )

        assert isinstance(build_vault_adapter(storage), ObsidianVaultAdapter)
        assert build_gemini_credential_pool(llm.gemini) is not None
        assert build_indexing_adapter(llm) is not None
        assert isinstance(build_anonymizer_adapter(obs), NoOpAnonymizerAdapter)
        assert isinstance(build_metrics_adapter(obs), NoOpMetricsAdapter)
        assert isinstance(build_telemetry_adapter(obs), NoOpTelemetryPort)

    def test_build_vault_adapter(self, mock_settings: CresmoSettings) -> None:
        vault = build_vault_adapter(mock_settings.storage)
        assert isinstance(vault, ObsidianVaultAdapter)

    def test_build_indexing_adapter(self, mock_settings: CresmoSettings) -> None:
        indexing = build_indexing_adapter(mock_settings.llm)
        assert indexing is not None

    def test_build_prompt_provider_json(self, mock_settings: CresmoSettings) -> None:
        provider = build_prompt_provider(mock_settings)
        assert isinstance(provider, LangfusePromptProvider)
        assert isinstance(provider._fallback, JsonPromptProvider)

    def test_build_preflight_checker(self, mock_settings: CresmoSettings) -> None:
        checker = build_preflight_checker(mock_settings)
        assert isinstance(checker, PreflightHealthChecker)

    def test_build_gemini_credential_pool_uses_settings_and_handles_empty_keys(self) -> None:
        """Verify build_gemini_credential_pool uses configured keys/timeout or returns None."""
        gemini = GeminiSettings(
            api_keys=(SecretStr("KEY_A"), SecretStr("KEY_B")),
            timeout_seconds=240.0,
        )
        pool = build_gemini_credential_pool(gemini)
        assert isinstance(pool, GeminiCredentialPool)
        assert pool.key_count == 2
        assert pool.timeout == 240.0

        empty_gemini = GeminiSettings(api_keys=())
        assert build_gemini_credential_pool(empty_gemini) is None

    def test_factories_reuse_injected_credential_pool(self, tmp_path: Path) -> None:
        """Verify synthesis, indexing, and judge factories reuse injected credential_pool."""
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys="KEY_1,KEY_2")),  # type: ignore[arg-type]
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            judge=JudgeSettings(provider="gemini"),
        )
        shared_pool = GeminiCredentialPool(keys=["KEY_1", "KEY_2"], timeout=120.0)

        synth = build_gemini_synthesis_adapter(settings.llm.gemini, credential_pool=shared_pool)
        assert isinstance(synth, GeminiLLMAdapter)
        assert synth._pool is shared_pool

        indexing = build_indexing_adapter(settings.llm, web_index=True, credential_pool=shared_pool)
        assert isinstance(indexing, GeminiLLMAdapter)
        assert indexing._pool is shared_pool

        judge = build_llm_judge_adapter(
            settings, enable_fallback=False, credential_pool=shared_pool
        )
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, GeminiJudgeAdapter)
        assert judge._inner_judge._inner_judge._pool is shared_pool

    def test_factories_propagate_thinking_level_and_max_output_tokens(self, tmp_path: Path) -> None:
        """Verify synthesis, indexing, and judge factories propagate thinking_level and max_output_tokens."""
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(
                gemini=GeminiSettings(
                    api_keys=(SecretStr("KEY_THINKING_1"),),
                    thinking_level="minimal",
                    max_output_tokens=16_384,
                ),
            ),
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            judge=JudgeSettings(
                provider="gemini",
                gemini=JudgeGeminiSettings(thinking_level="medium"),
            ),
        )

        synth = build_gemini_synthesis_adapter(settings.llm.gemini)
        assert isinstance(synth, GeminiLLMAdapter)
        assert synth.thinking_level == "minimal"
        assert synth.max_output_tokens == 16_384

        indexing = build_indexing_adapter(
            settings.llm, web_index=True, model_override="gemini-3.6-flash"
        )
        assert isinstance(indexing, GeminiLLMAdapter)
        assert indexing.thinking_level == "minimal"
        assert indexing.max_output_tokens == 16_384

        judge = build_llm_judge_adapter(settings, enable_fallback=False)
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        primary_judge = judge._inner_judge._inner_judge
        assert isinstance(primary_judge, GeminiJudgeAdapter)
        assert primary_judge.thinking_level == "medium"
        assert primary_judge.max_output_tokens == 16_384


class TestJudgeFactory:
    """Hermetic unit tests for judge factory."""

    def test_build_llm_judge_adapter_gemini(self, mock_settings: CresmoSettings) -> None:
        cfg = mock_settings.model_copy(
            update={"judge": mock_settings.judge.model_copy(update={"provider": "gemini"})}
        )
        judge = build_llm_judge_adapter(cfg, enable_fallback=False)
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, GeminiJudgeAdapter)

    def test_build_llm_judge_adapter_ollama(self, mock_settings: CresmoSettings) -> None:
        cfg = mock_settings.model_copy(
            update={"judge": mock_settings.judge.model_copy(update={"provider": "ollama"})}
        )
        judge = build_llm_judge_adapter(cfg, enable_fallback=False)
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_typesafe(self, mock_settings: CresmoSettings) -> None:
        cfg = mock_settings.model_copy(
            update={"judge": mock_settings.judge.model_copy(update={"provider": "typesafe"})}
        )
        judge = build_llm_judge_adapter(cfg, enable_fallback=False)
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, TypeSafeJudgeAdapter)

    def test_build_llm_judge_adapter_with_telemetry(self, mock_settings: CresmoSettings) -> None:
        telemetry_port = NoOpTelemetryPort()
        judge = build_llm_judge_adapter(
            mock_settings, telemetry_port=telemetry_port, enable_fallback=False
        )
        assert isinstance(judge, TelemetryJudgeDecorator)
        assert judge._telemetry is telemetry_port


class TestUseCaseFactory:
    """Hermetic unit tests for use case factory."""

    def test_build_index_raw_use_case(self, mock_settings: CresmoSettings) -> None:
        use_case = build_index_raw_use_case(settings=mock_settings)
        assert isinstance(use_case, IndexRawTranscriptsUseCase)

    def test_build_index_raw_use_case_shares_gemini_credential_pool(self, tmp_path: Path) -> None:
        """Verify build_index_raw_use_case shares one GeminiCredentialPool across indexing and judge."""
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys="KEY_IDX_1,KEY_IDX_2")),  # type: ignore[arg-type]
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            judge=JudgeSettings(provider="gemini"),
        )
        use_case = build_index_raw_use_case(settings=settings, web_index=True)

        assert isinstance(use_case.llm_indexing_port, GeminiLLMAdapter)
        assert isinstance(use_case.llm_judge_port, TelemetryJudgeDecorator)
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
        gemini_settings = CresmoSettings(
            _env_file=None,
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            embeddings=EmbeddingSettings(provider="gemini"),
            llm=LlmSettings(
                gemini=GeminiSettings(api_keys=(SecretStr("key-emb-1"),), timeout_seconds=45.0),
            ),
        )
        gemini_wrapped = build_embedding_adapter(settings=gemini_settings)
        assert isinstance(gemini_wrapped, ResilientEmbeddingAdapter)
        assert isinstance(gemini_wrapped.primary, GeminiEmbeddingAdapter)
        assert gemini_wrapped.primary.timeout_seconds == 45.0

        ollama_settings = CresmoSettings(
            _env_file=None,
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            embeddings=EmbeddingSettings(provider="ollama"),
            llm=LlmSettings(ollama=OllamaSettings(timeout_seconds=12.5)),
        )
        ollama_wrapped = build_embedding_adapter(settings=ollama_settings)
        assert isinstance(ollama_wrapped, ResilientEmbeddingAdapter)
        assert isinstance(ollama_wrapped.primary, OllamaEmbeddingAdapter)
        assert ollama_wrapped.primary.timeout_seconds == 12.5

        tfidf_settings = CresmoSettings(
            _env_file=None,
            storage=StorageSettings(vault_dir=tmp_path / "vault"),
            embeddings=EmbeddingSettings(provider="tfidf"),
        )
        assert isinstance(build_embedding_adapter(settings=tfidf_settings), TfidfEmbeddingAdapter)
