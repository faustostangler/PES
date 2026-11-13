# SPEC-052: Prompt Catalog SSOT in JSON Resource

**Status:** ACCEPTED  
**Date:** 2026-11-06  
**Governing ADR:** [`ADR-052`](../adr/ADR-052-prompt-catalog-ssot-in-json.md) (Supersedes [`ADR-050`](../adr/ADR-050-prompt-registry-ssot-description-unification.md))  
**Domain Layer:** `cresmo.infrastructure.adapters.prompts.catalog`, `cresmo.infrastructure.resources`

---

## 1. Specification Requirements

1. **`PromptSpec` Validation Model (`catalog.py`):**
   - Immutable Pydantic V2 model (`frozen=True`, `extra="forbid"`) validating `description`, `skills: list[str]`, optional `langfuse_slug`, `system_prompt`, and `user_prompt`.
   - `langfuse_name` property derives `langfuse_slug` if present, otherwise `f"cresmo-{key}"`.
2. **Bijective Catalog Loader (`load_prompt_catalog`):**
   - Validates 1:1 bijection between `PromptKey` enum values and keys in `prompts.json`.
   - Raises `PromptCatalogError` immediately on missing or extra keys.
3. **Retirement of `registry.py`:**
   - `src/cresmo/infrastructure/adapters/prompts/registry.py` is deleted; all consumers (`JsonPromptProvider`, `LangfusePromptProvider`, CLI `seed_prompts`) query `PromptCatalog`.

