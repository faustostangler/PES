"""Prompts Registry and Adapters Package for Cresmo.

Conforms to ADR-001 (Modular Monolith Domain Integrity) and
ADR-017 (Prompt Management with Langfuse & Local Fallback).
"""

from __future__ import annotations

from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider
from cresmo.infrastructure.adapters.prompts.registry import (
    LANGFUSE_TO_PROMPT_KEY,
    PROMPT_REGISTRY,
    PromptKey,
    PromptMetadata,
    get_prompt_metadata,
)

__all__ = [
    "LANGFUSE_TO_PROMPT_KEY",
    "PROMPT_REGISTRY",
    "JsonPromptProvider",
    "LangfusePromptProvider",
    "PromptKey",
    "PromptMetadata",
    "get_prompt_metadata",
]
