"""Hermetic unit tests for CresmoSettings and Anchor Marker resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.paths import find_workspace_root


class TestAnchorMarkerResolution:
    """Validate resilient Anchor Marker workspace root discovery."""

    def test_find_workspace_root_discovers_pyproject_toml(self) -> None:
        root = find_workspace_root()
        assert (root / "pyproject.toml").exists()
        assert root.is_dir()

    def test_find_workspace_root_from_nested_directory(self) -> None:
        nested_path = Path(__file__).resolve()
        root = find_workspace_root(nested_path)
        assert (root / "pyproject.toml").exists()

    def test_find_workspace_root_with_simulated_synthetic_anchor(self, tmp_path: Path) -> None:
        repo_dir = tmp_path / "synthetic_repo"
        sub_dir = repo_dir / "a" / "b" / "c" / "d" / "e"
        sub_dir.mkdir(parents=True)
        (repo_dir / "pyproject.toml").touch()

        discovered = find_workspace_root(sub_dir)
        assert discovered == repo_dir

    def test_find_workspace_root_fallback_when_no_anchor(self, tmp_path: Path) -> None:
        leaf_dir = tmp_path / "l1" / "l2" / "l3" / "l4"
        leaf_dir.mkdir(parents=True)
        # Without any pyproject.toml or .git, falls back to parents[3]
        fallback = find_workspace_root(leaf_dir)
        assert fallback == leaf_dir.resolve().parents[3]


class TestCresmoSettings:
    """Validate settings defaults and derived property invariants."""

    def test_default_paths_anchor_to_workspace(self) -> None:
        settings = CresmoSettings(_env_file=None)
        assert settings.data_dir.name == "data"
        assert settings.vault_dir.name == "vault"
        assert settings.raw_dir == settings.data_dir / "raw"
        assert settings.enriched_dir == settings.data_dir / "enriched"
        assert settings.master_dir == settings.data_dir / "master"
        assert settings.index_path == settings.vault_dir / "_index.json"
        assert settings.sqlite_ledger_path == settings.data_dir / "cresmo_ledger.db"
        assert settings.browser_cookies == "firefox"
        assert settings.auto_extract_cookies is True
        assert settings.enable_channel_crawler is False
        assert settings.require_auth_cookies is False
        assert settings.concat_max_words == 500_000
        assert settings.brain_csv_path == settings.data_dir / "brain.csv"
        assert settings.prometheus_enabled is True
        assert settings.prometheus_port == 9090
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "qwen2.5:7b"
        assert settings.indexing_provider == "ollama"
        assert settings.ollama_num_predict == 0
        assert settings.raw_index_max_chars == 0
        assert settings.language == "Português do Brasil"
        assert not hasattr(settings, "default_language")
        assert not hasattr(settings, "llm_temperature")
        assert not hasattr(settings, "raw_index_temperature")
        assert settings.llm_synthesis_temperature == 0.2
        assert settings.llm_indexing_temperature == 0.2
        assert settings.expansion_max_passes == 5
        assert settings.judge_max_attempts == 2
        assert settings.raw_index_max_attempts == 2
        assert settings.inventory_max_attempts == 2
        assert settings.max_retries == 2

    def test_max_retries_alias_and_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = CresmoSettings()
        assert settings.max_retries == 2
        assert settings.judge_max_attempts == 2

        monkeypatch.setenv("CRESMO_MAX_RETRIES", "4")
        overridden = CresmoSettings()
        assert overridden.max_retries == 4
        assert overridden.judge_max_attempts == 4

    def test_ollama_num_predict_defaults_and_env_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = CresmoSettings(_env_file=None)
        assert settings.ollama_num_predict == 0

        monkeypatch.setenv("CRESMO_OLLAMA_NUM_PREDICT", "450")
        overridden = CresmoSettings(_env_file=None)
        assert overridden.ollama_num_predict == 450

    def test_temperature_validation_bounds(self) -> None:
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CresmoSettings(llm_synthesis_temperature=-0.1)

        with pytest.raises(ValidationError):
            CresmoSettings(llm_synthesis_temperature=2.1)

        with pytest.raises(ValidationError):
            CresmoSettings(llm_indexing_temperature=-0.5)

        with pytest.raises(ValidationError):
            CresmoSettings.model_validate({"llm_synthesis_temperature": -0.1})

        with pytest.raises(ValidationError):
            CresmoSettings.model_validate({"llm_indexing_temperature": -0.5})

    def test_ensure_directories_creates_all_dirs_and_is_idempotent(self, tmp_path: Path) -> None:
        settings = CresmoSettings(
            data_dir=tmp_path / "nested" / "data",
            vault_dir=tmp_path / "nested" / "vault",
        )
        assert not (tmp_path / "nested").exists()
        settings.ensure_directories()

        for d in (
            settings.data_dir,
            settings.vault_dir,
            settings.mocs_dir,
            settings.raw_dir,
            settings.fluid_dir,
            settings.gap_filler_dir,
            settings.enriched_dir,
            settings.master_dir,
            settings.priority_texts_dir,
        ):
            assert d.exists()
            assert d.is_dir()

        assert settings.fluid_dir == settings.data_dir / "fluid_prose"
        assert settings.gap_filler_dir == settings.data_dir / "gap_filler"

        # Idempotent second run verifies exist_ok=True
        settings.ensure_directories()

    def test_git_sha_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = CresmoSettings(_env_file=None)
        assert settings.git_sha is None
        monkeypatch.setenv("GIT_SHA", "abcdef123456")
        overridden = CresmoSettings(_env_file=None)
        assert overridden.git_sha == "abcdef123456"

    def test_discovery_queue_maxsize_defaults_and_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from pydantic import ValidationError

        settings = CresmoSettings()
        assert settings.discovery_queue_maxsize == 50

        monkeypatch.setenv("DISCOVERY_QUEUE_MAXSIZE", "120")
        overridden = CresmoSettings()
        assert overridden.discovery_queue_maxsize == 120

        with pytest.raises(ValidationError):
            CresmoSettings.model_validate({"discovery_queue_maxsize": 0})

    def test_pipeline_version_default_and_env_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify pipeline_version resolves dynamically and unifies env override on CRESMO_PIPELINE_VERSION (ADR-026, ADR-063)."""
        import importlib.metadata
        from unittest.mock import patch

        from cresmo.infrastructure.config import resolve_default_pipeline_version

        expected_version = f"cresmo:v{importlib.metadata.version('pes')}"
        assert resolve_default_pipeline_version() == expected_version
        assert expected_version != "cresmo:v2"

        settings = CresmoSettings()
        assert settings.pipeline_version == expected_version

        with patch(
            "importlib.metadata.version",
            side_effect=importlib.metadata.PackageNotFoundError("pes"),
        ):
            assert resolve_default_pipeline_version() == "cresmo:v0.0.0-dev"

        # Python kwarg construction works via field name
        explicit = CresmoSettings(pipeline_version="cresmo:v9-kwarg")
        assert explicit.pipeline_version == "cresmo:v9-kwarg"

        # Legacy unprefixed PIPELINE_VERSION is ignored (unified on CRESMO_PIPELINE_VERSION)
        monkeypatch.setenv("PIPELINE_VERSION", "cresmo:v-legacy-ignored")
        assert CresmoSettings().pipeline_version == expected_version

        # Canonical Bounded Context env var overrides default
        monkeypatch.setenv("CRESMO_PIPELINE_VERSION", "cresmo:v3-canary")
        overridden = CresmoSettings()
        assert overridden.pipeline_version == "cresmo:v3-canary"

    def test_cresmo_settings_custom_env_file_override(self, tmp_path: Path) -> None:
        """Verify _env_file argument explicitly overrides environment file."""
        custom_env = tmp_path / "custom.env"
        custom_env.write_text("CRESMO_OLLAMA_MODEL=deepseek-r1:14b\n", encoding="utf-8")
        settings = CresmoSettings(_env_file=custom_env)
        assert settings.ollama_model == "deepseek-r1:14b"

    def test_calibration_and_benchmark_models_defaults_and_env_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify calibration and benchmark models defaults and safe comma-separated env parsing."""
        from cresmo.infrastructure.config import (
            DEFAULT_GEMINI_MODEL,
            DEFAULT_JUDGE_GEMINI_MODEL,
        )

        settings = CresmoSettings()
        assert settings.gemini_model == DEFAULT_GEMINI_MODEL
        assert settings.judge_gemini_model == DEFAULT_JUDGE_GEMINI_MODEL
        assert settings.benchmark_models == [
            "gemini:gemini-3.5-flash-lite",
            "gemini:gemini-3.8-flash",
            "gemini:gemini-4-hydrogen",
        ]
        assert settings.judge_calibration_models == settings.benchmark_models
        assert settings.generator_benchmark_models == settings.benchmark_models

        monkeypatch.setenv(
            "BENCHMARK_MODELS",
            "gemini:gemini-3.5-flash-lite, ollama:qwen2.5:14b",
        )
        overridden = CresmoSettings()
        assert overridden.benchmark_models == [
            "gemini:gemini-3.5-flash-lite",
            "ollama:qwen2.5:14b",
        ]
        assert overridden.judge_calibration_models == overridden.benchmark_models
        assert overridden.generator_benchmark_models == overridden.benchmark_models

    def test_gemini_timeout_seconds_defaults_and_env_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify gemini_timeout_seconds defaults to 300.0 and supports env override."""
        settings = CresmoSettings(_env_file=None)
        assert settings.gemini_timeout_seconds == 300.0

        monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "45.0")
        overridden = CresmoSettings(_env_file=None)
        assert overridden.gemini_timeout_seconds == 45.0

    def test_default_gemini_model_has_no_provider_prefix(self) -> None:
        """Verify DEFAULT_GEMINI_MODEL and settings defaults omit the 'gemini:' prefix."""
        from cresmo.infrastructure.config import DEFAULT_GEMINI_MODEL

        settings = CresmoSettings(_env_file=None)
        assert DEFAULT_GEMINI_MODEL == "gemini-3.5-flash-lite"
        assert settings.gemini_model == "gemini-3.5-flash-lite"
        assert settings.gemini_fallback_model == "gemini-3.6-flash"
        assert settings.gemini_fallback_model != settings.gemini_model
        assert settings.judge_gemini_model == "gemini-3.5-flash-lite"
        assert not settings.gemini_model.startswith("gemini:")

    def test_free_tier_models_catalog_exported_from_root_and_cresmo_config(self) -> None:
        """Verify GEMINI_FREE_TIER_MODELS exposes all 11 Free-Tier models and excludes paid-only models."""
        import config as root_config
        from cresmo.infrastructure.config import GEMINI_FREE_TIER_MODELS

        expected_free_tier = (
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.6-flash",
            "gemini-4-hydrogen",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemma-4-31b-it",
            "gemma-4-26b-a4b-it",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        )
        assert GEMINI_FREE_TIER_MODELS == expected_free_tier
        assert root_config.GEMINI_FREE_TIER_MODELS == GEMINI_FREE_TIER_MODELS
        assert hasattr(root_config, "GeminiFreeTierModel")
        assert hasattr(root_config, "GeminiThinkingLevel")
        assert hasattr(root_config, "GEMINI_THINKING_LEVELS")

        for paid_only in (
            "gemini-4-carbon",
            "gemini-4-argon",
            "gemini-4-neon",
            "gemini-3.1-pro-preview",
        ):
            assert paid_only not in GEMINI_FREE_TIER_MODELS

    def test_gemini_thinking_level_defaults_normalization_and_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify gemini_thinking_level and judge_gemini_thinking_level defaults, normalization, and validation."""
        from pydantic import ValidationError

        from cresmo.infrastructure.config import DEFAULT_GEMINI_THINKING_LEVEL

        settings = CresmoSettings(_env_file=None)
        assert DEFAULT_GEMINI_THINKING_LEVEL == "low"
        assert settings.gemini_thinking_level == "low"
        assert settings.judge_gemini_thinking_level == "low"

        monkeypatch.setenv("GEMINI_THINKING_LEVEL", " HIGH ")
        monkeypatch.setenv("JUDGE_GEMINI_THINKING_LEVEL", " Minimal ")
        overridden = CresmoSettings(_env_file=None)
        assert overridden.gemini_thinking_level == "high"
        assert overridden.judge_gemini_thinking_level == "minimal"

        monkeypatch.setenv("CRESMO_GEMINI_THINKING_LEVEL", "medium")
        monkeypatch.setenv("CRESMO_JUDGE_GEMINI_THINKING_LEVEL", "xhigh")
        prefixed = CresmoSettings(_env_file=None)
        assert prefixed.gemini_thinking_level == "medium"
        assert prefixed.judge_gemini_thinking_level == "xhigh"

        with pytest.raises(ValidationError):
            CresmoSettings(_env_file=None, gemini_thinking_level="ultra")  # type: ignore[arg-type]

        with pytest.raises(ValidationError):
            CresmoSettings(_env_file=None, judge_gemini_thinking_level="invalid")  # type: ignore[arg-type]

    def test_gemini_max_output_tokens_defaults_override_and_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify gemini_max_output_tokens defaults to 32768, supports env override, and enforces bounds."""
        from pydantic import ValidationError

        from cresmo.infrastructure.config import DEFAULT_GEMINI_MAX_OUTPUT_TOKENS

        settings = CresmoSettings(_env_file=None)
        assert DEFAULT_GEMINI_MAX_OUTPUT_TOKENS == 32_768
        assert settings.gemini_max_output_tokens == 32_768

        monkeypatch.setenv("GEMINI_MAX_OUTPUT_TOKENS", "16384")
        overridden = CresmoSettings(_env_file=None)
        assert overridden.gemini_max_output_tokens == 16_384

        with pytest.raises(ValidationError):
            CresmoSettings(_env_file=None, gemini_max_output_tokens=128)

    def test_deprecated_judge_temperature_removed(self) -> None:
        """Verify deprecated Gemini sampling tunable judge_temperature is removed from settings."""
        settings = CresmoSettings(_env_file=None)
        assert not hasattr(settings, "judge_temperature")

    def test_embedding_and_saturation_settings_defaults_env_overrides_and_bounds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify embedding and hybrid saturation defaults, CRESMO_* overrides, and Pydantic bounds."""
        from pydantic import ValidationError

        settings = CresmoSettings(_env_file=None)
        assert settings.embedding_provider == "gemini"
        assert settings.gemini_embedding_model == "gemini-embedding-001"
        assert settings.gemini_embedding_dimensions == 768
        assert settings.ollama_embedding_model == "nomic-embed-text"
        assert settings.saturation_lexical_threshold == 0.95
        assert settings.saturation_max_word_delta == 0.03
        assert settings.saturation_semantic_threshold == 0.88
        assert settings.saturation_max_novel_paragraphs == 0
        assert settings.saturation_long_unit_word_cutoff == 120
        assert settings.saturation_sliding_window_sentences == 3
        assert settings.saturation_sliding_window_overlap == 1

        monkeypatch.setenv("CRESMO_EMBEDDING_PROVIDER", "ollama")
        monkeypatch.setenv("CRESMO_GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        monkeypatch.setenv("CRESMO_GEMINI_EMBEDDING_DIMENSIONS", "256")
        monkeypatch.setenv("CRESMO_OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
        monkeypatch.setenv("CRESMO_SATURATION_LEXICAL_THRESHOLD", "0.90")
        monkeypatch.setenv("CRESMO_SATURATION_MAX_WORD_DELTA", "0.05")
        monkeypatch.setenv("CRESMO_SATURATION_SEMANTIC_THRESHOLD", "0.85")
        monkeypatch.setenv("CRESMO_SATURATION_MAX_NOVEL_PARAGRAPHS", "2")
        monkeypatch.setenv("CRESMO_SATURATION_LONG_UNIT_WORD_CUTOFF", "160")
        monkeypatch.setenv("CRESMO_SATURATION_SLIDING_WINDOW_SENTENCES", "4")
        monkeypatch.setenv("CRESMO_SATURATION_SLIDING_WINDOW_OVERLAP", "2")

        overridden = CresmoSettings(_env_file=None)
        assert overridden.embedding_provider == "ollama"
        assert overridden.gemini_embedding_model == "text-embedding-004"
        assert overridden.gemini_embedding_dimensions == 256
        assert overridden.ollama_embedding_model == "mxbai-embed-large"
        assert overridden.saturation_lexical_threshold == 0.90
        assert overridden.saturation_max_word_delta == 0.05
        assert overridden.saturation_semantic_threshold == 0.85
        assert overridden.saturation_max_novel_paragraphs == 2
        assert overridden.saturation_long_unit_word_cutoff == 160
        assert overridden.saturation_sliding_window_sentences == 4
        assert overridden.saturation_sliding_window_overlap == 2

        invalid_cases: list[dict[str, object]] = [
            {"gemini_embedding_dimensions": 0},
            {"gemini_embedding_dimensions": -128},
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
        ]
        for invalid_kwargs in invalid_cases:
            with pytest.raises(ValidationError):
                CresmoSettings(_env_file=None, **invalid_kwargs)  # type: ignore[arg-type]
