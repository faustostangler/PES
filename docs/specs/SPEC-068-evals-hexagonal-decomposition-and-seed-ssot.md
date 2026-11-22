# SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT

- **Related ADR:** [ADR-068](../adr/ADR-068-evals-hexagonal-decomposition-and-seed-ssot.md)
- **Status:** Accepted
- **Date:** 2026-11-22

---

## 1. JSON Seed SSOT (`evals/datasets/seeds/`)

- `evals/datasets/seeds/fluid_prose_seed.json`: 5 canonical items migrated verbatim from legacy `FLUID_PROSE_SEED_DATA`.
- `evals/datasets/seeds/gap_filler_seed.json`: 2 canonical items migrated verbatim from legacy `GAP_FILLER_SEED_DATA`.

---

## 2. Application Output Ports (`src/cresmo/application/ports/evals.py`)

### 2.1 `CalibrationCheckpointPort(ABC)`
- `load_completed_items(self, stage: str, provider: str, model: str, config_hash: str) -> dict[str, dict[str, Any]]`
- `record_item(self, stage: str, provider: str, model: str, config_hash: str, item_id: str, payload: dict[str, Any]) -> None`
- `record_cooldown(self, stage: str, provider: str, model: str, until_ts: float) -> None`
- `active_cooldown_until(self, stage: str, provider: str, model: str, now: float | None = None) -> float | None`
- `clear_cooldown(self, stage: str, provider: str, model: str) -> None`

### 2.2 `CalibrationDatasetPort(ABC)`
- `load_items(self, stage_name: str, default_golden_set_path: Path, default_seed_path: Path, *, dataset_path: Path | None = None, seed_only: bool = False) -> list[dict[str, Any]]`

### 2.3 `CalibrationReportWriterPort(ABC)`
- `write_report(self, output_path: Path, content: str) -> Path`

---

## 3. Pure English SDT Metrics (`src/cresmo/application/evals/calibration_metrics.py`)

### 3.1 `ConfusionMatrix`
- Fields: `hit`, `false_reject_beta`, `false_accept_alpha`, `correct_rejection`, `invalid`.
- Properties: `tp`, `fn`, `fp`, `tn`, `total_valid` (`hit + false_reject_beta`), `total_defective` (`false_accept_alpha + correct_rejection`), `total_approved` (`hit + false_accept_alpha`), `total_rejected` (`false_reject_beta + correct_rejection`), `total_samples` (`hit + false_reject_beta + false_accept_alpha + correct_rejection`), `accuracy`, `precision`, `recall`, `specificity`, `npv`, `alpha_fpr`, `beta_fnr`, `f05`, `f1`, `f2`, `lr_plus`, `lr_minus`, `mcc`, `d_prime`, `c_bias`.
- `record(expected, actual)` returns `"INVALID"`, `"HIT"`, `"CORRECT_REJECTION"`, `"FALSE_ACCEPT_ALPHA"`, or `"FALSE_REJECT_BETA"`.

### 3.2 `CalibrationVerdict(StrEnum)`
- Members: `APPROVED = "APPROVED"`, `PRE_CALIBRATED = "PRE-CALIBRATED"`, `REJECTED = "REJECTED"`, `COOLDOWN = "COOLDOWN"`, `ERROR = "ERROR"`.
- `ModelBenchmarkSummary.status` uses `CalibrationVerdict`.

---

## 4. Application Evals Modules (`src/cresmo/application/evals/`)

1. **`specs.py`**: `StageCalibrationSpec` (carries `default_seed_path: Path` instead of Python seed literals), `CalibrationThresholds` (`approved_min_accuracy=0.85`, `approved_max_false_accept=0`, `pre_calibrated_min_accuracy=0.80`), `build_stage_specs`, `resolve_model_spec`, `parse_stage_specs`, `parse_model_specs`, `sanitize_report_filename`, `compute_config_hash`.
2. **`executor.py`**: `CooldownActiveError(QuotaPoolExhaustedError)`, `CalibrationEventKind`, `CalibrationEvent`, `evaluate_single_item`, `extract_cooldown_seconds`, `is_transient_retryable_error`, `run_stage_calibration` (emits typed events via `on_event`; zero `print`).
3. **`suite.py`**: `ReportContentBuilder`, `run_calibration_suite` requiring injected `checkpoint_store`, `dataset_loader`, `report_writer`, parameterized `thresholds`, and emitting `CalibrationEvent`.

---

## 5. Infrastructure Adapters & Presentation Formatter

- `src/cresmo/infrastructure/adapters/evals/`: `JsonCalibrationCheckpointStore`, `JsonCalibrationDatasetLoader`, `FileCalibrationReportWriter`.
- `src/cresmo/presentation/formatters/calibration_report.py`: `MetricInfo`, `build_sdt_metric_diagnostics`, `format_confusion_matrix_2x2`, `format_calibration_report`, `format_benchmark_summary`, `render_calibration_event`.
- AST purity invariant: `src/cresmo/application/evals/` must contain zero `print(` calls, zero `os.replace`, zero `Path.read_text` / `write_text` / `mkdir`, and zero imports from `cresmo.infrastructure` or `cresmo.presentation`.
