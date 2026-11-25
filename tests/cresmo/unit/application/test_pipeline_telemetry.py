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

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.domain.entities import StageTranscript, UserIdentity
from cresmo.domain.value_objects import (
    BatchId,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import OpenTelemetryAdapter
from tests.cresmo.unit.application.test_pipeline import SmartMockLLMAdapter
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

        from cresmo.application.pipeline.models import PipelineDependencies
        from cresmo.application.pipeline.stage_factory import StageFactory
        from cresmo.application.pipeline.stage_runner import PipelineStageRunner
        from cresmo.application.ports import NoOpMetricsPort
        from cresmo.domain.value_objects import StageExecutionPolicy

        runner = PipelineStageRunner(
            PipelineDependencies(
                telemetry_port=telemetry_adapter,
                metrics_port=NoOpMetricsPort(),
                llm_transformation_port=llm_port,
                prompt_provider=prompt_provider,
                stage_factory=StageFactory(policy=StageExecutionPolicy()),
            )
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=media_port,
            vault_port=vault_port,
            stage_runner=runner,
            ledger_port=ledger_port,
            telemetry_port=telemetry_adapter,
        )

        return pipeline, exporter, vault_port

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_execute_generates_full_span_hierarchy(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = StageTranscript(
            channel=Channel(name=ChannelName("sandeco")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_sample1234').value}"
            ),
            content=Content(
                id=ContentId("yt_sample1234"),
                title="Modelos Transformadores",
                text="Aula completa sobre modelos transformadores e atenção multi-cabeça em deep learning.",
            ),
        )

        result = pipeline.execute(raw=raw, expansion_max_passes=1)

        assert result.success is True

        spans = exporter.get_finished_spans()
        assert len(spans) >= 6  # Root + child stage spans

        # Identify root span
        root_span = next(s for s in spans if s.name == "cresmo.coordinator")
        assert root_span.attributes is not None
        assert root_span.context is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:yt_sample1234"
        assert root_span.attributes["langfuse.user.id"] == "anonymous"
        assert root_span.attributes["cresmo.content.id"] == "yt_sample1234"
        assert root_span.attributes["cresmo.video.id"] == "yt_sample1234"
        assert root_span.attributes["cresmo.content.title"] == "Modelos Transformadores"
        assert root_span.attributes["cresmo.channel.name"] == "sandeco"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:sandeco"
        assert root_span.attributes["cresmo.user.is_anonymous"] is True
        assert root_span.attributes["cresmo.user.provider"] == "anonymous"
        assert "cresmo.content_id" not in root_span.attributes
        assert "cresmo.channel" not in root_span.attributes

        # Check all child stage spans are tied to the root trace_id
        stage_names = {
            "cresmo.raw_indexing",
            "cresmo.fluid_prose",
            "cresmo.expansion",
            "cresmo.inventory",
            "cresmo.atomic_batch",
            "cresmo.mocs",
            "cresmo.duplicate_unification",
        }

        finished_stage_names = {s.name for s in spans if s.name != "cresmo.coordinator"}
        assert stage_names.issubset(finished_stage_names)

        for span in spans:
            if span.name != "cresmo.coordinator":
                assert span.context is not None
                assert span.parent is not None
                assert span.context.trace_id == root_span.context.trace_id
                assert span.parent.span_id == root_span.context.span_id

        # Check session coherence event recorded on root span
        coherence_events = [e for e in root_span.events if e.name == "session_coherence"]
        assert len(coherence_events) == 1
        assert coherence_events[0].attributes is not None
        assert "eval.coherence_score" in coherence_events[0].attributes
        assert coherence_events[0].attributes["eval.session_id"] == "sandeco:yt_sample1234"

    def test_execute_with_identified_user(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = StageTranscript(
            channel=Channel(name=ChannelName("acropole")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_auth_test_01').value}"
            ),
            content=Content(
                id=ContentId("yt_auth_test_01"),
                title="Estoicismo Clássico",
                text="Aula completa sobre filosofia e estoicismo clássico em Atenas e Roma.",
            ),
        )

        user = UserIdentity.worker(name="fausto_operator")
        result = pipeline.execute(raw=raw, expansion_max_passes=1, user=user)

        assert result.final_transcript is not None

        spans = exporter.get_finished_spans()
        root_span = next(
            s
            for s in spans
            if s.name == "cresmo.coordinator"
            and s.attributes is not None
            and s.attributes.get("cresmo.content.id") == "yt_auth_test_01"
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "acropole:yt_auth_test_01"
        assert root_span.attributes["langfuse.user.id"] == "system:fausto_operator"
        assert root_span.attributes["cresmo.channel.name"] == "acropole"
        assert root_span.attributes["cresmo.content.title"] == "Estoicismo Clássico"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:acropole"
        assert root_span.attributes["cresmo.user.is_anonymous"] is False
        assert root_span.attributes["cresmo.user.provider"] == "system"
        assert root_span.attributes["cresmo.user.subject"] == "fausto_operator"
        assert "cresmo.channel" not in root_span.attributes
        assert "cresmo.content_id" not in root_span.attributes

    def test_execute_with_worker_identity(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = StageTranscript(
            channel=Channel(name=ChannelName("sandeco")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_worker_test_01').value}"
            ),
            content=Content(
                id=ContentId("yt_worker_test_01"),
                title="Automação com Workers",
                text="Aula sobre agentes e automação de pipelines com worker agendado.",
            ),
        )

        user = UserIdentity.worker()
        result = pipeline.execute(raw=raw, expansion_max_passes=1, user=user)

        assert result.final_transcript is not None

        spans = exporter.get_finished_spans()
        root_span = next(
            s
            for s in spans
            if s.name == "cresmo.coordinator"
            and s.attributes is not None
            and s.attributes.get("cresmo.content.id") == "yt_worker_test_01"
        )
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.session.id"] == "sandeco:yt_worker_test_01"
        assert root_span.attributes["langfuse.user.id"] == "system:worker"
        assert root_span.attributes["cresmo.user.is_anonymous"] is False
        assert root_span.attributes["cresmo.user.provider"] == "system"
        assert root_span.attributes["cresmo.user.subject"] == "worker"

    def test_execute_propagates_channel_id_to_telemetry_span(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        pipeline, exporter, _ = telemetry_pipeline

        raw = StageTranscript(
            channel=Channel(name=ChannelName("acropole"), id=ChannelId("UC_acropole123")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_chan_id_01').value}"
            ),
            content=Content(
                id=ContentId("yt_chan_id_01"),
                title="Estoicismo e Virtude",
                text="Aula completa sobre filosofia e estoicismo clássico em Atenas e Roma.",
            ),
        )

        result = pipeline.execute(raw=raw, expansion_max_passes=1)

        assert result.final_transcript is not None

        spans = exporter.get_finished_spans()
        root_span = next(
            s
            for s in spans
            if s.name == "cresmo.coordinator"
            and s.attributes is not None
            and s.attributes.get("cresmo.content.id") == "yt_chan_id_01"
        )
        assert root_span.attributes is not None
        # Algorithmic keys use stable ChannelId
        assert root_span.attributes["langfuse.session.id"] == "UC_acropole123:yt_chan_id_01"
        assert root_span.attributes["cresmo.tenant_id"] == "channel:UC_acropole123"
        assert root_span.attributes["cresmo.channel.id"] == "UC_acropole123"
        # Cognitive keys use human-readable Name/Title
        assert root_span.attributes["cresmo.channel.name"] == "acropole"
        assert root_span.attributes["cresmo.content.title"] == "Estoicismo e Virtude"
        assert "cresmo.channel" not in root_span.attributes
        assert "cresmo.channel_id" not in root_span.attributes
        assert "cresmo.content_id" not in root_span.attributes

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_pipeline_records_prometheus_metrics_on_stages(self) -> None:
        """SPEC-008 Scenario 5: Verifies pipeline records stage duration histograms and counters."""
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import InMemoryMetricReader

        from cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter import (
            OtlpMetricsAdapter,
        )

        reader = InMemoryMetricReader()
        metrics_adapter = OtlpMetricsAdapter(meter_provider=MeterProvider(metric_readers=[reader]))

        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()
        llm_port = SmartMockLLMAdapter()
        media_port = MockMediaIngestionPort()
        prompt_provider = JsonPromptProvider()

        from cresmo.application.pipeline.models import PipelineDependencies
        from cresmo.application.pipeline.stage_factory import StageFactory
        from cresmo.application.pipeline.stage_runner import PipelineStageRunner
        from cresmo.application.ports import NoOpTelemetryPort
        from cresmo.domain.value_objects import StageExecutionPolicy

        runner = PipelineStageRunner(
            PipelineDependencies(
                telemetry_port=NoOpTelemetryPort(),
                metrics_port=metrics_adapter,
                llm_transformation_port=llm_port,
                prompt_provider=prompt_provider,
                stage_factory=StageFactory(policy=StageExecutionPolicy()),
            )
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=media_port,
            vault_port=vault_port,
            stage_runner=runner,
            ledger_port=ledger_port,
            metrics_port=metrics_adapter,
        )

        raw = StageTranscript(
            channel=Channel(name=ChannelName("sandeco"), id=ChannelId("UC_sandeco_test")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_metrics_test_01').value}"
            ),
            content=Content(
                id=ContentId("yt_metrics_test_01"),
                title="Arquitetura Hexagonal",
                text="Aula completa sobre arquitetura hexagonal e métricas de observabilidade.",
            ),
        )

        result = pipeline.execute(raw=raw, expansion_max_passes=1)
        assert result.success is True

        # Check transcript counter (low-cardinality labels only)
        data = reader.get_metrics_data()
        assert data is not None
        samples: dict[str, list[tuple[dict[str, object], float | int]]] = {}
        for rm in data.resource_metrics:
            for sm in rm.scope_metrics:
                for metric in sm.metrics:
                    points: list[tuple[dict[str, object], float | int]] = []
                    for dp in metric.data.data_points:
                        val = getattr(dp, "value", None)
                        if val is None:
                            val = getattr(dp, "count", 0)
                        points.append((dict(dp.attributes or {}), val))
                    samples[metric.name] = points

        transcript_points = samples.get("cresmo_transcripts_processed_total", [])
        assert (
            {
                "channel_id": "UC_sandeco_test",
                "status": "completed",
                "modality": "transcript",
            },
            1.0,
        ) in transcript_points

        # Check stage duration histograms
        stage_points = samples.get("cresmo_pipeline_stage_duration_seconds", [])
        for stage in (
            "fluid_prose",
            "expansion",
            "inventory",
            "atomic_batch",
            "mocs",
            "duplicate_unification",
        ):
            assert (
                {
                    "stage": stage,
                    "channel_id": "UC_sandeco_test",
                    "status": "success",
                },
                1,
            ) in stage_points, f"Stage {stage} should have 1 histogram observation"

    def test_pipeline_execute_propagates_batch_id_adr035(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        """Verify ADR-035: CresmoPipeline.execute propagates batch_id to root span."""
        pipeline, exporter, _ = telemetry_pipeline

        raw = StageTranscript(
            channel=Channel(name=ChannelName("sandeco")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_batch_test').value}"
            ),
            content=Content(
                id=ContentId("yt_batch_test"),
                title="Batch ID Test",
                text="Texto para teste de batch_id.",
            ),
        )

        batch_id = BatchId.generate()
        result = pipeline.execute(raw=raw, batch_id=batch_id)

        assert result.final_transcript is not None

        spans = exporter.get_finished_spans()
        root_span = next(s for s in spans if s.name == "cresmo.coordinator")
        assert root_span.attributes is not None
        assert root_span.attributes["cresmo.batch_id"] == batch_id.value
        tags = root_span.attributes["langfuse.trace.tags"]
        assert isinstance(tags, (list, tuple))
        assert f"batch:{batch_id.value}" in tags

    def test_execute_emits_hierarchical_coordinator_and_stage_spans_adr065(
        self,
        telemetry_pipeline: tuple[CresmoPipeline, InMemorySpanExporter, InMemoryVaultAdapter],
    ) -> None:
        """Verify active conveyor emits cresmo.pipeline -> cresmo.coordinator -> cresmo.{stage_name}."""
        from cresmo.application.ports.telemetry import _get_active_telemetry_stage

        pipeline, exporter, _ = telemetry_pipeline
        observed_stages_during_transform: list[str | None] = []
        assert pipeline.stage_runner.llm_transformation_port is not None
        original_transform = pipeline.stage_runner.llm_transformation_port.transform

        def _spy_transform(*args: object, **kwargs: object) -> str:
            observed_stages_during_transform.append(_get_active_telemetry_stage())
            return original_transform(*args, **kwargs)  # type: ignore[arg-type]

        pipeline.stage_runner.llm_transformation_port.transform = _spy_transform  # type: ignore[method-assign]

        raw = StageTranscript(
            channel=Channel(name=ChannelName("sandeco")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('yt_adr065_01').value}"
            ),
            content=Content(
                id=ContentId("yt_adr065_01"),
                title="Hierarquia de Telemetria",
                text="Aula completa sobre hierarquia de spans no pipeline Cresmo.",
            ),
        )

        result = pipeline.execute(raw=raw, expansion_max_passes=1)
        assert result.final_transcript is not None
        assert _get_active_telemetry_stage() is None
        assert "fluid_prose" in observed_stages_during_transform
        assert "gap_filler" in observed_stages_during_transform
        assert "long_expander" in observed_stages_during_transform
        assert "wide_expander" in observed_stages_during_transform

        spans = exporter.get_finished_spans()
        root_span = next(s for s in spans if s.name == "cresmo.coordinator")
        assert root_span.attributes is not None
        assert root_span.attributes["langfuse.trace.name"] == "cresmo.pipeline"

        child_spans = {s.name: s for s in spans if s.name != "cresmo.coordinator"}
        assert {
            "cresmo.fluid_prose",
            "cresmo.gap_filler",
            "cresmo.long_expander",
            "cresmo.wide_expander",
        }.issubset(child_spans.keys())
        assert root_span.context is not None
        for child_name in (
            "cresmo.fluid_prose",
            "cresmo.gap_filler",
            "cresmo.long_expander",
            "cresmo.wide_expander",
        ):
            child_span = child_spans[child_name]
            assert child_span.context is not None
            assert child_span.parent is not None
            assert child_span.context.trace_id == root_span.context.trace_id
            assert child_span.parent.span_id == root_span.context.span_id
