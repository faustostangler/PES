# ADR-068: Hexagonal Decomposition of Judge Calibration (`application/evals`) and JSON Seed SSOT

- **Status:** Accepted
- **Date:** 2026-11-22
- **Deciders:** Principal Socio-Technical Architect (Fausto Stangler / Antigravity)
- **Refines / Supersedes:**
  - Refines `ADR-039` (Progressive LLM-as-a-Judge Calibration Lifecycle)
  - Refines `ADR-061` (Unified Zero-Fallback Judge Calibration CLI)
  - Refines `ADR-062` (Structural Consolidation & JSON Golden Set SSOT — eliminates last Python seed literals)
  - Complements `ADR-010` (Deletes monolithic `calibration_runner.py` with zero legacy shims)

---

## Context

Inspection of `src/cresmo/application/evals/` (1,813 lines across `calibration_runner.py` [1,186L] and `calibration_metrics.py` [548L]) exposed severe cohesion and Hexagonal boundary defects:

1. **Monolithic God File (`calibration_runner.py`, 1,186 lines) Mixed 7 Distinct Responsibilities:**
   - Hardcoded 177 lines of Python seed datasets (`FLUID_PROSE_SEED_DATA`, `GAP_FILLER_SEED_DATA`), violating `ADR-062` JSON SSOT governance.
   - Direct filesystem I/O inside Application (`CalibrationCheckpointStore` using `Path.read_text` / `write_text` / `mkdir` / `os.replace`, `load_stage_dataset`, and `save_calibration_report`).
   - CLI model/stage spec parsing (`resolve_model_spec`, `parse_stage_specs`, `parse_model_specs`).
   - Single-item judge invocation & retry/cooldown policy (`evaluate_single_item`, `run_stage_calibration`) coupled to default `print()`.
   - ASCII 2x2 confusion matrix, slice report, and benchmark table rendering (`_format_matrix_2x2`, `generate_calibration_report`, `print_benchmark_summary`).
   - Multi-stage orchestration (`run_calibration_suite`) with hardcoded verdict thresholds (`0.85` / `0.80`) and Portuguese status literals (`"APROVADO"`, `"REPROVADO"`, `"ERRO"`).

2. **Language & Presentation Leakage in `calibration_metrics.py` (548 lines):**
   - Core confusion matrix fields and verdict counters used Portuguese identifiers (`pedantismo_beta`, `permissivo_alfa`, `rejeicao`, `total_corretos`, `total_defeituosos`, `total_aprovados`, `total_reprovados`), violating workspace English-only engineering standards.
   - `ConfusionMatrix.get_all_metrics()` (226 lines) embedded Google Sheets formulas (`"=B4/B6"`) and UI diagnostic thresholds directly inside the pure Signal Detection Theory math dataclass.

---

## Decision

We split `application/evals/` cleanly along Hexagonal boundaries and standardize 100% of identifiers to English:

### 1. Externalize Calibration Seed Datasets as JSON SSOT (`evals/datasets/seeds/`)
- Move `FLUID_PROSE_SEED_DATA` to `evals/datasets/seeds/fluid_prose_seed.json` and `GAP_FILLER_SEED_DATA` to `evals/datasets/seeds/gap_filler_seed.json`.
- Zero seed dataset literals remain in Python code.

### 2. Application Output Ports (`src/cresmo/application/ports/evals.py`)
- Declare three pure abstract ports:
  - `CalibrationCheckpointPort` (`load_completed_items`, `record_item`, `record_cooldown`, `active_cooldown_until`, `clear_cooldown`)
  - `CalibrationDatasetPort` (`load_items`)
  - `CalibrationReportWriterPort` (`write_report`)
- Provide hermetic in-memory doubles in `tests/doubles/evals_fakes.py` (`ADR-008`).

### 3. Infrastructure Evals Adapters (`src/cresmo/infrastructure/adapters/evals/`)
- `JsonCalibrationCheckpointStore` (`json_checkpoint_store.py`): encapsulates atomic checkpoint & shared cooldown JSON persistence on disk.
- `JsonCalibrationDatasetLoader` (`json_dataset_loader.py`): reads golden JSON datasets and falls back to `evals/datasets/seeds/*_seed.json`.
- `FileCalibrationReportWriter` (`file_report_writer.py`): persists formatted report text to disk cleanly.

### 4. Presentation Formatter (`src/cresmo/presentation/formatters/calibration_report.py`)
- Extract `MetricInfo`, `build_sdt_metric_diagnostics`, `format_confusion_matrix_2x2`, `format_calibration_report`, `format_benchmark_summary`, and `render_calibration_event` out of Application into Presentation.

### 5. Cohesive English-Only Application Evals Modules
- Delete `calibration_runner.py` (`ADR-010`) and replace with:
  - `application/evals/specs.py`: `StageCalibrationSpec`, `CalibrationThresholds`, `CalibrationVerdict(StrEnum)` (`APPROVED`, `PRE-CALIBRATED`, `REJECTED`, `COOLDOWN`, `ERROR`), spec parsers, `sanitize_report_filename`, `compute_config_hash`.
  - `application/evals/executor.py`: `CooldownActiveError(QuotaPoolExhaustedError)`, `CalibrationEvent`, `evaluate_single_item`, `run_stage_calibration` (typed event observer, zero `print()`, zero `Path` I/O).
  - `application/evals/suite.py`: `run_calibration_suite` injecting ports, `CalibrationThresholds`, and optional pure `ReportContentBuilder` callback without depending on Presentation.
- Refactor `calibration_metrics.py` strictly to pure Signal Detection Theory mathematics in English (`hit`, `false_reject_beta`, `false_accept_alpha`, `correct_rejection`, `total_valid`, `total_defective`, `total_approved`, `total_rejected`, `total_samples`).
- Wire `evals/calibrate_judges.py` to compose Infrastructure adapters and Presentation formatters into the pure Application engine.

---

## Banned Anti-Patterns
1. **`*Application Disk I/O Leak*`**: Calling `Path.read_text`, `Path.write_text`, `mkdir`, or `os.replace` directly in `src/cresmo/application/evals/`.
2. **`*Python Seed Literal Duplication*`**: Embedding golden/seed evaluation datasets inside `.py` files instead of `evals/datasets/seeds/*.json`.
3. **`*Portuguese Domain Identifier*`**: Introducing non-English fields, methods, or verdict literals in `src/` or `tests/`.
4. **`*Spreadsheet Formula in Domain/Math*`**: Coupling Google Sheets formulas or terminal ASCII tables into `ConfusionMatrix` or Application runners.

---

## Consequences
- `application/evals/` shrinks from a 1,186-line I/O-coupled runner to four focused, 100% hermetic modules (`calibration_metrics.py`, `specs.py`, `executor.py`, `suite.py`) with zero `print()`, zero filesystem calls, and 0 surviving mutants.
- Presentation formatting and Infrastructure persistence are independently swappable and testable.
