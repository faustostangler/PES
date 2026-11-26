"""Stage candidate generation, multi-pass saturation, and closed-loop evaluation execution.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC)
- ADR-028: Multi-pass early stopping and mechanical saturation
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle (Zero OTel SDK in Application)
"""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any, Final

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_telemetry import (
    attach_evaluation_span_attributes,
    record_evaluation_metric,
    resolve_active_trace_id,
)
from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    MetricsPort,
    PromptProviderPort,
    TelemetryAttributeValue,
    TelemetryPort,
    active_telemetry_pass,
    format_stage_judge_span_name,
    format_stage_saturation_span_name,
)
from cresmo.domain.entities.transcripts import extract_source_text
from cresmo.domain.value_objects import (
    CandidateText,
    EvaluationContext,
    JudgeEvaluation,
    SaturationReason,
    SaturationVerdict,
)

logger = structlog.get_logger(__name__)

SPAN_ATTR_PASS_NUM: Final[str] = "cresmo.pass_num"
SPAN_ATTR_SATURATION_PREFIX: Final[str] = "cresmo.saturation."
SPAN_ATTR_JUDGE_STAGE_NAME: Final[str] = "judge.stage_name"
SPAN_ATTR_JUDGE_ATTEMPT: Final[str] = "judge.attempt"
PASS_TRACE_SUFFIX_PREFIX: Final[str] = "_pass_"

_CTX_KEY_PASS_NUM: Final[str] = "pass_num"
_CTX_KEY_TOTAL_PASSES: Final[str] = "total_passes"
_CTX_KEY_PREV_PASS_NUM: Final[str] = "prev_pass_num"
_CTX_KEY_CURRENT_TEXT: Final[str] = "current_text"

_META_KEY_CHANNEL_ID: Final[str] = "channel_id"
_META_KEY_CONTENT_ID: Final[str] = "content_id"
_META_KEY_CHANNEL_NAME: Final[str] = "channel_name"
_META_KEY_CONTENT_TITLE: Final[str] = "content_title"
_META_KEY_ATTEMPT: Final[str] = "attempt"
_META_KEY_PASSES_EXECUTED: Final[str] = "passes_executed"
_META_KEY_IS_SATURATED: Final[str] = "is_saturated"
_META_KEY_SATURATION_HISTORY: Final[str] = "saturation_history"


def _build_pass_prompt_context(
    *,
    pass_index: int,
    max_passes: int,
    is_multi_pass: bool,
    draft_text: str | None,
) -> dict[str, Any]:
    """Assemble prompt template variables for the active refinement pass."""
    prompt_context: dict[str, Any] = (
        {_CTX_KEY_PASS_NUM: pass_index, _CTX_KEY_TOTAL_PASSES: max_passes}
        if is_multi_pass
        else {}
    )
    if draft_text is not None:
        prompt_context[_CTX_KEY_PREV_PASS_NUM] = pass_index - 1
        prompt_context[_CTX_KEY_CURRENT_TEXT] = draft_text
    return prompt_context


