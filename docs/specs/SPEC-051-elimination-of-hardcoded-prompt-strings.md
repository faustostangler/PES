# SPEC-051: Elimination of Hardcoded Prompt Strings and Settings Alignment

**Status:** ACCEPTED  
**Date:** 2026-11-05  
**Governing ADR:** [`ADR-051`](../adr/ADR-051-elimination-of-hardcoded-prompt-strings-and-resource-literals.md)  
**Domain Layer:** `cresmo.infrastructure.adapters.prompts`, `cresmo.infrastructure.config`

---

## 1. Specification Requirements

1. **Zero Inline Fallback Strings (`builders.py`):**
   - `build_fluid_prose`, `build_gap_filler`, `build_long_expander`, `build_wide_expander`, `build_atomic_inventory`, `build_atomic_batch`, and `build_reconcile_mocs` must contain zero hardcoded multi-line prompt string fallbacks.
   - All builders delegate directly to `_format_paired_prompt` / `_format_single_prompt`.
2. **SSOT Resource Constants (`config.py`):**
   - `DEFAULT_PROMPTS_RESOURCE_PACKAGE = "cresmo.infrastructure.resources"`
   - `DEFAULT_PROMPTS_RESOURCE_NAME = "prompts.json"`
3. **Settings Alignment (`json_provider.py`):**
   - `JsonPromptProvider` resolves `prompts_path` and `skills_dir` from injected `CresmoSettings` before fallback path resolution.
   - Skill blocks are delimited with `--- SKILL SPECIFICATION ({skill_name}) ---` and `--- END SKILL SPECIFICATION ---`.

