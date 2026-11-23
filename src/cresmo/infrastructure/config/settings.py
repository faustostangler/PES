"""Unified CresmoSettings facade and shared singleton resolution.

Composes all six domain-scoped BaseSettings classes while preserving flat .env
compatibility, comma-separated complex env decoding, and runtime lifecycle helpers.

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-006: Resilient Workspace Root Discovery
    - ADR-048: Architectural Remediation and Comprehensive Mutation Blindage
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, ClassVar

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS,
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    DEFAULT_LANGFUSE_ENVIRONMENT,
    DEFAULT_LANGFUSE_PROMPT_LABEL,
    DEFAULT_PROMPTS_RESOURCE_NAME,
    DEFAULT_PROMPTS_RESOURCE_PACKAGE,
    DEFAULT_TAXONOMY_RESOURCE_NAME,
    DEFAULT_TAXONOMY_RESOURCE_PACKAGE,
    GEMINI_FREE_TIER_MODELS,
    GEMINI_THINKING_LEVELS,
    GeminiThinkingLevel,
    _customize_comma_list_sources,
)
from cresmo.infrastructure.config.ingestion import IngestionSettings
from cresmo.infrastructure.config.judge import JudgeSettings
from cresmo.infrastructure.config.llm import LlmSettings
from cresmo.infrastructure.config.saturation import SaturationSettings
from cresmo.infrastructure.config.storage import StorageSettings
from cresmo.infrastructure.config.telemetry import TelemetrySettings
from cresmo.infrastructure.environment import ensure_runtime_directories
from cresmo.infrastructure.paths import find_workspace_root

_WORKSPACE_DIR = find_workspace_root()


class CresmoSettings(
    LlmSettings,
    TelemetrySettings,
    StorageSettings,
    IngestionSettings,
    SaturationSettings,
    JudgeSettings,
):
    """Single Source of Truth (SSOT) configuration facade for the Cresmo engine."""

    DEFAULT_LANGUAGE: ClassVar[str] = DEFAULT_LANGUAGE
    DEFAULT_LANGFUSE_ENVIRONMENT: ClassVar[str] = DEFAULT_LANGFUSE_ENVIRONMENT
    DEFAULT_LANGFUSE_PROMPT_LABEL: ClassVar[str] = DEFAULT_LANGFUSE_PROMPT_LABEL
    DEFAULT_PROMPTS_RESOURCE_PACKAGE: ClassVar[str] = DEFAULT_PROMPTS_RESOURCE_PACKAGE
    DEFAULT_PROMPTS_RESOURCE_NAME: ClassVar[str] = DEFAULT_PROMPTS_RESOURCE_NAME
    DEFAULT_TAXONOMY_RESOURCE_PACKAGE: ClassVar[str] = DEFAULT_TAXONOMY_RESOURCE_PACKAGE
    DEFAULT_TAXONOMY_RESOURCE_NAME: ClassVar[str] = DEFAULT_TAXONOMY_RESOURCE_NAME
    DEFAULT_JUDGE_PASS_THRESHOLD: ClassVar[float] = DEFAULT_JUDGE_PASS_THRESHOLD
    GEMINI_FREE_TIER_MODELS: ClassVar[tuple[str, ...]] = GEMINI_FREE_TIER_MODELS
    GEMINI_THINKING_LEVELS: ClassVar[tuple[str, ...]] = GEMINI_THINKING_LEVELS
    DEFAULT_GEMINI_MODEL: ClassVar[str] = DEFAULT_GEMINI_MODEL
    DEFAULT_GEMINI_FALLBACK_MODEL: ClassVar[str] = DEFAULT_GEMINI_FALLBACK_MODEL
    DEFAULT_JUDGE_GEMINI_MODEL: ClassVar[str] = DEFAULT_GEMINI_MODEL
    DEFAULT_GEMINI_THINKING_LEVEL: ClassVar[GeminiThinkingLevel] = DEFAULT_GEMINI_THINKING_LEVEL
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS: ClassVar[int] = DEFAULT_GEMINI_MAX_OUTPUT_TOKENS
    DEFAULT_BENCHMARK_MODELS: ClassVar[list[str]] = DEFAULT_BENCHMARK_MODELS
    DEFAULT_JUDGE_CALIBRATION_MODELS: ClassVar[list[str]] = DEFAULT_BENCHMARK_MODELS
    DEFAULT_GENERATOR_BENCHMARK_MODELS: ClassVar[list[str]] = DEFAULT_BENCHMARK_MODELS

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            str(_WORKSPACE_DIR / ".env"),
            str(_WORKSPACE_DIR / "vault" / ".env"),
            str(_WORKSPACE_DIR / "data" / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise settings sources to safely parse comma-separated lists from env."""
        return _customize_comma_list_sources(
            (
                "gemini_api_keys",
                "benchmark_models",
                "judge_calibration_models",
                "generator_benchmark_models",
            ),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def __init__(
        self,
        *args: Any,
        _env_file: Path | str | None | Any = ...,
        **values: Any,
    ) -> None:
        """Initialize settings with optional explicit environment file override."""
        if _env_file is not ...:
            values["_env_file"] = _env_file
        super().__init__(*args, **values)

    def ensure_directories(self) -> None:
        """Ensure all runtime directories exist on the filesystem."""
        ensure_runtime_directories(self)


@functools.lru_cache(maxsize=1)
def get_shared_settings() -> CresmoSettings:
    """Return canonical cached CresmoSettings singleton."""
    return CresmoSettings()


def reset_shared_settings() -> None:
    """Clear cached settings singleton (used for test isolation)."""
    get_shared_settings.cache_clear()


def resolve_shared_settings(settings: CresmoSettings | None = None) -> CresmoSettings:
    """Resolve injected settings or fall back to the memoized single source of truth."""
    if settings is not None:
        return settings
    return get_shared_settings()


__all__ = [
    "CresmoSettings",
    "get_shared_settings",
    "reset_shared_settings",
    "resolve_shared_settings",
]
