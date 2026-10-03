"""LLM transcript distillation and multi-pass judge loops.

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
"""

from __future__ import annotations

import logging

from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.application.use_cases.indexing.validators import (
    can_retry,
    clean_concept_line,
    clean_text_line,
    is_valid_concepts_output,
    is_valid_synthesis_paragraph,
    parse_judge_boolean,
)
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    JudgeCriterion,
    PromptKey,
)

logger = logging.getLogger(__name__)


class LLMTranscriptDistiller:
    """Performs multi-pass LLM extraction and judge-evaluated refinement."""

    def __init__(
        self,
        llm_indexing_port: LLMTransformationPort,
        prompt_provider: PromptProviderPort,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
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
        system_instructions, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_CONCEPTS,
            video_title=title,
            transcript_excerpt=text,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        is_valid = False
        retries = 0
        raw_concepts = ""

        while not is_valid:
            if retries == 0:
                prompt = user_prompt
                trace_id = f"{video_id}_concepts"
                judge_trace_id = f"{video_id}_concepts_judge"
            else:
                logger.info(
                    "[IndexRaw] Attempt %d: concepts compliance check failed for '%s'. Requesting rewrite.",
                    retries,
                    video_id,
                )
                _, prompt = self.prompt_provider.get_prompt(
                    PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
                    previous_output=raw_concepts,
                    language=self.language,
                )
                trace_id = f"{video_id}_concepts_rewrite_{retries}"
                judge_trace_id = f"{video_id}_concepts_judge_retry_{retries}"

            raw_concepts = self.llm_indexing_port.transform(
                prompt=prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )

            if is_valid_concepts_output(raw_concepts):
                if self.llm_judge_port is not None:
                    ctx = EvaluationContext(
                        stage_name="raw_indexing_concepts",
                        raw_text=text,
                        candidate_text=raw_concepts,
                        metadata={"title": title, "channel": channel_name.value},
                        trace_id=judge_trace_id,
                        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                    )
                    is_valid = self.llm_judge_port.evaluate(ctx).passed
                elif self.prompt_provider:
                    # Transitional fallback (ADR-010 / ADR-029 §2.4)
                    judge_system_instructions, judge_prompt = self.prompt_provider.get_prompt(
                        PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
                        video_title=title,
                        transcript_excerpt=text,
                        concepts=raw_concepts,
                        language=self.language,
                    )
                    judge_response = self.llm_indexing_port.transform(
                        prompt=judge_prompt,
                        system_instruction=judge_system_instructions,
                        temperature=0.0,
                        trace_id=judge_trace_id,
                        session_id=session_id,
                        user_id=user_id,
                    )
                    is_valid = parse_judge_boolean(judge_response)
                else:
                    is_valid = True
            else:
                is_valid = False

            if not is_valid:
                if not can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        cleaned = clean_concept_line(raw_concepts)
        return cleaned if cleaned else "Síntese Conceitual"

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
        system_instructions, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_SUMMARY,
            video_title=title,
            transcript_excerpt=text,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        is_valid = False
        retries = 0
        raw_summary = ""
        summary = ""

        while not is_valid:
            trace_id = (
                f"{video_id}_summary" if retries == 0 else f"{video_id}_summary_retry_{retries}"
            )
            judge_trace_id = (
                f"{video_id}_summary_judge"
                if retries == 0
                else f"{video_id}_summary_judge_retry_{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: summary judge returned false for '%s'. Regenerating summary.",
                    retries,
                    video_id,
                )

            raw_summary = self.llm_indexing_port.transform(
                prompt=user_prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            summary = clean_text_line(raw_summary) or title

            if self.llm_judge_port is not None:
                ctx = EvaluationContext(
                    stage_name="raw_indexing_summary",
                    raw_text=text,
                    candidate_text=summary,
                    metadata={"title": title, "channel": channel_name.value},
                    trace_id=judge_trace_id,
                    required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                )
                is_valid = self.llm_judge_port.evaluate(ctx).passed
            elif self.prompt_provider:
                # Transitional fallback (ADR-010 / ADR-029 §2.4)
                judge_system_instructions, judge_prompt = self.prompt_provider.get_prompt(
                    PromptKey.JUDGE_RAW_INDEX_SUMMARY,
                    video_title=title,
                    transcript_excerpt=text,
                    summary=summary,
                    language=self.language,
                )
                judge_response = self.llm_indexing_port.transform(
                    prompt=judge_prompt,
                    system_instruction=judge_system_instructions,
                    temperature=0.0,
                    trace_id=judge_trace_id,
                    session_id=session_id,
                    user_id=user_id,
                )
                is_valid = parse_judge_boolean(judge_response)
            else:
                is_valid = True

            if not is_valid:
                if not can_retry(retries, self.max_rewrites):
                    break
                retries += 1

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
        system_instructions, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.RAW_INDEX_SYNTHESIS,
            video_title=title,
            summary=summary,
            language=self.language,
        )

        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=video_id,
            channel_id=channel_id,
        ).value
        user_id = user.value if user else UserIdentity.anonymous().value
        is_valid = False
        retries = 0
        raw_synthesis = ""
        synthesis = ""

        while not is_valid:
            trace_id = (
                f"{video_id}_synthesis" if retries == 0 else f"{video_id}_synthesis_retry_{retries}"
            )
            judge_trace_id = (
                f"{video_id}_synthesis_judge"
                if retries == 0
                else f"{video_id}_synthesis_judge_retry_{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: synthesis compliance check failed for '%s'. Regenerating synthesis.",
                    retries,
                    video_id,
                )

            raw_synthesis = self.llm_indexing_port.transform(
                prompt=user_prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            synthesis = clean_text_line(raw_synthesis)

            if is_valid_synthesis_paragraph(synthesis):
                if self.llm_judge_port is not None:
                    ctx = EvaluationContext(
                        stage_name="raw_indexing_synthesis",
                        raw_text=excerpt,
                        candidate_text=synthesis,
                        metadata={"title": title, "channel": channel_name.value},
                        trace_id=judge_trace_id,
                        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
                    )
                    is_valid = self.llm_judge_port.evaluate(ctx).passed
                elif self.prompt_provider:
                    # Transitional fallback (ADR-010 / ADR-029 §2.4)
                    judge_system_instructions, judge_prompt = self.prompt_provider.get_prompt(
                        PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
                        video_title=title,
                        transcript_excerpt=excerpt,
                        synthesis=synthesis,
                        language=self.language,
                    )
                    judge_response = self.llm_indexing_port.transform(
                        prompt=judge_prompt,
                        system_instruction=judge_system_instructions,
                        temperature=0.0,
                        trace_id=judge_trace_id,
                        session_id=session_id,
                        user_id=user_id,
                    )
                    is_valid = parse_judge_boolean(judge_response)
                else:
                    is_valid = True
            else:
                is_valid = False

            if not is_valid:
                if not can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        return synthesis if synthesis else (summary or title)
