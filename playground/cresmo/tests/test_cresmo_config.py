"""Unit and integration tests for Cresmo Centralized Configuration.

Tests the SOTA KISS single source of truth (SSOT) configuration architecture,
verifying fail-fast validation, 4-category taxonomy, provider-segregated LLM settings,
dynamic worker calculation, and external file loading (YAML, TOML, JSON).
"""

import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest
from pydantic import ValidationError

from cresmo_config import (
    AgentRPCSettings,
    CresmoConfig,
    GeminiProviderSettings,
    IngestionSettings,
    LLMConfig,
    OllamaProviderSettings,
    PipelineSettings,
    RetrySettings,
    RuntimeSettings,
    StorageSettings,
    get_config,
    reset_config,
)


@pytest.fixture(autouse=True)
def clean_config_state():
    """Reset cached singleton before and after each test."""
    reset_config()
    yield
    reset_config()


def test_cresmo_config_fail_fast_missing_api_key():
    """Verify system fails fast with ValidationError when GEMINI_API_KEY is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError) as exc_info:
            CresmoConfig(_env_file=None)
        errors = exc_info.value.errors()
        assert any("gemini_api_key" in str(err.get("loc", [])) for err in errors)


def test_cresmo_config_defaults_with_dummy_key():
    """Verify full configuration hierarchy loads with correct defaults."""
    config = CresmoConfig(_env_file=None, gemini_api_key="AIzaSyDummyKeyForTesting")

    # 🔴 Secret
    assert config.gemini_api_key.get_secret_value() == "AIzaSyDummyKeyForTesting"

    # 🟡 Infra & Topology
    assert isinstance(config.storage, StorageSettings)
    assert config.storage.root_dir.exists()
    assert config.storage.raw_dir == config.storage.root_dir / "raw"
    assert config.storage.enriched_dir == config.storage.root_dir / "enriched"
    assert config.storage.wiki_dir == config.storage.root_dir / "wiki"
    assert config.storage.processed_log == config.storage.root_dir / "processed_cresmo.json"
    assert config.storage.cookies_file == config.storage.root_dir / ".yt_dlp_cookies.txt"

    assert isinstance(config.agent_rpc, AgentRPCSettings)
    assert config.agent_rpc.ls_address == "127.0.0.1:41667"
    assert config.agent_rpc.grpc_test_timeout == 1.5
    assert config.agent_rpc.fallback_test_conversation_id == "0e69775c-ba22-4a48-ad18-ba6a318c9a04"

    # 🟢 Operational Tunables - LLM Provider Segregation
    assert isinstance(config.llm, LLMConfig)
    assert config.llm.active_provider == "gemini"
    assert isinstance(config.llm.gemini, GeminiProviderSettings)
    assert config.llm.gemini.model_name == "gemini-2.5-flash"
    assert config.llm.gemini.temperature == 0.7
    assert config.llm.gemini.max_output_tokens == 65536
    assert config.llm.gemini.request_timeout_seconds == 180.0
    assert config.llm.gemini.enable_streaming is True

    # Retry parameters are configurable, not hardcoded
    assert isinstance(config.llm.gemini.retry, RetrySettings)
    assert config.llm.gemini.retry.max_attempts == 7
    assert config.llm.gemini.retry.multiplier == 2.0
    assert config.llm.gemini.retry.min_seconds == 2.0
    assert config.llm.gemini.retry.max_seconds == 60.0

    assert isinstance(config.llm.ollama, OllamaProviderSettings)
    assert config.llm.ollama.base_url == "http://localhost:11434"
    assert config.llm.ollama.model_name == "phi3:mini"

    # 🟢 Pipeline Settings
    assert isinstance(config.pipeline, PipelineSettings)
    assert config.pipeline.trajectory_timeout_seconds == 15
    assert config.pipeline.poll_max_attempts == 300
    assert config.pipeline.stage2_passes == 3
    assert config.pipeline.prompt_max_bytes_inline == 120_000

    # 🟢 Ingestion Settings
    assert isinstance(config.ingestion, IngestionSettings)
    assert config.ingestion.days_lookback == 365 * 2
    assert config.ingestion.whisper_model == "base"
    assert config.ingestion.keep_audio is False

    # 🟢 Runtime Settings
    assert isinstance(config.runtime, RuntimeSettings)
    assert config.runtime.default_command == "sync"
    assert config.runtime.isolate_context is True
    assert config.runtime.default_categories == ("politics_br",)


def test_ingestion_worker_calculation_debug_vs_prod():
    """Verify max_workers is 1 for debug and CPU count for prod when not explicitly set."""
    ingestion = IngestionSettings(max_workers=None)

    # In debug mode, concurrency is strictly 1
    assert ingestion.resolve_max_workers(debug=True) == 1

    # In production mode, concurrency uses CPU count
    expected_prod_workers = max(1, os.cpu_count() or 1)
    assert ingestion.resolve_max_workers(debug=False) == expected_prod_workers

    # Explicit override takes precedence
    explicit_ingestion = IngestionSettings(max_workers=8)
    assert explicit_ingestion.resolve_max_workers(debug=True) == 8
    assert explicit_ingestion.resolve_max_workers(debug=False) == 8


def test_custom_storage_root_recalculates_paths(tmp_path: Path):
    """Verify setting a custom storage root correctly anchors all derived paths."""
    custom_root = tmp_path / "custom_cresmo"
    custom_root.mkdir()

    storage = StorageSettings(root_dir=custom_root)
    assert storage.raw_dir == custom_root / "raw"
    assert storage.enriched_dir == custom_root / "enriched"
    assert storage.wiki_dir == custom_root / "wiki"
    assert storage.processed_log == custom_root / "processed_cresmo.json"
    assert storage.playlist_file == custom_root / "playlist.txt"
    assert storage.cookies_file == custom_root / ".yt_dlp_cookies.txt"


def test_load_from_external_yaml_file(tmp_path: Path):
    """Verify CresmoConfig loads configuration from an external YAML file."""
    yaml_content = """
