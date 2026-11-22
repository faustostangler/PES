# ADR-046: Unified State-Driven Gap Filler Prompt

**Status:** ACCEPTED  
**Date:** 2026-10-25  
**Decision Makers:** Lead Architect (Fausto Stangler)  
**Related ADRs:** [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-040`](ADR-040-dynamic-cross-cutting-skill-block-composition.md), [`ADR-065`](ADR-065-hierarchical-stage-scoped-telemetry-nomenclature.md), [`ADR-066`](ADR-066-hybrid-semantic-saturation-and-text-embedding-adapters.md)

> [!NOTE]
> **Refinement (`ADR-066`):** Copy-back saturation exit (*"return the draft unchanged"*) and `check_complementary_mechanical_saturation` are superseded. `REFINE` mode emits `<NO_NEW_GAPS/>` on saturation, `stage_execution.py` tracks `baseline_text` from Pass 1 and restores it via `SaturationVerdict.preserve_baseline`, and `HybridSaturationEvaluator` drives convergence.

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
- `generate_stage_candidate` (`src/cresmo/application/pipeline/stage_execution.py`) executes a single SOTA-KISS loop (`for pass_index in range(1, max_passes + 1)`) driven purely by `previous_text: str | None` (`None` on pass 1 $\to$ BUILD; `previous_text` present on passes 2..N $\to$ REFINE with `<draft pass="N-1">`) and delegates early halting exclusively to `stage_config.saturation_policy(current_text, previous_text)` (Null-Object default `never_saturate`, zero redundant `early_stopping_enabled` flag or loop-level pass-1 guard), while scoping telemetry per pass (`active_telemetry_pass(pass_index)`, ADR-065).
- `prompts.json` (`gap_filler`), `build_gap_filler`, and `LangfusePromptProvider` preserve `{{raw_text}}{{draft_section}}` plus `source_text`, injecting explicit BUILD/REFINE system directives; `StageConfig.build_transform_prompt` enforces fail-safe `<draft pass="N-1">` appending whenever a remote or custom prompt template omits `current_text`.
- **Final-Pass Reflection Critique Invariant:** When a closed-loop retry (`ADR-031`) supplies a non-empty `critique`, `generate_stage_candidate` injects it strictly on the **final pass** (`pass_index == max_passes`, or a single terminal critique-directed pass immediately following early mechanical saturation at `pass_index < max_passes`), leaving earlier constructive passes undisturbed without ever dropping judge feedback or wasting intermediate passes.
- `PipelineStageRunner` reuses `stage_config.transform_prompt_key` for every pass.
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
