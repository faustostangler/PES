"""Hermetic Unit Tests for StageConfig and Closed-Loop Reflection in PipelineStageRunner.

Conforms to:
    - ADR-031: Standardized StageConfig, SourceTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric
    - SPEC-014: Standardized Stage Execution and Decision-Model Quality Fabric Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
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
    ChannelId,
    ChannelName,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    PromptKey,
    StageEvaluationSpec,
)


class TestStageConfigRunner:
    """Test suite for StageConfig execution with closed-loop reflection."""

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

        descriptor = StageConfig[SourceTranscript, CandidateText](
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
            session_id=PipelineSessionId.create(source.channel, source.content),
            user_identity=UserIdentity.worker(),
            channel=source.channel,
            content=source.content,
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

        descriptor = StageConfig[SourceTranscript, CandidateText](
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
            session_id=PipelineSessionId.create(source.channel, source.content),
            user_identity=UserIdentity.worker(),
            channel=source.channel,
            content=source.content,
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

        descriptor = StageConfig[SourceTranscript, str](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            post_processor=sample_post_processor,
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel, source.content),
            user_identity=UserIdentity.worker(),
            channel=source.channel,
            content=source.content,
        )

        result = runner.execute_stage(
            descriptor,
            source,
            context=ctx,
            prompt_provider=prompt_provider,
            llm_transformation_port=mock_llm,
        )

        assert result == "Clean continuous fluid prose."

    def test_execute_stage_symmetric_identity_metadata_parity(self) -> None:
        """Verify strict parity: analytical IDs (channel_id, content_id) and semantic text (channel_name, content_title)."""
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=1.0,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=1.0,
                    passed=True,
                ),
            ),
            provider="test_judge",
        )

        captured_candidate: list[CandidateText] = []

        def capture_candidate(cand: CandidateText) -> str:
            captured_candidate.append(cand)
            return cand.text

        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_llm.transform.return_value = "Symmetric output text."

        mock_prompt_provider = MagicMock(spec=NoOpPromptProviderPort())
        mock_prompt_provider.get_prompt.return_value = ("sys_instruction", "user_prompt")

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        source = SourceTranscript(
            content_id=ContentId("content_999"),
            channel_name=ChannelName("Sandeco Channel"),
            channel_id=ChannelId("UC_SAND123"),
            title="SOTA DDD Architecture",
            body="Raw spoken body transcript.",
        )

        descriptor = StageConfig[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text=source.body,
                candidate_extractor=capture_candidate,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=1,
            ),
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel, source.content),
            user_identity=UserIdentity.worker(),
            channel=source.channel,
            content=source.content,
        )

        result = runner.execute_stage(
            descriptor,
            source,
            context=ctx,
            prompt_provider=mock_prompt_provider,
            llm_transformation_port=mock_llm,
        )

        assert isinstance(result, CandidateText)

        # 1. Verify build_transform_prompt received symmetric 2x2 pairs
        mock_prompt_provider.get_prompt.assert_called_once()
        prompt_call_kwargs = mock_prompt_provider.get_prompt.call_args[1]
        assert prompt_call_kwargs["channel_id"] == "UC_SAND123"
        assert prompt_call_kwargs["content_id"] == "content_999"
        assert prompt_call_kwargs["channel_name"] == "Sandeco Channel"
        assert prompt_call_kwargs["content_title"] == "SOTA DDD Architecture"

        # 2. Verify CandidateText.metadata parity
        assert len(captured_candidate) == 1
        cand_meta = captured_candidate[0].metadata
        assert cand_meta["channel_id"] == "UC_SAND123"
        assert cand_meta["content_id"] == "content_999"
        assert cand_meta["channel_name"] == "Sandeco Channel"
        assert cand_meta["content_title"] == "SOTA DDD Architecture"
        assert cand_meta["attempt"] == 1

        # 3. Verify EvaluationContext.metadata parity
        mock_judge.evaluate.assert_called_once()
        eval_ctx = mock_judge.evaluate.call_args[0][0]
        eval_meta = eval_ctx.metadata
        assert eval_meta["channel_id"] == "UC_SAND123"
        assert eval_meta["content_id"] == "content_999"
        assert eval_meta["channel_name"] == "Sandeco Channel"
        assert eval_meta["content_title"] == "SOTA DDD Architecture"
        assert eval_meta["attempt"] == 1

    def test_trace_id_fallback_prioritizes_analytical_channel_id(self) -> None:
        """Verify fallback trace ID prefers analytical channel_id over human channel_name."""
        trace_id = PipelineStageRunner._get_active_trace_id(
            channel_id="UC_CHAN_123",
            content_id="content_abc",
            channel_name="Human Channel Name",
        )
        assert trace_id == "cresmo_UC_CHAN_123_content_abc"

