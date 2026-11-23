"""Pure unit tests for session_mapper (SPEC-070 §2.2)."""

from __future__ import annotations

from cresmo.application.ports.telemetry import (
    PIPELINE_ROOT_SPAN_NAME,
    PIPELINE_TRACE_NAME,
    SessionTelemetrySpec,
)
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.infrastructure.adapters.telemetry.session_mapper import (
    build_propagated_trace_metadata,
    build_session_span_attributes,
    parse_session_parts,
    resolve_root_operation_name,
)


class TestSessionMapper:
    """Verify pure mapping of SessionTelemetrySpec without OTel SDK dependencies."""

    def test_parse_session_parts_standard_and_content_prefixed(self) -> None:
        assert parse_session_parts(PipelineSessionId("UC_123:vid_456")) == ("UC_123", "vid_456")
        assert parse_session_parts(PipelineSessionId("content:sandeco:ep01")) == (
            "sandeco",
            "ep01",
        )
        assert parse_session_parts(PipelineSessionId("content:vid_only")) == (
            "content",
            "vid_only",
        )

    def test_resolve_root_operation_name_enforces_adr065_separation(self) -> None:
        assert resolve_root_operation_name(None) == (PIPELINE_TRACE_NAME, PIPELINE_ROOT_SPAN_NAME)
        assert resolve_root_operation_name(PIPELINE_TRACE_NAME) == (
            PIPELINE_TRACE_NAME,
            PIPELINE_ROOT_SPAN_NAME,
        )
        assert resolve_root_operation_name("cresmo.synthesis_pipeline") == (
            "cresmo.synthesis_pipeline",
            PIPELINE_ROOT_SPAN_NAME,
        )
        assert resolve_root_operation_name("cresmo.pipeline.execution") == (
            "cresmo.pipeline.execution",
            PIPELINE_ROOT_SPAN_NAME,
        )
        assert resolve_root_operation_name("custom.trace") == ("custom.trace", "custom.trace")

    def test_build_session_span_attributes_full_parity_and_zero_duplication(self) -> None:
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("UC_econ:vid_01"),
            user_id=UserIdentity.identified(subject="fausto@cresmo.ai", provider="oauth"),
            channel_tenant_id="channel:UC_econ",
            channel_id="UC_econ",
            channel_name="Economics",
            content_id="vid_01",
            content_title="Pareto Elites",
            source="transcript",
            raw_characters=420,
            raw_words=75,
            expansion_max_passes=3,
            force_reprocess=True,
            batch_id="20261122_130000_abc123",
            video_url="https://youtube.com/watch?v=vid_01",
            publication_date="2024-05-20",
            extra_metadata={"custom_tag": "gold", "channel_id": "ignored_canonical_shadow"},
        )

        attrs, tags, input_payload = build_session_span_attributes(
            spec,
            pipeline_version="cresmo:v0.1.0",
            git_sha="abcdef1234567890",
        )

        assert attrs["langfuse.observation.type"] == "span"
        assert attrs["langfuse.session.id"] == "UC_econ:vid_01"
        assert attrs["langfuse.user.id"] == "user:oauth:fausto@cresmo.ai"
        assert attrs["langfuse.trace.name"] == PIPELINE_TRACE_NAME
        assert attrs["cresmo.pipeline.version"] == "cresmo:v0.1.0"
        assert attrs["cresmo.pipeline.git_sha"] == "abcdef12"
        assert attrs["cresmo.channel.id"] == "UC_econ"
        assert attrs["cresmo.content.id"] == "vid_01"
        assert attrs["cresmo.channel.name"] == "Economics"
        assert attrs["cresmo.content.title"] == "Pareto Elites"
        assert attrs["cresmo.tenant_id"] == "channel:UC_econ"
        assert attrs["cresmo.user.is_anonymous"] is False
        assert attrs["cresmo.user.provider"] == "oauth"
        assert attrs["cresmo.user.subject"] == "fausto@cresmo.ai"
        assert attrs["cresmo.batch_id"] == "20261122_130000_abc123"
        assert attrs["cresmo.content.source"] == "transcript"
        assert attrs["cresmo.content.word_count"] == 75
        assert attrs["cresmo.content.char_count"] == 420
        assert attrs["cresmo.content.publication_date"] == "2024-05-20"
        assert attrs["cresmo.pipeline.expansion_max_passes"] == 3
        assert attrs["cresmo.pipeline.force_reprocess"] is True
        assert attrs["cresmo.metadata.custom_tag"] == "gold"
        assert "cresmo.metadata.channel_id" not in attrs
        assert not any(k.startswith("langfuse.input.") for k in attrs)

        assert tags == [
            "Economics",
            "cresmo:v0.1.0",
            "auth:oauth",
            "git:abcdef12",
            "batch:20261122_130000_abc123",
        ]
        assert input_payload == {
            "channel_id": "UC_econ",
            "content_id": "vid_01",
            "channel_name": "Economics",
            "content_title": "Pareto Elites",
            "raw_characters": "420",
            "raw_words": "75",
            "batch_id": "20261122_130000_abc123",
            "video_url": "https://youtube.com/watch?v=vid_01",
        }

    def test_build_session_span_attributes_minimal_defaults(self) -> None:
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("sandeco:vid_min"),
            user_id=UserIdentity.anonymous(),
        )
        attrs, tags, input_payload = build_session_span_attributes(
            spec,
            pipeline_version="cresmo:v0.1.0",
            git_sha="   ",
        )
        assert attrs["cresmo.channel.id"] == "sandeco"
        assert attrs["cresmo.content.id"] == "vid_min"
        assert attrs["cresmo.channel.name"] == "sandeco"
        assert attrs["cresmo.content.title"] == "vid_min"
        assert attrs["cresmo.tenant_id"] == "channel:sandeco"
        assert "cresmo.pipeline.git_sha" not in attrs
        assert "cresmo.user.subject" not in attrs
        assert "cresmo.batch_id" not in attrs
        assert "cresmo.content.publication_date" not in attrs
        assert tags == ["sandeco", "cresmo:v0.1.0", "auth:anonymous"]
        assert "video_url" not in input_payload
        assert "batch_id" not in input_payload

    def test_build_session_span_attributes_custom_trace_name_and_blank_source(self) -> None:
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("UC_1:vid_2"),
            user_id=UserIdentity.worker(),
            trace_name="custom.eval.trace",
            source="   ",
        )
        attrs, _, _ = build_session_span_attributes(
            spec,
            pipeline_version="cresmo:v0.2.0",
        )
        assert attrs["langfuse.trace.name"] == "custom.eval.trace"
        assert "cresmo.content.source" not in attrs

    def test_build_propagated_trace_metadata_truncates_at_200_chars(self) -> None:
        long_title = "X" * 250
        meta = build_propagated_trace_metadata(
            {
                "cresmo.channel.id": "UC_1",
                "cresmo.channel.name": "Chan",
                "cresmo.content.id": "vid_1",
                "cresmo.content.title": long_title,
                "cresmo.batch_id": "",
            }
        )
        assert meta["channel_id"] == "UC_1"
        assert meta["channel_name"] == "Chan"
        assert meta["content_id"] == "vid_1"
        assert len(meta["content_title"]) == 200
        assert "batch_id" not in meta

        meta_with_batch = build_propagated_trace_metadata(
            {
                "cresmo.channel.id": "UC_1",
                "cresmo.channel.name": "Chan",
                "cresmo.content.id": "vid_1",
                "cresmo.content.title": "Short",
                "cresmo.batch_id": "B" * 210,
            }
        )
        assert meta_with_batch == {
            "channel_id": "UC_1",
            "channel_name": "Chan",
            "content_id": "vid_1",
            "content_title": "Short",
            "batch_id": "B" * 200,
        }
