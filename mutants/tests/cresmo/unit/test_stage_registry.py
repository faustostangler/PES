"""Unit tests for StageRegistry, StageDefinition, PipelineStatus.QUARANTINED, and StageQuarantinedError (ADR-031)."""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import CresmoDomainError, DomainValidationError, StageQuarantinedError
from cresmo.domain.stage_registry import StageDefinition, StageRegistry
from cresmo.domain.value_objects import (
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


def test_stage_registry_unknown_stage_raises_key_error() -> None:
    """Verify requesting an unregistered stage raises KeyError with helpful message."""
    assert StageRegistry.contains("unknown_stage") is False
    with pytest.raises(KeyError, match="Stage 'unknown_stage' is not registered"):
        StageRegistry.get("unknown_stage")


def test_stage_registry_all_stages() -> None:
    """Verify all_stages returns registered stage identifiers as a list."""
    stages = StageRegistry.all_stages()
    assert isinstance(stages, list)
    assert "fluid_prose" in stages


def test_stage_registry_register_dynamic_stage() -> None:
    """Verify register adds and associates the exact StageDefinition spec."""
    custom_spec = StageDefinition(required_criteria=(JudgeCriterion.SEMANTIC_FAITHFULNESS,))
    try:
        StageRegistry.register("custom_dynamic_stage", custom_spec)
        assert StageRegistry.contains("custom_dynamic_stage") is True
        retrieved = StageRegistry.get("custom_dynamic_stage")
        assert retrieved is custom_spec
        assert retrieved is not None
        assert "custom_dynamic_stage" in StageRegistry.all_stages()
    finally:
        StageRegistry._SPECS.pop("custom_dynamic_stage", None)
