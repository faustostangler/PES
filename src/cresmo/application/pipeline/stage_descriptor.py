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
    ) -> tuple[str, str]:
        """Resolve system instructions and user prompt, injecting closed-loop reflection critique on retry."""
        resolved_title = content_title or getattr(source, "title", "")
        system_instruction, user_prompt = prompt_provider.get_prompt(
            self.transform_prompt_key,
            channel_name=channel_name,
            channel_id=channel_id,
            content_id=content_id,
            content_title=resolved_title,
            video_title=resolved_title,
            compendium_title=resolved_title,
            file_name=f"{content_id}.txt",
            raw_text=getattr(source, "body", str(source)),
            **extra_context,
        )

        if critique:
            user_prompt = (
                f"{user_prompt}\n\n[PREVIOUS ATTEMPT QUALITY FEEDBACK]\n"
                f"The previous generation failed quality evaluation:\n"
                f"{critique}\n"
                f"Please correct these defects in your output."
            )

        return system_instruction, user_prompt

    def post_process(self, candidate: CandidateText, source: TSource) -> TOutput:
        """Execute post-processing transformation on CandidateText or cast candidate directly."""
        if self.post_processor is not None:
            return self.post_processor(candidate, source)
        return candidate  # type: ignore[return-value]
