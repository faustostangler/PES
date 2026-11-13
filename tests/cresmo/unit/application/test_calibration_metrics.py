"""Comprehensive unit tests for SDT calibration metrics and result models."""

from __future__ import annotations

import math

import pytest

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    ConfusionMatrix,
    ItemEvaluationResult,
    MetricInfo,
    ModelBenchmarkSummary,
)

# Expected static descriptor fields: (code, name, math_formula, sheets_formula, practical, high, low)
EXPECTED_METRIC_METADATA: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a)",
        "Accuracy",
        "(Hit + Rejeicao) / Total",
        "=(B4+C5)/D6",
        "Overall proportion of correct verdicts.",
        "Most decisions align with ground truth.",
        "Judge frequently misclassifies items.",
    ),
    (
        "b)",
        "Precision / PPV",
        "Hit / (Hit + Permissivo-alfa)",
        "=B4/B6",
        "Purity of PASS verdicts.",
        "Approvals rarely pass defective candidates.",
        "Defective candidates leak through PASS gate.",
    ),
    (
        "c)",
        "Recall / Sensitivity",
        "Hit / (Hit + Pedantismo-beta)",
        "=B4/D4",
        "Share of valid candidates approved.",
        "Minimal false rejections of valid work.",
        "Judge is overly pedantic and discards valid work.",
    ),
    (
        "d)",
        "Specificity (TNR)",
        "Rejeicao / (Rejeicao + Permissivo-alfa)",
        "=C5/D5",
        "Share of defective candidates caught.",
        "Strong gate against defects.",
        "Defects bypass rejection.",
    ),
    (
        "e)",
        "NPV",
        "Rejeicao / (Rejeicao + Pedantismo-beta)",
        "=C5/C6",
        "Reliability of FAIL verdicts.",
        "Rejections correspond to real defects.",
        "Many valid candidates are rejected.",
    ),
    (
        "f)",
        "Alpha Rate (FPR)",
        "Permissivo-alfa / (Rejeicao + Permissivo-alfa)",
        "=B5/D5",
        "Rate of defective texts leaking through.",
        "Unacceptable defect leakage.",
        "Hermetic quality filter.",
    ),
    (
        "g)",
        "Beta Rate (FNR)",
        "Pedantismo-beta / (Hit + Pedantismo-beta)",
        "=C4/D4",
        "Rate of valid texts wasted in retries.",
        "Excessive self-healing churn.",
        "Low pedantry.",
    ),
    (
        "h)",
        "F0.5-Score",
        "1.25 * (P * R) / (0.25 * P + R)",
        "=(1+H17^2)*(D$11*D$12)/((H17^2*D$11)+D$12)",
        "Precision-weighted harmonic mean (2x Precision).",
        "Strong fidelity and low permissiveness.",
        "Leaked defects degraded gate purity.",
    ),
    (
        "i)",
        "F1-Score",
        "2 * (P * R) / (P + R)",
        "=(1+H18^2)*(D$11*D$12)/((H18^2*D$11)+D$12)",
        "Balanced harmonic mean of Precision and Recall.",
        "Well-balanced discrimination.",
        "Precision/Recall imbalance or weak discrimination.",
    ),
    (
        "j)",
        "F2-Score",
        "5 * (P * R) / (4 * P + R)",
        "=(1+H19^2)*(D$11*D$12)/((H19^2*D$11)+D$12)",
        "Recall-weighted harmonic mean (2x Recall).",
        "Preserves nearly all valid texts.",
        "Pedantry discards too much valid output.",
    ),
    (
        "k)",
        "LR+",
        "Sensitivity / (1 - Specificity)",
        "=(B4/D4)/(B5/D5)",
        "Evidentiary weight of a PASS decision.",
        "Strong confirmation of quality (>10).",
        "Weak confirmation (<2).",
    ),
    (
        "l)",
        "LR-",
        "(1 - Sensitivity) / Specificity",
        "=(C4/D4)/(C5/D5)",
        "Evidentiary weight of a FAIL decision.",
        "Inconclusive rejection (>0.5).",
        "Definitive defect confirmation (<0.1).",
    ),
    (
        "m)",
        "Matthews Correlation (MCC)",
        "((Hit * Rej) - (Alfa * Beta)) / SQRT(...)",
        "=((B4*C5)-(B5*C4))/SQRT(B6*D4*D5*C6)",
        "Full confusion matrix correlation in [-1, +1].",
        "Strong alignment with ground truth.",
        "Random or inverted alignment (<=0).",
    ),
    (
        "n)",
        "D-prime (d')",
        "NORM.S.INV(HitRate) - NORM.S.INV(FARate)",
        "=NORM.S.INV(B4/D4)-NORM.S.INV(B5/D5)",
        "Intrinsic signal-vs-noise discrimination acuity.",
        "Excellent discrimination (>=2.0).",
        "Inability to separate valid vs defective (~0).",
    ),
    (
        "o)",
        "Criterion c (Bias)",
        "-0.5 * (NORM.S.INV(HitRate) + NORM.S.INV(FARate))",
        "=-0.5*(NORM.S.INV(B4/D4)+NORM.S.INV(B5/D5))",
        "Systematic decision threshold bias.",
        "Pedantic/conservative (+).",
        "Permissive/liberal (-).",
    ),
]


