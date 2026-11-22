# SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation

- **Related ADR:** [ADR-071](../adr/ADR-071-langfuse-mirrored-prompt-resources-cohesion-and-taxonomy-relocation.md)
- **Status:** Accepted
- **Date:** 2026-11-22

---

## 1. Taxonomy Adapter Relocation

- **New Module:** `src/cresmo/infrastructure/adapters/taxonomy/json_taxonomy_adapter.py` exporting `TaxonomyCatalog`, `load_taxonomy_catalog`, and `JsonTaxonomyCatalogAdapter`.
- **Package Export:** `src/cresmo/infrastructure/adapters/taxonomy/__init__.py`.
- **Deleted Module:** `src/cresmo/infrastructure/adapters/prompts/taxonomy_catalog.py`.
- **Updated Callers:** `bootstrap/factories/adapter_factory.py`, `infrastructure/adapters/media/native_media_ingestion_adapter.py`, `tests/cresmo/unit/domain/test_taxonomy.py`, and dedicated `tests/cresmo/unit/infrastructure/test_json_taxonomy_adapter.py`.

---

## 2. Langfuse-Mirrored Resource Layout

- **Manifest (`src/cresmo/infrastructure/resources/prompts.json`):** Maps each of the 18 `PromptKey` values to `PromptManifestEntry(description: str, type: Literal["chat"] = "chat", skills: list[str] = [], langfuse_slug: str | None = None)` with `extra="forbid"`. Inline `system_prompt` and `user_prompt` keys are strictly rejected.
- **Markdown Templates (`src/cresmo/infrastructure/resources/prompts/<key>/{system,user}.md`):** 36 UTF-8 LF files plus `src/cresmo/infrastructure/resources/prompts/__init__.py`.
- **Catalog Loader (`catalog.py`):**
  - `load_prompt_catalog(path: Path | None = None) -> PromptCatalog` loads `prompts.json` and sibling `prompts/<key>/{system,user}.md` (via `importlib.resources` when `path is None`, or filesystem relative to `path.parent / "prompts"` when provided).
  - Raises `PromptCatalogError` fail-fast on missing keys, unknown keys, missing `system.md`/`user.md`, or orphan directories under `prompts/` not matching `PromptKey`.

---

## 3. Cohesive Prompt Components (`src/cresmo/infrastructure/adapters/prompts/`)

### 3.1 `skill_loader.py` (`SkillDocumentLoader`)
- Resolves `skills_dir` (explicit or repo `.agents/skills`).
- Reads `<skill_name>/SKILL.md`, strips leading YAML frontmatter (`^---\n.*?\n---\s*`), caches contents in memory.
- `build_skill_replacements(skills, templates)` returns `dict[str, str]` containing `{{<skill_name>}}` replacements and `skill_block` containing only skills not explicitly referenced inline in templates.

### 3.2 `template_renderer.py` (`TemplateRenderer`)
- Single compiled Mustache regex `\{\{\s*([a-zA-Z0-9_\-]+)\s*\}\}`.
- `render(template: str, variables: Mapping[str, str]) -> str` substitutes matched keys, preserves unmatched `{{...}}` placeholders, and leaves single-brace JSON objects (`{"title": "..."}`) untouched.

### 3.3 `context_normalizer.py` (`PromptVariableSchema`, `normalize_prompt_context`)
- `PROMPT_VARIABLE_SCHEMAS: Mapping[PromptKey, PromptVariableSchema]` validated bijectively against `PromptKey` at module load.
- `normalize_prompt_context(key: PromptKey, context: Mapping[str, Any], *, default_language: str) -> dict[str, str]`:
  - Coerces `ChannelName` values to `str`.
  - Resolves `language` with precedence: explicit non-empty `context["language"]` -> `default_language`.
  - Resolves `content_title` from `context["content_title"]` or alias `context["title"]`.
  - Computes `GAP_FILLER` variables: `raw_text` (from `source_text` or `raw_text`), `pass_num`, `prev_pass_num = max(0, int(pass_num) - 1)`, `draft_section = f'\n<draft pass="{prev_pass_num}">\n{current_text}\n</draft>\n' if current_text else ""`.
  - Applies declarative aliases (`WIDE_EXPANDER`: `text` from `current_text` or `text`; `JUDGE_RAW_INDEX_SYNTHESIS`: `summary` from `transcript_excerpt` or `summary`).
  - Preserves both `system.md` and `user.md` for all 18 prompts, fixing `RAW_INDEX_CONCEPTS_REWRITE`.

---

## 4. Provider & Presentation Wiring

- `JsonPromptProvider` composes `PromptCatalog`, `SkillDocumentLoader`, `TemplateRenderer`, and `normalize_prompt_context`.
- `LangfusePromptProvider` delegates all context normalization to `normalize_prompt_context`, preserving ADR-026 Rule 19 lazy fallback and `prompt_name`/`prompt_version` metadata.
- `builders.py` deleted (ADR-010).
- `seed_prompts.py` constructs catalog/provider via `bootstrap/factories/adapter_factory.py` helpers (`build_local_prompt_provider`, `load_local_prompt_catalog`).
