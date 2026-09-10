# Vault Repository & Persistence Architecture Specification

**Context**: Cresmo Knowledge Synthesis → Obsidian Second Brain  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION  
**Governing ADR**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  

---

## 1. Scope & Objective

Isolate all Obsidian Second Brain filesystem interactions behind a formal `VaultRepositoryPort`. The domain and application use cases will not perform direct file reading, writing, or directory creation (`Path.write_text()`, `os.mkdir`).

---

## 2. Port Contract (`VaultRepositoryPort`)

Defined in `src/cresmo/application/ports.py`:

```python
from abc import ABC, abstractmethod
from cresmo.domain.entities import AtomicNote, EnrichedCompendium, MapOfContent, RawTranscript
from cresmo.domain.value_objects import ContentId, NoteTitle


class VaultRepositoryPort(ABC):
    """Persistence port for the Obsidian Second Brain vault."""

    @abstractmethod
    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        """Persist raw transcript to raw storage directory."""
        raise NotImplementedError

    @abstractmethod
    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        """Retrieve raw transcript by content ID."""
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
1. File is written to a temporary file: `{file_path}.tmp.{uuid4().hex}`.
2. Flushed and synced to disk.
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
