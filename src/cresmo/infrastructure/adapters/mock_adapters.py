"""Mock in-memory adapters for hermetic unit testing of Cresmo use cases.

Zero I/O, deterministic responses, capturing call histories for test assertions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cresmo.application.ports import (
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
    VaultRepositoryPort,
)
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


class MockMediaIngestionPort(MediaIngestionPort):
    """In-memory mock for MediaIngestionPort."""

    def __init__(
        self,
        canned_transcript: RawTranscript | None = None,
        canned_feed: list[DiscoveredMediaItem] | None = None,
    ) -> None:
        self.canned_transcript = canned_transcript
        self.canned_feed = canned_feed or []
        self.ingest_single_calls: list[str] = []
        self.ingest_channels_calls: list[list[str]] = []
        self.discover_calls: list[ChannelFeedQuery] = []

    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        self.discover_calls.append(query)
        return list(self.canned_feed)

    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        self.ingest_single_calls.append(video_url)
        return self.canned_transcript

    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        self.ingest_channels_calls.append(playlist_urls)
        return [self.canned_transcript] if self.canned_transcript else []


class MockLLMAdapter(LLMTransformationPort):
    """In-memory mock for LLMTransformationPort."""

    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.call_history: list[dict[str, Any]] = []

    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "Deterministic mock LLM response."


class InMemoryVaultAdapter(VaultRepositoryPort):
    """In-memory mock for VaultRepositoryPort."""

    def __init__(self) -> None:
        self.raw_transcripts: dict[str, RawTranscript] = {}
        self.compendiums: dict[str, EnrichedCompendium] = {}
        self.atomic_notes: dict[str, AtomicNote] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.mocs: dict[str, MapOfContent] = {}

    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        self.raw_transcripts[transcript.content_id.value] = transcript

    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        return self.raw_transcripts.get(content_id.value)

    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        self.compendiums[compendium.content_id.value] = compendium

    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        return self.compendiums.get(content_id.value)

    def save_atomic_note(self, note: AtomicNote) -> None:
        self.atomic_notes[note.title.value.lower()] = note

    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        return self.atomic_notes.get(title.value.lower())

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        return list(self.atomic_notes.values())

    def update_index_entry(self, note: AtomicNote) -> None:
        self.index_entries[note.title.value.lower()] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "aliases": list(note.aliases),
        }

    def save_map_of_content(self, moc: MapOfContent) -> None:
        self.mocs[moc.title.value.lower()] = moc


class InMemoryLedgerAdapter(LedgerRepositoryPort):
    """In-memory mock for LedgerRepositoryPort."""

    def __init__(self) -> None:
        self.processed_ids: set[str] = set()
        self.entries: dict[str, LedgerEntry] = {}

    def is_processed(self, content_id: ContentId) -> bool:
        return content_id.value in self.processed_ids

    def mark_processed(self, content_id: ContentId) -> None:
        self.processed_ids.add(content_id.value)

    def save_entry(self, entry: LedgerEntry) -> None:
        self.processed_ids.add(entry.content_id.value)
        self.entries[entry.content_id.value] = entry

    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        return self.entries.get(content_id.value)

    def list_entries(self, limit: int = 100, offset: int = 0) -> list[LedgerEntry]:
        return list(self.entries.values())[offset : offset + limit]
