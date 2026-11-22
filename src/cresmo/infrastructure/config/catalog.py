"""Shared model catalogs, resource constants, and versioning helpers for Cresmo settings.

Conforms to:
    - ADR-063: Dynamic Pipeline Versioning via importlib.metadata
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

import importlib.metadata
from typing import Any, Literal

from pydantic_settings import PydanticBaseSettingsSource

DEFAULT_LANGFUSE_PROMPT_LABEL: str = "production"
DEFAULT_PROMPTS_RESOURCE_PACKAGE: str = "cresmo.infrastructure.resources"
DEFAULT_PROMPTS_RESOURCE_NAME: str = "prompts.json"
DEFAULT_TAXONOMY_RESOURCE_PACKAGE: str = "cresmo.infrastructure.resources"
DEFAULT_TAXONOMY_RESOURCE_NAME: str = "taxonomy.json"
DEFAULT_JUDGE_PASS_THRESHOLD: float = 0.9

GeminiFreeTierModel = Literal[
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
]
GEMINI_FREE_TIER_MODELS: tuple[str, ...] = (
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
GeminiThinkingLevel = Literal["minimal", "low", "medium", "high", "xhigh"]
GEMINI_THINKING_LEVELS: tuple[str, ...] = ("minimal", "low", "medium", "high", "xhigh")

DEFAULT_GEMINI_MODEL: str = "gemini-3.5-flash-lite"
DEFAULT_GEMINI_FALLBACK_MODEL: str = "gemini-3.6-flash"
DEFAULT_JUDGE_GEMINI_MODEL: str = DEFAULT_GEMINI_MODEL
DEFAULT_GEMINI_THINKING_LEVEL: GeminiThinkingLevel = "low"
DEFAULT_GEMINI_MAX_OUTPUT_TOKENS: int = 32_768
DEFAULT_GEMINI_TIMEOUT_SECONDS: float = 300.0
DEFAULT_BENCHMARK_MODELS: list[str] = [
    "gemini:gemini-3.5-flash-lite",
    "gemini:gemini-3.8-flash",
    "gemini:gemini-4-hydrogen",
    # Remaining Free-Tier text/multimodal options (GEMINI_FREE_TIER_MODELS):
    # "gemini:gemini-3.6-flash",
    # "gemini:gemini-3.1-flash-lite",
    # "gemini:gemini-3-flash-preview",
    # "gemini:gemma-4-31b-it",
    # "gemini:gemma-4-26b-a4b-it",
    # "gemini:gemini-2.5-flash-lite",
    # "gemini:gemini-2.5-flash",
    # "gemini:gemini-2.5-pro",
    # "ollama:qwen2.5:latest",
    # "ollama:gemma4:latest",
    # "ollama:deepseek-r1:7b",
    # "ollama:llama3:latest",
]
DEFAULT_JUDGE_CALIBRATION_MODELS: list[str] = DEFAULT_BENCHMARK_MODELS
DEFAULT_GENERATOR_BENCHMARK_MODELS: list[str] = DEFAULT_BENCHMARK_MODELS


def resolve_default_pipeline_version() -> str:
    """Resolve canonical pipeline version dynamically from distribution metadata (ADR-063)."""
    try:
        pkg_version = importlib.metadata.version("pes")
    except importlib.metadata.PackageNotFoundError:
        pkg_version = "0.0.0-dev"
    return f"cresmo:v{pkg_version}"


def _normalize_str_choice(value: Any) -> Any:
    """Strip surrounding whitespace and lowercase string choice values."""
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _customize_comma_list_sources(
    field_names: tuple[str, ...],
    init_settings: PydanticBaseSettingsSource,
    env_settings: PydanticBaseSettingsSource,
    dotenv_settings: PydanticBaseSettingsSource,
    file_secret_settings: PydanticBaseSettingsSource,
) -> tuple[PydanticBaseSettingsSource, ...]:
    """Wrap env and dotenv complex decoders to accept comma-separated strings safely."""

    def _safe_decode(field_name: str, field: Any, val: Any, orig_decode: Any) -> Any:
        if field_name in field_names and isinstance(val, str):
            try:
                return orig_decode(field_name, field, val)
            except (ValueError, TypeError):
                return [p.strip() for p in val.split(",") if p.strip()]
        return orig_decode(field_name, field, val)

    orig_dot = dotenv_settings.decode_complex_value
    dotenv_settings.decode_complex_value = (  # type: ignore[method-assign]
        lambda field_name, field, value: _safe_decode(field_name, field, value, orig_dot)
    )

    orig_env = env_settings.decode_complex_value
    env_settings.decode_complex_value = (  # type: ignore[method-assign]
        lambda field_name, field, value: _safe_decode(field_name, field, value, orig_env)
    )

    return (
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    )


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
    "DEFAULT_PROMPTS_RESOURCE_NAME",
    "DEFAULT_PROMPTS_RESOURCE_PACKAGE",
    "DEFAULT_TAXONOMY_RESOURCE_NAME",
    "DEFAULT_TAXONOMY_RESOURCE_PACKAGE",
    "GEMINI_FREE_TIER_MODELS",
    "GEMINI_THINKING_LEVELS",
    "GeminiFreeTierModel",
    "GeminiThinkingLevel",
    "resolve_default_pipeline_version",
]
