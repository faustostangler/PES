"""Declarative StageConfig for Standardized Pipeline Stage Execution.

Conforms to:
    - ADR-007: Pipeline Template Method DRY
    - ADR-021: Unified Pipeline Execution Template Method and Telemetry
    - ADR-031: Standardized StageConfig, StageTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric
    - SPEC-014: Standardized Stage Execution and Decision-Model Quality Fabric Specification
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final, cast

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.ports.prompt import PromptProviderPort
from cresmo.domain.entities.transcripts import extract_source_text
from cresmo.domain.services.convergence_evaluator import NO_NEW_GAPS_SENTINEL
from cresmo.domain.value_objects import (
    CandidateText,
    ChatMessage,
    ChatPrompt,
    MessageRole,
    PromptKey,
    SaturationPolicy,
    StageEvaluationSpec,
    never_saturate,
)

DEFAULT_STAGE_MAX_ATTEMPTS: Final[int] = 1
MIN_STAGE_MAX_PASSES: Final[int] = 1
DEFAULT_REFINE_PASS_NUM: Final[int] = 2
TRANSCRIPT_FILE_EXTENSION: Final[str] = ".txt"
REFINE_MODE_LABEL: Final[str] = "REFINE mode"

_CTX_KEY_CURRENT_TEXT: Final[str] = "current_text"
_CTX_KEY_PREV_PASS_NUM: Final[str] = "prev_pass_num"
_CTX_KEY_PASS_NUM: Final[str] = "pass_num"
_CTX_KEY_TOTAL_PASSES: Final[str] = "total_passes"
_CTX_KEY_DRAFT_SECTION: Final[str] = "draft_section"
_DRAFT_XML_TEMPLATE: Final[str] = '\n<draft pass="{pass_num}">\n{draft}\n</draft>\n'


def _append_to_last_user_message(prompt: ChatPrompt, suffix: str) -> ChatPrompt:
    """Append contextual draft or critique feedback to the final user turn of a ChatPrompt."""
    updated_messages: list[ChatMessage] = []
    appended = False
    last_index = len(prompt.messages) - 1
    for i, msg in enumerate(prompt.messages):
        if i == last_index and msg.role == MessageRole.USER:
            updated_messages.append(
                ChatMessage(role=MessageRole.USER, content=f"{msg.content}{suffix}")
            )
            appended = True
        else:
            updated_messages.append(msg)

    if not appended:
        updated_messages.append(ChatMessage(role=MessageRole.USER, content=suffix.strip()))

    return ChatPrompt(
        messages=tuple(updated_messages),
        system_prompt=prompt.system_prompt,
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
        max_attempts: Maximum generation attempts before giving up (default: 1).
        blocking: If True, raises StageQuarantinedError when quality evaluation fails after retries.
        max_passes: Maximum iterative refinement passes for multi-pass stages (default: 1).
        saturation_policy: Convergence evaluation callable governing early stopping.
    """

    stage_name: str
    transform_prompt_key: PromptKey
    judge_prompt_key: PromptKey | None = None
    eval_spec: StageEvaluationSpec | None = None
    post_processor: Callable[[CandidateText, TSource], TOutput] | None = None
    max_attempts: int = DEFAULT_STAGE_MAX_ATTEMPTS
    blocking: bool = False
    max_passes: int = MIN_STAGE_MAX_PASSES
    saturation_policy: SaturationPolicy = never_saturate

    def __post_init__(self) -> None:
        """Fail-fast validation for StageConfig invariants."""
        if isinstance(self.max_passes, bool) or self.max_passes < MIN_STAGE_MAX_PASSES:
            raise ValueError(
                f"StageConfig.max_passes must be >= {MIN_STAGE_MAX_PASSES}, got {self.max_passes!r}."
            )
        if not callable(self.saturation_policy):
            raise TypeError(
                f"StageConfig.saturation_policy must be callable, got {type(self.saturation_policy).__name__}."
            )

    def build_transform_prompt(
        self,
        prompt_provider: PromptProviderPort,
        source: TSource,
        *,
        context: PipelineExecutionContext,
        critique: str | None = None,
        **extra_context: Any,
    ) -> ChatPrompt:
        """Resolve ChatPrompt, injecting closed-loop reflection critique on retry."""
        effective_channel_id = context.channel.id.value if context.channel.id else ""
        raw_text = extract_source_text(source)  # type: ignore[arg-type]

        raw_current_text = extra_context.get(_CTX_KEY_CURRENT_TEXT)
        current_draft = (
            raw_current_text
            if isinstance(raw_current_text, str) and raw_current_text.strip()
            else None
        )
        provider_kwargs = dict(extra_context)
        draft_section = ""
        if current_draft is not None:
            raw_prev_pass = extra_context.get(_CTX_KEY_PREV_PASS_NUM)
            raw_pass_num = extra_context.get(_CTX_KEY_PASS_NUM, DEFAULT_REFINE_PASS_NUM)
            prev_pass_val = (
                int(raw_prev_pass)
                if raw_prev_pass is not None
                else max(MIN_STAGE_MAX_PASSES, int(raw_pass_num) - 1)
            )
            draft_section = _DRAFT_XML_TEMPLATE.format(
                pass_num=prev_pass_val, draft=current_draft
            )
            provider_kwargs.setdefault(_CTX_KEY_DRAFT_SECTION, draft_section)

        base_prompt: ChatPrompt = prompt_provider.get_prompt(
            self.transform_prompt_key,
            channel_name=context.channel.name,
            channel_id=effective_channel_id,
            content_id=context.content.id.value,
            content_title=context.content.title,
            file_name=f"{context.content.id.value}{TRANSCRIPT_FILE_EXTENSION}",
            raw_text=raw_text,
            **provider_kwargs,
        )

        # Fail-safe invariant: preserve Pass N-1 draft chaining even if remote prompt lacks {{draft_section}}
        if current_draft is not None:
            normalized_draft = current_draft.strip()
            draft_already_rendered = any(
                normalized_draft in msg.content for msg in base_prompt.messages
            )
            if not draft_already_rendered:
                pass_num = extra_context.get(_CTX_KEY_PASS_NUM)
                total_passes = extra_context.get(_CTX_KEY_TOTAL_PASSES)
                pass_header = (
                    f"Pass {pass_num}/{total_passes} — {REFINE_MODE_LABEL}"
                    if pass_num and total_passes
                    else REFINE_MODE_LABEL
                )
                draft_fallback_block = (
                    f"\n\n[{pass_header}: Iterative Expansion]\n"
                    f"Preserve verified facts, structure, and citations from the previous draft below, "
                    f"and iteratively deepen remaining conceptual, causal, historical, and Extra Info gaps "
                    f"without discarding prior work. If no verifiable gap remains, output ONLY "
                    f"{NO_NEW_GAPS_SENTINEL} and nothing else."
                    f"{draft_section}"
                )
                base_prompt = _append_to_last_user_message(base_prompt, draft_fallback_block)

        if not critique:
            return base_prompt

        critique_feedback = (
            f"\n\n[PREVIOUS ATTEMPT QUALITY FEEDBACK]\n"
            f"The previous generation failed quality evaluation:\n"
            f"{critique}\n"
            f"Please correct these defects in your output."
        )
        return _append_to_last_user_message(base_prompt, critique_feedback)

    def post_process(self, candidate: CandidateText, source: TSource) -> TOutput:
        """Execute post-processing transformation on CandidateText or return candidate directly."""
        if self.post_processor is not None:
            return self.post_processor(candidate, source)
        return cast(TOutput, candidate)
