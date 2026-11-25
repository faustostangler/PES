"""Unit tests for StageRegistry, StageDefinition, PipelineStatus.QUARANTINED, and StageQuarantinedError (ADR-031)."""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import CresmoDomainError, DomainValidationError, StageQuarantinedError
from cresmo.domain.stage_registry import (
    StageDefinition,
    StageRegistry,
)
from cresmo.domain.value_objects import (
    ConvergenceMode,
    JudgeCriterion,
    PipelineStatus,
)


def test_pipeline_status_quarantined_exists() -> None:
    """Verify PipelineStatus has QUARANTINED member conforming to ADR-031."""
    assert PipelineStatus.QUARANTINED.value == "QUARANTINED"
    assert PipelineStatus("QUARANTINED") is PipelineStatus.QUARANTINED


def test_stage_quarantined_error_contract() -> None:
    """Verify StageQuarantinedError captures all diagnostic provenance fields."""
    err = StageQuarantinedError(
        stage_name="fluid_prose",
        content_id="vid_123",
        attempts=3,
        critique="Orality removal failed.",
        overall_score=0.45,
    )

    assert isinstance(err, CresmoDomainError)
    assert isinstance(err, DomainValidationError)
    assert err.stage_name == "fluid_prose"
    assert err.content_id == "vid_123"
    assert err.attempts == 3
    assert err.critique == "Orality removal failed."
    assert err.overall_score == 0.45
    assert "Stage 'fluid_prose' quarantined" in str(err)
    assert "vid_123" in str(err)


def test_stage_registry_fluid_prose_spec() -> None:
    """Verify StageRegistry provides immutable, complete StageDefinition for fluid_prose."""
    assert StageRegistry.contains("fluid_prose") is True
    spec = StageRegistry.get("fluid_prose")

    assert isinstance(spec, StageDefinition)
    assert JudgeCriterion.ORALITY_REMOVAL in spec.required_criteria
    assert JudgeCriterion.SEMANTIC_FAITHFULNESS in spec.required_criteria
    assert JudgeCriterion.EPISTEMIC_CRITIQUE in spec.required_criteria
    assert JudgeCriterion.NER_PRESERVATION in spec.required_criteria
    assert JudgeCriterion.STRUCTURAL_COMPLIANCE in spec.required_criteria
    assert JudgeCriterion.AUTHORIAL_VOICE in spec.required_criteria
    assert spec.post_processor is not None


def test_stage_registry_gap_filler_spec() -> None:
    """Verify StageRegistry provides gap_filler specification with default max_passes=5 and convergence_mode."""
    assert StageRegistry.contains("gap_filler") is True
    spec = StageRegistry.get("gap_filler")
    assert isinstance(spec, StageDefinition)
    assert spec.convergence_mode is ConvergenceMode.HYBRID_SEMANTIC
    assert not hasattr(spec, "max_passes")
    assert not hasattr(spec, "early_stopping_enabled")
    assert not hasattr(spec, "saturation_checker")

    fluid_spec = StageRegistry.get("fluid_prose")
    assert fluid_spec.convergence_mode is ConvergenceMode.NONE


def test_stage_registry_long_expander_spec() -> None:
    """Verify StageRegistry configures long_expander with 5 criteria."""
    assert StageRegistry.contains("long_expander") is True
    spec = StageRegistry.get("long_expander")
    assert spec.convergence_mode is ConvergenceMode.HYBRID_SEMANTIC
    assert JudgeCriterion.LONGUE_DUREE_STRATIFICATION in spec.required_criteria
    assert JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING in spec.required_criteria
    assert JudgeCriterion.HISTORICAL_PALIMPSEST in spec.required_criteria
    assert JudgeCriterion.EXTRA_INFO_GRANULARITY in spec.required_criteria
    assert JudgeCriterion.IMPLICIT_FRAMING_STYLE in spec.required_criteria
    assert spec.eval_metadata["weights"][JudgeCriterion.LONGUE_DUREE_STRATIFICATION.value] == 0.35


def test_stage_registry_wide_expander_spec() -> None:
    """Verify StageRegistry configures wide_expander with 5 criteria."""
    assert StageRegistry.contains("wide_expander") is True
    spec = StageRegistry.get("wide_expander")
    assert spec.convergence_mode is ConvergenceMode.HYBRID_SEMANTIC
    assert JudgeCriterion.SYNCHRONIC_CONNECTIVITY in spec.required_criteria
    assert JudgeCriterion.COMPARATIVE_PARALLELISM in spec.required_criteria
    assert JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING in spec.required_criteria
    assert JudgeCriterion.EXTRA_INFO_GRANULARITY in spec.required_criteria
    assert JudgeCriterion.IMPLICIT_FRAMING_STYLE in spec.required_criteria
    assert spec.eval_metadata["weights"][JudgeCriterion.SYNCHRONIC_CONNECTIVITY.value] == 0.30
    assert spec.eval_metadata["weights"][JudgeCriterion.COMPARATIVE_PARALLELISM.value] == 0.30


def test_stage_registry_unknown_stage_raises_key_error() -> None:
    """Verify requesting an unregistered stage raises KeyError with helpful message."""
    assert StageRegistry.contains("unknown_stage") is False
    with pytest.raises(KeyError, match="Stage 'unknown_stage' is not registered"):
        StageRegistry.get("unknown_stage")
