"""Unit tests for OpenTelemetry Semantic Conventions and TelemetryPort implementations.

Conforms to ADR-016:
    - Verifies PipelineSessionId and telemetry Value Objects enforce strict domain invariants.
    - Verifies OpenTelemetryAdapter sets root attributes: langfuse.session.id, langfuse.user.id.
    - Verifies nested stage spans maintain OpenTelemetry trace hierarchy.
    - Verifies judge friction ratio calculation and score recording.
    - Verifies NoOpTelemetryAdapter executes gracefully when observability is offline (ADR-014).
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from cresmo.application.ports import TelemetryPort
from cresmo.domain.entities import (
    ContentId,
    JudgeFrictionMetric,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.infrastructure.adapters.opentelemetry_adapter import (
    NoOpTelemetryAdapter,
    OpenTelemetryAdapter,
    annotate_llm_span,
)


class TestTelemetryValueObjects:
    """Test domain value objects governing telemetry identity and clinical metrics."""

    def test_pipeline_session_id_valid(self) -> None:
        session_id = PipelineSessionId.create(channel="sandeco", content_id="yt_12345678")
        assert session_id.value == "sandeco:yt_12345678"
        assert session_id.channel_id == "sandeco"
        assert session_id.content_id == "yt_12345678"
        assert not hasattr(session_id, "video_id")
        assert not hasattr(session_id, "channel_token")

    def test_pipeline_session_id_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            PipelineSessionId(value="")

        with pytest.raises(ValueError, match="Invalid PipelineSessionId format"):
            PipelineSessionId(value="invalid_format_without_colons")

    def test_user_identity_anonymous(self) -> None:
        u1 = UserIdentity.anonymous()
        assert u1.value == "anonymous"
        assert u1.is_anonymous is True
        assert u1.provider == "anonymous"
        assert u1.subject == ""

        u2 = UserIdentity.anonymous(token="sess_999")
        assert u2.value == "anon:sess_999"
        assert u2.is_anonymous is True

    def test_user_identity_identified_oauth(self) -> None:
        u = UserIdentity.identified(subject="alice@example.com", provider="oauth")
        assert u.value == "user:oauth:alice@example.com"
        assert u.is_anonymous is False
        assert u.provider == "oauth"
        assert u.subject == "alice@example.com"

        u_google = UserIdentity.identified(subject="sub_12345", provider="google")
        assert u_google.value == "user:google:sub_12345"
        assert u_google.is_anonymous is False
        assert u_google.provider == "google"

    def test_user_identity_from_channel(self) -> None:
        u = UserIdentity.from_channel("sandeco")
        assert u.value == "channel:sandeco"
        assert u.is_anonymous is True
        assert u.provider == "channel"
        assert u.subject == "sandeco"

    def test_user_identity_invariants(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            UserIdentity(value="")

        with pytest.raises(ValueError, match="requires a non-empty subject"):
            UserIdentity.identified(subject="")

        with pytest.raises(ValueError, match="cannot be empty"):
            UserIdentity.from_channel("")

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
        user_id = UserIdentity.from_channel("sandeco")

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user_id,
            metadata={
                "source": "cli",
                "title": "Machiavelli and Modern State",
                "channel": "sandeco",
                "channel_id": "UC_Sandeco123",
                "content_id": "vid_test_123",
                "video_url": "https://youtube.com/watch?v=123",
            },
        ):
            with adapter.start_stage_span("raw_indexing", attributes={"step": 1}):
                pass
            with adapter.start_stage_span("fluid_prose", attributes={"step": 2}):
                pass

        spans = exporter.get_finished_spans()
        assert len(spans) == 3

        # Spans finish from inside out: raw_indexing, fluid_prose, then root pipeline
        raw_indexing_span = next(s for s in spans if s.name == "cresmo.stage.raw_indexing")
        fluid_prose_span = next(s for s in spans if s.name == "cresmo.stage.fluid_prose")
        root_span = next(
            s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )

        # Root span must have official Langfuse OTel attributes
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.observation.type"] == "span"
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_test_123"
        assert root_span.attributes["langfuse.user.id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.user.is_anonymous"] is True
        assert root_span.attributes["cresmo.user.provider"] == "channel"
        assert tuple(root_span.attributes["langfuse.trace.tags"]) == (
            "sandeco",
            "cresmo:v2",
            "auth:channel",
        )
        assert root_span.attributes["cresmo.content.id"] == "vid_test_123"
        assert "cresmo.video.id" not in root_span.attributes
        assert root_span.attributes["cresmo.content.title"] == "Machiavelli and Modern State"
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
        assert root_span.attributes["cresmo.channel.id"] == "UC_Sandeco123"
        assert "cresmo.content_id" not in root_span.attributes
        assert "cresmo.content_title" not in root_span.attributes
        assert "cresmo.channel" not in root_span.attributes
        assert "cresmo.channel_id" not in root_span.attributes

        # Zero metadata duplication for first-class canonical keys
        assert root_span.attributes["cresmo.metadata.source"] == "cli"
        assert "cresmo.metadata.channel" not in root_span.attributes
        assert "cresmo.metadata.channel_id" not in root_span.attributes
        assert "cresmo.metadata.content_id" not in root_span.attributes
        assert "cresmo.metadata.title" not in root_span.attributes

        # ADR-037 Lean canonical input payload (zero duplicate aliases)
        input_payload_str = str(root_span.attributes.get("input.value"))
        input_payload = json.loads(input_payload_str)
        assert input_payload == {
            "content_title": "Machiavelli and Modern State",
            "channel_name": "sandeco",
            "channel_id": "UC_Sandeco123",
            "content_id": "vid_test_123",
            "video_url": "https://youtube.com/watch?v=123",
        }
        assert "channel" not in input_payload
        assert "title" not in input_payload

        # Child spans share trace_id
        assert raw_indexing_span.context is not None
        assert fluid_prose_span.context is not None
        assert root_span.context is not None
        assert raw_indexing_span.parent is not None
        assert raw_indexing_span.context.trace_id == root_span.context.trace_id
        assert fluid_prose_span.context.trace_id == root_span.context.trace_id
        assert raw_indexing_span.parent.span_id == root_span.context.span_id

    def test_record_judge_evaluation(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_judge_01")
        user_id = UserIdentity.from_channel("sandeco")

        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            adapter.record_judge_evaluation(
                session_id=session_id,
                content_id=ContentId("vid_judge_01"),
                iteration=2,
                max_iterations=3,
                verdict="PASS",
            )

        root_span = next(
            s
            for s in exporter.get_finished_spans()
            if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )
        assert len(root_span.events) == 1
        event = root_span.events[0]
        assert event.name == "judge_evaluation"
        assert event.attributes is not None
        assert event.attributes["judge.session_id"] == "sandeco:vid_judge_01"
        assert event.attributes["judge.content_id"] == "vid_judge_01"
        assert event.attributes["judge.channel_id"] == "sandeco"
        assert event.attributes["judge.iteration"] == 2
        assert event.attributes["judge.max_iterations"] == 3
        assert event.attributes["judge.friction_ratio"] == 0.5
        assert event.attributes["judge.verdict"] == "PASS"

    def test_record_session_coherence(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_coherence_01")
        user_id = UserIdentity.from_channel("sandeco")

        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            adapter.record_session_coherence(
                session_id=session_id,
                content_id=ContentId("vid_coherence_01"),
                score=0.92,
                details={"wikilink_count": 14},
            )

        root_span = next(
            s
            for s in exporter.get_finished_spans()
            if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )
        event = next(e for e in root_span.events if e.name == "session_coherence")
        assert event.attributes is not None
        assert event.attributes["eval.session_id"] == "sandeco:vid_coherence_01"
        assert event.attributes["eval.content_id"] == "vid_coherence_01"
        assert event.attributes["eval.channel_id"] == "sandeco"
        assert event.attributes["eval.coherence_score"] == 0.92
        assert event.attributes["eval.details.wikilink_count"] == 14
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.output.coherence_score"] == "0.92"
        assert root_span.attributes["langfuse.output.wikilink_count"] == "14"
        assert json.loads(str(root_span.attributes["langfuse.output"])) == {
            "coherence_score": 0.92,
            "wikilink_count": 14,
        }

    def test_pipeline_session_with_anonymous_user(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_anon_01")
        user = UserIdentity.anonymous()

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user,
        ):
            pass

        spans = exporter.get_finished_spans()
        root_span = next(
            s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_anon_01"
        assert root_span.attributes["langfuse.user.id"] == "anonymous"
        assert root_span.attributes["cresmo.content.id"] == "vid_anon_01"
        assert root_span.attributes["cresmo.channel.id"] == "sandeco"
        assert root_span.attributes["cresmo.content.title"] == "vid_anon_01"
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
        assert "cresmo.video.id" not in root_span.attributes
        assert "cresmo.channel" not in root_span.attributes
        assert root_span.attributes["cresmo.user.is_anonymous"] is True
        assert root_span.attributes["cresmo.user.provider"] == "anonymous"

    def test_pipeline_session_with_identified_oauth_user(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_auth_01")
        user = UserIdentity.identified(subject="alice@corp.com", provider="google")

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user,
        ):
            pass

        spans = exporter.get_finished_spans()
        root_span = next(
            s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_auth_01"
        assert root_span.attributes["langfuse.user.id"] == "user:google:alice@corp.com"
        assert root_span.attributes["cresmo.content.id"] == "vid_auth_01"
        assert root_span.attributes["cresmo.channel.id"] == "sandeco"
        assert root_span.attributes["cresmo.content.title"] == "vid_auth_01"
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
        assert "cresmo.video.id" not in root_span.attributes
        assert "cresmo.channel" not in root_span.attributes
        assert root_span.attributes["cresmo.user.is_anonymous"] is False
        assert root_span.attributes["cresmo.user.provider"] == "google"
        assert root_span.attributes["cresmo.user.subject"] == "alice@corp.com"

    def test_pipeline_session_with_worker_identity(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_worker_01")
        user = UserIdentity.worker()

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user,
        ):
            pass

        spans = exporter.get_finished_spans()
        root_span = next(
            s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_worker_01"
        assert root_span.attributes["langfuse.user.id"] == "system:worker"
        assert root_span.attributes["cresmo.content.id"] == "vid_worker_01"
        assert root_span.attributes["cresmo.channel.id"] == "sandeco"
        assert root_span.attributes["cresmo.content.title"] == "vid_worker_01"
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
        assert root_span.attributes["cresmo.user.is_anonymous"] is False
        assert root_span.attributes["cresmo.user.provider"] == "system"
        assert root_span.attributes["cresmo.user.subject"] == "worker"

    def test_pipeline_session_with_custom_trace_name(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_custom_name")
        user = UserIdentity.anonymous()

        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user,
            trace_name="custom.synthesis.run",
        ):
            pass

        spans = exporter.get_finished_spans()
        root_span = next(s for s in spans if s.name == "custom.synthesis.run")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_custom_name"

    def test_pipeline_session_propagates_caller_exceptions(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        """Verify that caller exceptions are never swallowed by start_pipeline_session."""
        adapter, _ = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_exc_01")
        user_id = UserIdentity.from_channel("sandeco")

        with (
            pytest.raises(DomainValidationError, match="Entity discovery failed"),
            adapter.start_pipeline_session(session_id=session_id, user_id=user_id),
        ):
            raise DomainValidationError("Entity discovery failed")

    def test_pipeline_session_version_resolution_from_metadata(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        """Verify pipeline_version and version in metadata take precedence over default."""
        adapter, exporter = otel_setup
        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_ver_01")
        user = UserIdentity.anonymous()

        # 1. Custom pipeline_version in metadata
        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id=user,
            metadata={"pipeline_version": "cresmo:v3.0-beta"},
        ):
            pass

        spans = exporter.get_finished_spans()
        assert spans[-1].attributes is not None
        assert list(spans[-1].attributes["langfuse.trace.tags"]) == [
            "sandeco",
            "cresmo:v3.0-beta",
            "auth:anonymous",
        ]

        # 2. Version in metadata fallback
        session_id2 = PipelineSessionId.create(channel="sandeco", content_id="vid_ver_02")
        with adapter.start_pipeline_session(
            session_id=session_id2,
            user_id=user,
            metadata={"version": "v2.5"},
        ):
            pass

        spans = exporter.get_finished_spans()
        assert spans[-1].attributes is not None
        assert list(spans[-1].attributes["langfuse.trace.tags"]) == [
            "sandeco",
            "v2.5",
            "auth:anonymous",
        ]

    def test_opentelemetry_adapter_accepts_injected_pipeline_version(
        self,
        otel_setup: tuple[OpenTelemetryAdapter, InMemorySpanExporter],
    ) -> None:
        """Verify OpenTelemetryAdapter uses constructor-injected pipeline_version per ADR-026 Rule 9."""
        adapter, exporter = otel_setup
        custom_adapter = OpenTelemetryAdapter(
            tracer=adapter._tracer,
            pipeline_version="cresmo:v3-injected",
        )

        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_injected_ver")
        user = UserIdentity.anonymous()

        with custom_adapter.start_pipeline_session(session_id=session_id, user_id=user):
            pass

        spans = exporter.get_finished_spans()
        assert spans[-1].attributes is not None
        assert list(spans[-1].attributes["langfuse.trace.tags"]) == [
            "sandeco",
            "cresmo:v3-injected",
            "auth:anonymous",
        ]


class TestNoOpTelemetryAdapter:
    """Test NoOpTelemetryAdapter for graceful degradation when observability is offline."""

    def test_noop_execution(self) -> None:
        adapter = NoOpTelemetryAdapter()
        assert isinstance(adapter, TelemetryPort)

        session_id = PipelineSessionId.create(channel="sandeco", content_id="vid_noop")
        user_id = UserIdentity.from_channel("sandeco")

        # Must execute cleanly without exceptions
        with adapter.start_pipeline_session(session_id=session_id, user_id=user_id):
            with adapter.start_stage_span("raw_indexing"):
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


def test_name_telemetry_threads_assigns_canonical_names() -> None:
    """Verify name_telemetry_threads assigns canonical thread names per ADR-020 Pillar 5."""
    from unittest.mock import MagicMock

    from cresmo.infrastructure.adapters.opentelemetry_adapter import name_telemetry_threads

    # Setup mock consumers
    mock_media_consumer = MagicMock()
    mock_media_consumer.name = "Thread-1"

    mock_score_consumer = MagicMock()
    mock_score_consumer.name = "Thread-2"

    mock_cache_consumer = MagicMock()
    mock_cache_consumer.name = "Thread-3"

    mock_client = MagicMock()
    mock_client._resources._media_upload_consumers = [mock_media_consumer]
    mock_client._resources._ingestion_consumers = [mock_score_consumer]
    mock_client._resources.prompt_cache._task_manager._consumers = [mock_cache_consumer]

    from unittest.mock import patch

    # Setup dummy OpenTelemetry thread
    dummy_otel_thread = MagicMock()
    dummy_otel_thread.name = "OtelBatchSpanRecordProcessor"

    with patch("threading.enumerate", return_value=[dummy_otel_thread]):
        name_telemetry_threads(mock_client)

    assert mock_media_consumer.name == "LangfuseMediaUploadConsumer-0"
    assert mock_score_consumer.name == "LangfuseScoreIngestionConsumer-0"
    assert mock_cache_consumer.name == "LangfusePromptCacheConsumer-0"
    assert dummy_otel_thread.name == "CresmoOtelBatchSpanProcessor"


def test_opentelemetry_adapter_flush() -> None:
    """Verify flush drains both Langfuse and OpenTelemetry tracer provider."""
    from unittest.mock import MagicMock, patch

    mock_langfuse = MagicMock()
    adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)

    mock_provider = MagicMock()
    with patch("opentelemetry.trace.get_tracer_provider", return_value=mock_provider):
        adapter.flush()

    mock_langfuse.flush.assert_called_once()
    mock_provider.force_flush.assert_called_once_with(timeout_millis=2000)


def test_noop_telemetry_adapter_flush_is_graceful_noop() -> None:
    """Verify NoOpTelemetryAdapter flush executes gracefully without error."""
    adapter = NoOpTelemetryAdapter()
    adapter.flush()


def test_opentelemetry_adapter_record_score() -> None:
    """Verify record_score emits score to Langfuse and records event on span."""
    from unittest.mock import MagicMock

    mock_langfuse = MagicMock()
    adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)

    adapter.record_score(
        name="style_compliance",
        value=0.95,
        comment="Zero em-dashes and continuous prose verified",
        trace_id="trace_test_123",
    )

    mock_langfuse.score.assert_called_once_with(
        name="style_compliance",
        value=0.95,
        comment="Zero em-dashes and continuous prose verified",
        trace_id="trace_test_123",
    )


def test_opentelemetry_adapter_record_score_with_explicit_observation_id() -> None:
    """Verify record_score propagates explicit observation_id to Langfuse client (ADR-036)."""
    from unittest.mock import MagicMock

    mock_langfuse = MagicMock()
    adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)

    adapter.record_score(
        name="fluid_prose.semantic_faithfulness",
        value=0.98,
        comment="High factual alignment",
        trace_id="trace_test_456",
        observation_id="obs_span_789abc",
    )

    mock_langfuse.score.assert_called_once_with(
        name="fluid_prose.semantic_faithfulness",
        value=0.98,
        comment="High factual alignment",
        trace_id="trace_test_456",
        observation_id="obs_span_789abc",
    )


def test_noop_telemetry_adapter_record_score_is_graceful_noop() -> None:
    """Verify NoOpTelemetryAdapter record_score executes gracefully without error."""
    adapter = NoOpTelemetryAdapter()
    adapter.record_score(
        name="style_compliance",
        value=1.0,
        comment="test",
        trace_id="test_trace",
    )


def test_universal_algorithmic_and_cognitive_parity_adr034() -> None:
    """Verify ADR-034: Algorithmic (ID-ID) and Cognitive (TXT-TXT) Parity invariants."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("cresmo.test")
    adapter = OpenTelemetryAdapter(tracer=tracer)

    session_id = PipelineSessionId.create(channel="test_channel", content_id="test_content_456")
    user = UserIdentity.anonymous()

    with adapter.start_pipeline_session(
        session_id=session_id,
        user_id=user,
        metadata={"custom_key": "custom_val"},
    ):
        pass

    spans = exporter.get_finished_spans()
    root_span = next(
        s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
    )
    attrs = root_span.attributes or {}

    # Algorithmic Pair (ID - ID)
    assert attrs["cresmo.content.id"] == "test_content_456"
    assert attrs["cresmo.channel.id"] == "test_channel"

    # Cognitive Pair (TXT - TXT)
    assert attrs["cresmo.channel.name"] == "test_channel"
    assert attrs["cresmo.content.title"] == "test_content_456"


