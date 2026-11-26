"""Shared execution runner for prompt-driven LLM-as-a-Judge adapters.

Extracts template resolution, JSON verdict parsing, and composite scoring policy
evaluation into a composable function shared across GeminiJudgeAdapter and
OllamaJudgeAdapter (DRY + SRP + OCP).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Final

import structlog

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import (
    ChatPrompt,
    EvaluationContext,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.criterion_parser import (
    clean_json_markdown,
    parse_criteria_scores,
)

logger = structlog.get_logger(__name__)

_MS_PER_SECOND: Final[float] = 1000.0
_KEY_CRITERIA: Final[str] = "criteria"


def evaluate_prompt_judge(
    *,
    context: EvaluationContext,
    prompt_provider: PromptProviderPort,
    pass_threshold: float,
    provider_name: str,
    invoke_llm: Callable[[ChatPrompt], str],
) -> JudgeEvaluation:
    """Resolve judge prompt template, invoke LLM callback, and score criteria deterministically.

    Args:
        context: Immutable evaluation context specifying stage, source, candidate, criteria,
            and mandatory ``judge_prompt_key``.
        prompt_provider: Externalized prompt template repository port.
        pass_threshold: Minimum score floor for individual criterion pass verdicts.
        provider_name: Concrete judge provider label stored on the resulting evaluation.
        invoke_llm: Provider transport callback mapping rendered ``ChatPrompt`` to raw JSON text.

    Returns:
        Evaluated ``JudgeEvaluation`` with composite weighted score and mechanical vetoes.

    Raises:
        ValueError: If ``context.judge_prompt_key`` is ``None`` or LLM output is not valid JSON.
    """
    if context.judge_prompt_key is None:
        raise ValueError(
            f"EvaluationContext.judge_prompt_key is required for stage '{context.stage_name}'."
        )

    start_time = time.perf_counter()
    criteria_names = [criterion.value for criterion in context.required_criteria]
    chat_prompt = prompt_provider.get_prompt(
        context.judge_prompt_key,
        stage_name=context.stage_name,
        criteria_json=json.dumps(criteria_names),
        source_text=context.raw_text,
        candidate_text=context.candidate_text,
    )

    try:
        raw_response_text = invoke_llm(chat_prompt)
    except Exception as exc:
        logger.warning("%s judge invocation failed: %s", provider_name, exc)
        raise

    latency_ms = (time.perf_counter() - start_time) * _MS_PER_SECOND

    try:
        parsed = json.loads(clean_json_markdown(raw_response_text))
    except json.JSONDecodeError as err:
        logger.error("Failed to parse %s judge response as JSON: %s", provider_name, raw_response_text)
        raise ValueError(
            f"{provider_name} judge returned non-JSON output: {raw_response_text}"
        ) from err

    criteria_scores_list = parse_criteria_scores(
        raw_criteria=parsed.get(_KEY_CRITERIA, []),
        pass_threshold=pass_threshold,
        logger_instance=logger,
    )

    return JudgeEvaluation.create_with_composite_verdict(
        target_stage=context.stage_name,
        criteria_scores=criteria_scores_list,
        provider=provider_name,
        pass_threshold=pass_threshold,
        latency_ms=latency_ms,
        trace_id=context.trace_id,
    )


__all__ = ["evaluate_prompt_judge"]
