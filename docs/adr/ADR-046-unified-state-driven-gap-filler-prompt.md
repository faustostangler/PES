# ADR-046: Unified State-Driven Gap Filler Prompt

**Status:** ACCEPTED  
**Date:** 2026-10-25  
**Decision Makers:** Lead Architect (Fausto Stangler)  
**Related ADRs:** [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-040`](ADR-040-dynamic-cross-cutting-skill-block-composition.md)

---

## 1. Context

The `gap_filler` stage used two prompt templates: `gap_filler` (pass 1) and `gap_filler_refine` (passes 2..N).

- Both `system_prompt` blocks shared ~80% of their rules and had already drifted ("6 dimensions" vs. "5 review cycles").
- `PipelineStageRunner` contained a stage-specific branch (`if stage_name == "gap_filler": GAP_FILLER_REFINE`), leaking domain knowledge into a generic runner.
- The refine builder fell back to the wrong skill (`cresmo-expander`), and `cresmo-style-guide` was never injected although both prompts required compliance with it.
- Neither prompt offered a legitimate exit when no verifiable gap remained, pushing the model to pad or invent latent ties that `judge_gap_filler` then vetoes under `factual_grounding`.

## 2. Decision

Collapse both templates into a single `gap_filler` prompt whose behaviour is driven by **draft state**, not by pass number.

1. **BUILD mode:** no `<draft>` block present (pass 1). The model creates the compendium from `<source_text>`.
2. **REFINE mode:** `<draft pass="N">` block present (passes 2..N). The model preserves verified content and only adds, deepens, or corrects.
3. **Saturation:** when no verifiable gap remains, the model returns the draft unchanged.
4. **Documented agency only:** latent ties are articulated only when historically documented; an acknowledged absence is preferred over an invented link.

Mechanics:

- `PromptKey.GAP_FILLER_REFINE`, its builder, registry metadata and JSON entry are removed.
- `build_gap_filler` renders `{draft_section}`: empty on pass 1, a `<draft pass="{prev}">` block afterwards. The fluid prose is therefore sent once per call.
- `PipelineStageRunner` reuses `stage_config.transform_prompt_key` for every pass.
- Placeholder `raw_text` is renamed `source_text` to match `judge_gap_filler`; `{language}` is added.
- The prompt declares `"skills": ["cresmo-style-guide", "cresmo-gap-filler"]`.
- XML-style delimiters replace `--- ... ---` blocks, which collided with YAML frontmatter in sources.

## 3. Consequences

**Positive**
- Single source of truth for gap filler rules; no further drift.
- Stage-agnostic runner; any future multi-pass stage works without code changes.
- Explicit saturation instruction complements `check_complementary_mechanical_saturation`.

**Negative / Risks**
- One template with two modes may make pass 1 less constructive. Mitigated by the explicit mode declaration and `Pass: {pass_num}/{total_passes}` header.
- Langfuse prompt `cresmo-gap-filler-refine` becomes obsolete and must be archived; `cresmo-gap-filler` requires reseeding.

**Validation**
- Unit tests cover BUILD/REFINE rendering, runner key reuse and registry removal.
- A/B run on `scripts/gap_filler/golden_sets/gap_filler_golden_set.json` comparing `judge_gap_filler` scores and passes-to-saturation is recommended before production promotion.
