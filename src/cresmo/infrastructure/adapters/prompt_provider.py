"""Prompt Provider Adapters Facade.

Conforms to ADR-001 (Modular Monolith Domain Integrity),
ADR-017 (Prompt Management with Langfuse & Local Fallback), and
ADR-052 (Prompt Catalog SSOT Consolidation in JSON Resource).

This module re-exports components from `cresmo.infrastructure.adapters.prompts`
for unified catalog access.
"""

from __future__ import annotations

from cresmo.infrastructure.adapters.prompts import (
    JsonPromptProvider,
    LangfusePromptProvider,
    PromptCatalog,
    PromptCatalogError,
    PromptKey,
    PromptSpec,
    load_prompt_catalog,
)
from cresmo.infrastructure.adapters.prompts.json_provider import _CANDIDATE_SKILLS_DIRS

__all__ = [
    "_CANDIDATE_SKILLS_DIRS",
    "JsonPromptProvider",
    "LangfusePromptProvider",
    "PromptCatalog",
    "PromptCatalogError",
    "PromptKey",
    "PromptSpec",
    "load_prompt_catalog",
]
