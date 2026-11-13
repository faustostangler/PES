"""Unit tests for Cresmo Application Use Cases.

Derived from SPEC-001 Section 4 (Acceptance Criteria Scenarios).
Pure, hermetic tests using Mock Ports (0 external I/O) with strict port verification.
"""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import (
    NoOpPromptProviderPort,
    PromptProviderPort,
)
from cresmo.application.use_cases import (
    DiscoverAtomicInventoryUseCase,
    ExpandCompendiumUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
)
from cresmo.application.use_cases.synthesize_atomic_batch import _norm_honorific
from cresmo.domain.entities import (
    AtomicNote,
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    Channel,
    ChannelId,
    Content,
    ContentId,
    CrossContextRelations,
    MediaProvenance,
    NoteTitle,
    NoteType,
)
from tests.doubles.mock_adapters import (
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
        canned = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(id=cid, title="Example Channel", text="Raw spoken audio transcript."),
        )
        ingestion_port = MockMediaIngestionPort(canned_transcript=canned)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=dQw4w9WgXcQ")

        assert result is not None
        assert result.content.id == cid
        assert vault_port.get_stage_transcript("raw", cid) == canned
        assert ingestion_port.ingest_single_calls == ["https://youtube.com/watch?v=dQw4w9WgXcQ"]

    def test_ingest_single_video_none_returns_none(self) -> None:
        ingestion_port = MockMediaIngestionPort(canned_transcript=None)
        vault_port = InMemoryVaultAdapter()

        use_case = IngestRawTranscriptUseCase(ingestion_port, vault_port)
        result = use_case.execute("https://youtube.com/watch?v=missing123")

        assert result is None
        assert len(vault_port.raw_transcripts) == 0


