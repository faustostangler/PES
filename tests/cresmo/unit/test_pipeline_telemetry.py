"""Integration tests for CresmoPipeline OpenTelemetry Semantic Conventions.

Conforms to ADR-016:
    - Verifies complete Session Replay span hierarchy across pipeline stages.
    - Verifies root span contains langfuse.session.id and langfuse.user.id.
    - Verifies child stage spans inherit trace context from the root span.
    - Verifies session coherence evaluation is recorded on the root span.
"""

from __future__ import annotations

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from cresmo.application.pipeline import CresmoPipeline
from cresmo.domain.entities import RawTranscript, UserIdentity
from cresmo.domain.value_objects import ChannelName, ContentId
from cresmo.infrastructure.adapters.opentelemetry_adapter import OpenTelemetryAdapter
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from tests.cresmo.unit.test_pipeline import SmartMockLLMAdapter
from tests.doubles.mock_adapters import (
    InMemoryLedgerAdapter,
    InMemoryVaultAdapter,
    MockMediaIngestionPort,
)


class TestPipelineTelemetryIntegration:
    """Test end-to-end telemetry generation during pipeline synthesis."""

    @pytest.fixture
    def telemetry_pipeline(
        self,
    ) -> tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter]:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.pipeline.test")

        telemetry_adapter = OpenTelemetryAdapter(tracer=tracer)

        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()
        llm_port = SmartMockLLMAdapter()
        media_port = MockMediaIngestionPort()
        prompt_provider = JsonPromptProvider()

        pipeline = CresmoPipeline(
            media_ingestion_port=media_port,
            llm_port=llm_port,
            vault_port=vault_port,
            ledger_port=ledger_port,
            prompt_provider=prompt_provider,
            telemetry_port=telemetry_adapter,
        )

        return pipeline, exporter, vault_port

    def test_synthesize_transcript_generates_full_span_hierarchy(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = RawTranscript(
            content_id=ContentId("yt_sample1234"),
            channel_name=ChannelName("sandeco"),
            body="Aula completa sobre modelos transformadores e atenção multi-cabeça em deep learning.",
            title="Modelos Transformadores",
        )

        result = pipeline._synthesize_transcript(raw=raw, gap_filler_passes=1)

        assert result.success is True

        spans = exporter.get_finished_spans()
        assert len(spans) >= 6  # Root + child stage spans

        # Identify root span
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")
        assert root_span.attributes is not None
        assert root_span.context is not None
        assert root_span.attributes["langfuse.session.id"] == "content:sandeco:yt_sample1234"
        assert root_span.attributes["langfuse.user.id"] == "anonymous"
        assert root_span.attributes["cresmo.content_id"] == "yt_sample1234"
        assert root_span.attributes["cresmo.channel"] == "sandeco"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.user.is_anonymous"] is True
        assert root_span.attributes["cresmo.user.provider"] == "anonymous"

        # Check all child stage spans are tied to the root trace_id
        stage_names = {
            "cresmo.stage.raw_indexing",
            "cresmo.stage.fluid_prose",
            "cresmo.stage.expansion",
            "cresmo.stage.inventory",
            "cresmo.stage.atomic_batch",
            "cresmo.stage.mocs",
            "cresmo.stage.duplicate_unification",
        }

        finished_stage_names = {s.name for s in spans if s.name.startswith("cresmo.stage.")}
        assert stage_names.issubset(finished_stage_names)

        for span in spans:
            if span.name.startswith("cresmo.stage."):
                assert span.context is not None
                assert span.parent is not None
                assert span.context.trace_id == root_span.context.trace_id
                assert span.parent.span_id == root_span.context.span_id

        # Check session coherence event recorded on root span
        coherence_events = [e for e in root_span.events if e.name == "session_coherence"]
        assert len(coherence_events) == 1
        assert coherence_events[0].attributes is not None
        assert "eval.coherence_score" in coherence_events[0].attributes
        assert coherence_events[0].attributes["eval.session_id"] == "content:sandeco:yt_sample1234"

    def test_synthesize_transcript_with_identified_user(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = RawTranscript(
            content_id=ContentId("yt_auth_test_01"),
            channel_name=ChannelName("acropole"),
            body="Aula completa sobre filosofia e estoicismo clássico em Atenas e Roma.",
            title="Estoicismo Clássico",
        )

        user = UserIdentity.identified(subject="fausto@cresmo.ai", provider="oauth")
        result = pipeline._synthesize_transcript(raw=raw, gap_filler_passes=1, user=user)

        assert result.success is True

        spans = exporter.get_finished_spans()
        root_span = next(
            s
            for s in spans
            if s.name == "cresmo.pipeline.execution"
            and s.attributes is not None
            and s.attributes.get("cresmo.content_id") == "yt_auth_test_01"
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "content:acropole:yt_auth_test_01"
        assert root_span.attributes["langfuse.user.id"] == "user:oauth:fausto@cresmo.ai"
        assert root_span.attributes["cresmo.channel"] == "acropole"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:acropole"
        assert root_span.attributes["cresmo.user.is_anonymous"] is False
        assert root_span.attributes["cresmo.user.provider"] == "oauth"
        assert root_span.attributes["cresmo.user.subject"] == "fausto@cresmo.ai"

    def test_pipeline_records_prometheus_metrics_on_stages(self) -> None:
        """SPEC-008 Scenario 5: Verifies pipeline records stage duration histograms and counters."""
        from prometheus_client import CollectorRegistry

        from cresmo.infrastructure.adapters.prometheus_metrics_adapter import (
            PrometheusMetricsAdapter,
        )

        registry = CollectorRegistry(auto_describe=True)
        metrics_adapter = PrometheusMetricsAdapter(registry=registry)

        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()
        llm_port = SmartMockLLMAdapter()
        media_port = MockMediaIngestionPort()
        prompt_provider = JsonPromptProvider()

        pipeline = CresmoPipeline(
            media_ingestion_port=media_port,
            llm_port=llm_port,
            vault_port=vault_port,
            ledger_port=ledger_port,
            prompt_provider=prompt_provider,
            metrics_port=metrics_adapter,
        )

        raw = RawTranscript(
            content_id=ContentId("yt_metrics_test_01"),
            channel_name=ChannelName("sandeco"),
            body="Aula completa sobre arquitetura hexagonal e métricas de observabilidade.",
            title="Arquitetura Hexagonal",
        )

        result = pipeline.execute(raw=raw, gap_filler_passes=1)
        assert result.success is True

        # Check transcript counter
        transcript_sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {"channel": "sandeco", "status": "completed", "modality": "transcript"},
        )
        assert transcript_sample == 1.0

        # Check atomic notes counter
        notes_sample = registry.get_sample_value(
            "cresmo_atomic_notes_synthesized_total",
            {"channel": "sandeco", "note_type": "all"},
        )
        assert notes_sample is not None and notes_sample >= 1.0

        # Check stage duration histograms
        for stage in (
            "fluid_prose",
            "expansion",
            "inventory",
            "atomic_batch",
            "mocs",
            "duplicate_unification",
        ):
            count = registry.get_sample_value(
                "cresmo_pipeline_stage_duration_seconds_count",
                {"stage": stage, "channel": "sandeco", "status": "success"},
            )
            assert count == 1.0, f"Stage {stage} should have 1 histogram observation"
