# Vault Repository & Persistence Architecture Specification

**Context**: Cresmo Knowledge Synthesis → Obsidian Second Brain  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION (SYNCHRONIZED WITH ADR-026, ADR-028, ADR-031, ADR-038)  
**Governing ADRs**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-010`](../adr/ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-026`](../adr/ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-028`](../adr/ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-038`](../adr/ADR-038-pure-value-object-triad-composition.md)  

---

## 1. Scope & Objective

Isolate all Obsidian Second Brain filesystem interactions behind a formal `VaultRepositoryPort`. The domain and application use cases will not perform direct file reading, writing, or directory creation (`Path.write_text()`, `os.mkdir`).

Per [`ADR-026`](../adr/ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), port interfaces reside in dedicated modules under `src/cresmo/application/ports/` rather than monolithic files.

---

## 2. Port Contract (`VaultRepositoryPort`)

Defined in `src/cresmo/application/ports/vault.py`:

```python
from abc import ABC, abstractmethod
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    FluidTranscript,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.value_objects import ContentId, NoteTitle


class VaultRepositoryPort(ABC):
    """Persistence port for the Obsidian Second Brain vault."""

    @abstractmethod
    def save_source_transcript(self, transcript: SourceTranscript) -> None:
        """Persist canonical source transcript to raw storage directory.
        
        Supercedes legacy save_raw_transcript per ADR-010 and ADR-031.
        """
        raise NotImplementedError

    @abstractmethod
    def get_source_transcript(self, content_id: ContentId) -> SourceTranscript | None:
        """Retrieve canonical source transcript by content ID."""
        raise NotImplementedError

    @abstractmethod
    def save_fluid_transcript(self, transcript: FluidTranscript) -> None:
        """Persist Stage 1 normalized fluid prose transcript per ADR-028."""
        raise NotImplementedError

    @abstractmethod
    def get_fluid_transcript(self, content_id: ContentId) -> FluidTranscript | None:
        """Retrieve fluid transcript by content ID."""
        raise NotImplementedError

    @abstractmethod
    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory."""
        raise NotImplementedError

    @abstractmethod
    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID."""
        raise NotImplementedError

    @abstractmethod
    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter."""
        raise NotImplementedError

    @abstractmethod
    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        """Retrieve atomic note by its canonical title."""
        raise NotImplementedError

    @abstractmethod
    def update_index_entry(self, note: AtomicNote) -> None:
        """Update master _index.json lookup index with note metadata and aliases."""
        raise NotImplementedError

    @abstractmethod
    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist or update Map of Content in wiki/MOCs/."""
        raise NotImplementedError
```

---

## 3. Obsidian Vault Adapter Implementation Architecture

### 3.1 Atomic File Write Protocol
To prevent corrupted markdown files or partial writes:
1. File is written to a temporary file: `{file_path}.tmp.{uuid4().hex}` using safe temp paths per ADR-000 and ADR-026 Rule 4.
2. Flushed and synced to disk (`os.fsync`).
3. Atomically renamed to `{file_path}` using `os.replace`.

### 3.2 Standardized Markdown Serialization
The adapter handles the conversion from `AtomicNote` domain entity into Obsidian-compatible Markdown:
- Clean top-level YAML frontmatter (`type`, `content`, `domain`, `cluster`, `source`, `aliases`).
- Title heading `# [[{title}]]`.
- Structured H2 sections:
  - `## Definição & Análise Contextual`
  - `## Conexões & Relações Diretas`
  - `## Matriz Causal`
  - `## Redes de Conexão (Cross-Context)`

### 3.3 Index Governance (`_index.json`)
The adapter manages the tiered lookup file `wiki/_index.json`:
- Thread-safe JSON read and update.
- Maps `title.lower()` and each `alias.lower()` to the relative file path.
- Enables O(1) existence checks before synthesizing new entities.
