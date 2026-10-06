"""Declarative StageConfig for Standardized Pipeline Stage Execution.

Conforms to:
    - ADR-007: Pipeline Template Method DRY
    - ADR-021: Unified Pipeline Execution Template Method and Telemetry
    - ADR-031: Standardized StageConfig, SourceTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric
    - SPEC-014: Standardized Stage Execution and Decision-Model Quality Fabric Specification
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from cresmo.application.ports.prompt import PromptProviderPort
from cresmo.domain.value_objects import (
    CandidateText,
    ChatMessage,
    ChatPrompt,
    MessageRole,
    PromptKey,
    StageEvaluationSpec,
)


@dataclass(frozen=True)
class StageConfig[TSource, TOutput]:
    """Declarative specification defining transformation, quality gate, and post-processing for a stage.

    Attributes:
        stage_name: Unique identifier for the stage (e.g. 'fluid_prose').
        transform_prompt_key: Canonical PromptKey resolved via PromptProviderPort.
        judge_prompt_key: Optional PromptKey for LLM judge instructions.
        eval_spec: Quality gate criteria and candidate extraction specification.
        post_processor: Optional callable transforming CandidateText into domain aggregate or output.
        temperature: Sampling temperature override for generative LLM call.
        max_attempts: Maximum generation attempts before giving up (default: 1).
        blocking: If True, raises DomainValidationError when quality evaluation fails after retries.
    """

    stage_name: str
    transform_prompt_key: PromptKey
    judge_prompt_key: PromptKey | None = None
    eval_spec: StageEvaluationSpec | None = None
    post_processor: Callable[[CandidateText, TSource], TOutput] | None = None
    temperature: float | None = None
    max_attempts: int = 1
    blocking: bool = False

    def build_transform_prompt(
        self,
        prompt_provider: PromptProviderPort,
        source: TSource,
        *,
        channel_name: str,
        content_id: str,
        channel_id: str = "",
        content_title: str = "",
        critique: str | None = None,
        **extra_context: Any,
    ) -> ChatPrompt:
        """Resolve ChatPrompt, injecting closed-loop reflection critique on retry."""
        base_prompt: ChatPrompt = prompt_provider.get_prompt(
            self.transform_prompt_key,
            channel_name=channel_name,
            channel_id=channel_id,
            content_id=content_id,
            content_title=content_title,
            file_name=f"{content_id}.txt",
            raw_text=getattr(source, "body", str(source)),
            **extra_context,
        )

        if not critique:
            return base_prompt

        critique_feedback = (
            f"\n\n[PREVIOUS ATTEMPT QUALITY FEEDBACK]\n"
            f"The previous generation failed quality evaluation:\n"
            f"{critique}\n"
            f"Please correct these defects in your output."
        )

        new_messages: list[ChatMessage] = []
        for i, msg in enumerate(base_prompt.messages):
            if i == len(base_prompt.messages) - 1 and msg.role == MessageRole.USER:
                new_messages.append(
                    ChatMessage(role=MessageRole.USER, content=f"{msg.content}{critique_feedback}")
                )
            else:
                new_messages.append(msg)

        if not new_messages and base_prompt.system_instruction:
            new_messages.append(
                ChatMessage(role=MessageRole.USER, content=critique_feedback.strip())
            )

        return ChatPrompt(
            messages=tuple(new_messages),
            system_instruction=base_prompt.system_instruction,
        )

    def post_process(self, candidate: CandidateText, source: TSource) -> TOutput:
        """Execute post-processing transformation on CandidateText or cast candidate directly."""
        if self.post_processor is not None:
            return self.post_processor(candidate, source)
        return candidate  # type: ignore[return-value]
