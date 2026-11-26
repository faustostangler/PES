"""LLM transcript distillation and multi-pass judge loops.

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
"""

from __future__ import annotations

import itertools
from typing import Final

import structlog

from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.application.use_cases.indexing.validators import (
    FALLBACK_KEY_CONCEPT_TITLE,
    clean_concept_line,
    clean_text_line,
    is_valid_concepts_output,
    is_valid_synthesis_paragraph,
)
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import (
    DEFAULT_LANGUAGE,
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    JudgeCriterion,
    PromptKey,
)

logger = structlog.get_logger(__name__)

DEFAULT_DISTILLER_TEMPERATURE: Final[float] = 0.2
DEFAULT_DISTILLER_MAX_REWRITES: Final[int] = 3

TRACE_SUFFIX_CONCEPTS: Final[str] = "_concepts"
TRACE_SUFFIX_CONCEPTS_JUDGE: Final[str] = "_concepts_judge"
TRACE_SUFFIX_CONCEPTS_REWRITE: Final[str] = "_concepts_rewrite_"
TRACE_SUFFIX_CONCEPTS_JUDGE_RETRY: Final[str] = "_concepts_judge_retry_"
TRACE_SUFFIX_SUMMARY: Final[str] = "_summary"
TRACE_SUFFIX_SUMMARY_RETRY: Final[str] = "_summary_retry_"
TRACE_SUFFIX_SUMMARY_JUDGE: Final[str] = "_summary_judge"
TRACE_SUFFIX_SUMMARY_JUDGE_RETRY: Final[str] = "_summary_judge_retry_"
TRACE_SUFFIX_SYNTHESIS: Final[str] = "_synthesis"
TRACE_SUFFIX_SYNTHESIS_RETRY: Final[str] = "_synthesis_retry_"
TRACE_SUFFIX_SYNTHESIS_JUDGE: Final[str] = "_synthesis_judge"
TRACE_SUFFIX_SYNTHESIS_JUDGE_RETRY: Final[str] = "_synthesis_judge_retry_"

STAGE_RAW_INDEXING_CONCEPTS: Final[str] = "raw_indexing_concepts"
STAGE_RAW_INDEXING_SUMMARY: Final[str] = "raw_indexing_summary"
STAGE_RAW_INDEXING_SYNTHESIS: Final[str] = "raw_indexing_synthesis"

_META_KEY_TITLE: Final[str] = "title"
_META_KEY_CHANNEL_NAME: Final[str] = "channel_name"


def _retry_indices(max_rewrites: int) -> itertools.count[int] | range:
    """Yield retry attempt indices. If max_rewrites <= 0, allow unbounded retries."""
    if max_rewrites <= 0:
        return itertools.count(0)
    return range(max_rewrites + 1)


