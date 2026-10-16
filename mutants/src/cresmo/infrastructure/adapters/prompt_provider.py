"""Prompt Provider Adapters Facade.

Conforms to ADR-001 (Modular Monolith Domain Integrity) and
ADR-017 (Prompt Management with Langfuse & Local Fallback).

This module re-exports components from `cresmo.infrastructure.adapters.prompts`
for seamless backward-compatibility.
"""

from __future__ import annotations

from cresmo.infrastructure.adapters.prompts import (
    LANGFUSE_TO_PROMPT_KEY,
    PROMPT_REGISTRY,
    JsonPromptProvider,
    LangfusePromptProvider,
    PromptKey,
    PromptMetadata,
    get_prompt_metadata,
)
from cresmo.infrastructure.adapters.prompts.json_provider import _CANDIDATE_SKILLS_DIRS

__all__ = [
    "LANGFUSE_TO_PROMPT_KEY",
    "PROMPT_REGISTRY",
    "_CANDIDATE_SKILLS_DIRS",
    "JsonPromptProvider",
    "LangfusePromptProvider",
    "PromptKey",
    "PromptMetadata",
    "get_prompt_metadata",
]
