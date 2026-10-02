"""Domain StageRegistry and StageSpec Catalog for Pipeline Stages (ADR-031)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from cresmo.domain.entities import post_process_fluid_transcript
from cresmo.domain.value_objects import JudgeCriterion, PromptKey


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


class StageRegistry:
    """Immutable domain catalog of pipeline stage definitions.

    Conforms to ADR-031 by maintaining pure domain invariants for all pipeline stages.
    """

    _SPECS: ClassVar[dict[str, StageSpec]] = {
        "fluid_prose": StageSpec(
            transform_prompt_key=PromptKey.FLUID_PROSE,
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
                JudgeCriterion.NER_PRESERVATION,
                JudgeCriterion.STRUCTURAL_COMPLIANCE,
            ),
            post_processor=post_process_fluid_transcript,
        ),
        # --- Quarantined Stage Specifications (Pending Full ADR-031 Implementation) ---
        # "raw_indexing": StageSpec(
        #     transform_prompt_key=PromptKey.RAW_INDEX_SUMMARY,
        #     required_criteria=(
        #         JudgeCriterion.INDEX_SYNTHESIS_QUALITY,
        #         JudgeCriterion.SEMANTIC_FAITHFULNESS,
        #     ),
        # ),
        # "gap_filler": StageSpec(
        #     transform_prompt_key=PromptKey.GAP_FILLER_PASS1,
        #     required_criteria=(
        #         JudgeCriterion.SEMANTIC_FAITHFULNESS,
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #     ),
        # ),
        # "long_expander": StageSpec(
        #     transform_prompt_key=PromptKey.LONG_EXPANDER,
        #     required_criteria=(
        #         JudgeCriterion.SEMANTIC_FAITHFULNESS,
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #     ),
        # ),
        # "wide_expander": StageSpec(
        #     transform_prompt_key=PromptKey.WIDE_EXPANDER,
        #     required_criteria=(
        #         JudgeCriterion.SEMANTIC_FAITHFULNESS,
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #     ),
        # ),
        # "atomic_inventory": StageSpec(
        #     transform_prompt_key=PromptKey.ATOMIC_INVENTORY,
        #     required_criteria=(
        #         JudgeCriterion.INVENTORY_COHERENCE,
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #     ),
        # ),
        # "atomic_batch": StageSpec(
        #     transform_prompt_key=PromptKey.ATOMIC_BATCH,
        #     required_criteria=(
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #         JudgeCriterion.SEMANTIC_FAITHFULNESS,
        #     ),
        # ),
        # "reconcile_mocs": StageSpec(
        #     transform_prompt_key=PromptKey.RECONCILE_MOCS,
        #     required_criteria=(
        #         JudgeCriterion.STRUCTURAL_COMPLIANCE,
        #     ),
        # ),
    }

    @classmethod
    def get(cls, stage_name: str) -> StageSpec:
        """Retrieve the immutable StageSpec for a given stage name."""
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

    @classmethod
    def register(cls, stage_name: str, spec: StageSpec) -> None:
        """Register or override a stage specification dynamically."""
        cls._SPECS[stage_name] = spec

    @classmethod
    def all_stages(cls) -> list[str]:
        """Return list of all registered stage identifiers."""
        return list(cls._SPECS.keys())
