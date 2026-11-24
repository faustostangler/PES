"""Unified hierarchical CresmoSettings root, policy translators, and singleton helpers.

Composes immutable sub-domain Pydantic models under a single BaseSettings boundary
using ``CRESMO_`` + ``__`` nested environment delimiter, with zero legacy aliases.

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-006: Resilient Workspace Root Discovery
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from cresmo.domain.value_objects import (
    CompendiumRolloverPolicy,
    DiscoveryPolicy,
    StageExecutionPolicy,
)
from cresmo.infrastructure.config.embeddings import EmbeddingSettings
from cresmo.infrastructure.config.ingestion import IngestionSettings
from cresmo.infrastructure.config.judge import JudgeSettings
from cresmo.infrastructure.config.llm import LlmSettings
from cresmo.infrastructure.config.observability import ObservabilitySettings
from cresmo.infrastructure.config.pipeline import PipelineSettings
from cresmo.infrastructure.config.storage import StorageSettings
from cresmo.infrastructure.environment import ensure_runtime_directories
from cresmo.infrastructure.paths import find_workspace_root

_WORKSPACE_DIR = find_workspace_root()


class CresmoSettings(BaseSettings):
    """Single Source of Truth (SSOT) hierarchical configuration root for the Cresmo engine."""

    model_config = SettingsConfigDict(
        env_prefix="CRESMO_",
        env_nested_delimiter="__",
        env_file=(
            ".env",
            str(_WORKSPACE_DIR / ".env"),
            str(_WORKSPACE_DIR / "vault" / ".env"),
            str(_WORKSPACE_DIR / "data" / ".env"),
        ),
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
    )

    llm: LlmSettings = Field(default_factory=LlmSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)
    judge: JudgeSettings = Field(default_factory=JudgeSettings)
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

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

    def to_stage_execution_policy(self) -> StageExecutionPolicy:
        """Translate infrastructure settings into pure domain StageExecutionPolicy."""
        return StageExecutionPolicy(
            expansion_max_passes=self.pipeline.stages.expansion_max_passes,
            long_expander_max_passes=self.pipeline.stages.long_expander_max_passes,
            judge_max_attempts=self.judge.max_attempts,
            judge_blocking=self.judge.blocking,
            synthesis_temperature=self.llm.ollama.synthesis_temperature,
            saturation_thresholds=self.pipeline.saturation.to_domain_thresholds(),
        )

    def to_discovery_policy(self) -> DiscoveryPolicy:
        """Translate infrastructure settings into pure domain DiscoveryPolicy."""
        return DiscoveryPolicy(
            lookback_days=self.ingestion.days_lookback,
            discovery_workers=self.ingestion.workers.channel_discovery,
            queue_maxsize=self.ingestion.workers.discovery_queue_maxsize,
            enable_channel_crawler=self.ingestion.enable_channel_crawler,
        )

    def to_compendium_rollover_policy(self) -> CompendiumRolloverPolicy:
        """Translate infrastructure settings into pure domain CompendiumRolloverPolicy."""
        return CompendiumRolloverPolicy(max_words=self.pipeline.concat_max_words)

    def ensure_directories(self) -> None:
        """Ensure all runtime storage directories exist on the filesystem."""
        ensure_runtime_directories(self.storage)


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
