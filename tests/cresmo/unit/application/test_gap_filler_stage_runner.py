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
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    Content,
    ContentId,
    MediaProvenance,
)


@pytest.fixture
def sample_context() -> PipelineExecutionContext:
    return PipelineExecutionContext(
        user_identity=UserIdentity.worker(),
        channel=Channel(name="Historia", id=ChannelId("UC_hist")),
        content=Content.create(
            id=ContentId("vid_hist1"), title="Fundação", session_id="sess:gap_filler"
        ),
    )


@pytest.fixture
def sample_fluid_transcript() -> StageTranscript:
    return StageTranscript(
        channel=Channel(name="Historia", id=ChannelId("UC_hist")),
        provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_hist1"),
        content=Content.create(
            id="vid_hist1",
            title="Fundação",
            text="## Fundação de Portugal\n\nTexto fluido sem oralidades.",
        ),
    )


def test_gap_filler_execution_single_pass_override(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify gap_filler transforms StageTranscript into StageTranscript when max_passes=1 override is provided."""
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo.\n\n"
        "### Extra Info\n\n"
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

    assert isinstance(result, StageTranscript)
    assert result.content.id == ContentId("vid_hist1")
    assert "Henrique de Borgonha" in result.content.text
    assert "1066-1112" in result.content.text
    assert mock_llm.transform.call_count == 1


def test_gap_filler_execution_multi_pass_to_completion(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify gap_filler iterates through all 3 passes by domain default when non-saturated."""
    pass1_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes."
    )
    pass2_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI**.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
        "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense."
    )
    pass3_text = (
        "## Fundação de Portugal\n\n"
        "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI**.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
        "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense.\n"
        "3. **Teresa de Leão** (1080-1130) governou como regente."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_text, pass2_text, pass3_text]

    stage_factory = StageFactory(
        settings=DefaultPipelineSettings(expansion_max_passes=3, gap_filler_passes=3)
    )

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
        max_passes=3,
    )

    assert isinstance(result, StageTranscript)
    assert result.content.id == ContentId("vid_hist1")
    assert "Henrique de Borgonha" in result.content.text
    assert "Teresa de Leão" in result.content.text
    # Proves all 3 passes were executed as declared by domain intelligence
    assert mock_llm.transform.call_count == 3