def test_start_pipeline_session_with_batch_id_adr035() -> None:
    """Verify ADR-035: batch_id metadata sets cresmo.batch_id attribute, Langfuse tag, and input payload."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("cresmo.test")
    adapter = OpenTelemetryAdapter(tracer=tracer)

    session_id = PipelineSessionId.create(channel="test_channel", content_id="test_content_789")
    user = UserIdentity.anonymous()
    batch_key = "20261003_203603_a1b2c3"

    with adapter.start_pipeline_session(
        session_id=session_id,
        user_id=user,
        metadata={"batch_id": batch_key},
    ):
        pass

    spans = exporter.get_finished_spans()
    root_span = next(
        s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
    )
    attrs = root_span.attributes or {}

    assert attrs["cresmo.batch_id"] == batch_key
    tags = attrs.get("langfuse.trace.tags")
    assert isinstance(tags, (list, tuple))
    assert f"batch:{batch_key}" in tags

    raw_input = attrs.get("input.value") or attrs.get("langfuse.observation.input")
    assert isinstance(raw_input, str)
    input_payload = json.loads(raw_input)
    assert input_payload["batch_id"] == batch_key


def test_start_pipeline_session_sets_otel_observation_input_attributes() -> None:
    """Verify start_pipeline_session sets standard OTEL and Langfuse observation input attributes."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("cresmo.test")
    adapter = OpenTelemetryAdapter(tracer=tracer)

    session_id = PipelineSessionId.create(channel="test_channel", content_id="test_content_101")
    user = UserIdentity.anonymous()

    with adapter.start_pipeline_session(
        session_id=session_id,
        user_id=user,
        metadata={
            "title": "Test Title",
            "raw_characters": 1500,
            "raw_words": 250,
        },
    ):
        pass

    spans = exporter.get_finished_spans()
    root_span = next(
        s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
    )
    attrs = root_span.attributes or {}

    expected_dict = {
        "content_title": "Test Title",
        "raw_characters": "1500",
        "raw_words": "250",
        "channel_id": "test_channel",
        "content_id": "test_content_101",
        "channel_name": "test_channel",
    }
    assert json.loads(str(attrs["input.value"])) == expected_dict
    assert json.loads(str(attrs["langfuse.observation.input"])) == expected_dict
    assert json.loads(str(attrs["langfuse.trace.input"])) == expected_dict
    # Verify legacy alias bloat is eliminated (ADR-037)
    assert "channel" not in expected_dict
    assert "title" not in expected_dict


