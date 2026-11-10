"""Stage candidate generation, multi-pass saturation, and closed-loop evaluation execution.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC)
- ADR-028: Multi-pass early stopping and mechanical saturation
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_telemetry import (
    as_str,
    attach_evaluation_span_attributes,
)
from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.services.mechanical_validator import (
    check_complementary_mechanical_saturation,
)
from cresmo.domain.value_objects import (
    CandidateText,
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    JudgeEvaluation,
    StageEvaluationSpec,
)

logger = structlog.get_logger(__name__)


def generate_stage_candidate[TSource, TOutput](
    stage_config: StageConfig[TSource, TOutput],
    source: TSource,
    *,
    context: PipelineExecutionContext,
    prompt_provider: PromptProviderPort,
    llm_port: LLMTransformationPort,
    attempt: int,
    active_trace_id: str,
    critique: str | None = None,
) -> CandidateText:
    """Build prompt and invoke LLM transformation port to generate CandidateText (multi-pass aware)."""
    raw_max_passes = getattr(stage_config, "max_passes", 1)
    max_passes = raw_max_passes if isinstance(raw_max_passes, int) and raw_max_passes > 0 else 1

    pass_kwargs: dict[str, Any] = (
        {"pass_num": 1, "total_passes": max_passes} if max_passes > 1 else {}
    )
    if max_passes > 1:
        logger.info(
            "[StageRunner] Executing pass 1/%d for %s...",
            max_passes,
            stage_config.stage_name,
        )
    chat_prompt = stage_config.build_transform_prompt(
        prompt_provider,
        source,
        context=context,
        critique=critique,
        **pass_kwargs,
    )

    current_text = llm_port.transform(
        prompt=chat_prompt,
        temperature=stage_config.temperature,
        trace_id=f"{active_trace_id}_pass_1" if max_passes > 1 else active_trace_id,
        session_id=context.session_id.value,
        user_id=context.user_identity.value,
    )

    actual_passes = 1
    is_saturated = False

    if max_passes > 1:
        for pass_index in range(2, max_passes + 1):
            logger.info(
                "[StageRunner] Executing pass %d/%d for %s...",
                pass_index,
                max_passes,
                stage_config.stage_name,
            )
            subsequent_key = stage_config.transform_prompt_key
            chat_prompt = stage_config.build_transform_prompt(
                prompt_provider,
                source,
                context=context,
                prompt_key=subsequent_key,
                pass_num=pass_index,
                prev_pass_num=pass_index - 1,
                total_passes=max_passes,
                current_text=current_text,
            )
            new_text = llm_port.transform(
                prompt=chat_prompt,
                temperature=stage_config.temperature,
                trace_id=f"{active_trace_id}_pass_{pass_index}",
                session_id=context.session_id.value,
                user_id=context.user_identity.value,
            )
            actual_passes = pass_index

            if getattr(
                stage_config, "early_stopping_enabled", False
            ) and check_complementary_mechanical_saturation(current_text, new_text):
                logger.info(
                    "[StageRunner] Mechanical saturation reached at pass %d/%d. Halting early.",
                    pass_index,
                    max_passes,
                )
                is_saturated = True
                current_text = new_text
                break

            current_text = new_text

    candidate_metadata: dict[str, Any] = {
        "channel_id": context.channel.id.value if context.channel.id else "",
        "content_id": context.content.id.value,
        "channel_name": context.channel.name,
        "content_title": context.content.title,
        "attempt": attempt,
    }
    if max_passes > 1:
        candidate_metadata["passes_executed"] = actual_passes
        candidate_metadata["is_saturated"] = is_saturated

    return CandidateText(
        text=current_text,
        stage_name=stage_config.stage_name,
        metadata=candidate_metadata,
    )


def evaluate_stage_candidate[TSource, TOutput](
    runner: Any,
    stage_config: StageConfig[TSource, TOutput],
    source: TSource,
    candidate: CandidateText,
    *,
    context: PipelineExecutionContext,
    attempt: int,
) -> JudgeEvaluation | None:
    """Evaluate candidate text against stage quality criteria if judge and eval_spec are configured."""
    if runner.llm_judge is None or stage_config.eval_spec is None:
        return None

    active_trace_id = runner._get_active_trace_id(context=context)

    with runner.telemetry_port.start_stage_evaluation_span(
        stage_name=stage_config.stage_name,
        attempt=attempt,
        attributes={
            "judge.stage_name": stage_config.stage_name,
            "judge.attempt": attempt,
        },
    ):
        from cresmo.application.pipeline import stage_runner as _sr

        current_span = _sr.trace.get_current_span()
        active_observation_id: str | None = None
        if current_span and current_span.is_recording():
            span_ctx = current_span.get_span_context()
            if span_ctx.is_valid:
                active_observation_id = f"{span_ctx.span_id:016x}"

        eval_context = EvaluationContext(
            stage_name=stage_config.stage_name,
            raw_text=stage_config.eval_spec.extract_source_text(source),
            candidate_text=stage_config.eval_spec.candidate_extractor(candidate),
            metadata={
                "channel_id": context.channel.id.value if context.channel.id else "",
                "content_id": context.content.id.value,
                "channel_name": context.channel.name,
                "content_title": context.content.title,
                "attempt": attempt,
                **stage_config.eval_spec.metadata,
            },
            trace_id=active_trace_id,
            required_criteria=stage_config.eval_spec.required_criteria,
            observation_id=active_observation_id,
        )

        llm_judge: LlmJudgePort = runner.llm_judge
        evaluation = llm_judge.evaluate(eval_context)
        runner._record_evaluation_metrics(stage_config.stage_name, evaluation.passed, attempt)
        attach_evaluation_span_attributes(current_span, evaluation)
        return evaluation


def execute_evaluated_stage_loop[StageRet](
    runner: Any,
    stage_name: str,
    fn: Callable[[], StageRet],
    *,
    channel_name: ChannelName | str,
    content_id: ContentId | str,
    eval_spec: StageEvaluationSpec | None = None,
    channel_id: ChannelId | str | None = None,
    content_title: str = "",
    fatal: bool = True,
    fallback: StageRet | Callable[[], StageRet] | None = None,
) -> StageRet | None:
    """Execute a pipeline stage within a closed-loop quality evaluation gate with retries (Legacy ADR-030)."""
    if runner.llm_judge is None or eval_spec is None:
        return runner.run_stage(  # type: ignore[no-any-return]
            stage_name,
            fn,
            channel_name=channel_name,
            content_id=content_id,
            channel_id=channel_id,
            content_title=content_title,
            fatal=fatal,
            fallback=fallback,
        )

    effective_max_attempts = max(eval_spec.max_attempts, runner.judge_max_attempts)
    candidate: StageRet | None = None
    evaluation: JudgeEvaluation | None = None

    for attempt in range(1, effective_max_attempts + 1):
        candidate = runner.run_stage(
            stage_name,
            fn,
            channel_name=channel_name,
            content_id=content_id,
            channel_id=channel_id,
            content_title=content_title,
            fatal=fatal,
            fallback=fallback,
        )
        if candidate is None:
            return fallback() if callable(fallback) else fallback

        active_trace_id = runner._get_active_trace_id(
            channel=channel_id or channel_name,
            content_id=content_id,
            channel_id=channel_id,
            channel_name=channel_name,
        )
        eval_context = EvaluationContext(
            stage_name=stage_name,
            raw_text=eval_spec.raw_text,
            candidate_text=eval_spec.candidate_extractor(candidate),
            metadata={
                "channel_id": as_str(channel_id),
                "content_id": as_str(content_id),
                "channel_name": as_str(channel_name),
                "content_title": content_title or str(getattr(candidate, "title", "")),
                "attempt": attempt,
                **eval_spec.metadata,
            },
            trace_id=active_trace_id,
            required_criteria=eval_spec.required_criteria,
        )
        llm_judge: LlmJudgePort = runner.llm_judge
        evaluation = llm_judge.evaluate(eval_context)
        runner._record_evaluation_metrics(stage_name, evaluation.passed, attempt)

        if evaluation.passed:
            return candidate

        logger.warning(
            "LLM judge reported low score for '%s' on attempt %d/%d (overall=%.2f, passed=%s).",
            stage_name,
            attempt,
            effective_max_attempts,
            evaluation.overall_score,
            evaluation.passed,
        )
        if attempt < effective_max_attempts:
            runner.metrics_port.increment_counter(
                "cresmo_judge_retries_total", 1.0, labels={"stage": stage_name}
            )

    if runner.judge_blocking:
        raise DomainValidationError(
            f"{stage_name} quality evaluation failed threshold after {effective_max_attempts} attempts: "
            f"{(evaluation.overall_score if evaluation is not None else 0.0):.2f}"
        )

    logger.warning(
        "Quality evaluation for '%s' exhausted all %d attempts without passing. Returning candidate as judge_blocking is False.",
        stage_name,
        effective_max_attempts,
    )
    return candidate
