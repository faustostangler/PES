"""Unit tests for Cresmo 6-Stage Use Cases.

Derived from SPEC-001 Section 4 (Acceptance Criteria Scenarios).
Pure, hermetic tests using Mock Ports (0 external I/O).
"""

import pytest

from cresmo.application.use_cases import (
    DiscoverAtomicInventoryUseCase,
    ExpandLongitudinalSynchronicUseCase,
    FillGapsFluidProseUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
)
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ContentId,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.mock_adapters import (
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


class TestStage1IngestRawTranscript:
    """SPEC-001 Scenario 1.1: Stage 1 Raw Transcript Ingestion."""

    def test_ingest_single_video_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Raw spoken audio transcript.",
        )
        ingestion_port = MockMediaIngestionPort(canned_transcript=canned)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=dQw4w9WgXcQ")

        assert result is not None
        assert result.content_id == cid
        assert vault_port.get_raw_transcript(cid) == canned


class TestStage2FillGapsFluidProse:
    """SPEC-001 Scenario 2.1: Stage 2 Socratic Gap Filler."""

    def test_fill_gaps_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Spoken text without structure.",
        )
        llm_response = (
            "# Teoria das Elites\n\n"
            "A circulação das elites postula que minorias organizadas governam maiorias.\n\n"
            "## Informações Complementares\n\n"
            "Dados empíricos e análises contextuais aprofundadas."
        )
        llm_port = MockLLMAdapter(responses=[llm_response, llm_response, llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        compendium = use_case.execute(raw, passes=3)

        assert compendium.content_id == cid
        assert compendium.title.value == "Teoria das Elites"
        assert vault_port.get_enriched_compendium(cid) == compendium


class TestStage3ExpandLongitudinalSynchronic:
    """SPEC-001 Scenario 3.1: Stage 3 Braudel & Jaspers Expansion."""

    def test_expand_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous prose body.",
            complementary_info="Complementary info.",
            pass_count=1,
        )
        llm_response = (
            "Expanded continuous prose integrating longue durée causal analysis and axial networks.\n\n"
            "## Informações Complementares\n\n"
            "Multi-secular historical indices and global trade matrices."
        )
        llm_port = MockLLMAdapter(responses=[llm_response, llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandLongitudinalSynchronicUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)

        assert updated.content_id == cid
        assert "longue durée" in updated.body
        assert vault_port.get_enriched_compendium(cid) == updated


class TestStage4DiscoverAtomicInventory:
    """SPEC-001 Scenario 4.1: Stage 4 Holistic Inventory Discovery."""

    def test_discover_inventory_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body describing Vilfredo Pareto and Gaetano Mosca.",
            complementary_info="Complementary info.",
        )
        llm_json = '[{"title": "Vilfredo Pareto", "type": "entity"}, {"title": "Oligarquia de Ferro", "type": "concept"}]'
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        inventory = use_case.execute(compendium)

        assert len(inventory.items) == 2
        titles = [t.value for t, _ in inventory.items]
        assert "Vilfredo Pareto" in titles
        assert "Oligarquia de Ferro" in titles


class TestStage5SynthesizeAtomicBatch:
    """SPEC-001 Scenario 5.1: Stage 5 Batched Atomic Synthesis."""

    def test_synthesize_batch_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body describing elites.",
            complementary_info="Complementary info.",
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))

        batch_json = (
            '[{"title": "Vilfredo Pareto", "type": "entity", '
            '"definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.", '
            '"direct_relations": ["Teoria das Elites"], '
            '"causal_matrix": {"cause": "Heterogeneidade social", "effect": "Substituição cíclica de lideranças"}}]'
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        note = notes[0]
        assert note.title.value == "Vilfredo Pareto"
        assert note.note_type == NoteType.ENTITY
        assert vault_port.get_atomic_note_by_title(NoteTitle("Vilfredo Pareto")) == note


class TestStage6ReconcileMOCs:
    """SPEC-001 Scenario 6.1: Stage 6 MOC Reconciliation."""

    def test_reconcile_mocs_success(self) -> None:
        vault_port = InMemoryVaultAdapter()
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador do conceito de circulação das elites políticas e econômicas.",
        )
        vault_port.save_atomic_note(note)

        moc_json = (
            '[{"title": "MOC Teoria Politica", "theme": "Ciência Política", '
            '"overview": "Mapeamento das teorias de liderança.", '
            '"associated_notes": ["Vilfredo Pareto"]}]'
        )
        llm_port = MockLLMAdapter(responses=[moc_json])

        use_case = ReconcileMOCsUseCase(llm_port, vault_port)
        mocs = use_case.execute()

        assert len(mocs) == 1
        moc = mocs[0]
        assert moc.title.value == "MOC Teoria Politica"
        assert NoteTitle("Vilfredo Pareto") in moc.associated_notes


class TestStageUseCasesEdgeCases:
    """Boundary conditions and exception branch coverage."""

    def test_fill_gaps_missing_complementary_info_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Spoken text without structure.",
        )
        llm_response = "# Teoria das Elites\n\nOnly body text without complementary info section."
        llm_port = MockLLMAdapter(responses=[llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        with pytest.raises(Exception):
            use_case.execute(raw, passes=1)

    def test_discover_inventory_non_list_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Body content.",
            complementary_info="Complementary info.",
        )
        llm_port = MockLLMAdapter(responses=['{"not_a_list": true}'])
        use_case = DiscoverAtomicInventoryUseCase(llm_port)

        with pytest.raises(Exception):
            use_case.execute(compendium)

    def test_discover_inventory_empty_items_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Body content.",
            complementary_info="Complementary info.",
        )
        llm_port = MockLLMAdapter(responses=['[]'])
        use_case = DiscoverAtomicInventoryUseCase(llm_port)

        with pytest.raises(Exception):
            use_case.execute(compendium)

    def test_synthesize_batch_non_list_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Body content.",
            complementary_info="Complementary info.",
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        llm_port = MockLLMAdapter(responses=['{"not_a_list": true}'])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port)
        with pytest.raises(Exception):
            use_case.execute(inv, compendium)