def test_start_pipeline_session_propagates_trace_name_and_identity_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: in-progress traces must render name + identity in the Langfuse table.

    Langfuse v4 derives trace name/IO from the root observation, which is exported only
    when the root span ends. Child generations flushed mid-pipeline must therefore carry
    trace_name and identity metadata via propagate_attributes.
    """
    from unittest.mock import MagicMock

    import cresmo.infrastructure.adapters.opentelemetry_adapter as otel_module

    captured: dict[str, object] = {}

    def fake_propagate(**kwargs: object) -> object:
        captured.update(kwargs)
        return MagicMock(__enter__=MagicMock(), __exit__=MagicMock(return_value=False))

    monkeypatch.setattr(otel_module, "propagate_attributes", fake_propagate)

    provider = TracerProvider()
    adapter = OpenTelemetryAdapter(
        tracer=provider.get_tracer("cresmo.test"), langfuse_client=MagicMock()
    )
    session_id = PipelineSessionId.create(channel="chan_id_1", content_id="content_42")
    long_title = "T" * 500

    with adapter.start_pipeline_session(
        session_id=session_id,
        user_id=UserIdentity.anonymous(),
        metadata={"channel_name": "Marcelo Andrade", "title": long_title, "batch_id": "b1"},
    ):
        pass

    assert captured["trace_name"] == "cresmo.synthesis_pipeline"
    metadata = captured["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["content_id"] == "content_42"
    assert metadata["channel_id"] == "chan_id_1"
    assert metadata["channel_name"] == "Marcelo Andrade"
    assert metadata["batch_id"] == "b1"
    # Langfuse rejects propagated metadata values longer than 200 characters.
    assert len(metadata["content_title"]) <= 200


def test_record_session_output_sets_otel_and_langfuse_output_attributes() -> None:
    """Verify record_session_output records high-signal outcome attributes on root span."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("cresmo.test")
    adapter = OpenTelemetryAdapter(tracer=tracer)

    session_id = PipelineSessionId.create(channel="test_channel", content_id="test_content_102")
    user = UserIdentity.anonymous()

    with adapter.start_pipeline_session(
        session_id=session_id,
        user_id=user,
        metadata={"title": "Test Episode"},
    ):
        output_payload = {
            "status": "COMPLETED",
            "stage": "fluid_prose",
            "word_count": 850,
            "char_count": 5200,
        }
        adapter.record_session_output(output_payload)

    spans = exporter.get_finished_spans()
    root_span = next(
        s for s in spans if s.name in ("pipeline.coordinator", "cresmo.pipeline.execution")
    )
    attrs = root_span.attributes or {}

    expected_serialized = json.dumps(output_payload)
    assert attrs["output.value"] == expected_serialized
    assert attrs["langfuse.observation.output"] == expected_serialized
    assert attrs["langfuse.output"] == expected_serialized
    assert attrs["langfuse.trace.output"] == expected_serialized
    assert attrs["cresmo.output.status"] == "COMPLETED"
    assert attrs["cresmo.output.stage"] == "fluid_prose"
    assert attrs["cresmo.output.word_count"] == "850"
    assert attrs["cresmo.output.char_count"] == "5200"


