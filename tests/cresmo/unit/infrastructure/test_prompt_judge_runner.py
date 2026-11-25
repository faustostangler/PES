"""Hermetic unit tests for shared prompt-driven LLM judge runner (ADR-029)."""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import (
    ChatPrompt,
    EvaluationContext,
    JudgeCriterion,
    PromptKey,
)
from cresmo.infrastructure.adapters.judges import prompt_judge_runner
from cresmo.infrastructure.adapters.judges.prompt_judge_runner import evaluate_prompt_judge


def _make_context(
    criteria: tuple[JudgeCriterion, ...] = (
        JudgeCriterion.ORALITY_REMOVAL,
        JudgeCriterion.SEMANTIC_FAITHFULNESS,
    ),
) -> EvaluationContext:
    return EvaluationContext(
        stage_name="fluid_prose",
        raw_text="Raw spoken transcript.",
        candidate_text="Clean formal prose.",
        trace_id="tr-runner-1",
        required_criteria=criteria,
        judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
    )


def _make_provider() -> MagicMock:
    provider = MagicMock(spec=PromptProviderPort)
    provider.get_prompt.return_value = ChatPrompt.single_turn(
        user_prompt="Evaluate candidate.",
        system_prompt="Be strict.",
    )
    return provider


class TestPromptJudgeRunner:
    """Verify prompt resolution, latency measurement, JSON error handling, and logging."""

    def test_passes_serialized_criteria_and_computes_latency_ms(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ticks = iter([10.0, 10.25])
        monkeypatch.setattr(time, "perf_counter", lambda: next(ticks))

        provider = _make_provider()
        payload = json.dumps(
            {
                "criteria": [
                    {
                        "criterion": "orality_removal",
                        "score": 0.9,
                        "passed": True,
                        "reasoning": "Clean.",
                    }
                ]
            }
        )

        evaluation = evaluate_prompt_judge(
            context=_make_context(),
            prompt_provider=provider,
            pass_threshold=0.8,
            provider_name="custom-judge",
            invoke_llm=lambda _prompt: payload,
        )

        _, kwargs = provider.get_prompt.call_args
        assert kwargs["criteria_json"] == '["orality_removal", "semantic_faithfulness"]'
        assert evaluation.provider == "custom-judge"
        assert evaluation.trace_id == "tr-runner-1"
        assert evaluation.latency_ms == pytest.approx(250.0)
        assert evaluation.passed is True

    def test_logs_warning_and_reraises_when_invoke_llm_fails(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = _make_provider()
        spy_logger = MagicMock()
        monkeypatch.setattr(prompt_judge_runner, "logger", spy_logger)

        def _failing_llm(_prompt: ChatPrompt) -> str:
            raise RuntimeError("upstream 503")

        with pytest.raises(RuntimeError, match="upstream 503"):
            evaluate_prompt_judge(
                context=_make_context(),
                prompt_provider=provider,
                pass_threshold=0.8,
                provider_name="gemini",
                invoke_llm=_failing_llm,
            )

        spy_logger.warning.assert_called_once()
        call_args = spy_logger.warning.call_args.args
        assert call_args[0] == "%s judge invocation failed: %s"
        assert call_args[1] == "gemini"
        assert isinstance(call_args[2], RuntimeError)
        assert str(call_args[2]) == "upstream 503"

    def test_logs_error_and_raises_value_error_on_non_json_output(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = _make_provider()
        spy_logger = MagicMock()
        monkeypatch.setattr(prompt_judge_runner, "logger", spy_logger)

        with pytest.raises(
            ValueError,
            match=r"^ollama judge returned non-JSON output: not valid json$",
        ):
            evaluate_prompt_judge(
                context=_make_context(),
                prompt_provider=provider,
                pass_threshold=0.8,
                provider_name="ollama",
                invoke_llm=lambda _prompt: "not valid json",
            )

        spy_logger.error.assert_called_once_with(
            "Failed to parse %s judge response as JSON: %s",
            "ollama",
            "not valid json",
        )

    def test_missing_criteria_key_defaults_to_empty_list_without_type_warning(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = _make_provider()
        spy_logger = MagicMock()
        monkeypatch.setattr(prompt_judge_runner, "logger", spy_logger)

        evaluation = evaluate_prompt_judge(
            context=_make_context(),
            prompt_provider=provider,
            pass_threshold=0.8,
            provider_name="gemini",
            invoke_llm=lambda _prompt: "{}",
        )

        assert evaluation.criteria_scores == ()
        assert evaluation.passed is False
        spy_logger.debug.assert_not_called()

    def test_forwards_runner_logger_to_criterion_parser(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = _make_provider()
        spy_logger = MagicMock()
        monkeypatch.setattr(prompt_judge_runner, "logger", spy_logger)

        evaluation = evaluate_prompt_judge(
            context=_make_context(),
            prompt_provider=provider,
            pass_threshold=0.8,
            provider_name="gemini",
            invoke_llm=lambda _prompt: '{"criteria": ["malformed_item"]}',
        )

        assert evaluation.criteria_scores == ()
        spy_logger.debug.assert_called_once_with(
            "Skipping non-dict judge criterion item: %r",
            "malformed_item",
        )
