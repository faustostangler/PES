"""Hermetic unit tests for Presentation calibration ASCII & SDT diagnostic formatters.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import io
import math
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationVerdict,
    ConfusionMatrix,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.executor import CalibrationEvent, CalibrationEventKind
from cresmo.application.evals.specs import build_stage_specs
from cresmo.presentation.formatters.calibration_report import (
    build_sdt_metric_diagnostics,
    format_benchmark_summary,
    format_calibration_report,
    format_confusion_matrix_2x2,
    render_calibration_event,
)


class TestCalibrationReportFormatter:
    """Unit tests covering SDT metric diagnostics, ASCII reports, and benchmark tables."""

    def test_build_sdt_metric_diagnostics_covers_15_metrics_and_bands(self) -> None:
        cm_strong = ConfusionMatrix(
            hit=10, false_reject_beta=0, false_accept_alpha=0, correct_rejection=10
        )
        diagnostics = {m.code: m for m in build_sdt_metric_diagnostics(cm_strong)}
        assert len(diagnostics) == 15
        assert diagnostics["a)"].diagnosis == "Acceptable (>=80%)"
        assert diagnostics["k)"].formatted_value == "Inf"
        assert diagnostics["n)"].diagnosis == "Excellent (>=2.0)"

        cm_weak = ConfusionMatrix(
            hit=2, false_reject_beta=8, false_accept_alpha=8, correct_rejection=2
        )
        weak_diag = {m.code: m for m in build_sdt_metric_diagnostics(cm_weak)}
        assert weak_diag["a)"].diagnosis == "Below baseline (<80%)"
        assert weak_diag["f)"].diagnosis == "High leak (>20%)"
        assert weak_diag["g)"].diagnosis == "High churn (>15%)"

    def test_format_matrix_report_and_benchmark_summary(self, tmp_path: Path) -> None:
        cm = ConfusionMatrix(hit=3, false_reject_beta=1, false_accept_alpha=0, correct_rejection=2)
        matrix_str = format_confusion_matrix_2x2("2x2 CONFUSION MATRIX", cm)
        assert "HIT (TP): 3" in matrix_str
        assert "FALSE REJECT (FN): 1" in matrix_str
        assert "FALSE ACCEPT (FP): 0" in matrix_str
        assert "CORRECT REJECT (TN): 2" in matrix_str

        results = CalibrationResultSet(
            overall=cm,
            target_isolated=cm,
            by_criterion={"orality_removal": cm},
            by_difficulty={"easy": cm},
            disagreements=[
                {
                    "id": "it_2",
                    "criterion": "orality_removal",
                    "difficulty": "easy",
                    "expected": "PASS",
                    "actual_target": "FAIL",
                    "score": 0.4,
                    "reasoning": "Too strict",
                }
            ],
            evaluated_items=4,
            skipped_from_checkpoint=2,
        )
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        report = format_calibration_report(
            spec,
            results,
            provider="gemini",
            model="m1",
            timestamp=datetime(2026, 11, 22, 12, 0, tzinfo=UTC),
        )
        assert "2026-11-22 12:00:00 UTC" in report
        assert "SLICE BREAKDOWN BY CRITERION" in report
        assert "DISAGREEMENTS" in report

        table = format_benchmark_summary(
            [
                ModelBenchmarkSummary(
                    stage="fluid_prose",
                    provider="gemini",
                    model="m1",
                    status=CalibrationVerdict.APPROVED,
                    accuracy=0.90,
                    d_prime=2.5,
                    f1=0.90,
                    precision=1.0,
                    recall=0.80,
                    alpha_fpr=0.0,
                    evaluated_total=10,
                    dataset_total=10,
                ),
                ModelBenchmarkSummary(
                    stage="fluid_prose",
                    provider="gemini",
                    model="m2",
                    status=CalibrationVerdict.COOLDOWN,
                    evaluated_total=3,
                    dataset_total=10,
                    cooldown_remaining_s=45.0,
                ),
                ModelBenchmarkSummary(
                    stage="gap_filler",
                    provider="ollama",
                    model="m3",
                    status=CalibrationVerdict.ERROR,
                    evaluated_total=0,
                    dataset_total=5,
                    error_message="Socket closed",
                ),
            ]
        )
        assert "APPROVED" in table
        assert "retry in 45s" in table
        assert "Socket closed" in table

    def test_render_calibration_event_writes_to_stream(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        buf = io.StringIO()
        render_calibration_event(
            CalibrationEvent(kind=CalibrationEventKind.SUITE_STARTED, message="Hello suite"),
            out_stream=buf,
        )
        assert buf.getvalue() == "Hello suite\n"

        render_calibration_event(
            CalibrationEvent(kind=CalibrationEventKind.STAGE_STARTED, message="Default stdout"),
        )
        assert capsys.readouterr().out == "Default stdout\n"

    def test_build_sdt_metric_diagnostics_moderate_weak_and_exact_boundaries(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def _diag(cm: ConfusionMatrix) -> dict[str, str]:
            return {m.code: m.diagnosis for m in build_sdt_metric_diagnostics(cm)}

        moderate_pedantic = ConfusionMatrix(
            hit=7, false_reject_beta=3, false_accept_alpha=2, correct_rejection=8
        )
        m_ped = _diag(moderate_pedantic)
        assert m_ped["a)"] == "Below baseline (<80%)"
        assert m_ped["b)"] == "Leaky (<80%)"
        assert m_ped["c)"] == "Pedantic (<85%)"
        assert m_ped["d)"] == "Effective (>=70%)"
        assert m_ped["e)"] == "Noisy (<75%)"
        assert m_ped["f)"] == "Low leak (<=20%)"
        assert m_ped["g)"] == "High churn (>15%)"
        assert m_ped["k)"] == "Moderate (2-10)"
        assert m_ped["l)"] == "Moderate (0.1-0.5)"
        assert m_ped["m)"] == "Moderate (>0.20)"
        assert m_ped["n)"] == "Moderate (>=1.0)"
        assert m_ped["o)"] == f"Pedantic/conservative (+{moderate_pedantic.c_bias:.2f})"

        weak_perm = ConfusionMatrix(
            hit=8, false_reject_beta=2, false_accept_alpha=10, correct_rejection=0
        )
        m_weak = _diag(weak_perm)
        assert m_weak["d)"] == "Weak (<70%)"
        assert m_weak["f)"] == "High leak (>20%)"
        assert m_weak["h)"] == "Weak (<80%)"
        assert m_weak["i)"] == "Unbalanced (<80%)"
        assert m_weak["j)"] == "Restrictive (<85%)"
        assert m_weak["k)"] == "Weak (<2)"
        assert m_weak["l)"] == "Inconclusive (>0.5)"
        assert m_weak["m)"] == "Poor (<=0.20)"
        assert m_weak["n)"] == "Poor (<1.0)"
        assert m_weak["o)"] == f"Permissive/liberal ({weak_perm.c_bias:.2f})"

        cm_eq_80 = ConfusionMatrix(
            hit=4, false_reject_beta=1, false_accept_alpha=1, correct_rejection=4
        )
        d80 = _diag(cm_eq_80)
        assert d80["a)"] == "Acceptable (>=80%)"
        assert d80["b)"] == "Pure (>=80%)"
        assert d80["f)"] == "Low leak (<=20%)"
        assert d80["h)"] == "Strong (>=80%)"
        assert d80["i)"] == "Balanced (>=80%)"
        assert d80["m)"] == "Strong (>=0.60)"

        cm_eq_85 = ConfusionMatrix(
            hit=17, false_reject_beta=3, false_accept_alpha=3, correct_rejection=17
        )
        d85 = _diag(cm_eq_85)
        assert d85["c)"] == "Healthy (>=85%)"
        assert d85["g)"] == "Low churn (<=15%)"
        assert d85["j)"] == "Preserving (>=85%)"

        cm_spec_npv = ConfusionMatrix(
            hit=3, false_reject_beta=3, false_accept_alpha=4, correct_rejection=9
        )
        cm_spec_exact = ConfusionMatrix(
            hit=3, false_reject_beta=1, false_accept_alpha=3, correct_rejection=7
        )
        assert math.isclose(cm_spec_npv.npv, 0.75)
        assert _diag(cm_spec_npv)["e)"] == "Reliable (>=75%)"
        assert math.isclose(cm_spec_exact.specificity, 0.70)
        assert _diag(cm_spec_exact)["d)"] == "Effective (>=70%)"

        cm_lr10 = ConfusionMatrix(
            hit=5, false_reject_beta=5, false_accept_alpha=1, correct_rejection=19
        )
        cm_lr2 = ConfusionMatrix(
            hit=5, false_reject_beta=5, false_accept_alpha=5, correct_rejection=15
        )
        cm_lrm01 = ConfusionMatrix(
            hit=19, false_reject_beta=1, false_accept_alpha=5, correct_rejection=5
        )
        cm_lrm05 = ConfusionMatrix(
            hit=3, false_reject_beta=1, false_accept_alpha=5, correct_rejection=5
        )
        cm_mcc02 = ConfusionMatrix(
            hit=3, false_reject_beta=2, false_accept_alpha=2, correct_rejection=3
        )
        assert _diag(cm_lr10)["k)"] == "Strong (>=10)"
        assert _diag(cm_lr2)["k)"] == "Moderate (2-10)"
        assert _diag(cm_lrm01)["l)"] == "Definitive (<=0.1)"
        assert _diag(cm_lrm05)["l)"] == "Moderate (0.1-0.5)"
        assert _diag(cm_mcc02)["m)"] == "Poor (<=0.20)"

        base_cm = ConfusionMatrix(
            hit=5, false_reject_beta=1, false_accept_alpha=1, correct_rejection=5
        )
        monkeypatch.setattr(ConfusionMatrix, "d_prime", property(lambda _self: 2.0))
        assert _diag(base_cm)["n)"] == "Excellent (>=2.0)"
        monkeypatch.setattr(ConfusionMatrix, "d_prime", property(lambda _self: 1.0))
        assert _diag(base_cm)["n)"] == "Moderate (>=1.0)"
        monkeypatch.setattr(ConfusionMatrix, "c_bias", property(lambda _self: 0.15))
        assert _diag(base_cm)["o)"] == "Balanced/neutral (0.15)"
        monkeypatch.setattr(ConfusionMatrix, "c_bias", property(lambda _self: -0.15))
        assert _diag(base_cm)["o)"] == "Balanced/neutral (-0.15)"
