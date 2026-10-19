# ADR-043: Fluid Transcript Vault Persistence, Checkpointing, and Lineage Observability

**Status:** PROPOSED  
**Date:** 2026-10-18  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-009`](ADR-009-streaming-batch-source-discovery-producer-consumer.md), [`ADR-015`](ADR-015-artifact-segregation-and-exclusion-invariants.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-038`](ADR-038-pure-value-object-triad-composition.md), [`ADR-039`](ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md)

---

## 1. Context & Architectural Motivation

In [ADR-028](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), the Cresmo Knowledge Synthesis Engine decoupled Stage 1 linguistic detranscription (`fluid_prose`) from Stage 3 Socratic gap filling (`gap_filler`), introducing the `FluidTranscript` domain aggregate:

```
[Raw Ingestion] ──► [1. fluid_prose] ──► [2. raw_indexing] ──► [3. gap_filler] ──► [4. expansion] ...
```

### Architectural Deficiencies Identified:

1. **Transient Memory Fragility (Lack of Checkpointing):**
   In the current implementation of `TransformFluidProseUseCase` ([`src/cresmo/application/use_cases/transform_fluid_prose.py`](../../src/cresmo/application/use_cases/transform_fluid_prose.py)), `FluidTranscript` is constructed solely in memory and returned to the caller. `VaultRepositoryPort` ([`src/cresmo/application/ports/storage.py`](../../src/cresmo/application/ports/storage.py)) lacks methods to persist or retrieve `FluidTranscript`. If a downstream failure occurs in Stage 2 (`raw_indexing`), Stage 3 (`gap_filler`), or the quality judge gates, resuming execution requires re-invoking the generative LLM on the raw audio transcript, wasting API tokens and introducing unnecessary processing latency.
2. **Broken Data Lineage & Reduced Observability:**
   A central tenet of the Doctor Stangler Architecture Method is complete traceability across transformations:
   $$\texttt{data/raw/} \;\longrightarrow\; \texttt{data/fluid/} \;\longrightarrow\; \texttt{data/enriched/}$$
   Without persistent intermediate fluid prose, developers, domain experts, and automated calibration harnesses cannot inspect whether a factual or stylistic distortion originated during detranscription (Stage 1) or during Socratic expansion (Stage 3).
3. **Impedance to Decoupled Testing and Offline Calibration:**
   Offline calibration of Stage 2 (`gap_filler_judge`) and Stage 3 use cases requires authentic `FluidTranscript` inputs. Without a dedicated `data/fluid/` store, tests and tools must either mock the aggregate or synthesize synthetic approximations, drifting from production reality.

---

## 2. Decision

We extend the hexagonal storage architecture and the Obsidian Vault adapter to persist and retrieve `FluidTranscript` aggregates in a dedicated `data/fluid/` directory using POSIX atomic writes, canonical YAML frontmatter, and idempotent pipeline checkpointing.

### 2.1 Hexagonal Port Extension (`VaultRepositoryPort`)

In `src/cresmo/application/ports/storage.py`, `VaultRepositoryPort` gains two canonical persistence methods:

```python
@abstractmethod
def save_fluid_transcript(self, transcript: FluidTranscript) -> None:
    """Persist normalized fluid prose transcript directly into fluid/ directory with YAML frontmatter."""
    raise NotImplementedError("Persist fluid transcript atomically.")

@abstractmethod
def get_fluid_transcript(self, content_id: ContentId) -> FluidTranscript | None:
    """Retrieve normalized fluid prose transcript by content ID from fluid/ directory."""
    raise NotImplementedError("Retrieve fluid transcript by content ID.")

@abstractmethod
def get_fluid_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
    """Retrieve all persisted fluid transcript paths for a given channel."""
    raise NotImplementedError("List fluid transcripts by channel.")
```

### 2.2 Storage Layout & Invariants (`data/fluid/`)

