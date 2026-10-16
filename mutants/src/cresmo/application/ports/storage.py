"""Hexagonal Persistence Ports for Obsidian Vault and Ledger Repositories.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- ADR-003: Idempotent Content Ledger
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    LedgerEntry,
    NoteTitle,
    RawIndexEntry,
)


class VaultRepositoryPort(ABC):
    """Hexagonal Persistence Port for the Obsidian Second Brain vault and raw/enriched storage.

    Conforms to ADR-001 and SPEC-001. Enforces atomic file writes, YAML frontmatter serialization,
    tiered index synchronization (_index.json), and bidirectional WikiLink reconciliation.
    """

    @abstractmethod
    def save_transcript(self, transcript: SourceTranscript) -> None:
        """Persist source transcript to storage directory.

        Args:
            transcript: SourceTranscript domain aggregate containing verbatim text and metadata.
        """
        raise NotImplementedError("Persist source transcript atomically.")

    @abstractmethod
    def get_raw_transcript(self, content_id: ContentId) -> SourceTranscript | None:
        """Retrieve raw transcript by content ID.

        Args:
            content_id: Target unique content identifier.

        Returns:
            SourceTranscript aggregate or None if not present in storage.
        """
        raise NotImplementedError("Retrieve raw transcript by content ID.")

    @abstractmethod
    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory.

        Args:
            compendium: Validated multi-pass fluid prose compendium.
        """
        raise NotImplementedError("Persist enriched compendium atomically.")

    @abstractmethod
    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID.

        Args:
            content_id: Target unique content identifier.

        Returns:
            EnrichedCompendium aggregate or None if not present in storage.
        """
        raise NotImplementedError("Retrieve enriched compendium by content ID.")

    @abstractmethod
    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter.

        Args:
            note: Validated AtomicNote aggregate with taxonomy, tags, and WikiLinks.
        """
        raise NotImplementedError("Render frontmatter and persist atomic note atomically.")

    @abstractmethod
    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        """Retrieve atomic note by its canonical title.

        Args:
            title: Canonical NoteTitle of the target note.

        Returns:
            Parsed AtomicNote aggregate or None if not found.
        """
        raise NotImplementedError("Read and parse atomic note by title.")

    @abstractmethod
    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes currently persisted in the vault.

        Returns:
            List of all parsed AtomicNote aggregates.
        """
        raise NotImplementedError("Retrieve all atomic notes.")

    @abstractmethod
    def update_index_entry(self, note: AtomicNote) -> None:
        """Update master _index.json lookup index with note metadata and aliases.

        Args:
            note: AtomicNote providing title, slug, and alias keys for indexing.
        """
        raise NotImplementedError("Update _index.json atomically.")

    @abstractmethod
    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist or update Map of Content in vault/MOCs/.

        Args:
            moc: MapOfContent aggregate reconciling note cluster.
        """
        raise NotImplementedError("Persist Map of Content atomically.")

    @abstractmethod
    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries.

        Args:
            note: Target note to delete.
        """
        raise NotImplementedError("Delete atomic note.")

    @abstractmethod
    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        """Rewrite all inbound [[old_title]] links to [[new_title]] across vault markdown files.

        Args:
            old_title: Prior note title being renamed.
            new_title: Target canonical note title.

        Returns:
            Count of markdown files updated with rewritten links.
        """
        raise NotImplementedError("Rewrite wiki links.")

    @abstractmethod
    def remove_index_entry(self, key: str) -> None:
        """Remove specific canonical title or alias key from master _index.json.

        Args:
            key: Title or alias lookup key to purge.
        """
        raise NotImplementedError("Remove index entry.")

    @abstractmethod
    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all enriched markdown file paths for a given channel.

        Args:
            channel_name: Human-readable creator channel name.

        Returns:
            List of Path objects for all channel enriched markdown files.
        """
        raise NotImplementedError("Retrieve enriched file paths for channel.")

    @abstractmethod
    def save_master_document(
        self,
        channel_name: ChannelName,
        channel_category: str,
        part_number: int,
        content: str,
    ) -> Path:
        """Persist aggregated master document to master/<channel_category>/<channel_slug>_001.md.

        Args:
            channel_name: Creator channel name.
            channel_category: Macro taxonomy category name.
            part_number: 1-based sequential part number.
            content: Consolidated markdown document string.

        Returns:
            Path to the saved master document on disk.
        """
        raise NotImplementedError("Persist master document atomically.")

    @abstractmethod
    def clear_master_documents_for_channel(
        self,
        channel_name: ChannelName,
        channel_category: str,
    ) -> None:
        """Delete previous master parts for channel before writing fresh sequential parts.

        Args:
            channel_name: Channel name whose prior parts will be purged.
            channel_category: Macro category under which master files reside.
        """
        raise NotImplementedError("Clear previous master documents for channel.")

    @abstractmethod
    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        """Retrieve set of ContentIds already indexed in the channel's _canal.md.

        Args:
            channel_name: Channel identifier.

        Returns:
            Set of ContentId instances recorded in the channel raw index.
        """
        raise NotImplementedError("Retrieve indexed video IDs for channel.")

    @abstractmethod
    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/raw/<channel_name>/_canal.md atomically.

        Args:
            channel_name: Channel identifier.
            entry: RawIndexEntry value object.
        """
        raise NotImplementedError("Append entry to channel raw index.")

    @abstractmethod
    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/brain.csv atomically.

        Args:
            entry: RawIndexEntry value object.
        """
        raise NotImplementedError("Append entry to brain.csv.")

    @abstractmethod
    def get_channel_index_path(self, channel_name: ChannelName) -> Path:
        """Return absolute path to channel's _canal.md index file.

        Args:
            channel_name: Channel identifier.

        Returns:
            Path to the target _canal.md.
        """
        raise NotImplementedError("Return channel index path.")


class LedgerRepositoryPort(ABC):
    """Hexagonal Persistence Port for tracking processed content status and idempotency.

    Conforms to ADR-001 and ADR-003. Employs transactional SQLite WAL storage to guarantee
    zero duplicate LLM calls and reproducible execution audits.
    """

    @abstractmethod
    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages.

        Args:
            content_id: Target ContentId.

        Returns:
            True if marked COMPLETED in ledger; False otherwise.
        """
        raise NotImplementedError("Check processed ledger status.")

    @abstractmethod
    def mark_processed(self, content_id: ContentId) -> None:
        """Record content item as successfully processed.

        Args:
            content_id: ContentId to mark COMPLETED.
        """
        raise NotImplementedError("Record content ID in processed ledger.")

    @abstractmethod
    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically.

        Args:
            entry: LedgerEntry value object with timestamps and outcome status.
        """
        raise NotImplementedError("Persist ledger entry.")

    @abstractmethod
    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID.

        Args:
            content_id: ContentId lookup key.

        Returns:
            LedgerEntry or None if no record exists.
        """
        raise NotImplementedError("Retrieve ledger entry.")

    @abstractmethod
    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries.

        Args:
            limit: Maximum count of entries to return.

        Returns:
            List of LedgerEntry records ordered reverse-chronologically.
        """
        raise NotImplementedError("List ledger entries.")
