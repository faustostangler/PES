"""Application Ports (Abstract Base Classes) for the Cresmo Knowledge Synthesis context.

Defines the Hexagonal Ports that decouple business logic orchestration from infrastructure
adapters (media scraping, LLM APIs, Obsidian filesystem storage, and status ledgers).

[SKELETON STUB - BUILD-TO-LEARN]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    DiscoveredMediaItem,
    LedgerEntry,
    NoteTitle,
)


class MediaIngestionPort(ABC):
    """Port for media crawling, audio downloading, and subtitle/transcript ingestion."""

    @abstractmethod
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Fetch transcript or audio for a single video.

        Walkthrough:
        1. Query metadata for the target video URL.
        2. Attempt retrieval of native spoken captions (*-orig).
        3. If unavailable, download audio and run Whisper model.
        4. Return clean RawTranscript domain aggregate, or None if failed.
        """
        raise NotImplementedError("Step 1: Implement single video ingestion contract.")

    @abstractmethod
    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        """Crawl channel playlists and ingest new videos within lookback window.

        Walkthrough:
        1. Iterate through seed channel/playlist URLs.
        2. Identify videos published within lookback window not yet present in output_dir.
        3. Dispatch parallel downloads up to max_workers.
        4. Return sequence of newly ingested RawTranscript entities.
        """
        raise NotImplementedError("Step 1: Implement channels ingestion contract.")

    @abstractmethod
    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Query and discover media items from a channel or playlist feed within query constraints.

        Walkthrough:
        1. Resolve channel or playlist URL.
        2. Extract recent video metadata (content_id, title, published_at, url, channel_name).
        3. Filter by lookback window and return DiscoveredMediaItem list.
        """
        raise NotImplementedError("Step 1: Implement discover channel feed contract.")


class LLMTransformationPort(ABC):
    """Port defining contract for text generation and structured extraction."""

    @abstractmethod
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Execute text transformation contract given input prompt and optional system directive.

        Walkthrough:
        1. Receive prompt and configuration tunables.
        2. Send payload to underlying model client (e.g. Gemini, Ollama, Mock).
        3. Capture latency and token usage.
        4. Return generated response text.
        """
        raise NotImplementedError("Step 1: Implement LLM transformation contract.")


class VaultRepositoryPort(ABC):
    """Persistence port for the Obsidian Second Brain vault."""

    @abstractmethod
    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        """Persist raw transcript to raw storage directory.

        Walkthrough:
        1. Format YAML frontmatter with origin metadata.
        2. Write body to target channel directory atomically.
        """
        raise NotImplementedError("Step 1: Persist raw transcript atomically.")

    @abstractmethod
    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        """Retrieve raw transcript by content ID."""
        raise NotImplementedError("Step 1: Retrieve raw transcript by content ID.")

    @abstractmethod
    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory."""
        raise NotImplementedError("Step 1: Persist enriched compendium atomically.")

    @abstractmethod
    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID."""
        raise NotImplementedError("Step 1: Retrieve enriched compendium by content ID.")

    @abstractmethod
    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter."""
        raise NotImplementedError("Step 1: Render frontmatter and persist atomic note atomically.")

    @abstractmethod
    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        """Retrieve atomic note by its canonical title."""
        raise NotImplementedError("Step 1: Read and parse atomic note by title.")

    @abstractmethod
    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes currently persisted in the vault."""
        raise NotImplementedError("Step 1: Retrieve all atomic notes.")

    @abstractmethod
    def update_index_entry(self, note: AtomicNote) -> None:
        """Update master _index.json lookup index with note metadata and aliases."""
        raise NotImplementedError("Step 1: Update _index.json atomically.")

    @abstractmethod
    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist or update Map of Content in vault/MOCs/."""
        raise NotImplementedError("Step 1: Persist Map of Content atomically.")

    @abstractmethod
    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries."""
        raise NotImplementedError("Step 1: Delete atomic note.")

    @abstractmethod
    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        """Rewrite all inbound [[old_title]] links to [[new_title]] across all markdown files in vault/.

        Returns:
            Count of files updated.
        """
        raise NotImplementedError("Step 1: Rewrite wiki links.")

    @abstractmethod
    def remove_index_entry(self, key: str) -> None:
        """Remove specific canonical title or alias key from master _index.json."""
        raise NotImplementedError("Step 1: Remove index entry.")


class LedgerRepositoryPort(ABC):
    """Persistence port for tracking processed content status and idempotency."""

    @abstractmethod
    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        raise NotImplementedError("Step 1: Check processed ledger status.")

    @abstractmethod
    def mark_processed(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        raise NotImplementedError("Step 1: Record content ID in processed ledger.")

    @abstractmethod
    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        raise NotImplementedError("Step 1: Persist ledger entry.")

    @abstractmethod
    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        raise NotImplementedError("Step 1: Retrieve ledger entry.")

    @abstractmethod
    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        raise NotImplementedError("Step 1: List ledger entries.")


class PromptProviderPort(ABC):
    """Hexagonal Port for loading decoupled LLM prompt templates and skill documentation."""

    @abstractmethod
    def get_gap_filler_prompt(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        raise NotImplementedError

    @abstractmethod
    def get_long_expander_prompt(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        raise NotImplementedError

    @abstractmethod
    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        raise NotImplementedError

    @abstractmethod
    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        raise NotImplementedError

    @abstractmethod
    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        raise NotImplementedError

    @abstractmethod
    def get_mocs_prompt(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        raise NotImplementedError
