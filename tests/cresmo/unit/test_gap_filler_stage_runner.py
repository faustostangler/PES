"""Integration and unit tests for gap_filler execution in PipelineStageRunner.

Conforms to:
    - ADR-028: Decoupling Fluid Prose and Gap Filler
    - ADR-031: Standardized StageConfig and Closed-Loop Reflection
    - ADR-039: Two-Layered Mechanical and Semantic Quality Gate
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    DefaultPipelineSettings,
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
)
from cresmo.domain.entities import (
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.entities.compendium import EnrichedCompendium
from cresmo.domain.entities.transcripts import FluidTranscript
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    Content,
    ContentId,
)


@pytest.fixture
def sample_context() -> PipelineExecutionContext:
    return PipelineExecutionContext(
        session_id=PipelineSessionId("sess:gap_filler"),
        user_identity=UserIdentity.worker(),
        channel=Channel(name="Historia", id=ChannelId("UC_hist")),
        content=Content.create(id=ContentId("vid_hist1"), title="Fundação"),
    )


@pytest.fixture
def sample_fluid_transcript() -> FluidTranscript:
    return FluidTranscript.create(
        channel_name="Historia",
        content_id="vid_hist1",
        title="Fundação",
        body="## Fundação de Portugal\n\nTexto fluido sem oralidades.",
        source_url="https://youtube.com/watch?v=vid_hist1",
    )


def test_gap_filler_execution_single_pass_override(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: FluidTranscript,
) -> None:
    """Verify gap_filler transforms FluidTranscript into EnrichedCompendium when max_passes=1 override is provided."""
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes da Reconquista."
    )

    stage_factory = StageFactory(settings=DefaultPipelineSettings())

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result = runner.execute_stage(
        "gap_filler",
        source=sample_fluid_transcript,
        context=sample_context,
        max_passes=1,
    )

    assert isinstance(result, EnrichedCompendium)
    assert result.content_id == ContentId("vid_hist1")
    assert "Henrique de Borgonha" in result.body
    assert "1066-1112" in result.complementary_info
    assert mock_llm.transform.call_count == 1


def test_gap_filler_execution_multi_pass_to_completion(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: FluidTranscript,
) -> None:
    """Verify gap_filler iterates through all 3 passes by domain default when non-saturated."""
    pass1_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes."
    )
    pass2_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI**.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
        "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense."
    )
    pass3_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI**.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
        "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense.\n"
        "3. **Teresa de Leão** (1080-1130) governou como regente."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_text, pass2_text, pass3_text]

    stage_factory = StageFactory(settings=DefaultPipelineSettings())

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result = runner.execute_stage(
        "gap_filler",
        source=sample_fluid_transcript,
        context=sample_context,
    )

    assert isinstance(result, EnrichedCompendium)
    assert result.content_id == ContentId("vid_hist1")
    assert "Henrique de Borgonha" in result.body
    assert "Teresa de Leão" in result.complementary_info
    # Proves all 3 passes were executed as declared by domain intelligence
    assert mock_llm.transform.call_count == 3


def test_gap_filler_execution_early_stopping_on_saturation(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: FluidTranscript,
) -> None:
    """Verify gap_filler stops before max_passes when mechanical saturation is detected."""
    # Pass 1 output:
    pass1_text = (
        "## Fundação de Portugal\n\n"
        "O conde **Henrique de Borgonha** governou o território.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão** em 1093."
    )
    # Pass 2 output (same bold entities, delta items = 0 -> saturated):
    pass2_text = (
        "## Fundação de Portugal\n\n"
        "O nobre conde **Henrique de Borgonha** governou o território ocidental.\n\n"
        "## Informações Complementares\n\n"
        "1. O nobre **Henrique de Borgonha** casou com a infanta **Teresa de Leão** em 1093."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_text, pass2_text, "pass 3 should not be called"]

    settings = DefaultPipelineSettings(gap_filler_passes=3)
    stage_factory = StageFactory(settings=settings)

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result = runner.execute_stage(
        "gap_filler",
        source=sample_fluid_transcript,
        context=sample_context,
    )

    assert isinstance(result, EnrichedCompendium)
    # Proves early stopping occurred at pass 2 (pass 3 was never called)
    assert mock_llm.transform.call_count == 2
