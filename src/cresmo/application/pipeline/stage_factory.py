"""Factory for pipeline StageConfigs conforming to ADR-031."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.ports import PipelineSettingsProtocol, TextEmbeddingPort
from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
from cresmo.domain.stage_registry import StageDefinition, StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    ConvergenceMode,
    JudgeCriterion,
    PromptKey,
    SaturationPolicy,
    SaturationThresholds,
    StageEvaluationSpec,
    never_saturate,
)

TSource = TypeVar("TSource")
TOutput = TypeVar("TOutput")


class StageFactory:
    """Polyvalent Factory creating standardized StageConfigs from declarative domain specs.

    Maintains single source of truth for prompts, quality criteria, post-processors,
    and stage execution tunables across pipeline stages (ADR-031).
    Delegates domain metadata resolution to StageRegistry.
    """

    def __init__(
        self,
        settings: PipelineSettingsProtocol,
        embedding_port: TextEmbeddingPort | None = None,
    ) -> None:
        self.settings = settings
        self._embedding_port = embedding_port
        self._cache: dict[str, StageConfig[Any, Any]] = {}

    def _build_saturation_thresholds(self) -> SaturationThresholds:
        """Build SaturationThresholds from settings with safe defaults for minimal settings objects."""
        return SaturationThresholds(
            lexical_identity_threshold=float(
                getattr(self.settings, "saturation_lexical_threshold", 0.95)
            ),
            max_lexical_word_delta=float(getattr(self.settings, "saturation_max_word_delta", 0.03)),
            semantic_similarity_threshold=float(
                getattr(self.settings, "saturation_semantic_threshold", 0.88)
            ),
            max_novel_paragraphs_for_saturation=int(
                getattr(self.settings, "saturation_max_novel_paragraphs", 0)
            ),
            long_unit_word_cutoff=int(
                getattr(self.settings, "saturation_long_unit_word_cutoff", 120)
            ),
            sliding_window_sentences=int(
                getattr(self.settings, "saturation_sliding_window_sentences", 3)
            ),
            sliding_window_overlap=int(
                getattr(self.settings, "saturation_sliding_window_overlap", 1)
            ),
        )

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
        max_passes: int | None = None,
        saturation_policy: SaturationPolicy | None = None,
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
                max_passes,
                saturation_policy,
            )
        )

        if not has_overrides and stage_name in self._cache:
            return self._cache[stage_name]

        stage_definition: StageDefinition | None = (
            StageRegistry.get(stage_name) if StageRegistry.contains(stage_name) else None
        )

        # 1. Resolve transform prompt key (explicit -> stage_definition -> convention: PromptKey(stage_name))
        if transform_prompt_key is None:
            if stage_definition and stage_definition.transform_prompt_key is not None:
                transform_prompt_key = stage_definition.transform_prompt_key
            else:
                try:
                    transform_prompt_key = PromptKey(stage_name)
                except ValueError as err:
                    raise ValueError(
                        f"Unknown stage '{stage_name}' with no transform_prompt_key provided."
                    ) from err

        # 2. Resolve post processor
        if post_processor is None and stage_definition:
            post_processor = stage_definition.post_processor

        # 3. Resolve tunables from settings with call-site overrides
        if temperature is None:
            temperature = getattr(self.settings, "llm_synthesis_temperature", None)
        if max_attempts is None:
            max_attempts = getattr(self.settings, "judge_max_attempts", 2)
        if blocking is None:
            blocking = getattr(self.settings, "judge_blocking", False)

        # 4. Resolve quality evaluation spec (StageEvaluationSpec)
        if eval_spec is None:
            resolved_criteria = (
                tuple(required_criteria)
                if required_criteria is not None
                else (stage_definition.required_criteria if stage_definition else ())
            )
            resolved_candidate_extractor = (
                candidate_extractor
                if candidate_extractor is not None
                else (
                    stage_definition.candidate_extractor
                    if stage_definition and stage_definition.candidate_extractor is not None
                    else (lambda res: res.text if isinstance(res, CandidateText) else str(res))
                )
            )
            resolved_source_extractor = (
                source_extractor
                if source_extractor is not None
                else (stage_definition.source_extractor if stage_definition else None)
            )
            resolved_eval_metadata = (
                eval_metadata
                if eval_metadata is not None
                else (stage_definition.eval_metadata if stage_definition else {})
            )

            if resolved_criteria or candidate_extractor is not None or source_extractor is not None:
                eval_spec = StageEvaluationSpec(
                    candidate_extractor=resolved_candidate_extractor,
                    required_criteria=resolved_criteria,
                    max_attempts=max_attempts,
                    source_extractor=resolved_source_extractor,
                    metadata=resolved_eval_metadata,
                )

        # 5. Resolve judge prompt key
        if judge_prompt_key is None and stage_definition:
            judge_prompt_key = stage_definition.judge_prompt_key

        # 6. Resolve multi-pass and saturation policy tunables
        if max_passes is None:
            max_passes = (
                stage_definition.max_passes
                if stage_definition and stage_definition.max_passes > 1
                else 1
            )

        resolved_saturation_policy: SaturationPolicy
        if saturation_policy is not None:
            resolved_saturation_policy = saturation_policy
        elif (
            stage_definition is not None
            and stage_definition.convergence_mode == ConvergenceMode.HYBRID_SEMANTIC
        ):
            resolved_saturation_policy = HybridSaturationEvaluator(
                embedding_port=self._embedding_port,
                thresholds=self._build_saturation_thresholds(),
            )
        else:
            resolved_saturation_policy = never_saturate

        stage_config = StageConfig[TSource, TOutput](
            stage_name=stage_name,
            transform_prompt_key=transform_prompt_key,
            judge_prompt_key=judge_prompt_key,
            eval_spec=eval_spec,
            post_processor=post_processor,
            temperature=temperature,
            max_attempts=max_attempts,
            blocking=blocking,
            max_passes=max_passes,
            saturation_policy=resolved_saturation_policy,
        )

        if not has_overrides:
            self._cache[stage_name] = stage_config

        return stage_config

    # SOTA DX: Direct callable interface and aliases
    __call__ = build_stage
    create_stage = build_stage


__all__ = ["StageDefinition", "StageFactory"]
