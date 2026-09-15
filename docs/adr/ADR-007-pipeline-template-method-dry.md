# ADR-007: Template Method and DRY Unification in Cognitive Synthesis Pipeline

**Status:** APPROVED  
**Date:** 2026-09-14  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context

In [`src/cresmo/application/pipeline.py`](../../src/cresmo/application/pipeline.py), the orchestrator supported multiple source ingestion workflows:
- `run_for_video(video_url)`: Downloads media via `MediaIngestionPort`, generates raw transcript, and executes synthesis.
- `run_for_text_file(file_path)`: Directly parses raw local text/markdown file, saves to vault, and executes synthesis.

### The Problem (Duplication Smell & Drift Risk)
A structural inspection revealed that Stages 2 through 7:
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
This method acts as the invariant skeleton for Stages 2–7. It receives an already constructed `RawTranscript` domain entity and executes all stages identically regardless of origin.

### 2.2 Specialized Pre-Processing Steps
The public entrypoints retain solely their differentiated Stage 1 ingestion logic:
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
1. **DRY & Single Source of Truth:** The synthesis flow (Stages 2–7) is defined in exactly one place.
2. **Sub-Zero Bug Drift:** Any new stage or ledger policy update automatically benefits all ingestion modalities (video, priority text, manifests).
3. **High Cohesion & Readability:** Public methods are lean, single-purpose coordinators with Cyclomatic Complexity $\le 3$.

### Negative / Trade-offs
- Internal method dispatch adds a minor stack frame level (zero perceptible overhead in Python 3.13).