def _diag_by_code(cm: ConfusionMatrix) -> dict[str, MetricInfo]:
    return {item.code: item for item in cm.get_all_metrics()}


class TestConfusionMatrixAndModels:
    """Tests covering ConfusionMatrix SDT math, recording, and MetricInfo generation."""

    def test_record_tracks_all_verdict_buckets(self) -> None:
        cm = ConfusionMatrix()
        assert cm.record("PASS", "PASS") == "HIT"
        assert cm.record("PASS", "PASS") == "HIT"
        assert cm.record("FAIL", "FAIL") == "REJEICAO"
        assert cm.record("FAIL", "FAIL") == "REJEICAO"
        assert cm.record("FAIL", "PASS") == "PERMISSIVO_ALFA"
        assert cm.record("FAIL", "PASS") == "PERMISSIVO_ALFA"
        assert cm.record("PASS", "FAIL") == "PEDANTISMO_BETA"
        assert cm.record("PASS", "FAIL") == "PEDANTISMO_BETA"
        assert cm.record("UNKNOWN", "PASS") == "INVALID"
        assert cm.record("UNKNOWN", "FAIL") == "INVALID"
        assert cm.record("FAIL", "ERROR") == "PEDANTISMO_BETA"

        assert cm.tp == 2
        assert cm.tn == 2
        assert cm.fp == 2
        assert cm.fn == 3
        assert cm.invalid == 2
        assert cm.total_corretos == 5
        assert cm.total_defeituosos == 4
        assert cm.total_aprovados == 4
        assert cm.total_reprovados == 5
        assert cm.total_valid == 9

    def test_asymmetric_f_beta_lr_mcc_and_boundary_properties(self) -> None:
        cm = ConfusionMatrix(hit=4, pedantismo_beta=1, permissivo_alfa=2, rejeicao=3)
        p = 4 / 6
        r = 4 / 5
        assert cm.precision == pytest.approx(p)
        assert cm.recall == pytest.approx(r)
        assert cm.specificity == pytest.approx(3 / 5)
        assert cm.npv == pytest.approx(3 / 4)
        assert cm.alpha_fpr == pytest.approx(2 / 5)
        assert cm.beta_fnr == pytest.approx(1 / 5)
        assert cm.f05 == pytest.approx(1.25 * p * r / (0.25 * p + r))
        assert cm.f1 == pytest.approx(2.0 * p * r / (p + r))
        assert cm.f2 == pytest.approx(5.0 * p * r / (4.0 * p + r))
        assert cm.lr_plus == pytest.approx(r / (2 / 5))
        assert cm.lr_minus == pytest.approx((1 / 5) / (3 / 5))

        perfect = ConfusionMatrix(hit=5, pedantismo_beta=0, permissivo_alfa=0, rejeicao=5)
        assert perfect.lr_plus == float("inf")
        assert perfect.lr_minus == 0.0
        assert perfect.mcc == pytest.approx(1.0)
        assert perfect.d_prime > 2.0

        zero_all = ConfusionMatrix()
        assert zero_all.lr_plus == 1.0
        assert zero_all.lr_minus == 1.0
        assert zero_all.mcc == 0.0
        assert zero_all.d_prime == 0.0
        assert zero_all.c_bias == 0.0

        all_fail_tnr_zero = ConfusionMatrix(hit=0, pedantismo_beta=2, permissivo_alfa=2, rejeicao=0)
        assert all_fail_tnr_zero.lr_minus == float("inf")
        assert all_fail_tnr_zero.lr_plus == 0.0

    def test_get_all_metrics_static_catalog_and_strong_band(self) -> None:
        cm = ConfusionMatrix(hit=10, pedantismo_beta=0, permissivo_alfa=0, rejeicao=10)
        metrics = cm.get_all_metrics()
        assert len(metrics) == 15

        for actual_info, expected_tuple in zip(metrics, EXPECTED_METRIC_METADATA, strict=True):
            assert (
                actual_info.code,
                actual_info.name,
                actual_info.math_formula,
                actual_info.sheets_formula,
                actual_info.practical_implication,
                actual_info.high_meaning,
                actual_info.low_meaning,
            ) == expected_tuple

        by_code = {m.code: m for m in metrics}
        expected_values: dict[str, float] = {
            "a)": cm.accuracy,
            "b)": cm.precision,
            "c)": cm.recall,
            "d)": cm.specificity,
            "e)": cm.npv,
            "f)": cm.alpha_fpr,
            "g)": cm.beta_fnr,
            "h)": cm.f05,
            "i)": cm.f1,
            "j)": cm.f2,
            "k)": cm.lr_plus,
            "l)": cm.lr_minus,
            "m)": cm.mcc,
            "n)": cm.d_prime,
            "o)": cm.c_bias,
        }
        for code, exp_val in expected_values.items():
            assert by_code[code].value == exp_val

        assert by_code["a)"].formatted_value == "100.0%"
        assert by_code["a)"].diagnosis == "Acceptable (>=80%)"
        assert by_code["b)"].formatted_value == "100.0%"
        assert by_code["b)"].diagnosis == "Pure (>=80%)"
        assert by_code["c)"].formatted_value == "100.0%"
        assert by_code["c)"].diagnosis == "Healthy (>=85%)"
        assert by_code["d)"].formatted_value == "100.0%"
        assert by_code["d)"].diagnosis == "Effective (>=70%)"
        assert by_code["e)"].formatted_value == "100.0%"
        assert by_code["e)"].diagnosis == "Reliable (>=75%)"
        assert by_code["f)"].formatted_value == "0.0%"
        assert by_code["f)"].diagnosis == "Low leak (<=20%)"
        assert by_code["g)"].formatted_value == "0.0%"
        assert by_code["g)"].diagnosis == "Low churn (<=15%)"
        assert by_code["h)"].formatted_value == "100.0%"
        assert by_code["h)"].diagnosis == "Strong (>=80%)"
        assert by_code["i)"].formatted_value == "100.0%"
        assert by_code["i)"].diagnosis == "Balanced (>=80%)"
        assert by_code["j)"].formatted_value == "100.0%"
        assert by_code["j)"].diagnosis == "Preserving (>=85%)"
        assert by_code["k)"].formatted_value == "Inf"
        assert by_code["k)"].diagnosis == "Strong (>=10)"
        assert by_code["l)"].formatted_value == "0.00"
        assert by_code["l)"].diagnosis == "Definitive (<=0.1)"
        assert by_code["m)"].formatted_value == "+1.000"
        assert by_code["m)"].diagnosis == "Strong (>=0.60)"
        assert by_code["n)"].formatted_value == f"{cm.d_prime:.2f}"
        assert by_code["n)"].diagnosis == "Excellent (>=2.0)"
        assert by_code["o)"].formatted_value == f"{cm.c_bias:+.2f}"
        assert by_code["o)"].diagnosis == f"Balanced/neutral ({cm.c_bias:.2f})"

    def test_get_all_metrics_moderate_and_weak_bands(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Moderate LR+, LR-, MCC, d-prime, pedantic c > 0.15
        moderate_pedantic = ConfusionMatrix(hit=7, pedantismo_beta=3, permissivo_alfa=2, rejeicao=8)
        m_ped = _diag_by_code(moderate_pedantic)
        assert m_ped["a)"].diagnosis == "Below baseline (<80%)"
        assert m_ped["b)"].diagnosis == "Leaky (<80%)"
        assert m_ped["c)"].diagnosis == "Pedantic (<85%)"
        assert m_ped["d)"].diagnosis == "Effective (>=70%)"
        assert m_ped["e)"].diagnosis == "Noisy (<75%)"
        assert m_ped["f)"].formatted_value == "20.0%"
        assert m_ped["f)"].diagnosis == "Low leak (<=20%)"
        assert m_ped["g)"].formatted_value == "30.0%"
        assert m_ped["g)"].diagnosis == "High churn (>15%)"
        assert m_ped["k)"].formatted_value == f"{moderate_pedantic.lr_plus:.2f}"
        assert m_ped["k)"].diagnosis == "Moderate (2-10)"
        assert m_ped["l)"].formatted_value == f"{moderate_pedantic.lr_minus:.2f}"
        assert m_ped["l)"].diagnosis == "Moderate (0.1-0.5)"
        assert m_ped["m)"].diagnosis == "Moderate (>0.20)"
        assert m_ped["n)"].diagnosis == "Moderate (>=1.0)"
        assert m_ped["o)"].diagnosis == f"Pedantic/conservative (+{moderate_pedantic.c_bias:.2f})"

        # Permissive weak matrix (c < -0.15, weak metrics, LR- Inf)
        weak_perm = ConfusionMatrix(hit=8, pedantismo_beta=2, permissivo_alfa=10, rejeicao=0)
        m_weak = _diag_by_code(weak_perm)
        assert m_weak["b)"].diagnosis == "Leaky (<80%)"
        assert m_weak["d)"].diagnosis == "Weak (<70%)"
        assert m_weak["f)"].diagnosis == "High leak (>20%)"
        assert m_weak["h)"].diagnosis == "Weak (<80%)"
        assert m_weak["i)"].diagnosis == "Unbalanced (<80%)"
        assert m_weak["j)"].diagnosis == "Restrictive (<85%)"
        assert m_weak["k)"].diagnosis == "Weak (<2)"
        assert m_weak["l)"].formatted_value == "Inf"
        assert m_weak["l)"].diagnosis == "Inconclusive (>0.5)"
        assert m_weak["m)"].diagnosis == "Poor (<=0.20)"
        assert m_weak["n)"].diagnosis == "Poor (<1.0)"
        assert m_weak["o)"].diagnosis == f"Permissive/liberal ({weak_perm.c_bias:.2f})"

        # Finite LR- in (0.50, 1.50] must report Inconclusive (>0.5)
        finite_high_lrm = ConfusionMatrix(hit=4, pedantismo_beta=4, permissivo_alfa=4, rejeicao=4)
        assert math.isclose(finite_high_lrm.lr_minus, 1.0)
        assert _diag_by_code(finite_high_lrm)["l)"].diagnosis == "Inconclusive (>0.5)"

        # Exact floating thresholds for d_prime (2.0, 1.0) and c_bias (+-0.15, -1.15)
        base_cm = ConfusionMatrix(hit=5, pedantismo_beta=1, permissivo_alfa=1, rejeicao=5)
        monkeypatch.setattr(ConfusionMatrix, "d_prime", property(lambda _self: 2.0))
        assert _diag_by_code(base_cm)["n)"].diagnosis == "Excellent (>=2.0)"
        monkeypatch.setattr(ConfusionMatrix, "d_prime", property(lambda _self: 1.0))
        assert _diag_by_code(base_cm)["n)"].diagnosis == "Moderate (>=1.0)"

        monkeypatch.setattr(ConfusionMatrix, "c_bias", property(lambda _self: 0.15))
        assert _diag_by_code(base_cm)["o)"].diagnosis == "Balanced/neutral (0.15)"
        monkeypatch.setattr(ConfusionMatrix, "c_bias", property(lambda _self: -0.15))
        assert _diag_by_code(base_cm)["o)"].diagnosis == "Balanced/neutral (-0.15)"
        monkeypatch.setattr(ConfusionMatrix, "c_bias", property(lambda _self: -0.50))
        assert _diag_by_code(base_cm)["o)"].diagnosis == "Permissive/liberal (-0.50)"

    def test_get_all_metrics_exact_boundary_thresholds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Exact 0.80 accuracy, 0.80 precision, 0.20 alpha_fpr
        cm_eq_80 = ConfusionMatrix(hit=4, pedantismo_beta=1, permissivo_alfa=1, rejeicao=4)
        d80 = _diag_by_code(cm_eq_80)
        assert math.isclose(cm_eq_80.accuracy, 0.80)
        assert math.isclose(cm_eq_80.precision, 0.80)
        assert math.isclose(cm_eq_80.alpha_fpr, 0.20)
        assert d80["a)"].diagnosis == "Acceptable (>=80%)"
        assert d80["b)"].diagnosis == "Pure (>=80%)"
        assert d80["f)"].diagnosis == "Low leak (<=20%)"

        # Exact f05 == 0.80 and f1 == 0.80 (kills >= 0.80 -> > 0.80)
        cm_f_exact = ConfusionMatrix(hit=5, pedantismo_beta=1, permissivo_alfa=1, rejeicao=5)
        monkeypatch.setattr(ConfusionMatrix, "f05", property(lambda _self: 0.80))
        monkeypatch.setattr(ConfusionMatrix, "f1", property(lambda _self: 0.80))
        df80 = _diag_by_code(cm_f_exact)
        assert df80["h)"].diagnosis == "Strong (>=80%)"
        assert df80["i)"].diagnosis == "Balanced (>=80%)"

        # Exact 0.85 recall & 0.15 beta_fnr; hit=17, beta=3 -> recall=0.85, fnr=0.15
        # With alpha=3, rej=17 -> prec=0.85, spec=0.85, f05=0.85, f1=0.85, f2=0.85
        cm_eq_85 = ConfusionMatrix(hit=17, pedantismo_beta=3, permissivo_alfa=3, rejeicao=17)
        d85 = _diag_by_code(cm_eq_85)
        assert math.isclose(cm_eq_85.recall, 0.85)
        assert math.isclose(cm_eq_85.beta_fnr, 0.15)
        assert d85["c)"].diagnosis == "Healthy (>=85%)"
        assert d85["g)"].diagnosis == "Low churn (<=15%)"
        assert d85["j)"].diagnosis == "Preserving (>=85%)"

        # Exact 0.70 specificity & 0.75 npv:
        # spec = rej / (rej + alpha) = 7 / 10 = 0.70; npv = rej / (rej + beta) = 9 / 12 = 0.75
        cm_spec_npv = ConfusionMatrix(hit=3, pedantismo_beta=3, permissivo_alfa=4, rejeicao=9)
        cm_spec_exact = ConfusionMatrix(hit=3, pedantismo_beta=1, permissivo_alfa=3, rejeicao=7)
        assert math.isclose(cm_spec_npv.npv, 0.75)
        assert _diag_by_code(cm_spec_npv)["e)"].diagnosis == "Reliable (>=75%)"
        assert math.isclose(cm_spec_exact.specificity, 0.70)
        assert _diag_by_code(cm_spec_exact)["d)"].diagnosis == "Effective (>=70%)"

        # Exact LR+ == 10.0 and LR+ == 2.0 and LR- == 0.10 and LR- == 0.50:
        # hit=5, beta=5 -> recall=0.5, fnr=0.5; alpha=1, rej=19 -> fpr=0.05, spec=0.95 => LR+ = 10.0
        cm_lr10 = ConfusionMatrix(hit=5, pedantismo_beta=5, permissivo_alfa=1, rejeicao=19)
        assert math.isclose(cm_lr10.lr_plus, 10.0)
        assert _diag_by_code(cm_lr10)["k)"].diagnosis == "Strong (>=10)"

        # hit=5, beta=5 -> recall=0.5; alpha=5, rej=15 -> fpr=0.25 => LR+ = 2.0
        cm_lr2 = ConfusionMatrix(hit=5, pedantismo_beta=5, permissivo_alfa=5, rejeicao=15)
        assert math.isclose(cm_lr2.lr_plus, 2.0)
        assert _diag_by_code(cm_lr2)["k)"].diagnosis == "Moderate (2-10)"

        # hit=19, beta=1 -> fnr=0.05; alpha=5, rej=5 -> spec=0.5 => LR- = 0.10
        cm_lrm01 = ConfusionMatrix(hit=19, pedantismo_beta=1, permissivo_alfa=5, rejeicao=5)
        assert math.isclose(cm_lrm01.lr_minus, 0.10)
        assert _diag_by_code(cm_lrm01)["l)"].diagnosis == "Definitive (<=0.1)"

        # hit=3, beta=1 -> fnr=0.25; alpha=5, rej=5 -> spec=0.5 => LR- = 0.50
        cm_lrm05 = ConfusionMatrix(hit=3, pedantismo_beta=1, permissivo_alfa=5, rejeicao=5)
        assert math.isclose(cm_lrm05.lr_minus, 0.50)
        assert _diag_by_code(cm_lrm05)["l)"].diagnosis == "Moderate (0.1-0.5)"

        # MCC == 0.60 and MCC == 0.20 (symmetric hit=rejeicao=h, alpha=beta=a => MCC=(h-a)/(h+a)):
        cm_mcc06 = ConfusionMatrix(hit=4, pedantismo_beta=1, permissivo_alfa=1, rejeicao=4)
        assert math.isclose(cm_mcc06.mcc, 0.60)
        assert _diag_by_code(cm_mcc06)["m)"].diagnosis == "Strong (>=0.60)"

        cm_mcc02 = ConfusionMatrix(hit=3, pedantismo_beta=2, permissivo_alfa=2, rejeicao=3)
        assert math.isclose(cm_mcc02.mcc, 0.20)
        assert _diag_by_code(cm_mcc02)["m)"].diagnosis == "Poor (<=0.20)"

        # F0.5 == 0.80 exact (hit=4, beta=1, alpha=1, rej=4 -> p=r=0.80 -> f05=0.80)
        assert math.isclose(cm_eq_80.f05, 0.80)
        assert d80["h)"].diagnosis == "Strong (>=80%)"

        # d_prime & c_bias boundary thresholds around 2.0 / 1.0 / +-0.15
        cm_dp_ge1 = ConfusionMatrix(hit=7, pedantismo_beta=3, permissivo_alfa=3, rejeicao=7)
        assert cm_dp_ge1.d_prime > 1.0
        assert _diag_by_code(cm_dp_ge1)["n)"].diagnosis == "Moderate (>=1.0)"
        assert -0.15 <= cm_dp_ge1.c_bias <= 0.15
        assert (
            _diag_by_code(cm_dp_ge1)["o)"].diagnosis == f"Balanced/neutral ({cm_dp_ge1.c_bias:.2f})"
        )

    def test_result_set_and_summary_models_expose_expected_fields(self) -> None:
        rs = CalibrationResultSet()
        assert rs.tp == 0
        assert rs.fp == 0
        assert rs.fn == 0
        assert rs.tn == 0
        assert rs.invalid == 0
        assert rs.total_valid == 0
        assert rs.accuracy == 0.0
        assert rs.precision == 0.0
        assert rs.recall == 0.0
        assert rs.f1 == 0.0

        rs.overall.record("PASS", "PASS")
        rs.overall.record("FAIL", "PASS")
        rs.overall.record("PASS", "FAIL")
        rs.overall.record("FAIL", "FAIL")
        rs.overall.record("BAD", "PASS")
        assert rs.tp == 1
        assert rs.fp == 1
        assert rs.fn == 1
        assert rs.tn == 1
        assert rs.invalid == 1
        assert rs.total_valid == 4
        assert rs.accuracy == 0.5
        assert rs.precision == 0.5
        assert rs.recall == 0.5
        assert rs.f1 == 0.5

        item_res = ItemEvaluationResult(
            actual="PASS",
            expected="PASS",
            score=0.9,
            reasoning="clean",
        )
        assert item_res.target_actual == ""
        assert item_res.target_score == 0.0
        assert tuple(item_res) == ("PASS", "PASS", 0.9, "clean")

        summary = ModelBenchmarkSummary(
            stage="fluid_prose",
            provider="gemini",
            model="gemini-4-hydrogen",
            status="APROVADO",
        )
        assert summary.accuracy == 0.0
        assert summary.error_message == ""
        outcome = CalibrationSuiteOutcome(summaries=(summary,), has_errors=False)
        assert outcome.summaries == (summary,)
        assert outcome.has_errors is False
