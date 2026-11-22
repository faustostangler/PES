"""Presentation formatter for Signal Detection Theory diagnostics, ASCII reports, and CLI events.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TextIO

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationVerdict,
    ConfusionMatrix,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.executor import CalibrationEvent
from cresmo.application.evals.specs import StageCalibrationSpec


@dataclass(frozen=True, slots=True)
class MetricInfo:
    """Presentation descriptor encapsulating formula metadata, Sheets formula, and diagnosis."""

    code: str
    name: str
    math_formula: str
    sheets_formula: str
    value: float
    formatted_value: str
    practical_implication: str
    high_meaning: str
    low_meaning: str
    diagnosis: str


def build_sdt_metric_diagnostics(matrix: ConfusionMatrix) -> list[MetricInfo]:
    """Build 15 diagnostic MetricInfo rows from a pure ConfusionMatrix.

    Args:
        matrix: Evaluated confusion matrix containing SDT counts.

    Returns:
        Ordered list of 15 ``MetricInfo`` diagnostic descriptors (codes ``a)`` through ``o)``).
    """
    lr_plus_val = matrix.lr_plus
    lr_minus_val = matrix.lr_minus
    mcc_val = matrix.mcc
    dp_val = matrix.d_prime
    c_val = matrix.c_bias

    lr_plus_str = f"{lr_plus_val:.2f}" if not math.isinf(lr_plus_val) else "Inf"
    lr_minus_str = f"{lr_minus_val:.2f}" if not math.isinf(lr_minus_val) else "Inf"
    c_diag = (
        f"Pedantic/conservative (+{c_val:.2f})"
        if c_val > 0.15
        else f"Permissive/liberal ({c_val:.2f})"
        if c_val < -0.15
        else f"Balanced/neutral ({c_val:.2f})"
    )

    return [
        MetricInfo(
            code="a)",
            name="Accuracy",
            math_formula="(Hit + CorrectRej) / Total",
            sheets_formula="=(B4+C5)/D6",
            value=matrix.accuracy,
            formatted_value=f"{matrix.accuracy * 100:.1f}%",
            practical_implication="Overall proportion of correct verdicts.",
            high_meaning="Most decisions align with ground truth.",
            low_meaning="Judge frequently misclassifies items.",
            diagnosis=(
                "Acceptable (>=80%)" if matrix.accuracy >= 0.80 else "Below baseline (<80%)"
            ),
        ),
        MetricInfo(
            code="b)",
            name="Precision / PPV",
            math_formula="Hit / (Hit + FalseAccept)",
            sheets_formula="=B4/B6",
            value=matrix.precision,
            formatted_value=f"{matrix.precision * 100:.1f}%",
            practical_implication="Purity of PASS verdicts.",
            high_meaning="Approvals rarely pass defective candidates.",
            low_meaning="Defective candidates leak through PASS gate.",
            diagnosis="Pure (>=80%)" if matrix.precision >= 0.80 else "Leaky (<80%)",
        ),
        MetricInfo(
            code="c)",
            name="Recall / Sensitivity",
            math_formula="Hit / (Hit + FalseReject)",
            sheets_formula="=B4/D4",
            value=matrix.recall,
            formatted_value=f"{matrix.recall * 100:.1f}%",
            practical_implication="Share of valid candidates approved.",
            high_meaning="Minimal false rejections of valid work.",
            low_meaning="Judge is overly pedantic and discards valid work.",
            diagnosis="Healthy (>=85%)" if matrix.recall >= 0.85 else "Pedantic (<85%)",
        ),
        MetricInfo(
            code="d)",
            name="Specificity (TNR)",
            math_formula="CorrectRej / (CorrectRej + FalseAccept)",
            sheets_formula="=C5/D5",
            value=matrix.specificity,
            formatted_value=f"{matrix.specificity * 100:.1f}%",
            practical_implication="Share of defective candidates caught.",
            high_meaning="Strong gate against defects.",
            low_meaning="Defects bypass rejection.",
            diagnosis="Effective (>=70%)" if matrix.specificity >= 0.70 else "Weak (<70%)",
        ),
        MetricInfo(
            code="e)",
            name="NPV",
            math_formula="CorrectRej / (CorrectRej + FalseReject)",
            sheets_formula="=C5/C6",
            value=matrix.npv,
            formatted_value=f"{matrix.npv * 100:.1f}%",
            practical_implication="Reliability of FAIL verdicts.",
            high_meaning="Rejections correspond to real defects.",
            low_meaning="Many valid candidates are rejected.",
            diagnosis="Reliable (>=75%)" if matrix.npv >= 0.75 else "Noisy (<75%)",
        ),
        MetricInfo(
            code="f)",
            name="Alpha Rate (FPR)",
            math_formula="FalseAccept / (CorrectRej + FalseAccept)",
            sheets_formula="=B5/D5",
            value=matrix.alpha_fpr,
            formatted_value=f"{matrix.alpha_fpr * 100:.1f}%",
            practical_implication="Rate of defective texts leaking through.",
            high_meaning="Unacceptable defect leakage.",
            low_meaning="Hermetic quality filter.",
            diagnosis="Low leak (<=20%)" if matrix.alpha_fpr <= 0.20 else "High leak (>20%)",
        ),
        MetricInfo(
            code="g)",
            name="Beta Rate (FNR)",
            math_formula="FalseReject / (Hit + FalseReject)",
            sheets_formula="=C4/D4",
            value=matrix.beta_fnr,
            formatted_value=f"{matrix.beta_fnr * 100:.1f}%",
            practical_implication="Rate of valid texts wasted in retries.",
            high_meaning="Excessive self-healing churn.",
            low_meaning="Low pedantry.",
            diagnosis="Low churn (<=15%)" if matrix.beta_fnr <= 0.15 else "High churn (>15%)",
        ),
        MetricInfo(
            code="h)",
            name="F0.5-Score",
            math_formula="1.25 * (P * R) / (0.25 * P + R)",
            sheets_formula="=(1+H17^2)*(D$11*D$12)/((H17^2*D$11)+D$12)",
            value=matrix.f05,
            formatted_value=f"{matrix.f05 * 100:.1f}%",
            practical_implication="Precision-weighted harmonic mean (2x Precision).",
            high_meaning="Strong fidelity and low permissiveness.",
            low_meaning="Leaked defects degraded gate purity.",
            diagnosis="Strong (>=80%)" if matrix.f05 >= 0.80 else "Weak (<80%)",
        ),
        MetricInfo(
            code="i)",
            name="F1-Score",
            math_formula="2 * (P * R) / (P + R)",
            sheets_formula="=(1+H18^2)*(D$11*D$12)/((H18^2*D$11)+D$12)",
            value=matrix.f1,
            formatted_value=f"{matrix.f1 * 100:.1f}%",
            practical_implication="Balanced harmonic mean of Precision and Recall.",
            high_meaning="Well-balanced discrimination.",
            low_meaning="Precision/Recall imbalance or weak discrimination.",
            diagnosis="Balanced (>=80%)" if matrix.f1 >= 0.80 else "Unbalanced (<80%)",
        ),
        MetricInfo(
            code="j)",
            name="F2-Score",
            math_formula="5 * (P * R) / (4 * P + R)",
            sheets_formula="=(1+H19^2)*(D$11*D$12)/((H19^2*D$11)+D$12)",
            value=matrix.f2,
            formatted_value=f"{matrix.f2 * 100:.1f}%",
            practical_implication="Recall-weighted harmonic mean (2x Recall).",
            high_meaning="Preserves nearly all valid texts.",
            low_meaning="Pedantry discards too much valid output.",
            diagnosis="Preserving (>=85%)" if matrix.f2 >= 0.85 else "Restrictive (<85%)",
        ),
        MetricInfo(
            code="k)",
            name="LR+",
            math_formula="Sensitivity / (1 - Specificity)",
            sheets_formula="=(B4/D4)/(B5/D5)",
            value=lr_plus_val,
            formatted_value=lr_plus_str,
            practical_implication="Evidentiary weight of a PASS decision.",
            high_meaning="Strong confirmation of quality (>10).",
            low_meaning="Weak confirmation (<2).",
            diagnosis=(
                "Strong (>=10)"
                if lr_plus_val >= 10.0
                else "Moderate (2-10)"
                if lr_plus_val >= 2.0
                else "Weak (<2)"
            ),
        ),
        MetricInfo(
            code="l)",
            name="LR-",
            math_formula="(1 - Sensitivity) / Specificity",
            sheets_formula="=(C4/D4)/(C5/D5)",
            value=lr_minus_val,
            formatted_value=lr_minus_str,
            practical_implication="Evidentiary weight of a FAIL decision.",
            high_meaning="Inconclusive rejection (>0.5).",
            low_meaning="Definitive defect confirmation (<0.1).",
            diagnosis=(
                "Definitive (<=0.1)"
                if lr_minus_val <= 0.10
                else "Moderate (0.1-0.5)"
                if lr_minus_val <= 0.50
                else "Inconclusive (>0.5)"
            ),
        ),
        MetricInfo(
            code="m)",
            name="Matthews Correlation (MCC)",
            math_formula="((Hit * CorrectRej) - (FalseAccept * FalseReject)) / SQRT(...)",
            sheets_formula="=((B4*C5)-(B5*C4))/SQRT(B6*D4*D5*C6)",
            value=mcc_val,
            formatted_value=f"{mcc_val:+.3f}",
            practical_implication="Full confusion matrix correlation in [-1, +1].",
            high_meaning="Strong alignment with ground truth.",
            low_meaning="Random or inverted alignment (<=0).",
            diagnosis=(
                "Strong (>=0.60)"
                if mcc_val >= 0.60
                else "Moderate (>0.20)"
                if mcc_val > 0.20
                else "Poor (<=0.20)"
            ),
        ),
        MetricInfo(
            code="n)",
            name="D-prime (d')",
            math_formula="NORM.S.INV(HitRate) - NORM.S.INV(FARate)",
            sheets_formula="=NORM.S.INV(B4/D4)-NORM.S.INV(B5/D5)",
            value=dp_val,
            formatted_value=f"{dp_val:.2f}",
            practical_implication="Intrinsic signal-vs-noise discrimination acuity.",
            high_meaning="Excellent discrimination (>=2.0).",
            low_meaning="Inability to separate valid vs defective (~0).",
            diagnosis=(
                "Excellent (>=2.0)"
                if dp_val >= 2.0
                else "Moderate (>=1.0)"
                if dp_val >= 1.0
                else "Poor (<1.0)"
            ),
        ),
        MetricInfo(
            code="o)",
            name="Criterion c (Bias)",
            math_formula="-0.5 * (NORM.S.INV(HitRate) + NORM.S.INV(FARate))",
            sheets_formula="=-0.5*(NORM.S.INV(B4/D4)+NORM.S.INV(B5/D5))",
            value=c_val,
            formatted_value=f"{c_val:+.2f}",
            practical_implication="Systematic decision threshold bias.",
            high_meaning="Pedantic/conservative (+).",
            low_meaning="Permissive/liberal (-).",
            diagnosis=c_diag,
        ),
    ]


def format_confusion_matrix_2x2(title: str, matrix: ConfusionMatrix) -> str:
    """Render an ASCII 2x2 Signal Detection Theory confusion matrix table.

    Args:
        title: Table header title.
        matrix: Confusion matrix counts.

    Returns:
        Formatted multi-line ASCII table string.
    """
    lines = [
        "\n" + "=" * 80,
        title,
        "-" * 80,
        f"{'Ground Truth \\ Judge':<28} | {'Judge: PASS':<20} | {'Judge: FAIL':<20} | {'Total':<8}",
        "-" * 80,
        (
            f"{'PASS (Valid Output)':<28} | "
            f"{f'HIT (TP): {matrix.hit}':<20} | "
            f"{f'FALSE REJECT (FN): {matrix.false_reject_beta}':<20} | "
            f"{matrix.total_valid:<8}"
        ),
        (
            f"{'FAIL (Defective Output)':<28} | "
            f"{f'FALSE ACCEPT (FP): {matrix.false_accept_alpha}':<20} | "
            f"{f'CORRECT REJECT (TN): {matrix.correct_rejection}':<20} | "
            f"{matrix.total_defective:<8}"
        ),
        "-" * 80,
        (
            f"{'Total by Judge':<28} | {matrix.total_approved:<20} | "
            f"{matrix.total_rejected:<20} | {matrix.total_samples:<8}"
        ),
        "=" * 80,
    ]
    return "\n".join(lines)


def format_calibration_report(
    spec: StageCalibrationSpec,
    results: CalibrationResultSet,
    provider: str,
    model: str,
    *,
    timestamp: datetime | None = None,
) -> str:
    """Format full Signal Detection Theory, slice breakdown, and disagreement report.

    Args:
        spec: Stage calibration specification.
        results: Aggregated calibration results.
        provider: Judge provider name.
        model: Judge model identifier.
        timestamp: Optional UTC timestamp for deterministic rendering.

    Returns:
        Complete formatted calibration report ending with a trailing newline.
    """
    report_ts = timestamp if timestamp is not None else datetime.now(UTC)
    target_m = results.target_isolated
    lines: list[str] = [
        "=" * 80,
        f"LLM JUDGE CALIBRATION REPORT ({spec.label.upper()})",
        "=" * 80,
        f"Timestamp:       {report_ts.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Stage:           {spec.stage_name}",
        f"Provider:        {provider}",
        f"Model:           {model}",
        "Fallback Mode:   DISABLED (enable_fallback=False)",
        (
            f"Valid Items:     {target_m.total_samples} "
            f"(fresh={results.evaluated_items}, resumed={results.skipped_from_checkpoint})"
        ),
        format_confusion_matrix_2x2(
            "2x2 CONFUSION MATRIX (ISOLATED TARGET CRITERION)",
            target_m,
        ),
        "\n" + "=" * 80,
        "15 SIGNAL DETECTION THEORY (SDT) METRICS (TARGET ISOLATED)",
        "-" * 80,
        f"{'Code':<4} {'Metric':<28} | {'Value':<10} | {'Diagnosis'}",
        "-" * 80,
    ]
    for info in build_sdt_metric_diagnostics(target_m):
        lines.append(
            f"{info.code:<4} {info.name:<28} | {info.formatted_value:<10} | {info.diagnosis}"
        )

    lines.append(
        format_confusion_matrix_2x2(
            "2x2 CONFUSION MATRIX (GLOBAL COMPOSITE GATE)",
            results.overall,
        )
    )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY CRITERION",
            "-" * 80,
            (
                f"{'Criterion':<34} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            "-" * 80,
        ]
    )
    for crit, m in results.by_criterion.items():
        lines.append(
            f"{crit:<34} | {m.total_samples:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY DIFFICULTY",
            "-" * 80,
            (
                f"{'Difficulty':<18} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            "-" * 80,
        ]
    )
    for diff, m in results.by_difficulty.items():
        lines.append(
            f"{diff:<18} | {m.total_samples:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    if results.disagreements:
        lines.extend(["\n" + "=" * 80, "DISAGREEMENTS", "-" * 80])
        for d in results.disagreements:
            lines.append(
                f"[{d['id']}] crit={d['criterion']} diff={d['difficulty']} "
                f"exp={d['expected']} got={d['actual_target']} ({d['score']:.2f}): "
                f"{str(d['reasoning'])[:180]}"
            )

    return "\n".join(lines) + "\n"


def format_benchmark_summary(summaries: Sequence[ModelBenchmarkSummary]) -> str:
    """Format cross-stage and cross-model benchmark comparison ASCII table.

    Args:
        summaries: Sequence of per-target benchmark summary records.

    Returns:
        Formatted ASCII comparison table string.
    """
    lines = [
        "\n" + "=" * 116,
        "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)",
        "=" * 116,
        (
            f"{'Stage':<12} | {'Model':<32} | {'Status':<14} | {'Done':<7} | "
            f"{'Acc':<6} | {'d-prime':<7} | {'F1':<6} | {'Prec':<6} | {'Rec':<6} | {'FPR':<6}"
        ),
        "-" * 116,
    ]
    for s in summaries:
        label = f"{s.provider}:{s.model}"
        done = f"{s.evaluated_total}/{s.dataset_total}"
        status_text = s.status.value
        if s.status in (CalibrationVerdict.COOLDOWN, CalibrationVerdict.ERROR):
            extra = (
                f"retry in {int(s.cooldown_remaining_s)}s"
                if s.status is CalibrationVerdict.COOLDOWN
                else s.error_message[:32]
            )
            lines.append(f"{s.stage:<12} | {label:<32} | {status_text:<14} | {done:<7} | {extra}")
        else:
            lines.append(
                f"{s.stage:<12} | {label:<32} | {status_text:<14} | {done:<7} | "
                f"{s.accuracy * 100:5.1f}% | {s.d_prime:7.2f} | {s.f1:6.3f} | "
                f"{s.precision * 100:5.1f}% | {s.recall * 100:5.1f}% | {s.alpha_fpr * 100:5.1f}%"
            )
    lines.append("=" * 116 + "\n")
    return "\n".join(lines)


def render_calibration_event(
    event: CalibrationEvent,
    *,
    out_stream: TextIO | None = None,
) -> None:
    """Render a CalibrationEvent message line to standard output stream.

    Args:
        event: Emitted calibration progress event.
        out_stream: Optional text stream overriding ``sys.stdout``.
    """
    stream = out_stream if out_stream is not None else sys.stdout
    stream.write(f"{event.message}\n")