class TestExpandLongitudinalSynchronic:
    """SPEC-001 Scenario 3.1: Braudel & Jaspers Expansion."""

    def test_expand_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel", id=ChannelId("UC_Test")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body describing elites.\n\n### Extra Info\n\nInitial complementary info.",
            ),
            pass_count=1,
        )
        long_response = (
            "# Teoria das Elites (Longitudinal)\n\n"
            "Longitudinal analysis tracing Roman patricians through medieval baronies.\n\n"
            "### Extra Info\n\n"
            "Longitudinal footnotes and multi-secular metrics."
        )
        wide_response = (
            "# Teoria das Elites (Synchronic)\n\n"
            "Expanded continuous prose integrating longue durée causal analysis and axial networks.\n\n"
            "### Extra Info\n\n"
            "Multi-secular historical indices and global trade matrices."
        )
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandCompendiumUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)

        assert updated.content.id == cid
        assert updated.pass_count == 2
        assert updated.channel.id == ChannelId("UC_Test")
        assert updated.provenance.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert updated.content.title == initial_compendium.content.title
        assert updated.content.title == "Teoria das Elites"
        assert "longue durée" in updated.content.text
        # Leading H1 must be stripped from body
        assert not updated.content.text.startswith("#")
        assert "Multi-secular historical indices and global trade matrices." in updated.content.text
        assert vault_port.get_stage_transcript("gap_filler", cid) == updated

        # Verify strict port interactions
        assert len(llm_port.call_history) == 2
        assert all(c["session_id"] == "UC_Test:dQw4w9WgXcQ" for c in llm_port.call_history)
        assert all(c["user_id"] == "anonymous" for c in llm_port.call_history)
        # Pass 1: Longitude expander gets initial compendium body and complementary info
        p0 = llm_port.call_history[0]["prompt"].get_last_user_content()
        sys0 = llm_port.call_history[0]["system_prompt"] or ""
        assert "Continuous prose body describing elites." in p0
        assert "Initial complementary info." in p0
        assert sys0.startswith("You are Cresmo Long-Expander")
        assert p0.startswith("Take the following enriched Markdown document")
        assert not p0.startswith(sys0[:30])

        # Pass 2: Wide expander gets the response from longitudinal expansion
        p1 = llm_port.call_history[1]["prompt"].get_last_user_content()
        sys1 = llm_port.call_history[1]["system_prompt"] or ""
        assert "Longitudinal analysis tracing Roman patricians" in p1
        assert sys1.startswith("You are Cresmo Wide-Expander")
        assert p1.startswith("Take the following longitudinally expanded Markdown document")
        assert not p1.startswith(sys1[:30])

    def test_expand_missing_complementary_tag_falls_back_to_original(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body.\n\n### Extra Info\n\nOriginal complementary info.",
            ),
        )
        long_response = "Long response without section header."
        wide_response = "Wide response without section header."
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandCompendiumUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)

        assert updated.content.title == initial_compendium.content.title
        assert "Wide response without section header." in updated.content.text
        assert "Original complementary info." in updated.content.text

    def test_expand_empty_complementary_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body.\n\n### Extra Info\n\nInitial complementary info.",
            ),
        )
        long_response = "Long response."
        wide_response = "Wide response text.\n\n### Extra Info\n\n   "
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()
        use_case = ExpandCompendiumUseCase(llm_port, vault_port)
        with pytest.raises(
            CompendiumStructureError, match=r"^Missing complementary info in expansion\.$"
        ):
            use_case.execute(initial_compendium)

    def test_expand_init_validations(self) -> None:
        vault_port = InMemoryVaultAdapter()
        llm_port = MockLLMAdapter()

        with pytest.raises(ValueError, match=r"^llm_synthesis_port must be provided$"):
            ExpandCompendiumUseCase(None, vault_port)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match=r"^vault_port must be provided$"):
            ExpandCompendiumUseCase(llm_port, None)  # type: ignore[arg-type]

        uc = ExpandCompendiumUseCase(llm_port, vault_port)
        assert isinstance(uc.prompt_provider, NoOpPromptProviderPort)
        assert uc.temperature is None

    def test_expand_temperature_and_user_and_trace_ids(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body.\n\n### Extra Info\n\nInitial complementary info.",
            ),
        )
        long_response = "Long response text."
        wide_response = "Expanded body.\n\n### Extra Info\n\nExact tag notes."
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandCompendiumUseCase(llm_port, vault_port, temperature=0.85)
        user = UserIdentity("usr_special")
        updated = use_case.execute(initial_compendium, user=user)

        assert updated.pass_count == (initial_compendium.pass_count or 1) + 1
        assert len(llm_port.call_history) == 2
        assert llm_port.call_history[0]["temperature"] == 0.85
        assert llm_port.call_history[1]["temperature"] == 0.85
        assert llm_port.call_history[0]["user_id"] == "usr_special"
        assert llm_port.call_history[1]["user_id"] == "usr_special"
        assert llm_port.call_history[0]["trace_id"] == "dQw4w9WgXcQ_longitudinal"
        assert llm_port.call_history[1]["trace_id"] == "dQw4w9WgXcQ_synchronic"

    def test_expand_with_regex_variations_notas_complementares(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body.\n\n### Extra Info\n\nInitial complementary info.",
            ),
        )
        long_response = "Long response text."
        wide_response = (
            "# Leading Title\nExpanded body.\n\n### Notas Complementares\n\nNotas content."
        )
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandCompendiumUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)
        assert "Expanded body." in updated.content.text
        assert "Notas content." in updated.content.text

    def test_expand_preserves_distinct_metadata_and_dates(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        initial_compendium = StageTranscript(
            channel=Channel(name="Example Channel", id=ChannelId("UC_XYZ"), category="Direita"),
            provenance=MediaProvenance.create(
                url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                publication_date=date(2021, 1, 1),
                description="A deep video description.",
            ),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous prose body.\n\n### Extra Info\n\nInitial complementary info.",
            ),
            metadata={"video_date": "20220202"},
        )
        long_response = "Long response text."
        wide_response = "Expanded body.\n\n## Informações Adicionais\n\nAdicionais content."
        llm_port = MockLLMAdapter(responses=[long_response, wide_response])
        vault_port = InMemoryVaultAdapter()

        use_case = ExpandCompendiumUseCase(llm_port, vault_port)
        updated = use_case.execute(initial_compendium)
        assert updated.content.id == cid
        assert updated.channel.name == "Example Channel"
        assert updated.channel.id == ChannelId("UC_XYZ")
        assert updated.channel.category == "Direita"
        assert updated.provenance.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert updated.provenance.publication_date == date(2021, 1, 1)
        assert updated.metadata.get("video_date") == "20220202"
        assert updated.provenance.description == "A deep video description."
        assert "Adicionais content." in updated.content.text


