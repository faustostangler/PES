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
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")

        # Root span must have official Langfuse OTel attributes
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_test_123"
        assert root_span.attributes["langfuse.user.id"] == "channel:sandeco"
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

        # Full symmetric Langfuse input keys (cognitive pair + algorithmic pair + URL)
        assert root_span.attributes["langfuse.input.title"] == "Machiavelli and Modern State"
        assert root_span.attributes["langfuse.input.channel"] == "sandeco"
        assert root_span.attributes["langfuse.input.channel_name"] == "sandeco"
        assert root_span.attributes["langfuse.input.channel_id"] == "UC_Sandeco123"
        assert root_span.attributes["langfuse.input.content_id"] == "vid_test_123"
        assert root_span.attributes["langfuse.input.video_url"] == "https://youtube.com/watch?v=123"
        assert json.loads(str(root_span.attributes["langfuse.input"])) == {
            "title": "Machiavelli and Modern State",
            "channel": "sandeco",
            "channel_name": "sandeco",
            "channel_id": "UC_Sandeco123",
            "content_id": "vid_test_123",
            "video_url": "https://youtube.com/watch?v=123",
        }

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
        user_id = UserIdentity.from_channel("sandeco")

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
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_anon_01"
        assert root_span.attributes["langfuse.user.id"] == "anonymous"
        assert root_span.attributes["cresmo.content.id"] == "vid_anon_01"
        assert "cresmo.video.id" not in root_span.attributes
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
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
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_auth_01"
        assert root_span.attributes["langfuse.user.id"] == "user:google:alice@corp.com"
        assert root_span.attributes["cresmo.content.id"] == "vid_auth_01"
        assert "cresmo.video.id" not in root_span.attributes
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
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
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:vid_worker_01"
        assert root_span.attributes["langfuse.user.id"] == "system:worker"
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


def test_noop_telemetry_adapter_record_score_is_graceful_noop() -> None:
    """Verify NoOpTelemetryAdapter record_score executes gracefully without error."""
    adapter = NoOpTelemetryAdapter()
    adapter.record_score(
        name="style_compliance",
        value=1.0,
        comment="test",
        trace_id="test_trace",
    )


def test_cresmo_root_exports_only_package_metadata() -> None:
    """Verify cresmo package root strictly conforms to ADR-026 Rule 9."""
    import cresmo

    assert hasattr(cresmo, "__version__")
    assert not hasattr(cresmo, "PIPELINE_VERSION")
    assert cresmo.__all__ == ["__version__"]
