"""Prompts Catalog and Adapters Package for Cresmo.

Conforms to ADR-001 (Modular Monolith Domain Integrity),
ADR-017 (Prompt Management with Langfuse & Local Fallback), and
ADR-052 (Prompt Catalog SSOT Consolidation in JSON Resource).
"""

from __future__ import annotations

from cresmo.domain.value_objects import PromptKey
from cresmo.infrastructure.adapters.prompts.catalog import (
    PromptCatalog,
    PromptCatalogError,
    PromptSpec,
    load_prompt_catalog,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider

__all__ = [
    "JsonPromptProvider",
    "LangfusePromptProvider",
    "PromptCatalog",
    "PromptCatalogError",
    "PromptKey",
    "PromptSpec",
    "load_prompt_catalog",
]
