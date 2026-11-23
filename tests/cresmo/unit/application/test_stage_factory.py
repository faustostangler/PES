"""Unit tests for StageFactory and PipelineExecutionContext (ADR-031)."""

from __future__ import annotations

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.ports import DefaultPipelineSettings
from cresmo.domain.entities import (
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    JudgeCriterion,
    MediaProvenance,
    PromptKey,
)


def test_pipeline_execution_context_creation() -> None:
    """Verify PipelineExecutionContext holds all execution provenance fields."""
    channel = Channel(name="Test Channel", id=ChannelId("UC_test123"))
    content = Content.create(
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
    channel = Channel.from_name("Test Channel", id="UC_test123")
    content = Content.create("test_vid", title="Sample Title", session_id="test_chan:test_vid")
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
    settings = DefaultPipelineSettings(
        llm_synthesis_temperature=0.35,
        judge_blocking=True,
        judge_max_attempts=3,
    )
    factory = StageFactory(settings=settings)

    descriptor = factory.build_stage("fluid_prose")
    assert isinstance(descriptor, StageConfig)
    assert descriptor.stage_name == "fluid_prose"
    assert descriptor.transform_prompt_key == PromptKey.FLUID_PROSE
    assert descriptor.temperature == 0.35
    assert descriptor.blocking is True
    assert descriptor.max_attempts == 3
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.max_attempts == 3
    assert JudgeCriterion.ORALITY_REMOVAL in descriptor.eval_spec.required_criteria
    assert JudgeCriterion.SEMANTIC_FAITHFULNESS in descriptor.eval_spec.required_criteria

    # Verify callable interface returns cached instance
    assert factory("fluid_prose") is descriptor

    # Verify source text extraction
    source = StageTranscript(
        channel=Channel(name=ChannelName("Ch")),
        provenance=MediaProvenance.empty(),
        content=Content(id=ContentId("c123"), text="Verbatim source audio."),
    )
    extracted = descriptor.eval_spec.extract_source_text(source)
    assert extracted == "Verbatim source audio."

    # Verify candidate text extraction
    candidate = CandidateText("Synthesized fluid prose.", stage_name="fluid_prose")
    assert descriptor.eval_spec.candidate_extractor(candidate) == "Synthesized fluid prose."

    # Verify post processor produces StageTranscript
    processed = descriptor.post_process(candidate, source)
    assert isinstance(processed, StageTranscript)
    assert processed.content.id == source.content.id
    assert "Synthesized fluid prose." in processed.content.text


def test_stage_factory_generic_build_stage_custom_parameters() -> None:
    """Verify build_stage creates a custom StageConfig with injected parameters and overrides."""
    settings = DefaultPipelineSettings(
        llm_synthesis_temperature=0.7,
        judge_blocking=False,
        judge_max_attempts=2,
    )
    factory = StageFactory(settings=settings)

    # Injected custom post processor and extractors
    def custom_post_processor(candidate: CandidateText, source: StageTranscript) -> dict[str, str]:
        return {"output": candidate.text, "source_id": source.content.id.value}

    descriptor = factory.build_stage(
        stage_name="custom_analysis_stage",
        transform_prompt_key=PromptKey.RAW_INDEX_SUMMARY,
        judge_prompt_key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
        post_processor=custom_post_processor,
        candidate_extractor=lambda c: f"extracted:{c.text}",
        source_extractor=lambda s: f"src:{s.content.text}",
        temperature=0.15,
        max_attempts=4,
        blocking=True,
    )

    assert descriptor.stage_name == "custom_analysis_stage"
    assert descriptor.transform_prompt_key == PromptKey.RAW_INDEX_SUMMARY
    assert descriptor.judge_prompt_key == PromptKey.JUDGE_RAW_INDEX_SUMMARY
    assert descriptor.temperature == 0.15
    assert descriptor.max_attempts == 4
    assert descriptor.blocking is True

    # Validate dynamic evaluation spec
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.max_attempts == 4
    assert descriptor.eval_spec.required_criteria == (JudgeCriterion.INDEX_SYNTHESIS_QUALITY,)

    # Validate custom extractors
    candidate = CandidateText("raw response", stage_name="custom_analysis_stage")
    assert descriptor.eval_spec.candidate_extractor(candidate) == "extracted:raw response"

    dummy_source = StageTranscript(
        channel=Channel(name=ChannelName("dummy_channel")),
        provenance=MediaProvenance.empty(),
        content=Content(id=ContentId("dummy_content"), text="dummy body"),
    )
    assert descriptor.eval_spec.extract_source_text(dummy_source) == "src:dummy body"

    # Validate custom post-processing
    result = descriptor.post_process(candidate, dummy_source)
    assert result == {"output": "raw response", "source_id": "dummy_content"}


def test_stage_factory_build_stage_minimal_without_criteria() -> None:
    """Verify build_stage creates a stage descriptor with no eval_spec when criteria/extractors omitted."""
    settings = DefaultPipelineSettings(
        llm_synthesis_temperature=0.5,
        judge_blocking=False,
        judge_max_attempts=1,
    )
    factory = StageFactory(settings=settings)

    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
    )

    assert descriptor.stage_name == "minimal_stage"
    assert descriptor.transform_prompt_key == PromptKey.FLUID_PROSE
    assert descriptor.eval_spec is None
    assert descriptor.temperature == 0.5
    assert descriptor.max_attempts == 1
    assert descriptor.blocking is False


