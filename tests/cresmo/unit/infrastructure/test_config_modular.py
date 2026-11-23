"""Hermetic unit tests for modular settings architecture and sub-domain configs."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

import cresmo.infrastructure.config as cresmo_config
from cresmo.application.ports.settings import PipelineSettingsProtocol
from cresmo.infrastructure.config import (
    CresmoSettings,
    IngestionSettings,
    JudgeSettings,
    LlmSettings,
    SaturationSettings,
    StorageSettings,
    TelemetrySettings,
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
    DEFAULT_LANGFUSE_PROMPT_LABEL as CATALOG_DEFAULT_LANGFUSE_PROMPT_LABEL,
)
from cresmo.infrastructure.config.catalog import (
    GEMINI_FREE_TIER_MODELS as CATALOG_GEMINI_FREE_TIER_MODELS,
)
from cresmo.infrastructure.config.catalog import (
    GEMINI_THINKING_LEVELS as CATALOG_GEMINI_THINKING_LEVELS,
)
from cresmo.infrastructure.config.ingestion import (
    IngestionSettings as DirectIngestionSettings,
)
from cresmo.infrastructure.config.judge import JudgeSettings as DirectJudgeSettings
from cresmo.infrastructure.config.llm import LlmSettings as DirectLlmSettings
from cresmo.infrastructure.config.saturation import (
    SaturationSettings as DirectSaturationSettings,
)
from cresmo.infrastructure.config.settings import (
    CresmoSettings as DirectCresmoSettings,
)
from cresmo.infrastructure.config.settings import (
    get_shared_settings as direct_get_shared_settings,
)
from cresmo.infrastructure.config.settings import (
    reset_shared_settings as direct_reset_shared_settings,
)
from cresmo.infrastructure.config.settings import (
    resolve_shared_settings as direct_resolve_shared_settings,
)
from cresmo.infrastructure.config.storage import StorageSettings as DirectStorageSettings
from cresmo.infrastructure.config.telemetry import TelemetrySettings as DirectTelemetrySettings


class TestModularExportsAndInheritance:
    """Validate re-exports, __all__ completeness, inheritance, and protocol compliance."""

    def test_reexports_match_direct_submodule_objects(self) -> None:
        assert LlmSettings is DirectLlmSettings
        assert TelemetrySettings is DirectTelemetrySettings
        assert StorageSettings is DirectStorageSettings
        assert IngestionSettings is DirectIngestionSettings
        assert SaturationSettings is DirectSaturationSettings
        assert JudgeSettings is DirectJudgeSettings
        assert CresmoSettings is DirectCresmoSettings
        assert get_shared_settings is direct_get_shared_settings
        assert reset_shared_settings is direct_reset_shared_settings
        assert resolve_shared_settings is direct_resolve_shared_settings

        assert cresmo_config.DEFAULT_GEMINI_MODEL == CATALOG_DEFAULT_GEMINI_MODEL
        assert cresmo_config.DEFAULT_BENCHMARK_MODELS == CATALOG_DEFAULT_BENCHMARK_MODELS
        assert cresmo_config.DEFAULT_JUDGE_PASS_THRESHOLD == CATALOG_DEFAULT_JUDGE_PASS_THRESHOLD
        assert cresmo_config.DEFAULT_LANGFUSE_PROMPT_LABEL == CATALOG_DEFAULT_LANGFUSE_PROMPT_LABEL
        assert cresmo_config.GEMINI_FREE_TIER_MODELS == CATALOG_GEMINI_FREE_TIER_MODELS
        assert cresmo_config.GEMINI_THINKING_LEVELS == CATALOG_GEMINI_THINKING_LEVELS

    def test_cresmo_settings_inherits_all_six_sub_settings_and_satisfies_protocol(self) -> None:
        for base_cls in (
            LlmSettings,
            TelemetrySettings,
            StorageSettings,
            IngestionSettings,
            SaturationSettings,
            JudgeSettings,
        ):
            assert issubclass(CresmoSettings, base_cls)

        settings = CresmoSettings(_env_file=None)
        assert isinstance(settings, PipelineSettingsProtocol)

    def test_config_dunder_all_preserves_original_and_adds_sub_settings(self) -> None:
        expected_symbols = {
            "DEFAULT_BENCHMARK_MODELS",
            "DEFAULT_GEMINI_FALLBACK_MODEL",
            "DEFAULT_GEMINI_MAX_OUTPUT_TOKENS",
            "DEFAULT_GEMINI_MODEL",
            "DEFAULT_GEMINI_THINKING_LEVEL",
            "DEFAULT_GEMINI_TIMEOUT_SECONDS",
            "DEFAULT_GENERATOR_BENCHMARK_MODELS",
            "DEFAULT_JUDGE_CALIBRATION_MODELS",
            "DEFAULT_JUDGE_GEMINI_MODEL",
            "DEFAULT_JUDGE_PASS_THRESHOLD",
            "DEFAULT_LANGFUSE_PROMPT_LABEL",
            "GEMINI_FREE_TIER_MODELS",
            "GEMINI_THINKING_LEVELS",
            "CresmoSettings",
            "GeminiFreeTierModel",
            "GeminiThinkingLevel",
            "get_shared_settings",
            "reset_shared_settings",
            "resolve_default_pipeline_version",
            "resolve_shared_settings",
            "LlmSettings",
            "TelemetrySettings",
            "StorageSettings",
            "IngestionSettings",
            "SaturationSettings",
            "JudgeSettings",
        }
        exported = set(cresmo_config.__all__)
        assert expected_symbols.issubset(exported)
        for symbol in expected_symbols:
            assert hasattr(cresmo_config, symbol)


class TestLlmSettings:
    """Validate standalone LlmSettings defaults, credentials, normalization, and bounds."""

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in ("GEMINI_API_KEY", "GEMINI_API_KEYS", "GEMINI_THINKING_LEVEL"):
            monkeypatch.delenv(var, raising=False)

        llm = LlmSettings(_env_file=None)

        assert llm.gemini_api_keys == []
        assert llm.gemini_api_key == SecretStr("")
        assert llm.gemini_model == "gemini-3.5-flash-lite"
        assert llm.gemini_fallback_model == "gemini-3.6-flash"
        assert llm.gemini_thinking_level == "low"
        assert llm.gemini_max_output_tokens == 32_768
        assert llm.gemini_timeout_seconds == 300.0
        assert llm.ollama_base_url == "http://localhost:11434"
        assert llm.ollama_model == "qwen2.5:7b"
        assert llm.ollama_timeout_seconds == 300.0
        assert llm.ollama_warmup_timeout_seconds == 300.0
        assert llm.ollama_keep_alive == "1h"
        assert llm.ollama_num_predict == 0
        assert llm.indexing_provider == "ollama"
        assert llm.language == "Português do Brasil"
        assert llm.llm_synthesis_temperature == 0.2
        assert llm.llm_indexing_temperature == 0.2

    def test_single_gemini_api_key_kwarg_and_property(self) -> None:
        llm = LlmSettings(_env_file=None, gemini_api_key="single-secret-key")

        assert [k.get_secret_value() for k in llm.gemini_api_keys] == ["single-secret-key"]
        assert llm.gemini_api_key.get_secret_value() == "single-secret-key"

    def test_comma_separated_gemini_api_keys_string_and_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        llm_kw = LlmSettings(_env_file=None, gemini_api_keys="key-one, key-two , , key-three")
        assert [k.get_secret_value() for k in llm_kw.gemini_api_keys] == [
            "key-one",
            "key-two",
            "key-three",
        ]
        assert llm_kw.gemini_api_key.get_secret_value() == "key-one"

        monkeypatch.setenv("GEMINI_API_KEYS", "env-k1, env-k2")
        llm_env = LlmSettings(_env_file=None)
        assert [k.get_secret_value() for k in llm_env.gemini_api_keys] == ["env-k1", "env-k2"]

    def test_gemini_thinking_level_normalization_and_validation_error(self) -> None:
        normalized = LlmSettings(_env_file=None, gemini_thinking_level=" HIGH ")
        assert normalized.gemini_thinking_level == "high"

        with pytest.raises(ValidationError):
            LlmSettings.model_validate({"gemini_thinking_level": "ultra"})

    def test_temperature_bounds(self) -> None:
        low = LlmSettings(
            _env_file=None,
            llm_synthesis_temperature=0.0,
            llm_indexing_temperature=0.0,
        )
        high = LlmSettings(
            _env_file=None,
            llm_synthesis_temperature=2.0,
            llm_indexing_temperature=2.0,
        )
        assert low.llm_synthesis_temperature == 0.0
        assert high.llm_indexing_temperature == 2.0

        for invalid in (
            {"llm_synthesis_temperature": -0.1},
            {"llm_synthesis_temperature": 2.1},
            {"llm_indexing_temperature": -0.1},
            {"llm_indexing_temperature": 2.1},
        ):
            with pytest.raises(ValidationError):
                LlmSettings.model_validate(invalid)


class TestTelemetrySettings:
    """Validate standalone TelemetrySettings defaults, aliases, and env overrides."""

    def test_defaults_and_pipeline_version_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in (
            "CRESMO_PIPELINE_VERSION",
            "PIPELINE_VERSION",
            "GIT_SHA",
            "CRESMO_GIT_SHA",
            "LANGFUSE_BASE_URL",
            "LANGFUSE_HOST",
            "LANGFUSE_TRACING_ENVIRONMENT",
            "LANGFUSE_ENVIRONMENT",
            "LOG_LEVEL",
            "CRESMO_LOG_LEVEL",
            "LOG_FORMAT",
            "CRESMO_LOG_FORMAT",
        ):
            monkeypatch.delenv(var, raising=False)

        telemetry = TelemetrySettings(_env_file=None)
        assert telemetry.pipeline_version.startswith("cresmo:v")
        assert telemetry.git_sha is None
        assert telemetry.langfuse_host == "https://cloud.langfuse.com"
        assert telemetry.langfuse_environment == "staging"
        assert telemetry.langfuse_prompt_label == "production"
        assert telemetry.langfuse_timeout_seconds == 30
        assert telemetry.anonymization_enabled is True
        assert telemetry.preflight_probe_timeout_seconds == 2.0
        assert telemetry.enable_preflight_probes is True
        assert telemetry.prometheus_enabled is True
        assert telemetry.prometheus_port == 9090
        assert telemetry.log_level == "WARNING"
        assert telemetry.log_format == "json"

        kwarg_override = TelemetrySettings(_env_file=None, pipeline_version="cresmo:v9-kw")
        assert kwarg_override.pipeline_version == "cresmo:v9-kw"

        monkeypatch.setenv("CRESMO_PIPELINE_VERSION", "cresmo:v4-canary")
        env_override = TelemetrySettings(_env_file=None)
        assert env_override.pipeline_version == "cresmo:v4-canary"

    def test_langfuse_environment_aliases_normalization_and_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from pydantic import ValidationError

        from cresmo.infrastructure.config import (
            DEFAULT_LANGFUSE_ENVIRONMENT,
            LANGFUSE_ENVIRONMENT_PATTERN,
        )

        assert DEFAULT_LANGFUSE_ENVIRONMENT == "staging"
        assert LANGFUSE_ENVIRONMENT_PATTERN == r"^(?!langfuse)[a-z0-9-_]{1,40}$"
        assert CresmoSettings.DEFAULT_LANGFUSE_ENVIRONMENT == "staging"

        monkeypatch.delenv("LANGFUSE_TRACING_ENVIRONMENT", raising=False)
        monkeypatch.delenv("LANGFUSE_ENVIRONMENT", raising=False)

        # Fallback alias LANGFUSE_ENVIRONMENT
        monkeypatch.setenv("LANGFUSE_ENVIRONMENT", "  Production ")
        assert TelemetrySettings(_env_file=None).langfuse_environment == "production"

        # Canonical Langfuse SDK env var takes precedence over LANGFUSE_ENVIRONMENT
        monkeypatch.setenv("LANGFUSE_TRACING_ENVIRONMENT", "QA-Env_2")
        assert TelemetrySettings(_env_file=None).langfuse_environment == "qa-env_2"

        # Exact 40-char boundary is valid
        valid_40 = "a" * 40
        assert (
            TelemetrySettings(_env_file=None, langfuse_environment=valid_40).langfuse_environment
            == valid_40
        )

        # Invalid values fail fast
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
                TelemetrySettings(_env_file=None, langfuse_environment=invalid)

    def test_git_sha_langfuse_base_url_and_logging_overrides(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("LANGFUSE_HOST", raising=False)
        monkeypatch.setenv("GIT_SHA", "deadbeef99")
        monkeypatch.setenv("LANGFUSE_BASE_URL", "https://langfuse.internal")
        monkeypatch.setenv("CRESMO_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_FORMAT", "text")

        telemetry = TelemetrySettings(_env_file=None)

        assert telemetry.git_sha == "deadbeef99"
        assert telemetry.langfuse_host == "https://langfuse.internal"
        assert telemetry.log_level == "DEBUG"
        assert telemetry.log_format == "text"


class TestStorageSettings:
    """Validate standalone StorageSettings derived paths and defaults."""

    def test_derived_property_paths_and_cookies_default_none(self, tmp_path: Path) -> None:
        defaults = StorageSettings(_env_file=None)
        assert defaults.data_dir.name == "data"
        assert defaults.vault_dir.name == "vault"
        assert defaults.cookies_file is None

        data_dir = tmp_path / "lake"
        vault_dir = tmp_path / "obsidian"
        storage = StorageSettings(_env_file=None, data_dir=data_dir, vault_dir=vault_dir)

        assert storage.data_dir == data_dir
        assert storage.vault_dir == vault_dir
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
        assert storage.cookies_file is None


class TestIngestionSettings:
    """Validate IngestionSettings worker multiples, bounds, and pure validation."""

    def test_computed_worker_multiples_and_explicit_overrides(self) -> None:
        default_workers = IngestionSettings(_env_file=None)
        assert default_workers.whisper_workers == 1
        assert default_workers.subtitle_workers == 5
        assert default_workers.channel_discovery_workers == 10

        scaled = IngestionSettings(_env_file=None, whisper_workers=3)
        assert scaled.subtitle_workers == 15
        assert scaled.channel_discovery_workers == 30

        explicit = IngestionSettings(
            _env_file=None,
            whisper_workers=3,
            subtitle_workers=7,
            channel_discovery_workers=11,
        )
        assert explicit.subtitle_workers == 7
        assert explicit.channel_discovery_workers == 11

    def test_expansion_and_long_expander_max_passes_bounds(self) -> None:
        low = IngestionSettings(_env_file=None, expansion_max_passes=1, long_expander_max_passes=1)
        high = IngestionSettings(
            _env_file=None, expansion_max_passes=10, long_expander_max_passes=10
        )
        assert low.expansion_max_passes == 1
        assert low.long_expander_max_passes == 1
        assert high.expansion_max_passes == 10
        assert high.long_expander_max_passes == 10
        assert IngestionSettings(_env_file=None).long_expander_max_passes == 7

        for bad_passes in (0, 11):
            with pytest.raises(ValidationError):
                IngestionSettings.model_validate({"expansion_max_passes": bad_passes})
            with pytest.raises(ValidationError):
                IngestionSettings.model_validate({"long_expander_max_passes": bad_passes})

    def test_discovery_queue_maxsize_lower_bound(self) -> None:
        valid = IngestionSettings(_env_file=None, discovery_queue_maxsize=1)
        assert valid.discovery_queue_maxsize == 1

        with pytest.raises(ValidationError):
            IngestionSettings.model_validate({"discovery_queue_maxsize": 0})

    def test_pure_validation_does_not_mutate_cookies_file_from_disk(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("DEFAULT_COOKIES_FILE", raising=False)
        monkeypatch.delenv("CRESMO_COOKIES_FILE", raising=False)

        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "cookies.txt").write_text("# Netscape cookie\n", encoding="utf-8")
        (tmp_path / ".yt_dlp_cookies.txt").write_text("# Netscape cookie\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        settings = CresmoSettings(data_dir=data_dir, _env_file=None)

        assert settings.cookies_file is None


class TestSaturationSettings:
    """Validate ADR-066 SaturationSettings defaults, normalization, and window invariant."""

    def test_adr_066_defaults(self) -> None:
        sat = SaturationSettings(_env_file=None)

        assert sat.embedding_provider == "gemini"
        assert sat.gemini_embedding_model == "gemini-embedding-001"
        assert sat.gemini_embedding_dimensions == 768
        assert sat.ollama_embedding_model == "nomic-embed-text"
        assert sat.saturation_lexical_threshold == 0.95
        assert sat.saturation_max_word_delta == 0.03
        assert sat.saturation_semantic_threshold == 0.88
        assert sat.saturation_max_novel_paragraphs == 0
        assert sat.saturation_long_unit_word_cutoff == 120
        assert sat.saturation_sliding_window_sentences == 3
        assert sat.saturation_sliding_window_overlap == 1

    def test_embedding_provider_normalization_and_validation(self) -> None:
        ollama = SaturationSettings(_env_file=None, embedding_provider=" OLLAMA ")
        tfidf = SaturationSettings(_env_file=None, embedding_provider=" TfIdF ")
        assert ollama.embedding_provider == "ollama"
        assert tfidf.embedding_provider == "tfidf"

        with pytest.raises(ValidationError):
            SaturationSettings.model_validate({"embedding_provider": "unknown"})

    def test_threshold_bounds_and_sliding_window_validator(self) -> None:
        valid_boundary = SaturationSettings(
            _env_file=None,
            saturation_lexical_threshold=1.0,
            saturation_max_word_delta=0.0,
            saturation_semantic_threshold=1.0,
            saturation_sliding_window_sentences=3,
            saturation_sliding_window_overlap=2,
        )
        assert valid_boundary.saturation_sliding_window_overlap == 2

        invalid_cases: list[dict[str, object]] = [
            {"gemini_embedding_dimensions": 0},
            {"saturation_lexical_threshold": 0.0},
            {"saturation_lexical_threshold": 1.01},
            {"saturation_max_word_delta": -0.01},
            {"saturation_max_word_delta": 1.01},
            {"saturation_semantic_threshold": 0.0},
            {"saturation_semantic_threshold": 1.01},
            {"saturation_max_novel_paragraphs": -1},
            {"saturation_long_unit_word_cutoff": 0},
            {"saturation_sliding_window_sentences": 0},
            {"saturation_sliding_window_overlap": -1},
            {"saturation_sliding_window_sentences": 3, "saturation_sliding_window_overlap": 3},
            {"saturation_sliding_window_sentences": 2, "saturation_sliding_window_overlap": 4},
        ]
        for payload in invalid_cases:
            with pytest.raises(ValidationError):
                SaturationSettings.model_validate(payload)


class TestJudgeSettings:
    """Validate standalone JudgeSettings defaults, aliases, weights, and thinking level."""

    def test_defaults_and_max_retries_alias(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in ("CRESMO_MAX_RETRIES", "CRESMO_JUDGE_MAX_ATTEMPTS", "BENCHMARK_MODELS"):
            monkeypatch.delenv(var, raising=False)

        judge = JudgeSettings(_env_file=None)
        assert judge.typesafe_model == "jev-latest"
        assert judge.typesafe_base_url == "https://api.typesafe.ai/v1"
        assert judge.judge_provider == "gemini"
        assert judge.judge_fallback_provider == "ollama"
        assert judge.judge_blocking is False
        assert judge.judge_max_attempts == 2
        assert judge.max_retries == 2
        assert judge.judge_pass_threshold == 0.9
        assert judge.gap_filler_judge_threshold == 0.9
        assert judge.judge_gemini_model == "gemini-3.5-flash-lite"
        assert judge.judge_gemini_thinking_level == "low"

        monkeypatch.setenv("CRESMO_MAX_RETRIES", "5")
        overridden = JudgeSettings(_env_file=None)
        assert overridden.judge_max_attempts == 5
        assert overridden.max_retries == 5

        with pytest.raises(ValidationError):
            JudgeSettings.model_validate({"judge_max_attempts": 0})

    def test_judge_gemini_thinking_level_normalization_and_rejection(self) -> None:
        normalized = JudgeSettings(_env_file=None, judge_gemini_thinking_level=" XHIGH ")
        assert normalized.judge_gemini_thinking_level == "xhigh"

        with pytest.raises(ValidationError):
            JudgeSettings.model_validate({"judge_gemini_thinking_level": "invalid"})

    def test_benchmark_models_aliases_and_gap_filler_weights(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        defaults = JudgeSettings(_env_file=None)
        assert defaults.benchmark_models == [
            "gemini:gemini-3.5-flash-lite",
            "gemini:gemini-3.8-flash",
            "gemini:gemini-4-hydrogen",
        ]
        assert defaults.judge_calibration_models == defaults.benchmark_models
        assert defaults.generator_benchmark_models == defaults.benchmark_models

        expected_weight_keys = {
            "epistemic_grounding_segregation",
            "conceptual_mechanical_decomposition",
            "braudelian_stratification",
            "genealogy_hidden_agency",
            "competing_hypotheses",
            "extra_info_granularity",
            "linear_style_naturalism",
        }
        assert set(defaults.gap_filler_judge_weights.keys()) == expected_weight_keys
        assert sum(defaults.gap_filler_judge_weights.values()) == pytest.approx(1.0)

        monkeypatch.setenv(
            "BENCHMARK_MODELS",
            "gemini:gemini-3.5-flash-lite, ollama:qwen2.5:14b",
        )
        env_judge = JudgeSettings(_env_file=None)
        assert env_judge.benchmark_models == [
            "gemini:gemini-3.5-flash-lite",
            "ollama:qwen2.5:14b",
        ]
        assert env_judge.judge_calibration_models == env_judge.benchmark_models
        assert env_judge.generator_benchmark_models == env_judge.benchmark_models


class TestFlatEnvLoadingAndSharedResolution:
    """Validate flat .env loading across all six sub-domains and singleton helpers."""

    def test_flat_env_loads_all_six_sub_domains(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env_vars_to_clear = (
            "GEMINI_API_KEYS",
            "GEMINI_API_KEY",
            "CRESMO_OLLAMA_MODEL",
            "GEMINI_THINKING_LEVEL",
            "CRESMO_PIPELINE_VERSION",
            "LANGFUSE_HOST",
            "LANGFUSE_BASE_URL",
            "GIT_SHA",
            "DATA_DIR",
            "VAULT_DIR",
            "WHISPER_WORKERS",
            "CRESMO_EXPANSION_MAX_PASSES",
            "CRESMO_EMBEDDING_PROVIDER",
            "CRESMO_SATURATION_SEMANTIC_THRESHOLD",
            "BENCHMARK_MODELS",
            "CRESMO_JUDGE_BLOCKING",
            "CRESMO_JUDGE_MAX_ATTEMPTS",
        )
        for var in env_vars_to_clear:
            monkeypatch.delenv(var, raising=False)

        env_data_dir = tmp_path / "env_data"
        env_vault_dir = tmp_path / "env_vault"
        custom_env = tmp_path / "flat.env"
        custom_env.write_text(
            "\n".join(
                [
                    "GEMINI_API_KEYS=flat-k1,flat-k2",
                    "CRESMO_OLLAMA_MODEL=deepseek-r1:14b",
                    "GEMINI_THINKING_LEVEL=medium",
                    "CRESMO_PIPELINE_VERSION=cresmo:v77-flat",
                    "LANGFUSE_BASE_URL=https://flat.langfuse.local",
                    "GIT_SHA=flatsha123",
                    f"DATA_DIR={env_data_dir}",
                    f"VAULT_DIR={env_vault_dir}",
                    "WHISPER_WORKERS=2",
                    "CRESMO_EXPANSION_MAX_PASSES=8",
                    "CRESMO_EMBEDDING_PROVIDER=tfidf",
                    "CRESMO_SATURATION_SEMANTIC_THRESHOLD=0.92",
                    "BENCHMARK_MODELS=gemini:gemini-3.5-flash-lite,ollama:qwen2.5:14b",
                    "CRESMO_JUDGE_BLOCKING=true",
                    "CRESMO_JUDGE_MAX_ATTEMPTS=4",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        settings = CresmoSettings(_env_file=custom_env)

        # LLM
        assert [k.get_secret_value() for k in settings.gemini_api_keys] == ["flat-k1", "flat-k2"]
        assert settings.ollama_model == "deepseek-r1:14b"
        assert settings.gemini_thinking_level == "medium"
        # Telemetry
        assert settings.pipeline_version == "cresmo:v77-flat"
        assert settings.langfuse_host == "https://flat.langfuse.local"
        assert settings.git_sha == "flatsha123"
        # Storage
        assert settings.data_dir == env_data_dir
        assert settings.vault_dir == env_vault_dir
        assert settings.raw_dir == env_data_dir / "raw"
        # Ingestion
        assert settings.whisper_workers == 2
        assert settings.subtitle_workers == 10
        assert settings.channel_discovery_workers == 20
        assert settings.expansion_max_passes == 8
        # Saturation
        assert settings.embedding_provider == "tfidf"
        assert settings.saturation_semantic_threshold == 0.92
        # Judge
        assert settings.benchmark_models == [
            "gemini:gemini-3.5-flash-lite",
            "ollama:qwen2.5:14b",
        ]
        assert settings.judge_blocking is True
        assert settings.judge_max_attempts == 4
        assert settings.max_retries == 4

    def test_shared_settings_caching_reset_and_override(self) -> None:
        reset_shared_settings()
        try:
            first = get_shared_settings()
            second = get_shared_settings()
            assert first is second
            assert resolve_shared_settings() is first
            assert resolve_shared_settings(None) is first

            explicit = CresmoSettings(_env_file=None, batch_size=42)
            assert resolve_shared_settings(explicit) is explicit

            reset_shared_settings()
            third = get_shared_settings()
            assert third is not first
        finally:
            reset_shared_settings()
