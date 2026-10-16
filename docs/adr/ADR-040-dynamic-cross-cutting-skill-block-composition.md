# ADR-040: Dynamic Cross-Cutting Skill Block Composition in JsonPromptProvider and Cresmo Style Embedding

**Status:** PROPOSED  
**Date:** 2026-10-13  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-017`](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md), [`ADR-022`](ADR-022-universal-system-instruction-user-prompt-segregation.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-034`](ADR-034-algorithmic-and-cognitive-parity-standard.md), [`ADR-039`](ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md)

---

## 1. Context & Architectural Motivation

In ADR-017 and ADR-028, Cresmo established prompt template governance through `JsonPromptProvider` backed by `prompts.json` and agent skills located under `.agents/skills/`.

### 1.1 Structural Problem: Static Prompt Duplication vs. Dynamic SSOT
While downstream stages (`gap_filler_pass1`, `long_expander`, `wide_expander`) dynamically interpolate their skill markdown documents using the `{skill_block}` token in `prompts.json`, the Stage 1 prompt (`fluid_prose`) suffers from architectural decay:
1. **Static Inlining of Markdown Specs:** The prompt entry for `fluid_prose` in `src/cresmo/infrastructure/resources/prompts.json` contains hundreds of hardcoded lines copy-pasting the contents of `cresmo-style-guide/SKILL.md` and `cresmo-fluid-prose/SKILL.md`.
2. **Violation of Single Source of Truth (SSOT):** When updates, refinements, or style calibrators modify `.agents/skills/cresmo-style-guide/SKILL.md` or `.agents/skills/cresmo-fluid-prose/SKILL.md`, those modifications are silently decoupled from `fluid_prose` generation. The generator continues using the stale, hardcoded JSON strings.
3. **Single Skill Name Inflexibility:** In `JsonPromptProvider._format_paired_prompt` and `_get_skill_block(skill_name)`, the system only loads a single skill specified by string (`"skill_name": "..."`). However, authorial prose generation requires composing the **cross-cutting domain style guide** (`cresmo-style-guide`) with the **stage-specific operational contract** (`cresmo-fluid-prose`).

---

## 2. Decision

We establish dynamic multi-skill resolution in `JsonPromptProvider` and refactor the `fluid_prose` prompt configuration in `prompts.json` to adhere to strict Single Source of Truth (SSOT) dynamics.

### 2.1 Multi-Skill Block Resolution in `JsonPromptProvider`
We enhance `JsonPromptProvider` to support either a single skill name (`"skill_name": "cresmo-fluid-prose"`) or an ordered array of skill names (`"skills": ["cresmo-style-guide", "cresmo-fluid-prose"]`):
1. When `"skills"` is specified, `JsonPromptProvider` iterates through each skill, fetches its cached markdown content, and concatenates them with distinct boundary headers.
2. Backwards compatibility: If `"skill_name"` is provided as a scalar string, it resolves identically as before.

### 2.2 Template Decoupling in `prompts.json`
We refactor the `fluid_prose` entry in `prompts.json` to:
1. Declare `"skills": ["cresmo-style-guide", "cresmo-fluid-prose"]`.
2. Utilize dynamic template interpolation:
   ```json
   "system_instruction": "{task}\n\n{skill_block}\n..."
   ```
3. Remove the redundant hardcoded copies of Section I (Style Pillars), Section II (Literary DNA), and Section IV (Anti-Patterns), replacing them with the dynamic `{skill_block}` injection.
4. Keep the explicit Stage 1 execution invariants, mechanical contracts (zero em-dashes, affirmative syntax, line-start invariants), and user transcript wrapper intact.

---

## 3. Causal Chain & Consequences

```
.agents/skills/cresmo-style-guide/SKILL.md  ──┐
                                              ├──► JsonPromptProvider._get_skill_block() ──► Gemini System Instruction
.agents/skills/cresmo-fluid-prose/SKILL.md   ──┘
```

### Positive Consequences
- **True SSOT:** Edits to style guides or operational skills immediately propagate to prompt generation without manual synchronization in JSON files.
- **Maintainability:** Removes hundreds of redundant lines from `prompts.json`.
- **Cognitive Consistency:** Both `fluid_prose` and downstream stages share the identical programmatic skill composition mechanism.

### Negative / Mitigated Consequences
- **Token Footprint:** Markdown files are embedded verbatim. Mitigated by `_skill_cache` in-memory caching and concise skill markdown documentation.

---

## 4. Compliance & Verification
- **Unit Tests:** Verified in `tests/cresmo/unit/test_prompt_provider.py` asserting that `provider.get_prompt(PromptKey.FLUID_PROSE, ...)` incorporates both `cresmo-style-guide` and `cresmo-fluid-prose` markdown contents.
- **Fail-Fast Invariants:** Missing skill directories or empty files gracefully fall back without breaking execution.