gemini_api_key: AIzaSyFromYamlFile
llm:
  active_provider: gemini
  gemini:
    model_name: gemini-3.8-flash
    temperature: 0.3
    retry:
      max_attempts: 10
      multiplier: 1.5
pipeline:
  stage2_passes: 5
ingestion:
  max_workers: 4
"""
    yaml_file = tmp_path / "cresmo_config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    config = CresmoConfig.from_file(yaml_file)
    assert config.gemini_api_key.get_secret_value() == "AIzaSyFromYamlFile"
    assert config.llm.gemini.model_name == "gemini-3.8-flash"
    assert config.llm.gemini.temperature == 0.3
    assert config.llm.gemini.retry.max_attempts == 10
    assert config.llm.gemini.retry.multiplier == 1.5
    assert config.pipeline.stage2_passes == 5
    assert config.ingestion.max_workers == 4


def test_load_from_external_toml_file(tmp_path: Path):
    """Verify CresmoConfig loads configuration from an external TOML file."""
    toml_content = """
gemini_api_key = "AIzaSyFromTomlFile"

[llm]
active_provider = "ollama"

[llm.gemini]
model_name = "gemini-pro"

[llm.ollama]
base_url = "http://192.168.1.50:11434"
model_name = "llama3:8b"

[pipeline]
poll_max_attempts = 150
"""
    toml_file = tmp_path / "cresmo_config.toml"
    toml_file.write_text(toml_content, encoding="utf-8")

    config = CresmoConfig.from_file(toml_file)
    assert config.gemini_api_key.get_secret_value() == "AIzaSyFromTomlFile"
    assert config.llm.active_provider == "ollama"
    assert config.llm.gemini.model_name == "gemini-pro"
    assert config.llm.ollama.base_url == "http://192.168.1.50:11434"
    assert config.llm.ollama.model_name == "llama3:8b"
    assert config.pipeline.poll_max_attempts == 150


def test_load_from_external_json_file(tmp_path: Path):
    """Verify CresmoConfig loads configuration from an external JSON file."""
    json_data = {
        "gemini_api_key": "AIzaSyFromJsonFile",
        "runtime": {
            "default_command": "watch",
            "isolate_context": False,
        },
        "agent_rpc": {
            "fallback_test_conversation_id": "custom-fallback-uuid-1234",
            "grpc_test_timeout": 3.0,
        },
    }
    json_file = tmp_path / "cresmo_config.json"
    json_file.write_text(json.dumps(json_data), encoding="utf-8")

    config = CresmoConfig.from_file(json_file)
    assert config.gemini_api_key.get_secret_value() == "AIzaSyFromJsonFile"
    assert config.runtime.default_command == "watch"
    assert config.runtime.isolate_context is False
    assert config.agent_rpc.fallback_test_conversation_id == "custom-fallback-uuid-1234"
    assert config.agent_rpc.grpc_test_timeout == 3.0


def test_get_config_singleton_caching():
    """Verify get_config caches instance and respects reload=True."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSySingletonTest"}):
        cfg1 = get_config(reload=True)
        cfg2 = get_config()
        assert cfg1 is cfg2
        assert cfg1.gemini_api_key.get_secret_value() == "AIzaSySingletonTest"

    # Reload with new environment
    with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSySingletonReloaded"}):
        cfg3 = get_config(reload=True)
        assert cfg3 is not cfg1
        assert cfg3.gemini_api_key.get_secret_value() == "AIzaSySingletonReloaded"
