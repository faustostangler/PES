# SPEC-040: Dynamic Cross-Cutting Skill Block Composition and Cresmo Style Guide Embedding

**Status:** APPROVED  
**Date:** 2026-10-13  
**Originating ADR:** [`docs/adr/ADR-040-dynamic-cross-cutting-skill-block-composition.md`](../adr/ADR-040-dynamic-cross-cutting-skill-block-composition.md)  
**Governing Method:** Doctor Stangler Architecture Method (TDD Red-Green-Refactor, Hexagonal/Clean Architecture, Fail-Fast)  

---

## 1. Domain Requirements & Invariants

1. **Multi-Skill Resolution in JsonPromptProvider:**
   - `JsonPromptProvider` must support both scalar `"skill_name": "..."` and array `"skills": ["skill_1", "skill_2", ...]` in `prompts.json` templates.
   - When resolving `{skill_block}`, if `"skills"` is specified, it must generate consecutive formatted blocks for each skill in declared order:
     ```
     --- SKILL SPECIFICATION (skill_1) ---
     <skill_1 markdown content>

     --- SKILL SPECIFICATION (skill_2) ---
     <skill_2 markdown content>
     ```
   - If `"skills"` is absent or empty, it falls back to `"skill_name"`.
   - If neither is provided, `{skill_block}` resolves to an empty string `""`.

2. **Stage 1 (Fluid Prose) Template Decoupling:**
   - In `src/cresmo/infrastructure/resources/prompts.json`, the `"fluid_prose"` entry must declare:
     ```json
     "skills": ["cresmo-style-guide", "cresmo-fluid-prose"]
     ```
   - The `system_instruction` of `"fluid_prose"` must begin with `{task}\n\n{skill_block}`.
   - Static duplication of `cresmo-style-guide` pillars and DNA in the JSON is purged, preserving only stage-specific mechanical execution invariants (zero em-dashes, affirmative syntax, line-start invariants, enumeration serialization contract, and Stage 1 boundary contract).
   - In `src/cresmo/infrastructure/adapters/prompts/builders.py`, `build_fluid_prose` must resolve `skill_block` using the provider's multi-skill capability for fallback mode as well.

---

## 2. Test Specifications (Refractometry - Phase 2)

### Test 1: Unit Test - Multi-Skill Block Resolution in `JsonPromptProvider`
- **Location:** `tests/cresmo/unit/test_prompt_provider.py`
- **Scenario:** Provider receives a template specifying `"skills": ["skill-a", "skill-b"]`.
- **Expected Behavior:** `provider.get_raw_prompt_template(key)` contains both `--- SKILL SPECIFICATION (skill-a) ---` and `--- SKILL SPECIFICATION (skill-b) ---` along with their contents.

### Test 2: Unit Test - Fluid Prose Prompt Embeds Cresmo Style Guide and Fluid Prose Markdown
- **Location:** `tests/cresmo/unit/test_prompt_provider.py`
- **Scenario:** Default `JsonPromptProvider` calls `get_prompt(PromptKey.FLUID_PROSE, ...)`.
- **Expected Behavior:**
  - `prompt.system_instruction` contains `--- SKILL SPECIFICATION (cresmo-style-guide) ---`.
  - `prompt.system_instruction` contains `--- SKILL SPECIFICATION (cresmo-fluid-prose) ---`.
  - `prompt.system_instruction` contains the Literary DNA references from the markdown file (`Daniel Dennett`, `Emil Cioran`, `Friedrich Nietzsche`, `Jorge Luis Borges`, `Nassim Nicholas Taleb`).
  - `prompt.get_last_user_content()` contains the verbatim transcript payload.

---

## 3. Implementation Plan (Surgery - Phase 3)

1. **Red Phase:**
   - Add new tests in `tests/cresmo/unit/test_prompt_provider.py` covering multi-skill resolution and `FLUID_PROSE` skill block embedding. Verify failure (Red).
2. **Green Phase:**
   - Update `JsonPromptProvider._resolve_skill_block_from_entry(entry)` in `json_provider.py`.
   - Update `build_fluid_prose` in `builders.py` to use `_resolve_skill_block_from_entry`.
   - Update `"fluid_prose"` in `src/cresmo/infrastructure/resources/prompts.json` to use `"skills": ["cresmo-style-guide", "cresmo-fluid-prose"]` and `{task}\n\n{skill_block}`.
   - Verify tests pass (Green).
3. **Refactor Phase:**
   - Run full unit test suite and mutation/lint check.
