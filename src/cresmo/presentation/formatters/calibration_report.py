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
from typing import Final, TextIO

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationVerdict,
    ConfusionMatrix,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.executor import CalibrationEvent
from cresmo.application.evals.specs import StageCalibrationSpec

_PERCENT_MULTIPLIER: Final[float] = 100.0
_INF_DISPLAY_LABEL: Final[str] = "Inf"
_BIAS_PEDANTIC_THRESHOLD: Final[float] = 0.15
_BIAS_PERMISSIVE_THRESHOLD: Final[float] = -0.15
_ACCURACY_ACCEPTABLE_MIN: Final[float] = 0.80
_PRECISION_PURE_MIN: Final[float] = 0.80
_RECALL_HEALTHY_MIN: Final[float] = 0.85
_SPECIFICITY_EFFECTIVE_MIN: Final[float] = 0.70
_NPV_RELIABLE_MIN: Final[float] = 0.75
_FPR_LOW_LEAK_MAX: Final[float] = 0.20
_FNR_LOW_CHURN_MAX: Final[float] = 0.15
_F05_STRONG_MIN: Final[float] = 0.80
_F1_BALANCED_MIN: Final[float] = 0.80
_F2_PRESERVING_MIN: Final[float] = 0.85
_LR_PLUS_STRONG_MIN: Final[float] = 10.0
_LR_PLUS_MODERATE_MIN: Final[float] = 2.0
_LR_MINUS_DEFINITIVE_MAX: Final[float] = 0.10
_LR_MINUS_MODERATE_MAX: Final[float] = 0.50
_MCC_POOR_MAX: Final[float] = 0.20
_MCC_STRONG_MIN: Final[float] = 0.60
_DPRIME_EXCELLENT_MIN: Final[float] = 2.0
_DPRIME_MODERATE_MIN: Final[float] = 1.0
_REPORT_BANNER_WIDTH: Final[int] = 80
_BENCHMARK_BANNER_WIDTH: Final[int] = 116
_REPORT_DIVIDER_EQ: Final[str] = "=" * _REPORT_BANNER_WIDTH
_REPORT_DIVIDER_DASH: Final[str] = "-" * _REPORT_BANNER_WIDTH
_BENCHMARK_DIVIDER_EQ: Final[str] = "=" * _BENCHMARK_BANNER_WIDTH
_BENCHMARK_DIVIDER_DASH: Final[str] = "-" * _BENCHMARK_BANNER_WIDTH
_UTC_TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S UTC"
_REASONING_PREVIEW_MAX_CHARS: Final[int] = 180
_ERROR_PREVIEW_MAX_CHARS: Final[int] = 32


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

    lr_plus_str = f"{lr_plus_val:.2f}" if not math.isinf(lr_plus_val) else _INF_DISPLAY_LABEL
    lr_minus_str = f"{lr_minus_val:.2f}" if not math.isinf(lr_minus_val) else _INF_DISPLAY_LABEL
    c_diag = (
        f"Pedantic/conservative (+{c_val:.2f})"
        if c_val > _BIAS_PEDANTIC_THRESHOLD
        else f"Permissive/liberal ({c_val:.2f})"
        if c_val < _BIAS_PERMISSIVE_THRESHOLD
        else f"Balanced/neutral ({c_val:.2f})"
    )

    specs: list[tuple[str, str, str, str]] = [
        ("a)", "Accuracy", f"{matrix.accuracy * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.accuracy, [(_ACCURACY_ACCEPTABLE_MIN, "Acceptable (>=80%)")], "Below baseline (<80%)")),
        ("b)", "Precision / PPV", f"{matrix.precision * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.precision, [(_PRECISION_PURE_MIN, "Pure (>=80%)")], "Leaky (<80%)")),
        ("c)", "Recall / Sensitivity", f"{matrix.recall * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.recall, [(_RECALL_HEALTHY_MIN, "Healthy (>=85%)")], "Pedantic (<85%)")),
        ("d)", "Specificity (TNR)", f"{matrix.specificity * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.specificity, [(_SPECIFICITY_EFFECTIVE_MIN, "Effective (>=70%)")], "Weak (<70%)")),
        ("e)", "NPV", f"{matrix.npv * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.npv, [(_NPV_RELIABLE_MIN, "Reliable (>=75%)")], "Noisy (<75%)")),
        ("f)", "Alpha Rate (FPR)", f"{matrix.alpha_fpr * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.alpha_fpr, [(_FPR_LOW_LEAK_MAX, "Low leak (<=20%)")], "High leak (>20%)", upper_bound=True)),
        ("g)", "Beta Rate (FNR)", f"{matrix.beta_fnr * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.beta_fnr, [(_FNR_LOW_CHURN_MAX, "Low churn (<=15%)")], "High churn (>15%)", upper_bound=True)),
        ("h)", "F0.5-Score", f"{matrix.f05 * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.f05, [(_F05_STRONG_MIN, "Strong (>=80%)")], "Weak (<80%)")),
        ("i)", "F1-Score", f"{matrix.f1 * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.f1, [(_F1_BALANCED_MIN, "Balanced (>=80%)")], "Unbalanced (<80%)")),
        ("j)", "F2-Score", f"{matrix.f2 * _PERCENT_MULTIPLIER:.1f}%", _band_diagnosis(matrix.f2, [(_F2_PRESERVING_MIN, "Preserving (>=85%)")], "Restrictive (<85%)")),
        ("k)", "LR+", lr_plus_str, _band_diagnosis(lr_plus_val, [(_LR_PLUS_STRONG_MIN, "Strong (>=10)"), (_LR_PLUS_MODERATE_MIN, "Moderate (2-10)")], "Weak (<2)")),
        ("l)", "LR-", lr_minus_str, _band_diagnosis(lr_minus_val, [(_LR_MINUS_DEFINITIVE_MAX, "Definitive (<=0.1)"), (_LR_MINUS_MODERATE_MAX, "Moderate (0.1-0.5)")], "Inconclusive (>0.5)", upper_bound=True)),
        ("m)", "Matthews Correlation (MCC)", f"{mcc_val:+.3f}", "Poor (<=0.20)" if mcc_val <= _MCC_POOR_MAX else _band_diagnosis(mcc_val, [(_MCC_STRONG_MIN, "Strong (>=0.60)")], "Moderate (>0.20)")),
        ("n)", "D-prime (d')", f"{dp_val:.2f}", _band_diagnosis(dp_val, [(_DPRIME_EXCELLENT_MIN, "Excellent (>=2.0)"), (_DPRIME_MODERATE_MIN, "Moderate (>=1.0)")], "Poor (<1.0)")),
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
        "\n" + _REPORT_DIVIDER_EQ,
        title,
        _REPORT_DIVIDER_DASH,
        f"{'Ground Truth \\ Judge':<28} | {'Judge: PASS':<20} | {'Judge: FAIL':<20} | {'Total':<8}",
        _REPORT_DIVIDER_DASH,
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
        _REPORT_DIVIDER_DASH,
        (
            f"{'Total by Judge':<28} | {matrix.total_approved:<20} | "
            f"{matrix.total_rejected:<20} | {matrix.total_samples:<8}"
        ),
        _REPORT_DIVIDER_EQ,
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
        _REPORT_DIVIDER_EQ,
        f"LLM JUDGE CALIBRATION REPORT ({spec.label.upper()})",
        _REPORT_DIVIDER_EQ,
        f"Timestamp:       {report_ts.strftime(_UTC_TIMESTAMP_FORMAT)}",
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
        "\n" + _REPORT_DIVIDER_EQ,
        "15 SIGNAL DETECTION THEORY (SDT) METRICS (TARGET ISOLATED)",
        _REPORT_DIVIDER_DASH,
        f"{'Code':<4} {'Metric':<28} | {'Value':<10} | {'Diagnosis'}",
        _REPORT_DIVIDER_DASH,
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
            "\n" + _REPORT_DIVIDER_EQ,
            "SLICE BREAKDOWN BY CRITERION",
            _REPORT_DIVIDER_DASH,
            (
                f"{'Criterion':<34} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            _REPORT_DIVIDER_DASH,
        ]
    )
    for crit, m in results.by_criterion.items():
        lines.append(
            f"{crit:<34} | {m.total_samples:<4} | {m.accuracy * _PERCENT_MULTIPLIER:5.1f}% | "
            f"{m.precision * _PERCENT_MULTIPLIER:5.1f}% | {m.recall * _PERCENT_MULTIPLIER:5.1f}% | "
            f"{m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    lines.extend(
        [
            "\n" + _REPORT_DIVIDER_EQ,
            "SLICE BREAKDOWN BY DIFFICULTY",
            _REPORT_DIVIDER_DASH,
            (
                f"{'Difficulty':<18} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            _REPORT_DIVIDER_DASH,
        ]
    )
    for diff, m in results.by_difficulty.items():
        lines.append(
            f"{diff:<18} | {m.total_samples:<4} | {m.accuracy * _PERCENT_MULTIPLIER:5.1f}% | "
            f"{m.precision * _PERCENT_MULTIPLIER:5.1f}% | {m.recall * _PERCENT_MULTIPLIER:5.1f}% | "
            f"{m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    if results.disagreements:
        lines.extend(["\n" + _REPORT_DIVIDER_EQ, "DISAGREEMENTS", _REPORT_DIVIDER_DASH])
        for d in results.disagreements:
            lines.append(
                f"[{d['id']}] crit={d['criterion']} diff={d['difficulty']} "
                f"exp={d['expected']} got={d['actual_target']} ({d['score']:.2f}): "
                f"{str(d['reasoning'])[:_REASONING_PREVIEW_MAX_CHARS]}"
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
        "\n" + _BENCHMARK_DIVIDER_EQ,
        "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)",
        _BENCHMARK_DIVIDER_EQ,
        (
            f"{'Stage':<12} | {'Model':<32} | {'Status':<14} | {'Done':<7} | "
            f"{'Acc':<6} | {'d-prime':<7} | {'F1':<6} | {'Prec':<6} | {'Rec':<6} | {'FPR':<6}"
        ),
        _BENCHMARK_DIVIDER_DASH,
    ]
    for s in summaries:
        label = f"{s.provider}:{s.model}"
        done = f"{s.evaluated_total}/{s.dataset_total}"
        status_text = s.status.value
        if s.status in (CalibrationVerdict.COOLDOWN, CalibrationVerdict.ERROR):
            extra = (
                f"retry in {int(s.cooldown_remaining_s)}s"
                if s.status is CalibrationVerdict.COOLDOWN
                else s.error_message[:_ERROR_PREVIEW_MAX_CHARS]
            )
            lines.append(f"{s.stage:<12} | {label:<32} | {status_text:<14} | {done:<7} | {extra}")
        else:
            lines.append(
                f"{s.stage:<12} | {label:<32} | {status_text:<14} | {done:<7} | "
                f"{s.accuracy * _PERCENT_MULTIPLIER:5.1f}% | {s.d_prime:7.2f} | {s.f1:6.3f} | "
                f"{s.precision * _PERCENT_MULTIPLIER:5.1f}% | {s.recall * _PERCENT_MULTIPLIER:5.1f}% | "
                f"{s.alpha_fpr * _PERCENT_MULTIPLIER:5.1f}%"
            )
    lines.append(_BENCHMARK_DIVIDER_EQ + "\n")
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
