# ADR-059: Monomorphic Vault Repository Port and Legacy Stage Method Elimination

## Status
ACCEPTED

## Context
Following ADR-054 (Unified Stage Transcript Envelope), ADR-057 (Monomorphic StageTranscript Envelope and Pure Triad Ingestion), and ADR-058 (Unified Stage Transcript Persistence and Dynamic Path Resolution), all stage transcripts across the conveyor pipeline (`raw`, `fluid_prose`, `gap_filler`, `long_expander`, `wide_expander`, etc.) are encapsulated by the single canonical domain aggregate `StageTranscript`, persisted dynamically at `data/{stage}/{channel_name}/{content_id}.md`.

However, `VaultRepositoryPort` (`src/cresmo/application/ports/storage.py`), `ObsidianVaultAdapter` (`src/cresmo/infrastructure/adapters/obsidian/adapter.py`), `TranscriptVaultHandler` (`src/cresmo/infrastructure/adapters/obsidian/transcripts.py`), and test mock adapters continued to retain six legacy methods:
1. `save_transcript(transcript)`
2. `get_raw_transcript(content_id)`
3. `save_fluid_transcript(transcript)`
4. `get_fluid_transcript(content_id)`
5. `save_enriched_compendium(compendium)`
6. `get_enriched_compendium(content_id)`

These methods introduced polymorphism divergence, interface bloat, and conceptual dissonance with the extensible conveyor pipeline.

## Decision

### 1. Prune Legacy Stage Methods from VaultRepositoryPort
Completely remove the 6 legacy stage methods from `VaultRepositoryPort`. All stage persistence and retrieval operations must strictly pass through:
- `save_stage_transcript(self, stage_name: str | StageName, transcript: StageTranscript) -> None`
- `get_stage_transcript(self, stage_name: str | StageName, content_id: ContentId) -> StageTranscript | None`

### 2. Prune Legacy Methods from Adapters
Remove all 6 legacy methods from:
- `ObsidianVaultAdapter`
- `TranscriptVaultHandler`
- `InMemoryVaultAdapter` (in tests)

In `InMemoryVaultAdapter`, stage persistence is stored in a unified monomorphic dictionary:
`stage_transcripts: dict[str, dict[str, StageTranscript]]`.

### 3. Migrate Application Call Sites
Update all pipeline components and use cases to the monomorphic API:
- `coordinator.py`: calls `vault_port.get_stage_transcript("gap_filler", content_id)`
- `transcript_loader.py`: calls `vault_port.save_stage_transcript("raw", transcript)`
- `run.py`: calls `vault_port.get_stage_transcript("raw", result.content_id)`
- Use cases (`expand_compendium.py`, `fill_gaps.py`, `ingest_raw_transcript.py`, `transform_fluid_prose.py`) invoke `save_stage_transcript` / `get_stage_transcript` with their respective stage string or `StageName` enum.

### 4. Update Test Suites
Migrate all unit tests asserting against `save_transcript`, `get_raw_transcript`, `save_enriched_compendium`, `get_enriched_compendium`, `save_fluid_transcript`, and `get_fluid_transcript` to use `save_stage_transcript` and `get_stage_transcript`.

---

## Consequences
- **Interface Segregation & Zero Redundancy**: `VaultRepositoryPort` surface area is reduced by ~120 lines of redundant method declarations.
- **Pure Monomorphic Contract**: All stages (built-in and future plugins) share identical persistence semantics.
- **SOTA-KISS Architecture**: Zero forwarding wrappers or deprecated aliases in production code.

