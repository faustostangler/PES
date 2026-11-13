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
from cresmo.infrastructure.adapters.prompts.taxonomy_catalog import (
    JsonTaxonomyCatalogAdapter,
    TaxonomyCatalogError,
    load_taxonomy_catalog,
)

__all__ = [
    "JsonPromptProvider",
    "JsonTaxonomyCatalogAdapter",
    "LangfusePromptProvider",
    "PromptCatalog",
    "PromptCatalogError",
    "PromptKey",
    "PromptSpec",
    "TaxonomyCatalogError",
    "load_prompt_catalog",
    "load_taxonomy_catalog",
]
