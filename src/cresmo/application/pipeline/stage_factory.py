"""Factory for pipeline StageDescriptors conforming to ADR-031."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from cresmo.application.pipeline.stage_descriptor import StageDescriptor
from cresmo.application.ports import PipelineSettingsProtocol
from cresmo.domain.stage_registry import StageRegistry, StageSpec
from cresmo.domain.value_objects import (
    CandidateText,
    JudgeCriterion,
    PromptKey,
    StageEvaluationSpec,
)

TSource = TypeVar("TSource")
TOutput = TypeVar("TOutput")


class StageFactory:
    """Polyvalent Factory creating standardized StageDescriptors from declarative domain specs.

    Maintains single source of truth for prompts, quality criteria, post-processors,
    and stage execution tunables across pipeline stages (ADR-031).
    Delegates domain metadata resolution to StageRegistry.
    """

    def __init__(self, settings: PipelineSettingsProtocol) -> None:
        self.settings = settings
        self._cache: dict[str, StageDescriptor[Any, Any]] = {}

    def build_stage(
        self,
        stage_name: str,
        *,
        transform_prompt_key: PromptKey | None = None,
        required_criteria: Sequence[JudgeCriterion] | None = None,
        post_processor: Callable[[CandidateText, TSource], TOutput] | None = None,
        judge_prompt_key: PromptKey | None = None,
        candidate_extractor: Callable[[Any], str] | None = None,
        source_extractor: Callable[[TSource], str] | None = None,
        temperature: float | None = None,
        max_attempts: int | None = None,
        blocking: bool | None = None,
        eval_spec: StageEvaluationSpec | None = None,
        eval_metadata: dict[str, Any] | None = None,
    ) -> StageDescriptor[TSource, TOutput]:
        """Build or retrieve a standardized StageDescriptor for any pipeline stage.

        Resolves stage metadata from the declarative StageRegistry catalog, applies
        convention-over-configuration for prompts/extractors, and binds centralized
        settings with optional call-site overrides.
        """
        has_overrides = any(
            v is not None
            for v in (
                transform_prompt_key,
                required_criteria,
                post_processor,
                judge_prompt_key,
                candidate_extractor,
                source_extractor,
                temperature,
                max_attempts,
                blocking,
                eval_spec,
                eval_metadata,
            )
        )

        if not has_overrides and stage_name in self._cache:
            return self._cache[stage_name]

        spec: StageSpec | None = (
            StageRegistry.get(stage_name) if StageRegistry.contains(stage_name) else None
        )

        # 1. Resolve transform prompt key (explicit -> spec -> convention: PromptKey(stage_name))
        if transform_prompt_key is None:
            if spec and spec.transform_prompt_key is not None:
                transform_prompt_key = spec.transform_prompt_key
            else:
                try:
                    transform_prompt_key = PromptKey(stage_name)
                except ValueError as err:
                    raise ValueError(
                        f"Unknown stage '{stage_name}' with no transform_prompt_key provided."
                    ) from err

        # 2. Resolve post processor
        if post_processor is None and spec:
            post_processor = spec.post_processor

        # 3. Resolve tunables from settings with call-site overrides
        if temperature is None:
            temperature = getattr(self.settings, "llm_synthesis_temperature", None)
        effective_max_attempts: int = (
            max_attempts
            if max_attempts is not None
            else getattr(self.settings, "judge_max_attempts", 1)
        )
        effective_blocking: bool = (
            blocking
            if blocking is not None
            else getattr(self.settings, "judge_blocking", False)
        )

        # 4. Resolve quality evaluation spec
        if eval_spec is None:
            criteria = (
                tuple(required_criteria)
                if required_criteria is not None
                else (spec.required_criteria if spec else ())
            )
            cand_extractor = (
                candidate_extractor
                if candidate_extractor is not None
                else (
                    spec.candidate_extractor
                    if spec and spec.candidate_extractor is not None
                    else (lambda res: res.text if isinstance(res, CandidateText) else str(res))
                )
            )
            src_extractor = (
                source_extractor
                if source_extractor is not None
                else (spec.source_extractor if spec else None)
            )
            metadata = (
                eval_metadata if eval_metadata is not None else (spec.eval_metadata if spec else {})
            )

            if criteria or candidate_extractor is not None or source_extractor is not None:
                eval_spec = StageEvaluationSpec(
                    candidate_extractor=cand_extractor,
                    required_criteria=criteria,
                    max_attempts=effective_max_attempts,
                    source_extractor=src_extractor,
                    metadata=metadata,
                )

        if judge_prompt_key is None and spec:
            judge_prompt_key = spec.judge_prompt_key

        descriptor = StageDescriptor[TSource, TOutput](
            stage_name=stage_name,
            transform_prompt_key=transform_prompt_key,
            judge_prompt_key=judge_prompt_key,
            eval_spec=eval_spec,
            post_processor=post_processor,
            temperature=temperature,
            max_attempts=effective_max_attempts,
            blocking=effective_blocking,
        )

        if not has_overrides:
            self._cache[stage_name] = descriptor

        return descriptor

    # SOTA DX: Direct callable interface and aliases
    __call__ = build_stage
    create_stage = build_stage


__all__ = ["StageFactory", "StageSpec"]
