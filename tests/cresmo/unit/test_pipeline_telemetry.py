"""Integration tests for CresmoPipeline OpenTelemetry Semantic Conventions.

Conforms to ADR-016:
    - Verifies complete Session Replay span hierarchy across the 6 stages.
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
from cresmo.domain.entities import RawTranscript
from cresmo.domain.value_objects import ContentId
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
            channel_name="sandeco",
            body="Aula completa sobre modelos transformadores e atenção multi-cabeça em deep learning.",
            title="Modelos Transformadores",
        )

        result = pipeline._synthesize_transcript(raw=raw, gap_filler_passes=1)

        assert result.success is True

        spans = exporter.get_finished_spans()
        assert len(spans) >= 6  # Root + at least 5 stage spans

        # Identify root span
        root_span = next(s for s in spans if s.name == "cresmo.pipeline.execution")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "content:sandeco:yt_sample1234"
        assert root_span.attributes["langfuse.user.id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.content_id"] == "yt_sample1234"
        assert root_span.attributes["cresmo.channel"] == "sandeco"

        # Check all child stage spans are tied to the root trace_id
        stage_names = {
            "cresmo.stage.stage2_fluid_prose",
            "cresmo.stage.stage3_expansion",
            "cresmo.stage.stage4_inventory",
            "cresmo.stage.stage5_atomic_batch",
            "cresmo.stage.stage6_mocs",
            "cresmo.stage.stage7_duplicate_unification",
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
