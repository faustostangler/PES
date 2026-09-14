"""Unit tests for Cresmo 6-Stage Use Cases.

Derived from SPEC-001 Section 4 (Acceptance Criteria Scenarios).
Pure, hermetic tests using Mock Ports (0 external I/O) with strict port verification.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from cresmo.application.use_cases import (
    DiscoverAtomicInventoryUseCase,
    ExpandLongitudinalSynchronicUseCase,
    FillGapsFluidProseUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
)
from cresmo.application.use_cases.synthesize_atomic_batch import _norm_honorific
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    RawTranscript,
)
from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.mock_adapters import (
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


class TestNormHonorific:
    """Tests for honorific prefix stripping and title normalization."""

    @pytest.mark.parametrize(
        ("raw_title", "expected"),
        [
            ("Dom Pedro II", "pedro ii"),
            ("dom pedro ii", "pedro ii"),
            ("Dona Leopoldina", "leopoldina"),
            ("dona leopoldina", "leopoldina"),
            ("D. Pedro I", "pedro i"),
            ("d. manuel", "manuel"),
            ("d joão", "joão"),
            ("Vilfredo Pareto", "vilfredo pareto"),
            ("Oligarquia - de. Ferro, (conceito)", "oligarquia de ferro conceito"),
            ("   ", ""),
        ],
    )
    def test_norm_honorific_permutations(self, raw_title: str, expected: str) -> None:
        assert _norm_honorific(raw_title) == expected


class TestIngestRawTranscript:
    """SPEC-001 Scenario 1.1: Raw Transcript Ingestion."""

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
        assert ingestion_port.ingest_single_calls == ["https://youtube.com/watch?v=dQw4w9WgXcQ"]

    def test_ingest_single_video_none_returns_none(self) -> None:
        ingestion_port = MockMediaIngestionPort(canned_transcript=None)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=missing123")

        assert result is None
        assert len(vault_port.raw_transcripts) == 0


class TestFillGapsFluidProse:
    """SPEC-001 Scenario 2.1: Socratic Gap Filler."""

    def test_fill_gaps_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Spoken text without structure.",
            upload_date=datetime(2023, 5, 17, 12, 0, tzinfo=UTC),
            channel_id="UC123456",
            source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
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
        assert compendium.channel_name == "Example Channel"
        assert compendium.channel_id == "UC123456"
        assert compendium.video_date == "20230517"
        assert compendium.source_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert (
            compendium.body
            == "A circulação das elites postula que minorias organizadas governam maiorias."
        )
        assert (
            compendium.complementary_info == "Dados empíricos e análises contextuais aprofundadas."
        )
        assert compendium.pass_count == 3
        assert vault_port.get_enriched_compendium(cid) == compendium

        # Verify strict behavioral port interactions
        assert len(llm_port.call_history) == 3
        # Pass 1 contains raw body and channel name
        assert "Spoken text without structure." in llm_port.call_history[0]["prompt"]
        assert "Example Channel" in llm_port.call_history[0]["prompt"]
        # Pass 2 and 3 receive current_text from previous pass
        assert "A circulação das elites" in llm_port.call_history[1]["prompt"]
        assert "A circulação das elites" in llm_port.call_history[2]["prompt"]

    def test_fill_gaps_title_fallback_to_raw_transcript_title(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Raw spoken text.",
            title="Raw Video Title",
        )
        llm_response = (
            "Body text without an H1 markdown title.\n\n"
            "## Informações Complementares\n\n"
            "Complementary details."
        )
        llm_port = MockLLMAdapter(responses=[llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        compendium = use_case.execute(raw, passes=1)

        assert compendium.title.value == "Raw Video Title"

    def test_fill_gaps_title_fallback_to_default_when_no_raw_title(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Raw spoken text.",
            title="",
        )
        llm_response = (
            "Body text without H1 header.\n\n## Notas Complementares\n\nComplementary details."
        )
        llm_port = MockLLMAdapter(responses=[llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        compendium = use_case.execute(raw, passes=1)

        assert compendium.title.value == "Untitled Compendium"
        assert compendium.complementary_info == "Complementary details."

    def test_fill_gaps_alternative_regex_header_informacoes_adicionais(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Raw spoken text.",
        )
        llm_response = (
            "# H1 Title\n\n"
            "Primary text.\n\n"
            "### Informações Adicionais\n\n"
            "Additional notes and context."
        )
        llm_port = MockLLMAdapter(responses=[llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        compendium = use_case.execute(raw, passes=1)

        assert compendium.title.value == "H1 Title"
        assert compendium.body == "Primary text."
        assert compendium.complementary_info == "Additional notes and context."

    def test_fill_gaps_empty_complementary_section_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Raw spoken text.",
        )
        llm_response = "# H1 Title\n\nPrimary text.\n\n## Informações Complementares\n\n   "
        llm_port = MockLLMAdapter(responses=[llm_response])
        vault_port = InMemoryVaultAdapter()

        use_case = FillGapsFluidProseUseCase(llm_port, vault_port)
        with pytest.raises(CompendiumStructureError, match="must contain a non-empty"):
            use_case.execute(raw, passes=1)


class TestExpandLongitudinalSynchronic:
    """SPEC-001 Scenario 3.1: Braudel & Jaspers Expansion."""

    def test_expand_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous prose body describing elites.",
            complementary_info="Initial complementary info.",
            pass_count=1,
            channel_id="UC_Test",
            source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        )
        long_response = (
            "# Teoria das Elites (Longitudinal)\n\n"
            "Longitudinal analysis tracing Roman patricians through medieval baronies.\n\n"
            "## Informações Complementares\n\n"
            "Longitudinal footnotes and multi-secular metrics."
        )
        wide_response = (
            "# Teoria das Elites (Synchronic)\n\n"
            "Expanded continuous prose integrating longue durée causal analysis and axial networks.\n\n"
            "## Informações Complementares\n\n"
            "Multi-secular historical indices and global trade matrices."
        )
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandLongitudinalSynchronicUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)

        assert updated.content_id == cid
        assert updated.pass_count == 2
        assert updated.channel_id == "UC_Test"
        assert updated.source_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert "longue durée" in updated.body
        # Leading H1 must be stripped from body
        assert not updated.body.startswith("#")
        assert (
            updated.complementary_info
            == "Multi-secular historical indices and global trade matrices."
        )
        assert vault_port.get_enriched_compendium(cid) == updated

        # Verify strict port interactions
        assert len(llm_port.call_history) == 2
        # Pass 1: Longitude expander gets initial compendium body and complementary info
        assert "Continuous prose body describing elites." in llm_port.call_history[0]["prompt"]
        assert "Initial complementary info." in llm_port.call_history[0]["prompt"]
        # Pass 2: Wide expander gets the response from longitudinal expansion
        assert (
            "Longitudinal analysis tracing Roman patricians" in llm_port.call_history[1]["prompt"]
        )

    def test_expand_missing_complementary_tag_falls_back_to_original(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous prose body.",
            complementary_info="Original complementary info.",
        )
        long_response = "Long response without section header."
        wide_response = "Wide response without section header."
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandLongitudinalSynchronicUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)

        assert updated.body == "Wide response without section header."
        assert updated.complementary_info == "Original complementary info."

    def test_expand_empty_complementary_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous prose body.",
            complementary_info="Initial complementary info.",
        )
        long_response = "Long response."
        wide_response = "Wide response text.\n\n## Informações Complementares\n\n   "
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandLongitudinalSynchronicUseCase(llm_port, vault_port)
        with pytest.raises(
            CompendiumStructureError, match="Missing complementary info in expansion"
        ):
            use_case.execute(initial_compendium)


class TestDiscoverAtomicInventory:
    """SPEC-001 Scenario 4.1: Holistic Inventory Discovery."""

    def test_discover_inventory_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body describing Vilfredo Pareto and Gaetano Mosca.",
            complementary_info="Complementary info.",
        )
        llm_json = json.dumps(
            [
                {"title": "Vilfredo Pareto", "type": "entity"},
                {"title": "Oligarquia de Ferro", "type": "concept"},
            ]
        )
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        inventory = use_case.execute(compendium)

        assert len(inventory.items) == 2
        titles = [t.value for t, _ in inventory.items]
        assert "Vilfredo Pareto" in titles
        assert "Oligarquia de Ferro" in titles

        # Verify strict behavioral port verification
        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert call["temperature"] == 0.0
        assert "Teoria das Elites" in call["prompt"]
        assert "Example Channel" in call["prompt"]
        assert "Continuous body describing Vilfredo Pareto" in call["prompt"]

    def test_discover_inventory_deduplicates_case_insensitively(self) -> None:
        cid = ContentId("dQw4w9XcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Body content.",
            complementary_info="Complementary info.",
        )
        llm_json = json.dumps(
            [
                {"title": "Vilfredo Pareto", "type": "entity"},
                {"title": "vilfredo pareto", "type": "concept"},
                {"title": "VILFREDO PARETO", "type": "entity"},
            ]
        )
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        inventory = use_case.execute(compendium)

        assert len(inventory.items) == 1
        assert inventory.items[0][0].value == "Vilfredo Pareto"

    def test_discover_inventory_skips_malformed_entries_and_defaults_type(self) -> None:
        cid = ContentId("dQw4w9XcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Body content.",
            complementary_info="Complementary info.",
        )
        llm_json = json.dumps(
            [
                "string_entry_not_dict",
                123,
                {"missing_title": True},
                {"title": ""},
                {"title": 12345},
                {"title": "Unrecognized Typology", "type": "unknown_fantasy_type"},
            ]
        )
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        inventory = use_case.execute(compendium)

        assert len(inventory.items) == 1
        title, note_type = inventory.items[0]
        assert title.value == "Unrecognized Typology"
        assert note_type == NoteType.CONCEPT


class TestSynthesizeAtomicBatch:
    """SPEC-001 Scenario 5.1: Batched Atomic Synthesis."""

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

        batch_json = json.dumps(
            [
                {
                    "title": "Vilfredo Pareto",
                    "type": "entity",
                    "definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.",
                    "direct_relations": ["Teoria das Elites"],
                    "causal_matrix": {
                        "cause": "Heterogeneidade social",
                        "effect": "Substituição cíclica de lideranças",
                        "epistemic_attribution": "Tratado Geral de Sociologia",
                    },
                    "cross_context": {
                        "precursors": "Maquiavel",
                        "lateral_events": "Revolução Marginalista",
                        "aftermath": "Fascismo italiano",
                    },
                    "aliases": ["Pareto", "V. Pareto"],
                    "content_tags": ["sociologia", "elites"],
                    "domain": "Ciência Política",
                    "cluster": "Teoria das Elites",
                    "source": "Teoria das Elites",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        note = notes[0]
        assert note.title.value == "Vilfredo Pareto"
        assert note.note_type == NoteType.ENTITY
        assert note.domain == "Ciência Política"
        assert note.cluster == "Teoria das Elites"
        assert note.source == "Teoria das Elites"
        assert note.aliases == ("Pareto", "V. Pareto")
        assert note.content_tags == ("sociologia", "elites")
        assert note.direct_relations == (NoteTitle("Teoria das Elites"),)
        assert note.causal_matrix == CausalMatrix(
            cause="Heterogeneidade social",
            effect="Substituição cíclica de lideranças",
            epistemic_attribution="Tratado Geral de Sociologia",
        )
        assert note.cross_context == CrossContextRelations(
            precursors="Maquiavel",
            lateral_events="Revolução Marginalista",
            aftermath="Fascismo italiano",
        )
        assert vault_port.get_atomic_note_by_title(NoteTitle("Vilfredo Pareto")) == note

        # Verify strict port interactions
        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert "Teoria das Elites" in call["prompt"]
        assert "Example Channel" in call["prompt"]
        assert "Continuous body describing elites." in call["prompt"]
        assert "Vilfredo Pareto" in call["prompt"]

    def test_synthesize_batch_existing_note_exact_match_skips_llm(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body describing elites.",
            complementary_info="Complementary info.",
        )
        existing = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Existing definition.",
        )
        vault_port = InMemoryVaultAdapter()
        vault_port.save_atomic_note(existing)

        inv = AtomicEntityInventory(items=((NoteTitle("vilfredo pareto"), NoteType.ENTITY),))
        llm_port = MockLLMAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        assert notes[0] == existing
        assert len(llm_port.call_history) == 0

    def test_synthesize_batch_existing_note_alias_match_skips_llm(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body describing elites.",
            complementary_info="Complementary info.",
        )
        existing = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Existing definition.",
            aliases=("Pareto",),
        )
        vault_port = InMemoryVaultAdapter()
        vault_port.save_atomic_note(existing)

        inv = AtomicEntityInventory(items=((NoteTitle("pareto"), NoteType.ENTITY),))
        llm_port = MockLLMAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        assert notes[0] == existing
        assert len(llm_port.call_history) == 0

    def test_synthesize_batch_existing_note_honorific_match_skips_llm(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("História do Brasil"),
            body="Continuous body.",
            complementary_info="Complementary info.",
        )
        existing = AtomicNote(
            title=NoteTitle("Dom Pedro II"),
            note_type=NoteType.ENTITY,
            definition="Imperador do Brasil.",
        )
        vault_port = InMemoryVaultAdapter()
        vault_port.save_atomic_note(existing)

        # Inventory requests "Pedro II" without honorific prefix
        inv = AtomicEntityInventory(items=((NoteTitle("Pedro II"), NoteType.ENTITY),))
        llm_port = MockLLMAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        assert notes[0] == existing
        assert len(llm_port.call_history) == 0

    def test_synthesize_batch_partitions_chunks_by_batch_size(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body.",
            complementary_info="Complementary info.",
        )
        inv = AtomicEntityInventory(
            items=(
                (NoteTitle("Item 1"), NoteType.CONCEPT),
                (NoteTitle("Item 2"), NoteType.CONCEPT),
                (NoteTitle("Item 3"), NoteType.CONCEPT),
                (NoteTitle("Item 4"), NoteType.CONCEPT),
                (NoteTitle("Item 5"), NoteType.CONCEPT),
            )
        )
        chunk1_json = json.dumps(
            [
                {
                    "title": "Item 1",
                    "type": "concept",
                    "definition": "Definition text for item 1 with analysis.",
                },
                {
                    "title": "Item 2",
                    "type": "concept",
                    "definition": "Definition text for item 2 with analysis.",
                },
            ]
        )
        chunk2_json = json.dumps(
            [
                {
                    "title": "Item 3",
                    "type": "concept",
                    "definition": "Definition text for item 3 with analysis.",
                },
                {
                    "title": "Item 4",
                    "type": "concept",
                    "definition": "Definition text for item 4 with analysis.",
                },
            ]
        )
        chunk3_json = json.dumps(
            [
                {
                    "title": "Item 5",
                    "type": "concept",
                    "definition": "Definition text for item 5 with analysis.",
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[chunk1_json, chunk2_json, chunk3_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=2)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 5
        assert len(llm_port.call_history) == 3

    def test_synthesize_batch_skips_malformed_entries_and_defaults_type(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=NoteTitle("Teoria das Elites"),
            body="Continuous body.",
            complementary_info="Complementary info.",
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        batch_json = json.dumps(
            [
                "non_dict_entry",
                {"missing_title": True},
                {"title": ""},
                {"title": 999},
                {
                    "title": "Vilfredo Pareto",
                    "type": "invalid_type_defaults_to_concept",
                    "definition": "Valid definition with sufficient length.",
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        notes = use_case.execute(inv, compendium)

        assert len(notes) == 1
        assert notes[0].title.value == "Vilfredo Pareto"
        assert notes[0].note_type == NoteType.CONCEPT


class TestReconcileMOCs:
    """SPEC-001 Scenario 6.1: MOC Reconciliation."""

    def test_reconcile_mocs_success(self) -> None:
        vault_port = InMemoryVaultAdapter()
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador do conceito de circulação das elites políticas e econômicas.",
            domain="Ciência Política",
        )
        vault_port.save_atomic_note(note)

        moc_json = json.dumps(
            [
                {
                    "title": "MOC Teoria Politica",
                    "theme": "Ciência Política",
                    "overview": "Mapeamento das teorias de liderança.",
                    "associated_notes": ["Vilfredo Pareto"],
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[moc_json])

        use_case = ReconcileMOCsUseCase(llm_port, vault_port)
        mocs = use_case.execute()

        assert len(mocs) == 1
        moc = mocs[0]
        assert moc.title.value == "MOC Teoria Politica"
        assert moc.theme == "Ciência Política"
        assert moc.overview == "Mapeamento das teorias de liderança."
        assert NoteTitle("Vilfredo Pareto") in moc.associated_notes
        assert vault_port.mocs.get("moc teoria politica") == moc

        # Verify strict port interactions
        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert "Vilfredo Pareto" in call["prompt"]
        assert "Ciência Política" in call["prompt"]

    def test_reconcile_mocs_skips_malformed_entries_and_deduplicates_notes(self) -> None:
        vault_port = InMemoryVaultAdapter()
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador do conceito de circulação das elites.",
        )
        vault_port.save_atomic_note(note)

        moc_json = json.dumps(
            [
                "non_dict",
                {"missing_title": True},
                {"title": ""},
                {"title": "MOC Empty Notes", "associated_notes": []},
                {
                    "title": "MOC Valid",
                    "theme": "Sociologia",
                    "overview": "Overview text.",
                    "associated_notes": [
                        "Vilfredo Pareto",
                        "vilfredo pareto",  # Duplicate
                        "",  # Empty string
                        123,  # Non-string
                    ],
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[moc_json])

        use_case = ReconcileMOCsUseCase(llm_port, vault_port)
        mocs = use_case.execute()

        assert len(mocs) == 1
        moc = mocs[0]
        assert moc.title.value == "MOC Valid"
        assert len(moc.associated_notes) == 1
        assert moc.associated_notes[0].value == "Vilfredo Pareto"


class TestUseCasesEdgeCases:
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
        with pytest.raises(CompendiumStructureError):
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

        with pytest.raises(DomainValidationError, match="Expected JSON array"):
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
        llm_port = MockLLMAdapter(responses=["[]"])
        use_case = DiscoverAtomicInventoryUseCase(llm_port)

        with pytest.raises(DomainValidationError, match="No valid entities discovered"):
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
        with pytest.raises(DomainValidationError, match="Batch synthesis expected JSON array"):
            use_case.execute(inv, compendium)

    def test_reconcile_mocs_non_list_raises_error(self) -> None:
        vault_port = InMemoryVaultAdapter()
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador do conceito de circulação das elites.",
        )
        vault_port.save_atomic_note(note)
        llm_port = MockLLMAdapter(responses=['{"error": "not a list"}'])

        use_case = ReconcileMOCsUseCase(llm_port, vault_port)
        with pytest.raises(DomainValidationError, match="MOC reconciliation expected JSON array"):
            use_case.execute()
