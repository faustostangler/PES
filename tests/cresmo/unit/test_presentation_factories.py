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
from cresmo.application.use_cases.discover_batch_sources import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.anonymizer_adapter import (
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
from cresmo.infrastructure.adapters.noop_metrics_adapter import NoOpMetricsAdapter
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.opentelemetry_adapter import NoOpTelemetryAdapter
from cresmo.infrastructure.adapters.prometheus_metrics_adapter import PrometheusMetricsAdapter
from cresmo.infrastructure.adapters.prompt_provider import (
    JsonPromptProvider,
    LangfusePromptProvider,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.adapter_factory import (
    _resolve_cookie_file,
    build_indexing_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_vault_adapter,
)
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter
from cresmo.presentation.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.presentation.factories.telemetry_factory import (
    _build_mask_hook,
    _build_should_export_span,
    _clean_langfuse_env,
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
    probe_langfuse_ready,
)
from cresmo.presentation.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_sync_channel_use_case,
    build_unify_duplicates_use_case,
)


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
            "cresmo.presentation.factories.telemetry_factory.probe_http_endpoint"
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

    def test_build_should_export_span(self) -> None:
        predicate = _build_should_export_span()
        span_mock = MagicMock()
        span_mock.instrumentation_scope.name = "cresmo.pipeline"
        assert predicate(span_mock) is True

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


class TestAdapterFactory:
    """Hermetic unit tests for adapter factory."""

    def test_resolve_cookie_file(self, tmp_path: Path, mock_settings: CresmoSettings) -> None:
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
