"""Prompt provisioning adapters, catalog, skill loader, template renderer, and context normalizer.

Conforms to:
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

from cresmo.infrastructure.adapters.prompts.catalog import (
    PromptCatalog,
    PromptCatalogError,
    PromptManifestEntry,
    PromptSpec,
    load_prompt_catalog,
)
from cresmo.infrastructure.adapters.prompts.context_normalizer import (
    DEFAULT_LANGUAGE,
    PROMPT_VARIABLE_SCHEMAS,
    PromptVariableSchema,
    normalize_prompt_context,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider
from cresmo.infrastructure.adapters.prompts.skill_loader import (
    SkillDocumentLoader,
    strip_yaml_frontmatter,
)
from cresmo.infrastructure.adapters.prompts.template_renderer import TemplateRenderer

__all__ = [
    "DEFAULT_LANGUAGE",
    "PROMPT_VARIABLE_SCHEMAS",
    "JsonPromptProvider",
    "LangfusePromptProvider",
    "PromptCatalog",
    "PromptCatalogError",
    "PromptManifestEntry",
    "PromptSpec",
    "PromptVariableSchema",
    "SkillDocumentLoader",
    "TemplateRenderer",
    "load_prompt_catalog",
    "normalize_prompt_context",
    "strip_yaml_frontmatter",
]
