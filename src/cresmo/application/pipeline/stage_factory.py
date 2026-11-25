"""Factory for pipeline StageConfigs conforming to ADR-031 and ADR-077."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, cast

from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.ports import TextEmbeddingPort
from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
from cresmo.domain.stage_registry import StageName, StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    ConvergenceMode,
    SaturationPolicy,
    StageEvaluationSpec,
    StageExecutionPolicy,
    never_saturate,
)


class StageFactory:
    """Factory creating standardized StageConfigs from declarative domain specs.

    Maintains single source of truth for prompts, quality criteria, post-processors,
    and stage execution tunables across pipeline stages (ADR-031, ADR-074, ADR-077).
    """

    def __init__(
        self,
        policy: StageExecutionPolicy | None = None,
        embedding_port: TextEmbeddingPort | None = None,
    ) -> None:
        self.policy: StageExecutionPolicy = policy or StageExecutionPolicy()
        self._embedding_port = embedding_port
        self._cache: dict[str, StageConfig[Any, Any]] = {}

    def build_stage[TSource, TOutput](
        self,
        stage_name: StageName | str,
        *,
        max_passes: int | None = None,
    ) -> StageConfig[TSource, TOutput]:
        """Build or retrieve a standardized StageConfig for a registered pipeline stage."""
        canonical_name = str(stage_name)
        base_config = self._cache.get(canonical_name)
        if base_config is None:
            stage_definition = StageRegistry.get(canonical_name)
            if stage_definition.transform_prompt_key is None:
                raise ValueError(
                    f"Stage '{canonical_name}' is missing transform_prompt_key in StageRegistry."
                )

            max_attempts = self.policy.judge_max_attempts
            blocking = self.policy.judge_blocking

            eval_spec: StageEvaluationSpec | None = None
            if stage_definition.required_criteria:
                eval_spec = StageEvaluationSpec(
                    candidate_extractor=lambda res: (
                        res.text if isinstance(res, CandidateText) else str(res)
                    ),
                    required_criteria=stage_definition.required_criteria,
                    max_attempts=max_attempts,
                    metadata=dict(stage_definition.eval_metadata),
                )

            default_max_passes = self.policy.resolve_max_passes(
                canonical_name,
                stage_definition.convergence_mode,
            )

            saturation_policy: SaturationPolicy = (
                HybridSaturationEvaluator(
                    embedding_port=self._embedding_port,
                    thresholds=self.policy.saturation_thresholds,
                )
                if stage_definition.convergence_mode == ConvergenceMode.HYBRID_SEMANTIC
                else never_saturate
            )

            base_config = StageConfig[Any, Any](
                stage_name=canonical_name,
                transform_prompt_key=stage_definition.transform_prompt_key,
                judge_prompt_key=stage_definition.judge_prompt_key,
                eval_spec=eval_spec,
                post_processor=stage_definition.post_processor,
                max_attempts=max_attempts,
                blocking=blocking,
                max_passes=default_max_passes,
                saturation_policy=saturation_policy,
            )
            self._cache[canonical_name] = base_config

        if max_passes is not None:
            return cast(StageConfig[TSource, TOutput], replace(base_config, max_passes=max_passes))
        return cast(StageConfig[TSource, TOutput], base_config)


__all__ = ["StageFactory"]