def test_stage_factory_create_stage_alias() -> None:
    """Verify create_stage and __call__ are exact aliases for build_stage."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    assert factory.create_stage == factory.build_stage
    assert factory("fluid_prose") == factory.build_stage("fluid_prose")


def test_stage_factory_unknown_stage_raises_error() -> None:
    """Verify requesting an unknown stage with no prompt key raises ValueError."""
    import pytest

    factory = StageFactory(settings=DefaultPipelineSettings())
    with pytest.raises(ValueError, match="Unknown stage 'nonexistent_stage'"):
        factory.build_stage("nonexistent_stage")


def test_stage_factory_uses_domain_stage_registry() -> None:
    """Verify StageFactory dynamically resolves specifications from domain StageRegistry."""
    from cresmo.domain.stage_registry import StageDefinition, StageRegistry

    test_stage_name = "dynamic_registered_stage"
    custom_spec = StageDefinition(
        transform_prompt_key=PromptKey.FLUID_PROSE,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
    )
    StageRegistry.register(test_stage_name, custom_spec)

    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(test_stage_name)
    assert descriptor.stage_name == test_stage_name
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.required_criteria == (JudgeCriterion.ORALITY_REMOVAL,)


def test_stage_factory_caching_and_overrides_bypass() -> None:
    """Verify StageFactory caches instances but bypasses cache when overrides are specified."""
    settings = DefaultPipelineSettings(llm_synthesis_temperature=0.35)
    factory = StageFactory(settings=settings)
    cached = factory.build_stage("fluid_prose")
    assert factory._cache["fluid_prose"] is cached

    # Calling with override must bypass cache and return new descriptor with overridden value
    overridden = factory.build_stage("fluid_prose", temperature=0.99)
    assert overridden is not cached
    assert overridden.temperature == 0.99
    assert cached.temperature == 0.35
    assert factory.build_stage("fluid_prose") is cached


def test_stage_factory_convention_over_configuration_prompt_key() -> None:
    """Verify stage_name converts via convention to PromptKey when unregistered."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage("atomic_inventory")
    assert descriptor.transform_prompt_key == PromptKey.ATOMIC_INVENTORY
    assert descriptor.stage_name == "atomic_inventory"


def test_stage_factory_settings_defaults_fallback() -> None:
    """Verify fallback defaults when settings lacks attributes."""

    class BareSettings:
        pass

    factory = StageFactory(settings=BareSettings())  # type: ignore[arg-type]
    descriptor = factory.build_stage("atomic_inventory")
    assert descriptor.temperature is None
    assert descriptor.max_attempts == 2
    assert descriptor.blocking is False


