"""Comprehensive unit & OTel SDK tests for OpenTelemetryAdapter and NoOpTelemetryPort (ADR-070)."""

from __future__ import annotations

import logging
from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from cresmo.application.ports.telemetry import (
    LLM_GENERATION_FALLBACK_SPAN_NAME,
    LLM_GENERATION_SPAN_NAME,
    NOOP_TELEMETRY_SPAN,
    PIPELINE_ROOT_SPAN_NAME,
    PIPELINE_TRACE_NAME,
    NoOpTelemetryPort,
    SessionTelemetrySpec,
    SpanKind,
    active_telemetry_pass,
    active_telemetry_stage,
    format_stage_generation_span_name,
    format_stage_judge_span_name,
    format_stage_saturation_span_name,
    format_stage_span_name,
    get_active_telemetry_pass,
    get_active_telemetry_stage,
    resolve_llm_generation_span_name,
)
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import (
    DEFAULT_PIPELINE_VERSION,
    OTEL_FLUSH_TIMEOUT_MS,
    OpenTelemetryAdapter,
)


@pytest.fixture
def otel_harness() -> tuple[OpenTelemetryAdapter, InMemorySpanExporter, MagicMock]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("cresmo.pipeline")
    mock_langfuse = MagicMock()
    adapter = OpenTelemetryAdapter(
        tracer=tracer,
        langfuse_client=mock_langfuse,
        pipeline_version="cresmo:v0.1.0",
        git_sha="1234567890abcdef",
    )
    return adapter, exporter, mock_langfuse


class TestTelemetryNamingAndContextVars:
    """Verify ADR-065 hierarchical naming and contextvars scoping."""

    def test_formatting_and_validation_boundaries(self) -> None:
        assert format_stage_span_name(" fluid_prose ") == "cresmo.fluid_prose"
        assert format_stage_judge_span_name("gap_filler") == "cresmo.gap_filler.judge"
        assert format_stage_saturation_span_name("gap_filler") == "cresmo.gap_filler.saturation"
        assert (
            format_stage_saturation_span_name("gap_filler", pass_num=2)
            == "cresmo.gap_filler.saturation.pass_2"
        )
        assert format_stage_generation_span_name("fluid_prose") == "cresmo.fluid_prose.generate"
        assert (
            format_stage_generation_span_name("fluid_prose", fallback=True, pass_num=2)
            == "cresmo.fluid_prose.generate_fallback.pass_2"
        )
        assert format_stage_generation_span_name(None) == LLM_GENERATION_SPAN_NAME
        assert (
            format_stage_generation_span_name("   ", fallback=True)
            == LLM_GENERATION_FALLBACK_SPAN_NAME
        )

        with pytest.raises(ValueError, match="stage_name must be a non-empty string"):
            format_stage_span_name("   ")

        with pytest.raises(ValueError, match="pass_num must be a positive integer"):
            format_stage_saturation_span_name("gap_filler", pass_num=0)

        with pytest.raises(ValueError, match="pass_num must be a positive integer"):
            format_stage_saturation_span_name("gap_filler", pass_num=True)

    def test_nested_stage_and_pass_contextvars_isolation(self) -> None:
        assert get_active_telemetry_stage() is None
        assert get_active_telemetry_pass() is None
        assert resolve_llm_generation_span_name() == "cresmo.llm.generate"

        with active_telemetry_stage("gap_filler"):
            assert get_active_telemetry_stage() == "gap_filler"
            with active_telemetry_pass(2):
                assert get_active_telemetry_pass() == 2
                assert resolve_llm_generation_span_name() == "cresmo.gap_filler.generate.pass_2"
                assert (
                    resolve_llm_generation_span_name(fallback=True)
                    == "cresmo.gap_filler.generate_fallback.pass_2"
                )
                with active_telemetry_stage("nested_stage"):
                    assert get_active_telemetry_stage() == "nested_stage"
                    assert get_active_telemetry_pass() is None
                    assert resolve_llm_generation_span_name() == "cresmo.nested_stage.generate"
                assert get_active_telemetry_stage() == "gap_filler"
                assert get_active_telemetry_pass() == 2
            assert get_active_telemetry_pass() is None
        assert get_active_telemetry_stage() is None


