# SPEC-011: Fluid Prose Detranscription and Gap Filler Decoupling Specification

**Context:** Cresmo Knowledge Synthesis  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** PROPOSED SPECIFICATION  
**Governing ADR:** [`ADR-028`](../adr/ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`SPEC-008`](SPEC-008-metrics-port-and-prometheus-sre-dora.md), [`SPEC-010`](SPEC-010-unified-telemetry-vocabulary-and-langfuse-conventions.md)

---

## 1. Domain Entities & Invariants

### 1.1 `FluidTranscript` Aggregate
In `src/cresmo/domain/entities.py`:
- `content_id: ContentId` (validated length and alphanumeric format).
- `channel_name: ChannelName` (value object).
- `body: str`: Clean fluid prose text.
  - Invariant 1: Must be non-empty and non-whitespace string.
  - Invariant 2: Must be continuous prose; markdown tables (`| header |`) are strictly forbidden.
- Optional provenance metadata: `title: str = ""`, `source_url: str = ""`, `publication_date: date | None = None`, `upload_date: date | None = None`, `channel_id: ChannelId | None = None`, `channel_category: str = ""`, `video_description: str = ""`.

---

## 2. Use Case Contracts

### 2.1 `TransformFluidProseUseCase` (`src/cresmo/application/use_cases/transform_fluid_prose.py`)
```python
class TransformFluidProseUseCase:
    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        ...

    def execute(
        self,
        raw_transcript: RawTranscript,
        user: UserIdentity | None = None,
    ) -> FluidTranscript:
        """Transforms raw transcript with oralities into clean fluid prose."""
```
- Invariant 1: Invokes `llm_synthesis_port.transform` with `PromptKey.FLUID_PROSE`.
- Invariant 2: Parses generated markdown, extracts H1 title if present, removes H1 header from body, and verifies body is continuous prose.
- Invariant 3: Does not require or create `## Informações Complementares`.
- Invariant 4: If `vault_port` is provided, optionally persists to `vault_port.save_fluid_transcript(fluid)`.

### 2.2 `IndexRawTranscriptsUseCase` (`src/cresmo/application/use_cases/indexing/orchestrator.py`)
```python
def execute(
    self,
    transcript: FluidTranscript,
    force: bool = False,
    user: UserIdentity | None = None,
) -> RawIndexEntry | None:
```
- Invariant 1: Requires `isinstance(transcript, FluidTranscript)`. If anything other than `FluidTranscript` is provided, raises `TypeError("IndexRawTranscriptsUseCase requires FluidTranscript.")`.
- Invariant 2: Standalone channel directory scanning (`index_channel`, `index_all_channels`) is removed.
- Invariant 3: Extracts concepts, summary, and paratactic synthesis exclusively from the fluid transcript's body.

### 2.3 `FillGapsUseCase` (`src/cresmo/application/use_cases/fill_gaps.py`)
```python
def execute(
    self,
    fluid_transcript: FluidTranscript,
    passes: int = 3,
    user: UserIdentity | None = None,
) -> EnrichedCompendium:
```
- Invariant 1: Requires `isinstance(fluid_transcript, FluidTranscript)`. If anything other than `FluidTranscript` is provided, raises `TypeError("FillGapsUseCase requires FluidTranscript.")`.
- Invariant 2: Executes Socratic gap audit across 6 dimensions.
- Invariant 3: Mandates the presence of non-empty `## Informações Complementares` section; raises `CompendiumStructureError` if absent or empty.
- Invariant 4: Returns validated `EnrichedCompendium` and persists via `vault_port.save_enriched_compendium()`.

---

## 3. Pipeline Coordinator (`CresmoPipeline`) Lifecycle

In `src/cresmo/application/pipeline/coordinator.py`, `execute()` enforces:
1. `stage_runner.run_stage("fluid_prose", ...)` -> produces `fluid_transcript: FluidTranscript`.
2. `stage_runner.run_stage("raw_indexing", ...)` -> consumes `fluid_transcript`, produces `entry: RawIndexEntry`.
3. `stage_runner.run_stage("gap_filler", ...)` -> consumes `fluid_transcript`, produces `enriched_compendium: EnrichedCompendium`.
4. `stage_runner.run_stage("expansion", ...)` -> consumes `enriched_compendium`, produces `expanded_compendium: EnrichedCompendium`.
5. `stage_runner.run_stage("inventory", ...)` -> produces `inventory: AtomicEntityInventory`.
6. `stage_runner.run_stage("atomic_batch", ...)` -> produces `synthesized_notes: list[AtomicNote]`.
7. `stage_runner.run_stage("mocs", ...)` -> produces `mocs: list[MapOfContent]`.
8. `stage_runner.run_stage("duplicate_unification", ...)` -> produces `dedup_report`.

---

## 4. Test Strategy (Refractometry Test Anchors)

1. `test_transform_fluid_prose_success`: verifies transformation of raw transcript into `FluidTranscript` without oralities.
2. `test_transform_fluid_prose_preserves_metadata`: ensures content ID, channel name, publication dates are propagated.
3. `test_index_raw_accepts_fluid_transcript`: verifies `IndexRawTranscriptsUseCase` consumes `FluidTranscript` directly.
4. `test_index_raw_rejects_raw_transcript`: verifies `IndexRawTranscriptsUseCase` strictly rejects `RawTranscript` (ADR-028 Invariant).
5. `test_fill_gaps_on_fluid_transcript`: verifies Socratic gap audit on `FluidTranscript` producing `EnrichedCompendium`.
6. `test_pipeline_execution_stage_order`: verifies exact execution order `fluid_prose` -> `raw_indexing` -> `gap_filler` -> `expansion` -> `inventory` -> `atomic_batch` -> `mocs` -> `duplicate_unification`.
