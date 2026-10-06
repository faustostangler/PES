"""Unit tests for OllamaCritiqueAdapter and CritiqueSynthesizerPort (ADR-031)."""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.application.ports import LLMTransformationPort
from cresmo.domain.value_objects import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    VerdictType,
)
from cresmo.infrastructure.adapters.ollama_critique_adapter import OllamaCritiqueAdapter


def test_critique_synthesizer_passed_evaluation_returns_empty() -> None:
    """Verify that an evaluation that passed returns an empty critique string."""
    adapter = OllamaCritiqueAdapter()
    evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.95,
        provider="ollama",
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                passed=True,
                verdict_type=VerdictType.SCORE,
                score=0.95,
                reasoning="Clean prose.",
            ),
        ),
    )
    result = adapter.synthesize(evaluation, "fluid_prose")
    assert result == ""


def test_critique_synthesizer_fallback_when_no_llm_port() -> None:
    """Verify fallback to rule-based critique when no LLM transformation port is wired."""
    adapter = OllamaCritiqueAdapter(llm_transformation_port=None)
    evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.4,
        provider="ollama",
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                passed=False,
                verdict_type=VerdictType.SCORE,
                score=0.4,
                reasoning="Contains 'você sabe' and filler words.",
                improvement_suggestion="Remove filler words.",
            ),
        ),
    )
    result = adapter.synthesize(evaluation, "fluid_prose")
    assert "orality_removal" in result
    assert "Remove filler words." in result


def test_critique_synthesizer_invokes_llm_transformation_port() -> None:
    """Verify that OllamaCritiqueAdapter formats prompt and invokes LLM transformation port."""
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "1. Delete all speech fillers.\n2. Ensure neutral tone."

    adapter = OllamaCritiqueAdapter(llm_transformation_port=mock_llm)
    evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.5,
        provider="ollama",
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                passed=False,
                verdict_type=VerdictType.SCORE,
                score=0.5,
                reasoning="Orality marks detected.",
            ),
        ),
    )

    result = adapter.synthesize(evaluation, "fluid_prose", trace_id="trace_123")
    assert result == "1. Delete all speech fillers.\n2. Ensure neutral tone."
    mock_llm.transform.assert_called_once()
    _, kwargs = mock_llm.transform.call_args
    assert kwargs["trace_id"] == "trace_123"


def test_critique_synthesizer_resilient_fallback_on_exception() -> None:
    """Verify graceful fallback to rule-based critique when LLM transformation port raises error."""
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = RuntimeError("Ollama socket connection refused")

    adapter = OllamaCritiqueAdapter(llm_transformation_port=mock_llm)
    evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.3,
        provider="ollama",
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                passed=False,
                verdict_type=VerdictType.SCORE,
                score=0.3,
                reasoning="Hallucinated statements.",
            ),
        ),
    )

    result = adapter.synthesize(evaluation, "fluid_prose")
    assert "semantic_faithfulness" in result
    assert "Hallucinated statements." in result


def test_critique_synthesizer_uses_custom_prompt_provider() -> None:
    """Verify that OllamaCritiqueAdapter delegates prompt resolution to PromptProviderPort."""
    from cresmo.domain.value_objects import PromptKey
    from cresmo.domain.value_objects.prompt import ChatPrompt

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "1. Direct instruction."
    mock_prompt_provider = MagicMock()
    custom_chat_prompt = ChatPrompt.from_system_and_user(
        system="CUSTOM SYS", user="CUSTOM PROMPT"
    )
    mock_prompt_provider.get_prompt.return_value = custom_chat_prompt

    adapter = OllamaCritiqueAdapter(
        llm_transformation_port=mock_llm,
        prompt_provider=mock_prompt_provider,
    )
    evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.4,
        provider="ollama",
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                passed=False,
                verdict_type=VerdictType.SCORE,
                score=0.4,
                reasoning="Orality marks detected.",
            ),
        ),
    )

    result = adapter.synthesize(evaluation, "fluid_prose")
    assert result == "1. Direct instruction."
    mock_prompt_provider.get_prompt.assert_called_once()
    args, kwargs = mock_prompt_provider.get_prompt.call_args
    assert args[0] == PromptKey.OLLAMA_CRITIQUE
    assert kwargs["stage_name"] == "fluid_prose"
    assert kwargs["overall_score"] == "0.40"
    assert "orality_removal" in kwargs["criteria_failures"]

    mock_llm.transform.assert_called_once_with(
        prompt=custom_chat_prompt,
        temperature=0.1,
        trace_id=None,
    )
