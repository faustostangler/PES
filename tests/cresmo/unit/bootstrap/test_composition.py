"""Unit tests for Cresmo Composition Root.

Verifies Dependency Injection assembly, port wiring, and configuration binding
per SPEC-002 §4.4 and ADR-074.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    MediaIngestionPort,
    NoOpMetricsPort,
    NoOpTelemetryPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discovery.discover_batch_sources import (
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.indexing.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.bootstrap.composition import (
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
    resolve_langfuse_client,
    resolve_shared_settings,
)
from cresmo.bootstrap.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
)
from cresmo.bootstrap.factories.telemetry_factory import (
    _build_mask_hook,
    _build_should_export_span,
    _clean_langfuse_env,
)
from cresmo.infrastructure.adapters.anonymization.anonymizer_adapter import (
    NoOpAnonymizerAdapter,
    RegexAnonymizerAdapter,
)
from cresmo.infrastructure.adapters.judges.composite_judge import (
    ResilientCompositeJudgeAdapter,
)
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator
from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.llm.ollama_llm_adapter import OllamaLLMAdapter
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter import (
    OtlpMetricsAdapter,
)
from cresmo.infrastructure.adapters.obsidian.adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import (
    OpenTelemetryAdapter,
)
from cresmo.infrastructure.config import (
    CresmoSettings,
    GeminiSettings,
    JudgeSettings,
    LangfuseSettings,
    LlmSettings,
    ObservabilitySettings,
    PipelineSettings,
    PrometheusSettings,
    RuntimeTelemetrySettings,
    StorageSettings,
)
from cresmo.infrastructure.persistence.sqlite_ledger_adapter import SqliteLedgerAdapter


class TestCompositionRoot:
    """Hermetic unit tests for the composition root factory."""

    @pytest.fixture
    def test_settings(self, tmp_path: Path) -> CresmoSettings:
        return CresmoSettings(
            _env_file=None,
            llm=LlmSettings(
                gemini=GeminiSettings(api_keys=(SecretStr("TEST_FAKE_KEY_FOR_COMPOSITION"),)),
            ),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
            pipeline=PipelineSettings(batch_size=7),
        )

    def test_build_pipeline_wires_all_ports_correctly(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings)

        assert isinstance(pipeline, CresmoPipeline)
        assert isinstance(pipeline.stage_runner, PipelineStageRunner)
        assert isinstance(pipeline.stage_runner.stage_factory, StageFactory)
        assert isinstance(pipeline.media_ingestion_port, NativeMediaIngestionAdapter)
        assert isinstance(pipeline.stage_runner.llm_transformation_port, GeminiLLMAdapter)
        assert isinstance(pipeline.vault_port, ObsidianVaultAdapter)
        assert isinstance(pipeline.ledger_port, SqliteLedgerAdapter)

    def test_build_pipeline_wires_prompt_provider_to_llm_judge(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.bootstrap.composition.build_llm_judge_adapter") as mock_build_judge:
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
        with patch(
            "cresmo.bootstrap.composition.resolve_shared_settings", return_value=test_settings
        ):
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
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys=(SecretStr("TEST_KEY"),))),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
            observability=ObservabilitySettings(
                langfuse=LangfuseSettings(
                    public_key="pk-lf-test",
                    secret_key=SecretStr("sk-lf-test"),
                    host="https://cloud.langfuse.com",
                ),
                runtime=RuntimeTelemetrySettings(anonymization_enabled=True),
            ),
        )

        mock_langfuse_instance = MagicMock()
        mock_langfuse_cls = MagicMock(return_value=mock_langfuse_instance)

        with (
            patch(
                "cresmo.bootstrap.factories.telemetry_factory.probe_langfuse_ready",
                return_value=True,
            ),
            patch.dict("sys.modules", {"langfuse": MagicMock(Langfuse=mock_langfuse_cls)}),
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert pipeline.stage_policy == settings_with_langfuse.to_stage_execution_policy()
            assert isinstance(pipeline.vault_port, ObsidianVaultAdapter)
            assert pipeline.vault_port.vault_dir == (tmp_path / "vault").resolve()
            assert pipeline.stage_runner.stage_factory is not None
            assert (
                pipeline.stage_runner.stage_factory.policy
                == settings_with_langfuse.to_stage_execution_policy()
            )
            assert isinstance(pipeline.stage_runner.llm_judge, TelemetryJudgeDecorator)
            assert pipeline.stage_runner.llm_judge._telemetry is pipeline.telemetry_port
            assert pipeline.llm_indexing_port is not None
            assert pipeline.media_ingestion_port is not None
            assert pipeline.vault_port is not None
            assert pipeline.ledger_port is not None
            assert isinstance(pipeline.stage_runner.llm_transformation_port, GeminiLLMAdapter)
            assert (
                pipeline.stage_runner.llm_transformation_port._telemetry is pipeline.telemetry_port
            )
            assert (
                getattr(pipeline.stage_runner.telemetry_port, "_langfuse", None)
                is mock_langfuse_instance
            )
            assert (
                getattr(pipeline.stage_runner.prompt_provider, "_client", None)
                is mock_langfuse_instance
            )
            assert (
                getattr(pipeline.stage_runner.critique_synthesizer, "llm_transformation_port", None)
                is pipeline.llm_indexing_port
            )
            assert (
                getattr(pipeline.stage_runner.critique_synthesizer, "_prompt_provider", None)
                is pipeline.stage_runner.prompt_provider
            )
            assert pipeline.stage_runner.ledger_port is pipeline.ledger_port

    def test_build_pipeline_skips_langfuse_when_probe_fails(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        settings_with_langfuse = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys=(SecretStr("TEST_KEY"),))),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
            observability=ObservabilitySettings(
                langfuse=LangfuseSettings(
                    public_key="pk-lf-test",
                    secret_key=SecretStr("sk-lf-test"),
                    host="http://localhost:3000",
                ),
            ),
        )

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_langfuse_ready", return_value=False
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.stage_runner.llm_transformation_port, GeminiLLMAdapter)
            assert isinstance(
                pipeline.stage_runner.llm_transformation_port._telemetry, NoOpTelemetryPort
            )

        captured = capsys.readouterr()
        assert "Langfuse server at 'http://localhost:3000' is unreachable" in captured.err
        assert "Telemetry bypassed to prevent OpenTelemetry retry loops.\n" in captured.err
        assert (
            "To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n"
            in captured.err
        )

    def test_build_pipeline_with_langfuse_import_or_init_error(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        settings_with_langfuse = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys=(SecretStr("TEST_KEY"),))),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
            observability=ObservabilitySettings(
                langfuse=LangfuseSettings(
                    public_key="pk-lf-test",
                    secret_key=SecretStr("sk-lf-test"),
                    host="https://cloud.langfuse.com",
                ),
            ),
        )

        with (
            patch(
                "cresmo.bootstrap.factories.telemetry_factory.probe_langfuse_ready",
                return_value=True,
            ),
            patch("langfuse.Langfuse", side_effect=RuntimeError("Langfuse init failed")),
            caplog.at_level(logging.WARNING),
        ):
            pipeline = build_pipeline(settings=settings_with_langfuse)
            assert isinstance(pipeline, CresmoPipeline)
            assert isinstance(pipeline.stage_runner.llm_transformation_port, GeminiLLMAdapter)
            assert isinstance(
                pipeline.stage_runner.llm_transformation_port._telemetry, NoOpTelemetryPort
            )

        record = next(
            r for r in caplog.records if "Failed to initialize Langfuse client" in r.getMessage()
        )
        assert getattr(record, "error", "") == "Langfuse init failed"

    def test_build_pipeline_judge_attempts_and_blocking_configurations(
        self, tmp_path: Path
    ) -> None:
        s_custom = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys=(SecretStr("TEST"),))),
            storage=StorageSettings(vault_dir=tmp_path / "v1", data_dir=tmp_path / "d1"),
            judge=JudgeSettings(blocking=True, max_attempts=5),
            observability=ObservabilitySettings(
                prometheus=PrometheusSettings(enabled=True),
                runtime=RuntimeTelemetrySettings(enable_preflight_probes=False),
            ),
        )
        p_custom = build_pipeline(settings=s_custom)
        assert p_custom.stage_runner.judge_blocking is True
        assert p_custom.stage_runner.judge_max_attempts == 5
        assert isinstance(p_custom.stage_runner.metrics_port, OtlpMetricsAdapter)

        s_default = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(api_keys=(SecretStr("TEST"),))),
            storage=StorageSettings(vault_dir=tmp_path / "v2", data_dir=tmp_path / "d2"),
            observability=ObservabilitySettings(prometheus=PrometheusSettings(enabled=False)),
        )
        p_default = build_pipeline(settings=s_default)
        assert p_default.stage_runner.judge_blocking is False
        assert p_default.stage_runner.judge_max_attempts == 2
        assert isinstance(p_default.stage_runner.metrics_port, NoOpMetricsPort)

    def test_build_pipeline_web_index_reuses_synthesis_adapter(
        self, test_settings: CresmoSettings
    ) -> None:
        pipeline = build_pipeline(settings=test_settings, web_index=True)
        assert pipeline.llm_indexing_port is pipeline.stage_runner.llm_transformation_port

    def test_build_pipeline_default_web_index_is_false(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings)
        assert pipeline.llm_indexing_port is not pipeline.stage_runner.llm_transformation_port
        assert isinstance(pipeline.llm_indexing_port, OllamaLLMAdapter)

    def test_probe_langfuse_ready_url_construction(self) -> None:
        from cresmo.bootstrap.factories.telemetry_factory import probe_langfuse_ready

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert probe_langfuse_ready("http://localhost:3000/serviceX") is True
            mock_probe.assert_called_once_with(
                "http://localhost:3000/serviceX/api/public/health",
                timeout_seconds=2.0,
            )

    def test_probe_langfuse_ready_strips_trailing_slash(self) -> None:
        from cresmo.bootstrap.factories.telemetry_factory import probe_langfuse_ready

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_http_endpoint", return_value=True
        ) as mock_probe:
            assert (
                probe_langfuse_ready("http://localhost:3000/serviceX/", timeout_seconds=0.5) is True
            )
            mock_probe.assert_called_once_with(
                "http://localhost:3000/serviceX/api/public/health",
                timeout_seconds=0.5,
            )

    def test_resolve_langfuse_client_preflight_timeout_wiring(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        o1 = ObservabilitySettings(
            langfuse=LangfuseSettings(
                public_key="pk-1",
                secret_key=SecretStr("sk-1"),
                host="http://host1:3000",
            ),
        )
        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_langfuse_ready", return_value=False
        ) as mock_probe:
            assert resolve_langfuse_client(o1) is None
            mock_probe.assert_called_once_with("http://host1:3000", timeout_seconds=2.0)
            captured = capsys.readouterr()
            expected_msg = (
                f"[preflight] Langfuse server at '{o1.langfuse.host}' is unreachable. "
                "Telemetry bypassed to prevent OpenTelemetry retry loops.\n"
                "            To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n"
            )
            assert captured.err == expected_msg

        o2 = ObservabilitySettings(
            langfuse=LangfuseSettings(
                public_key="pk-2",
                secret_key=SecretStr("sk-2"),
                host="http://host2:3000",
            ),
            runtime=RuntimeTelemetrySettings(preflight_probe_timeout_seconds=3.5),
        )
        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_langfuse_ready", return_value=False
        ) as mock_probe2:
            assert resolve_langfuse_client(o2) is None
            mock_probe2.assert_called_once_with("http://host2:3000", timeout_seconds=3.5)

    def test_build_concat_master_use_case(self, test_settings: CresmoSettings) -> None:
        uc = build_concat_master_use_case(settings=test_settings)
        assert isinstance(uc, ConcatMasterUseCase)
        assert uc.rollover_policy == test_settings.to_compendium_rollover_policy()

    def test_build_index_raw_use_case_default_ollama(self, test_settings: CresmoSettings) -> None:
        uc = build_index_raw_use_case(settings=test_settings, web_index=False)
        assert isinstance(uc, IndexRawTranscriptsUseCase)
        assert isinstance(uc.llm_indexing_port, OllamaLLMAdapter)
        assert isinstance(uc.vault_port, ObsidianVaultAdapter)

    def test_build_index_raw_use_case_web_index_gemini(self, test_settings: CresmoSettings) -> None:
        uc = build_index_raw_use_case(settings=test_settings, web_index=True)
        assert isinstance(uc, IndexRawTranscriptsUseCase)
        assert isinstance(uc.llm_indexing_port, GeminiLLMAdapter)
        assert isinstance(uc.vault_port, ObsidianVaultAdapter)

    def test_build_pipeline_with_web_index(self, test_settings: CresmoSettings) -> None:
        pipeline = build_pipeline(settings=test_settings, web_index=True)
        assert isinstance(pipeline, CresmoPipeline)
        assert isinstance(pipeline.llm_indexing_port, GeminiLLMAdapter)

    def test_build_sync_channel_use_case_raises_runtime_error_when_ledger_port_missing(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.bootstrap.composition.build_pipeline") as mock_build_pipeline:
            mock_pipeline = MagicMock(spec=CresmoPipeline)
            mock_pipeline.ledger_port = None
            mock_build_pipeline.return_value = mock_pipeline

            with pytest.raises(
                RuntimeError, match=r"^Ledger port must be wired for channel sync\.$"
            ):
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

    def test_build_anonymizer_adapter_enabled_and_disabled(self) -> None:
        enabled = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(anonymization_enabled=True)
        )
        assert isinstance(build_anonymizer_adapter(enabled), RegexAnonymizerAdapter)

        disabled = ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(anonymization_enabled=False)
        )
        assert isinstance(build_anonymizer_adapter(disabled), NoOpAnonymizerAdapter)

    def test_build_telemetry_adapter_with_and_without_client(
        self, test_settings: CresmoSettings
    ) -> None:
        mock_client = MagicMock()
        adapter = build_telemetry_adapter(test_settings.observability, langfuse_client=mock_client)
        assert isinstance(adapter, OpenTelemetryAdapter)

        noop = build_telemetry_adapter(test_settings.observability, langfuse_client=None)
        assert isinstance(noop, NoOpTelemetryPort)

    def test_build_metrics_adapter_enabled_and_disabled(self) -> None:
        enabled = ObservabilitySettings(
            prometheus=PrometheusSettings(enabled=True),
            runtime=RuntimeTelemetrySettings(enable_preflight_probes=False),
        )
        assert isinstance(build_metrics_adapter(enabled), OtlpMetricsAdapter)

        disabled = ObservabilitySettings(prometheus=PrometheusSettings(enabled=False))
        assert isinstance(build_metrics_adapter(disabled), NoOpMetricsPort)

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.probe_prometheus_ready",
            return_value=False,
        ):
            probed_down = ObservabilitySettings(
                prometheus=PrometheusSettings(enabled=True),
                runtime=RuntimeTelemetrySettings(enable_preflight_probes=True),
            )
            assert isinstance(build_metrics_adapter(probed_down), NoOpMetricsPort)

    def test_build_prompt_provider(self, test_settings: CresmoSettings) -> None:
        provider = build_prompt_provider(test_settings, langfuse_client=None)
        assert isinstance(provider, LangfusePromptProvider)
        assert isinstance(provider._fallback, JsonPromptProvider)

    def test_build_gemini_synthesis_adapter(self, test_settings: CresmoSettings) -> None:
        adapter = build_gemini_synthesis_adapter(test_settings.llm.gemini, telemetry_port=None)
        assert isinstance(adapter, GeminiLLMAdapter)
        assert adapter.model_name == test_settings.llm.gemini.model

    def test_build_indexing_adapter_selection(self, test_settings: CresmoSettings) -> None:
        ollama_adapter = build_indexing_adapter(test_settings.llm, web_index=False)
        assert isinstance(ollama_adapter, OllamaLLMAdapter)

        gemini_adapter = build_indexing_adapter(test_settings.llm, web_index=True)
        assert isinstance(gemini_adapter, GeminiLLMAdapter)

        mock_synthesis = MagicMock(spec=GeminiLLMAdapter)
        reused = build_indexing_adapter(
            test_settings.llm, synthesis_adapter=mock_synthesis, web_index=True
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

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.is_default_export_span", return_value=True
        ) as mock_default:
            span_default = SimpleNamespace()
            assert predicate(span_default) is True
            mock_default.assert_called_once_with(span_default)

        with patch(
            "cresmo.bootstrap.factories.telemetry_factory.is_default_export_span",
            return_value=False,
        ) as mock_not_default:
            span_cresmo = SimpleNamespace(
                instrumentation_scope=SimpleNamespace(name="cresmo.pipeline.runner")
            )
            assert predicate(span_cresmo) is True
            mock_not_default.assert_called_once_with(span_cresmo)

            span_other = SimpleNamespace(
                instrumentation_scope=SimpleNamespace(name="requests.opentelemetry")
            )
            assert predicate(span_other) is False

            span_none_scope = SimpleNamespace(instrumentation_scope=None)
            assert predicate(span_none_scope) is False

            span_no_scope = SimpleNamespace()
            assert predicate(span_no_scope) is False

    def test_build_mask_hook_filtering_and_patching(self) -> None:
        assert _build_mask_hook(None) is None

        mock_anonymizer = MagicMock()
        mask_fn = _build_mask_hook(mock_anonymizer)
        assert mask_fn is not None

        mock_anonymizer.mask_mapping.return_value = {"key1": "val1"}
        span_clean = SimpleNamespace(attributes={"key1": "val1"})
        params_clean = SimpleNamespace(spans={"span-1": span_clean})
        assert mask_fn(params=params_clean) is None  # type: ignore[arg-type]
        mock_anonymizer.mask_mapping.assert_called_with({"key1": "val1"})

        raw = {"email": "user@test.com", "secret": "123", "normal": "public"}
        sanitized = {"email": "[REDACTED]", "normal": "public"}
        mock_anonymizer.mask_mapping.return_value = sanitized
        span_pii = SimpleNamespace(attributes=raw)
        params_pii = SimpleNamespace(spans={"span-2": span_pii})

        result = mask_fn(params=params_pii)  # type: ignore[arg-type]
        mock_anonymizer.mask_mapping.assert_called_with(raw)
        assert result is not None
        assert result.span_patches is not None
        patch_obj = result.span_patches.get("span-2")  # type: ignore[call-overload]
        assert patch_obj is not None
        assert patch_obj.set_attributes == {"email": "[REDACTED]"}
        assert patch_obj.delete_attributes == ("secret",)

        mock_anonymizer.mask_mapping.return_value = {}
        span_none_attr = SimpleNamespace(attributes=None)
        params_none = SimpleNamespace(spans={"span-3": span_none_attr})
        assert mask_fn(params=params_none) is None  # type: ignore[arg-type]
        mock_anonymizer.mask_mapping.assert_called_with({})

    def test_resolve_langfuse_client_probe_disabled_and_kwargs(self) -> None:
        obs = ObservabilitySettings(
            langfuse=LangfuseSettings(
                public_key="pk-custom",
                secret_key=SecretStr("sk-custom"),
                host="http://custom-host:3000",
                timeout_seconds=45,
                environment="staging",
            ),
            runtime=RuntimeTelemetrySettings(enable_preflight_probes=False),
        )

        mock_client = MagicMock()
        mock_langfuse_cls = MagicMock(return_value=mock_client)
        mock_anonymizer = MagicMock()

        with (
            patch("langfuse.Langfuse", mock_langfuse_cls),
            patch(
                "cresmo.bootstrap.factories.telemetry_factory.name_telemetry_threads"
            ) as mock_name_threads,
        ):
            client = resolve_langfuse_client(obs, anonymizer=mock_anonymizer)
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
            assert os.environ["LANGFUSE_TRACING_ENVIRONMENT"] == "staging"
            assert os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] == "45"

        _clean_langfuse_env()
        assert "LANGFUSE_TRACING_ENVIRONMENT" not in os.environ

    def test_resolve_langfuse_client_init_exception_logs_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        obs = ObservabilitySettings(
            langfuse=LangfuseSettings(
                public_key="pk-err",
                secret_key=SecretStr("sk-err"),
                host="http://host-err:3000",
            ),
            runtime=RuntimeTelemetrySettings(enable_preflight_probes=False),
        )
        with (
            patch("langfuse.Langfuse", side_effect=RuntimeError("Langfuse boom")),
            caplog.at_level(logging.WARNING),
        ):
            client = resolve_langfuse_client(obs)
            assert client is None
            record = next(r for r in caplog.records if r.levelno == logging.WARNING)
            assert "Failed to initialize Langfuse client" in record.getMessage()
            assert getattr(record, "error", "") == "Langfuse boom"

    def test_resolve_langfuse_client_missing_keys_returns_none(self) -> None:
        o1 = ObservabilitySettings(
            langfuse=LangfuseSettings(public_key="", secret_key=SecretStr("sk-test"))
        )
        assert resolve_langfuse_client(o1) is None

        o2 = ObservabilitySettings(
            langfuse=LangfuseSettings(public_key="pk-test", secret_key=SecretStr(""))
        )
        assert resolve_langfuse_client(o2) is None

    def test_build_sync_channel_use_case_parameter_and_port_wiring(
        self, test_settings: CresmoSettings
    ) -> None:
        uc = build_sync_channel_use_case(settings=test_settings)
        assert uc.pipeline.stage_policy == test_settings.to_stage_execution_policy()
        assert uc.media_ingestion_port is uc.pipeline.media_ingestion_port
        assert uc.ledger_port is uc.pipeline.ledger_port
        assert uc.preflight_checker is not None
        assert isinstance(uc.preflight_checker, PreflightHealthChecker)
        assert uc.preflight_checker._check_ffmpeg is True
        assert uc.preflight_checker._sqlite_ledger_path == test_settings.storage.sqlite_ledger_path

        uc_false = build_sync_channel_use_case(
            settings=test_settings,
            check_ffmpeg=False,
        )
        assert uc_false.preflight_checker is not None
        assert uc_false.preflight_checker._check_ffmpeg is False

        with patch(
            "cresmo.bootstrap.composition.resolve_shared_settings", return_value=test_settings
        ):
            uc_default = build_sync_channel_use_case(settings=None, check_ffmpeg=False)
            assert uc_default.pipeline is not None
            assert uc_default.media_ingestion_port is not None
            assert uc_default.ledger_port is not None

    def test_build_pipeline_logging_and_stage_runner_dependencies(
        self, test_settings: CresmoSettings
    ) -> None:
        with (
            patch("cresmo.bootstrap.composition.configure_logging") as mock_logging,
            patch(
                "cresmo.infrastructure.config.CresmoSettings.ensure_directories"
            ) as mock_ensure_dirs,
        ):
            pipeline = build_pipeline(settings=test_settings)
            mock_logging.assert_called_once_with(
                level=test_settings.observability.logging.level,
                fmt=test_settings.observability.logging.format,
            )
            mock_ensure_dirs.assert_called_once()

            runner = pipeline.stage_runner
            assert runner.telemetry_port is not None
            assert runner.metrics_port is not None
            assert runner.llm_judge is not None
            assert runner.judge_blocking == test_settings.judge.blocking
            assert runner.judge_max_attempts == test_settings.judge.max_attempts
            assert runner.prompt_provider is not None
            assert isinstance(runner.llm_transformation_port, GeminiLLMAdapter)
            assert runner.stage_factory is not None
            assert runner.critique_synthesizer is not None
            assert runner.ledger_port is pipeline.ledger_port

    def test_build_pipeline_subfactory_wiring_integrity(
        self, test_settings: CresmoSettings
    ) -> None:
        mock_anon_adapter = MagicMock()
        mock_lf_client = MagicMock(name="langfuse_client")
        mock_tel_adapter = MagicMock()
        mock_ingest_adapter = MagicMock()
        mock_prompt_prov = MagicMock()
        mock_pool = MagicMock()
        mock_synth_adapter = MagicMock()
        mock_index_adapter = MagicMock()
        mock_judge_adapter = MagicMock()

        with (
            patch(
                "cresmo.bootstrap.composition.build_anonymizer_adapter",
                return_value=mock_anon_adapter,
            ) as mock_anon,
            patch(
                "cresmo.bootstrap.composition.resolve_langfuse_client",
                return_value=mock_lf_client,
            ) as mock_lf,
            patch(
                "cresmo.bootstrap.composition.build_telemetry_adapter",
                return_value=mock_tel_adapter,
            ) as mock_tel,
            patch(
                "cresmo.bootstrap.composition.build_media_ingestion_adapter",
                return_value=mock_ingest_adapter,
            ) as mock_ingest,
            patch(
                "cresmo.bootstrap.composition.build_prompt_provider",
                return_value=mock_prompt_prov,
            ) as mock_prompt,
            patch(
                "cresmo.bootstrap.composition.build_gemini_credential_pool",
                return_value=mock_pool,
            ) as mock_pool_builder,
            patch(
                "cresmo.bootstrap.composition.build_gemini_synthesis_adapter",
                return_value=mock_synth_adapter,
            ) as mock_gemini,
            patch(
                "cresmo.bootstrap.composition.build_indexing_adapter",
                return_value=mock_index_adapter,
            ) as mock_idx,
            patch(
                "cresmo.bootstrap.composition.build_llm_judge_adapter",
                return_value=mock_judge_adapter,
            ) as mock_judge,
            patch("cresmo.infrastructure.config.CresmoSettings.ensure_directories"),
        ):
            pipeline = build_pipeline(settings=test_settings, web_index=False)
            mock_anon.assert_called_once_with(test_settings.observability)
            mock_lf.assert_called_once_with(
                test_settings.observability, anonymizer=mock_anon_adapter
            )
            mock_tel.assert_called_once_with(
                test_settings.observability, langfuse_client=mock_lf_client
            )
            mock_ingest.assert_called_once_with(test_settings)
            mock_prompt.assert_called_once_with(test_settings, langfuse_client=mock_lf_client)
            mock_pool_builder.assert_called_once_with(test_settings.llm.gemini)
            mock_gemini.assert_called_once_with(
                test_settings.llm.gemini,
                telemetry_port=mock_tel_adapter,
                credential_pool=mock_pool,
            )
            mock_idx.assert_called_once_with(
                test_settings.llm,
                synthesis_adapter=mock_synth_adapter,
                web_index=False,
                telemetry_port=mock_tel_adapter,
                credential_pool=mock_pool,
            )
            mock_judge.assert_called_once_with(
                test_settings,
                telemetry_port=mock_tel_adapter,
                prompt_provider=mock_prompt_prov,
                credential_pool=mock_pool,
            )
            assert pipeline.media_ingestion_port is mock_ingest_adapter
            assert pipeline.llm_indexing_port is mock_index_adapter

    def test_build_sync_channel_use_case_wires_preflight_checker_with_settings(
        self, test_settings: CresmoSettings
    ) -> None:
        with patch("cresmo.bootstrap.composition.build_preflight_checker") as mock_pfc:
            mock_pfc.return_value = MagicMock()
            build_sync_channel_use_case(settings=test_settings, check_ffmpeg=True)
            mock_pfc.assert_called_once_with(test_settings, check_ffmpeg=True)

    def test_gemini_timeout_seconds_wired_into_synthesis_and_indexing_adapters(
        self, tmp_path: Path
    ) -> None:
        """Verify llm.gemini.timeout_seconds propagates to synthesis and web_index adapters."""
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(
                gemini=GeminiSettings(
                    api_keys=(SecretStr("TEST_FAKE_KEY_FOR_TIMEOUT"),),
                    timeout_seconds=180.0,
                ),
            ),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
        )

        synthesis_adapter = build_gemini_synthesis_adapter(settings.llm.gemini, telemetry_port=None)
        assert isinstance(synthesis_adapter, GeminiLLMAdapter)
        assert synthesis_adapter.timeout_seconds == 180.0
        assert synthesis_adapter._pool is not None
        assert synthesis_adapter._pool.timeout == 180.0

        indexing_adapter = build_indexing_adapter(settings.llm, web_index=True)
        assert isinstance(indexing_adapter, GeminiLLMAdapter)
        assert indexing_adapter.timeout_seconds == 180.0
        assert indexing_adapter._pool is not None
        assert indexing_adapter._pool.timeout == 180.0

    def test_build_pipeline_shares_single_gemini_credential_pool_across_synthesis_and_judge(
        self, tmp_path: Path
    ) -> None:
        """Verify build_pipeline injects identical GeminiCredentialPool into synthesis and judge."""
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(
                gemini=GeminiSettings(
                    api_keys=(SecretStr("KEY_PRIMARY_POOL"), SecretStr("KEY_SECONDARY_POOL")),
                ),
            ),
            storage=StorageSettings(vault_dir=tmp_path / "vault", data_dir=tmp_path / "data"),
            judge=JudgeSettings(provider="gemini"),
            observability=ObservabilitySettings(prometheus=PrometheusSettings(enabled=False)),
        )

        pipeline = build_pipeline(settings=settings, web_index=True)

        synthesis_adapter = pipeline.stage_runner.llm_transformation_port
        assert isinstance(synthesis_adapter, GeminiLLMAdapter)

        judge_adapter = pipeline.stage_runner.llm_judge
        assert isinstance(judge_adapter, TelemetryJudgeDecorator)
        preflight = judge_adapter._inner_judge
        assert isinstance(preflight, MechanicalPreflightJudgeDecorator)
        composite = preflight._inner_judge
        assert isinstance(composite, ResilientCompositeJudgeAdapter)
        primary_judge = composite._primary
        assert isinstance(primary_judge, GeminiJudgeAdapter)

        assert synthesis_adapter._pool is primary_judge._pool

        primary_key, _, _ = synthesis_adapter._pool.lease()
        synthesis_adapter._pool.report_quota_exhausted(primary_key, 300.0)
        assert primary_judge._pool is not None
        judge_key, _, _ = primary_judge._pool.lease()
        assert judge_key == "KEY_SECONDARY_POOL"
