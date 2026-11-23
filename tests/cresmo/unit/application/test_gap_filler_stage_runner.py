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
from cresmo.application.pipeline.stage_descriptor import StageConfig
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

    stage_factory = StageFactory(settings=DefaultPipelineSettings(expansion_max_passes=3))

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
    """Verify gap_filler stops before max_passes when convergence saturation is detected."""
    pass1_text = (
        "## Fundação de Portugal\n\n"
        "O conde **Henrique de Borgonha** governou o território ocidental com apoio régio.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão** em 1093."
    )
    # Pass 2 returns identical content -> triggers Layer 1 lexical identity saturation
    pass2_text = pass1_text

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_text, pass2_text, "pass 3 should not be called"]

    settings = DefaultPipelineSettings(expansion_max_passes=3)
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

    stage_factory = StageFactory(settings=DefaultPipelineSettings(expansion_max_passes=3))
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
    assert [c.kwargs["trace_id"] for c in mock_llm.transform.call_args_list] == [
        "trace_critique_3_pass_1",
        "trace_critique_3_pass_2",
        "trace_critique_3_pass_3",
    ]


def test_multi_pass_early_saturation_with_critique_runs_terminal_critique_pass(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify early saturation schedules a single terminal critique pass without wasting remaining passes."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    pass1_text = (
        "## Title\n\nDraft one describing military governance in 1096.\n\n### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão**."
    )
    pass2_text = pass1_text
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
        saturation_policy=HybridSaturationEvaluator(),
    )
    with caplog.at_level("INFO"):
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

    assert any(
        r.getMessage() == "[StageRunner] Executing pass 1/5 for gap_filler..."
        for r in caplog.records
    )
    assert any(
        r.getMessage()
        == "[StageRunner] Saturation reached at pass 2/5; scheduling final critique pass."
        for r in caplog.records
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
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify Pass 1 receives source text as baseline_text and saturation_policy can halt on pass 1."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.value_objects import PromptKey
    from cresmo.domain.value_objects.convergence import SaturationReason, SaturationVerdict
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = ["Pass 1 already SATURATED.", "Should never execute pass 2."]

    recorded_calls: list[tuple[str, str, int]] = []

    def _pass1_policy(baseline_text: str, current_text: str, pass_index: int) -> SaturationVerdict:
        recorded_calls.append((baseline_text, current_text, pass_index))
        saturated = "SATURATED" in current_text
        return SaturationVerdict(
            is_saturated=saturated,
            reason=(
                SaturationReason.LEXICAL_IDENTITY if saturated else SaturationReason.NOVEL_CONTENT
            ),
            lexical_jaccard=1.0 if saturated else 0.0,
            word_delta_ratio=0.0 if saturated else 1.0,
            max_novelty=0.0 if saturated else 1.0,
            novel_paragraphs=0 if saturated else 1,
            total_paragraphs=1,
            preserve_baseline=False,
            provider="test",
        )

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=5,
        saturation_policy=_pass1_policy,
    )
    with caplog.at_level("INFO"):
        candidate = generate_stage_candidate(
            cfg,
            sample_fluid_transcript,
            context=sample_context,
            prompt_provider=JsonPromptProvider(),
            llm_port=mock_llm,
            attempt=1,
            active_trace_id="trace_pass1_sat",
        )

    assert any(
        r.getMessage()
        == "[StageRunner] Saturation reached at pass 1/5 (lexical_identity). Halting early."
        for r in caplog.records
    )
    assert recorded_calls == [
        (sample_fluid_transcript.content.text, "Pass 1 already SATURATED.", 1)
    ]
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