def _record_saturation_verdict(
    verdict: SaturationVerdict,
    *,
    stage_name: str,
    pass_index: int,
    telemetry_port: TelemetryPort | None,
    saturation_history: list[dict[str, Any]],
) -> None:
    """Emit scalar saturation telemetry span and append structured pass verdict history."""
    metadata_entry = verdict.to_metadata_dict()
    if telemetry_port is not None and verdict.reason is not SaturationReason.DISABLED:
        span_attrs: dict[str, TelemetryAttributeValue] = {SPAN_ATTR_PASS_NUM: pass_index}
        for key, val in metadata_entry.items():
            if isinstance(val, (bool, int, float, str)):
                span_attrs[f"{SPAN_ATTR_SATURATION_PREFIX}{key}"] = val
        with telemetry_port.start_span(
            format_stage_saturation_span_name(stage_name, pass_num=pass_index),
            attributes=span_attrs,
        ):
            pass

    metadata_entry[_CTX_KEY_PASS_NUM] = pass_index
    saturation_history.append(metadata_entry)


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
    telemetry_port: TelemetryPort | None = None,
) -> CandidateText:
    """Build prompt and invoke LLM transformation port to generate CandidateText (multi-pass aware)."""
    max_passes = stage_config.max_passes
    is_multi_pass = max_passes > 1

    baseline_text = extract_source_text(source)  # type: ignore[arg-type]
    draft_text: str | None = None
    current_text = ""
    passes_executed = 0
    is_saturated = False
    pending_final_critique = False
    saturation_history: list[dict[str, Any]] = []

    for pass_index in range(1, max_passes + 1):
        is_final_pass = pass_index == max_passes or pending_final_critique

        pass_prompt_context = _build_pass_prompt_context(
            pass_index=pass_index,
            max_passes=max_passes,
            is_multi_pass=is_multi_pass,
            draft_text=draft_text,
        )
        if is_multi_pass:
            logger.info(
                "[StageRunner] Executing pass %d/%d for %s...",
                pass_index,
                max_passes,
                stage_config.stage_name,
            )

        chat_prompt = stage_config.build_transform_prompt(
            prompt_provider,
            source,
            context=context,
            critique=critique if is_final_pass else None,
            **pass_prompt_context,
        )
        telemetry_pass_context: AbstractContextManager[None] = (
            active_telemetry_pass(pass_index) if is_multi_pass else nullcontext()
        )
        with telemetry_pass_context:
            current_text = llm_port.transform(
                prompt=chat_prompt,
                trace_id=(
                    f"{active_trace_id}{PASS_TRACE_SUFFIX_PREFIX}{pass_index}"
                    if is_multi_pass
                    else active_trace_id
                ),
                session_id=context.content.session_id,
                user_id=context.user_identity.value,
            )
        passes_executed = pass_index

        if pending_final_critique:
            is_saturated = True
            break

        if not is_multi_pass:
            break

        verdict = stage_config.saturation_policy(
            baseline_text,
            current_text,
            pass_index,
        )
        if not isinstance(verdict, SaturationVerdict):
            raise TypeError(
                f"StageConfig.saturation_policy must return SaturationVerdict, "
                f"got {type(verdict).__name__}."
            )

        if verdict.preserve_baseline:
            current_text = baseline_text

        _record_saturation_verdict(
            verdict,
            stage_name=stage_config.stage_name,
            pass_index=pass_index,
            telemetry_port=telemetry_port,
            saturation_history=saturation_history,
        )

        if verdict.is_saturated:
            if critique and pass_index < max_passes:
                logger.info(
                    "[StageRunner] Saturation reached at pass %d/%d; scheduling final critique pass.",
                    pass_index,
                    max_passes,
                )
                pending_final_critique = True
            else:
                logger.info(
                    "[StageRunner] Saturation reached at pass %d/%d (%s). Halting early.",
                    pass_index,
                    max_passes,
                    verdict.reason.value,
                )
                is_saturated = True
                break

        baseline_text = current_text
        draft_text = current_text

    candidate_metadata: dict[str, Any] = {
        _META_KEY_CHANNEL_ID: context.channel.id.value if context.channel.id else "",
        _META_KEY_CONTENT_ID: context.content.id.value,
        _META_KEY_CHANNEL_NAME: context.channel.name,
        _META_KEY_CONTENT_TITLE: context.content.title,
        _META_KEY_ATTEMPT: attempt,
    }
    if is_multi_pass:
        candidate_metadata[_META_KEY_PASSES_EXECUTED] = passes_executed
        candidate_metadata[_META_KEY_IS_SATURATED] = is_saturated
        candidate_metadata[_META_KEY_SATURATION_HISTORY] = saturation_history

    return CandidateText(
        text=current_text,
        stage_name=stage_config.stage_name,
        metadata=candidate_metadata,
    )


def evaluate_stage_candidate[TSource, TOutput](
    stage_config: StageConfig[TSource, TOutput],
    source: TSource,
    candidate: CandidateText,
    *,
    context: PipelineExecutionContext,
    attempt: int,
    llm_judge: LlmJudgePort | None,
    telemetry_port: TelemetryPort,
    metrics_port: MetricsPort,
) -> JudgeEvaluation | None:
    """Evaluate candidate text against stage quality criteria if judge and eval_spec are configured."""
    if llm_judge is None or stage_config.eval_spec is None:
        return None

    with telemetry_port.start_span(
        format_stage_judge_span_name(stage_config.stage_name),
        attributes={
            SPAN_ATTR_JUDGE_STAGE_NAME: stage_config.stage_name,
            SPAN_ATTR_JUDGE_ATTEMPT: attempt,
        },
    ) as eval_span:
        active_trace_id = resolve_active_trace_id(
            context,
            telemetry_port=telemetry_port,
            span=eval_span,
        )
        active_observation_id = eval_span.span_id

        eval_context = EvaluationContext(
            stage_name=stage_config.stage_name,
            raw_text=extract_source_text(source),  # type: ignore[arg-type]
            candidate_text=stage_config.eval_spec.candidate_extractor(candidate),
            metadata={
                _META_KEY_CHANNEL_ID: context.channel.id.value if context.channel.id else "",
                _META_KEY_CONTENT_ID: context.content.id.value,
                _META_KEY_CHANNEL_NAME: context.channel.name,
                _META_KEY_CONTENT_TITLE: context.content.title,
                _META_KEY_ATTEMPT: attempt,
                **stage_config.eval_spec.metadata,
            },
            trace_id=active_trace_id,
            required_criteria=stage_config.eval_spec.required_criteria,
            observation_id=active_observation_id,
            judge_prompt_key=stage_config.judge_prompt_key,
        )

        evaluation = llm_judge.evaluate(eval_context)
        record_evaluation_metric(
            metrics_port,
            stage_name=stage_config.stage_name,
            passed=evaluation.passed,
            attempt=attempt,
        )
        attach_evaluation_span_attributes(eval_span, evaluation)
        return evaluation
