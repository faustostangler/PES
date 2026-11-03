"""Unit tests for LLMTranscriptDistiller.

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

import itertools
from unittest.mock import MagicMock

from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.application.use_cases.indexing.distiller import (
    LLMTranscriptDistiller,
    _retry_indices,
)
from cresmo.domain.entities import UserIdentity
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    EvaluationContext,
    JudgeEvaluation,
    PromptKey,
)


class DummyTransformationPort(LLMTransformationPort):
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def transform(
        self,
        prompt: str,
        temperature: float = 0.2,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "temperature": temperature,
                "trace_id": trace_id,
                "session_id": session_id,
                "user_id": user_id,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return ""


class DummyPromptProvider(PromptProviderPort):
    def __init__(self) -> None:
        self.requested_prompts: list[tuple[PromptKey, dict[str, object]]] = []

    def get_prompt(self, key: PromptKey, **kwargs: object) -> str:
        self.requested_prompts.append((key, kwargs))
        return f"PROMPT_{key.name}_{kwargs}"


class DummyJudgePort(LlmJudgePort):
    def __init__(self, verdicts: list[bool]) -> None:
        self.verdicts = list(verdicts)
        self.evaluated_contexts: list[EvaluationContext] = []

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        self.evaluated_contexts.append(context)
        passed = self.verdicts.pop(0) if self.verdicts else True
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = passed
        return mock_eval


class TestRetryIndices:
    def test_non_positive_max_rewrites_yields_infinite(self) -> None:
        gen0 = _retry_indices(0)
        assert isinstance(gen0, itertools.count)
        first_three = [next(gen0) for _ in range(3)]
        assert first_three == [0, 1, 2]

        gen_neg = _retry_indices(-1)
        assert isinstance(gen_neg, itertools.count)

    def test_positive_max_rewrites_yields_range(self) -> None:
        indices = list(_retry_indices(3))
        assert indices == [0, 1, 2, 3]


class TestLLMTranscriptDistillerExtractConcepts:
    def test_extract_concepts_success_on_first_attempt(self) -> None:
        llm = DummyTransformationPort(responses=["Domain-Driven Design, Hexagonal Architecture"])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[True])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=2,
            llm_judge_port=judge,
        )

        res = distiller.extract_concepts(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            text="Transcript full text here",
            channel_name=ChannelName("pes_channel"),
        )

        assert res == "Domain-Driven Design, Hexagonal Architecture"
        assert len(llm.calls) == 1
        assert llm.calls[0]["trace_id"] == "dQw4w9WgXcQ_concepts"
        assert len(judge.evaluated_contexts) == 1

    def test_extract_concepts_retry_on_judge_rejection(self) -> None:
        llm = DummyTransformationPort(
            responses=[
                "First Non Compliant Concepts",
                "Second Valid Concepts, Clean Architecture",
            ]
        )
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[False, True])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=2,
            llm_judge_port=judge,
        )

        res = distiller.extract_concepts(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            text="Transcript text",
            channel_name=ChannelName("pes_channel"),
            user=UserIdentity("usr_123"),
        )

        assert res == "Second Valid Concepts, Clean Architecture"
        assert len(llm.calls) == 2
        assert llm.calls[1]["trace_id"] == "dQw4w9WgXcQ_concepts_rewrite_1"
        assert llm.calls[1]["user_id"] == "usr_123"
        assert len(judge.evaluated_contexts) == 2

    def test_extract_concepts_transitional_prompt_provider_judge_fallback(self) -> None:
        # Without llm_judge_port, uses prompt_provider judge prompt
        llm = DummyTransformationPort(
            responses=[
                "Valid Concept Line",
                "true",  # Judge boolean verdict
            ]
        )
        prompts = DummyPromptProvider()

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=1,
            llm_judge_port=None,
        )

        res = distiller.extract_concepts(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Title",
            text="Text",
            channel_name=ChannelName("pes_channel"),
        )

        assert res == "Valid Concept Line"
        assert len(llm.calls) == 2
        # Second call is the judge prompt with temperature 0.0
        assert llm.calls[1]["temperature"] == 0.0

    def test_extract_concepts_exhausted_retries_returns_cleaned_or_fallback(self) -> None:
        llm = DummyTransformationPort(responses=["", "", ""])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[False, False, False])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=2,
            llm_judge_port=judge,
        )

        res = distiller.extract_concepts(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            text="Transcript text",
            channel_name=ChannelName("pes_channel"),
        )

        assert res == "Síntese Conceitual"


class TestLLMTranscriptDistillerExtractSummary:
    def test_extract_summary_success_first_attempt(self) -> None:
        llm = DummyTransformationPort(responses=["Structured conceptual summary text."])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[True])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=1,
            llm_judge_port=judge,
        )

        summary = distiller.extract_summary(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            text="Transcript full text",
            channel_name=ChannelName("pes_channel"),
        )

        assert summary == "Structured conceptual summary text."
        assert len(llm.calls) == 1
        assert llm.calls[0]["trace_id"] == "dQw4w9WgXcQ_summary"

    def test_extract_summary_retry_and_transitional_fallback(self) -> None:
        llm = DummyTransformationPort(
            responses=[
                "First summary attempt",
                "false",  # Judge rejected
                "Second summary attempt",
                "true",   # Judge passed
            ]
        )
        prompts = DummyPromptProvider()

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=2,
            llm_judge_port=None,
        )

        summary = distiller.extract_summary(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            text="Transcript text",
            channel_name=ChannelName("pes_channel"),
        )

        assert summary == "Second summary attempt"
        assert len(llm.calls) == 4

    def test_extract_summary_exhausted_retries_falls_back_to_title(self) -> None:
        llm = DummyTransformationPort(responses=["", ""])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[False, False])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=1,
            llm_judge_port=judge,
        )

        summary = distiller.extract_summary(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Fallback Title",
            text="Transcript text",
            channel_name=ChannelName("pes_channel"),
        )

        assert summary == "Fallback Title"


class TestLLMTranscriptDistillerExtractSynthesis:
    _VALID_PARAGRAPH = (
        "Minorias burocráticas governam as instituições políticas centrais. "
        "A decadência dos governantes precipita a substituição por novas contra-elites "
        "organizadas em estruturas institucionais complexas e altamente resilientes."
    )

    def test_extract_synthesis_success_first_attempt(self) -> None:
        llm = DummyTransformationPort(responses=[self._VALID_PARAGRAPH])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[True])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=1,
            llm_judge_port=judge,
        )

        synthesis = distiller.extract_synthesis(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            excerpt="Excerpt text",
            summary="Summary text",
            channel_name=ChannelName("pes_channel"),
        )

        assert synthesis == self._VALID_PARAGRAPH
        assert len(llm.calls) == 1
        assert llm.calls[0]["trace_id"] == "dQw4w9WgXcQ_synthesis"

    def test_extract_synthesis_rejects_invalid_paragraph_formatting(self) -> None:
        # First output is bullet list (invalid formatting, skips judge)
        bullet_list = "Intro line\n- Bullet 1\n- Bullet 2\n" + ("word " * 20)
        llm = DummyTransformationPort(responses=[bullet_list, self._VALID_PARAGRAPH])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[True])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=2,
            llm_judge_port=judge,
        )

        synthesis = distiller.extract_synthesis(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Clean Architecture",
            excerpt="Excerpt",
            summary="Summary",
            channel_name=ChannelName("pes_channel"),
        )

        assert synthesis == self._VALID_PARAGRAPH
        assert len(llm.calls) == 2
        # Judge should only have been called ONCE (on second valid paragraph)
        assert len(judge.evaluated_contexts) == 1

    def test_extract_synthesis_exhausted_retries_falls_back_to_summary_or_title(self) -> None:
        llm = DummyTransformationPort(responses=["", ""])
        prompts = DummyPromptProvider()
        judge = DummyJudgePort(verdicts=[False, False])

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=llm,
            prompt_provider=prompts,
            max_rewrites=1,
            llm_judge_port=judge,
        )

        synthesis = distiller.extract_synthesis(
            video_id=ContentId("dQw4w9WgXcQ"),
            title="Fallback Title",
            excerpt="Excerpt",
            summary="Existing Summary",
            channel_name=ChannelName("pes_channel"),
        )

        assert synthesis == "Existing Summary"
