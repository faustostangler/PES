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
    """Presentation descriptor summarizing one SDT metric row."""

    code: str
    name: str
    formatted_value: str
    diagnosis: str


def _band_diagnosis(
    val: float,
    thresholds: Sequence[tuple[float, str]],
    default: str,
    *,
    upper_bound: bool = False,
) -> str:
    for limit, label in thresholds:
        if (val <= limit) if upper_bound else (val >= limit):
            return label
    return default


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

    specs: list[tuple[str, str, str, str]] = [
        ("a)", "Accuracy", f"{matrix.accuracy * 100:.1f}%", _band_diagnosis(matrix.accuracy, [(0.80, "Acceptable (>=80%)")], "Below baseline (<80%)")),
        ("b)", "Precision / PPV", f"{matrix.precision * 100:.1f}%", _band_diagnosis(matrix.precision, [(0.80, "Pure (>=80%)")], "Leaky (<80%)")),
        ("c)", "Recall / Sensitivity", f"{matrix.recall * 100:.1f}%", _band_diagnosis(matrix.recall, [(0.85, "Healthy (>=85%)")], "Pedantic (<85%)")),
        ("d)", "Specificity (TNR)", f"{matrix.specificity * 100:.1f}%", _band_diagnosis(matrix.specificity, [(0.70, "Effective (>=70%)")], "Weak (<70%)")),
        ("e)", "NPV", f"{matrix.npv * 100:.1f}%", _band_diagnosis(matrix.npv, [(0.75, "Reliable (>=75%)")], "Noisy (<75%)")),
        ("f)", "Alpha Rate (FPR)", f"{matrix.alpha_fpr * 100:.1f}%", _band_diagnosis(matrix.alpha_fpr, [(0.20, "Low leak (<=20%)")], "High leak (>20%)", upper_bound=True)),
        ("g)", "Beta Rate (FNR)", f"{matrix.beta_fnr * 100:.1f}%", _band_diagnosis(matrix.beta_fnr, [(0.15, "Low churn (<=15%)")], "High churn (>15%)", upper_bound=True)),
        ("h)", "F0.5-Score", f"{matrix.f05 * 100:.1f}%", _band_diagnosis(matrix.f05, [(0.80, "Strong (>=80%)")], "Weak (<80%)")),
        ("i)", "F1-Score", f"{matrix.f1 * 100:.1f}%", _band_diagnosis(matrix.f1, [(0.80, "Balanced (>=80%)")], "Unbalanced (<80%)")),
        ("j)", "F2-Score", f"{matrix.f2 * 100:.1f}%", _band_diagnosis(matrix.f2, [(0.85, "Preserving (>=85%)")], "Restrictive (<85%)")),
        ("k)", "LR+", lr_plus_str, _band_diagnosis(lr_plus_val, [(10.0, "Strong (>=10)"), (2.0, "Moderate (2-10)")], "Weak (<2)")),
        ("l)", "LR-", lr_minus_str, _band_diagnosis(lr_minus_val, [(0.10, "Definitive (<=0.1)"), (0.50, "Moderate (0.1-0.5)")], "Inconclusive (>0.5)", upper_bound=True)),
        ("m)", "Matthews Correlation (MCC)", f"{mcc_val:+.3f}", "Poor (<=0.20)" if mcc_val <= 0.20 else _band_diagnosis(mcc_val, [(0.60, "Strong (>=0.60)")], "Moderate (>0.20)")),
        ("n)", "D-prime (d')", f"{dp_val:.2f}", _band_diagnosis(dp_val, [(2.0, "Excellent (>=2.0)"), (1.0, "Moderate (>=1.0)")], "Poor (<1.0)")),
        ("o)", "Criterion c (Bias)", f"{c_val:+.2f}", c_diag),
    ]
    return [MetricInfo(code=c, name=n, formatted_value=v, diagnosis=d) for c, n, v, d in specs]


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
