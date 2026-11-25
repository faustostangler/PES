"""Domain StageRegistry and StageDefinition Catalog for Pipeline Stages (ADR-031)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar

from cresmo.domain.entities import post_process_fluid_transcript
from cresmo.domain.services.stage_post_processor import post_process_expanded_transcript
from cresmo.domain.value_objects import (
    GAP_FILLER_CANONICAL_WEIGHTS,
    GAP_FILLER_MECHANICAL_VETO_CRITERIA,
    LONG_EXPANDER_CANONICAL_WEIGHTS,
    LONG_EXPANDER_MECHANICAL_VETO_CRITERIA,
    WIDE_EXPANDER_CANONICAL_WEIGHTS,
    WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA,
    JudgeCriterion,
    PromptKey,
)
from cresmo.domain.value_objects.convergence import ConvergenceMode

__all__ = [
    "StageDefinition",
    "StageName",
    "StageRegistry",
]


class StageName(StrEnum):
    """Canonical enumeration of conveyor pipeline stage identifiers."""

    RAW = "raw"
    FLUID_PROSE = "fluid_prose"
    GAP_FILLER = "gap_filler"
    LONG_EXPANDER = "long_expander"
    WIDE_EXPANDER = "wide_expander"


@dataclass(frozen=True, slots=True)
class StageDefinition:
    """Declarative domain specification defining invariant stage metadata."""

    transform_prompt_key: PromptKey | None = None
    required_criteria: tuple[JudgeCriterion, ...] = ()
    judge_prompt_key: PromptKey | None = None
    post_processor: Callable[..., Any] | None = None
    eval_metadata: dict[str, Any] = field(default_factory=dict)
    convergence_mode: ConvergenceMode = ConvergenceMode.NONE


class StageRegistry:
    """Immutable domain catalog of pipeline stage definitions.

    Conforms to ADR-031 by maintaining pure domain invariants for all pipeline stages.
    """

    _SPECS: ClassVar[dict[str, StageDefinition]] = {
        StageName.FLUID_PROSE: StageDefinition(
            transform_prompt_key=PromptKey.FLUID_PROSE,
            judge_prompt_key=PromptKey.JUDGE_FLUID_PROSE,
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
                JudgeCriterion.EPISTEMIC_CRITIQUE,
                JudgeCriterion.NER_PRESERVATION,
                JudgeCriterion.STRUCTURAL_COMPLIANCE,
                JudgeCriterion.AUTHORIAL_VOICE,
            ),
            post_processor=post_process_fluid_transcript,
        ),
        StageName.GAP_FILLER: StageDefinition(
            transform_prompt_key=PromptKey.GAP_FILLER,
            judge_prompt_key=PromptKey.JUDGE_GAP_FILLER,
            required_criteria=tuple(GAP_FILLER_CANONICAL_WEIGHTS.keys()),
            post_processor=post_process_expanded_transcript,
            eval_metadata={
                "weights": {c.value: w for c, w in GAP_FILLER_CANONICAL_WEIGHTS.items()},
                "veto_criteria": sorted(c.value for c in GAP_FILLER_MECHANICAL_VETO_CRITERIA),
            },
            convergence_mode=ConvergenceMode.HYBRID_SEMANTIC,
        ),
        StageName.LONG_EXPANDER: StageDefinition(
            transform_prompt_key=PromptKey.LONG_EXPANDER,
            judge_prompt_key=PromptKey.JUDGE_LONG_EXPANDER,
            required_criteria=tuple(LONG_EXPANDER_CANONICAL_WEIGHTS.keys()),
            post_processor=post_process_expanded_transcript,
            eval_metadata={
                "weights": {c.value: w for c, w in LONG_EXPANDER_CANONICAL_WEIGHTS.items()},
                "veto_criteria": sorted(c.value for c in LONG_EXPANDER_MECHANICAL_VETO_CRITERIA),
            },
            convergence_mode=ConvergenceMode.HYBRID_SEMANTIC,
        ),
        StageName.WIDE_EXPANDER: StageDefinition(
            transform_prompt_key=PromptKey.WIDE_EXPANDER,
            judge_prompt_key=PromptKey.JUDGE_WIDE_EXPANDER,
            required_criteria=tuple(WIDE_EXPANDER_CANONICAL_WEIGHTS.keys()),
            post_processor=post_process_expanded_transcript,
            eval_metadata={
                "weights": {c.value: w for c, w in WIDE_EXPANDER_CANONICAL_WEIGHTS.items()},
                "veto_criteria": sorted(c.value for c in WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA),
            },
            convergence_mode=ConvergenceMode.HYBRID_SEMANTIC,
        ),
    }

    @classmethod
    def get(cls, stage_name: str) -> StageDefinition:
        """Retrieve the immutable StageDefinition for a given stage name."""
        if stage_name not in cls._SPECS:
            raise KeyError(
                f"Stage '{stage_name}' is not registered in StageRegistry. "
                f"Available stages: {list(cls._SPECS.keys())}"
            )
        return cls._SPECS[stage_name]

    @classmethod
    def contains(cls, stage_name: str) -> bool:
        """Check whether a stage is registered in the domain catalog."""
        return stage_name in cls._SPECS
