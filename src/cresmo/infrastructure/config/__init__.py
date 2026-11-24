"""Hierarchical Immutable Settings Package for Cresmo Hexagonal Modular Monolith.

Re-exports canonical catalog constants, type aliases, shared singleton helpers,
composed sub-domain BaseModels, and the CresmoSettings root per ADR-074.
"""

from __future__ import annotations

from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS,
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    DEFAULT_LANGFUSE_ENVIRONMENT,
    DEFAULT_LANGFUSE_PROMPT_LABEL,
    DEFAULT_PROMPTS_RESOURCE_NAME,
    DEFAULT_PROMPTS_RESOURCE_PACKAGE,
    DEFAULT_TAXONOMY_RESOURCE_NAME,
    DEFAULT_TAXONOMY_RESOURCE_PACKAGE,
    GEMINI_FREE_TIER_MODELS,
    GEMINI_THINKING_LEVELS,
    LANGFUSE_ENVIRONMENT_PATTERN,
    GeminiFreeTierModel,
    GeminiThinkingLevel,
    resolve_default_pipeline_version,
)
from cresmo.infrastructure.config.embeddings import EmbeddingSettings
from cresmo.infrastructure.config.ingestion import (
    CookieSettings,
    IngestionSettings,
    WorkerPoolSettings,
)
from cresmo.infrastructure.config.judge import (
    GapFillerJudgeSettings,
    JudgeGeminiSettings,
    JudgeProviderName,
    JudgeSettings,
    TypeSafeSettings,
)
from cresmo.infrastructure.config.llm import (
    GeminiSettings,
    LlmSettings,
    OllamaSettings,
)
from cresmo.infrastructure.config.observability import (
    LangfuseSettings,
    LoggingSettings,
    ObservabilitySettings,
    PrometheusSettings,
    RuntimeTelemetrySettings,
)
from cresmo.infrastructure.config.pipeline import (
    PipelineSettings,
    SaturationSettings,
    StageBudgetsSettings,
)
from cresmo.infrastructure.config.settings import (
    CresmoSettings,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.infrastructure.config.storage import StorageSettings

__all__ = [
    "DEFAULT_BENCHMARK_MODELS",
    "DEFAULT_GEMINI_FALLBACK_MODEL",
    "DEFAULT_GEMINI_MAX_OUTPUT_TOKENS",
    "DEFAULT_GEMINI_MODEL",
    "DEFAULT_GEMINI_THINKING_LEVEL",
    "DEFAULT_GEMINI_TIMEOUT_SECONDS",
    "DEFAULT_JUDGE_GEMINI_MODEL",
    "DEFAULT_JUDGE_PASS_THRESHOLD",
    "DEFAULT_LANGFUSE_ENVIRONMENT",
    "DEFAULT_LANGFUSE_PROMPT_LABEL",
    "DEFAULT_PROMPTS_RESOURCE_NAME",
    "DEFAULT_PROMPTS_RESOURCE_PACKAGE",
    "DEFAULT_TAXONOMY_RESOURCE_NAME",
    "DEFAULT_TAXONOMY_RESOURCE_PACKAGE",
    "GEMINI_FREE_TIER_MODELS",
    "GEMINI_THINKING_LEVELS",
    "LANGFUSE_ENVIRONMENT_PATTERN",
    "CookieSettings",
    "CresmoSettings",
    "EmbeddingSettings",
    "GapFillerJudgeSettings",
    "GeminiFreeTierModel",
    "GeminiSettings",
    "GeminiThinkingLevel",
    "IngestionSettings",
    "JudgeGeminiSettings",
    "JudgeProviderName",
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
    "resolve_default_pipeline_version",
    "resolve_shared_settings",
]
