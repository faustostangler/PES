"""Hermetic unit tests for pure SDT confusion matrices and calibration result models.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import math

import pytest

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    CalibrationVerdict,
    ConfusionMatrix,
    ItemEvaluationResult,
    ModelBenchmarkSummary,
)
from cresmo.domain.exceptions import DomainValidationError


class TestConfusionMatrixAndModels:
    """Tests covering ConfusionMatrix SDT math, recording, and result data models."""

    def test_record_tracks_all_verdict_buckets(self) -> None:
        cm = ConfusionMatrix()
        assert cm.record("PASS", "PASS") == "HIT"
        assert cm.record("PASS", "PASS") == "HIT"
        assert cm.record("FAIL", "FAIL") == "CORRECT_REJECTION"
        assert cm.record("FAIL", "FAIL") == "CORRECT_REJECTION"
        assert cm.record("FAIL", "PASS") == "FALSE_ACCEPT_ALPHA"
        assert cm.record("FAIL", "PASS") == "FALSE_ACCEPT_ALPHA"
        assert cm.record("PASS", "FAIL") == "FALSE_REJECT_BETA"
        assert cm.record("PASS", "FAIL") == "FALSE_REJECT_BETA"
        assert cm.record("PASS", "PASS") == "HIT"
        assert cm.record("FAIL", "ERROR") == "FALSE_REJECT_BETA"

        with pytest.raises(DomainValidationError, match="UNKNOWN"):
            cm.record("UNKNOWN", "PASS")
        with pytest.raises(DomainValidationError, match="BAD_EXPECTED"):
            cm.record("BAD_EXPECTED", "FAIL")

        assert cm.hit == 3
        assert cm.correct_rejection == 2
        assert cm.false_accept_alpha == 2
        assert cm.false_reject_beta == 3
        assert cm.total_valid == 6
        assert cm.total_defective == 4
        assert cm.total_approved == 5
        assert cm.total_rejected == 5
        assert cm.total_samples == 10

    def test_asymmetric_f_beta_lr_mcc_and_boundary_properties(self) -> None:
        cm = ConfusionMatrix(hit=4, false_reject_beta=1, false_accept_alpha=2, correct_rejection=3)
        assert math.isclose(cm.accuracy, 0.7)
        assert math.isclose(cm.precision, 4 / 6)
        assert math.isclose(cm.recall, 4 / 5)
        assert math.isclose(cm.specificity, 3 / 5)
        assert math.isclose(cm.npv, 3 / 4)
        assert math.isclose(cm.alpha_fpr, 2 / 5)
        assert math.isclose(cm.beta_fnr, 1 / 5)
        assert math.isclose(cm.f05, 1.25 * (4 / 6) * (4 / 5) / (0.25 * (4 / 6) + (4 / 5)))
        assert math.isclose(cm.f1, 2 * (4 / 6) * (4 / 5) / ((4 / 6) + (4 / 5)))
        assert math.isclose(cm.f2, 5 * (4 / 6) * (4 / 5) / (4 * (4 / 6) + (4 / 5)))
        assert math.isclose(cm.lr_plus, 2.0)
        assert math.isclose(cm.lr_minus, 1 / 3)
        expected_mcc = (4 * 3 - 2 * 1) / math.sqrt(6 * 5 * 5 * 4)
        assert math.isclose(cm.mcc, expected_mcc)
        assert cm.d_prime > 0.0

        perfect = ConfusionMatrix(
            hit=5, false_reject_beta=0, false_accept_alpha=0, correct_rejection=5
        )
        assert math.isinf(perfect.lr_plus)
        assert perfect.lr_minus == 0.0
        assert math.isclose(perfect.mcc, 1.0)
        assert perfect.d_prime > 2.0
        assert math.isclose(perfect.c_bias, 0.0, abs_tol=1e-9)

        zero_all = ConfusionMatrix()
        assert zero_all.accuracy == 0.0
        assert zero_all.precision == 0.0
        assert zero_all.recall == 0.0
        assert zero_all.specificity == 0.0
        assert zero_all.npv == 0.0
        assert zero_all.alpha_fpr == 0.0
        assert zero_all.beta_fnr == 0.0
        assert zero_all.f05 == 0.0
        assert zero_all.f1 == 0.0
        assert zero_all.f2 == 0.0
        assert zero_all.lr_plus == 1.0
        assert zero_all.lr_minus == 1.0
        assert zero_all.mcc == 0.0
        assert zero_all.d_prime == 0.0
        assert zero_all.c_bias == 0.0

        all_fail_tnr_zero = ConfusionMatrix(
            hit=0, false_reject_beta=2, false_accept_alpha=2, correct_rejection=0
        )
        assert math.isinf(all_fail_tnr_zero.lr_minus)

    def test_result_set_and_summary_models_expose_expected_fields(self) -> None:
        rs = CalibrationResultSet()
        assert rs.overall.hit == 0
        assert rs.overall.false_accept_alpha == 0
        assert rs.overall.false_reject_beta == 0
        assert rs.overall.correct_rejection == 0
        assert not hasattr(rs.overall, "invalid")
        assert rs.overall.total_samples == 0
        assert rs.overall.total_valid == 0
        assert rs.overall.accuracy == 0.0
        assert rs.overall.precision == 0.0
        assert rs.overall.recall == 0.0
        assert rs.overall.f1 == 0.0

        rs.overall.record("PASS", "PASS")
        rs.overall.record("FAIL", "FAIL")
        rs.overall.record("FAIL", "PASS")
        rs.overall.record("PASS", "FAIL")
        with pytest.raises(DomainValidationError, match="Invalid expected calibration verdict"):
            rs.overall.record("BAD", "PASS")

        assert rs.overall.hit == 1
        assert rs.overall.correct_rejection == 1
        assert rs.overall.false_accept_alpha == 1
        assert rs.overall.false_reject_beta == 1
        assert rs.overall.total_samples == 4
        assert rs.overall.total_valid == 2
        assert math.isclose(rs.overall.accuracy, 0.5)
        assert math.isclose(rs.overall.precision, 0.5)
        assert math.isclose(rs.overall.recall, 0.5)
        assert math.isclose(rs.overall.f1, 0.5)

        item_res = ItemEvaluationResult(
            actual="PASS",
            expected="PASS",
            score=0.92,
            reasoning="Clean",
            target_actual="PASS",
            target_score=0.95,
        )
        assert (item_res.actual, item_res.expected, item_res.score, item_res.reasoning) == (
            "PASS",
            "PASS",
            0.92,
            "Clean",
        )

        summary = ModelBenchmarkSummary(
            stage="fluid_prose",
            provider="gemini",
            model="gemini-3.8-flash",
            status=CalibrationVerdict.APPROVED,
            accuracy=0.95,
        )
        outcome = CalibrationSuiteOutcome(summaries=(summary,), has_errors=False)
        assert outcome.summaries == (summary,)
        assert outcome.has_errors is False
        assert summary.status.value == "APPROVED"

    @pytest.mark.parametrize(
        ("verdict", "expected"),
        [
            (CalibrationVerdict.APPROVED, "APPROVED"),
            (CalibrationVerdict.PRE_CALIBRATED, "PRE-CALIBRATED"),
            (CalibrationVerdict.REJECTED, "REJECTED"),
            (CalibrationVerdict.COOLDOWN, "COOLDOWN"),
            (CalibrationVerdict.ERROR, "ERROR"),
        ],
    )
    def test_calibration_verdict_enum_values(
        self, verdict: CalibrationVerdict, expected: str
    ) -> None:
        assert verdict.value == expected
