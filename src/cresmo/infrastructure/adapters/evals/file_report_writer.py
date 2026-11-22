"""Filesystem report writer adapter implementing CalibrationReportWriterPort.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.ports.evals import CalibrationReportWriterPort


class FileCalibrationReportWriter(CalibrationReportWriterPort):
    """Write formatted calibration reports cleanly to UTF-8 text files."""

    def write_report(self, output_path: Path, content: str) -> Path:
        """Create parent directories and persist rendered calibration report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        return output_path
