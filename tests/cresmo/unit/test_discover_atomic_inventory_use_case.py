"""Unit tests for DiscoverAtomicInventoryUseCase with LLM-as-a-Judge and Deterministic Guardrails.

Conforms to:
- ADR-024: Iterative LLM-as-a-Judge and Deterministic Guardrails for Atomic Inventory Discovery
- SPEC-009: Atomic Inventory Discovery Judge and Guardrails Specification
"""

from __future__ import annotations

import json

import pytest

from cresmo.application.use_cases.discover_atomic_inventory import (
    DiscoverAtomicInventoryUseCase,
    is_valid_inventory_json_structure,
)
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import ChannelName, ContentId, NoteTitle
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
        assert "Does the candidate inventory strictly satisfy" in llm.call_history[1]["prompt"]

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

    def test_discover_inventory_delegates_to_llm_judge_port_when_provided(
        self, sample_compendium: EnrichedCompendium
    ) -> None:
        """Verify DiscoverAtomicInventoryUseCase delegates 100% to LlmJudgePort (ADR-029)."""
        from unittest.mock import MagicMock

        from cresmo.application.ports import LlmJudgePort
        from cresmo.domain.value_objects import JudgeEvaluation

        cand = json.dumps([{"title": "Bacia do Mediterrâneo", "type": "entity"}])
        llm = MockLLMAdapter(responses=[cand])
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="atomic_inventory",
            passed=True,
            overall_score=0.95,
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