def test_noop_telemetry_adapters_record_session_output() -> None:
    """Verify NoOp telemetry adapters implement record_session_output gracefully."""
    from cresmo.application.ports.telemetry import NoOpTelemetryPort

    noop_port = NoOpTelemetryPort()
    noop_port.record_session_output({"status": "COMPLETED"})

    noop_adapter = NoOpTelemetryAdapter()
    noop_adapter.record_session_output({"status": "COMPLETED"})


def test_cresmo_root_exports_only_package_metadata() -> None:
    """Verify cresmo package root strictly conforms to ADR-026 Rule 9."""
    import cresmo

    assert hasattr(cresmo, "__version__")
    assert not hasattr(cresmo, "PIPELINE_VERSION")
    assert cresmo.__all__ == ["__version__"]


class TestAdr037LeanTelemetryAndEvaluationSpan:
    """Unit tests for ADR-037 Lean Telemetry Topography and Chronological Evaluation Spans."""

    def test_default_root_span_and_trace_separation(self) -> None:
        """Verify default root span name is pipeline.coordinator and trace name is cresmo.synthesis_pipeline."""
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)

        session_id = PipelineSessionId.create(channel="test_chan", content_id="test_cnt")
        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id="system:worker",
            metadata={"channel_name": "Test Chan", "content_title": "Test Title"},
        ):
            pass

        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        root_span = spans[0]
        attrs = root_span.attributes or {}
        assert root_span.name == "pipeline.coordinator"
        assert attrs.get("langfuse.trace.name") == "cresmo.synthesis_pipeline"

    def test_lean_input_payload_has_no_duplicate_aliases(self) -> None:
        """Verify input payload uses canonical keys only and removes redundant alias keys."""
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)

        session_id = PipelineSessionId.create(channel="chan_id", content_id="cnt_id")
        with adapter.start_pipeline_session(
            session_id=session_id,
            user_id="system:worker",
            metadata={
                "channel_id": "chan_id",
                "channel_name": "Channel Alpha",
                "content_id": "cnt_id",
                "content_title": "Content Alpha",
            },
        ):
            pass

        spans = exporter.get_finished_spans()
        root_span = spans[0]
        attrs = root_span.attributes or {}

        # Canonical input payload
        input_raw = attrs.get("input.value")
        assert isinstance(input_raw, str)
        input_json = json.loads(input_raw)
        assert "channel_name" in input_json
        assert "content_title" in input_json
        # Banned duplicate aliases (ADR-037)
        assert "channel" not in input_json
        assert "title" not in input_json
        assert "langfuse.input.channel" not in attrs
        assert "langfuse.input.title" not in attrs

    def test_start_stage_evaluation_span_creates_child_span(self) -> None:
        """Verify start_stage_evaluation_span creates a dedicated child span under stage span."""
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)

        with (
            adapter.start_stage_span("fluid_prose"),
            adapter.start_stage_evaluation_span(
                "fluid_prose",
                attempt=2,
                attributes={"judge.verdict": "PASS"},
            ) as eval_span,
        ):
            assert eval_span is not None

        spans = exporter.get_finished_spans()
        assert len(spans) == 2
        eval_span_data = next(s for s in spans if s.name == "cresmo.stage.fluid_prose.evaluation")
        stage_span_data = next(s for s in spans if s.name == "cresmo.stage.fluid_prose")

        # Verify hierarchy
        assert eval_span_data.parent is not None
        assert stage_span_data.context is not None
        assert eval_span_data.parent.span_id == stage_span_data.context.span_id

        eval_attrs = eval_span_data.attributes or {}
        assert eval_attrs.get("judge.attempt") == 2
        assert eval_attrs.get("judge.stage_name") == "fluid_prose"
        assert eval_attrs.get("judge.verdict") == "PASS"
        assert eval_attrs.get("langfuse.observation.type") == "span"

    def test_record_stage_io_populates_active_span(self) -> None:
        """Verify record_stage_io sets input and output payloads on the active stage span."""
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)

        with adapter.start_stage_span("fluid_prose"):
            adapter.record_stage_io(
                input_payload={"source_words": 1500, "source_type": "transcript"},
                output_payload={"synthesized_words": 850, "status": "APPROVED"},
            )

        spans = exporter.get_finished_spans()
        stage_span = spans[0]
        attrs = stage_span.attributes or {}

        input_raw = attrs.get("input.value")
        assert isinstance(input_raw, str)
        input_data = json.loads(input_raw)
        assert input_data["source_words"] == 1500

        output_raw = attrs.get("output.value")
        assert isinstance(output_raw, str)
        output_data = json.loads(output_raw)
        assert output_data["synthesized_words"] == 850

    def test_annotate_llm_span_records_temperature_and_max_tokens(self) -> None:
        """Verify annotate_llm_span populates gen_ai.request.temperature and gen_ai.request.max_tokens."""
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("test.llm"):
            annotate_llm_span(
                system="google",
                model="gemini-2.5-flash",
                prompt_tokens=100,
                candidate_tokens=50,
                temperature=0.7,
                max_tokens=8192,
            )

        spans = exporter.get_finished_spans()
        span = spans[0]
        attrs = span.attributes or {}
        assert attrs.get("gen_ai.request.temperature") == 0.7
        assert attrs.get("gen_ai.request.max_tokens") == 8192