def test_preserve_baseline_rollback_and_saturation_history_on_explicit_sentinel_pass_2(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify <NO_NEW_GAPS/> on Pass 2 reverts candidate.text to pass1_text and records saturation_history."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.services.convergence_evaluator import NO_NEW_GAPS_SENTINEL
    from cresmo.domain.value_objects import PromptKey
    from cresmo.domain.value_objects.convergence import SaturationReason
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    pass1_text = (
        "## Fundação de Portugal\n\n"
        "O conde **Henrique de Borgonha** governou o território ocidental.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão** em 1093."
    )
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [
        pass1_text,
        NO_NEW_GAPS_SENTINEL,
        "should not execute pass 3",
    ]

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=5,
        saturation_policy=HybridSaturationEvaluator(),
    )
    candidate = generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=1,
        active_trace_id="trace_rollback",
    )

    assert mock_llm.transform.call_count == 2
    assert candidate.metadata["passes_executed"] == 2
    assert candidate.metadata["is_saturated"] is True
    assert candidate.text == pass1_text
    assert NO_NEW_GAPS_SENTINEL not in candidate.text

    history = candidate.metadata["saturation_history"]
    assert isinstance(history, list)
    assert len(history) == 2
    expected_keys = {
        "is_saturated",
        "reason",
        "lexical_jaccard",
        "word_delta_ratio",
        "max_novelty",
        "novel_paragraphs",
        "total_paragraphs",
        "preserve_baseline",
        "provider",
    }
    assert expected_keys.issubset(history[0].keys())
    assert expected_keys.issubset(history[1].keys())
    assert history[0]["pass_num"] == 1
    assert history[0]["is_saturated"] is False
    assert history[0]["reason"] == SaturationReason.NOVEL_CONTENT.value
    assert history[0]["preserve_baseline"] is False
    assert history[1]["pass_num"] == 2
    assert history[1]["is_saturated"] is True
    assert history[1]["reason"] == SaturationReason.EXPLICIT_SENTINEL.value
    assert history[1]["preserve_baseline"] is True


def test_generate_stage_candidate_invokes_saturation_span_per_pass(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify telemetry_port.start_span emits saturation span per pass (cresmo.gap_filler.saturation.pass_N)."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.application.ports.telemetry import format_stage_saturation_span_name
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.services.convergence_evaluator import NO_NEW_GAPS_SENTINEL
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
    from tests.doubles.telemetry_fake import InMemoryTelemetryPort

    pass1_text = (
        "## Fundação de Portugal\n\n"
        "O conde **Henrique de Borgonha** governou o território ocidental.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** casou com **Teresa de Leão** em 1093."
    )
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_text, NO_NEW_GAPS_SENTINEL]

    spy_telemetry = InMemoryTelemetryPort()

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=3,
        saturation_policy=HybridSaturationEvaluator(),
    )
    generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=1,
        active_trace_id="trace_sat_spans",
        telemetry_port=spy_telemetry,
    )

    assert len(spy_telemetry.spans) == 2
    assert [span.name for span in spy_telemetry.spans] == [
        format_stage_saturation_span_name("gap_filler", 1),
        format_stage_saturation_span_name("gap_filler", 2),
    ]
    assert spy_telemetry.spans[0].attributes["cresmo.pass_num"] == 1
    assert spy_telemetry.spans[1].attributes["cresmo.pass_num"] == 2
    assert spy_telemetry.spans[1].attributes["cresmo.saturation.is_saturated"] is True
    assert (
        format_stage_saturation_span_name("gap_filler", 1) == "cresmo.gap_filler.saturation.pass_1"
    )
    assert (
        format_stage_saturation_span_name("gap_filler", 2) == "cresmo.gap_filler.saturation.pass_2"
    )


def test_stage_factory_wires_hybrid_saturation_and_never_saturate() -> None:
    """Verify StageFactory binds HybridSaturationEvaluator for gap_filler and never_saturate for fluid_prose."""
    from cresmo.application.ports.embedding import TextEmbeddingPort
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.value_objects.convergence import ConvergenceMode, never_saturate

    mock_embedding_port = MagicMock(spec=TextEmbeddingPort)
    mock_embedding_port.provider_name = "gemini"

    factory = StageFactory(
        settings=DefaultPipelineSettings(),
        embedding_port=mock_embedding_port,
    )

    gap_cfg = factory.build_stage("gap_filler")
    fluid_cfg = factory.build_stage("fluid_prose")

    assert isinstance(gap_cfg.saturation_policy, HybridSaturationEvaluator)
    assert gap_cfg.saturation_policy.embedding_port is mock_embedding_port
    assert gap_cfg.saturation_policy.mode is ConvergenceMode.HYBRID_SEMANTIC
    assert fluid_cfg.saturation_policy is never_saturate


