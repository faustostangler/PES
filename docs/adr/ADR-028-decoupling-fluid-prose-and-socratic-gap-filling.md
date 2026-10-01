# ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling for Pre-Indexing Linguistic Normalization

**Status:** PROPOSED  
**Date:** 2026-10-01  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md)

---

## 1. Context & Architectural Motivation

In the current Cresmo Knowledge Synthesis Engine ([`src/cresmo/application/pipeline/coordinator.py`](../../src/cresmo/application/pipeline/coordinator.py)), the pipeline execution sequence established in [ADR-021](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md) executes catalog indexing (`raw_indexing`) directly on the verbatim spoken transcript (`RawTranscript`) before downstream synthesis begins:

```
[Raw Ingestion] ──► [raw_indexing] ──► [fluid_prose (gap filler)] ──► [expansion] ──► ...
```

### Architectural Flaws & Domain Impedance Identified:

1. **Suboptimal Cognitive Input for Catalog Indexing (Garbage-In, Garbage-Out):**
   Raw spoken transcripts contain phonetic distortions, verbal crutches, false starts, conversational noise, audience addresses, and speech artifacts. Feeding verbatim spoken excerpts directly to `IndexRawTranscriptsUseCase` forces the LLM to extract domain concepts, summaries, and paratactic syntheses from disorganized spoken text, degrading the quality of `_canal.md` catalogs and `brain.csv` lookup keys.
2. **Coupling of Detranscription and Socratic Gap Filling:**
   `FillGapsUseCase` ([`src/cresmo/application/use_cases/fill_gaps.py`](../../src/cresmo/application/use_cases/fill_gaps.py)) coupled two distinct responsibilities into a single stage:
   - *Responsibility A (Detranscription & Fluid Prose):* Purging oralities, rewriting into third-person neutral narrative, and verifying NER spelling.
   - *Responsibility B (Socratic Gap Filling):* Conducting an epistemic gap audit across 6 dimensions, stratifying causality, and constructing the mandatory `## Informações Complementares` section.
3. **Missing Intermediate Domain Aggregate:**
   There is currently no domain entity representing clean, normalized fluid prose decoupled from the Socratic compendium with complementary info.

---

## 2. Decision

We decouple `fluid_prose` detranscription from `gap_filler` epistemic enrichment and reorder the synthesis pipeline to establish pre-indexing linguistic normalization.

### 2.1 The New Linear Pipeline Topology

The canonical execution sequence in `CresmoPipeline` is updated to:

```
[1. fluid_prose] ──► [2. raw_indexing] ──► [3. gap_filler] ──► [4. expansion] ──► [5. atomic inventory] ──► [6. atomic synthesis] ──► [7. moc] ──► [8. dedup]
```

### 2.2 Stage Responsibilities & Use Case Separation

1. **Stage 1: `fluid_prose` (`TransformFluidProseUseCase`):**
   - **Input:** `RawTranscript` (verbatim spoken audio/subtitle text).
   - **Transform:** Executes prompt `PromptKey.FLUID_PROSE` (`cresmo-expander` detranscription core).
   - **Invariants:**
     - Purges all speech noise, verbal crutches, hesitations, conversational filler, speaker self-references, timestamps, and direct audience addresses.
     - Conceptually reorganizes the text into formal third-person neutral narrative prose.
     - Verifies and standardizes spelling of Named Entities (NER: historical actors, institutions, places, treaties, dates, canonical concepts).
     - Strictly enforces `cresmo-style-guide`: continuous prose starting directly with `##` on Line 1, zero bullet points, zero markdown tables, zero em-dashes (`—`), zero binary antithetical contrast formulas (`não X, mas Y`).
     - Does *not* perform Socratic gap expansion and does *not* create `## Informações Complementares`.
   - **Output:** `FluidTranscript` domain aggregate.

2. **Stage 2: `raw_indexing` (`IndexRawTranscriptsUseCase`):**
   - **Input:** `FluidTranscript` strictly.
   - **Transform:** Extracts concepts (`PromptKey.RAW_INDEX_CONCEPTS`), summary (`PromptKey.RAW_INDEX_SUMMARY`), and paratactic synthesis (`PromptKey.RAW_INDEX_SYNTHESIS`) evaluated via iterative LLM-as-a-Judge loops.
   - **Advantage:** All index descriptors and search tokens are extracted from pristine, normalized third-person prose with verified NER spelling.
   - **Output:** `RawIndexEntry`.

