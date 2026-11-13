# ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown-Aware Checkpointing

**Status:** ACCEPTED  
**Date:** 2026-11-13  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Related ADRs:** [`ADR-010`](ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-029`](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), [`ADR-039`](ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md), [`ADR-041`](ADR-041-gemini-credential-pool-and-quota-failover.md), [`ADR-060`](ADR-060-gap-filler-judge-criteria-v2.md)

---

## 1. Context & Architectural Motivation

Previously, offline calibration of Cresmo LLM judges lived in two duplicated per-stage scripts (`scripts/fluid_prose/llm_judge/calibrate.py` and `scripts/gap_filler/llm_judge/calibrate.py`) with dangerous divergence:
1. **Metrological Contamination via Silent Fallback:** `scripts/fluid_prose/llm_judge/calibrate.py` instantiated `build_llm_judge_adapter(settings=settings)` with default `enable_fallback=True`. When Gemini API keys hit HTTP `429` or `503`/`504`, evaluations silently failed over to the fallback judge while labeling the resulting metrics under the Gemini model name.
2. **Duplicated CLI & SDT Boilerplate:** Confusion matrix / SDT math, cooldown handling, and report formatting were duplicated across two ~900–1300 line scripts with drifting CLI flags.
3. **Wasted Quota Across Partial Failures & Multi-Stage Runs:** When a model exhausted RPD quota mid-dataset (e.g., item 34/42 or 25/49), re-running started from item 1, burning scarce free-tier requests and triggering repeated cooldown locks across stages sharing the same `(provider, model)` quota pool.

---

## 2. Decision

We consolidate judge calibration into a single zero-fallback, checkpoint-resumable CLI entrypoint: [`scripts/calibrate_judges.py`](../../scripts/calibrate_judges.py), and permanently delete the legacy per-stage `calibrate.py` scripts in accordance with ADR-010 (Zero Legacy Shims).

### 2.1 Canonical Stage Registry (`STAGE_SPECS`)
All calibrated stages (`fluid_prose`, `gap_filler`) are parameterized uniformly through an immutable `StageCalibrationSpec` mapping:
- `stage_name`, `required_criteria`, `golden_set_path`, `langfuse_dataset_name`, `report_dir`, `default_threshold`, `passing_accuracy_gate`, and `seed_items`.
- **Default Behavior (Zero Mandatory Flags):** Invoking `uv run python scripts/calibrate_judges.py` runs **all registered stages** (`fluid_prose`, `gap_filler`) sequentially against **all configured benchmark models** (`CresmoSettings().judge_calibration_models`).
- Users may narrow scope optionally via `--stage` / `--stages` and `--model` / `--models` (both repeated flags and comma-separated values supported).

### 2.2 Unconditional Zero-Fallback Invariant
- `build_llm_judge_adapter(..., enable_fallback=False)` is enforced **unconditionally** for every `(stage, provider, model)` execution. Calibration must measure only the target model or fail/cooldown explicitly.

### 2.3 Cooldown-Aware Incremental JSON Checkpointing (SOTA-KISS Default)
With zero opt-in/opt-out toggle flags, calibration ALWAYS persists state to JSON under `data/calibration_checkpoints/`:
- **Incremental State per `(stage, provider, model)`:**
  - `config_hash` (`sha256` of dataset items, stage prompt system template, scoring threshold, and required criteria).
  - Completed per-item verdicts keyed by `item_id`, flushed atomically on disk after every evaluated item.
  - `cooldown_until` (UTC Unix timestamp) tracked both per `(stage, provider, model)` and per shared `(provider, model)` quota key.
- **Deterministic Resume & Cooldown Rules:**
  1. **First run / hash mismatch:** Starts cleanly from item 1 (`config_hash` change auto-invalidates stale cached items when golden sets or prompts evolve).
  2. **Always resume from previous point:** Replays already-evaluated item verdicts from JSON with zero LLM calls and continues strictly from the first unevaluated item. If all items for `(stage, provider, model)` already completed under the current `config_hash`, generates the report with zero redundant API calls.
  3. **Short cooldown (`retry_after <= max_retry_wait`, e.g., RPM/TPM window):** Sleeps `retry_after` + 1s buffer and retries the same item immediately.
  4. **Long cooldown (`retry_after > max_retry_wait`, e.g., daily RPD exhaustion):** Atomically saves completed partial progress and records `cooldown_until = now + retry_after`. Immediately marks the current `(stage, model)` — and any subsequent `(stage, model)` sharing that exhausted `(provider, model)` in the queue — as `COOLDOWN` without wasting quota.
  5. **Restart before cooldown expiry:** Detects `now < cooldown_until` in JSON and skips with `COOLDOWN` immediately; restarting after `cooldown_until` passes clears the cooldown and resumes incrementally from the exact next item.

---

## 3. Consequences

- **Positive:** Zero fallback contamination across all stages; zero wasted RPD quota on restarts; single 12-Factor CLI aligned with ADR-010/ADR-039/ADR-060; clean cross-stage summary table.
- **Negative / Trade-offs:** Previous stage paths (`scripts/{fluid_prose,gap_filler}/llm_judge/calibrate.py`) are removed outright (no backward-compatible wrappers), requiring docs and test imports to point directly to `scripts/calibrate_judges.py`.