def test_pass1_semantic_plateau_keeps_current_text_instead_of_reverting_to_source(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify Pass 1 SEMANTIC_PLATEAU keeps candidate Extra Info output rather than reverting to fluid source."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.application.ports.embedding import TextEmbeddingPort
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.value_objects import PromptKey
    from cresmo.domain.value_objects.convergence import SaturationReason
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    pass1_gap_output = (
        "## Origens\n\n"
        f"{sample_fluid_transcript.content.text}\n\n"
        "### Extra Info\n"
        "1. First grounded historical note.\n"
        "2. Second grounded historical note."
    )
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = pass1_gap_output

    # Return identical unit vectors so Layer 2 returns SEMANTIC_PLATEAU on Pass 1
    mock_emb = MagicMock(spec=TextEmbeddingPort)
    mock_emb.provider_name = "gemini"
    mock_emb.embed_batch.return_value = [[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]]

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=5,
        saturation_policy=HybridSaturationEvaluator(embedding_port=mock_emb),
    )
    candidate = generate_stage_candidate(
        cfg,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm,
        attempt=1,
        active_trace_id="trace_pass1_plateau",
    )

    assert mock_llm.transform.call_count == 1
    assert candidate.metadata["passes_executed"] == 1
    assert candidate.metadata["is_saturated"] is True
    assert (
        candidate.metadata["saturation_history"][0]["reason"]
        == SaturationReason.SEMANTIC_PLATEAU.value
    )
    assert candidate.metadata["saturation_history"][0]["preserve_baseline"] is False
    assert candidate.text == pass1_gap_output
    assert "### Extra Info" in candidate.text


def test_draft_fallback_block_instructs_no_new_gaps_sentinel_not_copy_back(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify fallback REFINE draft injection emits <NO_NEW_GAPS/> instruction, never copy-back."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.domain.services.convergence_evaluator import NO_NEW_GAPS_SENTINEL
    from cresmo.domain.value_objects import ChatPrompt, PromptKey

    mock_provider = MagicMock()
    mock_provider.get_prompt.return_value = ChatPrompt.from_system_and_user(
        system="System prompt",
        user="Remote prompt template without draft placeholder.",
    )
    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=3,
    )

    prompt = cfg.build_transform_prompt(
        mock_provider,
        sample_fluid_transcript,
        context=sample_context,
        pass_num=2,
        total_passes=3,
        prev_pass_num=1,
        current_text="## Draft\n\nExisting pass 1 draft.",
    )
    rendered = prompt.get_last_user_content()

    assert NO_NEW_GAPS_SENTINEL in rendered
    assert "return the draft unchanged" not in rendered.lower()


def test_generate_stage_candidate_rejects_non_verdict_saturation_policy_return(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify generate_stage_candidate fails fast when saturation_policy returns non-SaturationVerdict."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import generate_stage_candidate
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "## Draft\n\nCandidate text."

    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="gap_filler",
        transform_prompt_key=PromptKey.GAP_FILLER,
        max_passes=3,
        saturation_policy=lambda _b, _c, _p: True,  # type: ignore[arg-type,return-value]
    )

    with pytest.raises(
        TypeError,
        match=r"^StageConfig\.saturation_policy must return SaturationVerdict, got bool\.$",
    ):
        generate_stage_candidate(
            cfg,
            sample_fluid_transcript,
            context=sample_context,
            prompt_provider=JsonPromptProvider(),
            llm_port=mock_llm,
            attempt=1,
            active_trace_id="trace_bad_verdict",
        )


