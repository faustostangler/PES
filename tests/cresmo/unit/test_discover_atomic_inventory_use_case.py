"""Unit tests for DiscoverAtomicInventoryUseCase with LLM-as-a-Judge and Deterministic Guardrails.

Conforms to:
- ADR-024: Iterative LLM-as-a-Judge and Deterministic Guardrails for Atomic Inventory Discovery
- SPEC-009: Atomic Inventory Discovery Judge and Guardrails Specification
"""

from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import LlmJudgePort, PromptProviderPort
from cresmo.application.use_cases.discover_atomic_inventory import (
    DiscoverAtomicInventoryUseCase,
    _parse_and_deduplicate_items,
    is_valid_inventory_json_structure,
)
from cresmo.domain.entities import EnrichedCompendium, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    ChannelName,
    ChatMessage,
    ChatPrompt,
    ContentId,
    JudgeCriterion,
    JudgeEvaluation,
    MessageRole,
    NoteTitle,
    NoteType,
    PromptKey,
)
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from tests.doubles.mock_adapters import MockLLMAdapter


class TestDiscoverAtomicInventoryJudge:
    """Hermetic unit tests for atomic inventory discovery with guardrail and judge verification."""

    @pytest.fixture
    def sample_compendium(self) -> EnrichedCompendium:
        return EnrichedCompendium(
            content_id=ContentId("vid_inv_1234"),
            channel_name=ChannelName("Geopolitics Channel"),
            title=NoteTitle("The Longue Durée of Mediterranean Trade"),
            body="Fernand Braudel analyzes the Mediterranean basin across centuries.",
            complementary_info="1. Detailed chronological notes on Venetian commerce.",
        )

    def test_guardrail_accepts_valid_inventory(self) -> None:
        data = [
            {"title": "Bacia do Mediterrâneo", "type": "entity"},
            {"title": "Longue Durée", "type": "concept"},
            {"title": "1571 Batalha de Lepanto", "type": "event"},
            {"title": "Fluxo Comercial Veneziano", "type": "process"},
        ]
        assert is_valid_inventory_json_structure(data) is True

    def test_guardrail_rejects_empty_or_non_list(self) -> None:
        assert is_valid_inventory_json_structure([]) is False
        assert is_valid_inventory_json_structure({}) is False
        assert is_valid_inventory_json_structure("string") is False
        assert is_valid_inventory_json_structure(None) is False

    def test_guardrail_rejects_missing_title_or_invalid_type(self) -> None:
        assert is_valid_inventory_json_structure([{"title": "", "type": "entity"}]) is False
        assert is_valid_inventory_json_structure([{"type": "entity"}]) is False
        assert (
            is_valid_inventory_json_structure([{"title": "Valid", "type": "unknown_type"}]) is False
        )

    def test_guardrail_enforces_big_endian_date_for_events(self) -> None:
        # Event with Big-Endian year
        assert (
            is_valid_inventory_json_structure(
                [{"title": "1945 Acordo de Potsdam", "type": "event"}]
            )
            is True
        )
        # Event without Big-Endian year must be rejected
        assert (
            is_valid_inventory_json_structure(
                [{"title": "Acordo de Potsdam em 1945", "type": "event"}]
            )
            is False
        )

    def test_discover_inventory_judge_success_first_attempt(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        prompt_provider = JsonPromptProvider()
        candidate_json = json.dumps(
            [
                {"title": "Bacia do Mediterrâneo", "type": "entity"},
                {"title": "Longue Durée", "type": "concept"},
                {"title": "1571 Batalha de Lepanto", "type": "event"},
            ]
        )
        # First call: candidate extraction; Second call: judge boolean verdict
        llm = MockLLMAdapter(responses=[candidate_json, "true"])

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=3,
        )
        inventory = use_case.execute(sample_compendium)

        assert len(inventory.items) == 3
        assert len(llm.call_history) == 2

        # Verify extraction call
        assert llm.call_history[0]["trace_id"] == "vid_inv_1234_inventory"
        assert llm.call_history[0]["temperature"] == 0.0
        assert llm.call_history[0]["session_id"] == "Geopolitics Channel:vid_inv_1234"
        assert llm.call_history[0]["user_id"] == "anonymous"

        # Verify judge call
        assert llm.call_history[1]["trace_id"] == "vid_inv_1234_inventory_judge"
        assert llm.call_history[1]["temperature"] == 0.0
        assert llm.call_history[1]["session_id"] == "Geopolitics Channel:vid_inv_1234"
        assert llm.call_history[1]["user_id"] == "anonymous"
        assert (
            "Does the candidate inventory strictly satisfy"
            in llm.call_history[1]["prompt"].get_last_user_content()
        )

    def test_discover_inventory_judge_retry_loop(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        prompt_provider = JsonPromptProvider()
        cand1 = json.dumps([{"title": "Alucinacao Espuria", "type": "entity"}])
        cand2 = json.dumps(
            [
                {"title": "Bacia do Mediterrâneo", "type": "entity"},
                {"title": "Longue Durée", "type": "concept"},
            ]
        )
        # Attempt 0: cand1 -> judge says "false"
        # Attempt 1: cand2 -> judge says "true"
        llm = MockLLMAdapter(responses=[cand1, "false", cand2, "true"])

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=3,
        )
        inventory = use_case.execute(sample_compendium)

        assert len(inventory.items) == 2
        assert len(llm.call_history) == 4

        # Verification of retry trace IDs
        assert llm.call_history[0]["trace_id"] == "vid_inv_1234_inventory"
        assert llm.call_history[1]["trace_id"] == "vid_inv_1234_inventory_judge"
        assert llm.call_history[2]["trace_id"] == "vid_inv_1234_inventory_retry_1"
        assert llm.call_history[3]["trace_id"] == "vid_inv_1234_inventory_judge_retry_1"

    def test_discover_inventory_fast_fail_guardrail_skips_judge(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        prompt_provider = JsonPromptProvider()
        # Attempt 0: malformed JSON (not a list) -> fails Gate 1, judge is skipped!
        cand0 = json.dumps({"invalid": "not_a_list"})
        # Attempt 1: valid list -> passes Gate 1, judge is called and returns "true"
        cand1 = json.dumps([{"title": "Longue Durée", "type": "concept"}])
        llm = MockLLMAdapter(responses=[cand0, cand1, "true"])

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=3,
        )
        inventory = use_case.execute(sample_compendium)

        assert len(inventory.items) == 1
        # Exactly 3 calls: cand0 (attempt 0), cand1 (attempt 1), judge (attempt 1).
        # Judge was NOT called for cand0!
        assert len(llm.call_history) == 3
        assert llm.call_history[0]["trace_id"] == "vid_inv_1234_inventory"
        assert llm.call_history[1]["trace_id"] == "vid_inv_1234_inventory_retry_1"
        assert llm.call_history[2]["trace_id"] == "vid_inv_1234_inventory_judge_retry_1"

    def test_discover_inventory_exhausts_retries_raises_domain_error(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        prompt_provider = JsonPromptProvider()
        cand = json.dumps([{"title": "Nó Questionável", "type": "concept"}])
        # All judge evaluations return "false"
        llm = MockLLMAdapter(responses=[cand, "false", cand, "false"])

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=1,
        )
        with pytest.raises(
            DomainValidationError,
            match="Candidate entity inventory rejected by LLM-as-a-judge",
        ):
            use_case.execute(sample_compendium)

    def test_guardrail_rejects_non_dict_element_and_non_string_type(self) -> None:
        assert is_valid_inventory_json_structure(["not_a_dict"]) is False
        assert is_valid_inventory_json_structure([{"title": "Valid", "type": 123}]) is False
        assert is_valid_inventory_json_structure([{"title": "Valid", "type": None}]) is False

    def test_parse_and_deduplicate_items_skips_invalid_and_deduplicates_case_insensitively(
        self,
    ) -> None:
        raw = [
            "not_a_dict",
            {"type": "concept"},  # missing title
            {"title": "", "type": "concept"},  # empty title
            {"title": 123, "type": "concept"},  # non-string title
            {"title": "Rome", "type": "entity"},
            {"title": "rome", "type": "concept"},  # duplicate lowercase
            {"title": "ROME", "type": "concept"},  # duplicate uppercase
            {"title": "Empire", "type": "concept"},
            {"title": "Senator"},  # missing type -> defaults to concept
            {"title": "Consul", "type": "invalid_type_str"},  # invalid type -> fallback to concept
        ]
        items = _parse_and_deduplicate_items(raw, "Test Compendium")
        titles = [item[0].value for item in items]
        types = [item[1] for item in items]
        assert titles == ["Rome", "Empire", "Senator", "Consul"]
        assert types == [NoteType.ENTITY, NoteType.CONCEPT, NoteType.CONCEPT, NoteType.CONCEPT]

    def test_parse_and_deduplicate_items_empty_raises_domain_error(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match="No valid entities discovered in compendium 'Empty Doc'.",
        ):
            _parse_and_deduplicate_items([], "Empty Doc")

    def test_init_validation_and_defaults(self) -> None:
        with pytest.raises(ValueError, match=r"^llm_synthesis_port must be provided$"):
            DiscoverAtomicInventoryUseCase(llm_synthesis_port=None)  # type: ignore[arg-type]

        use_case = DiscoverAtomicInventoryUseCase(llm_synthesis_port=MockLLMAdapter())
        assert use_case.max_rewrites == 3
        assert use_case.temperature == 0.0
        assert use_case.judge_enabled is False

    def test_judge_disabled_evaluates_list_guardrail(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        llm = MockLLMAdapter(responses=[json.dumps([{"title": "Alpha", "type": "concept"}])])
        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            judge_enabled=False,
        )
        inv = use_case.execute(sample_compendium)
        assert len(inv.items) == 1

        # Malformed non-list raises DomainValidationError
        llm_bad = MockLLMAdapter(responses=[json.dumps({"not": "a_list"})])
        use_case_bad = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm_bad,
            judge_enabled=False,
        )
        with pytest.raises(
            DomainValidationError,
            match="Expected JSON array of entities for 'The Longue Durée of Mediterranean Trade', got: dict",
        ):
            use_case_bad.execute(sample_compendium)

    def test_execute_empty_candidate_items_raises_error_with_compendium_title(
        self,
    ) -> None:
        compendium = EnrichedCompendium(
            content_id=ContentId("vid_inv_empty"),
            channel_name=ChannelName("Test Channel"),
            title=NoteTitle("Unique Compendium Alpha"),
            body="Valid narrative body text.",
            complementary_info="Complementary context.",
        )
        llm = MockLLMAdapter(responses=[json.dumps([])])
        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            judge_enabled=False,
        )
        with pytest.raises(
            DomainValidationError,
            match=r"^No valid entities discovered in compendium 'Unique Compendium Alpha'\.$",
        ):
            use_case.execute(compendium)

    def test_discover_inventory_session_id_resolves_channel_id(
        self,
    ) -> None:
        from cresmo.domain.value_objects import ChannelId

        # 1. ChannelId Value Object
        compendium_vo = EnrichedCompendium(
            content_id=ContentId("vid_inv_1234"),
            channel_name=ChannelName("Geopolitics Channel"),
            title=NoteTitle("The Longue Durée of Mediterranean Trade"),
            body="Fernand Braudel analyzes the Mediterranean basin across centuries.",
            complementary_info="1. Detailed chronological notes on Venetian commerce.",
            channel_id=ChannelId("ch_geo_vo"),
        )
        llm_vo = MockLLMAdapter(responses=[json.dumps([{"title": "Entity A", "type": "entity"}])])
        use_case_vo = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm_vo,
            judge_enabled=False,
        )
        use_case_vo.execute(compendium_vo)
        assert llm_vo.call_history[0]["session_id"] == "ch_geo_vo:vid_inv_1234"

        # 2. ChannelId raw string
        compendium_str = EnrichedCompendium(
            content_id=ContentId("vid_inv_1234"),
            channel_name=ChannelName("Geopolitics Channel"),
            title=NoteTitle("The Longue Durée of Mediterranean Trade"),
            body="Fernand Braudel analyzes the Mediterranean basin across centuries.",
            complementary_info="1. Detailed chronological notes on Venetian commerce.",
            channel_id="ch_geo_raw_str",
        )
        llm_str = MockLLMAdapter(responses=[json.dumps([{"title": "Entity A", "type": "entity"}])])
        use_case_str = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm_str,
            judge_enabled=False,
        )
        use_case_str.execute(compendium_str)
        assert llm_str.call_history[0]["session_id"] == "ch_geo_raw_str:vid_inv_1234"

    def test_discover_inventory_delegates_to_llm_judge_port_with_complete_context(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        cand_list = [{"title": "Bacia do Mediterrâneo", "type": "entity"}]
        cand = json.dumps(cand_list, ensure_ascii=False)
        llm = MockLLMAdapter(responses=[cand])
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="atomic_inventory",
            passed=True,
            overall_score=0.98,
            criteria_scores=(),
            provider="gemini",
        )

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            llm_judge_port=mock_judge,
            max_rewrites=1,
        )
        inventory = use_case.execute(sample_compendium)
        assert len(inventory.items) == 1
        mock_judge.evaluate.assert_called_once()
        ctx = mock_judge.evaluate.call_args[0][0]
        assert ctx.stage_name == "atomic_inventory"
        assert ctx.raw_text == sample_compendium.body
        assert ctx.candidate_text == json.dumps(cand_list)
        assert ctx.metadata == {
            "title": "The Longue Durée of Mediterranean Trade",
            "channel": "Geopolitics Channel",
        }
        assert ctx.trace_id == "vid_inv_1234_inventory_judge"
        assert ctx.required_criteria == (JudgeCriterion.INVENTORY_COHERENCE,)

    def test_discover_inventory_multiple_retries_and_user_identity_logging(
        self, sample_compendium: EnrichedCompendium, caplog: pytest.LogCaptureFixture
    ) -> None:
        prompt_provider = JsonPromptProvider()
        cand1 = json.dumps([{"title": "Bad 1", "type": "concept"}])
        cand2 = json.dumps([{"title": "Bad 2", "type": "concept"}])
        cand3 = json.dumps([{"title": "Good Note", "type": "concept"}])

        llm = MockLLMAdapter(responses=[cand1, "false", cand2, "false", cand3, "true"])
        user = UserIdentity("user_operator_99")

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=3,
        )
        with caplog.at_level(logging.INFO):
            inventory = use_case.execute(sample_compendium, user=user)

        assert len(inventory.items) == 1
        # Verify user_id and prompt propagation
        assert llm.call_history[0]["user_id"] == "user_operator_99"
        assert llm.call_history[0]["prompt"] is not None
        assert llm.call_history[1]["user_id"] == "user_operator_99"

        # Verify Attempt 0 was not logged
        assert "Attempt 0" not in caplog.text

        # Verify exact record messages
        retry_messages = [
            rec.getMessage()
            for rec in caplog.records
            if "[InventoryDiscovery]" in rec.getMessage()
        ]
        assert len(retry_messages) == 2
        assert (
            retry_messages[0]
            == "[InventoryDiscovery] Attempt 1: candidate inventory compliance check failed for 'vid_inv_1234'. Re-extracting."
        )
        assert (
            retry_messages[1]
            == "[InventoryDiscovery] Attempt 2: candidate inventory compliance check failed for 'vid_inv_1234'. Re-extracting."
        )


    def test_fallback_judge_prompt_provider_argument_fidelity(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        cand_list = [{"title": "Bacia do Mediterrâneo", "type": "entity"}]
        cand = json.dumps(cand_list, ensure_ascii=False)
        llm = MockLLMAdapter(responses=[cand, "true"])

        mock_provider = MagicMock(spec=PromptProviderPort)
        mock_provider.get_prompt.side_effect = [
            ChatPrompt(messages=(ChatMessage(role=MessageRole.USER, content="extract entities"),)),
            ChatPrompt(messages=(ChatMessage(role=MessageRole.USER, content="judge boolean: true"),)),
        ]

        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=llm,
            prompt_provider=mock_provider,
            judge_enabled=True,
        )
        inventory = use_case.execute(sample_compendium)
        assert len(inventory.items) == 1

        assert mock_provider.get_prompt.call_count == 2
        # Call 1: extraction prompt
        extract_call = mock_provider.get_prompt.call_args_list[0]
        assert extract_call[0][0] == PromptKey.ATOMIC_INVENTORY
        assert extract_call[1]["content_title"] == sample_compendium.title.value
        assert extract_call[1]["channel_name"] == sample_compendium.channel_name
        assert extract_call[1]["compendium_body"] == sample_compendium.body

        # Call 2: judge prompt
        judge_call = mock_provider.get_prompt.call_args_list[1]
        assert judge_call[0][0] == PromptKey.JUDGE_ATOMIC_INVENTORY
        assert judge_call[1]["content_title"] == sample_compendium.title.value
        assert judge_call[1]["channel_name"] == sample_compendium.channel_name
        assert judge_call[1]["compendium_body"] == sample_compendium.body
        assert judge_call[1]["inventory_json"] == json.dumps(cand_list)

    def test_evaluate_candidate_inventory_fallback_returns_true_when_no_judge_or_provider(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        use_case = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=MockLLMAdapter(),
            prompt_provider=None,
            judge_enabled=True,
            llm_judge_port=None,
        )
        res = use_case._evaluate_candidate_inventory(
            candidate_data=[{"title": "Valid", "type": "entity"}],
            compendium=sample_compendium,
            judge_trace_id="test_trace",
            session_id="test_session",
            user_id="test_user",
        )
        assert res is True
