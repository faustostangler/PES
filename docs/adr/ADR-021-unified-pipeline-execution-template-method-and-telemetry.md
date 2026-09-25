# ADR-021: Unified Pipeline Execution — SOTA-KISS Template Method, Single Root Span Telemetry, and Symmetrical Dispatchers

**Status:** PROPOSED  
**Date:** 2026-09-25  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md)

---

## 1. Context & Architectural Motivation

In the evolution of the Cresmo Knowledge Synthesis Engine, `CresmoPipeline` ([`src/cresmo/application/pipeline.py`](../../src/cresmo/application/pipeline.py)) was structured under [ADR-007](ADR-007-pipeline-template-method-dry.md) around a protected Template Method `_synthesize_transcript(raw, ...)` handling Stages 2 through 7 (Fluid Prose, Expansion, Inventory, Atomic Synthesis, MOC Reconciliation, Duplicate Unification).

Later, [ADR-013](ADR-013-iterative-llm-as-a-judge-indexing-loops.md) introduced Stage 1b (`IndexRawTranscriptsUseCase`), which extracts key concepts and generates paratactic catalog summaries verified via LLM-as-a-Judge loops. However, because `_synthesize_transcript` was already locked into Stages 2–7, `index_raw.execute(raw)` was bolted directly into the public ingestion methods `run_for_video` and `run_for_text_file`.

Furthermore, [ADR-016](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md) established OpenTelemetry and Langfuse session replays via `telemetry_port.start_pipeline_session(...)`, which was placed inside `_synthesize_transcript`.

### Architectural Flaws & Anti-Patterns Identified

1. **DRY & Template Method Violation:**
   Both `run_for_video` and `run_for_text_file` contain identical 8-line blocks executing `self.index_raw.execute(raw)` wrapped in identical `try/except` logging blocks. This violates GoF Template Method and DRY: entrypoints should only prepare input domain entities and delegate to a single orchestrator.

2. **Telemetry Session Fracture:**
   Because `start_pipeline_session` was inside `_synthesize_transcript`, Stage 1b (`index_raw`) executed *outside* the root trace span (`cresmo.pipeline.execution`). The iterative LLM-as-a-judge calls and Langfuse traces generated during catalog indexing were orphaned or severed from the execution tree, corrupting trace trees and session replays.

3. **Idempotency Bypass & Token Waste:**
   In the legacy layout, `self.index_raw.execute(raw)` was called in `run_for_video` *before* delegating to `_synthesize_transcript`, where the ledger idempotency check (`is_processed`) resided. If a transcript was already processed in the ledger, the pipeline still burned LLM tokens executing indexing before aborting at Stage 2.

4. **Cognitive Asymmetry & Violation of ADR-020 Pillar 3:**
   Per ADR-020 (Pillar 3: Universal Invocation KISS), core orchestrators should expose a canonical `.execute(...)` entrypoint accepting the domain aggregate. `_synthesize_transcript` was private and semantically incomplete (omitting Stage 1b), forcing callers to know internal staging details.

---

## 2. Decision

We establish a unified, symmetrical, and telemetry-complete Template Method architecture for `CresmoPipeline`:

```
+----------------------------------------------------------------------------------------------------+
|                                      INGESTION DISPATCHERS (THIN)                                  |
|                                                                                                    |
|    run_for_video(url) ---------\                                                                   |
|                                  +--->  CresmoPipeline.execute(raw: RawTranscript, ...)            |
|    run_for_text_file(path) -----/                                                                   |
+----------------------------------------------------------------------------------------------------+
                                                |
                                                v
+----------------------------------------------------------------------------------------------------+
|                        SINGLE ROOT TELEMETRY SPAN (cresmo.pipeline.execution)                      |
|                                                                                                    |
|  [0] Idempotency Guard (ledger_port.is_processed) ---- (Early exit if already processed)           |
|                                                                                                    |
|  [Stage 1b] stage1b_raw_indexing: self.index_raw.execute(raw)  <-- LLM-as-a-Judge nested in root  |
|  [Stage 2]  stage2_fluid_prose: fill_gaps_fluid_prose.execute(raw)                                |
|  [Stage 3]  stage3_expansion: expand_longitudinal_synchronic.execute(compendium)                   |
|  [Stage 4]  stage4_inventory: discover_atomic_inventory.execute(expanded_compendium)               |
|  [Stage 5]  stage5_atomic_batch: synthesize_atomic_batch.execute(inventory, expanded_compendium)   |
|  [Stage 6]  stage6_mocs: reconcile_mocs.execute()                                                  |
|  [Stage 7]  stage7_duplicate_unification: unify_duplicate_notes.execute()                          |
|                                                                                                    |
|  [Terminal] Ledger mark processed & record_session_coherence eval metric                           |
+----------------------------------------------------------------------------------------------------+
```

### 2.1 The Canonical Template Method: `execute(...)`
`CresmoPipeline` exposes a public canonical method:
```python
def execute(
    self,
    raw: RawTranscript,
    gap_filler_passes: int = 3,
    force_reprocess: bool = False,
    user: UserIdentity | None = None,
    entry: RawIndexEntry | None = None,
) -> PipelineResult:
```

### 2.2 Invariant Execution Ordering Inside Single Root Span
1. **Root Span Initialization:** Opens `telemetry_port.start_pipeline_session(...)` wrapping the entire pipeline lifecycle.
2. **Fail-Fast Idempotency Check:** Evaluates `ledger_port.is_processed(content_id)`. If processed and not `force_reprocess`, immediately returns `already_processed=True` without making any LLM calls.
3. **Stage 1b Child Span (`stage1b_raw_indexing`):** Executes `self.index_raw.execute(raw)` inside `with self.telemetry_port.start_stage_span("stage1b_raw_indexing"):`. If `entry` was pre-provided (e.g. in test doubles), it is reused; otherwise, indexing executes with failure-tolerant logging.
4. **Stages 2 through 7 Child Spans:** Sequentially executed within their respective child spans (`stage2_fluid_prose`, `stage3_expansion`, `stage4_inventory`, `stage5_atomic_batch`, `stage6_mocs`, `stage7_duplicate_unification`).
5. **Terminal Settlement:** Marks `ledger_port.mark_processed(content_id)` and records `telemetry_port.record_session_coherence(...)`.

### 2.3 Thin Symmetrical Dispatchers
- `run_for_video`: Warmed up, calls `ingest_raw_transcript.execute(video_url)`, validates non-null, and returns `self.execute(raw=raw, ...)`.
- `run_for_text_file`: Validates processable file, warms up, loads `RawTranscript`, persists to raw lake if outside lake, and returns `self.execute(raw=raw, ...)`.
- `_synthesize_transcript`: Retained as a thin pass-through delegating to `self.execute(raw=raw, entry=entry, ...)` for backwards compatibility.

---

## 3. Consequences & Impact

### Positive
1. **Absolute DRY:** Zero duplicated indexing logic or error-handling blocks.
2. **Unified Telemetry Hierarchy:** 100% of LLM generations and judge loops (Stage 1b through Stage 7) are children of the single root span `cresmo.pipeline.execution`.
3. **Token Conservation:** Idempotency guard prevents unnecessary Stage 1b indexing on already-processed content.
4. **Clean Domain Ergonomics:** Public `execute(raw)` allows synthetic or streamed transcripts to run through the entire pipeline without touching fake URLs or disk files.
5. **Zero Breaking Changes:** `_synthesize_transcript` and existing public methods preserve exact signatures and return types.

### Negative / Trade-offs
- None. Refactoring is purely structural and enhances system coherence and observability.
