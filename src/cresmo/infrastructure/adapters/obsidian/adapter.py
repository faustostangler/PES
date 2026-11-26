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
from typing import Final

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import (
    AtomicNote,
    MapOfContent,
    StageTranscript,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    NoteTitle,
    RawIndexEntry,
)
from cresmo.infrastructure.adapters.obsidian.catalog import ChannelCatalogHandler
from cresmo.infrastructure.adapters.obsidian.mocs import MocVaultHandler
from cresmo.infrastructure.adapters.obsidian.notes import AtomicNoteVaultHandler
from cresmo.infrastructure.adapters.obsidian.transcripts import TranscriptVaultHandler

_MASTER_DIR_NAME: Final[str] = "master"
_MOCS_DIR_NAME: Final[str] = "MOCs"
_VAULT_INDEX_FILENAME: Final[str] = "_index.json"


class ObsidianVaultAdapter(VaultRepositoryPort):
    """Filesystem-backed Obsidian Second Brain vault adapter.

    Manages persistence for all stages of the knowledge synthesis pipeline, ensuring
    POSIX atomic file replacement, two-tier indexing (brain.csv and _index.json),
    and bi-directional WikiLink integrity.
    """

    def __init__(
        self,
        vault_dir: Path,
        data_dir: Path,
    ) -> None:
        self.vault_dir = Path(vault_dir).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.raw_dir = self.data_dir / StageName.RAW.value
        self.master_dir = self.data_dir / _MASTER_DIR_NAME
        self.mocs_dir = self.vault_dir / _MOCS_DIR_NAME
        self.index_path = self.vault_dir / _VAULT_INDEX_FILENAME

        self._transcripts = TranscriptVaultHandler(data_dir=self.data_dir)
        self._notes = AtomicNoteVaultHandler(
            vault_dir=self.vault_dir,
            index_path=self.index_path,
        )
        self._mocs = MocVaultHandler(
            vault_dir=self.vault_dir,
            mocs_dir=self.mocs_dir,
            master_dir=self.master_dir,
        )
        self._catalog = ChannelCatalogHandler(data_dir=self.data_dir)

    # --- Transcripts & Compendiums (ADR-058, ADR-059) ---

    def resolve_stage_dir(self, stage_name: str | StageName) -> Path:
        return self._transcripts.resolve_stage_dir(stage_name)

    def save_stage_transcript(
        self, stage_name: str | StageName, transcript: StageTranscript
    ) -> None:
        self._transcripts.save_stage_transcript(stage_name, transcript)

    def get_stage_transcript(
        self, stage_name: str | StageName, content_id: ContentId
    ) -> StageTranscript | None:
        return self._transcripts.get_stage_transcript(stage_name, content_id)

    def get_stage_files_for_channel(
        self, stage_name: str | StageName, channel_name: ChannelName
    ) -> list[Path]:
        return self._transcripts.get_stage_files_for_channel(stage_name, channel_name)

    # --- Atomic Notes ---

    def save_atomic_note(self, note: AtomicNote) -> None:
        self._notes.save_atomic_note(note)

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        return self._notes.get_all_atomic_notes()

    def update_index_entry(self, note: AtomicNote) -> None:
        self._notes.update_index_entry(note)

    def delete_atomic_note(self, note: AtomicNote) -> None:
        self._notes.delete_atomic_note(note)

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

    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        return self._catalog.get_indexed_video_ids_for_channel(channel_name)

    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        self._catalog.append_channel_index_entry(channel_name, entry)

    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        self._catalog.append_brain_csv_entry(entry)
