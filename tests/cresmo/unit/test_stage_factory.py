"""Unit tests for StageFactory and PipelineExecutionContext (ADR-031)."""

from __future__ import annotations

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageDescriptor
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.ports import DefaultPipelineSettings
from cresmo.domain.entities import (
    FluidTranscript,
    PipelineSessionId,
    SourceTranscript,
    UserIdentity,
)
from cresmo.domain.value_objects import (
    CandidateText,
    ChannelId,
    ChannelName,
    ContentId,
    JudgeCriterion,
    PromptKey,
)


def test_pipeline_execution_context_creation() -> None:
    """Verify PipelineExecutionContext holds all execution provenance fields."""
    ctx = PipelineExecutionContext(
        session_id=PipelineSessionId("test_chan:test_vid"),
        user_identity=UserIdentity.worker(),
        channel_name=ChannelName("Test Channel"),
        content_id=ContentId("test_vid"),
        channel_id=ChannelId("UC_test123"),
    )

    assert ctx.session_id.value == "test_chan:test_vid"
    assert ctx.user_identity.is_anonymous is False
    assert ctx.channel_name.value == "Test Channel"
    assert ctx.content_id.value == "test_vid"
    assert ctx.channel_id is not None
    assert ctx.channel_id.value == "UC_test123"


def test_pipeline_execution_context_composite_creation() -> None:
    """Verify PipelineExecutionContext receives composite Channel and Content VOs (ADR-032)."""
    from cresmo.domain.value_objects import Channel, Content

    channel = Channel.from_name("Test Channel", id="UC_test123")
    content = Content.create("test_vid", title="Sample Title")
    ctx = PipelineExecutionContext(
        session_id=PipelineSessionId("test_chan:test_vid"),
        user_identity=UserIdentity.worker(),
        channel=channel,
        content=content,
    )

    assert ctx.channel == channel
    assert ctx.content == content
    assert ctx.video == content
    assert ctx.channel_name.value == "Test Channel"
    assert ctx.content_id.value == "test_vid"
    assert ctx.channel_id is not None
    assert ctx.channel_id.value == "UC_test123"


def test_stage_factory_builds_fluid_prose_descriptor() -> None:
    """Verify StageFactory produces a properly wired, stateless StageDescriptor for fluid prose."""
    settings = DefaultPipelineSettings(
        llm_temperature=0.35,
        judge_blocking=True,
        judge_max_attempts=3,
    )
    factory = StageFactory(settings=settings)

    descriptor = factory.build_stage("fluid_prose")
    assert isinstance(descriptor, StageDescriptor)
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
    source = SourceTranscript(
        content_id=ContentId("c123"),
        channel_name=ChannelName("Ch"),
        body="Verbatim source audio.",
    )
    extracted = descriptor.eval_spec.extract_source_text(source)
    assert extracted == "Verbatim source audio."

    # Verify candidate text extraction
    candidate = CandidateText("Synthesized fluid prose.", stage_name="fluid_prose")
    assert descriptor.eval_spec.candidate_extractor(candidate) == "Synthesized fluid prose."

    # Verify post processor produces FluidTranscript
    processed = descriptor.post_process(candidate, source)
    assert isinstance(processed, FluidTranscript)
    assert processed.content_id == source.content_id
    assert "Synthesized fluid prose." in processed.body


def test_stage_factory_generic_build_stage_custom_parameters() -> None:
    """Verify build_stage creates a custom StageDescriptor with injected parameters and overrides."""
    settings = DefaultPipelineSettings(
        llm_temperature=0.7,
        judge_blocking=False,
        judge_max_attempts=2,
    )
    factory = StageFactory(settings=settings)

    # Injected custom post processor and extractors
    def custom_post_processor(candidate: CandidateText, source: FluidTranscript) -> dict[str, str]:
        return {"output": candidate.text, "source_id": source.content_id.value}

    descriptor = factory.build_stage(
        stage_name="custom_analysis_stage",
        transform_prompt_key=PromptKey.RAW_INDEX_SUMMARY,
        judge_prompt_key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        required_criteria=(JudgeCriterion.INDEX_SYNTHESIS_QUALITY,),
        post_processor=custom_post_processor,
        candidate_extractor=lambda c: f"extracted:{c.text}",
        source_extractor=lambda s: f"src:{s.body}",
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

    dummy_source = FluidTranscript(
        content_id=ContentId("dummy_content"),
        channel_name=ChannelName("dummy_channel"),
        body="dummy body",
    )
    assert descriptor.eval_spec.extract_source_text(dummy_source) == "src:dummy body"

    # Validate custom post-processing
    result = descriptor.post_process(candidate, dummy_source)
    assert result == {"output": "raw response", "source_id": "dummy_content"}


def test_stage_factory_build_stage_minimal_without_criteria() -> None:
    """Verify build_stage creates a stage descriptor with no eval_spec when criteria/extractors omitted."""
    settings = DefaultPipelineSettings(
        llm_temperature=0.5,
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
    from cresmo.domain.stage_registry import StageRegistry, StageSpec

    test_stage_name = "dynamic_registered_stage"
    custom_spec = StageSpec(
        transform_prompt_key=PromptKey.FLUID_PROSE,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
    )
    StageRegistry.register(test_stage_name, custom_spec)

    factory = StageFactory(settings=DefaultPipelineSettings())
    descriptor = factory.build_stage(test_stage_name)
    assert descriptor.stage_name == test_stage_name
    assert descriptor.eval_spec is not None
    assert descriptor.eval_spec.required_criteria == (JudgeCriterion.ORALITY_REMOVAL,)
