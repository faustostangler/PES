# ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation

- **Status:** Accepted
- **Date:** 2026-11-22
- **Refines:** ADR-052 (Langfuse Chat-Native Prompt Catalog & Local JSON Fallback)
- **Deletes:** `src/cresmo/infrastructure/adapters/prompts/taxonomy_catalog.py`, `src/cresmo/infrastructure/adapters/prompts/builders.py` (ADR-010 Zero Legacy Shims)

---

## 1. Context

Audit of `src/cresmo/infrastructure/adapters/prompts/` (1,402 lines) and `src/cresmo/infrastructure/resources/prompts.json` (49.6 KB) exposed four structural defects:

1. **Misplaced Adapter (`taxonomy_catalog.py`):** `JsonTaxonomyCatalogAdapter` implements `ChannelTaxonomyPort` (domain taxonomy classification), unrelated to LLM prompt provisioning.
2. **Monolithic Single-Line Prompt Corpus (`prompts.json`):** Embedding 18 multi-thousand-character system and user prompts as `\n`-escaped JSON strings degrades diff readability, code review of LLM rubrics, and maintenance ergonomics.
3. **Context Normalization Drift (Local vs Remote):** `GAP_FILLER` (`<draft pass="...">`) and `ChannelName` coercion were duplicated between `builders.py` and `langfuse_provider.py`, creating silent drift risk between Langfuse Cloud compilation and local fallback rendering. Additionally, `builders.py` (382 lines) invoked private `_format_paired_prompt`/`_format_single_prompt` methods and silently dropped the 987-char `system_prompt` of `RAW_INDEX_CONCEPTS_REWRITE`.
4. **Overloaded `json_provider.py` (405 lines):** Conflated catalog loading, `.agents/skills/*/SKILL.md` reading/frontmatter stripping/caching, and two separate template substitution engines (`_safe_format` vs `_replace_template_tags`).

---

## 2. Decision

1. **Relocate Taxonomy Adapter:** Move `JsonTaxonomyCatalogAdapter` and `load_taxonomy_catalog` to `src/cresmo/infrastructure/adapters/taxonomy/json_taxonomy_adapter.py` (exported via `adapters/taxonomy/__init__.py`) and remove taxonomy re-exports from `adapters/prompts/`.
2. **Langfuse-Mirrored Markdown Resources:** Slim `src/cresmo/infrastructure/resources/prompts.json` to a lightweight SSOT manifest (`description`, `type: "chat"`, `skills`, optional `langfuse_slug`; `extra="forbid"`, rejecting inline `system_prompt`/`user_prompt`). Store all 18 canonical chat turns in 36 UTF-8 LF Markdown files under `src/cresmo/infrastructure/resources/prompts/<key>/{system,user}.md` with `prompts/__init__.py` for `importlib.resources` traversal and wheel packaging.
3. **Cohesive Prompt Pipeline Components:**
   - `SkillDocumentLoader` (`skill_loader.py`): Resolves `skills_dir`, strips YAML frontmatter, caches `SKILL.md` bodies in memory, and builds `{{<skill-name>}}` and `{{skill_block}}` replacements.
   - `TemplateRenderer` (`template_renderer.py`): Single compiled Mustache `{{variable}}` regex engine preserving literal JSON braces (`{"title": "..."}`) and unmatched placeholders intact.
   - `PromptVariableSchema` & `PromptContextNormalizer` (`context_normalizer.py`): Declarative bijective mapping covering all 18 `PromptKey` values, unifying `ChannelName` coercion, `language` precedence, `content_title`/`title` aliasing, `GAP_FILLER` `<draft pass="N-1">` generation, stage aliases, and full `system.md` + `user.md` rendering for `RAW_INDEX_CONCEPTS_REWRITE`.
4. **Zero Legacy Shims (ADR-010):** Delete `builders.py` and `taxonomy_catalog.py`. Both `JsonPromptProvider` and `LangfusePromptProvider` delegate variable normalization to `normalize_prompt_context()`, guaranteeing 100% local/remote variable parity. Wire `seed_prompts.py` prompt provider construction through `bootstrap/factories/adapter_factory.py` so Presentation has zero direct `infrastructure.adapters.prompts` imports.

---

## 3. Langfuse Ingestion Strategy

- **1:1 Chat-Native Parity:** Each `<key>` in `prompts.json` paired with `prompts/<key>/system.md` and `prompts/<key>/user.md` maps directly to `client.create_prompt(name=spec.langfuse_name, type="chat", prompt=[{"role": "system", "content": ...}, {"role": "user", "content": ...}])`.
- **Mustache Syntax Canon:** All 36 Markdown templates exclusively use double-brace Mustache `{{variable}}` syntax compatible with Langfuse `prompt.compile(**variables)` and local `TemplateRenderer.render(...)`.
- **Skill Embedding Boundary:** During `cresmo seed-prompts`, `JsonPromptProvider.get_chat_prompt_template(key)` resolves static `{{description}}`, `{{skill_block}}`, and `{{<skill-name>}}` tokens while preserving runtime Mustache variables (`{{raw_text}}`, `{{draft_section}}`, `{{language}}`, etc.) intact for remote Langfuse compilation. On local fallback (`JsonPromptProvider.get_prompt`), the exact same `SkillDocumentLoader` + `TemplateRenderer` + `normalize_prompt_context` pipeline runs locally.
- **Telemetry Traceability:** `LangfusePromptProvider` preserves `prompt_name` and `prompt_version` metadata on `ChatPrompt` and maintains ADR-026 Rule 19 lazy degradation (zero fallback execution on happy path).

---

## 4. Consequences

- **Positive:** Human-reviewable Markdown diffs for every LLM rubric; mathematically enforced 1:1 variable parity between Langfuse Cloud and local fallback; ~45% reduction in Python boilerplate (`builders.py` eliminated); clean `adapters/taxonomy/` Bounded Context separation; bug fix restoring `RAW_INDEX_CONCEPTS_REWRITE` system prompt.
- **Trade-offs:** Custom test overlays for `load_prompt_catalog(path=...)` must provide sibling `prompts/<key>/{system,user}.md` files alongside the manifest JSON.