class LLMTranscriptDistiller:
    """Performs multi-pass LLM extraction and judge-evaluated refinement."""

    def __init__(
        self,
        llm_indexing_port: LLMTransformationPort,
        prompt_provider: PromptProviderPort,
        temperature: float = DEFAULT_DISTILLER_TEMPERATURE,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = DEFAULT_DISTILLER_MAX_REWRITES,
        llm_judge_port: LlmJudgePort | None = None,
    ) -> None:
        self.llm_indexing_port = llm_indexing_port
        self.prompt_provider = prompt_provider
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

    def extract_concepts(
        self,
        video_id: ContentId,
        title: str,
        text: str,
        channel_name: ChannelName,
        channel_id: ChannelId | None = None,
        user: UserIdentity | None = None,
    ) -> str:
        """Extract principal concepts through an iterative LLM-as-a-judge loop."""
        initial_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_CONCEPTS,
            content_title=title,
            transcript_excerpt=text,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        raw_concepts = ""

        for retries in _retry_indices(self.max_rewrites):
            if retries == 0:
                prompt = initial_prompt
                trace_id = f"{video_id}{TRACE_SUFFIX_CONCEPTS}"
                judge_trace_id = f"{video_id}{TRACE_SUFFIX_CONCEPTS_JUDGE}"
            else:
                logger.info(
                    "[IndexRaw] Attempt %d: concepts compliance check failed for '%s'. Requesting rewrite.",
                    retries,
                    video_id,
                )
                prompt = self.prompt_provider.get_prompt(
                    PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
                    previous_output=raw_concepts,
                    language=self.language,
                )
                trace_id = f"{video_id}{TRACE_SUFFIX_CONCEPTS_REWRITE}{retries}"
                judge_trace_id = f"{video_id}{TRACE_SUFFIX_CONCEPTS_JUDGE_RETRY}{retries}"

            raw_concepts = self.llm_indexing_port.transform(
                prompt=prompt,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )

            is_valid = False
            if is_valid_concepts_output(raw_concepts):
                if self.llm_judge_port is not None:
                    ctx = EvaluationContext(
                        stage_name=STAGE_RAW_INDEXING_CONCEPTS,
                        raw_text=text,
                        candidate_text=raw_concepts,
                        metadata={
                            _META_KEY_TITLE: title,
                            _META_KEY_CHANNEL_NAME: channel_name.value,
                        },
                        trace_id=judge_trace_id,
                        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                        judge_prompt_key=PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
                    )
                    is_valid = self.llm_judge_port.evaluate(ctx).passed
                else:
                    is_valid = True

            if is_valid:
                break

        cleaned = clean_concept_line(raw_concepts)
        return cleaned if cleaned else FALLBACK_KEY_CONCEPT_TITLE

    def extract_summary(
        self,
        video_id: ContentId,
        title: str,
        text: str,
        channel_name: ChannelName,
        channel_id: ChannelId | None = None,
        user: UserIdentity | None = None,
    ) -> str:
        """Extract structured conceptual summary through an iterative LLM-as-a-judge loop."""
        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_SUMMARY,
            content_title=title,
            transcript_excerpt=text,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        raw_summary = ""
        summary = ""

        for retries in _retry_indices(self.max_rewrites):
            trace_id = (
                f"{video_id}{TRACE_SUFFIX_SUMMARY}"
                if retries == 0
                else f"{video_id}{TRACE_SUFFIX_SUMMARY_RETRY}{retries}"
            )
            judge_trace_id = (
                f"{video_id}{TRACE_SUFFIX_SUMMARY_JUDGE}"
                if retries == 0
                else f"{video_id}{TRACE_SUFFIX_SUMMARY_JUDGE_RETRY}{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: summary judge returned false for '%s'. Regenerating summary.",
                    retries,
                    video_id,
                )

            raw_summary = self.llm_indexing_port.transform(
                prompt=chat_prompt,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            summary = clean_text_line(raw_summary) or title

            is_valid = False
            if self.llm_judge_port is not None:
                ctx = EvaluationContext(
                    stage_name=STAGE_RAW_INDEXING_SUMMARY,
                    raw_text=text,
                    candidate_text=summary,
                    metadata={
                        _META_KEY_TITLE: title,
                        _META_KEY_CHANNEL_NAME: channel_name.value,
                    },
                    trace_id=judge_trace_id,
                    required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                    judge_prompt_key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
                )
                is_valid = self.llm_judge_port.evaluate(ctx).passed
            else:
                is_valid = True

            if is_valid:
                break

        return summary if summary else title

    def extract_synthesis(
        self,
        video_id: ContentId,
        title: str,
        excerpt: str,
        summary: str,
        channel_name: ChannelName,
        channel_id: ChannelId | None = None,
        user: UserIdentity | None = None,
    ) -> str:
        """Synthesize dense single paratactic paragraph through an iterative LLM-as-a-judge loop."""
        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_SYNTHESIS,
            channel_name=channel_name.value,
            content_title=title,
            summary=summary,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        raw_synthesis = ""
        synthesis = ""

        for retries in _retry_indices(self.max_rewrites):
            trace_id = (
                f"{video_id}{TRACE_SUFFIX_SYNTHESIS}"
                if retries == 0
                else f"{video_id}{TRACE_SUFFIX_SYNTHESIS_RETRY}{retries}"
            )
            judge_trace_id = (
                f"{video_id}{TRACE_SUFFIX_SYNTHESIS_JUDGE}"
                if retries == 0
                else f"{video_id}{TRACE_SUFFIX_SYNTHESIS_JUDGE_RETRY}{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: synthesis compliance check failed for '%s'. Regenerating synthesis.",
                    retries,
                    video_id,
                )

            raw_synthesis = self.llm_indexing_port.transform(
                prompt=chat_prompt,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            synthesis = clean_text_line(raw_synthesis)

            is_valid = False
            if is_valid_synthesis_paragraph(synthesis):
                if self.llm_judge_port is not None:
                    ctx = EvaluationContext(
                        stage_name=STAGE_RAW_INDEXING_SYNTHESIS,
                        raw_text=excerpt,
                        candidate_text=synthesis,
                        metadata={
                            _META_KEY_TITLE: title,
                            _META_KEY_CHANNEL_NAME: channel_name.value,
                        },
                        trace_id=judge_trace_id,
                        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                        judge_prompt_key=PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
                    )
                    is_valid = self.llm_judge_port.evaluate(ctx).passed
                else:
                    is_valid = True

            if is_valid:
                break

        return synthesis if synthesis else (summary or title)
