"""Hermetic Unit Tests for LlmJudgePort, Decision-Model Evaluators, and Adapters.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from cresmo.domain.value_objects.prompt import ChatPrompt
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.composite_judge import ResilientCompositeJudgeAdapter
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.langfuse_decorator import LangfuseJudgeDecorator
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter


class TestQualityValueObjects:
    """Test suite for domain value objects and invariant validations."""

    def test_criterion_score_valid_instantiation(self) -> None:
        score = CriterionScore(
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            score=0.95,
            passed=True,
            confidence=0.98,
            reasoning="All filler words removed.",
        )
        assert score.criterion == JudgeCriterion.ORALITY_REMOVAL
        assert score.score == 0.95
        assert score.passed is True
        assert score.confidence == 0.98
        assert score.reasoning == "All filler words removed."

    def test_criterion_score_out_of_bounds_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Score must be between 0.0 and 1.0"):
            CriterionScore(
                criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                score=1.5,
                passed=True,
            )

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            CriterionScore(
                criterion=JudgeCriterion.NER_PRESERVATION,
                score=0.8,
                passed=True,
                confidence=-0.1,
            )

    def test_judge_evaluation_get_score_query(self) -> None:
        s1 = CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.9, True)
        s2 = CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.85, True)
        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.875,
            criteria_scores=(s1, s2),
            provider="gemini",
            latency_ms=120.0,
            trace_id="tr-12345",
        )
        assert eval_result.target_stage == "fluid_prose"
        assert eval_result.passed is True
        assert eval_result.get_score(JudgeCriterion.ORALITY_REMOVAL) == s1
        assert eval_result.get_score(JudgeCriterion.NER_PRESERVATION) is None

    def test_evaluation_context_immutability(self) -> None:
        ctx = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="Raw audio text",
            candidate_text="Clean prose",
            trace_id="tr-test",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )
        assert ctx.stage_name == "fluid_prose"
        assert ctx.raw_text == "Raw audio text"
        assert ctx.required_criteria == (JudgeCriterion.ORALITY_REMOVAL,)


class TestGeminiJudgeAdapter:
    """Test suite for Gemini-based LLM-as-a-judge adapter."""

    def test_evaluate_parses_structured_json_response(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "orality_removal",
                        "score": 0.95,
                        "passed": True,
                        "reasoning": "No oralities remaining.",
                    },
                    {
                        "criterion": "semantic_faithfulness",
                        "score": 0.90,
                        "passed": True,
                        "reasoning": "Core facts intact.",
                    },
                ],
                "overall_score": 0.925,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiJudgeAdapter(client=mock_genai_client, model="gemini-3.5-flash-lite")
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="uh so we went there you know",
            candidate_text="We went there.",
            trace_id="tr-gemini-1",
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
            ),
        )

        evaluation = adapter.evaluate(context)
        assert evaluation.passed is True
        assert evaluation.provider == "gemini"
        assert evaluation.trace_id == "tr-gemini-1"
        assert len(evaluation.criteria_scores) == 2
        score_item = evaluation.get_score(JudgeCriterion.ORALITY_REMOVAL)
        assert score_item is not None
        assert score_item.score == 0.95

    def test_gemini_judge_uses_custom_prompt_provider(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "orality_removal",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Clean",
                    }
                ],
                "overall_score": 1.0,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.from_system_and_user(
            system="CUSTOM GEMINI SYS",
            user="CUSTOM GEMINI USER",
        )

        adapter = GeminiJudgeAdapter(
            client=mock_genai_client,
            prompt_provider=mock_prompt_provider,
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )
        adapter.evaluate(context)

        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args
        from cresmo.domain.value_objects import PromptKey

        assert args[0] == PromptKey.LLM_JUDGE
        assert kwargs["stage_name"] == "fluid_prose"
        assert kwargs["source_text"] == "raw"
        assert kwargs["candidate_text"] == "cand"

    def test_gemini_judge_raises_value_error_without_api_key_or_client(self) -> None:
        """Verify fail-fast when attempting to access unconfigured client (ADR-026 Rule 9)."""
        adapter = GeminiJudgeAdapter()
        with pytest.raises(ValueError, match="Gemini API key must be provided explicitly"):
            _ = adapter.client

    def test_gemini_judge_respects_custom_pass_threshold(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "orality_removal",
                        "score": 0.75,
                        "reasoning": "Mostly clean.",
                    }
                ],
                "overall_score": 0.75,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        # Default threshold 0.8 fails
        adapter_default = GeminiJudgeAdapter(client=mock_genai_client)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )
        eval_default = adapter_default.evaluate(context)
        assert eval_default.passed is False
        assert eval_default.criteria_scores[0].passed is False

        # Custom threshold 0.70 passes
        adapter_lenient = GeminiJudgeAdapter(client=mock_genai_client, pass_threshold=0.70)
        eval_lenient = adapter_lenient.evaluate(context)
        assert eval_lenient.passed is True
        assert eval_lenient.criteria_scores[0].passed is True

    def test_gemini_judge_respects_custom_temperature(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [],
                "overall_score": 1.0,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiJudgeAdapter(client=mock_genai_client, temperature=0.7)
        assert adapter.temperature == 0.7
        assert adapter.pass_threshold == 0.8
        assert adapter.model == "gemini-3.5-flash-lite"

        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
        )
        adapter.evaluate(context)

        _, kwargs = mock_genai_client.models.generate_content.call_args
        config = kwargs["config"]
        assert config.temperature == 0.7


class TestOllamaJudgeAdapter:
    """Test suite for local Ollama fallback judge adapter."""

    def test_evaluate_parses_ollama_json_response(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "response": json.dumps(
                {
                    "criteria": [
                        {
                            "criterion": "orality_removal",
                            "score": 0.85,
                            "passed": True,
                            "reasoning": "Acceptable cleanup.",
                        }
                    ],
                    "overall_score": 0.85,
                    "passed": True,
                }
            )
        }
        mock_http_client.post.return_value = mock_post_resp

        adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="né então tipo assim",
            candidate_text="Portanto.",
            trace_id="tr-ollama-1",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )

        evaluation = adapter.evaluate(context)
        assert evaluation.passed is True
        assert evaluation.provider == "ollama"
        ollama_score = evaluation.get_score(JudgeCriterion.ORALITY_REMOVAL)
        assert ollama_score is not None
        assert ollama_score.score == 0.85

    def test_ollama_judge_uses_custom_prompt_provider(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "response": json.dumps(
                {
                    "criteria": [
                        {
                            "criterion": "orality_removal",
                            "score": 1.0,
                            "passed": True,
                            "reasoning": "Ok",
                        }
                    ],
                    "overall_score": 1.0,
                    "passed": True,
                }
            )
        }
        mock_http_client.post.return_value = mock_post_resp

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.from_system_and_user(
            system="CUSTOM OLLAMA SYS",
            user="CUSTOM OLLAMA USER",
        )

        adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            prompt_provider=mock_prompt_provider,
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw text",
            candidate_text="cand text",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )
        adapter.evaluate(context)

        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args
        from cresmo.domain.value_objects import PromptKey

        assert args[0] == PromptKey.LLM_JUDGE
        assert kwargs["stage_name"] == "fluid_prose"
        assert kwargs["source_text"] == "raw text"
        assert kwargs["candidate_text"] == "cand text"

        call_kwargs = mock_http_client.post.call_args[1]
        assert call_kwargs["json"]["messages"] == [
            {"role": "system", "content": "CUSTOM OLLAMA SYS"},
            {"role": "user", "content": "CUSTOM OLLAMA USER"},
        ]


class TestTypeSafeJudgeAdapter:
    """Test suite for TypeSafe AI (System One Jev) decision-model evaluator."""

    def test_evaluate_with_mock_typesafe_http_response(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "nouls": {
                "orality_removal": {"noul": 0.98},
                "ner_preservation": {"noul": 0.95},
            },
            "scores": {
                "semantic_faithfulness": {"score": 0.90, "confidence": 0.94},
            },
            "choices": {},
        }
        mock_http_client.post.return_value = mock_post_resp

        adapter = TypeSafeJudgeAdapter(
            http_client=mock_http_client,
            api_key="ts-test-key",
            model="jev-latest",
            base_url="https://api.typesafe.ai/v1",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="Raw text",
            candidate_text="Candidate text",
            trace_id="tr-typesafe-1",
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
                JudgeCriterion.NER_PRESERVATION,
            ),
        )

        evaluation = adapter.evaluate(context)
        assert evaluation.passed is True
        assert evaluation.provider == "typesafe"
        assert evaluation.trace_id == "tr-typesafe-1"
        ts_orality = evaluation.get_score(JudgeCriterion.ORALITY_REMOVAL)
        assert ts_orality is not None
        assert ts_orality.score == 0.98
        ts_faithfulness = evaluation.get_score(JudgeCriterion.SEMANTIC_FAITHFULNESS)
        assert ts_faithfulness is not None
        assert ts_faithfulness.confidence == 0.94


class TestResilientCompositeJudgeAdapter:
    """Test suite for fallback resilience chain (Primary -> Fallback)."""

    def test_primary_succeeds_without_calling_fallback(self) -> None:
        primary = MagicMock()
        fallback = MagicMock()
        expected_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(),
            provider="gemini",
        )
        primary.evaluate.return_value = expected_eval

        composite = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)
        context = EvaluationContext(stage_name="fluid_prose", raw_text="r", candidate_text="c")

        result = composite.evaluate(context)
        assert result == expected_eval
        primary.evaluate.assert_called_once_with(context)
        fallback.evaluate.assert_not_called()

    def test_primary_fails_triggers_fallback(self) -> None:
        primary = MagicMock()
        fallback = MagicMock()
        primary.evaluate.side_effect = ConnectionError("Gemini API rate limit / timeout")

        fallback_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.85,
            criteria_scores=(),
            provider="ollama",
        )
        fallback.evaluate.return_value = fallback_eval

        composite = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)
        context = EvaluationContext(stage_name="fluid_prose", raw_text="r", candidate_text="c")

        result = composite.evaluate(context)
        assert result == fallback_eval
        assert result.provider == "ollama"
        primary.evaluate.assert_called_once_with(context)
        fallback.evaluate.assert_called_once_with(context)


class TestLangfuseJudgeDecorator:
    """Test suite for Langfuse telemetry emission decorator."""

    def test_emits_scores_for_each_criterion_when_client_present(self) -> None:
        mock_judge = MagicMock()
        mock_langfuse = MagicMock()

        s1 = CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.95, True, reasoning="Clean")
        s2 = CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.88, True, reasoning="Faithful")
        mock_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.915,
            criteria_scores=(s1, s2),
            provider="gemini",
            trace_id="tr-test-777",
        )
        mock_judge.evaluate.return_value = mock_eval

        decorator = LangfuseJudgeDecorator(inner_judge=mock_judge, langfuse_client=mock_langfuse)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="r",
            candidate_text="c",
            trace_id="tr-test-777",
        )

        result = decorator.evaluate(context)
        assert result == mock_eval
        assert mock_langfuse.create_score.call_count == 2
        mock_langfuse.create_score.assert_any_call(
            trace_id="tr-test-777",
            name="fluid_prose.orality_removal",
            value=0.95,
            comment="Clean",
        )
        mock_langfuse.create_score.assert_any_call(
            trace_id="tr-test-777",
            name="fluid_prose.semantic_faithfulness",
            value=0.88,
            comment="Faithful",
        )

    def test_emits_scores_with_observation_id_binding(self) -> None:
        mock_judge = MagicMock()
        mock_langfuse = MagicMock()

        s1 = CriterionScore(JudgeCriterion.NER_PRESERVATION, 0.99, True, reasoning="Preserved")
        mock_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.99,
            criteria_scores=(s1,),
            provider="gemini",
            trace_id="tr-test-999",
        )
        mock_judge.evaluate.return_value = mock_eval

        decorator = LangfuseJudgeDecorator(inner_judge=mock_judge, langfuse_client=mock_langfuse)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="r",
            candidate_text="c",
            trace_id="tr-test-999",
            observation_id="obs_span_abc123",
        )

        result = decorator.evaluate(context)
        assert result == mock_eval
        mock_langfuse.create_score.assert_called_once_with(
            trace_id="tr-test-999",
            name="fluid_prose.ner_preservation",
            value=0.99,
            comment="Preserved",
            observation_id="obs_span_abc123",
        )

    def test_safe_bypass_when_langfuse_client_is_none(self) -> None:
        mock_judge = MagicMock()
        mock_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = mock_eval

        decorator = LangfuseJudgeDecorator(inner_judge=mock_judge, langfuse_client=None)
        context = EvaluationContext(stage_name="fluid_prose", raw_text="r", candidate_text="c")

        result = decorator.evaluate(context)
        assert result == mock_eval


class TestLlmJudgeFactory:
    """Test suite for build_llm_judge_adapter DI factory."""

    def test_build_llm_judge_adapter_creates_composite_decorator(self) -> None:
        from cresmo.infrastructure.config import CresmoSettings
        from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

        settings = CresmoSettings(judge_provider="gemini")
        judge = build_llm_judge_adapter(settings, langfuse_client=None)

        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, ResilientCompositeJudgeAdapter)
        assert isinstance(judge._inner_judge._primary, GeminiJudgeAdapter)
        assert isinstance(judge._inner_judge._fallback, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_typesafe_provider(self) -> None:
        from cresmo.infrastructure.config import CresmoSettings
        from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

        settings = CresmoSettings(judge_provider="typesafe")
        judge = build_llm_judge_adapter(settings, langfuse_client=None)

        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, ResilientCompositeJudgeAdapter)
        assert isinstance(judge._inner_judge._primary, TypeSafeJudgeAdapter)
        assert isinstance(judge._inner_judge._fallback, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_ollama_provider(self) -> None:
        from cresmo.infrastructure.config import CresmoSettings
        from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

        settings = CresmoSettings(judge_provider="ollama")
        judge = build_llm_judge_adapter(settings, langfuse_client=None)

        assert isinstance(judge, LangfuseJudgeDecorator)
        assert isinstance(judge._inner_judge, ResilientCompositeJudgeAdapter)
        assert isinstance(judge._inner_judge._primary, OllamaJudgeAdapter)
        assert isinstance(judge._inner_judge._fallback, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_injects_configured_tunables(self) -> None:
        from cresmo.infrastructure.config import CresmoSettings
        from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

        settings = CresmoSettings(
            judge_provider="gemini",
            judge_pass_threshold=0.88,
            judge_gemini_model="gemini-custom-judge",
            judge_temperature=0.15,
        )
        judge = build_llm_judge_adapter(settings, langfuse_client=None)

        assert isinstance(judge, LangfuseJudgeDecorator)
        inner = judge._inner_judge
        assert isinstance(inner, ResilientCompositeJudgeAdapter)
        primary = inner._primary
        assert isinstance(primary, GeminiJudgeAdapter)
        assert primary.pass_threshold == 0.88
        assert primary.model == "gemini-custom-judge"
        assert primary.temperature == 0.15

        fallback = inner._fallback
        assert isinstance(fallback, OllamaJudgeAdapter)
        assert fallback.pass_threshold == 0.88


class TestCoordinatorLlmJudgeIntegration:
    """Test suite for CresmoPipeline Stage 1 quality evaluation hooking."""

    def test_coordinator_triggers_llm_judge_for_fluid_prose(self) -> None:
        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.domain.entities import SourceTranscript
        from cresmo.domain.value_objects import ChannelName, ContentId
        from cresmo.infrastructure.config import CresmoSettings
        from tests.cresmo.unit.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_1")
        canned_raw = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Test Channel"),
            body="Raw audio text with uh and um.",
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_transcript(canned_raw)
        ledger_port = InMemoryLedgerAdapter()

        mock_judge = MagicMock()
        mock_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.92,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = mock_eval

        settings = CresmoSettings(judge_blocking=False)
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
            settings=settings,
            llm_judge_port=mock_judge,
        )

        pipeline.execute(canned_raw)

        assert mock_judge.evaluate.call_count >= 1
        eval_ctx = mock_judge.evaluate.call_args[0][0]
        assert eval_ctx.stage_name == "fluid_prose"
        assert JudgeCriterion.ORALITY_REMOVAL in eval_ctx.required_criteria
        assert JudgeCriterion.SEMANTIC_FAITHFULNESS in eval_ctx.required_criteria
        assert JudgeCriterion.NER_PRESERVATION in eval_ctx.required_criteria
        assert JudgeCriterion.STRUCTURAL_COMPLIANCE in eval_ctx.required_criteria

    def test_coordinator_blocking_mode_raises_on_quality_failure(self) -> None:
        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.domain.entities import SourceTranscript
        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import ChannelName, ContentId
        from cresmo.infrastructure.config import CresmoSettings
        from tests.cresmo.unit.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_2")
        canned_raw = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Test Channel"),
            body="Raw audio.",
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_transcript(canned_raw)
        ledger_port = InMemoryLedgerAdapter()

        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.45,
            criteria_scores=(),
            provider="gemini",
        )

        settings = CresmoSettings(judge_blocking=True)
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
            settings=settings,
            llm_judge_port=mock_judge,
        )

        with pytest.raises(DomainValidationError, match="Stage 'fluid_prose' quarantined"):
            pipeline.execute(canned_raw)

    def test_coordinator_records_session_output_on_success(self) -> None:
        """Verify CresmoPipeline records high-signal outcome to telemetry port upon completion."""
        from unittest.mock import MagicMock

        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.domain.entities import SourceTranscript
        from cresmo.domain.value_objects import ChannelName, ContentId
        from cresmo.infrastructure.config import CresmoSettings
        from tests.cresmo.unit.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_telemetry")
        canned_raw = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Test Channel"),
            body="Raw audio text with speech noise.",
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_transcript(canned_raw)
        ledger_port = InMemoryLedgerAdapter()
        mock_telemetry = MagicMock()

        settings = CresmoSettings(judge_blocking=False)
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
            settings=settings,
            telemetry_port=mock_telemetry,
        )

        pipeline.execute(canned_raw)

        mock_telemetry.record_session_output.assert_called_once()
        recorded_output = mock_telemetry.record_session_output.call_args[0][0]
        assert recorded_output["status"] == "COMPLETED"
        assert recorded_output["stage"] == "fluid_prose"
        assert "word_count" in recorded_output
        assert "char_count" in recorded_output
