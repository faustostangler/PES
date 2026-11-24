"""Hermetic unit tests for hierarchical CresmoSettings, policy translators, and Anchor Marker resolution."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from cresmo.domain.value_objects import (
    CompendiumRolloverPolicy,
    DiscoveryPolicy,
    SaturationThresholds,
    StageExecutionPolicy,
)
from cresmo.infrastructure.config import (
    CresmoSettings,
    EmbeddingSettings,
    IngestionSettings,
    JudgeSettings,
    LlmSettings,
    ObservabilitySettings,
    PipelineSettings,
    StorageSettings,
)
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
        fallback = find_workspace_root(leaf_dir)
        assert fallback == leaf_dir.resolve().parents[3]


class TestCresmoSettingsRoot:
    """Validate composed root defaults, immutability, policy translators, and env overrides."""

    def test_default_tree_structure_and_zero_legacy_shims(self) -> None:
        settings = CresmoSettings(_env_file=None)

        assert isinstance(settings.llm, LlmSettings)
        assert isinstance(settings.embeddings, EmbeddingSettings)
        assert isinstance(settings.pipeline, PipelineSettings)
        assert isinstance(settings.judge, JudgeSettings)
        assert isinstance(settings.ingestion, IngestionSettings)
        assert isinstance(settings.storage, StorageSettings)
        assert isinstance(settings.observability, ObservabilitySettings)

        # Storage defaults anchored to workspace
        assert settings.storage.data_dir.name == "data"
        assert settings.storage.vault_dir.name == "vault"
        assert settings.storage.raw_dir == settings.storage.data_dir / "raw"
        assert settings.storage.enriched_dir == settings.storage.data_dir / "enriched"
        assert settings.storage.master_dir == settings.storage.data_dir / "master"
        assert settings.storage.index_path == settings.storage.vault_dir / "_index.json"
        assert settings.storage.sqlite_ledger_path == settings.storage.data_dir / "cresmo_ledger.db"
        assert settings.storage.brain_csv_path == settings.storage.data_dir / "brain.csv"

        # Zero legacy flat attributes or ClassVar mirrors
        for removed in (
            "DEFAULT_GEMINI_MODEL",
            "DEFAULT_LANGUAGE",
            "gemini_model",
            "gemini_api_key",
            "max_retries",
            "judge_calibration_models",
            "generator_benchmark_models",
            "vault_dir",
            "data_dir",
            "batch_size",
        ):
            assert not hasattr(settings, removed)
            assert not hasattr(CresmoSettings, removed)

    def test_root_is_frozen_and_nested_models_forbid_extra(self) -> None:
        settings = CresmoSettings(_env_file=None)
        with pytest.raises(ValidationError):
            settings.pipeline = PipelineSettings()  # type: ignore[misc]

        with pytest.raises(ValidationError):
            LlmSettings.model_validate({"unknown_key": "boom"})

        with pytest.raises(ValidationError):
            PipelineSettings.model_validate({"unknown_key": 123})

    def test_policy_translators_produce_pure_domain_value_objects(self, tmp_path: Path) -> None:
        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(ollama={"synthesis_temperature": 0.45}),  # type: ignore[arg-type]
            pipeline=PipelineSettings(
                concat_max_words=120_000,
                stages={"expansion_max_passes": 4, "long_expander_max_passes": 9},  # type: ignore[arg-type]
                saturation={"semantic_threshold": 0.91},  # type: ignore[arg-type]
            ),
            judge=JudgeSettings(blocking=True, max_attempts=3),
            ingestion=IngestionSettings(
                days_lookback=30,
                enable_channel_crawler=True,
                workers={"whisper": 2, "discovery_queue_maxsize": 25},  # type: ignore[arg-type]
            ),
            storage=StorageSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault"),
        )

        stage_policy = settings.to_stage_execution_policy()
        assert stage_policy == StageExecutionPolicy(
            expansion_max_passes=4,
            long_expander_max_passes=9,
            judge_max_attempts=3,
            judge_blocking=True,
            synthesis_temperature=0.45,
            saturation_thresholds=SaturationThresholds(semantic_similarity_threshold=0.91),
        )

        discovery_policy = settings.to_discovery_policy()
        assert discovery_policy == DiscoveryPolicy(
            lookback_days=30,
            discovery_workers=20,
            queue_maxsize=25,
            enable_channel_crawler=True,
        )

        rollover_policy = settings.to_compendium_rollover_policy()
        assert rollover_policy == CompendiumRolloverPolicy(max_words=120_000)

    def test_ensure_directories_creates_all_dirs_and_is_idempotent(self, tmp_path: Path) -> None:
        settings = CresmoSettings(
            _env_file=None,
            storage=StorageSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault"),
        )
        settings.ensure_directories()
        settings.ensure_directories()

        for expected in (
            settings.storage.data_dir,
            settings.storage.vault_dir,
            settings.storage.mocs_dir,
            settings.storage.raw_dir,
            settings.storage.fluid_dir,
            settings.storage.gap_filler_dir,
            settings.storage.enriched_dir,
            settings.storage.master_dir,
            settings.storage.priority_texts_dir,
        ):
            assert expected.is_dir()

    def test_nested_env_override_for_gemini_api_keys_and_workers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CRESMO_LLM__GEMINI__API_KEYS", "k-env-1, k-env-2")
        monkeypatch.setenv("CRESMO_INGESTION__WORKERS__WHISPER", "3")
        monkeypatch.delenv("CRESMO_INGESTION__WORKERS__SUBTITLE", raising=False)
        monkeypatch.delenv("CRESMO_INGESTION__WORKERS__CHANNEL_DISCOVERY", raising=False)

        settings = CresmoSettings(_env_file=None)
        assert settings.llm.gemini.api_keys == (SecretStr("k-env-1"), SecretStr("k-env-2"))
        assert settings.llm.gemini.primary_api_key().get_secret_value() == "k-env-1"
        assert settings.ingestion.workers.whisper == 3
        assert settings.ingestion.workers.subtitle == 15
        assert settings.ingestion.workers.channel_discovery == 30
