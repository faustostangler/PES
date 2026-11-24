"""Unit tests for OTelTelemetrySpan and GenAI attribute builder (SPEC-070 §2.1 & §2.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import INVALID_SPAN_CONTEXT

from cresmo.application.ports.telemetry import NOOP_TELEMETRY_SPAN, active_telemetry_pass
from cresmo.infrastructure.adapters.telemetry.genai import build_genai_attributes
from cresmo.infrastructure.adapters.telemetry.otel_span import (
    OTelTelemetrySpan,
    wrap_current_otel_span,
)


class TestOTelTelemetrySpan:
    """Verify OTelTelemetrySpan recording, root vs child I/O, events, errors, and non-recording safety."""

    def test_recording_root_span_attributes_io_events_and_errors(self) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("cresmo.coordinator") as raw_span:
            wrapped = OTelTelemetrySpan(raw_span, is_root=True)
            assert wrapped.trace_id is not None and len(wrapped.trace_id) == 32
            assert wrapped.span_id is not None and len(wrapped.span_id) == 16

            wrapped.set_attributes(
                {"str_k": "val", "int_k": 3, "bool_k": True, "tup_k": ("a", "b")}
            )
            wrapped.set_input({"content_id": "vid_1"})
            wrapped.set_output({"status": "COMPLETED", "word_count": 42})
            wrapped.add_event("session_coherence", {"eval.coherence_score": 0.9})
            wrapped.record_error(ValueError("boom"))

        finished = exporter.get_finished_spans()[0]
        attrs = finished.attributes or {}
        assert attrs["str_k"] == "val"
        assert attrs["int_k"] == 3
        assert attrs["bool_k"] is True
        assert tuple(attrs["tup_k"]) == ("a", "b")  # type: ignore[arg-type]

        expected_in = json.dumps({"content_id": "vid_1"})
        assert attrs["input.value"] == expected_in
        assert attrs["langfuse.observation.input"] == expected_in
        assert attrs["langfuse.trace.input"] == expected_in

        expected_out = json.dumps({"status": "COMPLETED", "word_count": 42})
        assert attrs["output.value"] == expected_out
        assert attrs["langfuse.observation.output"] == expected_out
        assert attrs["langfuse.trace.output"] == expected_out
        assert attrs["cresmo.output.status"] == "COMPLETED"
        assert attrs["cresmo.output.word_count"] == "42"
        assert attrs["langfuse.observation.level"] == "ERROR"
        assert finished.status.status_code == trace.StatusCode.ERROR
        assert finished.status.description == "boom"

        events_by_name = {e.name: e for e in finished.events}
        assert "session_coherence" in events_by_name
        assert dict(events_by_name["session_coherence"].attributes or {}) == {
            "eval.coherence_score": 0.9,
        }
        assert "exception" in events_by_name
        exc_attrs = dict(events_by_name["exception"].attributes or {})
        assert exc_attrs["exception.type"] == "ValueError"
        assert exc_attrs["exception.message"] == "boom"

    def test_default_is_root_false_filters_invalid_values_and_serializes_non_json_payloads(
        self,
    ) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("cresmo.default_child") as raw_span:
            wrapped = OTelTelemetrySpan(raw_span)
            wrapped.set_attributes(
                {
                    "valid_float": 1.5,
                    "invalid_none": cast(Any, None),
                    "invalid_tuple": cast(Any, (1, 2)),
                }
            )
            wrapped.set_input({"artifact_path": Path("vault/note.md")})
            wrapped.set_output({"count": 1})
            wrapped.add_event(
                "filtered_event",
                {
                    "ok": "yes",
                    "bad_none": cast(Any, None),
                    "bad_tuple": cast(Any, (1, 2)),
                },
            )

        finished = exporter.get_finished_spans()[0]
        attrs = finished.attributes or {}
        assert attrs["valid_float"] == 1.5
        assert "invalid_none" not in attrs
        assert "invalid_tuple" not in attrs
        assert json.loads(str(attrs["input.value"])) == {"artifact_path": "vault/note.md"}
        assert "langfuse.trace.input" not in attrs
        assert "langfuse.trace.output" not in attrs
        assert not any(k.startswith("cresmo.output.") for k in attrs)

        filtered_event = next(e for e in finished.events if e.name == "filtered_event")
        assert dict(filtered_event.attributes or {}) == {"ok": "yes"}

    def test_root_non_mapping_output_and_zero_context_ids_return_none(self) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("cresmo.root_str") as raw_span:
            wrapped = OTelTelemetrySpan(raw_span, is_root=True)
            wrapped.set_output("plain root summary")

        finished = exporter.get_finished_spans()[0]
        attrs = finished.attributes or {}
        assert attrs["langfuse.trace.output"] == "plain root summary"
        assert not any(k.startswith("cresmo.output.") for k in attrs)

        zero_ctx_span = MagicMock()
        zero_ctx_span.is_recording.return_value = True
        zero_ctx_span.get_span_context.return_value = INVALID_SPAN_CONTEXT
        zero_wrapped = OTelTelemetrySpan(zero_ctx_span)
        assert zero_wrapped.trace_id is None
        assert zero_wrapped.span_id is None

    def test_recording_child_span_does_not_overwrite_trace_level_io(self) -> None:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")

        with tracer.start_as_current_span("cresmo.fluid_prose") as raw_span:
            wrapped = OTelTelemetrySpan(raw_span, is_root=False)
            wrapped.set_input("raw string input")
            wrapped.set_output("raw string output")
            wrapped.add_event("stage_marker")

        finished = exporter.get_finished_spans()[0]
        attrs = finished.attributes or {}
        assert attrs["input.value"] == "raw string input"
        assert attrs["langfuse.observation.input"] == "raw string input"
        assert "langfuse.trace.input" not in attrs
        assert attrs["output.value"] == "raw string output"
        assert attrs["langfuse.observation.output"] == "raw string output"
        assert "langfuse.trace.output" not in attrs
        assert not any(k.startswith("cresmo.output.") for k in attrs)

    def test_non_recording_span_is_safe_noop(self) -> None:
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        wrapped = OTelTelemetrySpan(mock_span, is_root=True)
        assert wrapped.trace_id is None
        assert wrapped.span_id is None
        wrapped.set_attributes({"a": 1})
        wrapped.set_input({"b": 2})
        wrapped.set_output({"c": 3})
        wrapped.add_event("evt", {"d": 4})
        wrapped.record_error(RuntimeError("ignored"))
        mock_span.set_attribute.assert_not_called()
        mock_span.add_event.assert_not_called()
        mock_span.record_exception.assert_not_called()

    def test_wrap_current_otel_span_returns_noop_when_outside_span(self) -> None:
        assert wrap_current_otel_span() is NOOP_TELEMETRY_SPAN

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("cresmo.test")
        with tracer.start_as_current_span("active_child"):
            handle = wrap_current_otel_span()
            assert isinstance(handle, OTelTelemetrySpan)
            assert handle.trace_id is not None
            handle.set_input("child payload")

        with tracer.start_as_current_span("active_root"):
            root_handle = wrap_current_otel_span(is_root=True)
            assert isinstance(root_handle, OTelTelemetrySpan)
            root_handle.set_input("root payload")

        spans_by_name = {s.name: s for s in exporter.get_finished_spans()}
        child_attrs = spans_by_name["active_child"].attributes or {}
        root_attrs = spans_by_name["active_root"].attributes or {}
        assert child_attrs["input.value"] == "child payload"
        assert "langfuse.trace.input" not in child_attrs
        assert root_attrs["langfuse.trace.input"] == "root payload"


class TestBuildGenAiAttributes:
    """Verify CNCF OTel GenAI Semantic Conventions builder (SPEC-070 §2.3)."""

    def test_minimal_and_full_genai_attributes_with_active_pass(self) -> None:
        minimal = build_genai_attributes(
            system="ollama",
            model="qwen2.5:7b",
            prompt_tokens=10,
            candidate_tokens=20,
        )
        assert minimal == {
            "gen_ai.system": "ollama",
            "gen_ai.request.model": "qwen2.5:7b",
            "gen_ai.usage.input_tokens": 10,
            "gen_ai.usage.output_tokens": 20,
        }

        with active_telemetry_pass(2):
            full = build_genai_attributes(
                system="google",
                model="gemini-3.5-flash-lite",
                prompt_tokens=100,
                candidate_tokens=250,
                session_id="UC_1:vid_1",
                user_id="system:worker",
                trace_id="trace_abc",
                temperature=0.3,
                max_tokens=8192,
                thinking_level="low",
                thinking_tokens=64,
            )

        assert full == {
            "gen_ai.system": "google",
            "gen_ai.request.model": "gemini-3.5-flash-lite",
            "gen_ai.usage.input_tokens": 100,
            "gen_ai.usage.output_tokens": 250,
            "langfuse.session.id": "UC_1:vid_1",
            "langfuse.user.id": "system:worker",
            "cresmo.trace_id": "trace_abc",
            "gen_ai.request.temperature": 0.3,
            "gen_ai.request.max_tokens": 8192,
            "cresmo.thinking_level": "low",
            "gen_ai.usage.reasoning_tokens": 64,
            "cresmo.pass_num": 2,
        }

    def test_explicit_pass_num_overrides_active_telemetry_pass(self) -> None:
        with active_telemetry_pass(2):
            attrs = build_genai_attributes(
                system="google",
                model="gemini-3.5-flash-lite",
                prompt_tokens=12,
                candidate_tokens=34,
                pass_num=4,
            )

        assert attrs["cresmo.pass_num"] == 4
