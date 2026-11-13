# ADR-058: Unified Stage Transcript Persistence and Dynamic Path Resolution

## Status
ACCEPTED

## Context
Following ADR-054 (Unified Stage Transcript Envelope) and ADR-057 (Monomorphic StageTranscript Envelope and Pure Triad Ingestion), all stage transcripts across the conveyor pipeline (`raw`, `fluid_prose`, `gap_filler`, and downstream stages such as `long_expander` and `wide_expander`) are represented by the single canonical domain aggregate `StageTranscript`.

However, the persistence layer in `TranscriptVaultHandler` (`src/cresmo/infrastructure/adapters/obsidian/transcripts.py`) retains triplicated legacy persistence code:
1. **Triplicated Persistence Routines**: Three separate methods exist (`save_transcript`, `save_fluid_transcript`, `save_enriched_compendium`), each duplicating frontmatter construction, string escaping, date formatting, and atomic file writing.
2. **Brittle Stage Dispatch**: `save_stage_transcript` and `get_stage_transcript` employ a hardcoded `match stage_name` dispatch restricted to `"raw"`, `"fluid_prose"`, and `"gap_filler"`. Adding new conveyor stages (e.g. `long_expander`, `wide_expander`, or custom stylers) raises `KeyError` unless new dedicated methods are manually implemented, violating the Open/Closed Principle (OCP).
3. **Hardcoded Directory Divergence**: Existing methods route to disparate directory attributes (`self.raw_dir`, `self.fluid_dir`, `self.enriched_dir`) with divergent folder naming conventions (`raw`, `fluid`, `enriched`), rather than adhering to a uniform, dynamic hierarchy: `data/{stage}/{channel_name}/{content_id}.md`.

## Decision

### 1. Unified Monomorphic Persistence Method
Consolidate `save_stage_transcript` into a single canonical engine:
```python
def save_stage_transcript(self, stage: str | StageName, transcript: StageTranscript) -> None:
```
- Resolves the stage identifier dynamically: `stage_key = stage.value if hasattr(stage, "value") else str(stage).strip()`.
- Resolves target path dynamically:
  `stage_dir = self.resolve_stage_dir(stage_key)`
  `file_path = stage_dir / sanitize_filename(transcript.channel.name) / f"{transcript.content.id.value}.md"`
- Generates canonical YAML frontmatter monomorphically via `_format_stage_frontmatter(transcript: StageTranscript, stage_name: str) -> str`.
- Preserves optional frontmatter properties (e.g., `pass_count` is included only when `transcript.pass_count is not None`).
- Writes atomically using POSIX temp-file rename (`atomic_write(file_path, content)`).

### 2. Dynamic Stage Directory Resolution
Implement `resolve_stage_dir(self, stage: str | StageName) -> Path`:
- Default resolution maps directly to `self.data_dir / stage_key` (yielding `data/{stage}/`).
- Maintains backward-compatible overrides when explicit directories are passed to constructor (`self.raw_dir` for `"raw"`, `self.fluid_dir` for `"fluid"` or `"fluid_prose"`, `self.enriched_dir` for `"enriched"` or `"gap_filler"`).

### 3. Unified Monomorphic Retrieval
Consolidate `get_stage_transcript(self, stage: str | StageName, content_id: ContentId) -> StageTranscript | None`:
- Searches dynamically within `self.resolve_stage_dir(stage)` using glob `**/{content_id.value}.md`.
- Parses canonical frontmatter using `_FRONTMATTER_PATTERN` and reconstructs the `StageTranscript` domain aggregate with pure Value Object triad (`Channel`, `MediaProvenance`, `Content`).

### 4. Thin Backward-Compatibility Delegation Wrappers
To avoid breaking changes for existing callers and legacy test suites:
- `save_transcript(transcript)` delegates to `save_stage_transcript("raw", transcript)`.
- `save_fluid_transcript(transcript)` delegates to `save_stage_transcript("fluid_prose", transcript)`.
- `save_enriched_compendium(compendium)` delegates to `save_stage_transcript("gap_filler", compendium)`.
- `get_raw_transcript(content_id)` delegates to `get_stage_transcript("raw", content_id)`.
- `get_fluid_transcript(content_id)` delegates to `get_stage_transcript("fluid_prose", content_id)`.
- `get_enriched_compendium(content_id)` delegates to `get_stage_transcript("gap_filler", content_id)`.

## Consequences
- **Zero Duplication (DRY & SOTA-KISS)**: Eliminates ~150 lines of duplicate serialization boilerplate.
- **Open/Closed Principle (OCP)**: Any new pipeline stage automatically gains persistence and retrieval capabilities without modifying `TranscriptVaultHandler`.
- **Pure Monomorphic Triad**: Enforces uniform markdown frontmatter and body structure across all conveyor stages.
- **Zero Breaking Changes**: Existing callers and test suites retain full functional compatibility via zero-cost delegation.

