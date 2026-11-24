"""Shared model catalogs, resource constants, and parsing helpers for Cresmo settings.

Conforms to:
    - ADR-063: Dynamic Pipeline Versioning via importlib.metadata
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

import importlib.metadata
import json
from typing import Any, Literal

DEFAULT_LANGFUSE_ENVIRONMENT: str = "staging"
LANGFUSE_ENVIRONMENT_PATTERN: str = r"^(?!langfuse)[a-z0-9-_]{1,40}$"
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
DEFAULT_BENCHMARK_MODELS: tuple[str, ...] = (
    "gemini:gemini-3.5-flash-lite",
    "gemini:gemini-3.8-flash",
    "gemini:gemini-4-hydrogen",
)


def resolve_default_pipeline_version() -> str:
    """Resolve canonical pipeline version dynamically from distribution metadata (ADR-063)."""
    try:
        pkg_version = importlib.metadata.version("pes")
    except importlib.metadata.PackageNotFoundError:
        pkg_version = "0.0.0-dev"
    return f"cresmo:v{pkg_version}"


def normalize_str_choice(value: Any) -> Any:
    """Strip surrounding whitespace and lowercase string choice values."""
    if isinstance(value, str):
        return value.strip().lower()
    return value


def parse_comma_separated_strings(value: Any) -> Any:
    """Parse comma-separated strings, JSON string arrays, or sequences into a clean tuple[str, ...]."""
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ()
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                raise ValueError("Expected JSON array for sequence setting.")
            return tuple(str(item).strip() for item in parsed if str(item).strip())
        return tuple(part.strip() for part in stripped.split(",") if part.strip())
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return value


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
    "GeminiFreeTierModel",
    "GeminiThinkingLevel",
    "normalize_str_choice",
    "parse_comma_separated_strings",
    "resolve_default_pipeline_version",
]