def test_stage_factory_resolves_long_expander_max_passes_from_settings() -> None:
    """Verify StageFactory honors long_expander_max_passes and default budget of 7."""
    factory_default = StageFactory(settings=DefaultPipelineSettings())
    desc_default: StageConfig[StageTranscript, StageTranscript] = factory_default.build_stage(
        "long_expander"
    )
    assert desc_default.max_passes == 7
    assert desc_default.judge_prompt_key == PromptKey.JUDGE_LONG_EXPANDER

    factory_custom = StageFactory(settings=DefaultPipelineSettings(long_expander_max_passes=9))
    desc_custom: StageConfig[StageTranscript, StageTranscript] = factory_custom.build_stage(
        "long_expander"
    )
    assert desc_custom.max_passes == 9


def test_stage_factory_resolves_wide_expander_max_passes_from_settings() -> None:
    """Verify StageFactory honors expansion_max_passes for wide_expander and default budget of 5."""
    factory_default = StageFactory(settings=DefaultPipelineSettings())
    desc_default: StageConfig[StageTranscript, StageTranscript] = factory_default.build_stage(
        "wide_expander"
    )
    assert desc_default.max_passes == 5
    assert desc_default.judge_prompt_key == PromptKey.JUDGE_WIDE_EXPANDER

    factory_custom = StageFactory(settings=DefaultPipelineSettings(expansion_max_passes=8))
    desc_custom: StageConfig[StageTranscript, StageTranscript] = factory_custom.build_stage(
        "wide_expander"
    )
    assert desc_custom.max_passes == 8


def test_stage_factory_explicit_eval_spec_passed() -> None:
    """Verify explicit eval_spec is respected directly."""
    from cresmo.domain.value_objects import StageEvaluationSpec

    custom_spec = StageEvaluationSpec(
        candidate_extractor=lambda c: "custom_candidate",
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        max_attempts=5,
    )
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        eval_spec=custom_spec,
    )
    assert descriptor.eval_spec is custom_spec
    assert descriptor.eval_spec.max_attempts == 5


def test_stage_factory_candidate_extractor_fallback_non_candidate_text() -> None:
    """Verify default candidate extractor converts non-CandidateText via str()."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
    )
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.candidate_extractor("custom_raw_text") == "custom_raw_text"
    assert descriptor.eval_spec.candidate_extractor(12345) == "12345"


def test_stage_factory_eval_metadata_explicit() -> None:
    """Verify explicit eval_metadata is passed to StageEvaluationSpec."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        eval_metadata={"tier": "strict", "threshold": 0.85},
    )
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.metadata == {"tier": "strict", "threshold": 0.85}


