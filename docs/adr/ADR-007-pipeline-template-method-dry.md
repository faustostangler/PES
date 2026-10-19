# ADR-007: Template Method and DRY Unification in Cognitive Synthesis Pipeline

**Status:** DEPRECATED (SUPERSEDED by [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md))  
**Date:** 2026-09-14  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Superseded By:** [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-030`](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-035`](ADR-035-atomic-work-item-traces-and-sota-kiss-batch-correlation.md)  

> [!WARNING]
> **SUPERSEDED ARCHITECTURAL DECISION:**  
> The downstream private template method (`_synthesize_transcript`) operating on `RawTranscript` has been **DEPRECATED and SUPERSEDED**:
> - **Pipeline Orchestration**: Hoisted to `CresmoPipeline.execute(...)` with single root execution span per [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md).
> - **Execution Sequence**: Decoupled fluid prose and established `transform_fluid_prose` as Stage 1 before catalog indexing per [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md).
> - **Stage Runner Fabric**: Individual stage execution refactored into `PipelineStageRunner.run_evaluated_stage` and universal `StageConfig` per [`ADR-030`](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md) and [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md).
> - **Domain Aggregate**: `RawTranscript` completely replaced by `SourceTranscript` per [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md) and [`ADR-038`](ADR-038-pure-value-object-triad-composition.md).
> - **Telemetry Invariant**: Single mega-trace replaced by 1 Trace = 1 Work Item per [`ADR-035`](ADR-035-atomic-work-item-traces-and-sota-kiss-batch-correlation.md) and [`ADR-037`](ADR-037-lean-telemetry-topography-and-chronological-evaluation.md).

---

## 1. Context

In [`src/cresmo/application/pipeline.py`](../../src/cresmo/application/pipeline.py), the orchestrator supported multiple source ingestion workflows:
- `run_for_video(video_url)`: Downloads media via `MediaIngestionPort`, generates raw transcript, and executes synthesis.
- `run_for_text_file(file_path)`: Directly parses raw local text/markdown file, saves to vault, and executes synthesis.

### The Problem (Duplication Smell & Drift Risk)
A structural inspection revealed that downstream synthesis steps:
1. Idempotency ledger check (`is_processed`)
2. Socratic Gap Filler & Longitudinal Expander (`FillGapsFluidProseUseCase` + `ExpandLongitudinalSynchronicUseCase`)
3. Holistic Inventory Discovery (`DiscoverAtomicInventoryUseCase`)
4. Batched Atomic Synthesis (`SynthesizeAtomicBatchUseCase`)
5. MOC Reconciliation (`ReconcileMOCsUseCase`)
6. Duplicate Entity Resolution (`UnifyDuplicateNotesUseCase`)
7. Ledger mark processed and summary projection (`PipelineResult`)

were duplicated across both public entrypoints (~50 lines of duplicate orchestration code). Any future enhancement to cognitive stages (e.g., audio generation, language translation, semantic embeddings) would require dual modifications, creating high risk of behavioral drift and defect regression.

---

## 2. Decision

We apply the **GoF Template Method** and **DRY (Don't Repeat Yourself)** principles to encapsulate the common downstream synthesis stages into a private template method:

### 2.1 Private Template Method: `_synthesize_transcript`
```python
def _synthesize_transcript(
    self,
    raw: RawTranscript,
    gap_filler_passes: int = 3,
    force_reprocess: bool = False,
) -> PipelineResult:
```
This method acts as the invariant skeleton for downstream synthesis. It receives an already constructed `RawTranscript` domain entity and executes all synthesis steps identically regardless of origin.

### 2.2 Specialized Pre-Processing Steps
The public entrypoints retain solely their differentiated raw ingestion logic:
- `run_for_video`: Invokes `self.ingest_raw_transcript.execute(video_url=video_url)` $\rightarrow$ delegates to `_synthesize_transcript`.
- `run_for_text_file`: Invokes `self._load_transcript_from_file(file_path)` + `self.vault_port.save_raw_transcript(raw)` $\rightarrow$ delegates to `_synthesize_transcript`.
- `run_for_manifest`: Sequentially delegates each manifest line to `run_for_video`.

---

## 3. Verification & Test Coverage

- Executed the complete hermetic Cresmo unit test suite (`tests/cresmo/unit/`).
- **405 unit tests passed with 100% success** (including all 21 pipeline-specific edge cases, error conditions, and mocks).
- Formatted and validated against `ruff`.

---

## 4. Consequences & Impact

### Positive
1. **DRY & Single Source of Truth:** The downstream synthesis flow is defined in exactly one place.
2. **Sub-Zero Bug Drift:** Any new stage or ledger policy update automatically benefits all ingestion modalities (video, priority text, manifests).
3. **High Cohesion & Readability:** Public methods are lean, single-purpose coordinators with Cyclomatic Complexity $\le 3$.

### Negative / Trade-offs
- Internal method dispatch adds a minor stack frame level (zero perceptible overhead in Python 3.13).