3. **Stage 3: `gap_filler` (`FillGapsUseCase`):**
   - **Input:** `FluidTranscript`.
   - **Transform:** Executes Socratic gap audit across 6 epistemic dimensions over `gap_filler_passes` cycles. Generates and enriches the mandatory `## Informações Complementares` section with numbered continuous paragraphs for secondary lineages, biographies, and granular data.
   - **Output:** `EnrichedCompendium` domain aggregate.

4. **Stages 4 through 8:**
   Remain downstream of `EnrichedCompendium`: `expansion` (`ExpandCompendiumUseCase`), `inventory` (`DiscoverAtomicInventoryUseCase`), `atomic_batch` (`SynthesizeAtomicBatchUseCase`), `mocs` (`ReconcileMOCsUseCase`), and `duplicate_unification` (`UnifyDuplicateNotesUseCase`).

### 2.3 Strict Rejection of Standalone Raw Indexing & Universal `FluidTranscript` Contract

1. **Elimination of Standalone Raw Indexing:**
   Raw indexing (`raw_indexing`) without pre-normalization into fluid prose is an anti-pattern that pollutes catalogs with oral artifacts. Standalone CLI commands (such as `cresmo index-raw`) and directory-scanning loops across raw files are completely removed.
2. **Universal `FluidTranscript` Type Guard:**
   Both `IndexRawTranscriptsUseCase` (Stage 2) and `FillGapsUseCase` (Stage 3) strictly require a `FluidTranscript` domain aggregate as their primary input. Passing a `RawTranscript` or any unnormalized text directly to these use cases raises a `TypeError` / `DomainValidationError`. Zero shims, zero fallback to `RawTranscript`.

### 2.4 New Domain Entity: `FluidTranscript`

We introduce `FluidTranscript` in `src/cresmo/domain/entities.py`:
- Immutable `@dataclass(frozen=True)` aggregate.
- Attributes: `content_id`, `channel_name`, `body` (clean fluid prose), `title`, `source_url`, `publication_date`, `upload_date`, `channel_id`, `channel_category`, `video_description`.
- Invariants: `body` must not be empty; Markdown tables are strictly forbidden.

---

## 3. Telemetry, Prometheus & Langfuse Specifications

1. **Root Span Hierarchy:**
   All child spans remain nested within `cresmo.pipeline.execution`:
   - `fluid_prose`: span name `fluid_prose`, trace ID `{content_id}_fluid_prose`
   - `raw_indexing`: span name `raw_indexing`, trace ID `{content_id}_raw_indexing`
   - `gap_filler`: span name `gap_filler`, trace ID `{content_id}_gap_fill_pass_{pass}`
   - `expansion`: span name `expansion`
   - `inventory`: span name `inventory`
   - `atomic_batch`: span name `atomic_batch`
   - `mocs`: span name `mocs`
   - `duplicate_unification`: span name `duplicate_unification`
2. **Prometheus Metrics:**
   Histogram `cresmo_pipeline_stage_duration_seconds` emits with labels `stage="fluid_prose"`, `stage="raw_indexing"`, `stage="gap_filler"`, etc.

---

## 4. Consequences & Migration

### Positive
1. **Maximized Index Quality:** Indexing summary, concepts, and synthesis are extracted from clean, grammatically sound, third-person prose with verified NER spelling.
2. **High Cohesion & Low Coupling:** Separation of concerns between linguistic detranscription (`fluid_prose`) and epistemological expansion (`gap_filler`).
3. **Observability Clarity:** Independent timing, token consumption, and failure tracking for fluid prose transformation vs. gap filling.

### Invariant & Migration
- `FillGapsUseCase` strictly requires `FluidTranscript` and raises `DomainValidationError` on `RawTranscript`.
- `IndexRawTranscriptsUseCase` strictly requires `FluidTranscript` and raises `DomainValidationError` on `RawTranscript`.
- Standalone `cresmo index-raw` CLI command is completely eliminated. All pipeline runs execute Stage 1 (`fluid_prose`) first.
