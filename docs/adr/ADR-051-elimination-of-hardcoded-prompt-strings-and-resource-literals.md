# ADR-051: Elimination of Hardcoded Prompt Strings, Magic Resource Literals, and Settings Injection Alignment

## Status
Accepted

## Context
ADR-011 mandates zero hardcoded prompts in Python source files and zero scattered magic strings.
However:
1. `src/cresmo/infrastructure/adapters/prompts/builders.py` retained legacy multi-line prompt strings in `if not template and not system_template:` fallback branches across builders (`build_fluid_prose`, `build_gap_filler`, `build_long_expander`, `build_wide_expander`, `build_atomic_inventory`, `build_atomic_batch`, `build_reconcile_mocs`).
2. `src/cresmo/infrastructure/adapters/prompts/json_provider.py` hardcoded resource names (`"cresmo.infrastructure.resources"`, `"prompts.json"`), ignored `settings.prompts_path` and `settings.skills_dir`, and hardcoded `"pt-BR"` fallback instead of `CresmoSettings.DEFAULT_LANGUAGE`.
3. `_get_skill_block` format in `json_provider.py` diverged from canonical skill delimiter contract (`--- SKILL SPECIFICATION ({skill_name}) ---`), breaking 3 unit tests.

## Decision
1. **Purge Inline Prompts in `builders.py`**: Remove all `if not template and not system_template:` fallback branches. Builders must uniformly delegate to `_format_paired_prompt` / `_format_single_prompt`, relying exclusively on centralized `prompts.json` or Langfuse.
2. **SSOT Constants in `config.py`**:
   - `DEFAULT_PROMPTS_RESOURCE_PACKAGE: str = "cresmo.infrastructure.resources"`
   - `DEFAULT_PROMPTS_RESOURCE_NAME: str = "prompts.json"`
3. **Settings Alignment in `JsonPromptProvider`**:
   - Resolve `prompts_path` from `prompts_path or getattr(settings, "prompts_path", None)`.
   - Resolve `skills_dir` from `skills_dir or getattr(settings, "skills_dir", None)` before candidate path discovery.
   - Fall back to `CresmoSettings.DEFAULT_LANGUAGE` instead of hardcoded `"pt-BR"`.
4. **Restore Canonical Skill Delimiters**: Ensure `_get_skill_block` wraps content with:
   ```
   \n\n--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n--- END SKILL SPECIFICATION ---\n
   ```

## Consequences
- Strict compliance with ADR-011 and ADR-050.
- Zero raw prompt strings in Python source files.
- 100% test pass across `tests/cresmo/unit/test_prompt*`.
