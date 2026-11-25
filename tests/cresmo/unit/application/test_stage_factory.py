"""Unit tests for StageFactory and PipelineExecutionContext (ADR-031, ADR-074)."""

from __future__ import annotations

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
from cresmo.domain.entities import (
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.stage_registry import StageDefinition, StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    ConvergenceMode,
    JudgeCriterion,
    MediaProvenance,
    PromptKey,
    SaturationThresholds,
    StageEvaluationSpec,
    StageExecutionPolicy,
)


def test_pipeline_execution_context_creation() -> None:
    """Verify PipelineExecutionContext holds all execution provenance fields."""
    channel = Channel(name="Test Channel", id=ChannelId("UC_test123"))
    content = Content(
        id=ContentId("test_vid"), title="Test Content", session_id="test_chan:test_vid"
    )
    ctx = PipelineExecutionContext(
        user_identity=UserIdentity.worker(),
        channel=channel,
        content=content,
    )

    assert not hasattr(ctx, "session_id")
    assert ctx.content.session_id == "test_chan:test_vid"
    assert ctx.user_identity.is_anonymous is False
    assert ctx.channel.name == "Test Channel"
    assert ctx.content.id.value == "test_vid"
    assert ctx.channel.id is not None
    assert ctx.channel.id.value == "UC_test123"
    assert not hasattr(ctx, "video")
    assert not hasattr(ctx, "channel_name")
    assert not hasattr(ctx, "channel_id")
    assert not hasattr(ctx, "content_id")
    assert not hasattr(ctx, "channel_id_str")
    assert not hasattr(ctx, "content_id_str")
    assert not hasattr(ctx, "content_title")


def test_pipeline_execution_context_composite_creation() -> None:
    """Verify PipelineExecutionContext receives composite Channel and Content VOs (ADR-032)."""
    channel = Channel("Test Channel", id="UC_test123")
    content = Content("test_vid", title="Sample Title", session_id="test_chan:test_vid")
    ctx = PipelineExecutionContext(
        user_identity=UserIdentity.worker(),
        channel=channel,
        content=content,
    )

    assert ctx.channel == channel
    assert ctx.content == content
    assert ctx.channel.name == "Test Channel"
    assert ctx.content.id.value == "test_vid"
    assert ctx.channel.id is not None
    assert ctx.channel.id.value == "UC_test123"


def test_stage_factory_builds_fluid_prose_descriptor() -> None:
    """Verify StageFactory produces a properly wired, stateless StageConfig for fluid prose."""
    policy = StageExecutionPolicy(
        judge_blocking=True,
        judge_max_attempts=3,
    )
    factory = StageFactory(policy=policy)

    descriptor = factory.build_stage("fluid_prose")
    assert isinstance(descriptor, StageConfig)
    assert descriptor.stage_name == "fluid_prose"
    assert descriptor.transform_prompt_key == PromptKey.FLUID_PROSE
    assert descriptor.blocking is True
    assert descriptor.max_attempts == 3
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.max_attempts == 3
    assert JudgeCriterion.ORALITY_REMOVAL in descriptor.eval_spec.required_criteria
    assert JudgeCriterion.SEMANTIC_FAITHFULNESS in descriptor.eval_spec.required_criteria

    # Verify source text extraction via canonical domain extractor
    source = StageTranscript(
        channel=Channel(name=ChannelName("Ch")),
        provenance=MediaProvenance(),
        content=Content(id=ContentId("c123"), text="Verbatim source audio."),
    )
    from cresmo.domain.entities.transcripts import extract_source_text

    assert extract_source_text(source) == "Verbatim source audio."

    # Verify candidate text extraction
    candidate = CandidateText("Synthesized fluid prose.", stage_name="fluid_prose")
    assert descriptor.eval_spec.candidate_extractor(candidate) == "Synthesized fluid prose."

    # Verify post processor produces StageTranscript
    processed = descriptor.post_process(candidate, source)
    assert isinstance(processed, StageTranscript)
    assert processed.content.id == source.content.id
    assert "Synthesized fluid prose." in processed.content.text


def test_stage_factory_unknown_stage_raises_error() -> None:
    """Verify requesting an unknown stage raises KeyError."""
    factory = StageFactory()
    with pytest.raises(KeyError, match="nonexistent_stage"):
        factory.build_stage("nonexistent_stage")