In compliance with ADR-015 (Artifact Segregation and Exclusion Invariants):
- Directory Path: Configured via `CresmoSettings.fluid_dir` (default: `data/fluid`).
- File Path Pattern: `data/fluid/{channel_name}/{video_id}.md`
- Serialization Format:
  - Strict YAML frontmatter containing: `video_title`, `video_id`, `channel_name`, `channel_id`, `channel_category`, `url`, `video_date`, `video_description`.
  - Body: Pristine Markdown prose starting with `## `, conforming to `validate_fluid_prose_mechanical_invariants`.
- Atomic Writes: Utilizing `atomic_write(file_path, content)` via temporary file replacement to avoid partial writes during concurrent or interrupted executions.

### 2.3 Use Case Integration (`TransformFluidProseUseCase`)

Upon successful LLM transformation and post-processing in `TransformFluidProseUseCase.execute()`:
1. The resulting `FluidTranscript` is immediately persisted via `self.vault_port.save_fluid_transcript(fluid_transcript)` if `vault_port` is configured.
2. The aggregate is returned to the pipeline coordinator.

### 2.4 Idempotent Pipeline Checkpointing (`CresmoPipeline`)

In `CresmoPipeline`:
- Before invoking `TransformFluidProseUseCase`, the coordinator probes `vault_port.get_fluid_transcript(content_id)`.
- If an existing, non-empty `FluidTranscript` is found on disk and overwrite is not forced, the pipeline skips the LLM call and resumes directly into downstream stages (`raw_indexing` and `gap_filler`).

---

## 3. Alternatives Considered

| Alternative | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **Option A: Ephemeral In-Memory Only (Status Quo)** | Zero disk I/O, no filesystem footprint. | Zero crash resilience; pipeline restarts re-invoke LLM; impossible to inspect intermediate prose. | **REJECTED** |
| **Option B: Persist in `data/raw/` with Suffix (`_fluid.md`)** | Reuses existing `raw_dir`. | Violates ADR-015 (segregation of raw media lake); complicates glob patterns; risks accidental ingestion loops. | **REJECTED** |
| **Option C: Dedicated `data/fluid/` Store with Atomic Frontmatter (Proposed)** | 100% crash recovery; complete provenance audit trail; clean bounded context separation; zero token waste. | Minor disk footprint (~15 KB per transcript). | **ACCEPTED** |

---

## 4. Consequences

### Positive
- **Fault-Tolerant Checkpointing:** Any pipeline failure downstream of Stage 1 resumes without re-executing `fluid_prose` detranscription.
- **Diagnostic Clarity:** Engineers can diff `data/raw/{channel}/{id}.md` against `data/fluid/{channel}/{id}.md` to immediately evaluate detranscription quality.
- **Decoupled Conveyor Execution:** Stage 2 (`raw_indexing`) and Stage 3 (`gap_filler`) can run in independent batch jobs or CLI invocations without raw media dependencies.
- **Strict Adherence to 12-Factor App & DDD:** Explicit persistence port eliminates hidden state and volatile memory dependence.

### Negative / Trade-offs
- **Filesystem Footprint:** Additional directory `data/fluid/` requiring disk storage (~11 MB for 724 transcripts).
- **Maintenance Overhead:** Test doubles (`MockVaultRepository`) must implement the new port methods.

---

## 5. Compliance Verification & Acceptance Criteria

1. **Port Contract Test:** `tests/cresmo/unit/test_vault_repository.py` verifies `save_fluid_transcript` and `get_fluid_transcript` roundtrip fidelity.
2. **Frontmatter Integrity:** Frontmatter parses cleanly with `yaml.safe_load` and reconstitutes identical `FluidTranscript` metadata.
3. **Atomic Replacement:** Interrupted writes leave existing files intact.
4. **Pipeline Idempotency Test:** `test_pipeline_skips_fluid_prose_when_checkpoint_exists` proves zero LLM calls on second pass.
