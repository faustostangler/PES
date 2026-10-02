"""Obsidian Second Brain Vault Repository Adapter.

Implements VaultRepositoryPort using atomic filesystem writes, YAML frontmatter serialization,
and tiered index management. Acts as an Anti-Corruption Layer (ACL) shielding domain entities
from markdown serialization quirks.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-003: PES Production Architecture & Telemetry
    - SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    NoteTitle,
    NoteType,
    RawIndexEntry,
)
from cresmo.infrastructure.adapters.obsidian.catalog import ChannelCatalogHandler
from cresmo.infrastructure.adapters.obsidian.mocs import MocVaultHandler
from cresmo.infrastructure.adapters.obsidian.notes import AtomicNoteVaultHandler
from cresmo.infrastructure.adapters.obsidian.transcripts import TranscriptVaultHandler
from cresmo.infrastructure.adapters.obsidian.utils import (
    atomic_write,
)


class ObsidianVaultAdapter(VaultRepositoryPort):
    """Filesystem-backed Obsidian Second Brain vault adapter.

    Manages persistence for all stages of the knowledge synthesis pipeline, ensuring
    POSIX atomic file replacement, two-tier indexing (brain.csv and _index.json),
    and bi-directional WikiLink integrity.
    """

    def __init__(
        self,
        vault_dir: Path,
        raw_dir: Path,
        enriched_dir: Path,
        master_dir: Path | None = None,
        data_dir: Path | None = None,
        mocs_dir: Path | None = None,
        index_path: Path | None = None,
    ) -> None:
        self.vault_dir = Path(vault_dir).resolve()
        self.raw_dir = Path(raw_dir).resolve()
        self.enriched_dir = Path(enriched_dir).resolve()
        self.data_dir = Path(data_dir).resolve() if data_dir else self.raw_dir.parent
        self.master_dir = Path(master_dir).resolve() if master_dir else (self.data_dir / "master")

        self.mocs_dir = Path(mocs_dir).resolve() if mocs_dir else (self.vault_dir / "MOCs")
        self.index_path = (
            Path(index_path).resolve() if index_path else (self.vault_dir / "_index.json")
        )

        self._transcripts = TranscriptVaultHandler(
            raw_dir=self.raw_dir,
            enriched_dir=self.enriched_dir,
        )
        self._notes = AtomicNoteVaultHandler(
            vault_dir=self.vault_dir,
            index_path=self.index_path,
        )
        self._mocs = MocVaultHandler(
            vault_dir=self.vault_dir,
            mocs_dir=self.mocs_dir,
            master_dir=self.master_dir,
        )
        self._catalog = ChannelCatalogHandler(
            raw_dir=self.raw_dir,
            data_dir=self.data_dir,
        )

    def _atomic_write(self, target_path: Path, content: str) -> None:
        """Atomically write text content using temp-file replace pattern."""
        atomic_write(target_path, content)

    # --- Transcripts & Compendiums ---

    def save_raw_transcript(self, transcript: SourceTranscript) -> None:
        self._transcripts.save_raw_transcript(transcript)

    def get_raw_transcript(self, content_id: ContentId) -> SourceTranscript | None:
        return self._transcripts.get_raw_transcript(content_id)

    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        self._transcripts.save_enriched_compendium(compendium)

    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        return self._transcripts.get_enriched_compendium(content_id)

    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        return self._transcripts.get_enriched_files_for_channel(channel_name)

    # --- Atomic Notes ---

    @staticmethod
    def _get_note_subfolder(note_type: NoteType) -> str:
        return AtomicNoteVaultHandler.get_note_subfolder(note_type)

    def _get_note_path(self, note: AtomicNote) -> Path:
        return self._notes.get_note_path(note)

    def save_atomic_note(self, note: AtomicNote) -> None:
        self._notes.save_atomic_note(note)

    def _parse_atomic_note_file(self, file_path: Path) -> AtomicNote | None:
        return self._notes.parse_atomic_note_file(file_path)

    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        return self._notes.get_atomic_note_by_title(title)

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        return self._notes.get_all_atomic_notes()

    def update_index_entry(self, note: AtomicNote) -> None:
        self._notes.update_index_entry(note)

    def delete_atomic_note(self, note: AtomicNote) -> None:
        self._notes.delete_atomic_note(note)

    def remove_index_entry(self, key: str) -> None:
        self._notes.remove_index_entry(key)

    # --- MOCs & Master Documents ---

    def save_map_of_content(self, moc: MapOfContent) -> None:
        self._mocs.save_map_of_content(moc)

    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        return self._mocs.rewrite_wiki_links(old_title, new_title)

    def save_master_document(
        self,
        channel_name: ChannelName,
        channel_category: str,
        part_number: int,
        content: str,
    ) -> Path:
        return self._mocs.save_master_document(channel_name, channel_category, part_number, content)

    def clear_master_documents_for_channel(
        self,
        channel_name: ChannelName,
        channel_category: str,
    ) -> None:
        self._mocs.clear_master_documents_for_channel(channel_name, channel_category)

    # --- Catalog & Tabular Index ---

    def get_channel_index_path(self, channel_name: ChannelName) -> Path:
        return self._catalog.get_channel_index_path(channel_name)

    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        return self._catalog.get_indexed_video_ids_for_channel(channel_name)

    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        self._catalog.append_channel_index_entry(channel_name, entry)

    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        self._catalog.append_brain_csv_entry(entry)
