"""Application-layer evaluation metrics, checkpointing, and calibration runner.

Contains pure, testable Signal Detection Theory metrics, atomic JSON checkpointing,
and stage-agnostic LLM Judge calibration orchestration decoupled from CLI adapters.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-062: Structural Consolidation & Bootstrap Separation
"""

from __future__ import annotations

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    ConfusionMatrix,
    ItemEvaluationResult,
    MetricInfo,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.calibration_runner import (
    DEFAULT_CHECKPOINT_DIR,
    DEFAULT_DATASETS_DIR,
    DEFAULT_REPORTS_DIR,
    FLUID_PROSE_SEED_DATA,
    GAP_FILLER_SEED_DATA,
    STAGE_SPECS,
    CalibrationCheckpointStore,
    CooldownActiveError,
    JudgeCalibrationFactory,
    PromptTemplateLookup,
    StageCalibrationSpec,
    build_stage_specs,
    compute_config_hash,
    evaluate_single_item,
    generate_calibration_report,
    load_stage_dataset,
    parse_model_specs,
    parse_stage_specs,
    print_benchmark_summary,
    resolve_model_spec,
    run_calibration_suite,
    run_stage_calibration,
    sanitize_report_filename,
    save_calibration_report,
)

__all__ = [
    "DEFAULT_CHECKPOINT_DIR",
    "DEFAULT_DATASETS_DIR",
    "DEFAULT_REPORTS_DIR",
    "FLUID_PROSE_SEED_DATA",
    "GAP_FILLER_SEED_DATA",
    "STAGE_SPECS",
    "CalibrationCheckpointStore",
    "CalibrationResultSet",
    "CalibrationSuiteOutcome",
    "ConfusionMatrix",
    "CooldownActiveError",
    "ItemEvaluationResult",
    "JudgeCalibrationFactory",
    "MetricInfo",
    "ModelBenchmarkSummary",
    "PromptTemplateLookup",
    "StageCalibrationSpec",
    "build_stage_specs",
    "compute_config_hash",
    "evaluate_single_item",
    "generate_calibration_report",
    "load_stage_dataset",
    "parse_model_specs",
    "parse_stage_specs",
    "print_benchmark_summary",
    "resolve_model_spec",
    "run_calibration_suite",
    "run_stage_calibration",
    "sanitize_report_filename",
    "save_calibration_report",
]
