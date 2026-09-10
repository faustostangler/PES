# ADR-001: Strangling Cresmo into Hexagonal Modular Monolith with Media Ingestion ACL and Vault Port

**Status:** APPROVED  
**Date:** 2026-09-10  
**Decision Makers:** Lead Architect (Fausto Stangler), Stereoscopist (Doctor Stangler Committee)  

---

## 1. Context

The PES workspace contains an advanced audiovisual knowledge ingestion, detranscription, expansion, and synthesis ecosystem primarily residing in `playground/cresmo/` and its upstream progenitor `playground/isb.ai/`.

As documented in [`docs/legacy_discovery/DISCO-001-cresmo-ecosystem-archaeology.md`](../legacy_discovery/DISCO-001-cresmo-ecosystem-archaeology.md), the system has grown organically from an experimental script suite into an essential intelligence pipeline. While operational capabilities are high (73 passing tests in `playground/cresmo/tests/`, centralized `CresmoConfig`, and official `google-genai` SDK support), the architectural foundation suffers from critical technical debt:
1. **Fragile Runtime Ingestion Coupling**: `cresmo_ingestion.py` and `cresmo_pipeline.py` rely on runtime `sys.path.insert(0, ...)` injection to call unencapsulated scripts (`sync_channels.py`, `downloader.py`) in `playground/isb.ai/`, directly mutating global state (e.g. `downloader.RATE_LIMIT_LOG_FILE`).
2. **Procedural GOD-Modules**: Core logic is concentrated in monolithic files ([`cresmo_pipeline.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/playground/cresmo/cresmo_pipeline.py) with 2,017 lines; [`cresmo_shared.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/playground/cresmo/cresmo_shared.py) with 1,040 lines) that mix pipeline orchestration, regex parsing, CLI arguments, and filesystem operations.
3. **Dual Execution Runtime**: Pipeline stages maintain redundant code paths between direct Hexagonal LLM calls (`GeminiAPIAdapter`) and legacy IDE Subagent RPC (`agentapi` binary, gRPC socket `127.0.0.1:41667`, and trajectory log parsing).
4. **Filesystem as Unbounded Database**: Business logic directly reads and writes disk files without a repository abstraction, hindering unit testing and violating Hexagonal Ports & Adapters.
5. **Absence of Standard AI Telemetry (Langfuse)**: Non-deterministic LLM generations are not traced via structured spans (`trace_id`, `session_id`, `generation`), lacking automated Eval gates for hallucination and faithfulness.

The Bounded Context and Ubiquitous Language are defined in [`CONTEXT.md`](../../CONTEXT.md).

---

## 2. Decision

We will strangulate the legacy procedural code in `playground/cresmo/` and `playground/isb.ai/` into a Clean Hexagonal Modular Monolith located in `src/cresmo/`, implementing:
1. **Strict Hexagonal Directory Layout**: Segregating pure `domain/`, application use cases and abstract interfaces in `application/`, external technology implementations and Anti-Corruption Layers in `infrastructure/`, and CLI controllers in `presentation/`.
2. **Media Ingestion Anti-Corruption Layer (`MediaIngestionPort`)**: Abstracting all YouTube/Whisper scraping behind a clean interface, moving `isb.ai` calls entirely inside `infrastructure/adapters/legacy_isb_ingestion_adapter.py` with zero `sys.path` leakage into domain or application layers.
3. **Vault Repository Port (`VaultRepositoryPort`)**: Isolating Obsidian Second Brain persistence (`wiki/`, `enriched/`, `_index.json`, `MOCs/`) behind an infrastructure adapter (`infrastructure/adapters/obsidian_vault_adapter.py`).
4. **Decomposition into Single-Responsibility Use Cases**: Refactoring the 2,017 LOC procedural pipeline into dedicated use cases:
   - `IngestRawTranscriptUseCase` (Stage 1: Raw Transcript)
   - `FillGapsFluidProseUseCase` (Stage 2: Gap Filler)
   - `ExpandLongitudinalSynchronicUseCase` (Stage 3: Expander)
   - `DiscoverAtomicInventoryUseCase` (Stage 4: Inventory)
   - `SynthesizeAtomicBatchUseCase` (Stage 5: Batch)
   - `ReconcileMOCsUseCase` (Stage 6: MOC)