def test_stage_execution_pass_context_and_boundary_contracts(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify _build_pass_prompt_context and generate_stage_candidate boundary invariants."""
    from cresmo.application.pipeline.stage_descriptor import StageConfig
    from cresmo.application.pipeline.stage_execution import (
        _build_pass_prompt_context,
        generate_stage_candidate,
    )
    from cresmo.domain.value_objects import ChatPrompt, PromptKey
    from cresmo.domain.value_objects.convergence import SaturationReason, SaturationVerdict
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    # 1. Exact prompt context keys and prev_pass_num arithmetic
    assert _build_pass_prompt_context(
        pass_index=3, max_passes=5, is_multi_pass=True, draft_text="prev draft"
    ) == {
        "pass_num": 3,
        "total_passes": 5,
        "prev_pass_num": 2,
        "current_text": "prev draft",
    }
    assert (
        _build_pass_prompt_context(pass_index=1, max_passes=1, is_multi_pass=False, draft_text=None)
        == {}
    )

    # 2. stage_config missing max_passes attribute defaults safely to single pass (1)
    class ConfigWithoutMaxPasses:
        stage_name = "fluid_prose"
        temperature = None

        def build_transform_prompt(
            self, _provider: object, _source: object, **_kwargs: object
        ) -> ChatPrompt:
            return ChatPrompt.from_system_and_user(system="sys", user="usr")

    mock_llm_default = MagicMock(spec=LLMTransformationPort)
    mock_llm_default.transform.return_value = "Single pass default."
    cand_default = generate_stage_candidate(
        ConfigWithoutMaxPasses(),  # type: ignore[arg-type]
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=NoOpPromptProviderPort(),
        llm_port=mock_llm_default,
        attempt=1,
        active_trace_id="trace_no_attr",
    )
    assert mock_llm_default.transform.call_count == 1
    assert "passes_executed" not in cand_default.metadata

    # 3. max_passes=0 clamps to 1 and runs single pass
    mock_llm_zero = MagicMock(spec=LLMTransformationPort)
    mock_llm_zero.transform.return_value = "Clamped single pass."
    cfg_zero = StageConfig[StageTranscript, StageTranscript](
        stage_name="fluid_prose",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        max_passes=0,
    )
    cand_zero = generate_stage_candidate(
        cfg_zero,
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=NoOpPromptProviderPort(),
        llm_port=mock_llm_zero,
        attempt=1,
        active_trace_id="trace_zero_passes",
    )
    assert mock_llm_zero.transform.call_count == 1
    assert cand_zero.text == "Clamped single pass."
    assert "passes_executed" not in cand_zero.metadata

    # 4. max_passes=2 activates multi-pass, forwards total_passes=2, and saturating on final pass with critique marks is_saturated=True
    observed_prompt_kwargs: list[dict[str, object]] = []

    class SpyTwoPassConfig:
        stage_name = "gap_filler"
        temperature = None
        max_passes = 2

        def build_transform_prompt(
            self, _provider: object, _source: object, **kwargs: object
        ) -> ChatPrompt:
            observed_prompt_kwargs.append(dict(kwargs))
            return ChatPrompt.from_system_and_user(system="sys", user="usr")

        def saturation_policy(
            self, _baseline: str, _current: str, pass_index: int
        ) -> SaturationVerdict:
            saturated = pass_index == 2
            return SaturationVerdict(
                is_saturated=saturated,
                reason=(
                    SaturationReason.LEXICAL_IDENTITY
                    if saturated
                    else SaturationReason.NOVEL_CONTENT
                ),
                lexical_jaccard=1.0 if saturated else 0.1,
                word_delta_ratio=0.0 if saturated else 0.5,
                max_novelty=0.0 if saturated else 0.9,
                novel_paragraphs=0 if saturated else 1,
                total_paragraphs=1,
                preserve_baseline=False,
                provider="test",
            )

    mock_llm_two = MagicMock(spec=LLMTransformationPort)
    mock_llm_two.transform.side_effect = ["Pass 1 text.", "Pass 2 saturated text."]
    cand_two = generate_stage_candidate(
        SpyTwoPassConfig(),  # type: ignore[arg-type]
        sample_fluid_transcript,
        context=sample_context,
        prompt_provider=JsonPromptProvider(),
        llm_port=mock_llm_two,
        attempt=2,
        active_trace_id="trace_two_passes",
        critique="Address residual gaps.",
    )
    assert mock_llm_two.transform.call_count == 2
    assert observed_prompt_kwargs[0]["pass_num"] == 1
    assert observed_prompt_kwargs[0]["total_passes"] == 2
    assert observed_prompt_kwargs[1]["pass_num"] == 2
    assert observed_prompt_kwargs[1]["total_passes"] == 2
    assert observed_prompt_kwargs[1]["prev_pass_num"] == 1
    assert cand_two.metadata["passes_executed"] == 2
    assert cand_two.metadata["is_saturated"] is True


def test_long_expander_reuses_stage_agnostic_build_refine_and_sentinel_stop(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify long_expander runs BUILD/REFINE + <NO_NEW_GAPS/> early exit via StageFactory."""
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    source_gap = StageTranscript(
        channel=sample_fluid_transcript.channel,
        provenance=sample_fluid_transcript.provenance,
        content=Content(
            id=sample_fluid_transcript.content.id,
            title="Fundação de Portugal",
            text=(
                "## O Condado Portucalense\n\n"
                "Prosa densa expandida na fase de preenchimento de lacunas.\n\n"
                "### Extra Info\n\n"
                "1. Em 1096 **Henrique de Borgonha** recebeu o Condado Portucalense."
            ),
        ),
        pass_count=2,
    )
    pass1_long = (
        "## Estruturas Fiscais e Continuidade Ibérica\n\n"
        "O Condado Portucalense herdou estruturas municipais romanas e redes paroquiais suevas.\n\n"
        "### Extra Info\n\n"
        "1. Os forais de 1096 preservaram costumes fiscais leoneses e moçárabes."
    )
    pass2_long = (
        "## Estruturas Fiscais e Continuidade Ibérica\n\n"
        "O Condado Portucalense herdou estruturas municipais romanas, redes paroquiais suevas "
        "e circuitos atlânticos anteriores às cruzadas.\n\n"
        "### Extra Info\n\n"
        "1. Os forais de 1096 preservaram costumes fiscais leoneses e moçárabes.\n"
        "2. O porto do Porto integrava rotas marítimas desde a antiguidade tardia."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_long, pass2_long, "<NO_NEW_GAPS/>"]

    stage_factory = StageFactory(settings=DefaultPipelineSettings(long_expander_max_passes=7))
    long_descriptor: StageConfig[StageTranscript, StageTranscript] = stage_factory.build_stage(
        "long_expander"
    )
    assert long_descriptor.max_passes == 7
    assert long_descriptor.transform_prompt_key is PromptKey.LONG_EXPANDER

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=JsonPromptProvider(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result: StageTranscript = runner.execute_stage(
        "long_expander",
        source=source_gap,
        context=sample_context,
    )

    assert isinstance(result, StageTranscript)
    assert mock_llm.transform.call_count == 3
    assert result.pass_count == 3
    assert "circuitos atlânticos" in result.content.text
    assert "antiguidade tardia" in result.content.text
    pass1_call_user = mock_llm.transform.call_args_list[0].kwargs["prompt"].get_last_user_content()
    pass2_call_user = mock_llm.transform.call_args_list[1].kwargs["prompt"].get_last_user_content()
    assert "<draft" not in pass1_call_user
    assert '<draft pass="1">' in pass2_call_user


def test_wide_expander_reuses_stage_agnostic_build_refine_and_sentinel_stop(
    sample_context: PipelineExecutionContext,
    sample_fluid_transcript: StageTranscript,
) -> None:
    """Verify wide_expander runs BUILD/REFINE + <NO_NEW_GAPS/> early exit via StageFactory."""
    from cresmo.domain.value_objects import PromptKey
    from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

    source_long = StageTranscript(
        channel=sample_fluid_transcript.channel,
        provenance=sample_fluid_transcript.provenance,
        content=Content(
            id=sample_fluid_transcript.content.id,
            title="Crise do Século XVII",
            text=(
                "## Estruturas Fiscais de Longa Duração\n\n"
                "Prosa densa expandida na fase longitudinal.\n\n"
                "### Extra Info\n\n"
                "1. Em 1640 a crise monetária ibérica coincidiu com retração agrária."
            ),
        ),
        pass_count=3,
    )
    pass1_wide = (
        "## Redes Sincrônicas da Prata e Paralelismos Agrários\n\n"
        "A retração monetária de 1640 conectou Potosí, Sevilha e Cantão pela circulação de prata.\n\n"
        "### Extra Info\n\n"
        "1. O Galeão de Manila integrou os mercados hispânico e Ming entre 1571 e 1640."
    )
    pass2_wide = (
        "## Redes Sincrônicas da Prata e Paralelismos Agrários\n\n"
        "A retração monetária de 1640 conectou Potosí, Sevilha e Cantão pela circulação de prata, "
        "enquanto Tokugawa restringiu o comércio externo no mesmo decênio.\n\n"
        "### Extra Info\n\n"
        "1. O Galeão de Manila integrou os mercados hispânico e Ming entre 1571 e 1640.\n"
        "2. No Japão Tokugawa, o decreto Sakoku de 1639 coincidiu com reordenação fiscal autônoma."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [pass1_wide, pass2_wide, "<NO_NEW_GAPS/>"]

    stage_factory = StageFactory(settings=DefaultPipelineSettings(expansion_max_passes=5))
    wide_descriptor: StageConfig[StageTranscript, StageTranscript] = stage_factory.build_stage(
        "wide_expander"
    )
    assert wide_descriptor.max_passes == 5
    assert wide_descriptor.transform_prompt_key is PromptKey.WIDE_EXPANDER

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=JsonPromptProvider(),
        llm_transformation_port=mock_llm,
        stage_factory=stage_factory,
    )

    result: StageTranscript = runner.execute_stage(
        "wide_expander",
        source=source_long,
        context=sample_context,
    )

    assert isinstance(result, StageTranscript)
    assert mock_llm.transform.call_count == 3
    assert result.pass_count == 3
    assert "Sakoku" in result.content.text
    assert "Potosí" in result.content.text
    pass1_call_user = mock_llm.transform.call_args_list[0].kwargs["prompt"].get_last_user_content()
    pass2_call_user = mock_llm.transform.call_args_list[1].kwargs["prompt"].get_last_user_content()
    assert "<draft" not in pass1_call_user
    assert '<draft pass="1">' in pass2_call_user