class TestOpenTelemetryAdapterSessionsAndSpans:
    """Verify full OTel span hierarchy, attributes, I/O, errors, and post-span flushing."""

    def test_start_session_and_nested_spans_emit_adr065_tree(
        self,
        otel_harness: tuple[OpenTelemetryAdapter, InMemorySpanExporter, MagicMock],
    ) -> None:
        adapter, exporter, mock_langfuse = otel_harness
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("UC_chan:vid_42"),
            user_id=UserIdentity.identified(subject="fausto@cresmo.ai", provider="oauth"),
            channel_tenant_id="channel:UC_chan",
            trace_name=PIPELINE_TRACE_NAME,
            channel_id="UC_chan",
            channel_name="Channel Name",
            content_id="vid_42",
            content_title="Clean Architecture",
            source="transcript",
            raw_characters=500,
            raw_words=90,
            expansion_max_passes=3,
            force_reprocess=False,
            batch_id="batch_xyz",
            video_url="https://youtube.com/watch?v=vid_42",
            publication_date="2026-01-15",
        )

        with (
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.propagate_attributes",
                return_value=nullcontext(),
            ) as mock_prop,
            adapter.start_session(spec) as root_span,
        ):
            assert root_span.trace_id is not None
            assert root_span.span_id is not None
            assert adapter.current_span().span_id == root_span.span_id

            with adapter.start_span(
                "cresmo.fluid_prose",
                stage_name="fluid_prose",
                attributes={"cresmo.stage.content.id": "vid_42"},
                flush_on_exit=True,
            ) as stage_span:
                assert get_active_telemetry_stage() == "fluid_prose"
                stage_span.set_input({"stage_name": "fluid_prose"})
                with adapter.start_span(
                    "cresmo.fluid_prose.generate",
                    kind=SpanKind.GENERATION,
                    attributes={"gen_ai.system": "google", "gen_ai.request.model": "gemini-3.5"},
                ) as gen_span:
                    gen_span.set_output("Generated prose")
                stage_span.set_output({"status": "APPROVED"})

            assert get_active_telemetry_stage() is None
            root_span.set_output({"status": "COMPLETED", "word_count": 120})

        mock_prop.assert_called_once()
        prop_kwargs = mock_prop.call_args.kwargs
        assert prop_kwargs["session_id"] == "UC_chan:vid_42"
        assert prop_kwargs["user_id"] == "user:oauth:fausto@cresmo.ai"
        assert prop_kwargs["trace_name"] == PIPELINE_TRACE_NAME
        assert "git:12345678" in prop_kwargs["tags"]
        assert "batch:batch_xyz" in prop_kwargs["tags"]
        # Stage flush + root session flush
        assert mock_langfuse.flush.call_count == 2

        spans = {s.name: s for s in exporter.get_finished_spans()}
        assert set(spans.keys()) == {
            PIPELINE_ROOT_SPAN_NAME,
            "cresmo.fluid_prose",
            "cresmo.fluid_prose.generate",
        }
        root = spans[PIPELINE_ROOT_SPAN_NAME]
        stage = spans["cresmo.fluid_prose"]
        gen = spans["cresmo.fluid_prose.generate"]

        assert root.attributes is not None
        assert root.attributes["langfuse.trace.name"] == PIPELINE_TRACE_NAME
        assert root.attributes["cresmo.pipeline.version"] == "cresmo:v0.1.0"
        assert root.attributes["cresmo.pipeline.git_sha"] == "12345678"
        assert root.attributes["cresmo.output.status"] == "COMPLETED"
        assert root.attributes["cresmo.output.word_count"] == "120"
        assert "langfuse.trace.input" in root.attributes
        assert "langfuse.trace.output" in root.attributes
        assert not any(k.startswith("langfuse.input.") for k in root.attributes)

        assert stage.parent is not None and root.context is not None
        assert stage.parent.span_id == root.context.span_id
        assert stage.attributes is not None
        assert stage.attributes["langfuse.observation.type"] == "span"
        assert stage.attributes["cresmo.stage.content.id"] == "vid_42"

        assert gen.parent is not None and stage.context is not None
        assert gen.parent.span_id == stage.context.span_id
        assert gen.attributes is not None
        assert gen.attributes["langfuse.observation.type"] == "generation"
        assert gen.attributes["gen_ai.system"] == "google"
        assert gen.attributes["langfuse.observation.output"] == "Generated prose"

    def test_start_session_records_error_and_flushes_after_close_on_exception(
        self,
        otel_harness: tuple[OpenTelemetryAdapter, InMemorySpanExporter, MagicMock],
    ) -> None:
        adapter, exporter, mock_langfuse = otel_harness
        order: list[str] = []
        mock_langfuse.flush.side_effect = lambda: order.append(
            f"flush_finished_count={len(exporter.get_finished_spans())}"
        )
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("ch:vid_err"),
            user_id=UserIdentity.worker(),
        )

        with (
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.propagate_attributes",
                side_effect=RuntimeError("propagate broken"),
            ),
            pytest.raises(ValueError, match="pipeline exploded"),
            adapter.start_session(spec),
        ):
            raise ValueError("pipeline exploded")

        # Flush must happen AFTER the root span has closed and been exported
        assert order == ["flush_finished_count=1"]
        root = exporter.get_finished_spans()[0]
        assert root.status.status_code == trace.StatusCode.ERROR
        assert root.attributes is not None
        assert root.attributes["langfuse.observation.level"] == "ERROR"

    def test_start_span_record_exceptions_flag_and_post_span_flush(
        self,
        otel_harness: tuple[OpenTelemetryAdapter, InMemorySpanExporter, MagicMock],
    ) -> None:
        adapter, exporter, mock_langfuse = otel_harness
        order: list[str] = []
        mock_langfuse.flush.side_effect = lambda: order.append(
            f"flush_finished={len(exporter.get_finished_spans())}"
        )

        with (
            pytest.raises(RuntimeError, match="recorded error"),
            adapter.start_span(
                "cresmo.gap_filler",
                attributes={"tuple_attr": ("x", "y"), "ignored_none": None},  # type: ignore[dict-item]
                record_exceptions=True,
                flush_on_exit=True,
            ),
        ):
            raise RuntimeError("recorded error")

        assert order == ["flush_finished=1"]
        s1 = exporter.get_finished_spans()[0]
        assert s1.status.status_code == trace.StatusCode.ERROR
        assert len([e for e in s1.events if e.name == "exception"]) == 1
        assert s1.attributes is not None
        assert tuple(s1.attributes["tuple_attr"]) == ("x", "y")  # type: ignore[arg-type]
        assert "ignored_none" not in s1.attributes

        with (
            pytest.raises(RuntimeError, match="unrecorded error"),
            adapter.start_span("cresmo.silent", record_exceptions=False, flush_on_exit=False),
        ):
            raise RuntimeError("unrecorded error")

        s2 = exporter.get_finished_spans()[1]
        assert s2.status.status_code != trace.StatusCode.ERROR
        assert len([e for e in s2.events if e.name == "exception"]) == 0

    def test_record_score_auto_observation_id_explicit_override_and_fallback_score_method(
        self,
        otel_harness: tuple[OpenTelemetryAdapter, InMemorySpanExporter, MagicMock],
    ) -> None:
        adapter, exporter, mock_langfuse = otel_harness

        with adapter.start_span("cresmo.fluid_prose.judge") as eval_span:
            expected_obs_id = eval_span.span_id
            adapter.record_score(
                name="fluid_prose.orality_removal",
                value=0.92,
                comment="Clean",
                trace_id="trace_1",
            )
            adapter.record_score(
                name="fluid_prose.ner",
                value=0.88,
                observation_id="explicit_obs",
            )

        assert mock_langfuse.create_score.call_count == 2
        mock_langfuse.create_score.assert_any_call(
            name="fluid_prose.orality_removal",
            value=0.92,
            comment="Clean",
            trace_id="trace_1",
            observation_id=expected_obs_id,
        )
        mock_langfuse.create_score.assert_any_call(
            name="fluid_prose.ner",
            value=0.88,
            observation_id="explicit_obs",
        )

        span = exporter.get_finished_spans()[0]
        score_events = [e for e in span.events if e.name == "telemetry_score"]
        assert len(score_events) == 2
        assert dict(score_events[0].attributes or {}) == {
            "score.name": "fluid_prose.orality_removal",
            "score.value": 0.92,
            "score.comment": "Clean",
            "score.trace_id": "trace_1",
            "score.observation_id": expected_obs_id,
        }
        assert dict(score_events[1].attributes or {}) == {
            "score.name": "fluid_prose.ner",
            "score.value": 0.88,
            "score.observation_id": "explicit_obs",
        }

        # Fallback to legacy .score() when .create_score is absent + fail-silent exception handling
        class LegacyLangfuse:
            def __init__(self) -> None:
                self.calls: list[dict[str, object]] = []

            def score(self, **kwargs: object) -> None:
                self.calls.append(kwargs)

        legacy_client = LegacyLangfuse()
        legacy_adapter = OpenTelemetryAdapter(langfuse_client=legacy_client)
        legacy_adapter.record_score(name="session_coherence", value=1.0, comment="done")
        assert legacy_client.calls == [
            {"name": "session_coherence", "value": 1.0, "comment": "done"}
        ]

        # Langfuse object with neither create_score nor score is safely ignored without AttributeError
        no_score_adapter = OpenTelemetryAdapter(langfuse_client=object())
        no_score_adapter.record_score(name="ignored", value=0.5)

    def test_init_uses_default_tracer_name_and_names_telemetry_threads(self) -> None:
        sentinel_lf = object()
        fake_tracer = MagicMock()
        with (
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.trace.get_tracer",
                return_value=fake_tracer,
            ) as mock_get_tracer,
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.name_telemetry_threads"
            ) as mock_name_threads,
        ):
            adapter = OpenTelemetryAdapter(langfuse_client=sentinel_lf)

        assert adapter._tracer is fake_tracer
        mock_get_tracer.assert_called_once_with("cresmo.pipeline")
        mock_name_threads.assert_called_once_with(sentinel_lf)

    def test_record_score_and_flush_fail_silent_resilience(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        broken_lf = MagicMock()
        broken_lf.create_score.side_effect = RuntimeError("score fail")
        broken_lf.flush.side_effect = RuntimeError("lf flush fail")

        adapter = OpenTelemetryAdapter(langfuse_client=broken_lf)
        assert adapter._pipeline_version == DEFAULT_PIPELINE_VERSION
        assert adapter.current_span() is NOOP_TELEMETRY_SPAN

        broken_provider = MagicMock()
        broken_provider.force_flush.side_effect = RuntimeError("otel flush fail")

        with (
            caplog.at_level(logging.DEBUG),
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.trace.get_tracer_provider",
                return_value=broken_provider,
            ),
        ):
            adapter.record_score(name="s", value=0.5)
            adapter.flush()

        broken_provider.force_flush.assert_called_once_with(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)
        messages = [r.getMessage() for r in caplog.records]
        assert "[OpenTelemetryAdapter] Langfuse score emission skipped: score fail" in messages
        assert "[OpenTelemetryAdapter] Langfuse client flush skipped: lf flush fail" in messages
        assert (
            "[OpenTelemetryAdapter] OpenTelemetry tracer provider flush skipped: otel flush fail"
            in messages
        )

        # Provider without force_flush attribute must not raise or log flush-skipped errors
        caplog.clear()
        no_lf_adapter = OpenTelemetryAdapter(langfuse_client=None)
        with (
            caplog.at_level(logging.DEBUG),
            patch(
                "cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter.trace.get_tracer_provider",
                return_value=object(),
            ),
        ):
            no_lf_adapter.flush()

        assert caplog.records == []

    def test_noop_telemetry_port_full_contract(self) -> None:
        noop = NoOpTelemetryPort()
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("ch:vid_noop"),
            user_id=UserIdentity.anonymous(),
        )
        with noop.start_session(spec) as root:
            assert root is NOOP_TELEMETRY_SPAN
            root.set_output({"ok": True})
        with noop.start_span("cresmo.fluid_prose", stage_name="fluid_prose") as stage:
            assert stage is NOOP_TELEMETRY_SPAN
            assert get_active_telemetry_stage() == "fluid_prose"
        assert get_active_telemetry_stage() is None
        assert noop.current_span() is NOOP_TELEMETRY_SPAN
        noop.record_score(name="x", value=1.0)
        noop.flush()
