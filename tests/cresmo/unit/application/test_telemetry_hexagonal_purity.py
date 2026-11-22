"""AST architectural purity and port contract tests for ADR-070 / SPEC-070."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from cresmo.application.ports.telemetry import (
    LLM_GENERATION_FALLBACK_SPAN_NAME,
    LLM_GENERATION_SPAN_NAME,
    NOOP_TELEMETRY_SPAN,
    NoOpTelemetryPort,
    NoOpTelemetrySpan,
    SessionTelemetrySpec,
    SpanKind,
    TelemetryPort,
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

SRC_ROOT = Path(__file__).resolve().parents[4] / "src" / "cresmo"


def _collect_imported_roots(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


class TestTelemetryHexagonalPurity:
    """Verify strict Hexagonal separation of telemetry SDKs per ADR-070."""

    @pytest.mark.parametrize("layer_dir", ["domain", "application"])
    def test_domain_and_application_never_import_opentelemetry_or_langfuse(
        self, layer_dir: str
    ) -> None:
        violations: list[str] = []
        for py_file in sorted((SRC_ROOT / layer_dir).rglob("*.py")):
            imported = _collect_imported_roots(py_file)
            forbidden = imported & {"opentelemetry", "langfuse"}
            if forbidden:
                violations.append(f"{py_file.relative_to(SRC_ROOT)}: {sorted(forbidden)}")
        assert violations == []

    @pytest.mark.parametrize("adapter_dir", ["adapters/llm", "adapters/judges"])
    def test_llm_and_judge_adapters_never_import_opentelemetry_or_langfuse(
        self, adapter_dir: str
    ) -> None:
        violations: list[str] = []
        for py_file in sorted((SRC_ROOT / "infrastructure" / adapter_dir).rglob("*.py")):
            imported = _collect_imported_roots(py_file)
            forbidden = imported & {"opentelemetry", "langfuse"}
            if forbidden:
                violations.append(f"{py_file.relative_to(SRC_ROOT)}: {sorted(forbidden)}")
        assert violations == []

    def test_legacy_duplicate_files_are_deleted(self) -> None:
        assert not (SRC_ROOT / "infrastructure" / "adapters" / "telemetry" / "noop.py").exists()
        assert not (
            SRC_ROOT / "infrastructure" / "adapters" / "judges" / "langfuse_decorator.py"
        ).exists()


class TestSessionTelemetrySpecAndPortContracts:
    """Verify SPEC-070 §1 invariants, TelemetryPort surface, and single NoOpTelemetryPort."""

    def test_session_telemetry_spec_validates_invariants(self) -> None:
        valid = SessionTelemetrySpec(
            session_id=PipelineSessionId("ch:vid_1"),
            user_id=UserIdentity.worker(),
            raw_characters=0,
            raw_words=0,
            gap_filler_passes=1,
        )
        assert valid.source == "transcript"
        assert valid.force_reprocess is False
        with pytest.raises(TypeError):
            valid.extra_metadata["mutated"] = "nope"  # type: ignore[index]

        with pytest.raises(ValueError, match=r"^raw_characters must be >= 0$"):
            SessionTelemetrySpec(
                session_id=PipelineSessionId("ch:vid_1"),
                user_id=UserIdentity.worker(),
                raw_characters=-1,
            )

        with pytest.raises(ValueError, match=r"^raw_words must be >= 0$"):
            SessionTelemetrySpec(
                session_id=PipelineSessionId("ch:vid_1"),
                user_id=UserIdentity.worker(),
                raw_words=-1,
            )

        with pytest.raises(ValueError, match=r"^gap_filler_passes must be >= 1$"):
            SessionTelemetrySpec(
                session_id=PipelineSessionId("ch:vid_1"),
                user_id=UserIdentity.worker(),
                gap_filler_passes=0,
            )

        with pytest.raises(ValueError, match=r"^gap_filler_passes must be >= 1$"):
            SessionTelemetrySpec(
                session_id=PipelineSessionId("ch:vid_1"),
                user_id=UserIdentity.worker(),
                gap_filler_passes=True,
            )

    def test_telemetry_port_exposes_exact_minimal_method_set(self) -> None:
        abstract_methods = TelemetryPort.__abstractmethods__
        assert abstract_methods == frozenset(
            {"start_session", "start_span", "current_span", "record_score"}
        )
        assert hasattr(TelemetryPort, "flush")
        for removed in (
            "start_pipeline_session",
            "start_stage_span",
            "start_stage_evaluation_span",
            "start_stage_saturation_span",
            "record_judge_evaluation",
            "record_session_coherence",
            "record_session_output",
            "record_stage_io",
        ):
            assert not hasattr(TelemetryPort, removed)

    def test_noop_telemetry_port_and_span_behavior(self) -> None:
        port = NoOpTelemetryPort()
        spec = SessionTelemetrySpec(
            session_id=PipelineSessionId("ch:vid_noop"),
            user_id=UserIdentity.anonymous(),
        )
        assert port.current_span() is NOOP_TELEMETRY_SPAN
        assert isinstance(NOOP_TELEMETRY_SPAN, NoOpTelemetrySpan)
        assert NOOP_TELEMETRY_SPAN.trace_id is None
        assert NOOP_TELEMETRY_SPAN.span_id is None

        with port.start_session(spec) as root_span:
            assert root_span is NOOP_TELEMETRY_SPAN
            root_span.set_attributes({"k": "v"})
            root_span.set_input({"in": 1})
            root_span.set_output({"out": 2})
            root_span.add_event("evt", {"a": 1})
            root_span.record_error(RuntimeError("noop"))

        assert get_active_telemetry_stage() is None
        with port.start_span("cresmo.fluid_prose", stage_name="fluid_prose") as stage_span:
            assert stage_span is NOOP_TELEMETRY_SPAN
            assert get_active_telemetry_stage() == "fluid_prose"
        assert get_active_telemetry_stage() is None

        with port.start_span("cresmo.llm.generate", kind=SpanKind.GENERATION) as gen_span:
            assert gen_span is NOOP_TELEMETRY_SPAN
            assert get_active_telemetry_stage() is None

        port.record_score(name="s", value=0.9, comment="ok", trace_id="t", observation_id="o")
        port.flush()

    def test_telemetry_span_naming_validation_and_contextvars_resolution(self) -> None:
        assert format_stage_span_name(" fluid_prose ") == "cresmo.fluid_prose"
        assert format_stage_judge_span_name("gap_filler") == "cresmo.gap_filler.judge"
        assert format_stage_saturation_span_name("gap_filler") == "cresmo.gap_filler.saturation"
        assert (
            format_stage_saturation_span_name("gap_filler", pass_num=2)
            == "cresmo.gap_filler.saturation.pass_2"
        )

        with pytest.raises(ValueError, match=r"^stage_name must be a non-empty string$"):
            format_stage_span_name("   ")

        for invalid_pass in (0, -1, True, False):
            with pytest.raises(ValueError, match=r"^pass_num must be a positive integer$"):
                format_stage_saturation_span_name("gap_filler", pass_num=invalid_pass)

        assert format_stage_generation_span_name("fluid_prose") == "cresmo.fluid_prose.generate"
        assert (
            format_stage_generation_span_name("fluid_prose", fallback=True)
            == "cresmo.fluid_prose.generate_fallback"
        )
        assert (
            format_stage_generation_span_name("fluid_prose", fallback=True, pass_num=2)
            == "cresmo.fluid_prose.generate_fallback.pass_2"
        )
        assert format_stage_generation_span_name(None) == LLM_GENERATION_SPAN_NAME
        assert (
            format_stage_generation_span_name(None, fallback=True)
            == LLM_GENERATION_FALLBACK_SPAN_NAME
        )
        assert (
            format_stage_generation_span_name("   ", fallback=True, pass_num=2)
            == "cresmo.llm.generate_fallback.pass_2"
        )

        assert get_active_telemetry_stage() is None
        assert get_active_telemetry_pass() is None
        assert resolve_llm_generation_span_name() == LLM_GENERATION_SPAN_NAME
        assert resolve_llm_generation_span_name(fallback=True) == LLM_GENERATION_FALLBACK_SPAN_NAME

        with active_telemetry_stage("gap_filler"), active_telemetry_pass(2):
            assert resolve_llm_generation_span_name() == "cresmo.gap_filler.generate.pass_2"
            assert (
                resolve_llm_generation_span_name(fallback=True)
                == "cresmo.gap_filler.generate_fallback.pass_2"
            )
            assert (
                resolve_llm_generation_span_name(stage_name="fluid_prose")
                == "cresmo.fluid_prose.generate.pass_2"
            )
            assert (
                resolve_llm_generation_span_name(pass_num=5) == "cresmo.gap_filler.generate.pass_5"
            )
            assert (
                resolve_llm_generation_span_name(
                    stage_name="fluid_prose", pass_num=3, fallback=True
                )
                == "cresmo.fluid_prose.generate_fallback.pass_3"
            )
