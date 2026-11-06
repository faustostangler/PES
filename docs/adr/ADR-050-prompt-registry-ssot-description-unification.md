# ADR-050: Elimination of Prompt Task Duplication and SSOT Consolidation in PROMPT_REGISTRY

## Status
Accepted

## Context
In previous iterations, prompt definitions maintained descriptions and synthesis responsibilities in two separate locations:
1. `PromptMetadata.description` within `src/cresmo/infrastructure/adapters/prompts/registry.py` (canonical Python registry typed with `PromptKey`).
2. The `"task"` field inside `src/cresmo/infrastructure/resources/prompts.json` and associated template substitution placeholders (`{task}`).

This separation caused duplication, divergent descriptions, semantic drifts between local fallbacks and Langfuse cloud registrations, and violated the Single Source of Truth (SSOT) tenet of Hexagonal Architecture and ADR-017.

## Decision
1. **SSOT Consolidation**: Establish `PROMPT_REGISTRY` in `src/cresmo/infrastructure/adapters/prompts/registry.py` as the sole canonical authority for prompt descriptions, responsibilities, and metadata.
2. **Purge `"task"` without Backward Compatibility**: Completely remove all `"task"` keys from `prompts.json`.
3. **Template Substitution**: Migrate all `{task}` occurrences within system/user prompts to `{description}`, resolved directly from `PROMPT_REGISTRY[key].description`.
4. **Builder and Provider Refactoring**: Refactor `JsonPromptProvider` and `builders.py` to source `description` exclusively from `PROMPT_REGISTRY`, failing fast if an unregistered key is queried.

## Consequences
- Single, strictly typed source of truth for prompt responsibilities.
- Zero duplicate description strings between JSON resources and Python registry.
- Seamless alignment with Langfuse prompt seeding and observability metadata.

