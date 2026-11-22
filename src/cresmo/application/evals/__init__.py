"""Application-layer pure evaluation models, specifications, executor, and suite orchestrator.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    CalibrationVerdict,
    ConfusionMatrix,
    ItemEvaluationResult,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.executor import (
    CalibrationEvent,
    CalibrationEventKind,
    CooldownActiveError,
    JudgeCalibrationFactory,
    evaluate_single_item,
    extract_cooldown_seconds,
    is_transient_retryable_error,
    run_stage_calibration,
)
from cresmo.application.evals.specs import (
    DEFAULT_CHECKPOINT_DIR,
    DEFAULT_DATASETS_DIR,
    DEFAULT_REPORTS_DIR,
    DEFAULT_SEEDS_DIR,
    STAGE_SPECS,
    CalibrationThresholds,
    PromptTemplateLookup,
    StageCalibrationSpec,
    build_stage_specs,
    classify_verdict,
    compute_config_hash,
    parse_model_specs,
    parse_stage_specs,
    resolve_model_spec,
    sanitize_report_filename,
)
from cresmo.application.evals.suite import (
    ReportContentBuilder,
    run_calibration_suite,
)

__all__ = [
    "DEFAULT_CHECKPOINT_DIR",
    "DEFAULT_DATASETS_DIR",
    "DEFAULT_REPORTS_DIR",
    "DEFAULT_SEEDS_DIR",
    "STAGE_SPECS",
    "CalibrationEvent",
    "CalibrationEventKind",
    "CalibrationResultSet",
    "CalibrationSuiteOutcome",
    "CalibrationThresholds",
    "CalibrationVerdict",
    "ConfusionMatrix",
    "CooldownActiveError",
    "ItemEvaluationResult",
    "JudgeCalibrationFactory",
    "ModelBenchmarkSummary",
    "PromptTemplateLookup",
    "ReportContentBuilder",
    "StageCalibrationSpec",
    "build_stage_specs",
    "classify_verdict",
    "compute_config_hash",
    "evaluate_single_item",
    "extract_cooldown_seconds",
    "is_transient_retryable_error",
    "parse_model_specs",
    "parse_stage_specs",
    "resolve_model_spec",
    "run_calibration_suite",
    "run_stage_calibration",
    "sanitize_report_filename",
]
