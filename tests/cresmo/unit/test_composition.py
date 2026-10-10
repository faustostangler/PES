"""Unit tests for Cresmo Composition Root.

Verifies Dependency Injection assembly, port wiring, and configuration binding
per SPEC-002 §4.4.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.pipeline import (
    CresmoPipeline,
    PipelineStageRunner,
    StageFactory,
)
from cresmo.application.ports import MediaIngestionPort
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
from cresmo.infrastructure.adapters.judges.langfuse_decorator import LangfuseJudgeDecorator
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
    _build_mask_hook,
    _build_should_export_span,
    _clean_langfuse_env,
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
    resolve_langfuse_client,
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
        assert isinstance(pipeline.stage_runner, PipelineStageRunner)
        assert pipeline.stage_runner.llm_transformation_port is pipeline.llm_synthesis_port
        assert isinstance(pipeline.stage_runner.stage_factory, StageFactory)
        assert isinstance(pipeline.media_ingestion_port, NativeMediaIngestionAdapter)
        assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
        assert isinstance(pipeline.vault_port, ObsidianVaultAdapter)
        assert isinstance(pipeline.ledger_port, SqliteLedgerAdapter)
        assert pipeline.batch_size == 7

    def test_build_pipeline_with_batch_size_override(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings, batch_size_override=12)

        assert pipeline.batch_size == 12

    def test_build_pipeline_wires_prompt_provider_to_llm_judge(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.presentation.composition.build_llm_judge_adapter") as mock_build_judge:
            build_pipeline(settings=test_settings)
            mock_build_judge.assert_called_once()
            _, kwargs = mock_build_judge.call_args
            assert "prompt_provider" in kwargs
            assert kwargs["prompt_provider"] is not None

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

    def test_build_discover_batch_sources_use_case_with_injected_port(
        self, test_settings: CresmoSettings
    ) -> None:
        mock_port = MagicMock(spec=MediaIngestionPort)
        use_case = build_discover_batch_sources_use_case(
            settings=test_settings,
            media_ingestion_port=mock_port,
        )
        assert isinstance(use_case, DiscoverBatchSourcesUseCase)
        assert use_case.media_ingestion_port is mock_port

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
            anonymization_enabled=True,
        )

        mock_langfuse_instance = MagicMock()
        mock_langfuse_cls = MagicMock(return_value=mock_langfuse_instance)

        with (
            patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=True),
            patch.dict("sys.modules", {"langfuse": MagicMock(Langfuse=mock_langfuse_cls)}),
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert pipeline.settings is settings_with_langfuse
            assert isinstance(pipeline.vault_port, ObsidianVaultAdapter)
            assert pipeline.vault_port.vault_dir == (tmp_path / "vault").resolve()
            assert pipeline.stage_runner.stage_factory is not None
            assert pipeline.stage_runner.stage_factory.settings is settings_with_langfuse
            assert isinstance(pipeline.stage_runner.llm_judge, LangfuseJudgeDecorator)
            assert pipeline.stage_runner.llm_judge._langfuse_client is mock_langfuse_instance
            assert pipeline.llm_indexing_port is not None
            assert pipeline.media_ingestion_port is not None
            assert pipeline.vault_port is not None
            assert pipeline.ledger_port is not None
            assert isinstance(pipeline.llm_synthesis_port, GeminiLLMAdapter)
            assert pipeline.llm_synthesis_port._langfuse is mock_langfuse_instance
            assert getattr(pipeline.stage_runner.telemetry_port, "_langfuse", None) is mock_langfuse_instance
            assert getattr(pipeline.stage_runner.prompt_provider, "_client", None) is mock_langfuse_instance
            assert getattr(pipeline.stage_runner.critique_synthesizer, "llm_transformation_port", None) is pipeline.llm_indexing_port
            assert (
                getattr(pipeline.stage_runner.critique_synthesizer, "_prompt_provider", None)
                is pipeline.stage_runner.prompt_provider
            )
            assert pipeline.stage_runner.ledger_port is pipeline.ledger_port

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
        assert "Langfuse server at 'http://localhost:3000' is unreachable" in captured.err
        assert "Telemetry bypassed to prevent OpenTelemetry retry loops.\n" in captured.err
        assert "To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n" in captured.err

    def test_build_pipeline_with_langfuse_import_or_init_error(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
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

        assert "[composition] Failed to initialize Langfuse client: Langfuse init failed" in caplog.text

    def test_build_pipeline_judge_attempts_and_blocking_configurations(
        self, tmp_path: Path
    ) -> None:
        s_custom = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v1",
            judge_blocking=True,
            judge_max_attempts=5,
            prometheus_enabled=True,
        )
        p_custom = build_pipeline(settings=s_custom)
        assert p_custom.stage_runner.judge_blocking is True
        assert p_custom.stage_runner.judge_max_attempts == 5
        assert isinstance(p_custom.stage_runner.metrics_port, PrometheusMetricsAdapter)

        s_default = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v2",
            prometheus_enabled=False,
        )
        p_default = build_pipeline(settings=s_default)
        assert p_default.stage_runner.judge_blocking is False
        assert p_default.stage_runner.judge_max_attempts == 1
        assert isinstance(p_default.stage_runner.metrics_port, NoOpMetricsAdapter)

    def test_build_pipeline_web_index_reuses_synthesis_adapter(
        self, test_settings: CresmoSettings
    ) -> None:
        pipeline = build_pipeline(settings=test_settings, web_index=True)
        assert pipeline.llm_indexing_port is pipeline.llm_synthesis_port

    def test_build_pipeline_default_web_index_is_false(
        self, test_settings: CresmoSettings
    ) -> None:
        pipeline = build_pipeline(settings=test_settings)
        assert pipeline.llm_indexing_port is not pipeline.llm_synthesis_port
        assert isinstance(pipeline.llm_indexing_port, OllamaLLMAdapter)

    def test_probe_langfuse_ready_url_construction(self) -> None:
        from cresmo.presentation.composition import probe_langfuse_ready

        with patch(
            "cresmo.presentation.composition.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000/serviceX") is True
            mock_probe.assert_called_once_with(
                "http://localhost:3000/serviceX/api/public/health",
                timeout_seconds=1.0,
            )

    def test_probe_langfuse_ready_strips_trailing_slash(self) -> None:
        from cresmo.presentation.composition import probe_langfuse_ready

        with patch(
            "cresmo.presentation.composition.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000/serviceX/", timeout_seconds=0.5) is True
            mock_probe.assert_called_once_with(
                "http://localhost:3000/serviceX/api/public/health",
                timeout_seconds=0.5,
            )

    def test_resolve_langfuse_client_preflight_timeout_wiring(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        s1 = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v1",
            langfuse_public_key="pk-1",
            langfuse_secret_key=SecretStr("sk-1"),
            langfuse_host="http://host1:3000",
        )
        with patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=False) as mock_probe:
            assert resolve_langfuse_client(s1) is None
            mock_probe.assert_called_once_with("http://host1:3000", timeout_seconds=1.0)
            captured = capsys.readouterr()
            expected_msg = (
                f"[preflight] Langfuse server at '{s1.langfuse_host}' is unreachable. "
                "Telemetry bypassed to prevent OpenTelemetry retry loops.\n"
                "            To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n"
            )
            assert captured.err == expected_msg

        s2 = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v2",
            langfuse_public_key="pk-2",
            langfuse_secret_key=SecretStr("sk-2"),
            langfuse_host="http://host2:3000",
            preflight_probe_timeout_seconds=3.5,
        )
        with patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=False) as mock_probe2:
            assert resolve_langfuse_client(s2) is None
            mock_probe2.assert_called_once_with("http://host2:3000", timeout_seconds=3.5)

        s_missing_probe_attrs = SimpleNamespace(
            langfuse_public_key="pk-miss",
            langfuse_secret_key=SecretStr("sk-miss"),
            langfuse_host="http://hostmiss:3000",
        )
        with patch("cresmo.presentation.composition.probe_langfuse_ready", return_value=False) as mock_probe_miss:
            assert resolve_langfuse_client(s_missing_probe_attrs) is None  # type: ignore[arg-type]
            mock_probe_miss.assert_called_once_with("http://hostmiss:3000", timeout_seconds=1.0)

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
        assert isinstance(pipeline.llm_indexing_port, GeminiLLMAdapter)

    def test_build_sync_channel_use_case_raises_runtime_error_when_ledger_port_missing(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.presentation.composition.build_pipeline") as mock_build_pipeline:
            mock_pipeline = MagicMock(spec=CresmoPipeline)
            mock_pipeline.ledger_port = None
            mock_build_pipeline.return_value = mock_pipeline

            with pytest.raises(RuntimeError, match=r"^Ledger port must be wired for channel sync\.$"):
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

    def test_clean_langfuse_env_removes_all_targeted_keys(self) -> None:
        os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-test"
        os.environ["LANGFUSE_SECRET_KEY"] = "sk-test"
        os.environ["LANGFUSE_HOST"] = "http://localhost:3000"
        os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = "15"

        _clean_langfuse_env()

        assert "LANGFUSE_PUBLIC_KEY" not in os.environ
        assert "LANGFUSE_SECRET_KEY" not in os.environ
        assert "LANGFUSE_HOST" not in os.environ
        assert "OTEL_EXPORTER_OTLP_TIMEOUT" not in os.environ

    def test_build_should_export_span_filtering(self) -> None:
        predicate = _build_should_export_span()

        # 1. Default export span returns True
        with patch("cresmo.presentation.composition.is_default_export_span", return_value=True) as mock_default:
            span_default = SimpleNamespace()
            assert predicate(span_default) is True
            mock_default.assert_called_once_with(span_default)

        # 2. Not default export, but starts with cresmo.
        with patch("cresmo.presentation.composition.is_default_export_span", return_value=False) as mock_not_default:
            span_cresmo = SimpleNamespace(
                instrumentation_scope=SimpleNamespace(name="cresmo.pipeline.runner")
            )
            assert predicate(span_cresmo) is True
            mock_not_default.assert_called_once_with(span_cresmo)

            # 3. Not cresmo scope
            span_other = SimpleNamespace(
                instrumentation_scope=SimpleNamespace(name="requests.opentelemetry")
            )
            assert predicate(span_other) is False

            # 4. Scope is None
            span_none_scope = SimpleNamespace(instrumentation_scope=None)
            assert predicate(span_none_scope) is False

            # 5. No instrumentation_scope attribute
            span_no_scope = SimpleNamespace()
            assert predicate(span_no_scope) is False

    def test_build_mask_hook_filtering_and_patching(self) -> None:
        assert _build_mask_hook(None) is None

        mock_anonymizer = MagicMock()
        mask_fn = _build_mask_hook(mock_anonymizer)
        assert mask_fn is not None

        # Case A: Identical attributes (no mask applied)
        mock_anonymizer.mask_span_attributes.return_value = {"key1": "val1"}
        span_clean = SimpleNamespace(attributes={"key1": "val1"})
        params_clean = SimpleNamespace(spans={"span-1": span_clean})
        assert mask_fn(params=params_clean) is None  # type: ignore[arg-type]
        mock_anonymizer.mask_span_attributes.assert_called_with({"key1": "val1"})

        # Case B: Sanitized attributes with modification and deletion
        raw = {"email": "user@test.com", "secret": "123", "normal": "public"}
        sanitized = {"email": "[REDACTED]", "normal": "public"}
        mock_anonymizer.mask_span_attributes.return_value = sanitized
        span_pii = SimpleNamespace(attributes=raw)
        params_pii = SimpleNamespace(spans={"span-2": span_pii})

        result = mask_fn(params=params_pii)  # type: ignore[arg-type]
        mock_anonymizer.mask_span_attributes.assert_called_with(raw)
        assert result is not None
        assert result.span_patches is not None
        patch = result.span_patches.get("span-2")  # type: ignore[call-overload]
        assert patch is not None
        assert patch.set_attributes == {"email": "[REDACTED]"}
        assert patch.delete_attributes == ("secret",)

        # Case C: Span with None attributes
        mock_anonymizer.mask_span_attributes.return_value = {}
        span_none_attr = SimpleNamespace(attributes=None)
        params_none = SimpleNamespace(spans={"span-3": span_none_attr})
        assert mask_fn(params=params_none) is None  # type: ignore[arg-type]
        mock_anonymizer.mask_span_attributes.assert_called_with({})

    def test_resolve_langfuse_client_probe_disabled_and_kwargs(
        self, tmp_path: Path
    ) -> None:
        settings = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v",
            langfuse_public_key="pk-custom",
            langfuse_secret_key=SecretStr("sk-custom"),
            langfuse_host="http://custom-host:3000",
            enable_preflight_probes=False,
            langfuse_timeout_seconds=45,
            langfuse_environment="staging",
        )

        mock_client = MagicMock()
        mock_langfuse_cls = MagicMock(return_value=mock_client)
        mock_anonymizer = MagicMock()

        with (
            patch("langfuse.Langfuse", mock_langfuse_cls),
            patch("cresmo.presentation.composition.name_telemetry_threads") as mock_name_threads,
        ):
            client = resolve_langfuse_client(settings, anonymizer=mock_anonymizer)
            assert client is mock_client
            mock_name_threads.assert_called_once_with(mock_client)

            mock_langfuse_cls.assert_called_once()
            _, kwargs = mock_langfuse_cls.call_args
            assert kwargs["public_key"] == "pk-custom"
            assert kwargs["secret_key"] == "sk-custom"
            assert kwargs["host"] == "http://custom-host:3000"
            assert kwargs["timeout"] == 45
            assert kwargs["environment"] == "staging"
            assert callable(kwargs["should_export_span"])
            assert callable(kwargs["mask_otel_spans"])

            assert os.environ["LANGFUSE_PUBLIC_KEY"] == "pk-custom"
            assert os.environ["LANGFUSE_SECRET_KEY"] == "sk-custom"
            assert os.environ["LANGFUSE_HOST"] == "http://custom-host:3000"
            assert os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] == "45"

        # Defaults when timeout and environment are completely missing from settings object
        s_missing_timeout_env = SimpleNamespace(
            langfuse_public_key="pk-defaults",
            langfuse_secret_key=SecretStr("sk-defaults"),
            langfuse_host="http://custom-host:3000",
            enable_preflight_probes=False,
        )
        with (
            patch.dict("sys.modules", {"langfuse": SimpleNamespace()}),
            patch("cresmo.presentation.composition.Langfuse", mock_langfuse_cls),
            patch("cresmo.presentation.composition.name_telemetry_threads"),
        ):
            resolve_langfuse_client(s_missing_timeout_env)  # type: ignore[arg-type]
            _, kwargs_def = mock_langfuse_cls.call_args
            assert kwargs_def["timeout"] == 30
            assert kwargs_def["environment"] == "development"
            assert os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] == "30"

    def test_resolve_langfuse_client_init_exception_logs_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        settings = SimpleNamespace(
            langfuse_public_key="pk-err",
            langfuse_secret_key=SecretStr("sk-err"),
            langfuse_host="http://host-err:3000",
            enable_preflight_probes=False,
        )
        with (
            patch("langfuse.Langfuse", side_effect=RuntimeError("Langfuse boom")),
            caplog.at_level(logging.WARNING),
        ):
            client = resolve_langfuse_client(settings)  # type: ignore[arg-type]
            assert client is None
            record = next(r for r in caplog.records if r.levelno == logging.WARNING)
            assert record.msg == "[composition] Failed to initialize Langfuse client: %s"
            assert record.args is not None and "Langfuse boom" in str(record.args)

    def test_resolve_langfuse_client_missing_keys_returns_none(self, tmp_path: Path) -> None:
        s1 = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v",
            langfuse_public_key="",
            langfuse_secret_key=SecretStr("sk-test"),
        )
        assert resolve_langfuse_client(s1) is None

        s2 = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v",
            langfuse_public_key="pk-test",
            langfuse_secret_key=SecretStr(""),
        )
        assert resolve_langfuse_client(s2) is None

    def test_build_sync_channel_use_case_parameter_and_port_wiring(
        self, test_settings: CresmoSettings
    ) -> None:
        # 1. Custom batch size override and check_ffmpeg defaulting to True
        uc = build_sync_channel_use_case(
            settings=test_settings,
            batch_size_override=19,
        )
        assert uc.pipeline.batch_size == 19
        assert uc.pipeline.settings is test_settings
        assert uc.media_ingestion_port is uc.pipeline.media_ingestion_port
        assert uc.ledger_port is uc.pipeline.ledger_port
        assert uc.preflight_checker is not None
        assert isinstance(uc.preflight_checker, PreflightHealthChecker)
        assert uc.preflight_checker._check_ffmpeg is True
        assert uc.preflight_checker._sqlite_ledger_path == test_settings.sqlite_ledger_path

        # 2. Explicit check_ffmpeg=False
        uc_false = build_sync_channel_use_case(
            settings=test_settings,
            check_ffmpeg=False,
        )
        assert uc_false.preflight_checker is not None
        assert uc_false.preflight_checker._check_ffmpeg is False

        # 3. None settings defaults correctly
        with patch("cresmo.presentation.composition.CresmoSettings", return_value=test_settings):
            uc_default = build_sync_channel_use_case(settings=None, check_ffmpeg=False)
            assert uc_default.pipeline is not None
            assert uc_default.media_ingestion_port is not None
            assert uc_default.ledger_port is not None

    def test_build_pipeline_logging_and_stage_runner_dependencies(
        self, test_settings: CresmoSettings
    ) -> None:
        with (
            patch("cresmo.presentation.composition.configure_logging") as mock_logging,
            patch("cresmo.infrastructure.config.CresmoSettings.ensure_directories") as mock_ensure_dirs,
        ):
            pipeline = build_pipeline(settings=test_settings, batch_size_override=23)
            mock_logging.assert_called_once_with(
                level=test_settings.log_level,
                fmt=test_settings.log_format,
            )
            mock_ensure_dirs.assert_called_once()
            assert pipeline.batch_size == 23

            runner = pipeline.stage_runner
            assert runner.telemetry_port is not None
            assert runner.metrics_port is not None
            assert runner.llm_judge is not None
            assert runner.judge_blocking == getattr(test_settings, "judge_blocking", False)
            assert runner.judge_max_attempts == getattr(test_settings, "judge_max_attempts", 1)
            assert runner.prompt_provider is not None
            assert runner.llm_transformation_port is pipeline.llm_synthesis_port
            assert runner.stage_factory is not None
            assert runner.critique_synthesizer is not None
            assert runner.ledger_port is pipeline.ledger_port

    def test_build_pipeline_missing_judge_attributes_fallbacks(
        self, tmp_path: Path
    ) -> None:
        real_settings = CresmoSettings(
            gemini_api_key=SecretStr("TEST"),
            vault_dir=tmp_path / "v_miss",
            prometheus_enabled=False,
        )

        class SettingsWithoutJudgeAttrs:
            def __getattr__(self, name: str) -> Any:
                if name in ("judge_blocking", "judge_max_attempts"):
                    raise AttributeError(f"No {name}")
                return getattr(real_settings, name)

        pipeline = build_pipeline(settings=SettingsWithoutJudgeAttrs())  # type: ignore[arg-type]
        assert pipeline.stage_runner.judge_blocking is False
        assert pipeline.stage_runner.judge_max_attempts == 1

    def test_build_pipeline_subfactory_wiring_integrity(
        self, test_settings: CresmoSettings
    ) -> None:
        mock_anon_adapter = MagicMock()
        mock_lf_client = MagicMock(name="langfuse_client")
        mock_tel_adapter = MagicMock()
        mock_ingest_adapter = MagicMock()
        mock_prompt_prov = MagicMock()
        mock_synth_adapter = MagicMock()
        mock_index_adapter = MagicMock()
        mock_judge_adapter = MagicMock()

        with (
            patch("cresmo.presentation.composition.build_anonymizer_adapter", return_value=mock_anon_adapter) as mock_anon,
            patch("cresmo.presentation.composition.resolve_langfuse_client", return_value=mock_lf_client) as mock_lf,
            patch("cresmo.presentation.composition.build_telemetry_adapter", return_value=mock_tel_adapter) as mock_tel,
            patch("cresmo.presentation.composition.build_media_ingestion_adapter", return_value=mock_ingest_adapter) as mock_ingest,
            patch("cresmo.presentation.composition.build_prompt_provider", return_value=mock_prompt_prov) as mock_prompt,
            patch("cresmo.presentation.composition.build_gemini_synthesis_adapter", return_value=mock_synth_adapter) as mock_gemini,
            patch("cresmo.presentation.composition.build_indexing_adapter", return_value=mock_index_adapter) as mock_idx,
            patch("cresmo.presentation.composition.build_llm_judge_adapter", return_value=mock_judge_adapter) as mock_judge,
            patch("cresmo.infrastructure.config.CresmoSettings.ensure_directories"),
        ):
            pipeline = build_pipeline(settings=test_settings, web_index=False)
            mock_anon.assert_called_once_with(test_settings)
            mock_lf.assert_called_once_with(test_settings, anonymizer=mock_anon_adapter)
            mock_tel.assert_called_once_with(test_settings, langfuse_client=mock_lf_client)
            mock_ingest.assert_called_once_with(test_settings)
            mock_prompt.assert_called_once_with(test_settings, langfuse_client=mock_lf_client)
            mock_gemini.assert_called_once_with(test_settings, langfuse_client=mock_lf_client)
            mock_idx.assert_called_once_with(
                test_settings,
                synthesis_adapter=mock_synth_adapter,
                web_index=False,
                langfuse_client=mock_lf_client,
            )
            mock_judge.assert_called_once_with(
                test_settings,
                langfuse_client=mock_lf_client,
                prompt_provider=mock_prompt_prov,
            )
            assert pipeline.media_ingestion_port is mock_ingest_adapter
            assert pipeline.llm_indexing_port is mock_index_adapter

    def test_build_sync_channel_use_case_wires_preflight_checker_with_settings(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.presentation.composition.build_preflight_checker") as mock_pfc:
            mock_pfc.return_value = MagicMock()
            build_sync_channel_use_case(settings=test_settings, check_ffmpeg=True)
            mock_pfc.assert_called_once_with(test_settings, check_ffmpeg=True)