def test_stage_factory_eval_spec_created_with_only_candidate_extractor() -> None:
    """Verify StageEvaluationSpec is created when only candidate_extractor is provided."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        candidate_extractor=lambda c: "only_candidate",
    )
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.candidate_extractor("test") == "only_candidate"


def test_stage_factory_eval_spec_created_with_only_source_extractor() -> None:
    """Verify StageEvaluationSpec is created when only source_extractor is provided."""
    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(
        stage_name="minimal_stage",
        transform_prompt_key=PromptKey.FLUID_PROSE,
        source_extractor=lambda s: "only_source",
    )
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.extract_source_text("dummy") == "only_source"


def test_stage_factory_wires_custom_and_default_saturation_thresholds() -> None:
    """Verify _build_saturation_thresholds maps all 7 settings fields and safe fallbacks."""
    from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
    from cresmo.domain.value_objects import SaturationThresholds

    class CustomSaturationSettings(DefaultPipelineSettings):
        saturation_lexical_threshold: float = 0.91
        saturation_max_word_delta: float = 0.07
        saturation_semantic_threshold: float = 0.82
        saturation_max_novel_paragraphs: int = 2
        saturation_long_unit_word_cutoff: int = 150
        saturation_sliding_window_sentences: int = 5
        saturation_sliding_window_overlap: int = 2

    class BareSettings:
        pass

    custom_factory = StageFactory(settings=CustomSaturationSettings())
    custom_cfg: StageConfig[StageTranscript, StageTranscript] = custom_factory.build_stage(
        "gap_filler"
    )
    assert isinstance(custom_cfg.saturation_policy, HybridSaturationEvaluator)
    assert custom_cfg.saturation_policy.thresholds == SaturationThresholds(
        lexical_identity_threshold=0.91,
        max_lexical_word_delta=0.07,
        semantic_similarity_threshold=0.82,
        max_novel_paragraphs_for_saturation=2,
        long_unit_word_cutoff=150,
        sliding_window_sentences=5,
        sliding_window_overlap=2,
    )

    bare_factory = StageFactory(settings=BareSettings())  # type: ignore[arg-type]
    bare_cfg: StageConfig[StageTranscript, StageTranscript] = bare_factory.build_stage(
        "wide_expander"
    )
    assert isinstance(bare_cfg.saturation_policy, HybridSaturationEvaluator)
    assert bare_cfg.saturation_policy.thresholds == SaturationThresholds(
        lexical_identity_threshold=0.95,
        max_lexical_word_delta=0.03,
        semantic_similarity_threshold=0.88,
        max_novel_paragraphs_for_saturation=0,
        long_unit_word_cutoff=120,
        sliding_window_sentences=3,
        sliding_window_overlap=1,
    )


def test_stage_factory_max_passes_edge_cases_and_saturation_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify bool pass guards, unregistered fallback, NONE multi-pass, and policy override."""
    from cresmo.domain.stage_registry import StageDefinition, StageRegistry
    from cresmo.domain.value_objects import ConvergenceMode, SaturationReason, SaturationVerdict

    class BareSettings:
        pass

    class BoolPassSettings(DefaultPipelineSettings):
        long_expander_max_passes: int = True
        expansion_max_passes: int = True

    bare_factory = StageFactory(settings=BareSettings())  # type: ignore[arg-type]
    bare_long: StageConfig[StageTranscript, StageTranscript] = bare_factory.build_stage(
        "long_expander"
    )
    bare_wide: StageConfig[StageTranscript, StageTranscript] = bare_factory.build_stage(
        "wide_expander"
    )
    assert bare_long.max_passes == 7
    assert bare_wide.max_passes == 5

    bool_factory = StageFactory(settings=BoolPassSettings())
    bool_long: StageConfig[StageTranscript, StageTranscript] = bool_factory.build_stage(
        "long_expander"
    )
    bool_wide: StageConfig[StageTranscript, StageTranscript] = bool_factory.build_stage(
        "wide_expander"
    )
    assert bool_long.max_passes == 7
    assert bool_wide.max_passes == 5

    # Explicit saturation_policy override must be preserved verbatim
    def custom_policy(_baseline: str, _current: str, _pass_index: int) -> SaturationVerdict:
        return SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.0,
            word_delta_ratio=1.0,
        )

    overridden_cfg: StageConfig[StageTranscript, StageTranscript] = bool_factory.build_stage(
        "gap_filler",
        saturation_policy=custom_policy,
    )
    assert overridden_cfg.saturation_policy is custom_policy

    # ConvergenceMode.NONE stage with max_passes=2 must preserve max_passes=2 (not clamp to 1)
    two_pass_stage = "two_pass_none_stage"
    StageRegistry.register(
        two_pass_stage,
        StageDefinition(
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_passes=2,
            convergence_mode=ConvergenceMode.NONE,
        ),
    )
    try:
        none_cfg: StageConfig[StageTranscript, StageTranscript] = bare_factory.build_stage(
            two_pass_stage
        )
        assert none_cfg.max_passes == 2
    finally:
        StageRegistry._SPECS.pop(two_pass_stage, None)

    # Defensive fallback=7 when long_expander is absent from StageRegistry and settings
    monkeypatch.setattr(StageRegistry, "contains", lambda _name: False)
    unregistered_long: StageConfig[StageTranscript, StageTranscript] = StageFactory(
        settings=BareSettings()  # type: ignore[arg-type]
    ).build_stage("long_expander")
    assert unregistered_long.max_passes == 7