5. **Deprecation of Legacy IDE Agent RPC in Core**: Standardizing all AI transformations on `LLMTransformationPort` and official `google-genai` adapters.
6. **Clinical Telemetry & Eval Gates via Langfuse**: Wrapping every generative call in Langfuse spans and enforcing frozen numeric Eval Rubrics before marking synthesis complete.

---

## 3. Consequences

### Positive
- **Architectural Purity**: Domain and Application layers become 100% free of external frameworks, CLI arguments, and disk paths.
- **Hermetic Testing**: All use cases become testable in memory using mock ports (`MockLLMAdapter`, `InMemoryVaultAdapter`, `MockMediaIngestionPort`) without touching the filesystem, YouTube, or Google APIs.
- **Safe Evolutionary Strangling**: The existing `playground/cresmo` test suite (73 tests) remains the regression anchor during migration.
- **Fail-Fast Configuration**: Centralized `CresmoConfig` via `pydantic-settings` remains the single source of truth (SSOT).
- **Observability**: Complete observability for LLM token usage, latency, and automated quality scoring (faithfulness, hallucination) via Langfuse.

### Negative
- **Structural Migration Effort**: Requires creating the `src/cresmo/` tree and migrating existing procedural functions into cohesive classes.
- **Adapting Legacy Upstream**: Requires maintaining the `LegacyISBMediaIngestionAdapter` ACL until `downloader.py` and `sync_channels.py` are natively refactored.

### Neutral
- Output artifacts (Obsidian markdown files, YAML frontmatter, `_index.json`, `MOC_*.md`) remain 100% byte-compatible with the existing vault.

---

## 4. Alternatives Considered

### Alternative A: In-Place Refactoring of `playground/cresmo/cresmo_pipeline.py`
- **Pros:** Fast, avoids creating new directory structures.
- **Cons:** Keeps the 2,017-line god-file; fails to decouple filesystem I/O from business rules; fails to isolate `sys.path` tampering from `isb.ai`.
- **Why Rejected:** Violates the Doctor Stangler Modular Monolith and Clean Architecture standards. Leaves technical debt in place.

### Alternative B: Complete Rewrite of Scrapers (`yt-dlp` and `whisper`) from Scratch
- **Pros:** Completely eliminates `playground/isb.ai/`.
- **Cons:** High cognitive load and delivery risk. `downloader.py` contains battle-tested HTTP 429 mitigations (filtering `tlang=`) and YouTube Netscape cookie rotation that work reliably.
- **Why Rejected:** Violates the KISS and Strangler Fig principles. Legacy code should be strangulated behind an ACL, not prematurely rewritten.

---

## 5. Domain Model Impact

### Value Objects
- `ContentId`: Strongly-typed unique identifier for raw transcripts and media items (replaces bare `str`). Rejects whitespace and invalid characters at instantiation.
- `NoteTitle`: Validated canonical title for atomic notes. Automatically strips `[[`, `]]`, and path-traversal characters.
- `NoteType`: Enum/Literal Value Object restricted strictly to `{"concept", "entity", "event", "process"}`.
- `CausalMatrix`: Immutable value object representing `cause`, `effect`, and `epistemic_attribution`.
- `CrossContextRelations`: Immutable value object representing `precursors`, `lateral_events`, and `aftermath`.

### Entities & Aggregates
- `RawTranscript`: Root aggregate for Stage 1 (Raw Transcript), containing `ContentId`, source metadata, and verbatim body.
- `EnrichedCompendium`: Aggregate for Stage 2 (Gap Filler) and Stage 3 (Expander), validating that the body contains dense continuous prose and the mandatory `## Informações Complementares`.
- `AtomicNote`: Rich domain entity encapsulating frontmatter metadata, contextual definition, typed connections, causal matrix, and cross-context links (Stage 4 Inventory & Stage 5 Batch). Invariants verified at instantiation (no empty titles, valid type, non-empty definition).
- `MapOfContent`: Aggregate representing thematic MOCs (Stage 6 MOC), ensuring bidirectional links and zero orphaned notes.

