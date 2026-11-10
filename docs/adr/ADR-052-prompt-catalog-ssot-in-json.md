# ADR-052: Prompt Catalog SSOT Consolidation in JSON Resource

## Status
ACCEPTED (SUPERSEDES §1 of ADR-050)

## Context
Previously, prompt definitions and metadata were fragmented across three separate representations:
1. `PromptKey` enum in `src/cresmo/domain/value_objects/prompt.py` (canonical identity).
2. `PROMPT_REGISTRY` in `src/cresmo/infrastructure/adapters/prompts/registry.py` (Python dictionary defining `PromptMetadata.description` and optional `langfuse_slug`).
3. `prompts.json` in `src/cresmo/infrastructure/resources/prompts.json` (JSON resource storing `system_prompt`, `user_prompt`, and heterogeneous `skills`/`skill_name` attributes).

This fragmentation caused several architectural and operational deficiencies:
- Dual-maintenance risk: changing a prompt's intent or synthesis contract required modifying both Python code and JSON data.
- Domain contamination risk: placing prompt engineering text and remote Langfuse slugs in Python code blurred boundary clarity.
- Schema inconsistency: `prompts.json` contained dead fields (`active: bool`) and alternating schemas (`skills: list[str]` vs `skill_name: str`).
- Silent failure antipattern: `_get_description_for_key` returned empty strings on missing keys rather than failing fast.

## Decision
1. **JSON Resource as Sole Prompt Content & Metadata SSOT**:
   Consolidate all prompt engineering templates and metadata (`description`, `skills`, `langfuse_slug`, `system_prompt`, `user_prompt`) directly into `prompts.json`.
2. **Schema Uniformity & Dead Field Elimination**:
   - Normalize skill dependencies to `skills: list[str]` across all entries.
   - Purge dead `"active"` boolean flags.
   - Support optional `"langfuse_slug"` overrides directly in the JSON schema.
3. **Pydantic V2 `PromptSpec` Model**:
   Define an immutable, fail-fast `PromptSpec` model (`extra="forbid"`) in `src/cresmo/infrastructure/adapters/prompts/catalog.py` deriving `langfuse_name` deterministically (`cresmo-{key}` or `langfuse_slug`).
4. **Bijective Validation & Fail-Fast Catalog**:
   Implement `load_prompt_catalog()` validating that the keys in `prompts.json` match `PromptKey` exactly (1:1 bijection). Missing or unregistered keys raise `PromptCatalogError` immediately at startup.
5. **Retire `registry.py`**:
   Remove `src/cresmo/infrastructure/adapters/prompts/registry.py`. Migrate `JsonPromptProvider`, `LangfusePromptProvider`, and CLI `seed_prompts` to consume the unified `PromptCatalog`.
6. **Strict Template Consistency**:
   Eliminate `{task}` legacy alias from `JsonPromptProvider`. Embed `{description}` consistently across templates.

## Consequences
- Single, declarative JSON Single Source of Truth for all prompt templates and metadata.
- Compile-time and startup-time guarantees via bijective `PromptKey` validation.
- Clean Hexagonal Architecture: domain layer maintains pure identity (`PromptKey`), infrastructure layer loads and validates prompt content (`PromptCatalog`).