def test_gap_filler_execution_early_stopping_on_saturation(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify gap_filler stops before max_passes when mechanical saturation is detected."""
    # Pass 1 output:
    pass1_text = (
        "## Fundação de Portugal\n\n"
        "O conde **Henrique de Borgonha** governou o território.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão** em 1093."
    )
    # Pass 2 output (same bold entities, delta items = 0 -> saturated):
    pass2_text = (
        "## Fundação de Portugal\n\n"
        "O nobre conde **Henrique de Borgonha** governou o território ocidental.\n\n"
        "### Extra Info\n\n"
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

    assert isinstance(result, StageTranscript)
    # Proves early stopping occurred at pass 2 (pass 3 was never called)
    assert mock_llm.transform.call_count == 2


def test_gap_filler_multi_pass_chains_previous_output_and_emits_pass_telemetry(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify multi-pass gap_filler chains Pass N-1 draft into Pass N and scopes telemetry pass numbers."""
    from cresmo.application.ports import (
        get_active_telemetry_pass,
        get_active_telemetry_stage,
        resolve_llm_generation_span_name,
    )
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    outputs = [
        (
            "## Fundação de Portugal\n\n"
            "Em 1096, o conde **Henrique de Borgonha** assumiu o governo.\n\n"
            "### Extra Info\n\n"
            "1. **Henrique de Borgonha** (1066-1112) liderou contingentes."
        ),
        (
            "## Fundação de Portugal\n\n"
            "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI**.\n\n"
            "### Extra Info\n\n"
            "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
            "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense."
        ),
        (
            "## Fundação de Portugal\n\n"
            "Em 1096, o conde **Henrique de Borgonha** assumiu o governo sob **Afonso VI** e casou com **Teresa de Leão**.\n\n"
            "### Extra Info\n\n"
            "1. **Henrique de Borgonha** (1066-1112) liderou contingentes.\n"
            "2. **Afonso VI de Leão** (1040-1109) concedeu o Condado Portucalense.\n"
            "3. **Teresa de Leão** (1080-1130) governou como regente."
        ),
    ]
    recorded_calls: list[tuple[str, int | None, str]] = []
    call_idx = 0

    def _spy_transform(prompt: object, **_kwargs: object) -> str:
        nonlocal call_idx
        user_content = prompt.get_last_user_content()  # type: ignore[attr-defined]
        recorded_calls.append(
            (user_content, get_active_telemetry_pass(), resolve_llm_generation_span_name())
        )
        out = outputs[call_idx]
        call_idx += 1
        return out

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = _spy_transform

    stage_factory = StageFactory(
        settings=DefaultPipelineSettings(expansion_max_passes=3, gap_filler_passes=3)
    )
    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=JsonPromptProvider(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result = runner.execute_stage(
        "gap_filler",
        source=sample_fluid_transcript,
        context=sample_context,
        max_passes=3,
    )

    assert isinstance(result, StageTranscript)
    assert len(recorded_calls) == 3

    p1_user, p1_pass, p1_span = recorded_calls[0]
    assert "<draft" not in p1_user
    assert "Texto fluido sem oralidades." in p1_user
    assert p1_pass == 1
    assert p1_span == "cresmo.gap_filler.generate.pass_1"

    p2_user, p2_pass, p2_span = recorded_calls[1]
    assert '<draft pass="1">' in p2_user
    assert outputs[0] in p2_user
    assert p2_pass == 2
    assert p2_span == "cresmo.gap_filler.generate.pass_2"

    p3_user, p3_pass, p3_span = recorded_calls[2]
    assert '<draft pass="2">' in p3_user
    assert outputs[1] in p3_user
    assert p3_pass == 3
    assert p3_span == "cresmo.gap_filler.generate.pass_3"

    assert get_active_telemetry_pass() is None
    assert get_active_telemetry_stage() is None


def test_gap_filler_single_pass_omits_telemetry_pass_suffix(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify max_passes=1 runs without sequential pass number so observation stays cresmo.{stage}.generate."""
    from cresmo.application.ports import (
        get_active_telemetry_pass,
        resolve_llm_generation_span_name,
    )

    captured: list[tuple[int | None, str]] = []

    def _spy_transform(*_args: object, **_kwargs: object) -> str:
        captured.append((get_active_telemetry_pass(), resolve_llm_generation_span_name()))
        return "## Title\n\nBody.\n\n### Extra Info\n\n1. Item."

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = _spy_transform

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=StageFactory(settings=DefaultPipelineSettings()),
    )

    runner.execute_stage(
        "gap_filler",
        source=sample_fluid_transcript,
        context=sample_context,
        max_passes=1,
    )

    assert captured == [(None, "cresmo.gap_filler.generate")]


def test_multi_pass_injects_critique_only_on_final_pass(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify multi-pass stages inject reflection critique strictly on the final pass (ADR-046)."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    outputs = [
        "## Title\n\nPass 1.\n\n### Extra Info\n\n1. **Entity A**.",
        "## Title\n\nPass 2.\n\n### Extra Info\n\n1. **Entity A**.\n2. **Entity B**.",
        "## Title\n\nPass 3 final.\n\n### Extra Info\n\n1. **Entity A**.\n2. **Entity B**.\n3. **Entity C**.",
    ]
    prompts_seen: list[str] = []
    call_idx = 0

    def _spy_transform(prompt: object, **_kwargs: object) -> str:
        nonlocal call_idx
        prompts_seen.append(prompt.get_last_user_content())  # type: ignore[attr-defined]
        out = outputs[call_idx]
        call_idx += 1
        return out

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = _spy_transform

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=3,
    )
    candidate = generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=2,
        active_trace_id="trace_critique_3",
        critique="Add competing hypotheses and Big-Endian dates.",
    )

    assert len(prompts_seen) == 3
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" not in prompts_seen[0]
    assert "Add competing hypotheses" not in prompts_seen[0]
    assert '<draft pass="1">' in prompts_seen[1]
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" not in prompts_seen[1]
    assert '<draft pass="2">' in prompts_seen[2]
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" in prompts_seen[2]
    assert "Add competing hypotheses and Big-Endian dates." in prompts_seen[2]
    assert prompts_seen[2].find("[PREVIOUS ATTEMPT QUALITY FEEDBACK]") > prompts_seen[2].find(
        '<draft pass="2">'
    )
    assert candidate.metadata["passes_executed"] == 3
    assert candidate.metadata["is_saturated"] is False
    assert candidate.text == outputs[2]


def test_multi_pass_early_saturation_with_critique_runs_terminal_critique_pass(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify early mechanical saturation schedules a single terminal critique pass without wasting remaining passes."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.stage_registry import gap_filler_saturation_policy
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    pass1_text = (
        "## Title\n\nDraft one.\n\n### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão**."
    )
    pass2_text = (
        "## Title\n\nDraft two.\n\n### Extra Info\n\n"
        "1. **Henrique de Borgonha** e **Teresa de Leão** consolidaram o condado."
    )
    pass3_text = (
        "## Title\n\nCritique fixed final draft.\n\n### Extra Info\n\n"
        "1. **Henrique de Borgonha** e **Teresa de Leão** em 1096."
    )
    outputs = [pass1_text, pass2_text, pass3_text, "should not run pass 4", "should not run pass 5"]
    prompts_seen: list[str] = []
    call_idx = 0

    def _spy_transform(prompt: object, **_kwargs: object) -> str:
        nonlocal call_idx
        prompts_seen.append(prompt.get_last_user_content())  # type: ignore[attr-defined]
        out = outputs[call_idx]
        call_idx += 1
        return out

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = _spy_transform

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=5,
        saturation_policy=gap_filler_saturation_policy,
    )
    candidate = generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=2,
        active_trace_id="trace_critique_sat",
        critique="Fix grounding defect.",
    )

    assert len(prompts_seen) == 3
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" not in prompts_seen[0]
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" not in prompts_seen[1]
    assert '<draft pass="2">' in prompts_seen[2]
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" in prompts_seen[2]
    assert "Fix grounding defect." in prompts_seen[2]
    assert candidate.metadata["passes_executed"] == 3
    assert candidate.metadata["is_saturated"] is True
    assert candidate.text == pass3_text


def test_saturation_policy_can_halt_immediately_on_pass_1(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify saturation_policy owns halting and can break on pass 1 without waiting for pass 2."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = ["Pass 1 already SATURATED.", "Should never execute pass 2."]

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=5,
        saturation_policy=lambda current_text, _previous_text=None: "SATURATED" in current_text,
    )
    candidate = generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=1,
        active_trace_id="trace_pass1_sat",
    )

    assert mock_llm.transform.call_count == 1
    assert candidate.metadata["passes_executed"] == 1
    assert candidate.metadata["is_saturated"] is True
    assert candidate.text == "Pass 1 already SATURATED."


def test_stage_config_rejects_non_callable_saturation_policy() -> None:
    """Verify fail-fast validation when saturation_policy is not callable."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.domain.value_objects import PromptKey

    with pytest.raises(TypeError, match="saturation_policy must be callable"):
        StageConfig(
            stage_name="gap_filler",
            transform_prompt_key=PromptKey.GAP_FILLER,
            saturation_policy="not_callable",  # type: ignore[arg-type]
        )


def test_single_pass_with_critique_applies_critique_on_pass_1(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify single-pass stages (max_passes=1) still inject critique directly on Pass 1."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    prompts_seen: list[str] = []

    def _spy_transform(prompt: object, **_kwargs: object) -> str:
        prompts_seen.append(prompt.get_last_user_content())  # type: ignore[attr-defined]
        return "## Title\n\nClean prose."

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = _spy_transform

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="fluid_prose",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        max_passes=1,
    )
    generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=2,
        active_trace_id="trace_single_critique",
        critique="Remove colloquialism.",
    )

    assert len(prompts_seen) == 1
    assert "[PREVIOUS ATTEMPT QUALITY FEEDBACK]" in prompts_seen[0]
    assert "Remove colloquialism." in prompts_seen[0]
