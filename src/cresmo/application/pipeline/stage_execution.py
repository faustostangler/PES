"""Stage candidate generation, multi-pass saturation, and closed-loop evaluation execution.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC)
- ADR-028: Multi-pass early stopping and mechanical saturation
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions
"""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any

import structlog
from opentelemetry import trace

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import (
    StageConfig,
    extract_stage_source_text,
)
from cresmo.application.pipeline.stage_telemetry import attach_evaluation_span_attributes
from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
    TelemetryPort,
    active_telemetry_pass,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    CandidateText,
    EvaluationContext,
    JudgeEvaluation,
    SaturationReason,
    SaturationVerdict,
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
    telemetry_port: TelemetryPort | None = None,
) -> CandidateText:
    """Build prompt and invoke LLM transformation port to generate CandidateText (multi-pass aware)."""
    raw_max_passes = getattr(stage_config, "max_passes", 1)
    max_passes = raw_max_passes if isinstance(raw_max_passes, int) and raw_max_passes > 0 else 1
    is_multi_pass = max_passes > 1

    source_text = extract_stage_source_text(source)
    draft_text: str | None = None
    baseline_text: str = source_text
    current_text = ""
    passes_executed = 0
    is_saturated = False
    pending_final_critique = False
    saturation_history: list[dict[str, Any]] = []

    for pass_index in range(1, max_passes + 1):
        if stage_config.stage_name == StageName.GAP_FILLER:  # stage specific debug, keep it
            pass
        is_final_pass = pass_index == max_passes or pending_final_critique
        pass_prompt_context: dict[str, Any] = (
            {"pass_num": pass_index, "total_passes": max_passes} if is_multi_pass else {}
        )
        if draft_text is not None:
            pass_prompt_context["prev_pass_num"] = pass_index - 1
            pass_prompt_context["current_text"] = draft_text
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
                temperature=stage_config.temperature,
                trace_id=(
                    f"{active_trace_id}_pass_{pass_index}" if is_multi_pass else active_trace_id
                ),
                session_id=context.content.session_id,
                user_id=context.user_identity.value,
            )
        passes_executed = pass_index

        if pending_final_critique:
            is_saturated = True
            break

        raw_verdict: Any = stage_config.saturation_policy(
            baseline_text,
            current_text,
            pass_index,
        )
        if isinstance(raw_verdict, SaturationVerdict):
            verdict = raw_verdict
            if verdict.preserve_baseline:
                current_text = baseline_text

            if telemetry_port is not None and verdict.reason is not SaturationReason.DISABLED:
                span_attrs: dict[str, Any] = {
                    "cresmo.saturation.is_saturated": verdict.is_saturated,
                    "cresmo.saturation.reason": verdict.reason.value,
                    "cresmo.saturation.lexical_jaccard": verdict.lexical_jaccard,
                    "cresmo.saturation.word_delta_ratio": verdict.word_delta_ratio,
                    "cresmo.saturation.max_novelty": verdict.max_novelty,
                    "cresmo.saturation.novel_paragraphs": verdict.novel_paragraphs,
                    "cresmo.saturation.total_paragraphs": verdict.total_paragraphs,
                    "cresmo.saturation.preserve_baseline": verdict.preserve_baseline,
                    "cresmo.saturation.provider": verdict.provider,
                }
                with telemetry_port.start_stage_saturation_span(
                    stage_config.stage_name,
                    pass_num=pass_index,
                    attributes=span_attrs,
                ):
                    pass

            history_entry = verdict.to_metadata_dict()
            history_entry["pass_num"] = pass_index
            saturation_history.append(history_entry)

            if verdict.is_saturated:
                if critique and pass_index < max_passes:
                    logger.info(
                        "[StageRunner] Mechanical saturation reached at pass %d/%d; scheduling final critique pass.",
                        pass_index,
                        max_passes,
                    )
                    pending_final_critique = True
                else:
                    logger.info(
                        "[StageRunner] Mechanical saturation reached at pass %d/%d. Halting early.",
                        pass_index,
                        max_passes,
                    )
                    is_saturated = True
                    break

        baseline_text = current_text
        draft_text = current_text

    candidate_metadata: dict[str, Any] = {
        "channel_id": context.channel.id.value if context.channel.id else "",
        "content_id": context.content.id.value,
        "channel_name": context.channel.name,
        "content_title": context.content.title,
        "attempt": attempt,
    }
    if is_multi_pass:
        candidate_metadata["passes_executed"] = passes_executed
        candidate_metadata["is_saturated"] = is_saturated
        candidate_metadata["saturation_history"] = saturation_history

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
        current_span = trace.get_current_span()
        active_observation_id: str | None = None
        if current_span and current_span.is_recording():
            span_context = current_span.get_span_context()
            if span_context.is_valid:
                active_observation_id = f"{span_context.span_id:016x}"

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
