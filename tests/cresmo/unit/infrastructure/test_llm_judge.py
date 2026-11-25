"""Hermetic Unit Tests for LlmJudgePort, Decision-Model Evaluators, and Adapters.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import json
from typing import Any, cast
from unittest.mock import MagicMock

import httpx
import pytest
import structlog.testing

from cresmo.domain.value_objects.prompt import ChatMessage, ChatPrompt, MessageRole, PromptKey
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.composite_judge import ResilientCompositeJudgeAdapter
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


class TestQualityValueObjects:
    """Test suite for domain value objects and invariant validations."""

    def test_criterion_score_valid_instantiation(self) -> None:
        score = CriterionScore(
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            score=0.95,
            passed=True,
            reasoning="All filler words removed.",
        )
        assert score.criterion == JudgeCriterion.ORALITY_REMOVAL
        assert score.score == 0.95
        assert score.passed is True
        assert score.reasoning == "All filler words removed."

    def test_criterion_score_out_of_bounds_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Score must be between 0.0 and 1.0"):
            CriterionScore(
                criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                score=1.5,
                passed=True,
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
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
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
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(
            user_prompt="CUSTOM GEMINI USER",
            system_prompt="CUSTOM GEMINI SYS",
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
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        adapter.evaluate(context)

        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args

        assert args[0] == PromptKey.JUDGE_FLUID_PROSE
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
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        eval_default = adapter_default.evaluate(context)
        assert eval_default.passed is False
        assert eval_default.criteria_scores[0].passed is False

        # Custom threshold 0.70 passes
        adapter_lenient = GeminiJudgeAdapter(client=mock_genai_client, pass_threshold=0.70)
        eval_lenient = adapter_lenient.evaluate(context)
        assert eval_lenient.passed is True
        assert eval_lenient.criteria_scores[0].passed is True

    def test_gemini_judge_applies_thinking_level_and_omits_deprecated_temperature(self) -> None:
        from google.genai import types

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

        adapter = GeminiJudgeAdapter(client=mock_genai_client, thinking_level="minimal")
        assert adapter.thinking_level == "minimal"
        assert not hasattr(adapter, "temperature")
        from cresmo.infrastructure.config import (
            DEFAULT_JUDGE_GEMINI_MODEL,
            DEFAULT_JUDGE_PASS_THRESHOLD,
        )

        assert adapter.pass_threshold == DEFAULT_JUDGE_PASS_THRESHOLD
        assert adapter.model == DEFAULT_JUDGE_GEMINI_MODEL

        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        adapter.evaluate(context)

        _, kwargs = mock_genai_client.models.generate_content.call_args
        config = kwargs["config"]
        assert config.temperature is None
        assert config.thinking_config is not None
        assert config.thinking_config.thinking_level == types.ThinkingLevel.MINIMAL
        assert config.max_output_tokens == 32_768

    def test_gemini_judge_uses_judge_gap_filler_for_gap_filler_stage(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "epistemic_grounding_segregation",
                        "score": 0.95,
                        "passed": True,
                        "reasoning": "Fully grounded in real-world facts.",
                    }
                ],
                "overall_score": 0.95,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(
            user_prompt="USER PROMPT",
            system_prompt="SYSTEM INSTRUCTION FOR GAP FILLER",
        )

        adapter = GeminiJudgeAdapter(
            client=mock_genai_client,
            prompt_provider=mock_prompt_provider,
        )
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source transcript",
            candidate_text="candidate compendium",
            required_criteria=(JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,),
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
        )
        evaluation = adapter.evaluate(context)

        assert evaluation.passed is True
        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args

        assert args[0] == PromptKey.JUDGE_GAP_FILLER
        assert kwargs["stage_name"] == "gap_filler"

    def test_gemini_judge_passes_response_schema_in_config(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "epistemic_grounding_segregation",
                        "score": 0.95,
                        "passed": True,
                        "reasoning": "Accurate grounding.",
                    }
                ],
                "overall_score": 0.95,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiJudgeAdapter(client=mock_genai_client)
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source",
            candidate_text="candidate",
            required_criteria=(JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,),
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
        )
        adapter.evaluate(context)

        mock_genai_client.models.generate_content.assert_called_once()
        _, kwargs = mock_genai_client.models.generate_content.call_args
        config = kwargs["config"]
        from cresmo.infrastructure.adapters.judges.criterion_parser import (
            JudgeResponseOutputSchema,
        )

        assert config.response_schema is JudgeResponseOutputSchema
        assert config.response_mime_type == "application/json"

    def test_gemini_judge_resiliently_parses_aliases_and_skips_unparseable_meta(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "name": "epistemic_grounding_segregation",
                        "score": 0.95,
                        "passed": True,
                        "reasoning": "Valid via name alias.",
                    },
                    {
                        "criterion_name": "conceptual_mechanical_decomposition",
                        "score": 0.92,
                        "passed": True,
                        "reasoning": "Valid via criterion_name alias.",
                    },
                    {
                        "summary": "Non-criterion meta object produced by LLM",
                        "overall_score": 0.95,
                    },
                ],
                "overall_score": 0.935,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiJudgeAdapter(client=mock_genai_client, pass_threshold=0.80)
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source",
            candidate_text="candidate",
            required_criteria=(
                JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
                JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
            ),
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
        )
        evaluation = adapter.evaluate(context)

        assert evaluation.passed is True
        assert len(evaluation.criteria_scores) == 2
        fg = evaluation.get_score(JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION)
        assert fg is not None
        assert fg.score == 0.95
        depth = evaluation.get_score(JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION)
        assert depth is not None
        assert depth.score == 0.92

    def test_gemini_judge_enforces_gap_filler_mechanical_veto_and_weights(self) -> None:
        mock_genai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "epistemic_grounding_segregation",
                        "score": 0.50,
                        "passed": False,
                        "reasoning": "Fabricated fact.",
                    },
                    {
                        "criterion": "conceptual_mechanical_decomposition",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                    {
                        "criterion": "braudelian_stratification",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                    {
                        "criterion": "genealogy_hidden_agency",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                    {
                        "criterion": "competing_hypotheses",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                    {
                        "criterion": "extra_info_granularity",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                    {
                        "criterion": "linear_style_naturalism",
                        "score": 1.0,
                        "passed": True,
                        "reasoning": "Ok.",
                    },
                ],
                "overall_score": 0.90,
                "passed": True,
            }
        )
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiJudgeAdapter(client=mock_genai_client, pass_threshold=0.80)
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source",
            candidate_text="candidate",
            required_criteria=(
                JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
                JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
                JudgeCriterion.BRAUDELIAN_STRATIFICATION,
                JudgeCriterion.GENEALOGY_HIDDEN_AGENCY,
                JudgeCriterion.COMPETING_HYPOTHESES,
                JudgeCriterion.EXTRA_INFO_GRANULARITY,
                JudgeCriterion.LINEAR_STYLE_NATURALISM,
            ),
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
        )
        evaluation = adapter.evaluate(context)

        # Weighted score: 0.50*0.20 + 1.0*0.80 = 0.90 >= 0.80, but Mechanical Veto MUST reject
        assert evaluation.overall_score == 0.9
        assert evaluation.is_vetoed is True
        assert evaluation.passed is False

    def test_transient_network_and_disconnect_error_detection(self) -> None:
        from cresmo.infrastructure.adapters.llm.gemini_common import (
            is_transient_cluster_error,
            is_transient_genai_error,
        )

        disconnect_err = Exception("Server disconnected without sending a response.")
        assert is_transient_genai_error(disconnect_err) is True
        assert is_transient_cluster_error(disconnect_err) is True

        conn_reset_err = ConnectionResetError("Connection reset by peer")
        assert is_transient_genai_error(conn_reset_err) is True
        assert is_transient_cluster_error(conn_reset_err) is True

        protocol_err = Exception("RemoteProtocolError: peer closed connection")
        assert is_transient_genai_error(protocol_err) is True
        assert is_transient_cluster_error(protocol_err) is True

        # Ensure quota exhaustion is NOT handled as cluster error (delegated to pool)
        quota_err = Exception("ResourceExhausted: 429 Resource has been exhausted")
        assert is_transient_genai_error(quota_err) is True
        assert is_transient_cluster_error(quota_err) is False

    def test_gemini_judge_adapter_accepts_timeout_seconds(self) -> None:
        """Verify GeminiJudgeAdapter accepts timeout_seconds and passes it to pool."""
        judge = GeminiJudgeAdapter(api_key="mock-key", timeout_seconds=45.0)
        assert judge._pool is not None
        assert judge._pool.timeout == 45.0

    def test_gemini_judge_normalizes_provider_prefix_on_model(self) -> None:
        """Verify ACL strips leading 'gemini:' provider prefix from judge model."""
        mock_client = MagicMock()
        judge = GeminiJudgeAdapter(model="gemini:gemini-3.8-flash", client=mock_client)
        assert judge.model == "gemini-3.8-flash"

    def test_transient_504_deadline_exceeded_returns_true(self) -> None:
        """Verify 504 DEADLINE_EXCEEDED error string is classified as transient."""
        from cresmo.infrastructure.adapters.llm.gemini_common import is_transient_genai_error

        assert is_transient_genai_error(RuntimeError("504 DEADLINE_EXCEEDED")) is True

    def test_gemini_judge_and_llm_adapter_share_common_retry_helper(self) -> None:
        """Verify GeminiJudgeAdapter and GeminiLLMAdapter share gemini_common.generate_content_with_retry."""
        import cresmo.infrastructure.adapters.judges.gemini_judge as gemini_judge_mod
        import cresmo.infrastructure.adapters.llm.gemini_adapter as gemini_adapter_mod
        from cresmo.infrastructure.adapters.llm.gemini_common import generate_content_with_retry

        assert callable(generate_content_with_retry)
        assert not hasattr(gemini_judge_mod, "_generate_content_with_retry")
        assert not hasattr(gemini_adapter_mod, "_generate_with_retry")

    def test_gemini_judge_retries_transient_503_then_succeeds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify GeminiJudgeAdapter retries transient 503 via shared retry helper."""
        from cresmo.infrastructure.adapters.llm.gemini_common import generate_content_with_retry

        retry_controller = cast(Any, generate_content_with_retry).retry
        monkeypatch.setattr(retry_controller, "sleep", lambda _: None)

        mock_client = MagicMock()
        valid_resp = MagicMock(
            text=json.dumps(
                {
                    "criteria": [
                        {"criterion": "orality_removal", "score": 0.95, "passed": True}
                    ],
                    "overall_score": 0.95,
                    "passed": True,
                }
            )
        )
        mock_client.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE: high demand"),
            valid_resp,
        ]

        judge = GeminiJudgeAdapter(client=mock_client, model="gemini-3.5-flash-lite")
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        evaluation = judge.evaluate(context)

        assert evaluation.passed is True
        assert mock_client.models.generate_content.call_count == 2

    def test_gemini_judge_fails_over_to_fallback_model_after_exhausting_3_retries(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify GeminiJudgeAdapter fails over to fallback_model after exhausting 3 primary retries."""
        from cresmo.infrastructure.adapters.llm.gemini_common import generate_content_with_retry

        retry_controller = cast(Any, generate_content_with_retry).retry
        monkeypatch.setattr(retry_controller, "sleep", lambda _: None)

        mock_client = MagicMock()
        valid_resp = MagicMock(
            text=json.dumps(
                {
                    "criteria": [
                        {"criterion": "orality_removal", "score": 0.95, "passed": True}
                    ],
                    "overall_score": 0.95,
                    "passed": True,
                }
            )
        )
        mock_client.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE"),
            RuntimeError("503 UNAVAILABLE"),
            RuntimeError("503 UNAVAILABLE"),
            valid_resp,
        ]

        judge = GeminiJudgeAdapter(
            client=mock_client,
            model="gemini-3.5-flash-lite",
            fallback_model="gemini-3.6-flash",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        evaluation = judge.evaluate(context)

        assert evaluation.passed is True
        assert mock_client.models.generate_content.call_count == 4
        calls = mock_client.models.generate_content.call_args_list
        assert [c.kwargs["model"] for c in calls[:3]] == ["gemini-3.5-flash-lite"] * 3
        assert calls[3].kwargs["model"] == "gemini-3.6-flash"

    def test_gemini_judge_fallback_recomputes_thinking_config_for_fallback_model(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify fallback call clamps thinking_level appropriately for the fallback judge model."""
        from google.genai import types

        from cresmo.infrastructure.adapters.llm.gemini_common import generate_content_with_retry

        retry_controller = cast(Any, generate_content_with_retry).retry
        monkeypatch.setattr(retry_controller, "sleep", lambda _: None)

        mock_client = MagicMock()
        valid_resp = MagicMock(
            text=json.dumps(
                {
                    "criteria": [
                        {"criterion": "orality_removal", "score": 0.95, "passed": True}
                    ],
                    "overall_score": 0.95,
                    "passed": True,
                }
            )
        )
        mock_client.models.generate_content.side_effect = [
            ValueError("Primary failed"),
            valid_resp,
        ]

        judge = GeminiJudgeAdapter(
            client=mock_client,
            model="gemini-4-hydrogen",
            fallback_model="gemini-3.6-flash",
            thinking_level="xhigh",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        evaluation = judge.evaluate(context)

        assert evaluation.passed is True
        assert mock_client.models.generate_content.call_count == 2
        fallback_kwargs = mock_client.models.generate_content.call_args_list[1].kwargs
        assert fallback_kwargs["model"] == "gemini-3.6-flash"
        assert fallback_kwargs["config"].thinking_config is not None
        assert fallback_kwargs["config"].thinking_config.thinking_level == types.ThinkingLevel.HIGH

    def test_gemini_judge_does_not_failover_model_when_credential_pool_exhausted(self) -> None:
        """Verify 429 pool exhaustion raises immediately without failing over to secondary model."""
        from cresmo.infrastructure.adapters.llm.gemini_pool import (
            CredentialPoolExhaustedError,
            GeminiCredentialPool,
        )

        client1 = MagicMock()
        client1.models.generate_content.side_effect = RuntimeError(
            "429 RESOURCE_EXHAUSTED: retry in 60s"
        )
        pool = GeminiCredentialPool(keys=["k1"], client_factory=lambda _: client1)
        judge = GeminiJudgeAdapter(
            credential_pool=pool,
            model="gemini-3.5-flash-lite",
            fallback_model="gemini-3.6-flash",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )

        with pytest.raises(CredentialPoolExhaustedError):
            judge.evaluate(context)

        assert client1.models.generate_content.call_count == 1
        assert client1.models.generate_content.call_args.kwargs["model"] == "gemini-3.5-flash-lite"

    @pytest.mark.parametrize("fallback_model", [None, "gemini-3.5-flash-lite"])
    def test_gemini_judge_reraises_when_fallback_model_none_or_same_as_primary(
        self, fallback_model: str | None
    ) -> None:
        """Verify judge re-raises immediately when fallback_model is None or identical to primary."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = ValueError("Fatal error")

        judge = GeminiJudgeAdapter(
            client=mock_client,
            model="gemini-3.5-flash-lite",
            fallback_model=fallback_model,
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )

        with pytest.raises(ValueError, match="Fatal error"):
            judge.evaluate(context)

        assert mock_client.models.generate_content.call_count == 1

    def test_gemini_judge_normalizes_provider_prefix_on_fallback_model(self) -> None:
        """Verify ACL strips leading 'gemini:' provider prefix from fallback_model."""
        mock_client = MagicMock()
        judge = GeminiJudgeAdapter(
            model="gemini:gemini-3.8-flash",
            fallback_model="gemini:gemini-3.6-flash",
            client=mock_client,
        )
        assert judge.model == "gemini-3.8-flash"
        assert judge.fallback_model == "gemini-3.6-flash"

    def test_gemini_judge_credential_pool_init_variants_and_timeout(self) -> None:
        """Verify api_keys, CSV api_key, client timeout propagation, and unconfigured evaluate."""
        single_key_judge = GeminiJudgeAdapter(api_keys=["single-key"], timeout_seconds=42.5)
        assert single_key_judge._pool is not None
        assert single_key_judge._pool.key_count == 1
        assert single_key_judge._pool.timeout == 42.5

        csv_key_judge = GeminiJudgeAdapter(api_key=" key-a , , key-b ", timeout_seconds=19.0)
        assert csv_key_judge._pool is not None
        assert csv_key_judge._pool.key_count == 2
        assert csv_key_judge._pool.timeout == 19.0

        client_judge = GeminiJudgeAdapter(client=MagicMock(), timeout_seconds=17.5)
        assert client_judge._pool is not None
        assert client_judge._pool.timeout == 17.5

        unconfigured = GeminiJudgeAdapter()
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        with pytest.raises(ValueError, match="Gemini API key must be provided explicitly"):
            unconfigured.evaluate(context)

    def test_gemini_judge_maps_chat_turns_system_instruction_and_disables_afc(self) -> None:
        """Verify multi-turn role mapping, system_instruction forwarding, and AFC disablement."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MagicMock(text="{}")

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt(
            system_prompt="STRICT SYSTEM INSTRUCTION",
            messages=(
                ChatMessage(role=MessageRole.USER, content="First user turn"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Assistant exemplar"),
            ),
        )

        judge = GeminiJudgeAdapter(client=mock_client, prompt_provider=mock_prompt_provider)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        judge.evaluate(context)

        _, kwargs = mock_client.models.generate_content.call_args
        contents = kwargs["contents"]
        assert len(contents) == 2
        assert contents[0].role == "user"
        assert contents[0].parts[0].text == "First user turn"
        assert contents[1].role == "model"
        assert contents[1].parts[0].text == "Assistant exemplar"

        config = kwargs["config"]
        assert config.system_instruction == "STRICT SYSTEM INSTRUCTION"
        assert config.automatic_function_calling is not None
        assert config.automatic_function_calling.disable is True

    def test_gemini_judge_empty_response_fallback_and_failover_adapter_label(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify failover logs canonical adapter label and empty response.text falls back to '{}'."""
        from cresmo.infrastructure.adapters.llm.gemini_common import generate_content_with_retry

        retry_controller = cast(Any, generate_content_with_retry).retry
        monkeypatch.setattr(retry_controller, "sleep", lambda _: None)

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE"),
            RuntimeError("503 UNAVAILABLE"),
            RuntimeError("503 UNAVAILABLE"),
            MagicMock(text=""),
        ]

        judge = GeminiJudgeAdapter(
            client=mock_client,
            model="gemini-3.5-flash-lite",
            fallback_model="gemini-3.6-flash",
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )

        with structlog.testing.capture_logs() as logs:
            evaluation = judge.evaluate(context)

        assert evaluation.criteria_scores == ()
        assert evaluation.passed is False
        assert any(
            entry.get("log_level") == "warning"
            and "Primary model" in str(entry.get("event", ""))
            and entry.get("positional_args", (None,))[0] == "GeminiJudgeAdapter"
            for entry in logs
        )


class TestOllamaJudgeAdapter:
    """Test suite for local Ollama fallback judge adapter."""

    def test_evaluate_parses_ollama_json_response(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "message": {
                "content": json.dumps(
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
        }
        mock_http_client.post.return_value = mock_post_resp

        adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            pass_threshold=0.80,
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="né então tipo assim",
            candidate_text="Portanto.",
            trace_id="tr-ollama-1",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
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
            "message": {
                "content": json.dumps(
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
        }
        mock_http_client.post.return_value = mock_post_resp

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(
            user_prompt="CUSTOM OLLAMA USER",
            system_prompt="CUSTOM OLLAMA SYS",
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
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )
        adapter.evaluate(context)

        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args

        assert args[0] == PromptKey.JUDGE_FLUID_PROSE
        assert kwargs["stage_name"] == "fluid_prose"
        assert kwargs["source_text"] == "raw text"
        assert kwargs["candidate_text"] == "cand text"

        call_kwargs = mock_http_client.post.call_args[1]
        assert call_kwargs["json"]["messages"] == [
            {"role": "system", "content": "CUSTOM OLLAMA SYS"},
            {"role": "user", "content": "CUSTOM OLLAMA USER"},
        ]

    def test_ollama_judge_uses_judge_gap_filler_for_gap_filler_stage(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "message": {
                "content": json.dumps(
                    {
                        "criteria": [
                            {
                                "criterion": "epistemic_grounding_segregation",
                                "score": 0.90,
                                "passed": True,
                                "reasoning": "Grounded.",
                            }
                        ],
                        "overall_score": 0.90,
                        "passed": True,
                    }
                )
            }
        }
        mock_http_client.post.return_value = mock_post_resp

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(
            user_prompt="OLLAMA GAP FILLER USER",
            system_prompt="OLLAMA GAP FILLER SYS",
        )

        adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            prompt_provider=mock_prompt_provider,
        )
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source raw",
            candidate_text="cand text",
            required_criteria=(JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,),
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
        )
        evaluation = adapter.evaluate(context)

        assert evaluation.passed is True
        mock_prompt_provider.get_prompt.assert_called_once()
        args, kwargs = mock_prompt_provider.get_prompt.call_args

        assert args[0] == PromptKey.JUDGE_GAP_FILLER
        assert kwargs["stage_name"] == "gap_filler"

    def test_ollama_judge_default_http_client_and_timeout(self) -> None:
        """Verify OllamaJudgeAdapter constructs httpx.Client with default and custom timeouts."""
        default_adapter = OllamaJudgeAdapter()
        try:
            assert isinstance(default_adapter._client, httpx.Client)
            assert default_adapter._client.timeout == httpx.Timeout(120.0)
        finally:
            default_adapter._client.close()

        custom_adapter = OllamaJudgeAdapter(timeout_seconds=45.0)
        try:
            assert isinstance(custom_adapter._client, httpx.Client)
            assert custom_adapter._client.timeout == httpx.Timeout(45.0)
        finally:
            custom_adapter._client.close()

    def test_ollama_judge_posts_canonical_payload_and_strips_trailing_slash(self) -> None:
        """Verify endpoint URL normalization and exact Ollama /api/chat JSON payload fields."""
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.json.return_value = {"message": {"content": "{}"}}
        mock_http_client.post.return_value = mock_post_resp

        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(
            user_prompt="USER",
            system_prompt="SYS",
        )

        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )

        default_adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            prompt_provider=mock_prompt_provider,
        )
        default_adapter.evaluate(context)
        assert mock_http_client.post.call_args.args[0] == "http://localhost:11434/api/chat"
        assert mock_http_client.post.call_args.kwargs["json"] == {
            "model": "qwen2.5:7b",
            "messages": [
                {"role": "system", "content": "SYS"},
                {"role": "user", "content": "USER"},
            ],
            "format": "json",
            "stream": False,
        }

        mock_http_client.post.reset_mock()
        custom_adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            base_url="http://127.0.0.1:11434///",
            model="llama3.2",
            prompt_provider=mock_prompt_provider,
        )
        assert custom_adapter._client is mock_http_client
        custom_adapter.evaluate(context)
        assert mock_http_client.post.call_args.args[0] == "http://127.0.0.1:11434/api/chat"
        assert mock_http_client.post.call_args.kwargs["json"]["model"] == "llama3.2"

        mock_http_client.post.reset_mock()
        non_slash_suffix_adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            base_url="http://127.0.0.1:11434/X",
            prompt_provider=mock_prompt_provider,
        )
        non_slash_suffix_adapter.evaluate(context)
        assert mock_http_client.post.call_args.args[0] == "http://127.0.0.1:11434/X/api/chat"

    def test_ollama_judge_handles_missing_content_and_non_dict_message(self) -> None:
        """Verify missing message.content and non-dict message fall back safely to '{}'."""
        mock_http_client = MagicMock()
        mock_prompt_provider = MagicMock()
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.single_turn(user_prompt="U")
        adapter = OllamaJudgeAdapter(
            http_client=mock_http_client,
            prompt_provider=mock_prompt_provider,
        )
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            required_criteria=(),
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        )

        mock_resp_empty_msg = MagicMock()
        mock_resp_empty_msg.json.return_value = {"message": {}}
        mock_http_client.post.return_value = mock_resp_empty_msg
        eval_empty = adapter.evaluate(context)
        assert eval_empty.criteria_scores == ()
        assert eval_empty.passed is False

        mock_resp_non_dict = MagicMock()
        mock_resp_non_dict.json.return_value = {"message": "unexpected-string"}
        mock_http_client.post.return_value = mock_resp_non_dict
        eval_non_dict = adapter.evaluate(context)
        assert eval_non_dict.criteria_scores == ()
        assert eval_non_dict.passed is False


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
            "choices": dict[str, Any](),
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
        assert ts_faithfulness.score == 0.90

    def test_typesafe_judge_evaluates_gap_filler_criteria(self) -> None:
        mock_http_client = MagicMock()
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "nouls": dict[str, Any](),
            "scores": {
                "epistemic_grounding_segregation": {"score": 0.92, "confidence": 0.95},
                "conceptual_mechanical_decomposition": {"score": 0.88, "confidence": 0.90},
                "braudelian_stratification": {"score": 0.85, "confidence": 0.88},
                "genealogy_hidden_agency": {"score": 0.89, "confidence": 0.91},
                "competing_hypotheses": {"score": 0.86, "confidence": 0.87},
                "extra_info_granularity": {"score": 0.90, "confidence": 0.92},
                "linear_style_naturalism": {"score": 0.87, "confidence": 0.89},
            },
        }
        mock_http_client.post.return_value = mock_post_resp

        adapter = TypeSafeJudgeAdapter(
            api_key="sk-test",
            http_client=mock_http_client,
            pass_threshold=0.80,
        )
        context = EvaluationContext(
            stage_name="gap_filler",
            raw_text="source text",
            candidate_text="candidate compendium text",
            required_criteria=(
                JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
                JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
                JudgeCriterion.BRAUDELIAN_STRATIFICATION,
                JudgeCriterion.GENEALOGY_HIDDEN_AGENCY,
                JudgeCriterion.COMPETING_HYPOTHESES,
                JudgeCriterion.EXTRA_INFO_GRANULARITY,
                JudgeCriterion.LINEAR_STYLE_NATURALISM,
            ),
        )
        evaluation = adapter.evaluate(context)

        assert evaluation.passed is True
        assert len(evaluation.criteria_scores) == 7
        score_eg = evaluation.get_score(JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION)
        assert score_eg is not None
        assert score_eg.score == 0.92
        assert score_eg.passed is True


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


class TestTelemetryJudgeDecoratorWiring:
    """Test suite for TelemetryJudgeDecorator emission and factory wiring (ADR-070)."""

    def test_emits_scores_for_each_criterion_when_telemetry_port_present(self) -> None:
        mock_judge = MagicMock()
        telemetry = InMemoryTelemetryPort()

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

        decorator = TelemetryJudgeDecorator(inner_judge=mock_judge, telemetry_port=telemetry)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="r",
            candidate_text="c",
            trace_id="tr-test-777",
        )

        result = decorator.evaluate(context)
        assert result == mock_eval
        assert len(telemetry.scores) == 2
        assert (
            telemetry.scores[0].name,
            telemetry.scores[0].value,
            telemetry.scores[0].comment,
        ) == (
            "fluid_prose.orality_removal",
            0.95,
            "Clean",
        )
        assert (
            telemetry.scores[1].name,
            telemetry.scores[1].value,
            telemetry.scores[1].comment,
        ) == (
            "fluid_prose.semantic_faithfulness",
            0.88,
            "Faithful",
        )
        assert telemetry.scores[0].trace_id == "tr-test-777"

    def test_emits_scores_with_observation_id_binding(self) -> None:
        mock_judge = MagicMock()
        telemetry = InMemoryTelemetryPort()

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

        decorator = TelemetryJudgeDecorator(inner_judge=mock_judge, telemetry_port=telemetry)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="r",
            candidate_text="c",
            trace_id="tr-test-999",
            observation_id="obs_span_abc123",
        )

        result = decorator.evaluate(context)
        assert result == mock_eval
        assert len(telemetry.scores) == 1
        assert telemetry.scores[0].trace_id == "tr-test-999"
        assert telemetry.scores[0].name == "fluid_prose.ner_preservation"
        assert telemetry.scores[0].value == 0.99
        assert telemetry.scores[0].comment == "Preserved"
        assert telemetry.scores[0].observation_id == "obs_span_abc123"

    def test_safe_bypass_when_telemetry_port_is_none(self) -> None:
        mock_judge = MagicMock()
        mock_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = mock_eval

        decorator = TelemetryJudgeDecorator(inner_judge=mock_judge, telemetry_port=None)
        context = EvaluationContext(stage_name="fluid_prose", raw_text="r", candidate_text="c")

        result = decorator.evaluate(context)
        assert result == mock_eval


class TestLlmJudgeFactory:
    """Test suite for build_llm_judge_adapter DI factory."""

    def test_build_llm_judge_adapter_creates_composite_decorator(self) -> None:
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import CresmoSettings, JudgeSettings

        settings = CresmoSettings(_env_file=None, judge=JudgeSettings(provider="gemini"))
        judge = build_llm_judge_adapter(settings, telemetry_port=None)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        composite = judge._inner_judge._inner_judge
        assert isinstance(composite, ResilientCompositeJudgeAdapter)
        assert isinstance(composite._primary, GeminiJudgeAdapter)
        assert isinstance(composite._fallback, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_typesafe_provider(self) -> None:
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import CresmoSettings, JudgeSettings

        settings = CresmoSettings(_env_file=None, judge=JudgeSettings(provider="typesafe"))
        judge = build_llm_judge_adapter(settings, telemetry_port=None)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        composite = judge._inner_judge._inner_judge
        assert isinstance(composite, ResilientCompositeJudgeAdapter)
        assert isinstance(composite._primary, TypeSafeJudgeAdapter)
        assert isinstance(composite._fallback, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_ollama_provider(self) -> None:
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import CresmoSettings, JudgeSettings

        settings = CresmoSettings(_env_file=None, judge=JudgeSettings(provider="ollama"))
        judge = build_llm_judge_adapter(settings, telemetry_port=None)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, OllamaJudgeAdapter)

    def test_build_llm_judge_adapter_injects_configured_tunables(self) -> None:
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import (
            CresmoSettings,
            JudgeGeminiSettings,
            JudgeSettings,
        )

        settings = CresmoSettings(
            _env_file=None,
            judge=JudgeSettings(
                provider="gemini",
                pass_threshold=0.88,
                gemini=JudgeGeminiSettings(
                    model="gemini-custom-judge",
                    thinking_level="medium",
                ),
            ),
        )
        judge = build_llm_judge_adapter(settings, telemetry_port=None)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        inner = judge._inner_judge._inner_judge
        assert isinstance(inner, ResilientCompositeJudgeAdapter)
        primary = inner._primary
        assert isinstance(primary, GeminiJudgeAdapter)
        assert primary.pass_threshold == 0.88
        assert primary.model == "gemini-custom-judge"
        assert primary.thinking_level == "medium"
        assert not hasattr(primary, "temperature")

        fallback = inner._fallback
        assert isinstance(fallback, OllamaJudgeAdapter)
        assert fallback.pass_threshold == 0.88

    def test_build_llm_judge_adapter_without_fallback_bypasses_composite(self) -> None:
        """Verify build_llm_judge_adapter with enable_fallback=False returns primary adapter directly."""
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import CresmoSettings, JudgeSettings

        settings = CresmoSettings(_env_file=None, judge=JudgeSettings(provider="gemini"))
        judge = build_llm_judge_adapter(settings, telemetry_port=None, enable_fallback=False)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        assert isinstance(judge._inner_judge._inner_judge, GeminiJudgeAdapter)
        assert not isinstance(judge._inner_judge._inner_judge, ResilientCompositeJudgeAdapter)

    def test_build_llm_judge_adapter_propagates_fallback_model_when_enabled(self) -> None:
        """Verify build_llm_judge_adapter propagates llm.gemini.fallback_model when fallback is enabled."""
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import (
            CresmoSettings,
            GeminiSettings,
            JudgeSettings,
            LlmSettings,
        )

        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(fallback_model="gemini-3.6-flash")),
            judge=JudgeSettings(provider="gemini"),
        )
        judge = build_llm_judge_adapter(settings, telemetry_port=None, enable_fallback=True)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        composite = judge._inner_judge._inner_judge
        assert isinstance(composite, ResilientCompositeJudgeAdapter)
        primary = composite._primary
        assert isinstance(primary, GeminiJudgeAdapter)
        assert primary.fallback_model == "gemini-3.6-flash"

    def test_build_llm_judge_adapter_disables_fallback_model_when_enable_fallback_false(
        self,
    ) -> None:
        """Verify enable_fallback=False disables secondary Gemini model failover for calibration."""
        from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
        from cresmo.infrastructure.config import (
            CresmoSettings,
            GeminiSettings,
            JudgeSettings,
            LlmSettings,
        )

        settings = CresmoSettings(
            _env_file=None,
            llm=LlmSettings(gemini=GeminiSettings(fallback_model="gemini-3.6-flash")),
            judge=JudgeSettings(provider="gemini"),
        )
        judge = build_llm_judge_adapter(settings, telemetry_port=None, enable_fallback=False)

        assert isinstance(judge, TelemetryJudgeDecorator)
        assert isinstance(judge._inner_judge, MechanicalPreflightJudgeDecorator)
        primary = judge._inner_judge._inner_judge
        assert isinstance(primary, GeminiJudgeAdapter)
        assert primary.fallback_model is None


class TestCoordinatorLlmJudgeIntegration:
    """Test suite for CresmoPipeline Stage 1 quality evaluation hooking."""

    def test_coordinator_triggers_llm_judge_for_fluid_prose(self) -> None:
        from cresmo.domain.entities import StageTranscript
        from cresmo.domain.value_objects import (
            Channel,
            Content,
            ContentId,
            MediaProvenance,
            StageExecutionPolicy,
        )
        from tests.cresmo.unit.application.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_1")
        canned_raw = StageTranscript(
            channel=Channel(name="Test Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_coord_1"),
            content=Content(id=cid, title="Test", text="Raw audio text with uh and um."),
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_stage_transcript("raw", canned_raw)
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

        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.application.pipeline.models import PipelineDependencies
        from cresmo.application.pipeline.stage_factory import StageFactory
        from cresmo.application.pipeline.stage_runner import PipelineStageRunner
        from cresmo.application.ports import (
            NoOpMetricsPort,
            NoOpPromptProviderPort,
            NoOpTelemetryPort,
        )

        policy = StageExecutionPolicy(judge_blocking=False)
        runner = PipelineStageRunner(
            PipelineDependencies(
                telemetry_port=NoOpTelemetryPort(),
                metrics_port=NoOpMetricsPort(),
                llm_judge=mock_judge,
                judge_blocking=False,
                prompt_provider=NoOpPromptProviderPort(),
                llm_transformation_port=mock_llm,
                stage_factory=StageFactory(policy=policy),
                ledger_port=ledger_port,
            )
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=vault_port,
            stage_runner=runner,
            ledger_port=ledger_port,
        )

        pipeline.execute(canned_raw)

        assert mock_judge.evaluate.call_count >= 1
        fluid_eval_ctx = mock_judge.evaluate.call_args_list[0][0][0]
        assert fluid_eval_ctx.stage_name == "fluid_prose"
        assert JudgeCriterion.ORALITY_REMOVAL in fluid_eval_ctx.required_criteria
        assert JudgeCriterion.SEMANTIC_FAITHFULNESS in fluid_eval_ctx.required_criteria
        assert JudgeCriterion.NER_PRESERVATION in fluid_eval_ctx.required_criteria
        assert JudgeCriterion.STRUCTURAL_COMPLIANCE in fluid_eval_ctx.required_criteria

        if mock_judge.evaluate.call_count >= 2:
            gap_eval_ctx = mock_judge.evaluate.call_args_list[1][0][0]
            assert gap_eval_ctx.stage_name == "gap_filler"
            assert JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION in gap_eval_ctx.required_criteria
            assert (
                JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION in gap_eval_ctx.required_criteria
            )

    def test_coordinator_blocking_mode_raises_on_quality_failure(self) -> None:
        from cresmo.domain.entities import StageTranscript
        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import (
            Channel,
            Content,
            ContentId,
            MediaProvenance,
            StageExecutionPolicy,
        )
        from tests.cresmo.unit.application.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_2")
        canned_raw = StageTranscript(
            channel=Channel(name="Test Channel"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_coord_2"),
            content=Content(id=cid, title="Test", text="Raw audio."),
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_stage_transcript("raw", canned_raw)
        ledger_port = InMemoryLedgerAdapter()

        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.45,
            criteria_scores=(),
            provider="gemini",
        )

        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.application.pipeline.models import PipelineDependencies
        from cresmo.application.pipeline.stage_factory import StageFactory
        from cresmo.application.pipeline.stage_runner import PipelineStageRunner
        from cresmo.application.ports import (
            NoOpMetricsPort,
            NoOpPromptProviderPort,
            NoOpTelemetryPort,
        )

        policy = StageExecutionPolicy(judge_blocking=True)
        runner = PipelineStageRunner(
            PipelineDependencies(
                telemetry_port=NoOpTelemetryPort(),
                metrics_port=NoOpMetricsPort(),
                llm_judge=mock_judge,
                judge_blocking=True,
                prompt_provider=NoOpPromptProviderPort(),
                llm_transformation_port=mock_llm,
                stage_factory=StageFactory(policy=policy),
                ledger_port=ledger_port,
            )
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=vault_port,
            stage_runner=runner,
            ledger_port=ledger_port,
        )

        with pytest.raises(DomainValidationError, match="Stage 'fluid_prose' quarantined"):
            pipeline.execute(canned_raw)

    def test_coordinator_records_session_output_on_success(self) -> None:
        """Verify CresmoPipeline records high-signal outcome to telemetry port upon completion."""

        from cresmo.domain.entities import StageTranscript
        from cresmo.domain.value_objects import (
            Channel,
            Content,
            ContentId,
            MediaProvenance,
            StageExecutionPolicy,
        )
        from tests.cresmo.unit.application.test_pipeline import SmartMockLLMAdapter
        from tests.doubles.mock_adapters import (
            InMemoryLedgerAdapter,
            InMemoryVaultAdapter,
            MockMediaIngestionPort,
        )

        cid = ContentId("vid_coord_telemetry")
        canned_raw = StageTranscript(
            channel=Channel(name="Test Channel"),
            provenance=MediaProvenance.create(
                url="https://youtube.com/watch?v=vid_coord_telemetry"
            ),
            content=Content(id=cid, title="Test", text="Raw audio text with speech noise."),
        )
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        vault_port.save_stage_transcript("raw", canned_raw)
        ledger_port = InMemoryLedgerAdapter()
        telemetry = InMemoryTelemetryPort()

        from cresmo.application.pipeline.coordinator import CresmoPipeline
        from cresmo.application.pipeline.models import PipelineDependencies
        from cresmo.application.pipeline.stage_factory import StageFactory
        from cresmo.application.pipeline.stage_runner import PipelineStageRunner
        from cresmo.application.ports import NoOpMetricsPort, NoOpPromptProviderPort

        policy = StageExecutionPolicy(judge_blocking=False)
        runner = PipelineStageRunner(
            PipelineDependencies(
                telemetry_port=telemetry,
                metrics_port=NoOpMetricsPort(),
                judge_blocking=False,
                prompt_provider=NoOpPromptProviderPort(),
                llm_transformation_port=mock_llm,
                stage_factory=StageFactory(policy=policy),
                ledger_port=ledger_port,
            )
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=vault_port,
            stage_runner=runner,
            ledger_port=ledger_port,
            telemetry_port=telemetry,
        )

        pipeline.execute(canned_raw)

        root_span = next(s for s in telemetry.spans if s.is_root)
        assert len(root_span.outputs) == 1
        recorded_output = root_span.outputs[0]
        assert recorded_output["status"] == "COMPLETED"
        assert recorded_output["stage"] == "wide_expander"
        assert recorded_output["stages_completed"] == [
            "fluid_prose",
            "gap_filler",
            "long_expander",
            "wide_expander",
        ]
        assert "word_count" in recorded_output
        assert "char_count" in recorded_output
