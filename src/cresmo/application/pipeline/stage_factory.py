"""Factory for pipeline StageDescriptors conforming to ADR-031."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, ClassVar

from cresmo.application.pipeline.stage_descriptor import StageDescriptor
from cresmo.application.ports import PipelineSettingsProtocol
from cresmo.application.use_cases.transform_fluid_prose import post_process_fluid_transcript
from cresmo.domain.value_objects import (
    CandidateText,
    JudgeCriterion,
    PromptKey,
    StageEvaluationSpec,
)


@dataclass(frozen=True, slots=True)
class StageSpec:
    """Declarative domain specification defining invariant stage metadata."""

    transform_prompt_key: PromptKey | None = None
    required_criteria: tuple[JudgeCriterion, ...] = ()
    judge_prompt_key: PromptKey | None = None
    post_processor: Callable[..., Any] | None = None
    source_extractor: Callable[..., str] | None = None
    candidate_extractor: Callable[..., str] | None = None
    eval_metadata: dict[str, Any] = field(default_factory=dict)


class StageFactory:
    """Polyvalent Factory creating standardized StageDescriptors from declarative domain specs.

    Maintains single source of truth for prompts, quality criteria, post-processors,
    and stage execution tunables across pipeline stages (ADR-031).
    """

    _STAGE_SPECS: ClassVar[dict[str, StageSpec]] = {
        "fluid_prose": StageSpec(
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
                JudgeCriterion.NER_PRESERVATION,
                JudgeCriterion.STRUCTURAL_COMPLIANCE,
            ),
            post_processor=post_process_fluid_transcript,
        ),
    }

    def __init__(self, settings: PipelineSettingsProtocol) -> None:
        self.settings = settings
        self._cache: dict[str, StageDescriptor[Any, Any]] = {}

    def build_stage[TSource, TOutput](
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

        Resolves stage metadata from the declarative catalog, applies convention-over-configuration
        for prompts/extractors, and binds centralized settings with optional call-site overrides.
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

        spec = self._STAGE_SPECS.get(stage_name)

        # 1. Resolve transform prompt key (explicit -> spec -> convention: PromptKey(stage_name))
        resolved_transform_prompt_key: PromptKey
        if transform_prompt_key is not None:
            resolved_transform_prompt_key = transform_prompt_key
        elif spec and spec.transform_prompt_key is not None:
            resolved_transform_prompt_key = spec.transform_prompt_key
        else:
            try:
                resolved_transform_prompt_key = PromptKey(stage_name)
            except ValueError as err:
                raise ValueError(
                    f"Unknown stage '{stage_name}' with no transform_prompt_key provided."
                ) from err

        # 2. Resolve post processor
        resolved_post_processor = (
            post_processor
            if post_processor is not None
            else (spec.post_processor if spec else None)
        )

        # 3. Resolve tunables from settings with call-site overrides
        resolved_temperature = (
            temperature
            if temperature is not None
            else getattr(self.settings, "llm_temperature", None)
        )
        resolved_max_attempts = (
            max_attempts
            if max_attempts is not None
            else getattr(self.settings, "judge_max_attempts", 1)
        )
        resolved_blocking = (
            blocking if blocking is not None else getattr(self.settings, "judge_blocking", False)
        )

        # 4. Resolve quality evaluation spec
        resolved_eval_spec: StageEvaluationSpec | None
        if eval_spec is not None:
            resolved_eval_spec = eval_spec
        else:
            resolved_criteria = (
                tuple(required_criteria)
                if required_criteria is not None
                else (spec.required_criteria if spec else ())
            )
            resolved_cand_ext = (
                candidate_extractor
                if candidate_extractor is not None
                else (
                    spec.candidate_extractor
                    if spec and spec.candidate_extractor is not None
                    else (lambda res: res.text if isinstance(res, CandidateText) else str(res))
                )
            )
            resolved_src_ext = (
                source_extractor
                if source_extractor is not None
                else (spec.source_extractor if spec else None)
            )
            resolved_eval_meta = (
                eval_metadata if eval_metadata is not None else (spec.eval_metadata if spec else {})
            )

            if resolved_criteria or candidate_extractor is not None or source_extractor is not None:
                resolved_eval_spec = StageEvaluationSpec(
                    candidate_extractor=resolved_cand_ext,
                    required_criteria=resolved_criteria,
                    max_attempts=resolved_max_attempts,
                    source_extractor=resolved_src_ext,
                    metadata=resolved_eval_meta,
                )
            else:
                resolved_eval_spec = None

        resolved_judge_prompt_key = (
            judge_prompt_key
            if judge_prompt_key is not None
            else (spec.judge_prompt_key if spec else None)
        )

        descriptor = StageDescriptor[TSource, TOutput](
            stage_name=stage_name,
            transform_prompt_key=resolved_transform_prompt_key,
            judge_prompt_key=resolved_judge_prompt_key,
            eval_spec=resolved_eval_spec,
            post_processor=resolved_post_processor,
            temperature=resolved_temperature,
            max_attempts=resolved_max_attempts,
            blocking=resolved_blocking,
        )

        if not has_overrides:
            self._cache[stage_name] = descriptor

        return descriptor

    # SOTA DX: Direct callable interface and aliases
    __call__ = build_stage
    create_stage = build_stage
