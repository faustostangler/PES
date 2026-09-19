"""Unit tests for mock infrastructure adapters.

Ensures test doubles (MockMediaIngestionPort, MockLLMAdapter, InMemoryVaultAdapter,
InMemoryLedgerAdapter) strictly respect port contracts and behavior under mutation testing.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ChannelFeedQuery,
    ContentId,
    CrossContextRelations,
    DiscoveredMediaItem,
    LedgerEntry,
    NoteTitle,
    NoteType,
    PipelineStatus,
)
from tests.doubles.mock_adapters import (
    InMemoryLedgerAdapter,
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


def _create_sample_note(
    title: str, definition: str = "A valid definition with at least twenty characters."
) -> AtomicNote:
    return AtomicNote(
        title=NoteTitle(title),
        note_type=NoteType.CONCEPT,
        definition=definition,
        direct_relations=(),
        causal_matrix=CausalMatrix(cause="", effect=""),
        cross_context=CrossContextRelations(),
    )


class TestMockMediaIngestionPort:
    """Verifies in-memory MockMediaIngestionPort contract compliance."""

    def test_discover_channel_feed_records_call_and_returns_copy(self) -> None:
        item = DiscoveredMediaItem(
            content_id=ContentId("sampleFeed01"),
            title="Sample Video",
            published_at=datetime.now(UTC),
            media_url="https://youtube.com/watch?v=sampleFeed01",
            channel_name="Sample Channel",
        )
        port = MockMediaIngestionPort(canned_feed=[item])
        query = ChannelFeedQuery(channel_url="https://youtube.com/@Sample")

        feed = port.discover_channel_feed(query)
        assert len(feed) == 1
        assert feed[0].content_id.value == "sampleFeed01"
        assert len(port.discover_calls) == 1
        assert port.discover_calls[0].channel_url == "https://youtube.com/@Sample"

    def test_ingest_single_video_records_and_returns_canned(self, tmp_path: Path) -> None:
        cid = ContentId("singleVid123")
        transcript = RawTranscript(
            content_id=cid,
            channel_name="Channel",
            body="Spoken text",
        )
        port = MockMediaIngestionPort(canned_transcript=transcript)
        result = port.ingest_single_video(
            video_url="https://youtube.com/watch?v=singleVid123",
            output_dir=tmp_path,
            whisper_model="tiny",
            keep_audio=True,
        )
        assert result is transcript
        assert port.ingest_single_calls == ["https://youtube.com/watch?v=singleVid123"]

    def test_extract_channel_url_from_video(self) -> None:
        port = MockMediaIngestionPort()
        assert port.extract_channel_url_from_video("https://yt.com/watch?v=123") is None

        port.canned_channel_url = "https://yt.com/@ExplicitChan"
        assert (
            port.extract_channel_url_from_video("https://yt.com/watch?v=123")
            == "https://yt.com/@ExplicitChan"
        )


class TestMockLLMAdapter:
    """Verifies in-memory MockLLMAdapter responses and call tracking."""

    def test_transform_default_and_canned_responses(self) -> None:
        adapter = MockLLMAdapter(responses=["First Response", "Second Response"])
        r1 = adapter.transform(prompt="Prompt 1", system_instruction="Sys 1", temperature=0.7)
        assert r1 == "First Response"

        r2 = adapter.transform(prompt="Prompt 2")
        assert r2 == "Second Response"

        # Defaults when responses empty
        r3 = adapter.transform(prompt="Prompt 3")
        assert r3 == "Deterministic mock LLM response."

        assert len(adapter.call_history) == 3
        assert adapter.call_history[0]["prompt"] == "Prompt 1"
        assert adapter.call_history[0]["system_instruction"] == "Sys 1"
        assert adapter.call_history[0]["temperature"] == 0.7


class TestInMemoryVaultAdapter:
    """Verifies in-memory VaultRepositoryPort implementations and link rewriting."""

    def test_raw_transcript_crud(self) -> None:
        vault = InMemoryVaultAdapter()
        cid = ContentId("transTest123")
        raw = RawTranscript(content_id=cid, channel_name="Ch", body="Text")
        assert vault.get_raw_transcript(cid) is None

        vault.save_raw_transcript(raw)
        assert vault.get_raw_transcript(cid) is raw

    def test_enriched_compendium_crud(self) -> None:
        vault = InMemoryVaultAdapter()
        cid = ContentId("compTest123")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name="Ch",
            title=NoteTitle("T"),
            body="Body",
            complementary_info="Info",
        )
        assert vault.get_enriched_compendium(cid) is None

        vault.save_enriched_compendium(comp)
        assert vault.get_enriched_compendium(cid) is comp

    def test_atomic_note_and_index_crud(self) -> None:
        vault = InMemoryVaultAdapter()
        note = _create_sample_note("Concept Alpha")
        assert vault.get_atomic_note_by_title(NoteTitle("Concept Alpha")) is None

        vault.save_atomic_note(note)
        assert vault.get_atomic_note_by_title(NoteTitle("concept alpha")) is note
        assert len(vault.get_all_atomic_notes()) == 1

        vault.update_index_entry(note)
        assert "concept alpha" in vault.index_entries
        assert vault.index_entries["concept alpha"]["title"] == "Concept Alpha"

        vault.delete_atomic_note(note)
        assert vault.get_atomic_note_by_title(NoteTitle("Concept Alpha")) is None
        assert "concept alpha" not in vault.index_entries

    def test_save_map_of_content(self) -> None:
        vault = InMemoryVaultAdapter()
        moc = MapOfContent(
            title=NoteTitle("MOC History"),
            theme="History",
            overview="An overview",
            associated_notes=(NoteTitle("Note A"),),
        )
        vault.save_map_of_content(moc)
        assert vault.mocs.get("moc history") is moc

    def test_rewrite_wiki_links_renames_in_definition_and_direct_relations(self) -> None:
        vault = InMemoryVaultAdapter()
        note1 = AtomicNote(
            title=NoteTitle("Target Concept"),
            note_type=NoteType.CONCEPT,
            definition="Points to [[Old Concept]] and also [[Old Concept|custom alias]].",
            direct_relations=(NoteTitle("Old Concept"), NoteTitle("Other Note")),
            causal_matrix=CausalMatrix(cause="", effect=""),
            cross_context=CrossContextRelations(),
        )
        vault.save_atomic_note(note1)

        # Same title returns 0
        assert vault.rewrite_wiki_links(NoteTitle("Same"), NoteTitle("Same")) == 0

        # Rename Old Concept -> New Concept
        updated_count = vault.rewrite_wiki_links(NoteTitle("Old Concept"), NoteTitle("New Concept"))
        assert updated_count == 1

        updated_note = vault.get_atomic_note_by_title(NoteTitle("Target Concept"))
        assert updated_note is not None
        assert "[[New Concept]]" in updated_note.definition
        assert "[[New Concept|custom alias]]" in updated_note.definition
        assert NoteTitle("New Concept") in updated_note.direct_relations
        assert NoteTitle("Old Concept") not in updated_note.direct_relations


class TestInMemoryLedgerAdapter:
    """Verifies in-memory LedgerRepositoryPort implementations."""

    def test_ledger_processed_tracking(self) -> None:
        ledger = InMemoryLedgerAdapter()
        cid = ContentId("ledgerId001")
        assert ledger.is_processed(cid) is False

        ledger.mark_processed(cid)
        assert ledger.is_processed(cid) is True

    def test_ledger_entries_crud_and_pagination(self) -> None:
        ledger = InMemoryLedgerAdapter()
        entry1 = LedgerEntry(
            content_id=ContentId("entryOne001"),
            media_url="https://yt.com/1",
            title="Video 1",
            channel_name="Ch",
            status=PipelineStatus.COMPLETED,
        )
        entry2 = LedgerEntry(
            content_id=ContentId("entryTwo002"),
            media_url="https://yt.com/2",
            title="Video 2",
            channel_name="Ch",
            status=PipelineStatus.COMPLETED,
        )

        assert ledger.get_entry(entry1.content_id) is None

        ledger.save_entry(entry1)
        ledger.save_entry(entry2)

        assert ledger.is_processed(entry1.content_id) is True
        assert ledger.get_entry(entry1.content_id) == entry1

        # Pagination
        assert len(ledger.list_entries(limit=1, offset=0)) == 1
        assert len(ledger.list_entries(limit=10, offset=0)) == 2
        assert len(ledger.list_entries(limit=10, offset=2)) == 0
