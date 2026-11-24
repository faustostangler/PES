"""Hermetic unit tests for hierarchical immutable config sub-models and nested .env loading."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

import cresmo.infrastructure.config as cresmo_config
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
    PipelineSettings,
    SaturationSettings,
    StageBudgetsSettings,
    StorageSettings,
    TypeSafeSettings,
    WorkerPoolSettings,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS as CATALOG_DEFAULT_BENCHMARK_MODELS,
)
from cresmo.infrastructure.config.catalog import (
    DEFAULT_GEMINI_MODEL as CATALOG_DEFAULT_GEMINI_MODEL,
)
from cresmo.infrastructure.config.catalog import (
    DEFAULT_JUDGE_PASS_THRESHOLD as CATALOG_DEFAULT_JUDGE_PASS_THRESHOLD,
)
from cresmo.infrastructure.config.catalog import (
    DEFAULT_LANGFUSE_ENVIRONMENT as CATALOG_DEFAULT_LANGFUSE_ENVIRONMENT,
)
from cresmo.infrastructure.config.catalog import (
    DEFAULT_LANGFUSE_PROMPT_LABEL as CATALOG_DEFAULT_LANGFUSE_PROMPT_LABEL,
)
from cresmo.infrastructure.config.catalog import (
    GEMINI_FREE_TIER_MODELS as CATALOG_GEMINI_FREE_TIER_MODELS,
)
from cresmo.infrastructure.config.catalog import (
    GEMINI_THINKING_LEVELS as CATALOG_GEMINI_THINKING_LEVELS,
)
from cresmo.infrastructure.config.catalog import (
    LANGFUSE_ENVIRONMENT_PATTERN as CATALOG_LANGFUSE_ENVIRONMENT_PATTERN,
)


class TestModularExports:
    """Validate __all__ completeness and direct catalog constant alignment."""

    def test_catalog_exports_and_dunder_all(self) -> None:
        assert cresmo_config.DEFAULT_GEMINI_MODEL == CATALOG_DEFAULT_GEMINI_MODEL
        assert cresmo_config.DEFAULT_BENCHMARK_MODELS == CATALOG_DEFAULT_BENCHMARK_MODELS
        assert cresmo_config.DEFAULT_JUDGE_PASS_THRESHOLD == CATALOG_DEFAULT_JUDGE_PASS_THRESHOLD
        assert cresmo_config.DEFAULT_LANGFUSE_ENVIRONMENT == CATALOG_DEFAULT_LANGFUSE_ENVIRONMENT
        assert cresmo_config.DEFAULT_LANGFUSE_PROMPT_LABEL == CATALOG_DEFAULT_LANGFUSE_PROMPT_LABEL
        assert cresmo_config.GEMINI_FREE_TIER_MODELS == CATALOG_GEMINI_FREE_TIER_MODELS
        assert cresmo_config.GEMINI_THINKING_LEVELS == CATALOG_GEMINI_THINKING_LEVELS
        assert cresmo_config.LANGFUSE_ENVIRONMENT_PATTERN == CATALOG_LANGFUSE_ENVIRONMENT_PATTERN

        expected = {
            "CookieSettings",
            "CresmoSettings",
            "EmbeddingSettings",
            "GapFillerJudgeSettings",
            "GeminiSettings",
            "IngestionSettings",
            "JudgeGeminiSettings",
            "JudgeSettings",
            "LangfuseSettings",
            "LlmSettings",
            "LoggingSettings",
            "ObservabilitySettings",
            "OllamaSettings",
            "PipelineSettings",
            "PrometheusSettings",
            "RuntimeTelemetrySettings",
            "SaturationSettings",
            "StageBudgetsSettings",
            "StorageSettings",
            "TypeSafeSettings",
            "WorkerPoolSettings",
            "get_shared_settings",
            "reset_shared_settings",
            "resolve_shared_settings",
        }
        assert expected.issubset(set(cresmo_config.__all__))


class TestLlmAndEmbeddingSettings:
    """Validate LlmSettings, GeminiSettings, OllamaSettings, and EmbeddingSettings."""

    def test_llm_defaults_and_immutability(self) -> None:
        llm = LlmSettings()
        assert llm.gemini.api_keys == ()
        assert llm.gemini.primary_api_key() == SecretStr("")
        assert llm.gemini.model == "gemini-3.5-flash-lite"
        assert llm.gemini.fallback_model == "gemini-3.6-flash"
        assert llm.gemini.thinking_level == "low"
        assert llm.gemini.max_output_tokens == 32_768
        assert llm.gemini.timeout_seconds == 300.0
        assert llm.ollama.base_url == "http://localhost:11434"
        assert llm.ollama.model == "qwen2.5:7b"
        assert llm.ollama.timeout_seconds == 300.0
        assert llm.ollama.warmup_timeout_seconds == 300.0
        assert llm.ollama.keep_alive == "1h"
        assert llm.ollama.num_predict == 0
        assert llm.ollama.synthesis_temperature == 0.2
        assert llm.ollama.indexing_temperature == 0.2
        assert llm.indexing_provider == "ollama"

        with pytest.raises(ValidationError):
            llm.gemini.model = "other"  # type: ignore[misc]

    def test_gemini_api_keys_parsing_modes(self) -> None:
        from_csv = GeminiSettings(api_keys="key-one, key-two , , key-three")  # type: ignore[arg-type]
        assert [k.get_secret_value() for k in from_csv.api_keys] == [
            "key-one",
            "key-two",
            "key-three",
        ]
        assert from_csv.primary_api_key().get_secret_value() == "key-one"

        from_json = GeminiSettings(api_keys='["j-1", "j-2"]')  # type: ignore[arg-type]
        assert [k.get_secret_value() for k in from_json.api_keys] == ["j-1", "j-2"]

        from_secret = GeminiSettings(api_keys=SecretStr("solo"))  # type: ignore[arg-type]
        assert [k.get_secret_value() for k in from_secret.api_keys] == ["solo"]

        with pytest.raises(ValidationError):
            GeminiSettings.model_validate({"api_keys": [123]})

    def test_gemini_thinking_level_and_temperature_bounds(self) -> None:
        normalized = GeminiSettings(thinking_level=" HIGH ")  # type: ignore[arg-type]
        assert normalized.thinking_level == "high"

        with pytest.raises(ValidationError):
            GeminiSettings.model_validate({"thinking_level": "ultra"})

        low = OllamaSettings(synthesis_temperature=0.0, indexing_temperature=0.0)
        high = OllamaSettings(synthesis_temperature=2.0, indexing_temperature=2.0)
        assert low.synthesis_temperature == 0.0
        assert high.indexing_temperature == 2.0

        for invalid in (
            {"synthesis_temperature": -0.1},
            {"synthesis_temperature": 2.1},
            {"indexing_temperature": -0.1},
            {"indexing_temperature": 2.1},
        ):
            with pytest.raises(ValidationError):
                OllamaSettings.model_validate(invalid)

    def test_embedding_settings_defaults_and_normalization(self) -> None:
        emb = EmbeddingSettings()
        assert emb.provider == "gemini"
        assert emb.gemini_model == "gemini-embedding-001"
        assert emb.gemini_dimensions == 768
        assert emb.ollama_model == "nomic-embed-text"

        assert EmbeddingSettings(provider=" OLLAMA ").provider == "ollama"  # type: ignore[arg-type]
        assert EmbeddingSettings(provider=" TfIdF ").provider == "tfidf"  # type: ignore[arg-type]

        with pytest.raises(ValidationError):
            EmbeddingSettings.model_validate({"provider": "unknown"})
        with pytest.raises(ValidationError):
            EmbeddingSettings.model_validate({"gemini_dimensions": 0})


class TestObservabilitySettings:
    """Validate ObservabilitySettings, Langfuse environment regex, and runtime controls."""

    def test_defaults(self) -> None:
        obs = ObservabilitySettings()
        assert obs.langfuse.host == "https://cloud.langfuse.com"
        assert obs.langfuse.environment == "staging"
        assert obs.langfuse.prompt_label == "production"
        assert obs.langfuse.timeout_seconds == 30
        assert obs.prometheus.enabled is True
        assert obs.prometheus.port == 9090
        assert obs.logging.level == "WARNING"
        assert obs.logging.format == "json"
        assert obs.runtime.pipeline_version.startswith("cresmo:v")
        assert obs.runtime.git_sha is None
        assert obs.runtime.anonymization_enabled is True
        assert obs.runtime.enable_preflight_probes is True
        assert obs.runtime.preflight_probe_timeout_seconds == 2.0

    def test_langfuse_environment_validation(self) -> None:
        assert LangfuseSettings(environment="  Production ").environment == "production"
        assert LangfuseSettings(environment="a" * 40).environment == "a" * 40

        for invalid in (
            "",
            "   ",
            "langfuse",
            "langfuse-prod",
            "a" * 41,
            "prod/1",
            "prod.1",
            "prod env",
        ):
            with pytest.raises(ValidationError):
                LangfuseSettings(environment=invalid)


class TestStorageAndIngestionSettings:
    """Validate StorageSettings derived paths and IngestionSettings worker pool math."""

    def test_storage_derived_paths(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "lake"
        vault_dir = tmp_path / "obsidian"
        storage = StorageSettings(data_dir=data_dir, vault_dir=vault_dir)

        assert storage.raw_dir == data_dir / "raw"
        assert storage.fluid_dir == data_dir / "fluid_prose"
        assert storage.gap_filler_dir == data_dir / "gap_filler"
        assert storage.enriched_dir == data_dir / "enriched"
        assert storage.master_dir == data_dir / "master"
        assert storage.index_path == vault_dir / "_index.json"
        assert storage.mocs_dir == vault_dir / "MOCs"
        assert storage.sqlite_ledger_path == data_dir / "cresmo_ledger.db"
        assert storage.brain_csv_path == data_dir / "brain.csv"
        assert storage.playlist_path == data_dir / "playlist.txt"
        assert storage.playlist_priority_path == data_dir / "playlist-priority.txt"
        assert storage.priority_texts_dir == data_dir / "priority"

    def test_worker_pool_frozen_multiples_and_overrides(self) -> None:
        default_workers = WorkerPoolSettings()
        assert default_workers.whisper == 1
        assert default_workers.subtitle == 5
        assert default_workers.channel_discovery == 10
        assert default_workers.discovery_queue_maxsize == 50

        scaled = WorkerPoolSettings(whisper=3)
        assert scaled.subtitle == 15
        assert scaled.channel_discovery == 30

        explicit = WorkerPoolSettings(whisper=3, subtitle=7, channel_discovery=11)
        assert explicit.subtitle == 7
        assert explicit.channel_discovery == 11

        with pytest.raises(ValidationError):
            scaled.subtitle = 99  # type: ignore[misc]

        with pytest.raises(ValidationError):
            WorkerPoolSettings.model_validate({"discovery_queue_maxsize": 0})

    def test_cookies_settings_defaults(self) -> None:
        cookies = CookieSettings()
        assert cookies.browser == "firefox"
        assert cookies.auto_extract is True
        assert cookies.require_auth is False
        assert cookies.file is None


class TestPipelineAndJudgeSettings:
    """Validate StageBudgetsSettings, SaturationSettings, and JudgeSettings."""

    def test_stage_budgets_and_saturation_bounds(self) -> None:
        budgets = StageBudgetsSettings()
        assert budgets.expansion_max_passes == 5
        assert budgets.long_expander_max_passes == 7
        assert budgets.raw_index_max_attempts == 2
        assert budgets.inventory_max_attempts == 2

        for bad in (0, 11):
            with pytest.raises(ValidationError):
                StageBudgetsSettings.model_validate({"expansion_max_passes": bad})
            with pytest.raises(ValidationError):
                StageBudgetsSettings.model_validate({"long_expander_max_passes": bad})

        sat = SaturationSettings(
            lexical_threshold=1.0,
            max_word_delta=0.0,
            semantic_threshold=1.0,
            sliding_window_sentences=3,
            sliding_window_overlap=2,
        )
        assert sat.to_domain_thresholds().sliding_window_overlap == 2

        for payload in (
            {"lexical_threshold": 0.0},
            {"lexical_threshold": 1.01},
            {"max_word_delta": -0.01},
            {"semantic_threshold": 0.0},
            {"max_novel_paragraphs": -1},
            {"long_unit_word_cutoff": 0},
            {"sliding_window_sentences": 0},
            {"sliding_window_overlap": -1},
            {"sliding_window_sentences": 3, "sliding_window_overlap": 3},
        ):
            with pytest.raises(ValidationError):
                SaturationSettings.model_validate(payload)

    def test_judge_settings_and_benchmark_models(self) -> None:
        judge = JudgeSettings()
        assert judge.typesafe == TypeSafeSettings()
        assert judge.gemini == JudgeGeminiSettings()
        assert judge.provider == "gemini"
        assert judge.fallback_provider == "ollama"
        assert judge.blocking is False
        assert judge.max_attempts == 2
        assert judge.pass_threshold == 0.9
        assert judge.gap_filler.threshold == 0.9
        assert sum(judge.gap_filler.weights.values()) == pytest.approx(1.0)
        assert judge.benchmark_models == (
            "gemini:gemini-3.5-flash-lite",
            "gemini:gemini-3.8-flash",
            "gemini:gemini-4-hydrogen",
        )

        custom = JudgeSettings(
            benchmark_models="gemini:gemini-3.5-flash-lite, ollama:qwen2.5:14b",  # type: ignore[arg-type]
            gemini=JudgeGeminiSettings(thinking_level=" XHIGH "),  # type: ignore[arg-type]
        )
        assert custom.benchmark_models == ("gemini:gemini-3.5-flash-lite", "ollama:qwen2.5:14b")
        assert custom.gemini.thinking_level == "xhigh"

        with pytest.raises(ValidationError):
            JudgeSettings.model_validate({"max_attempts": 0})


class TestNestedEnvLoadingAndSharedResolution:
    """Validate CRESMO_*__* .env loading across all 7 sections and singleton helpers."""

    def test_nested_env_file_loads_all_seven_sections(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key in list(monkeypatch._setitem) if hasattr(monkeypatch, "_setitem") else []:
            _ = key

        env_data_dir = tmp_path / "env_data"
        env_vault_dir = tmp_path / "env_vault"
        custom_env = tmp_path / "nested.env"
        custom_env.write_text(
            "\n".join(
                [
                    "CRESMO_LLM__GEMINI__API_KEYS=nested-k1,nested-k2",
                    "CRESMO_LLM__GEMINI__THINKING_LEVEL=medium",
                    "CRESMO_LLM__OLLAMA__MODEL=deepseek-r1:14b",
                    "CRESMO_EMBEDDINGS__PROVIDER=tfidf",
                    "CRESMO_PIPELINE__BATCH_SIZE=8",
                    "CRESMO_PIPELINE__STAGES__EXPANSION_MAX_PASSES=9",
                    "CRESMO_PIPELINE__SATURATION__SEMANTIC_THRESHOLD=0.92",
                    "CRESMO_JUDGE__BENCHMARK_MODELS=gemini:gemini-3.5-flash-lite,ollama:qwen2.5:14b",
                    "CRESMO_JUDGE__BLOCKING=true",
                    "CRESMO_JUDGE__MAX_ATTEMPTS=4",
                    "CRESMO_INGESTION__WORKERS__WHISPER=2",
                    f"CRESMO_STORAGE__DATA_DIR={env_data_dir}",
                    f"CRESMO_STORAGE__VAULT_DIR={env_vault_dir}",
                    "CRESMO_OBSERVABILITY__RUNTIME__PIPELINE_VERSION=cresmo:v77-nested",
                    "CRESMO_OBSERVABILITY__RUNTIME__GIT_SHA=nestedsha123",
                    "CRESMO_OBSERVABILITY__LANGFUSE__HOST=https://nested.langfuse.local",
                    "CRESMO_OBSERVABILITY__LANGFUSE__ENVIRONMENT=qa-env_1",
                    "CRESMO_OBSERVABILITY__LOGGING__LEVEL=DEBUG",
                    "CRESMO_OBSERVABILITY__LOGGING__FORMAT=text",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        # Clear any ambient CRESMO_* overrides from shell
        for env_key in (
            "CRESMO_LLM__GEMINI__API_KEYS",
            "CRESMO_LLM__GEMINI__THINKING_LEVEL",
            "CRESMO_LLM__OLLAMA__MODEL",
            "CRESMO_EMBEDDINGS__PROVIDER",
            "CRESMO_PIPELINE__BATCH_SIZE",
            "CRESMO_PIPELINE__STAGES__EXPANSION_MAX_PASSES",
            "CRESMO_PIPELINE__SATURATION__SEMANTIC_THRESHOLD",
            "CRESMO_JUDGE__BENCHMARK_MODELS",
            "CRESMO_JUDGE__BLOCKING",
            "CRESMO_JUDGE__MAX_ATTEMPTS",
            "CRESMO_INGESTION__WORKERS__WHISPER",
            "CRESMO_STORAGE__DATA_DIR",
            "CRESMO_STORAGE__VAULT_DIR",
            "CRESMO_OBSERVABILITY__RUNTIME__PIPELINE_VERSION",
            "CRESMO_OBSERVABILITY__RUNTIME__GIT_SHA",
            "CRESMO_OBSERVABILITY__LANGFUSE__HOST",
            "CRESMO_OBSERVABILITY__LANGFUSE__ENVIRONMENT",
            "CRESMO_OBSERVABILITY__LOGGING__LEVEL",
            "CRESMO_OBSERVABILITY__LOGGING__FORMAT",
        ):
            monkeypatch.delenv(env_key, raising=False)

        settings = CresmoSettings(_env_file=custom_env)

        assert [k.get_secret_value() for k in settings.llm.gemini.api_keys] == [
            "nested-k1",
            "nested-k2",
        ]
        assert settings.llm.gemini.thinking_level == "medium"
        assert settings.llm.ollama.model == "deepseek-r1:14b"
        assert settings.embeddings.provider == "tfidf"
        assert settings.pipeline.batch_size == 8
        assert settings.pipeline.stages.expansion_max_passes == 9
        assert settings.pipeline.saturation.semantic_threshold == 0.92
        assert settings.judge.benchmark_models == (
            "gemini:gemini-3.5-flash-lite",
            "ollama:qwen2.5:14b",
        )
        assert settings.judge.blocking is True
        assert settings.judge.max_attempts == 4
        assert settings.ingestion.workers.whisper == 2
        assert settings.ingestion.workers.subtitle == 10
        assert settings.ingestion.workers.channel_discovery == 20
        assert settings.storage.data_dir == env_data_dir
        assert settings.storage.vault_dir == env_vault_dir
        assert settings.observability.runtime.pipeline_version == "cresmo:v77-nested"
        assert settings.observability.runtime.git_sha == "nestedsha123"
        assert settings.observability.langfuse.host == "https://nested.langfuse.local"
        assert settings.observability.langfuse.environment == "qa-env_1"
        assert settings.observability.logging.level == "DEBUG"
        assert settings.observability.logging.format == "text"

    def test_shared_settings_caching_reset_and_override(self) -> None:
        reset_shared_settings()
        try:
            first = get_shared_settings()
            second = get_shared_settings()
            assert first is second
            assert resolve_shared_settings() is first
            assert resolve_shared_settings(None) is first

            explicit = CresmoSettings(_env_file=None, pipeline=PipelineSettings(batch_size=42))
            assert resolve_shared_settings(explicit) is explicit

            reset_shared_settings()
            third = get_shared_settings()
            assert third is not first
        finally:
            reset_shared_settings()
