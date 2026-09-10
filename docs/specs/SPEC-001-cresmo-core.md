# SPEC-001: Cresmo Knowledge Synthesis Core Specifications

**Linked ADR:** [ADR-001](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  
**Linked Eval Rubric:** [EVAL-001](./EVAL-001-cresmo-synthesis.md)  
**Status:** Draft  
**Date:** 2026-09-10  
**Bounded Context:** Cresmo Knowledge Synthesis  

---

## 1. Overview & Objectives

This specification defines the precision acceptance criteria, entity invariants, boundary failure modes, and test strategy derived from [ADR-001](../adr/ADR-001-cresmo-modular-monolith-strangling.md). It serves as the frozen contract for Test-Driven Development (Phase 3 Surgery).

The six incremental integer stages specified:
- **Stage 1**: Raw Transcript (Ingestion via `MediaIngestionPort` ACL)
- **Stage 2**: Gap Filler (Socratic multi-pass fluid prose expansion)
- **Stage 3**: Expander (Braudelian longitudinal & Jaspers synchronic expansion)
- **Stage 4**: Inventory (Holistic discovery of unique atomic entities)
- **Stage 5**: Batch (Batched atomic synthesis and vault proliferation)
- **Stage 6**: MOC (Map of Content reconciliation with zero orphaned notes)

---

## 2. Bounded Context & Domain Invariants

### 2.1 Value Objects (Zero Primitive Obsession)

- **`ContentId`**:
  - *Invariant*: Must be a non-empty string matching `^[a-zA-Z0-9_-]{8,64}$`. Rejects whitespace, empty strings, and special characters.
  - *Failure*: Raises `DomainValidationError`.

- **`NoteTitle`**:
  - *Invariant*: Length between 1 and 200 characters. Automatically sanitizes brackets (`[[`, `]]`), newlines, and filesystem reserved characters (`/ \ : * ? " < > | %`).
  - *Failure*: Cannot be empty or generic placeholders (`"Untitled"`, `"Untitled_Note"`). Raises `DomainValidationError`.

- **`NoteType`**:
  - *Invariant*: Must strictly be one of `NoteType.CONCEPT`, `NoteType.ENTITY`, `NoteType.EVENT`, or `NoteType.PROCESS`. Case-insensitive normalized.
  - *Failure*: Raises `NoteTypologyError`.

- **`CausalMatrix`**:
  - *Invariant*: Immutable ternary value object (`cause`, `effect`, `epistemic_attribution`). Strings trimmed; `cause` and `effect` must be non-empty when instantiated.
  - *Failure*: Raises `DomainValidationError`.

- **`CrossContextRelations`**:
  - *Invariant*: Immutable triad (`precursors`, `lateral_events`, `aftermath`). Strings trimmed.

### 2.2 Entities & Aggregates (Always Valid at Construction)

- **`RawTranscript` (Stage 1 Aggregate)**:
  - *Invariant*: `body` must contain non-whitespace text. `content_id` must be a valid `ContentId`.
  - *Failure*: Raises `DomainValidationError`.

- **`EnrichedCompendium` (Stage 2 & 3 Aggregate)**:
  - *Invariant*: `body` must be continuous prose (rejects raw markdown tables or bulleted lists in primary narrative). `complementary_info` must not be empty. `pass_count >= 1`.
  - *Failure*: Raises `CompendiumStructureError`.

- **`AtomicNote` (Stage 4 & 5 Aggregate)**:
  - *Invariant*: `title` cannot appear in `direct_relations` (no self-referential cycles). `definition` must be at least 20 characters. `note_type` must be valid.
  - *Failure*: Raises `SelfReferentialRelationError` or `DomainValidationError`.

- **`MapOfContent` (Stage 6 Aggregate)**:
  - *Invariant*: Must contain at least one associated `NoteTitle`. Rejects duplicate note titles within the same MOC.
  - *Failure*: Raises `DomainValidationError`.

---

## 3. Test Strategy Classification

### 3.1 Unit Tests (`tests/cresmo/unit/`)
- **Scope**: Pure Domain models, Value Object parsing/validation, Entity invariant enforcement, Use Case orchestration logic.
- **Mock Boundary**: Hermetic. All external dependencies mocked using:
  - `MockLLMAdapter` (canned deterministic text/JSON responses).
  - `InMemoryVaultAdapter` (in-memory dictionary mimicking Obsidian vault).
  - `MockMediaIngestionPort` (in-memory fixtures mimicking YouTube transcripts).
- **Target**: **0 surviving mutants** under `mutmut`.

### 3.2 Integration Tests (`tests/cresmo/integration/`)
- **Scope**:
  - `ObsidianVaultAdapter`: Real filesystem reads/writes, atomic file replacement (`.tmp` -> rename), frontmatter parsing, and `_index.json` locking/updating.
  - `LegacyISBMediaIngestionAdapter`: Encapsulation of `playground/isb.ai` calls, subtitle sanitization, and error translation.
- **Target**: `< 5% surviving mutants` under `mutmut`.

### 3.3 LLM Eval Gates (Langfuse Telemetry)
- **Scope**: Output of Stages 2 through 6 evaluated against frozen criteria in [`EVAL-001`](./EVAL-001-cresmo-synthesis.md).
- **Blocking Gates**: `faithfulness >= 0.80`, `relevance >= 0.75`, `hallucination <= 0.10`, `toxicity <= 0.05`.

---

## 4. Acceptance Criteria (Scenarios)

### Stage 1: Raw Transcript Ingestion

#### Scenario 1.1: Successful Ingestion via ACL
- **Given**: A valid YouTube URL with available native subtitles.
- **When**: `IngestRawTranscriptUseCase.execute(video_url)` is invoked.
- **Then**: Returns a `RawTranscript` aggregate with valid `ContentId`, populated `body`, and metadata; no `sys.path` tampering escapes the adapter.

#### Scenario 1.2: Ingestion Rejects Corrupted or Empty Payload
- **Given**: A media source returning empty transcript text.
- **When**: Construction of `RawTranscript` is attempted.
- **Then**: `DomainValidationError` is raised; no corrupted file is persisted.

---

### Stage 2: Socratic Gap Filler

#### Scenario 2.1: Multi-Pass Continuous Prose Generation
- **Given**: A valid `RawTranscript`.
- **When**: `FillGapsFluidProseUseCase.execute(raw_transcript, passes=3)` is invoked.
- **Then**: An `EnrichedCompendium` is produced containing fluid prose and a `## Informações Complementares` section; all oralities and bulleted summaries are absent from the body.

#### Scenario 2.2: Rejection of Discontinuous or Bulleted Output
- **Given**: An LLM response formatted purely as bulleted summaries.
- **When**: Validation of `EnrichedCompendium` is executed.
- **Then**: `CompendiumStructureError` is raised, triggering a retry or failure.

---

### Stage 3: Longitudinal & Synchronic Expander

#### Scenario 3.1: Braudelian & Jaspers In-Place Enrichment
- **Given**: An `EnrichedCompendium` from Stage 2.
- **When**: `ExpandLongitudinalSynchronicUseCase.execute(compendium)` is invoked.
- **Then**: The compendium is enriched with 3-tier causal depth (longue durée) and axial synchronicity without overwriting origin metadata.

---

### Stage 4: Holistic Inventory Discovery

#### Scenario 4.1: Exhaustive Entity Discovery
- **Given**: An `EnrichedCompendium` from Stage 3.
- **When**: `DiscoverAtomicInventoryUseCase.execute(compendium)` is invoked with `temperature=0.0`.
- **Then**: Returns an `AtomicEntityInventory` containing unique, deduplicated entity titles and their normalized `NoteType`.

---

### Stage 5: Batched Atomic Synthesis & Vault Proliferation

#### Scenario 5.1: Batched Note Synthesis with Causal Matrix
- **Given**: An `AtomicEntityInventory` with 12 entities and `batch_size=5`.
- **When**: `SynthesizeAtomicBatchUseCase.execute(inventory, compendium)` is invoked.
- **Then**: Notes are synthesized in 3 discrete batches (5, 5, 2); each note has a valid `CausalMatrix`, `CrossContextRelations`, and definition; persisted incrementally via `VaultRepositoryPort`.

#### Scenario 5.2: Self-Referential Relation Prevention
- **Given**: An atomic note entity where `title = "Teoria das Elites"`.
- **When**: An attempt is made to include `"Teoria das Elites"` in `direct_relations`.
- **Then**: `SelfReferentialRelationError` is raised immediately at instantiation.

---

### Stage 6: Map of Content (MOC) Reconciliation

#### Scenario 6.1: Vault Reconciliation with Zero Orphaned Notes
- **Given**: Newly proliferated `AtomicNote` entities in the vault.
- **When**: `ReconcileMOCsUseCase.execute()` is invoked.
- **Then**: All notes are linked to at least one thematic `MapOfContent`; `_index.json` is updated with canonical paths and aliases; zero orphaned nodes remain.

---

## 5. Boundary Conditions & Exception Mapping

| Component | Input / Condition | Expected Domain Exception |
|---|---|---|
| `ContentId` | `""` or `"   "` or `"inv@lid#id"` | `DomainValidationError` |
| `NoteTitle` | `""` or `"Untitled_Note"` or `"> 200 chars"` | `DomainValidationError` |
| `NoteTitle` | `"[[Concept Name]]"` | Normalized automatically to `"Concept Name"` |
| `NoteType` | `"unknown_tag"` | `NoteTypologyError` |
| `AtomicNote` | `definition < 20 chars` | `DomainValidationError` |
| `AtomicNote` | `title in direct_relations` | `SelfReferentialRelationError` |
| `EnrichedCompendium` | Missing `## Informações Complementares` | `CompendiumStructureError` |
| `MediaIngestionAdapter` | Upstream YouTube HTTP 429 | `RateLimitExceededError` |
| `ObsidianVaultAdapter` | Concurrent write collision | `VaultStorageConflictError` |

---

## 6. Regression Anchors

The 73 legacy tests currently located in `playground/cresmo/tests/` serve as the immutable regression baseline:
- `test_cresmo_config.py` (8 tests)
- `test_cresmo_llm.py` (10 tests)
- `test_cresmo_notes_batched.py` (3 tests)
- `test_cresmo_pipeline_llm.py` (4 tests)
- `test_json_atomic.py` (7 tests)
- `test_context_isolation.py` (5 tests)
- `test_folder_priority.py` (10 tests)
- `test_moc_manager_prompt.py` (3 tests)
- `test_priority_autosync.py` (3 tests)
- `test_priority_fastpath.py` (7 tests)
- `test_proliferation.py` (3 tests)
- `test_rate_limit_path.py` (3 tests)
- `test_validation.py` (7 tests)

*Regression Gate*: All 73 tests must continue to pass uninterrupted during the strangling migration.

---

## 7. Observability & Telemetry Assertions

Every use case execution must verify telemetry via `Langfuse`:
- Assert root trace is generated with name `cresmo-pipeline-run` and tags `["cresmo", category, channel]`.
- Assert each stage produces its corresponding span (`Stage_1_RawTranscript`, `Stage_2_GapFiller`, `Stage_3_Expander`, `Stage_4_Inventory`, `Stage_5_Batch`, `Stage_6_MOC`).
- Assert all generations capture token usage and latency.