def _create_mock_non_recording_span() -> Any:
    from unittest.mock import MagicMock

    mock_span = MagicMock()
    mock_span.is_recording.return_value = False
    mock_ctx = MagicMock()
    mock_ctx.trace_id = 0
    mock_ctx.span_id = 0
    mock_ctx.is_valid = False
    mock_span.get_span_context.return_value = mock_ctx
    return mock_span


class TestAnnotateLlmSpanExtended:
    """Comprehensive tests for annotate_llm_span GenAI Semantic Conventions."""

    def test_annotate_llm_span_all_parameters(self) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("test.llm"):
            annotate_llm_span(
                system="google",
                model="gemini-2.5-flash",
                prompt_tokens=100,
                candidate_tokens=50,
                session_id="sandeco:vid1",
                user_id="user:sandeco",
                trace_id="vid1",
                temperature=0.7,
                max_tokens=8192,
            )

        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        attrs = spans[0].attributes or {}
        assert attrs["gen_ai.system"] == "google"
        assert attrs["gen_ai.request.model"] == "gemini-2.5-flash"
        assert attrs["gen_ai.usage.input_tokens"] == 100
        assert attrs["gen_ai.usage.output_tokens"] == 50
        assert attrs["langfuse.observation.type"] == "generation"
        assert attrs["langfuse.session.id"] == "sandeco:vid1"
        assert attrs["langfuse.user.id"] == "user:sandeco"
        assert attrs["cresmo.trace_id"] == "vid1"
        assert attrs["gen_ai.request.temperature"] == 0.7
        assert attrs["cresmo.temperature"] == 0.7
        assert attrs["gen_ai.request.max_tokens"] == 8192

    def test_annotate_llm_span_minimal_parameters(self) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("test.llm"):
            annotate_llm_span(
                system="ollama",
                model="qwen2.5:7b",
                prompt_tokens=20,
                candidate_tokens=10,
            )

        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        attrs = spans[0].attributes or {}
        assert attrs["gen_ai.system"] == "ollama"
        assert attrs["gen_ai.request.model"] == "qwen2.5:7b"
        assert attrs["gen_ai.usage.input_tokens"] == 20
        assert attrs["gen_ai.usage.output_tokens"] == 10
        assert attrs["langfuse.observation.type"] == "generation"
        assert "langfuse.session.id" not in attrs
        assert "langfuse.user.id" not in attrs
        assert "cresmo.trace_id" not in attrs
        assert "gen_ai.request.temperature" not in attrs
        assert "cresmo.temperature" not in attrs
        assert "gen_ai.request.max_tokens" not in attrs

    def test_annotate_llm_span_non_recording_span_noop(self) -> None:
        from unittest.mock import patch

        mock_span = _create_mock_non_recording_span()
        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            annotate_llm_span(
                system="google",
                model="gemini",
                prompt_tokens=1,
                candidate_tokens=1,
            )
        mock_span.set_attribute.assert_not_called()

    def test_annotate_llm_span_no_current_span_noop(self) -> None:
        from unittest.mock import patch

        with patch("opentelemetry.trace.get_current_span", return_value=None):
            annotate_llm_span(
                system="google",
                model="gemini",
                prompt_tokens=1,
                candidate_tokens=1,
            )