class TestDiscoverAtomicInventory:
    """SPEC-001 Scenario 4.1: Holistic Inventory Discovery."""

    def test_discover_inventory_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing Vilfredo Pareto and Gaetano Mosca.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        assert call["session_id"] == "Example Channel:dQw4w9WgXcQ"
        assert call["user_id"] == "anonymous"
        user_prompt = call["prompt"].get_last_user_content()
        assert "Teoria das Elites" in user_prompt
        assert "Example Channel" in user_prompt
        assert "Continuous body describing Vilfredo Pareto" in user_prompt

    def test_discover_inventory_uses_channel_id_when_available(self) -> None:
        """When ChannelId is available on the compendium, session_id and user_id use the ID."""
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel", id=ChannelId("UC_TestChannelId")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing Vilfredo Pareto and Gaetano Mosca.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        llm_json = json.dumps([{"title": "Vilfredo Pareto", "type": "entity"}])
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        use_case.execute(compendium)

        call = llm_port.call_history[0]
        assert call["session_id"] == "UC_TestChannelId:dQw4w9WgXcQ"
        assert call["user_id"] == "anonymous"

    def test_discover_inventory_deduplicates_case_insensitively(self) -> None:
        cid = ContentId("dQw4w9XcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9XcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9XcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
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

    def test_discover_inventory_non_list_json_raises_domain_validation_error(self) -> None:
        cid = ContentId("dQw4w9XcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9XcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        llm_json = json.dumps({"not": "a list", "title": "Vilfredo Pareto"})
        llm_port = MockLLMAdapter(responses=[llm_json])

        use_case = DiscoverAtomicInventoryUseCase(llm_port)
        with pytest.raises(
            DomainValidationError,
            match=r"Expected JSON array of entities for 'Teoria das Elites', got: dict",
        ):
            use_case.execute(compendium)


class TestSynthesizeAtomicBatch:
    """SPEC-001 Scenario 5.1: Batched Atomic Synthesis."""

    def test_synthesize_batch_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        assert call["session_id"] == "Example Channel:dQw4w9WgXcQ"
        assert call["user_id"] == "anonymous"
        user_prompt = call["prompt"].get_last_user_content()
        assert "Teoria das Elites" in user_prompt
        assert "Example Channel" in user_prompt
        assert "Continuous body describing elites." in user_prompt
        assert "Vilfredo Pareto" in user_prompt

    def test_synthesize_batch_uses_channel_id_when_available(self) -> None:
        """When ChannelId is available on the compendium, session_id and user_id use the ID."""
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel", id=ChannelId("UC_TestChannelId")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        batch_json = json.dumps(
            [
                {
                    "title": "Vilfredo Pareto",
                    "type": "entity",
                    "definition": "Economista e sociólogo italiano conhecido pela teoria das elites.",
                    "conceptual_typology": {
                        "theoretical_lineage": "Sociologia Clássica",
                        "lateral_events": "Revolução Marginalista",
                        "aftermath": "Fascismo italiano",
                    },
                    "aliases": ["Pareto"],
                    "content_tags": ["sociologia"],
                    "domain": "Ciência Política",
                    "cluster": "Teoria das Elites",
                    "source": "Teoria das Elites",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        use_case.execute(inv, compendium)

        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert call["session_id"] == "UC_TestChannelId:dQw4w9WgXcQ"
        assert call["user_id"] == "anonymous"

    def test_synthesize_batch_non_list_json_raises_domain_validation_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        llm_json = json.dumps({"title": "Vilfredo Pareto", "type": "entity"})
        llm_port = MockLLMAdapter(responses=[llm_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        with pytest.raises(
            DomainValidationError,
            match=r"Batch synthesis expected JSON array, got: dict",
        ):
            use_case.execute(inv, compendium)

    def test_synthesize_batch_short_definition_raises_domain_validation_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        llm_json = json.dumps(
            [{"title": "Vilfredo Pareto", "type": "entity", "definition": "Short"}]
        )
        llm_port = MockLLMAdapter(responses=[llm_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_port, vault_port, batch_size=5)
        with pytest.raises(
            DomainValidationError,
            match=r"must contain at least 20 characters",
        ):
            use_case.execute(inv, compendium)

    def test_synthesize_batch_existing_note_exact_match_skips_llm(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body describing elites.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="História do Brasil",
                text="Continuous body.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Continuous body.\n\n### Extra Info\n\nComplementary info.",
            ),
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
        user_prompt = call["prompt"].get_last_user_content()
        assert '"title": "Vilfredo Pareto"' in user_prompt
        assert '"type": "entity"' in user_prompt
        assert '"domain": "Ciência Política"' in user_prompt

    def test_reconcile_mocs_init_options(self) -> None:
        llm = MockLLMAdapter()
        vault = InMemoryVaultAdapter()
        uc_def = ReconcileMOCsUseCase(llm, vault)

        assert isinstance(uc_def.prompt_provider, PromptProviderPort)

        custom_pp = MagicMock()
        uc_cust = ReconcileMOCsUseCase(llm, vault, prompt_provider=custom_pp)
        assert uc_cust.prompt_provider is custom_pp

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
                    "theme": "  Sociologia  ",
                    "overview": "  Overview text.  ",
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
        assert moc.theme == "Sociologia"
        assert moc.overview == "Overview text."
        assert len(moc.associated_notes) == 1
        assert moc.associated_notes[0].value == "Vilfredo Pareto"


class TestUseCasesEdgeCases:
    """Boundary conditions and exception branch coverage."""

    def test_discover_inventory_non_list_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        llm_port = MockLLMAdapter(responses=['{"not_a_list": true}'])
        use_case = DiscoverAtomicInventoryUseCase(llm_port)

        with pytest.raises(DomainValidationError, match="Expected JSON array"):
            use_case.execute(compendium)

    def test_discover_inventory_empty_items_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
        )
        llm_port = MockLLMAdapter(responses=["[]"])
        use_case = DiscoverAtomicInventoryUseCase(llm_port)

        with pytest.raises(DomainValidationError, match="No valid entities discovered"):
            use_case.execute(compendium)

    def test_synthesize_batch_non_list_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        compendium = StageTranscript(
            channel=Channel(name="Example Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Teoria das Elites",
                text="Body content.\n\n### Extra Info\n\nComplementary info.",
            ),
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