### Ports (Abstract Base Classes in Application Layer)
- `MediaIngestionPort`: Contracts for fetching media transcripts (`ingest_channel`, `ingest_single_video`).
- `LLMTransformationPort`: Contract for generative transformations (`transform`).
- `VaultRepositoryPort`: Contracts for reading, writing, and indexing atomic notes and MOCs in the vault.
- `LedgerRepositoryPort`: Contract for tracking processed video IDs (`is_processed`, `mark_processed`).

---

## 6. Cross-Context State Strategy

- **Boundary Violations Check**: Passed. The Cresmo module does not access external database tables or violate other bounded contexts.
- **Consistency Model**: Eventual Consistency across pipeline stages. Each stage produces an immutable artifact checkpoint on disk, allowing idempotent resumption if interrupted.
- **Failure Modes & Resumption**: Checkpoints in `enriched/[Channel]/[Video_ID].json` (inventory + completed notes array) and `processed_cresmo.json` guarantee that failures in batch synthesis resume from the exact uncompleted entity without regenerating already processed notes.

---

## 7. Langfuse Ingestion Strategy (Mandatory AI Telemetry)

All calls through `LLMTransformationPort` will integrate clinical telemetry:
1. **Trace Taxonomy**:
   - `trace_id`: Derived deterministically as `cresmo-{content_id}`.
   - `session_id`: Unique execution run identifier (e.g. `run-YYYYMMDD-HHMMSS`).
   - `user_id`: Operator identifier.
   - `tags`: `["cresmo", category, channel_name, stage_name]`.
2. **Span Hierarchy**:
   - Trace Root: `PipelineRun` (overall execution).
   - Spans: `Stage_1_RawTranscript`, `Stage_2_GapFiller`, `Stage_3_Expander`, `Stage_4_Inventory`, `Stage_5_Batch`, `Stage_6_MOC`.
   - Child Generations: Each individual LLM call is wrapped in a Langfuse `generation` capturing prompt tokens, completion tokens, latency, model parameters, and raw inputs/outputs.
3. **Prompt Version Tracking**:
   - Every prompt template is registered in Langfuse with semantic versioning (`cresmo-stage2-gapfiller:v1`, `cresmo-stage3-expander-longitudinal:v1`, `cresmo-stage3-expander-synchronic:v1`, `cresmo-stage4-inventory:v1`, `cresmo-stage5-batch:v1`, `cresmo-stage6-moc:v1`).
4. **Score Schema & Blocking Thresholds**:

| Dimension | Evaluation Method | Threshold | Pipeline Blocking? |
|---|---|---|---|
| `faithfulness` | LLM-as-judge (factual alignment with raw transcript) | ≥ 0.80 | Yes |
| `relevance` | Semantic embedding similarity | ≥ 0.75 | Yes |
| `hallucination` | LLM-as-judge (zero unsupported assertions) | ≤ 0.10 | Yes |
| `toxicity` | Classifier / rule-based | ≤ 0.05 | Yes |

---

## 8. Compliance Checklist

- [x] Hexagonal Architecture layers respected (`domain/`, `application/`, `infrastructure/`, `presentation/`)
- [x] No framework or I/O dependencies in Domain layer
- [x] Domain model avoids Primitive Obsession (Value Objects for `ContentId`, `NoteTitle`, `NoteType`)
- [x] Entities enforce invariants at construction (always valid state)
- [x] Domain models separated from persistence representations
- [x] Test strategy defined (Hermetic unit tests, mutmut mutation coverage, Langfuse Evals)
- [x] Observability plan included (Prometheus golden signals + Langfuse telemetry)
- [x] Security assessed (prompt sanitization against jailbreaks, secure cookie storage)
- [x] Ubiquitous Language terms linked to `CONTEXT.md`

---

## 9. References

- Discovery Document: [`docs/legacy_discovery/DISCO-001-cresmo-ecosystem-archaeology.md`](../legacy_discovery/DISCO-001-cresmo-ecosystem-archaeology.md)
- Context & Ubiquitous Language: [`CONTEXT.md`](../../CONTEXT.md)
- Method Specification: [`.agents/skills/stangler-doctor/SKILL.md`](../../.agents/skills/stangler-doctor/SKILL.md)