class TestIdentityResolutionExtended:
    """Test string and polymorphic identity resolution functions."""

    def test_resolve_identity_from_string_system(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        ident, tenant = _resolve_identity_from_string("system:worker:node:1")
        assert ident.value == "system:worker:node:1"
        assert ident.provider == "system"
        assert ident.subject == "worker:node:1"
        assert tenant is None

    def test_resolve_identity_from_string_channel(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        ident, tenant = _resolve_identity_from_string("channel:sandeco:sub")
        assert ident.value == "channel:sandeco:sub"
        assert ident.provider == "channel"
        assert ident.subject == "sandeco:sub"
        assert tenant == "channel:sandeco:sub"

    def test_resolve_identity_from_string_anonymous(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        ident, tenant = _resolve_identity_from_string("anonymous")
        assert ident.value == "anonymous"
        assert ident.is_anonymous is True
        assert ident.provider == "anonymous"
        assert ident.subject == ""
        assert tenant is None

    def test_resolve_identity_from_string_user_structured(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        ident, tenant = _resolve_identity_from_string("user:google:alice:admin")
        assert ident.value == "user:google:alice:admin"
        assert ident.provider == "google"
        assert ident.subject == "alice:admin"
        assert tenant is None

        # Exactly 3 parts (_MIN_STRUCTURED_USER_PARTS)
        ident3, tenant3 = _resolve_identity_from_string("user:google:alice")
        assert ident3.value == "user:google:alice"
        assert ident3.provider == "google"
        assert ident3.subject == "alice"
        assert tenant3 is None

    def test_resolve_identity_from_string_user_short(self) -> None:
        from unittest.mock import patch

        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        with patch(
            "cresmo.infrastructure.adapters.opentelemetry_adapter.UserIdentity.identified",
            wraps=UserIdentity.identified,
        ) as mock_id:
            ident, tenant = _resolve_identity_from_string("user:bob")
            assert ident.value == "user:oauth:bob"
            assert ident.provider == "oauth"
            assert ident.subject == "bob"
            assert tenant is None
            mock_id.assert_called_once_with(subject="bob", provider="oauth")

    def test_resolve_identity_from_string_fallback(self) -> None:
        from unittest.mock import patch

        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_identity_from_string,
        )

        with patch(
            "cresmo.infrastructure.adapters.opentelemetry_adapter.UserIdentity.identified",
            wraps=UserIdentity.identified,
        ) as mock_id:
            ident, tenant = _resolve_identity_from_string("plain_user_123")
            assert ident.value == "user:oauth:plain_user_123"
            assert ident.provider == "oauth"
            assert ident.subject == "plain_user_123"
            assert tenant is None
            mock_id.assert_called_once_with(subject="plain_user_123", provider="oauth")

    def test_resolve_user_identity_and_tenant_variants(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _resolve_user_identity_and_tenant,
        )

        session_id = PipelineSessionId.create(channel="mychan", content_id="cnt1")

        # 1. UserIdentity instance with channel_tenant_id provided
        u1 = UserIdentity.worker("w1")
        res_u1, res_t1 = _resolve_user_identity_and_tenant(u1, "custom_t", session_id)
        assert res_u1 == u1
        assert res_t1 == "custom_t"

        # 2. UserIdentity instance with channel_tenant_id None -> default session channel
        res_u2, res_t2 = _resolve_user_identity_and_tenant(u1, None, session_id)
        assert res_u2 == u1
        assert res_t2 == "channel:mychan"

        # 3. str user_id with channel: prefix, no tenant provided -> parsed tenant
        res_u3, res_t3 = _resolve_user_identity_and_tenant("channel:sandeco", None, session_id)
        assert res_u3.value == "channel:sandeco"
        assert res_t3 == "channel:sandeco"

        # 4. str user_id with channel: prefix, but explicit tenant provided
        res_u4, res_t4 = _resolve_user_identity_and_tenant(
            "channel:sandeco", "explicit_t", session_id
        )
        assert res_u4.value == "channel:sandeco"
        assert res_t4 == "explicit_t"

        # 5. Invalid type -> anonymous fallback
        res_u5, res_t5 = _resolve_user_identity_and_tenant(
            12345, None, session_id  # type: ignore[arg-type]
        )
        assert res_u5.is_anonymous is True
        assert res_u5.value == "anonymous"
        assert res_t5 == "channel:mychan"


class TestLangfusePayloadAndSessionAttributesExtended:
    """Test _build_langfuse_input_payload and _build_session_span_attributes."""

    def test_build_langfuse_input_payload_all_keys(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _build_langfuse_input_payload,
        )

        attrs: dict[str, Any] = {}
        meta = {
            "batch_id": "batch_99",
            "video_url": "https://youtu.be/test",
            "raw_characters": 5000,
            "raw_words": 800,
            "custom_key": "custom_val",
            "title": "ignored_title_in_loop",
            "channel": "ignored_chan_in_loop",
        }
        _build_langfuse_input_payload(
            metadata=meta,
            channel_name="chan_default",
            channel_id="cid_1",
            content_id="cnt_1",
            content_title="title_default",
            attributes=attrs,
        )

        assert "cresmo.metadata.batch_id" not in attrs
        assert attrs["cresmo.metadata.custom_key"] == "custom_val"
        assert "langfuse.input.title" not in attrs
        assert "langfuse.input.channel" not in attrs
        assert attrs["langfuse.input.batch_id"] == "batch_99"
        assert attrs["langfuse.input.video_url"] == "https://youtu.be/test"
        assert attrs["langfuse.input.raw_characters"] == "5000"
        assert attrs["langfuse.input.raw_words"] == "800"
        assert attrs["langfuse.input.channel_id"] == "cid_1"
        assert attrs["langfuse.input.content_id"] == "cnt_1"
        assert attrs["langfuse.input.channel_name"] == "ignored_chan_in_loop"
        assert attrs["langfuse.input.content_title"] == "ignored_title_in_loop"

        payload = json.loads(attrs["input.value"])
        assert payload["batch_id"] == "batch_99"
        assert payload["video_url"] == "https://youtu.be/test"
        assert payload["raw_characters"] == "5000"
        assert payload["raw_words"] == "800"
        assert payload["channel_id"] == "cid_1"
        assert payload["content_id"] == "cnt_1"
        assert payload["channel_name"] == "ignored_chan_in_loop"
        assert payload["content_title"] == "ignored_title_in_loop"
        assert attrs["langfuse.observation.input"] == attrs["input.value"]
        assert attrs["langfuse.trace.input"] == attrs["input.value"]

    def test_build_langfuse_input_payload_channel_and_title_fallbacks(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _build_langfuse_input_payload,
        )

        # Case 1: channel_name and content_title from metadata
        attrs1: dict[str, Any] = {}
        _build_langfuse_input_payload(
            metadata={"channel_name": "cname", "content_title": "ctitle"},
            channel_name="param_c",
            channel_id="",
            content_id="",
            content_title="param_t",
            attributes=attrs1,
        )
        assert attrs1["langfuse.input.channel_name"] == "cname"
        assert attrs1["langfuse.input.content_title"] == "ctitle"
        assert "langfuse.input.channel_id" not in attrs1
        assert "langfuse.input.content_id" not in attrs1

        # Case 2: channel and title from metadata
        attrs2: dict[str, Any] = {}
        _build_langfuse_input_payload(
            metadata={"channel": "chan2", "title": "tit2"},
            channel_name="param_c",
            channel_id="",
            content_id="",
            content_title="param_t",
            attributes=attrs2,
        )
        assert attrs2["langfuse.input.channel_name"] == "chan2"
        assert attrs2["langfuse.input.content_title"] == "tit2"

        # Case 3: from fallback parameters when metadata empty
        attrs3: dict[str, Any] = {}
        _build_langfuse_input_payload(
            metadata={},
            channel_name="param_c",
            channel_id="",
            content_id="",
            content_title="param_t",
            attributes=attrs3,
        )
        assert attrs3["langfuse.input.channel_name"] == "param_c"
        assert attrs3["langfuse.input.content_title"] == "param_t"

        # Case 4: all empty -> no input payload serialized
        attrs4: dict[str, Any] = {}
        _build_langfuse_input_payload(
            metadata={},
            channel_name="",
            channel_id="",
            content_id="",
            content_title="",
            attributes=attrs4,
        )
        assert "input.value" not in attrs4
        assert "langfuse.observation.input" not in attrs4
        assert "langfuse.trace.input" not in attrs4

    def test_build_session_span_attributes_variants(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            _build_session_span_attributes,
        )

        session_id = PipelineSessionId.create(channel="chan_alpha", content_id="cnt_beta")
        user = UserIdentity.identified(subject="alice", provider="google")

        # 1. With batch_id and subject
        attrs, tags = _build_session_span_attributes(
            session_id=session_id,
            user=user,
            tenant="tenant_xyz",
            pipeline_version="cresmo:v3",
            metadata={
                "batch_id": "b_123",
                "channel": "chan_from_meta",
                "title": "title_from_meta",
            },
        )
        assert attrs["langfuse.observation.type"] == "span"
        assert attrs["langfuse.session.id"] == "chan_alpha:cnt_beta"
        assert attrs["langfuse.user.id"] == "user:google:alice"
        assert attrs["cresmo.channel.id"] == "chan_alpha"
        assert attrs["cresmo.content.id"] == "cnt_beta"
        assert attrs["cresmo.channel.name"] == "chan_from_meta"
        assert attrs["cresmo.content.title"] == "title_from_meta"
        assert attrs["cresmo.tenant_id"] == "tenant_xyz"
        assert attrs["cresmo.user.is_anonymous"] is False
        assert attrs["cresmo.user.provider"] == "google"
        assert attrs["cresmo.user.subject"] == "alice"
        assert attrs["cresmo.batch_id"] == "b_123"
        assert "batch:b_123" in tags
        assert "chan_from_meta" in tags
        assert "cresmo:v3" in tags
        assert "auth:google" in tags

        # 2. Metadata fallback to channel_id and content_id
        attrs2, _tags2 = _build_session_span_attributes(
            session_id=session_id,
            user=UserIdentity.anonymous(),
            tenant="tenant_def",
            pipeline_version="cresmo:v2",
            metadata={},
        )
        assert attrs2["cresmo.channel.name"] == "chan_alpha"
        assert attrs2["cresmo.content.title"] == "cnt_beta"
        assert "cresmo.user.subject" not in attrs2
        assert "cresmo.batch_id" not in attrs2

        # 3. Metadata with only content_title
        attrs3, _ = _build_session_span_attributes(
            session_id=session_id,
            user=user,
            tenant="tenant_xyz",
            pipeline_version="cresmo:v3",
            metadata={"content_title": "ct_alone"},
        )
        assert attrs3["cresmo.content.title"] == "ct_alone"

        # 4. Metadata empty verifies content_title in input.value falls back to content_id
        input_payload2 = json.loads(attrs2["input.value"])
        assert input_payload2["content_title"] == "cnt_beta"


class TestOpenTelemetryAdapterRecordMethodsAndFlushExtended:
    """Test record_score, record_judge_evaluation, record_session_coherence, record_stage_io, and flush."""

    def test_record_score_inside_span_auto_observation_id(self) -> None:
        from unittest.mock import MagicMock

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        mock_langfuse = MagicMock()
        adapter = OpenTelemetryAdapter(tracer=tracer, langfuse_client=mock_langfuse)

        with tracer.start_as_current_span("parent_span") as span:
            span_ctx = span.get_span_context()
            expected_obs_id = f"{span_ctx.span_id:016x}"
            adapter.record_score(
                name="precision",
                value=0.99,
                comment="great score",
                trace_id="tr_789",
                observation_id=None,
            )

        finished = exporter.get_finished_spans()
        assert len(finished) == 1
        event = finished[0].events[0]
        assert event.name == "telemetry_score"
        assert event.attributes is not None
        assert event.attributes["score.name"] == "precision"
        assert event.attributes["score.value"] == 0.99
        assert event.attributes["score.comment"] == "great score"
        assert event.attributes["score.trace_id"] == "tr_789"
        assert event.attributes["score.observation_id"] == expected_obs_id

        mock_langfuse.score.assert_called_once_with(
            name="precision",
            value=0.99,
            comment="great score",
            trace_id="tr_789",
            observation_id=expected_obs_id,
        )

    def test_record_score_non_recording_span_and_langfuse_exception(self) -> None:
        from unittest.mock import MagicMock, patch

        mock_span = _create_mock_non_recording_span()
        mock_langfuse = MagicMock()
        mock_langfuse.score.side_effect = RuntimeError("langfuse failure")
        adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)

        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            adapter.record_score(name="test", value=1.0)

        mock_span.add_event.assert_not_called()
        mock_langfuse.score.assert_called_once_with(name="test", value=1.0)

    def test_record_judge_evaluation_span_event_and_langfuse(self) -> None:
        from unittest.mock import MagicMock

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        mock_langfuse = MagicMock()
        adapter = OpenTelemetryAdapter(tracer=tracer, langfuse_client=mock_langfuse)

        session_id = PipelineSessionId.create(channel="sandeco", content_id="c123")
        content_id = ContentId("c123")

        with tracer.start_as_current_span("eval_stage"):
            adapter.record_judge_evaluation(
                session_id=session_id,
                content_id=content_id,
                iteration=2,
                max_iterations=3,
                verdict="PASS",
            )

        finished = exporter.get_finished_spans()
        assert len(finished) == 1
        event = finished[0].events[0]
        assert event.name == "judge_evaluation"
        assert event.attributes is not None
        assert event.attributes["judge.session_id"] == "sandeco:c123"
        assert event.attributes["judge.content_id"] == "c123"
        assert event.attributes["judge.channel_id"] == "sandeco"
        assert event.attributes["judge.iteration"] == 2
        assert event.attributes["judge.max_iterations"] == 3
        assert event.attributes["judge.verdict"] == "PASS"
        assert event.attributes["judge.friction_ratio"] == 0.5

        mock_langfuse.score.assert_called_once_with(
            name="judge_friction",
            value=0.5,
            comment="Iteration 2/3 - PASS",
        )

    def test_record_judge_evaluation_non_recording_span_and_langfuse_err(self) -> None:
        from unittest.mock import MagicMock, patch

        mock_span = _create_mock_non_recording_span()
        mock_langfuse = MagicMock()
        mock_langfuse.score.side_effect = RuntimeError("err")
        adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)

        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            adapter.record_judge_evaluation(
                session_id=PipelineSessionId.create("ch", "c1"),
                content_id=ContentId("c1"),
                iteration=1,
                max_iterations=1,
                verdict="PASS",
            )
        mock_span.add_event.assert_not_called()

    def test_record_session_coherence_with_langfuse_and_non_recording(self) -> None:
        from unittest.mock import MagicMock, patch

        mock_langfuse = MagicMock()
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer, langfuse_client=mock_langfuse)

        session_id = PipelineSessionId.create(channel="chan1", content_id="c1")
        content_id = ContentId("c1")

        with tracer.start_as_current_span("coherence_span"):
            adapter.record_session_coherence(
                session_id=session_id,
                content_id=content_id,
                score=0.88,
                details={"metric_a": 10},
            )

        mock_langfuse.score.assert_called_once_with(
            name="session_coherence",
            value=0.88,
            comment="Coherence for c1",
        )

        # Test non-recording span & langfuse exception
        mock_span = _create_mock_non_recording_span()
        mock_langfuse.score.side_effect = RuntimeError("score error")
        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            adapter.record_session_coherence(
                session_id=session_id,
                content_id=content_id,
                score=0.5,
            )
        mock_span.add_event.assert_not_called()
        mock_span.set_attribute.assert_not_called()

    def test_record_stage_io_string_payloads_and_non_recording(self) -> None:
        from unittest.mock import patch

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        adapter = OpenTelemetryAdapter(tracer=tracer)

        with tracer.start_as_current_span("stage_span"):
            adapter.record_stage_io(
                input_payload="plain text input",
                output_payload="plain text output",
            )

        finished = exporter.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert attrs["input.value"] == "plain text input"
        assert attrs["langfuse.observation.input"] == "plain text input"
        assert attrs["output.value"] == "plain text output"
        assert attrs["langfuse.observation.output"] == "plain text output"

        # Non-recording span
        mock_span = _create_mock_non_recording_span()
        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            adapter.record_stage_io("in", "out")
        mock_span.set_attribute.assert_not_called()

    def test_record_session_output_non_recording_span(self) -> None:
        from unittest.mock import patch

        adapter = OpenTelemetryAdapter()
        mock_span = _create_mock_non_recording_span()
        with patch("opentelemetry.trace.get_current_span", return_value=mock_span):
            adapter.record_session_output({"status": "OK"})
        mock_span.set_attribute.assert_not_called()

    def test_open_telemetry_adapter_init_defaults(self) -> None:
        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            DEFAULT_PIPELINE_VERSION,
        )

        adapter = OpenTelemetryAdapter()
        assert adapter._tracer is not None
        assert adapter._pipeline_version == DEFAULT_PIPELINE_VERSION
        assert adapter._langfuse is None

        adapter2 = OpenTelemetryAdapter(pipeline_version="custom:v99")
        assert adapter2._pipeline_version == "custom:v99"

    def test_flush_exceptions_and_fallbacks(self) -> None:
        from unittest.mock import MagicMock, patch

        from cresmo.infrastructure.adapters.opentelemetry_adapter import (
            OTEL_FLUSH_TIMEOUT_MS,
        )

        # 1. client is None, get_client() succeeds, flush succeeds
        mock_client = MagicMock()
        adapter = OpenTelemetryAdapter(langfuse_client=None)
        with (
            patch("langfuse.get_client", return_value=mock_client),
            patch("opentelemetry.trace.get_tracer_provider") as mock_gtp,
        ):
            mock_tp = MagicMock()
            mock_gtp.return_value = mock_tp
            adapter.flush()
            mock_client.flush.assert_called_once()
            mock_tp.force_flush.assert_called_once_with(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)

        # 2. client.flush() raises Exception, tracer_provider.force_flush raises Exception
        mock_bad_client = MagicMock()
        mock_bad_client.flush.side_effect = RuntimeError("langfuse flush crash")
        adapter_bad = OpenTelemetryAdapter(langfuse_client=mock_bad_client)
        with patch("opentelemetry.trace.get_tracer_provider") as mock_gtp:
            mock_tp = MagicMock()
            mock_tp.force_flush.side_effect = RuntimeError("tp flush crash")
            mock_gtp.return_value = mock_tp
            adapter_bad.flush()  # does not raise

        # 3. tracer_provider has non-callable force_flush
        with patch("opentelemetry.trace.get_tracer_provider") as mock_gtp:
            mock_tp = MagicMock()
            mock_tp.force_flush = "not_callable"
            mock_gtp.return_value = mock_tp
            adapter_bad.flush()  # does not raise

    def test_record_score_inside_span_preserves_explicit_observation_id(self) -> None:
        from unittest.mock import MagicMock

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        mock_langfuse = MagicMock()
        adapter = OpenTelemetryAdapter(tracer=tracer, langfuse_client=mock_langfuse)

        with tracer.start_as_current_span("parent_span"):
            adapter.record_score(
                name="precision",
                value=0.99,
                observation_id="explicit_obs_id_keep",
            )

        mock_langfuse.score.assert_called_once_with(
            name="precision",
            value=0.99,
            observation_id="explicit_obs_id_keep",
        )

    def test_record_judge_evaluation_passes_verdict_to_metric(self) -> None:
        from unittest.mock import MagicMock, patch

        mock_langfuse = MagicMock()
        adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)
        session_id = PipelineSessionId.create(channel="sandeco", content_id="c123")
        content_id = ContentId("c123")

        with patch(
            "cresmo.infrastructure.adapters.opentelemetry_adapter.JudgeFrictionMetric",
            wraps=JudgeFrictionMetric,
        ) as mock_jfm:
            adapter.record_judge_evaluation(
                session_id=session_id,
                content_id=content_id,
                iteration=2,
                max_iterations=3,
                verdict="PASS",
            )
            mock_jfm.assert_called_once_with(iterations=2, max_iterations=3, verdict="PASS")

    def test_open_telemetry_adapter_init_calls_tracer_and_thread_naming(self) -> None:
        from unittest.mock import MagicMock, patch

        mock_client = MagicMock()
        with (
            patch("opentelemetry.trace.get_tracer") as mock_get_tracer,
            patch(
                "cresmo.infrastructure.adapters.opentelemetry_adapter.name_telemetry_threads"
            ) as mock_name_threads,
        ):
            OpenTelemetryAdapter(langfuse_client=mock_client)
            mock_get_tracer.assert_called_once_with("cresmo.pipeline")
            mock_name_threads.assert_called_once_with(mock_client)

    def test_flush_tracer_provider_without_force_flush_attribute(self) -> None:
        from unittest.mock import MagicMock, patch

        adapter = OpenTelemetryAdapter()
        mock_tp = MagicMock(spec=[])
        assert not hasattr(mock_tp, "force_flush")
        with (
            patch("opentelemetry.trace.get_tracer_provider", return_value=mock_tp),
            patch("cresmo.infrastructure.adapters.opentelemetry_adapter.logger.debug") as mock_debug,
        ):
            adapter.flush()
            mock_debug.assert_not_called()

    def test_flush_when_get_client_raises_does_not_log_client_flush_skip(self) -> None:
        from unittest.mock import MagicMock, patch

        adapter = OpenTelemetryAdapter(langfuse_client=None)
        mock_tp = MagicMock(spec=[])
        with (
            patch("langfuse.get_client", side_effect=ImportError("No langfuse")),
            patch("cresmo.infrastructure.adapters.opentelemetry_adapter.logger.debug") as mock_debug,
            patch("opentelemetry.trace.get_tracer_provider", return_value=mock_tp),
        ):
            adapter.flush()
            mock_debug.assert_not_called()

    def test_telemetry_methods_log_debug_on_exceptions(self) -> None:
        from unittest.mock import MagicMock, patch

        err = RuntimeError("telemetry failure")
        mock_langfuse = MagicMock()
        mock_langfuse.score.side_effect = err
        mock_langfuse.flush.side_effect = err
        adapter = OpenTelemetryAdapter(langfuse_client=mock_langfuse)
        session_id = PipelineSessionId.create(channel="chan", content_id="c1")
        content_id = ContentId("c1")

        with patch("cresmo.infrastructure.adapters.opentelemetry_adapter.logger.debug") as mock_debug:
            adapter.record_score("score1", 0.5)
            mock_debug.assert_called_with(
                "[OpenTelemetryAdapter] Langfuse score emission skipped: %s", err
            )

            mock_debug.reset_mock()
            adapter.record_judge_evaluation(session_id, content_id, 1, 1, "PASS")
            mock_debug.assert_called_with(
                "[OpenTelemetryAdapter] Langfuse score emission skipped: %s", err
            )

            mock_debug.reset_mock()
            adapter.record_session_coherence(session_id, content_id, 0.8)
            mock_debug.assert_called_with(
                "[OpenTelemetryAdapter] Langfuse score emission skipped: %s", err
            )

            mock_debug.reset_mock()
            adapter.flush()
            mock_debug.assert_called_with(
                "[OpenTelemetryAdapter] Langfuse client flush skipped: %s", err
            )

            mock_debug.reset_mock()
            mock_tp = MagicMock()
            err_tp = RuntimeError("tp flush error")
            mock_tp.force_flush.side_effect = err_tp
            with patch("opentelemetry.trace.get_tracer_provider", return_value=mock_tp):
                adapter.flush()
                mock_debug.assert_called_with(
                    "[OpenTelemetryAdapter] OpenTelemetry tracer provider flush skipped: %s", err_tp
                )

