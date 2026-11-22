"""Presentation formatter utilities package for Cresmo CLI and report rendering."""

from __future__ import annotations

from cresmo.presentation.formatters.calibration_report import (
    MetricInfo,
    build_sdt_metric_diagnostics,
    format_benchmark_summary,
    format_calibration_report,
    format_confusion_matrix_2x2,
    render_calibration_event,
)

__all__ = [
    "MetricInfo",
    "build_sdt_metric_diagnostics",
    "format_benchmark_summary",
    "format_calibration_report",
    "format_confusion_matrix_2x2",
    "render_calibration_event",
]
