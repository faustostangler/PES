# ADR-060: Gap Filler Judge Criteria v2 and Stage Scoring Policy Wiring

**Status:** ACCEPTED  
**Date:** 2026-11-12  
**Decision Makers:** Lead Architect (Fausto Stangler)  
**Related ADRs:** [`ADR-029`](ADR-029-unified-llm-judge-port-and-resilient-adapters.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-039`](ADR-039-fluid-prose-canonical-judge-criteria.md), [`ADR-046`](ADR-046-unified-state-driven-gap-filler-prompt.md)

---

## 1. Context

The `cresmo-gap-filler` skill (`SKILL.md`) evolved into four explicit analytical axes (A: Cognitive & Mechanical Decomposition, B: Braudelian Causal Stratification, C: Genealogy, Relational Networks & Hidden Agency, D: Epistemology, Evidence & Analysis of Competing Hypotheses) plus strict Passo 2 linear-prose and `### Extra Info` saturation rules.

The previous 5-criterion `gap_filler` judge rubric (`factual_grounding`, `socratic_epistemic_depth`, `causal_stratification_agency`, `complementary_substance`, `authorial_naturalism`) and unused `epistemic_saturation` enum member suffered from three defects:

1. **Rubric drift:** Referenced legacy "6 dimensions" Socratic analysis while omitting A1 operational boundaries, D1 fact/model segregation, C1 precursor tracking, C3 *Cui Bono* / intent-hypothesis framing, D5 Popperian falsification / ACH, and Passo 2 linearity / restricted vocabulary checks.
2. **Overly narrow `### Extra Info` definition:** Restricted entries to treaties and mini-biographies rather than saturation-level high-granularity specifics.
3. **Broken runtime scoring policy:** `GeminiJudgeAdapter`, `OllamaJudgeAdapter`, and `TypeSafeJudgeAdapter` called `JudgeEvaluation.create_with_composite_verdict` without `weights` or `veto_criteria`, silently falling back to `DEFAULT_FLUID_PROSE_WEIGHTS` (uniform `1.0` weights) and `DEFAULT_MECHANICAL_VETO_CRITERIA` (`SEMANTIC_FAITHFULNESS`, `NER_PRESERVATION`), so `gap_filler` mechanical vetoes never fired in production code.

---

## 2. Decision

Replace the legacy `gap_filler` criteria without backwards compatibility with **7 orthogonal `JudgeCriterion` members**:

1. `epistemic_grounding_segregation` (weight `0.20`, **Mechanical Veto**)
2. `conceptual_mechanical_decomposition` (weight `0.15`)
3. `braudelian_stratification` (weight `0.15`)
4. `genealogy_hidden_agency` (weight `0.15`)
5. `competing_hypotheses` (weight `0.15`)
6. `extra_info_granularity` (weight `0.10`, **Mechanical Veto**)
7. `linear_style_naturalism` (weight `0.10`)

Introduce a pure domain policy resolver `resolve_stage_scoring_policy(stage_name)` in `cresmo.domain.value_objects.quality` returning `(weights, veto_criteria)` for `gap_filler` vs. `fluid_prose`/default stages, and wire all three judge adapters (`GeminiJudgeAdapter`, `OllamaJudgeAdapter`, `TypeSafeJudgeAdapter`) plus `MechanicalPreflightJudgeDecorator` to use it.

Align `judge_gap_filler` in `prompts.json` with the gold-standard structure of `judge_fluid_prose` (declared `skills`, `CRITICAL FAILURE (score=0.0, passed=false)` hard gates, `STRICT ... INVARIANT`s, identical JSON schema and `user_prompt`).

---

## 3. Consequences

**Positive**
- 1-to-1 coverage of all four `cresmo-gap-filler` axes (A, B, C, D), Passo 2 linearity, and `cresmo-style-guide` bans.
- `GAP_FILLER_CANONICAL_WEIGHTS` and `GAP_FILLER_MECHANICAL_VETO_CRITERIA` are enforced uniformly across Gemini, Ollama, and TypeSafe judges without duplicating `if stage_name == "gap_filler"` logic.
- Clean removal of legacy criteria and orphan `EPISTEMIC_SATURATION` eliminates dead branches.

**Negative / Migration**
- Existing `scripts/gap_filler/golden_sets/gap_filler_golden_set.json` and calibration modules (`scripts/gap_filler/llm_judge/criterion_*.py`) must be regenerated for the 7 new criteria (49 items: 7 criteria × 7 cases).
- Any external Langfuse prompt `judge_gap_filler` / `cresmo-gap-filler` must be re-seeded.

