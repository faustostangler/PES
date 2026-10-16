"""Hermetic unit tests for SynthesizeAtomicBatchUseCase.

Verifies batched atomic note synthesis, honorific title normalization,
alias and exact note caching, batch chunking, error validation, and vault persistence.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.ports import PromptProviderPort
from cresmo.application.use_cases.synthesize_atomic_batch import (
    SynthesizeAtomicBatchUseCase,
    _norm_honorific,
)
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    UserIdentity,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    ChannelId,
    ChannelName,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
    PromptKey,
)
from tests.doubles.mock_adapters import InMemoryVaultAdapter, MockLLMAdapter


@pytest.fixture
def sample_compendium() -> EnrichedCompendium:
    return EnrichedCompendium(
        content_id=ContentId("dQw4w9WgXcQ"),
        channel_name=ChannelName("Example Channel"),
        channel_id=ChannelId("UC_TestChannelId"),
        title=NoteTitle("Teoria das Elites"),
        body="Continuous body describing elites and power structures in society.",
        complementary_info="Complementary info.",
    )


class TestSynthesizeAtomicBatchUseCase:
    """Hermetic unit tests for SynthesizeAtomicBatchUseCase."""

    def test_norm_honorific_all_prefixes_and_punctuation(self) -> None:
        """Verify honorific stripping (dom, dona, d., d) and punctuation collapse."""
        assert _norm_honorific("Dom Pedro II") == "pedro ii"
        assert _norm_honorific("dona leopoldina") == "leopoldina"
        assert _norm_honorific("D. João VI") == "joão vi"
        assert _norm_honorific("D Duarte") == "duarte"
        assert _norm_honorific("  Dom   Pedro---II (Imperador)... ") == "pedro ii imperador"
        assert _norm_honorific("Normal Title") == "normal title"

    def test_init_validation_and_batch_size_clamping(self) -> None:
        """Verify fail-fast parameter validation and batch_size clamping to >= 1."""
        llm = MockLLMAdapter()
        vault = InMemoryVaultAdapter()

        with pytest.raises(ValueError) as exc1:
            SynthesizeAtomicBatchUseCase(llm_synthesis_port=None, vault_port=vault)  # type: ignore[arg-type]
        assert str(exc1.value) == "llm_synthesis_port must be provided"

        with pytest.raises(ValueError) as exc2:
            SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm, vault_port=None)  # type: ignore[arg-type]
        assert str(exc2.value) == "vault_port must be provided"

        # batch_size <= 0 clamps to 1
        use_case_clamp = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
            batch_size=0,
            temperature=0.3,
        )
        assert use_case_clamp.batch_size == 1
        assert use_case_clamp.temperature == 0.3
        assert isinstance(use_case_clamp.prompt_provider, PromptProviderPort)

        use_case_neg = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
            batch_size=-5,
        )
        assert use_case_neg.batch_size == 1

        use_case_default = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
        )
        assert use_case_default.batch_size == 5

        custom_prompt_provider = MagicMock(spec=PromptProviderPort)
        use_case_cust = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
            prompt_provider=custom_prompt_provider,
        )
        assert use_case_cust.prompt_provider is custom_prompt_provider

    def test_synthesize_batch_success_with_all_fields_and_persistence(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify full synthesis with all metadata fields, relations, matrices, and dual persistence."""
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        batch_json = json.dumps(
            [
                {
                    "title": "Vilfredo Pareto",
                    "type": "entity",
                    "definition": "Economista e sociólogo italiano conhecido pela teoria das elites.",
                    "direct_relations": ["Teoria das Elites", "", 123],
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
                    "aliases": ["Pareto", "V. Pareto", "", "   "],
                    "content_tags": ["sociologia", "elites", ""],
                    "domain": "Ciência Política",
                    "cluster": "Teoria das Elites",
                    "source": "Fonte Primária Distinta",
                }
            ],
            ensure_ascii=False,
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
            batch_size=5,
            temperature=0.2,
        )

        user = UserIdentity("custom_user_42")
        with patch("json.dumps", wraps=json.dumps) as mock_dumps:
            notes = use_case.execute(inv, sample_compendium, user=user)
            assert mock_dumps.call_args[1].get("ensure_ascii") is False

        assert len(notes) == 1
        note = notes[0]
        assert note.title.value == "Vilfredo Pareto"
        assert note.note_type == NoteType.ENTITY
        assert note.domain == "Ciência Política"
        assert note.cluster == "Teoria das Elites"
        assert note.source == "Fonte Primária Distinta"
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

        # Dual persistence in vault
        assert vault_port.get_atomic_note_by_title(NoteTitle("Vilfredo Pareto")) == note
        assert vault_port.index_entries["vilfredo pareto"]["title"] == "Vilfredo Pareto"

        # Verify LLM call metadata
        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert call["session_id"] == "UC_TestChannelId:dQw4w9WgXcQ"
        assert call["user_id"] == "custom_user_42"
        assert call["temperature"] == 0.2
        assert call["trace_id"] == "dQw4w9WgXcQ_atomic_batch"

    def test_synthesize_batch_default_fields_and_anonymous_user(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify defaults for domain, source, cluster, and anonymous user when user=None."""
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        # Payload omitting domain, source, cluster, causal_matrix, cross_context, type
        batch_json = json.dumps(
            [
                {
                    "title": "Vilfredo Pareto",
                    "definition": "Economista e sociólogo italiano conhecido pela teoria das elites.",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)
        notes = use_case.execute(inv, sample_compendium, user=None)

        assert len(notes) == 1
        note = notes[0]
        assert note.note_type == NoteType.CONCEPT
        assert note.domain == str(sample_compendium.channel_name)
        assert note.source == sample_compendium.title.value
        assert note.cluster == ""
        assert note.causal_matrix is None
        assert note.cross_context is None

        assert llm_port.call_history[0]["user_id"] == "anonymous"

    def test_synthesize_batch_raises_on_non_list_json(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify DomainValidationError when extracted JSON is not a list."""
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        llm_port = MockLLMAdapter(responses=['{"not": "a list"}'])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)
        with pytest.raises(DomainValidationError) as exc:
            use_case.execute(inv, sample_compendium)
        assert str(exc.value) == "Batch synthesis expected JSON array, got: dict"

    def test_synthesize_batch_skips_malformed_entries(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify filtering of non-dict entries and missing/empty titles."""
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        batch_json = json.dumps(
            [
                "non_dict",
                12345,
                {"missing_title": True},
                {"title": ""},
                {"title": "   "},
                {"title": 888},
                {
                    "title": "Vilfredo Pareto",
                    "definition": "Economista e sociólogo italiano conhecido pela teoria das elites.",
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)
        notes = use_case.execute(inv, sample_compendium)

        assert len(notes) == 1
        assert notes[0].title.value == "Vilfredo Pareto"

    def test_synthesize_batch_missing_definition_raises_domain_validation_error_with_empty_got(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify DomainValidationError matches Got: '' when definition key is omitted."""
        inv = AtomicEntityInventory(items=((NoteTitle("Vilfredo Pareto"), NoteType.ENTITY),))
        batch_json = json.dumps([{"title": "Vilfredo Pareto"}])
        llm_port = MockLLMAdapter(responses=[batch_json])
        vault_port = InMemoryVaultAdapter()
        use_case = SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)

        with pytest.raises(DomainValidationError, match=r"Got: ''"):
            use_case.execute(inv, sample_compendium)

    def test_synthesize_batch_caching_and_exact_alias_honorific_lookups(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify exact match, alias match, and honorific boundary length normalization cache hits."""
        vault_port = InMemoryVaultAdapter()

        # 1. Exact note
        exact_note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Definição sociológica prévia de Vilfredo Pareto com texto longo.",
        )
        vault_port.save_atomic_note(exact_note)

        # 1b. Exact short note (length 3 < 4) to ensure exact lookup lowercase is tested without norm_lookup
        short_exact_note = AtomicNote(
            title=NoteTitle("Fox"),
            note_type=NoteType.CONCEPT,
            definition="Definição sociológica de raposa paretiana.",
        )
        vault_port.save_atomic_note(short_exact_note)

        # 2. Alias note
        alias_note = AtomicNote(
            title=NoteTitle("Niccolò Machiavelli"),
            note_type=NoteType.ENTITY,
            definition="Definição prévia de Maquiavel com análise descritiva suficiente.",
            aliases=("Maquiavel",),
        )
        vault_port.save_atomic_note(alias_note)

        # 3. Honorific note: length exactly 4 ("Dom Raul" -> "raul", len=4)
        honorific_note_len4 = AtomicNote(
            title=NoteTitle("Dom Raul"),
            note_type=NoteType.ENTITY,
            definition="Definição prévia de Dom Raul com análise descritiva suficiente.",
        )
        vault_port.save_atomic_note(honorific_note_len4)

        # 4. Honorific note: length 3 ("Dom Rui" -> "rui", len=3 < 4) - should NOT enter norm_lookup!
        honorific_short = AtomicNote(
            title=NoteTitle("Dom Rui"),
            note_type=NoteType.ENTITY,
            definition="Definição prévia de Dom Rui com análise descritiva suficiente.",
        )
        vault_port.save_atomic_note(honorific_short)

        inv = AtomicEntityInventory(
            items=(
                (NoteTitle("vilfredo pareto"), NoteType.ENTITY),  # Exact match (case-insensitive)
                (
                    NoteTitle("fox"),
                    NoteType.CONCEPT,
                ),  # Exact short match (<4 chars, tests lower() without norm_lookup)
                (NoteTitle("maquiavel"), NoteType.ENTITY),  # Alias match
                (NoteTitle("raul"), NoteType.ENTITY),  # Honorific norm match (len=4 >= 4)
                (NoteTitle("rui"), NoteType.ENTITY),  # Length 3 < 4: NOT matched, sent to LLM!
            )
        )

        llm_response = json.dumps(
            [
                {
                    "title": "Rui",
                    "definition": "Político e jurista brasileiro com carreira extensa e notável.",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[llm_response])

        use_case = SynthesizeAtomicBatchUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)
        notes = use_case.execute(inv, sample_compendium)

        # 4 cached notes returned directly + 1 synthesized from LLM = 5 notes
        assert len(notes) == 5
        assert notes[0] == exact_note
        assert notes[1] == short_exact_note
        assert notes[2] == alias_note
        assert notes[3] == honorific_note_len4
        assert notes[4].title.value == "Rui"

        # Exactly 1 LLM call for "rui"
        assert len(llm_port.call_history) == 1
        prompt = llm_port.call_history[0]["prompt"].get_last_user_content()
        assert "rui" in prompt
        assert "Vilfredo Pareto" not in prompt
        assert "fox" not in prompt

    def test_synthesize_batch_partitions_multiple_chunks(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify batch partitioning across multiple chunks conforming to batch_size."""
        inv = AtomicEntityInventory(
            items=(
                (NoteTitle("Entity 1"), NoteType.CONCEPT),
                (NoteTitle("Entity 2"), NoteType.CONCEPT),
                (NoteTitle("Entity 3"), NoteType.CONCEPT),
            )
        )
        chunk1 = json.dumps(
            [
                {
                    "title": "Entity 1",
                    "definition": "Definition text for entity 1 with long body.",
                },
                {
                    "title": "Entity 2",
                    "definition": "Definition text for entity 2 with long body.",
                },
            ]
        )
        chunk2 = json.dumps(
            [
                {
                    "title": "Entity 3",
                    "definition": "Definition text for entity 3 with long body.",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[chunk1, chunk2])
        vault_port = InMemoryVaultAdapter()

        use_case = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
            batch_size=2,
        )
        notes = use_case.execute(inv, sample_compendium)

        assert len(notes) == 3
        assert len(llm_port.call_history) == 2

    def test_parse_single_atomic_note_defaults_and_fallbacks(
        self,
        sample_compendium: EnrichedCompendium,
    ) -> None:
        """Verify strict default value assignments and error fallbacks for single note parsing."""
        inv = AtomicEntityInventory(
            items=(
                (NoteTitle("Note Trimmed Definition"), NoteType.CONCEPT),
                (NoteTitle("Note Empty CM"), NoteType.CONCEPT),
                (NoteTitle("Note Empty CC"), NoteType.CONCEPT),
                (NoteTitle("Note Invalid Type"), NoteType.CONCEPT),
                (NoteTitle("Note NonStr Type"), NoteType.CONCEPT),
                (NoteTitle("Note Missing Type"), NoteType.CONCEPT),
            )
        )
        batch_payload = json.dumps(
            [
                {
                    "title": "Note Trimmed Definition",
                    "definition": "   Definição contextual com espaços em branco excedentes nas bordas.   ",
                },
                {
                    "title": "Note Empty CM",
                    "definition": "Definição longa o suficiente para ser aceita pelo agregado de domínio.",
                    "causal_matrix": {},
                },
                {
                    "title": "Note Empty CC",
                    "definition": "Definição longa o suficiente para ser aceita pelo agregado de domínio.",
                    "cross_context": {},
                },
                {
                    "title": "Note Invalid Type",
                    "definition": "Definição longa o suficiente para ser aceita pelo agregado de domínio.",
                    "type": "completely_invalid_typology_xyz",
                },
                {
                    "title": "Note NonStr Type",
                    "definition": "Definição longa o suficiente para ser aceita pelo agregado de domínio.",
                    "type": 9999,
                },
                {
                    "title": "Note Missing Type",
                    "definition": "Definição longa o suficiente para ser aceita pelo agregado de domínio.",
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_payload])
        vault_port = InMemoryVaultAdapter()
        use_case = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
            batch_size=10,
        )
        notes = use_case.execute(inv, sample_compendium)

        assert len(notes) == 6
        # Definition whitespace is cleanly trimmed
        assert (
            notes[0].definition
            == "Definição contextual com espaços em branco excedentes nas bordas."
        )

        # Empty causal matrix defaults all inner fields to empty string
        assert notes[1].causal_matrix is not None
        assert notes[1].causal_matrix.cause == ""
        assert notes[1].causal_matrix.effect == ""
        assert notes[1].causal_matrix.epistemic_attribution == ""
        assert notes[1].causal_matrix == CausalMatrix(cause="", effect="", epistemic_attribution="")

        # Empty cross context defaults all inner fields to empty string
        assert notes[2].cross_context is not None
        assert notes[2].cross_context.precursors == ""
        assert notes[2].cross_context.lateral_events == ""
        assert notes[2].cross_context.aftermath == ""
        assert notes[2].cross_context == CrossContextRelations(
            precursors="", lateral_events="", aftermath=""
        )

        # Invalid type falls back to NoteType.CONCEPT
        assert notes[3].note_type is NoteType.CONCEPT

        # Non-string type falls back to NoteType.CONCEPT
        assert notes[4].note_type is NoteType.CONCEPT

        # Missing type falls back to NoteType.CONCEPT
        assert notes[5].note_type is NoteType.CONCEPT

    def test_synthesize_chunk_prompt_parameters_and_session_resolution(self) -> None:
        """Verify prompt provider arguments, targets_json keys, and channel_id=None session resolution."""
        compendium_no_cid = EnrichedCompendium(
            content_id=ContentId("content123"),
            channel_name=ChannelName("Channel Alpha"),
            channel_id=None,
            title=NoteTitle("Alpha Title"),
            body="Continuous text for channel alpha.",
            complementary_info="Complementary context.",
        )
        inv = AtomicEntityInventory(items=((NoteTitle("Alpha Entity"), NoteType.ENTITY),))
        batch_payload = json.dumps(
            [
                {
                    "title": "Alpha Entity",
                    "type": "entity",
                    "definition": "Definition for alpha entity.",
                }
            ]
        )
        llm_port = MockLLMAdapter(responses=[batch_payload])
        vault_port = InMemoryVaultAdapter()
        mock_prompt_provider = MagicMock(spec=PromptProviderPort)
        mock_prompt_provider.get_prompt.return_value = "custom prompt"

        use_case = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
            prompt_provider=mock_prompt_provider,
        )
        notes = use_case.execute(inv, compendium_no_cid)

        assert len(notes) == 1
        assert mock_prompt_provider.get_prompt.call_count == 1
        call_args, call_kwargs = mock_prompt_provider.get_prompt.call_args

        # Verify exact prompt key and keyword arguments
        assert call_args[0] == PromptKey.ATOMIC_BATCH
        assert call_kwargs["content_title"] == "Alpha Title"
        assert call_kwargs["content_title"] == compendium_no_cid.title.value
        assert call_kwargs["channel_name"] == compendium_no_cid.channel_name
        assert call_kwargs["compendium_body"] == "Continuous text for channel alpha."
        assert call_kwargs["compendium_body"] == compendium_no_cid.body
        assert "targets_json" in call_kwargs

        targets = json.loads(call_kwargs["targets_json"])
        assert len(targets) == 1
        assert targets[0] == {"title": "Alpha Entity", "type": "entity"}
        assert "title" in targets[0]
        assert "type" in targets[0]
        assert list(targets[0].keys()) == ["title", "type"]

        # Verify session_id resolution with channel_id=None strictly relies on channel_name
        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert call["session_id"] == "Channel Alpha:content123"
