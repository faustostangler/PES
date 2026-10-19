# SPEC-043: Fluid Transcript Persistence and Checkpointing Specification

**Context:** Cresmo Knowledge Synthesis  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** PROPOSED SPECIFICATION  
**Governing ADR:** [`ADR-043`](../adr/ADR-043-fluid-transcript-vault-persistence-and-checkpointing.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`SPEC-011`](SPEC-011-fluid-prose-detranscription-and-gap-filler-decoupling.md)

---

## 1. Storage & Configuration Invariants

### 1.1 Directory Structure & Invariants
- `CresmoSettings` gains property `fluid_dir: Path`, returning `self.data_dir / "fluid"`.
- Layout: `data/fluid/{sanitized_channel_name}/{content_id}.md`.
- Invariant 1: File writes must be atomic via `atomic_write` temp-file replacement.
- Invariant 2: Overwrite behavior must be explicit and deterministic.

### 1.2 Serialization Contract (YAML Frontmatter + Markdown Body)
The persisted `.md` file must strictly adhere to the following schema:
```markdown
---
video_title: "{escaped_title}"
video_id: {content_id}
channel_name: "{escaped_channel}"
channel_id: {channel_id}
channel_category: "{channel_category}"
url: {source_url}
video_date: {YYYYMMDD}
video_description: |
  {indented_description}
---

{fluid_body_starting_with_h2}
```
- Invariant 3: `body` must begin with `## ` on Line 1 after frontmatter.
- Invariant 4: No Markdown tables and no em-dashes (`—`).

---

## 2. Hexagonal Port Specifications

### 2.1 `VaultRepositoryPort` (`src/cresmo/application/ports/storage.py`)
```python
@abstractmethod
def save_fluid_transcript(self, transcript: FluidTranscript) -> None:
    """Persist normalized fluid prose transcript directly into fluid/ directory with YAML frontmatter."""

@abstractmethod
def get_fluid_transcript(self, content_id: ContentId) -> FluidTranscript | None:
    """Retrieve normalized fluid prose transcript by content ID from fluid/ directory."""

@abstractmethod
def get_fluid_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
    """Retrieve all persisted fluid transcript paths for a given channel."""
```

### 2.2 `TranscriptVaultHandler` & `ObsidianVaultAdapter` (`src/cresmo/infrastructure/adapters/obsidian/`)
- `TranscriptVaultHandler.__init__` accepts `fluid_dir: Path | None = None` (defaulting to `raw_dir.parent / "fluid"`).
- `save_fluid_transcript`:
  - Sanitizes channel subfolder.
  - Generates YAML frontmatter and joins with `transcript.content.body`.
  - Performs atomic write.
- `get_fluid_transcript`:
  - Searches `self.fluid_dir.glob(f"**/{content_id.value}.md")`.
  - If match found, parses frontmatter via `yaml.safe_load`.
  - Reconstitutes `FluidTranscript` aggregate with value objects `Channel`, `MediaProvenance`, and `Content`.
  - Returns `None` if no match or corrupted file.

---

## 3. Use Case & Coordinator Integration

### 3.1 `TransformFluidProseUseCase` (`src/cresmo/application/use_cases/transform_fluid_prose.py`)
- In `execute()`:
  - If `self.vault_port is not None`:
    `self.vault_port.save_fluid_transcript(fluid_transcript)`
  - Returns `fluid_transcript`.

### 3.2 `CresmoPipeline` Checkpoint Execution (`src/cresmo/application/pipeline/coordinator.py`)
- In Stage 1 execution:
  - If `force_refresh is False`:
    `cached = self.vault_port.get_fluid_transcript(content_id)`
    - If `cached is not None`:
      Logs debug message and reuses `cached` without calling LLM.

---

## 4. Test Specifications (Refractometry Test Cases)

1. `test_vault_save_and_get_fluid_transcript_roundtrip`:
   - Persists a `FluidTranscript` with metadata and body.
   - Retrieves it via `get_fluid_transcript`.
   - Asserts exact equality across `content_id`, `channel.name`, `content.body`, `content.title`, and `provenance`.
2. `test_vault_get_fluid_transcript_returns_none_when_absent`:
   - Inquires for non-existent `ContentId`.
   - Asserts return value is `None`.
3. `test_transform_fluid_prose_use_case_persists_to_vault`:
   - Mocks `LLMTransformationPort` and provides `MockVaultRepository`.
   - Executes `TransformFluidProseUseCase`.
   - Asserts `mock_vault.save_fluid_transcript` was invoked with the generated `FluidTranscript`.
4. `test_pipeline_fluid_prose_checkpoint_skips_llm`:
   - Pre-seeds vault with `FluidTranscript`.
   - Runs pipeline on source.
   - Asserts `llm_synthesis_port.transform` was called 0 times for `fluid_prose`.
