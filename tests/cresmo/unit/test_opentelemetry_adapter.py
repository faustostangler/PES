"""Unit tests for OpenTelemetry Semantic Conventions and TelemetryPort implementations.

Conforms to ADR-016:
    - Verifies PipelineSessionId and ChannelTenantId Value Objects enforce strict domain invariants.
    - Verifies OpenTelemetryAdapter sets root attributes: langfuse.session.id, langfuse.user.id.
    - Verifies nested stage spans maintain OpenTelemetry trace hierarchy.
    - Verifies judge friction ratio calculation and score recording.
    - Verifies NoOpTelemetryAdapter executes gracefully when observability is offline (ADR-014).
"""

from __future__ import annotations

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from cresmo.application.ports import TelemetryPort
from cresmo.domain.entities import (
    ChannelTenantId,
    ContentId,
    JudgeFrictionMetric,
    PipelineSessionId,
)
from cresmo.infrastructure.adapters.opentelemetry_adapter import (
    NoOpTelemetryAdapter,
    OpenTelemetryAdapter,
)


class TestTelemetryValueObjects:
    """Test domain value objects governing telemetry identity and clinical metrics."""

    def test_pipeline_session_id_valid(self) -> None:
        session_id = PipelineSessionId.create(channel="sandeco", content_id="yt_12345678")
        assert session_id.value == "content:sandeco:yt_12345678"
        assert session_id.channel_name == "sandeco"
        assert session_id.content_id == "yt_12345678"

    def test_pipeline_session_id_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            PipelineSessionId(value="")

        with pytest.raises(ValueError, match="Invalid PipelineSessionId format"):
            PipelineSessionId(value="invalid_format_without_colons")

    def test_channel_tenant_id_valid(self) -> None:
        tenant = ChannelTenantId.create("sandeco")
        assert tenant.value == "channel:sandeco"
        assert tenant.channel_name == "sandeco"

    def test_channel_tenant_id_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            ChannelTenantId(value="")

        with pytest.raises(ValueError, match="Invalid ChannelTenantId format"):
            ChannelTenantId(value="not_prefixed")

    def test_judge_friction_metric_calculation(self) -> None:
        # First iteration pass -> 0.0 friction
        m1 = JudgeFrictionMetric(iterations=1, max_iterations=3, verdict="PASS")
        assert m1.friction_ratio == 0.0

        # One retry before pass -> 0.5 friction
        m2 = JudgeFrictionMetric(iterations=2, max_iterations=3, verdict="PASS")
        assert m2.friction_ratio == 0.5

        # All retries exhausted -> 1.0 friction
        m3 = JudgeFrictionMetric(iterations=3, max_iterations=3, verdict="NEEDS_REWRITE")
        assert m3.friction_ratio == 1.0

    def test_judge_friction_metric_invariants(self) -> None:
        with pytest.raises(ValueError, match="iterations must be >= 1"):
            JudgeFrictionMetric(iterations=0, max_iterations=3, verdict="PASS")

        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            JudgeFrictionMetric(iterations=1, max_iterations=0, verdict="PASS")


class TestOpenTelemetryAdapter:
    """Test OpenTelemetryAdapter implementation conforming to ADR-016."""

    @pytest.fixture
    def otel_setup(self) -> tuple[OpenTelemetryAdapter, InMemorySpanExporter]:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)
        return adapter, exporter

    def test_implements_telemetry_port(
        self, otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter]
    ) -> None:
        adapter, _ = otel_setup
        assert isinstance(adapter, TelemetryPort)

    def test_pipeline_session_and_stage_spans(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_test_123")
        user_id = ChannelTenantId.create("sandeco")

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user_id,
            metadata={"source": "cli"},
        ):
            with adapter.start_stage_span("stage1_raw_indexing", attributes={"step": 1}):
                pass
            with adapter.start_stage_span("stage2_fluid_prose", attributes={"step": 2}):
                pass

        spans = exporter.get_finished_spans()
        assert len(spans) == 3

        # Spans finish from inside out: stage1, stage2, then root pipeline
        stage1_span = next(s for s in spans if s.name == "cresmo.stage.stage1_raw_indexing")
        stage2_span = next(s for s in spans if s.name == "cresmo.stage.stage2_fluid_prose")
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")

        # Root span must have official Langfuse OTel attributes
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "content:sandeco:vid_test_123"
        assert root_span.attributes["langfuse.user.id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.content_id"] == "vid_test_123"
        assert root_span.attributes["cresmo.channel"] == "sandeco"
        assert root_span.attributes["cresmo.metadata.source"] == "cli"

        # Child spans share trace_id
        assert stage1_span.context is not None
        assert stage2_span.context is not None
        assert root_span.context is not None
        assert stage1_span.parent is not None
        assert stage1_span.context.trace_id == root_span.context.trace_id
        assert stage2_span.context.trace_id == root_span.context.trace_id
        assert stage1_span.parent.span_id == root_span.context.span_id

    def test_record_judge_evaluation(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_judge_01")
        user_id = ChannelTenantId.create("sandeco")

        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            adapter.record_judge_evaluation(
                session_id=session_id,
                content_id=ContentId("vid_judge_01"),
                iteration=2,
                max_iterations=3,
                verdict="PASS",
            )

        root_span = next(
            s for s in exporter.get_finished_spans() if s.name == "cresmo.pipeline.execution"
        )
        assert len(root_span.events) == 1
        event = root_span.events[0]
        assert event.name == "judge_evaluation"
        assert event.attributes is not None
        assert event.attributes["judge.friction_ratio"] == 0.5
        assert event.attributes["judge.verdict"] == "PASS"

    def test_record_session_coherence(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_coherence_01")
        user_id = ChannelTenantId.create("sandeco")

        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            adapter.record_session_coherence(
                session_id=session_id,
                content_id=ContentId("vid_coherence_01"),
                score=0.92,
                details={"wikilink_count": 14},
            )

        root_span = next(
            s for s in exporter.get_finished_spans() if s.name == "cresmo.pipeline.execution"
        )
        event = next(e for e in root_span.events if e.name == "session_coherence")
        assert event.attributes is not None
        assert event.attributes["eval.coherence_score"] == 0.92
        assert event.attributes["eval.details.wikilink_count"] == 14


class TestNoOpTelemetryAdapter:
    """Test NoOpTelemetryAdapter for graceful degradation when observability is offline."""

    def test_noop_execution(self) -> None:
        adapter = NoOpTelemetryAdapter()
        assert isinstance(adapter, TelemetryPort)

        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_noop")
        user_id = ChannelTenantId.create("sandeco")

        # Must execute cleanly without exceptions
        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            with adapter.start_stage_span("stage1"):
                pass
            adapter.record_judge_evaluation(
                session_id=session_id,
                content_id=ContentId("vid_noop"),
                iteration=1,
                max_iterations=3,
                verdict="PASS",
            )
            adapter.record_session_coherence(
                session_id=session_id,
                content_id=ContentId("vid_noop"),
                score=1.0,
                details={},
            )