def test_stage_factory_uses_domain_stage_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify StageFactory dynamically resolves specifications from domain StageRegistry."""
    test_stage_name = "dynamic_registered_stage"
    custom_spec = StageDefinition(
        transform_prompt_key=PromptKey.FLUID_PROSE,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
    )
    monkeypatch.setitem(StageRegistry._SPECS, test_stage_name, custom_spec)
    factory = StageFactory()
    descriptor = factory.build_stage(test_stage_name)
    assert descriptor.stage_name == test_stage_name
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.required_criteria == (JudgeCriterion.ORALITY_REMOVAL,)


def test_stage_factory_caching_and_overrides_bypass() -> None:
    """Verify StageFactory caches instances but bypasses cache when max_passes override is specified."""
    factory = StageFactory(policy=StageExecutionPolicy(expansion_max_passes=3))
    cached = factory.build_stage("gap_filler")
    assert factory._cache["gap_filler"] is cached

    overridden = factory.build_stage("gap_filler", max_passes=9)
    assert overridden is not cached
    assert overridden.max_passes == 9
    assert cached.max_passes == 3
    assert factory.build_stage("gap_filler") is cached


def test_stage_factory_default_policy_when_omitted() -> None:
    """Verify StageFactory uses canonical StageExecutionPolicy defaults when policy=None."""
    factory = StageFactory()
    descriptor = factory.build_stage("fluid_prose")
    assert descriptor.max_attempts == 2
    assert descriptor.blocking is False
    assert descriptor.max_passes == 1


def test_stage_factory_resolves_long_expander_max_passes_from_policy() -> None:
    """Verify StageFactory honors long_expander_max_passes and default budget of 7."""
    factory_default = StageFactory()
    desc_default: StageConfig[StageTranscript, StageTranscript] = factory_default.build_stage(
        "long_expander"
    )
    assert desc_default.max_passes == 7
    assert desc_default.judge_prompt_key == PromptKey.JUDGE_LONG_EXPANDER

    factory_custom = StageFactory(policy=StageExecutionPolicy(long_expander_max_passes=9))
    desc_custom: StageConfig[StageTranscript, StageTranscript] = factory_custom.build_stage(
        "long_expander"
    )
    assert desc_custom.max_passes == 9


def test_stage_factory_resolves_wide_expander_max_passes_from_policy() -> None:
    """Verify StageFactory honors expansion_max_passes for wide_expander and default budget of 5."""
    factory_default = StageFactory()
    desc_default: StageConfig[StageTranscript, StageTranscript] = factory_default.build_stage(
        "wide_expander"
    )
    assert desc_default.max_passes == 5
    assert desc_default.judge_prompt_key == PromptKey.JUDGE_WIDE_EXPANDER

    factory_custom = StageFactory(policy=StageExecutionPolicy(expansion_max_passes=8))
    desc_custom: StageConfig[StageTranscript, StageTranscript] = factory_custom.build_stage(
        "wide_expander"
    )
    assert desc_custom.max_passes == 8


def test_stage_config_explicit_eval_spec_and_metadata() -> None:
    """Verify explicit StageConfig & StageEvaluationSpec honor custom criteria and metadata."""
    custom_spec = StageEvaluationSpec(
        candidate_extractor=lambda c: f"extracted:{c.text}" if isinstance(c, CandidateText) else str(c),
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        max_attempts=5,
        metadata={"tier": "strict", "threshold": 0.85},
    )
    cfg = StageConfig[StageTranscript, StageTranscript](
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        eval_spec=custom_spec,
    )
    assert cfg.eval_spec is custom_spec
    assert cfg.eval_spec.max_attempts == 5
    assert cfg.eval_spec.metadata == {"tier": "strict", "threshold": 0.85}
    assert cfg.eval_spec.candidate_extractor("custom_raw_text") == "custom_raw_text"
    assert cfg.eval_spec.candidate_extractor(12345) == "12345"


def test_stage_factory_wires_custom_and_default_saturation_thresholds() -> None:
    """Verify StageExecutionPolicy.saturation_thresholds wires cleanly into HybridSaturationEvaluator."""
    custom_thresholds = SaturationThresholds(
        lexical_identity_threshold=0.91,
        max_lexical_word_delta=0.07,
        semantic_similarity_threshold=0.82,
        max_novel_paragraphs_for_saturation=2,
        long_unit_word_cutoff=150,
        sliding_window_sentences=5,
        sliding_window_overlap=2,
    )
    custom_factory = StageFactory(
        policy=StageExecutionPolicy(saturation_thresholds=custom_thresholds)
    )
    custom_cfg: StageConfig[StageTranscript, StageTranscript] = custom_factory.build_stage(
        "gap_filler"
    )
    assert isinstance(custom_cfg.saturation_policy, HybridSaturationEvaluator)
    assert custom_cfg.saturation_policy.thresholds == custom_thresholds

    default_factory = StageFactory()
    default_cfg: StageConfig[StageTranscript, StageTranscript] = default_factory.build_stage(
        "wide_expander"
    )
    assert isinstance(default_cfg.saturation_policy, HybridSaturationEvaluator)
    assert default_cfg.saturation_policy.thresholds == SaturationThresholds()


def test_stage_factory_max_passes_edge_cases_and_unregistered_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify NONE convergence default, policy override, and unregistered stage KeyError."""
    default_factory = StageFactory()

    overridden_cfg: StageConfig[StageTranscript, StageTranscript] = default_factory.build_stage(
        "gap_filler",
        max_passes=2,
    )
    assert overridden_cfg.max_passes == 2

    two_pass_stage = "two_pass_none_stage"
    monkeypatch.setitem(
        StageRegistry._SPECS,
        two_pass_stage,
        StageDefinition(
            transform_prompt_key=PromptKey.FLUID_PROSE,
            convergence_mode=ConvergenceMode.NONE,
        ),
    )
    none_cfg: StageConfig[StageTranscript, StageTranscript] = default_factory.build_stage(
        two_pass_stage
    )
    assert none_cfg.max_passes == 1

    with pytest.raises(KeyError, match="not_in_registry"):
        StageFactory().build_stage("not_in_registry")
