"""Factory for pipeline StageConfigs conforming to ADR-031."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.ports import PipelineSettingsProtocol
from cresmo.domain.stage_registry import StageDefinition, StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    JudgeCriterion,
    PromptKey,
    StageEvaluationSpec,
)

TSource = TypeVar("TSource")
TOutput = TypeVar("TOutput")


class StageFactory:
    """Polyvalent Factory creating standardized StageConfigs from declarative domain specs.

    Maintains single source of truth for prompts, quality criteria, post-processors,
    and stage execution tunables across pipeline stages (ADR-031).
    Delegates domain metadata resolution to StageRegistry.
    """

    def __init__(self, settings: PipelineSettingsProtocol) -> None:
        self.settings = settings
        self._cache: dict[str, StageConfig[Any, Any]] = {}

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
    ) -> StageConfig[TSource, TOutput]:
        """Build or retrieve a standardized StageConfig for any pipeline stage.

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

        stage_definition: StageDefinition | None = (
            StageRegistry.get(stage_name) if StageRegistry.contains(stage_name) else None
        )

        # 1. Resolve transform prompt key (explicit -> stage_definition -> convention: PromptKey(stage_name))
        if transform_prompt_key is not None:
            effective_transform_prompt_key = transform_prompt_key
        elif stage_definition and stage_definition.transform_prompt_key is not None:
            effective_transform_prompt_key = stage_definition.transform_prompt_key
        else:
            try:
                effective_transform_prompt_key = PromptKey(stage_name)
            except ValueError as err:
                raise ValueError(
                    f"Unknown stage '{stage_name}' with no transform_prompt_key provided."
                ) from err

        # 2. Resolve post processor
        effective_post_processor = (
            post_processor
            if post_processor is not None
            else (stage_definition.post_processor if stage_definition else None)
        )

        # 3. Resolve tunables from settings with call-site overrides
        effective_temperature = (
            temperature
            if temperature is not None
            else getattr(self.settings, "llm_synthesis_temperature", None)
        )
        effective_max_attempts: int = (
            max_attempts
            if max_attempts is not None
            else getattr(self.settings, "judge_max_attempts", 1)
        )
        effective_blocking: bool = (
            blocking if blocking is not None else getattr(self.settings, "judge_blocking", False)
        )

        # 4. Resolve quality evaluation spec (StageEvaluationSpec)
        effective_eval_spec = eval_spec
        if effective_eval_spec is None:
            effective_criteria = (
                tuple(required_criteria)
                if required_criteria is not None
                else (stage_definition.required_criteria if stage_definition else ())
            )
            effective_candidate_extractor = (
                candidate_extractor
                if candidate_extractor is not None
                else (
                    stage_definition.candidate_extractor
                    if stage_definition and stage_definition.candidate_extractor is not None
                    else (lambda res: res.text if isinstance(res, CandidateText) else str(res))
                )
            )
            effective_source_extractor = (
                source_extractor
                if source_extractor is not None
                else (stage_definition.source_extractor if stage_definition else None)
            )
            effective_eval_metadata = (
                eval_metadata
                if eval_metadata is not None
                else (stage_definition.eval_metadata if stage_definition else {})
            )

            if (
                effective_criteria
                or candidate_extractor is not None
                or source_extractor is not None
            ):
                effective_eval_spec = StageEvaluationSpec(
                    candidate_extractor=effective_candidate_extractor,
                    required_criteria=effective_criteria,
                    max_attempts=effective_max_attempts,
                    source_extractor=effective_source_extractor,
                    metadata=effective_eval_metadata,
                )

        # 5. Resolve judge prompt key
        effective_judge_prompt_key = (
            judge_prompt_key
            if judge_prompt_key is not None
            else (stage_definition.judge_prompt_key if stage_definition else None)
        )

        stage_config = StageConfig[TSource, TOutput](
            stage_name=stage_name,
            transform_prompt_key=effective_transform_prompt_key,
            judge_prompt_key=effective_judge_prompt_key,
            eval_spec=effective_eval_spec,
            post_processor=effective_post_processor,
            temperature=effective_temperature,
            max_attempts=effective_max_attempts,
            blocking=effective_blocking,
        )

        if not has_overrides:
            self._cache[stage_name] = stage_config

        return stage_config

    # SOTA DX: Direct callable interface and aliases
    __call__ = build_stage
    create_stage = build_stage


__all__ = ["StageDefinition", "StageFactory"]
