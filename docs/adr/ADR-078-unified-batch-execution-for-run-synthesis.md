# ADR-078: Unified Batch Execution for RunSynthesisUseCase

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Principal Socio-Technical Architect (Fausto Stangler / Antigravity)
- **Refines:**
  - Refines `ADR-067` (Humble Presentation CLI and Run/Sync Use Cases)
  - Aligns with `ADR-035` (Atomic Work-Item Traces & SOTA-KISS Batch Correlation)
  - Aligns with `ADR-010` (Zero Legacy Shims & Streaming-First Unification)

---

## 1. Context

`RunSynthesisUseCase` (`src/cresmo/application/use_cases/run_synthesis.py`) previously bifurcated execution into two separate paths:
1. `_execute_single_video` when `request.url` was provided (`mode="single"`), with 5 dedicated `single_*` fields on `RunSynthesisOutcome`, no `BatchId` generation, no per-item `_drain_telemetry_and_memory` cleanup, and a separate `_render_outcome` branch in `presentation/commands/run.py`.
2. `_execute_batch` for all other invocations (`mode="batch"`).

Maintaining two orchestration and rendering paths for 1 vs. N items duplicated dry-run, error-handling, and summary logic while leaving single-URL runs without `batch_id` correlation (`ADR-035`).

---

## 2. Decision

We will treat `request.url` as a 1-item batch (`[BatchSource(kind=SourceModality.URL, target=request.url)]`) routed through the unified batch dry-run and batch execution pipelines because a single uniform execution and output contract eliminates duplicated branching, ensures `BatchId` correlation on every run, and simplifies both `RunSynthesisUseCase` and `presentation/commands/run.py`.

Specifically:
1. Remove `_execute_single_video` from `RunSynthesisUseCase`.
2. Remove `mode` and all `single_*` fields (`single_stages_completed`, `single_final_chars`, `single_content_id`, `single_dry_run_chars`, `single_dry_run_url`) from `RunSynthesisOutcome`.
3. When `request.url` is truthy, construct `[BatchSource(kind=SourceModality.URL, target=request.url)]` directly in `RunSynthesisUseCase.execute()` and dispatch to `_execute_batch_dry_run` or `_execute_batch_run` (generating a `BatchId` and running `_drain_telemetry_and_memory` and `_consolidate_master` uniformly).
4. Remove the `if outcome.mode == "single":` branch from `_render_outcome` in `src/cresmo/presentation/commands/run.py`.

---

## 3. Domain Model & Observability Impact

- **Bounded Context:** Cresmo Application & Presentation (`RunSynthesisUseCase`, `commands/run.py`).
- **Value Objects:** `BatchId` is now always generated for every non-dry-run `RunSynthesisUseCase.execute()` invocation, including single-URL runs.
- **Observability:** Aligns 100% with `ADR-035` (`1 Trace = 1 Work Item` + `batch_id` metadata correlation).

---

## 4. Alternatives Considered

1. **Keep `mode="single"` and `mode="batch"` separate:** Rejected due to duplicated dry-run, master consolidation, and outcome rendering code, plus missing `batch_id` and memory/telemetry drain on single-URL runs.
2. **Pass `request.url` into `DiscoverBatchSourcesUseCase`:** Rejected because `RunSynthesisUseCase` already has the exact `BatchSource` in hand; constructing `[BatchSource(kind=SourceModality.URL, target=request.url)]` avoids unnecessary discovery I/O.

---

## 5. Consequences

- **Positive:** Single execution path, single `RunSynthesisOutcome` schema, single `_render_outcome` path, uniform `batch_id` correlation, and uniform GC/telemetry draining.
- **Neutral:** Single-URL CLI runs now emit `[1/1]` item events and `Batch Synthesis Summary [Batch: ...]:` instead of `Synthesis completed successfully for [...]`.
