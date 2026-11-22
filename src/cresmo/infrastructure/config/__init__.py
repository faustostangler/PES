"""Modular Domain Settings Package for Cresmo Hexagonal Modular Monolith.

Re-exports all legacy configuration constants, type aliases, shared singleton helpers,
and domain-scoped BaseSettings classes per ADR-069.
"""

from __future__ import annotations

from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS,
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    DEFAULT_GENERATOR_BENCHMARK_MODELS,
    DEFAULT_JUDGE_CALIBRATION_MODELS,
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    DEFAULT_LANGFUSE_PROMPT_LABEL,
    GEMINI_FREE_TIER_MODELS,
    GEMINI_THINKING_LEVELS,
    GeminiFreeTierModel,
    GeminiThinkingLevel,
    resolve_default_pipeline_version,
)
from cresmo.infrastructure.config.ingestion import IngestionSettings
from cresmo.infrastructure.config.judge import JudgeSettings
from cresmo.infrastructure.config.llm import LlmSettings
from cresmo.infrastructure.config.saturation import SaturationSettings
from cresmo.infrastructure.config.settings import (
    CresmoSettings,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.infrastructure.config.storage import StorageSettings
from cresmo.infrastructure.config.telemetry import TelemetrySettings

__all__ = [
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
    "IngestionSettings",
    "JudgeSettings",
    "LlmSettings",
    "SaturationSettings",
    "StorageSettings",
    "TelemetrySettings",
    "get_shared_settings",
    "reset_shared_settings",
    "resolve_default_pipeline_version",
    "resolve_shared_settings",
]
