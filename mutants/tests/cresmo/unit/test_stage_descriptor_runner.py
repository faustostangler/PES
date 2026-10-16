"""Hermetic Unit Tests for StageConfig and Closed-Loop Reflection in PipelineStageRunner.

Conforms to:
    - ADR-031: Standardized StageConfig, SourceTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric
    - SPEC-014: Standardized Stage Execution and Decision-Model Quality Fabric Specification
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PromptProviderPort,
)
from cresmo.domain.entities import PipelineSessionId, SourceTranscript, UserIdentity
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    ChatMessage,
    ChatPrompt,
    Content,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    MessageRole,
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
                raw_text=source.content.body,
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
                raw_text=source.content.body,
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
        assert isinstance(second_call_prompt, ChatPrompt)
        assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" in second_call_prompt.get_last_user_content()
        assert "tipo assim" in second_call_prompt.get_last_user_content()

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
        mock_prompt_provider.get_prompt.return_value = ChatPrompt.from_system_and_user(
            system="sys_instruction", user="user_prompt"
        )

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
                raw_text=source.content.body,
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

    def test_generate_candidate_and_evaluate_candidate_isolated(self) -> None:
        """Verify _generate_candidate and _evaluate_candidate can be invoked in isolation."""
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.98,
            criteria_scores=(),
            provider="test_judge",
        )

        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_llm.transform.return_value = "Isolated candidate text"

        prompt_provider = MagicMock()
        prompt_provider.get_prompt.return_value = ChatPrompt.from_system_and_user(
            system="sys instruction", user="user prompt"
        )

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        descriptor = StageConfig[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="ground truth",
                required_criteria=(),
            ),
        )

        source = SourceTranscript(
            body="Raw ground truth",
            channel_name=ChannelName("Channel A"),
            content_id=ContentId("content_isolated"),
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId.create(source.channel, source.content),
            user_identity=UserIdentity.worker(),
            channel=source.channel,
            content=source.content,
        )

        # 1. Test isolated candidate generation
        candidate = runner._generate_candidate(
            descriptor,
            source,
            context=ctx,
            prompt_provider=prompt_provider,
            llm_port=mock_llm,
            attempt=1,
            critique="Focus on parataxis",
        )
        assert candidate.text == "Isolated candidate text"
        assert candidate.stage_name == "fluid_prose"
        assert candidate.metadata["attempt"] == 1
        assert candidate.metadata["channel_name"] == "Channel A"

        # 2. Test isolated candidate evaluation
        eval_result = runner._evaluate_candidate(
            descriptor,
            source,
            candidate,
            context=ctx,
            attempt=1,
        )
        assert eval_result is not None
        assert eval_result.passed is True
        assert eval_result.overall_score == 0.98
        mock_judge.evaluate.assert_called_once()


class TestStageConfigPromptBuilding:
    """Hermetic unit tests for StageConfig defaults, prompt building, and post-processing."""

    def test_stage_config_defaults_and_identity_post_processing(self) -> None:
        cfg = StageConfig[str, CandidateText](
            stage_name="default_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        assert cfg.stage_name == "default_stage"
        assert cfg.transform_prompt_key == PromptKey.FLUID_PROSE
        assert cfg.judge_prompt_key is None
        assert cfg.eval_spec is None
        assert cfg.post_processor is None
        assert cfg.temperature is None
        assert cfg.max_attempts == 1
        assert cfg.blocking is False

        cand = CandidateText(stage_name="default_stage", text="unprocessed text")
        assert cfg.post_process(cand, "dummy_source") is cand

    def test_build_transform_prompt_with_context(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        base_prompt = ChatPrompt(
            messages=(ChatMessage(role=MessageRole.USER, content="User instruction"),),
            system_instruction="System instruction",
        )
        mock_provider.get_prompt.return_value = base_prompt

        cfg = StageConfig[str, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="MyChan", id=ChannelId("UC_chan")),
            content=Content(id=ContentId("vid_c123"), title="MyTitle"),
        )
        result = cfg.build_transform_prompt(
            mock_provider,
            source="raw_source_text",
            context=ctx,
        )
        mock_provider.get_prompt.assert_called_once_with(
            PromptKey.FLUID_PROSE,
            channel_name="MyChan",
            channel_id="UC_chan",
            content_id="vid_c123",
            content_title="MyTitle",
            file_name="vid_c123.txt",
            raw_text="raw_source_text",
        )
        assert result is base_prompt

    def test_build_transform_prompt_with_channel_without_id(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        mock_provider.get_prompt.return_value = ChatPrompt(
            messages=(ChatMessage(role=MessageRole.USER, content="Text"),),
        )

        cfg = StageConfig[str, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:2"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NamedChannel", id=None),
            content=Content(id=ContentId("vid_c123"), title="MyTitle"),
        )
        cfg.build_transform_prompt(
            mock_provider,
            source="raw",
            context=ctx,
        )
        called_kwargs = mock_provider.get_prompt.call_args[1]
        assert called_kwargs["channel_name"] == "NamedChannel"
        assert called_kwargs["channel_id"] == ""

    def test_build_transform_prompt_with_extra_context(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        mock_provider.get_prompt.return_value = ChatPrompt(
            messages=(ChatMessage(role=MessageRole.USER, content="Instruction"),),
        )

        cfg = StageConfig[str, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:3"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="CustomChan", id=ChannelId("UC_chan")),
            content=Content(id=ContentId("vid_c456"), title="CustomTitle"),
        )
        cfg.build_transform_prompt(
            mock_provider,
            source="custom_text",
            context=ctx,
            extra_param="extra_val",
        )
        mock_provider.get_prompt.assert_called_once_with(
            PromptKey.FLUID_PROSE,
            channel_name="CustomChan",
            channel_id="UC_chan",
            content_id="vid_c456",
            content_title="CustomTitle",
            file_name="vid_c456.txt",
            raw_text="custom_text",
            extra_param="extra_val",
        )

    def test_build_transform_prompt_source_extraction_variants(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        mock_provider.get_prompt.return_value = ChatPrompt(
            messages=(ChatMessage(role=MessageRole.USER, content="Text"),),
        )

        cfg = StageConfig[object, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:4"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Chan"),
            content=Content(id=ContentId("vid_1001")),
        )

        # 1. Source with content.body
        class SourceContentBody:
            content = Content(id="vid_1001", body="extracted from content.body")

        cfg.build_transform_prompt(mock_provider, source=SourceContentBody(), context=ctx)
        assert mock_provider.get_prompt.call_args[1]["raw_text"] == "extracted from content.body"

        # 2. Source with body attribute
        class SourceBody:
            body = "extracted from body"

        cfg.build_transform_prompt(mock_provider, source=SourceBody(), context=ctx)
        assert mock_provider.get_prompt.call_args[1]["raw_text"] == "extracted from body"

        # 3. Source with text attribute
        class SourceText:
            text = "extracted from text"

        cfg.build_transform_prompt(mock_provider, source=SourceText(), context=ctx)
        assert mock_provider.get_prompt.call_args[1]["raw_text"] == "extracted from text"

        # 4. Fallback to str(source)
        class CustomObj:
            def __str__(self) -> str:
                return "custom_str_repr"

        cfg.build_transform_prompt(mock_provider, source=CustomObj(), context=ctx)
        assert mock_provider.get_prompt.call_args[1]["raw_text"] == "custom_str_repr"

    def test_build_transform_prompt_with_critique_multi_turn(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        base_prompt = ChatPrompt(
            messages=(
                ChatMessage(role=MessageRole.USER, content="Example user question"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Example assistant response"),
                ChatMessage(role=MessageRole.USER, content="Actual task instruction"),
            ),
            system_instruction="System prompt directive",
        )
        mock_provider.get_prompt.return_value = base_prompt

        cfg = StageConfig[str, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:5"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Chan"),
            content=Content(id=ContentId("vid_1001")),
        )
        result = cfg.build_transform_prompt(
            mock_provider,
            source="raw",
            context=ctx,
            critique="Colloquialism detected: 'tipo assim'.",
        )

        assert len(result.messages) == 3
        # First message (USER) must NOT have critique appended
        assert result.messages[0].role == MessageRole.USER
        assert result.messages[0].content == "Example user question"
        # Second message (ASSISTANT) must NOT be mutated
        assert result.messages[1].role == MessageRole.ASSISTANT
        assert result.messages[1].content == "Example assistant response"
        # Only the final USER message must have the critique appended
        assert result.messages[2].role == MessageRole.USER
        assert result.messages[2].content == (
            "Actual task instruction\n\n[PREVIOUS ATTEMPT QUALITY FEEDBACK]\n"
            "The previous generation failed quality evaluation:\n"
            "Colloquialism detected: 'tipo assim'.\n"
            "Please correct these defects in your output."
        )
        assert result.system_instruction == "System prompt directive"

    def test_build_transform_prompt_with_critique_empty_messages_system_only(self) -> None:
        mock_provider = MagicMock(spec=PromptProviderPort)
        base_prompt = ChatPrompt(
            messages=(),
            system_instruction="System only directive",
        )
        mock_provider.get_prompt.return_value = base_prompt

        cfg = StageConfig[str, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:6"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Chan"),
            content=Content(id=ContentId("vid_1001")),
        )
        result = cfg.build_transform_prompt(
            mock_provider,
            source="raw",
            context=ctx,
            critique="Missing citations.",
        )

        assert len(result.messages) == 1
        assert result.messages[0].role == MessageRole.USER
        expected_content = (
            "[PREVIOUS ATTEMPT QUALITY FEEDBACK]\n"
            "The previous generation failed quality evaluation:\n"
            "Missing citations.\n"
            "Please correct these defects in your output."
        )
        assert result.messages[0].content == expected_content
        assert result.system_instruction == "System only directive"

    def test_post_process_invokes_callable_with_exact_candidate_and_source(self) -> None:
        received_args: list[tuple[Any, Any]] = []

        def custom_processor(cand: CandidateText, src: SourceTranscript) -> str:
            received_args.append((cand, src))
            return f"Processed: {src.channel.name} -> {cand.text}"

        cfg = StageConfig[SourceTranscript, str](
            stage_name="test_stage",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            post_processor=custom_processor,
        )
        src = SourceTranscript(
            content_id=ContentId("cid1"),
            channel_name=ChannelName("ChanA"),
            body="source_body",
        )
        cand = CandidateText(stage_name="test_stage", text="candidate_body")
        out = cfg.post_process(cand, src)

        assert out == "Processed: ChanA -> candidate_body"
        assert len(received_args) == 1
        assert received_args[0][0] is cand
        assert received_args[0][1] is src
