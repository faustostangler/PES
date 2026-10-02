"""Hermetic Unit Tests for StageDescriptor and Closed-Loop Reflection in PipelineStageRunner.

Conforms to:
    - ADR-031: Standardized StageDescriptor, SourceTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric
    - SPEC-014: Standardized Stage Execution and Decision-Model Quality Fabric Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageDescriptor
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
)
from cresmo.domain.entities import PipelineSessionId, SourceTranscript, UserIdentity
from cresmo.domain.value_objects import (
    CandidateText,
    ChannelName,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    PromptKey,
    StageEvaluationSpec,
)


class TestStageDescriptorRunner:
    """Test suite for StageDescriptor execution with closed-loop reflection."""

    def test_execute_stage_success_first_attempt(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=1.0,
                    passed=True,
                ),
            ),
            provider="test_judge",
        )

        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_llm.transform.return_value = "Cleaned fluid prose text without oralities."

        prompt_provider = NoOpPromptProviderPort()
        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        source = SourceTranscript(
            content_id=ContentId("content_test"),
            channel_name=ChannelName("Channel Alpha"),
            body="Um, so basically, this is raw spoken text.",
        )

        descriptor = StageDescriptor[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text=source.body,
                candidate_extractor=lambda c: c.text if isinstance(c, CandidateText) else str(c),
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=3,
            ),
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel_name, source.content_id),
            user_identity=UserIdentity.worker(),
            channel_name=source.channel_name,
            content_id=source.content_id,
        )

        result = runner.execute_stage(
            descriptor,
            source,
            context=ctx,
            prompt_provider=prompt_provider,
            llm_transformation_port=mock_llm,
        )

        assert isinstance(result, CandidateText)
        assert result.text == "Cleaned fluid prose text without oralities."
        assert mock_llm.transform.call_count == 1
        assert mock_judge.evaluate.call_count == 1

    def test_execute_stage_closed_loop_reflection_retry(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = MagicMock(spec=NoOpMetricsPort())
        mock_judge = MagicMock()

        # Attempt 1 fails with critique; Attempt 2 passes
        failure_evaluation = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.4,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.4,
                    passed=False,
                    reasoning="Found verbal filler 'tipo assim'.",
                    improvement_suggestion="Purge all instances of 'tipo assim'.",
                ),
            ),
            provider="test_judge",
        )
        success_evaluation = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.98,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=1.0,
                    passed=True,
                ),
            ),
            provider="test_judge",
        )
        mock_judge.evaluate.side_effect = [failure_evaluation, success_evaluation]

        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_llm.transform.side_effect = [
            "Attempt 1 with remaining verbal crutches.",
            "Attempt 2 fully cleansed of oralities.",
        ]

        prompt_provider = NoOpPromptProviderPort()
        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        source = SourceTranscript(
            content_id=ContentId("content_retry"),
            channel_name=ChannelName("Channel Beta"),
            body="Text with oralities.",
        )

        descriptor = StageDescriptor[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text=source.body,
                candidate_extractor=lambda c: c.text if isinstance(c, CandidateText) else str(c),
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=3,
            ),
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel_name, source.content_id),
            user_identity=UserIdentity.worker(),
            channel_name=source.channel_name,
            content_id=source.content_id,
        )

        result = runner.execute_stage(
            descriptor,
            source,
            context=ctx,
            prompt_provider=prompt_provider,
            llm_transformation_port=mock_llm,
        )

        assert result.text == "Attempt 2 fully cleansed of oralities."
        assert mock_llm.transform.call_count == 2
        assert mock_judge.evaluate.call_count == 2

        # Verify critique was injected into prompt on attempt 2
        second_call_prompt = mock_llm.transform.call_args_list[1].kwargs.get("prompt")
        assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" in second_call_prompt
        assert "tipo assim" in second_call_prompt

    def test_execute_stage_with_post_processor(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()

        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_llm.transform.return_value = "# Header Title\nClean continuous fluid prose."

        prompt_provider = NoOpPromptProviderPort()
        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=None,
        )

        source = SourceTranscript(
            content_id=ContentId("content_post"),
            channel_name=ChannelName("Channel Gamma"),
            body="Raw spoken text.",
        )

        def sample_post_processor(candidate: CandidateText, src: SourceTranscript) -> str:
            # Strip header
            return candidate.text.replace("# Header Title\n", "").strip()

        descriptor = StageDescriptor[SourceTranscript, str](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            post_processor=sample_post_processor,
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel_name, source.content_id),
            user_identity=UserIdentity.worker(),
            channel_name=source.channel_name,
            content_id=source.content_id,
        )

        result = runner.execute_stage(
            descriptor,
            source,
            context=ctx,
            prompt_provider=prompt_provider,
            llm_transformation_port=mock_llm,
        )

        assert result == "Clean continuous fluid prose."
