# SPEC-062: Structural Consolidation, Evals SSOT, Bootstrap Separation, and Repository Hygiene

**Conforms to:** [`ADR-062`](../adr/ADR-062-structural-consolidation-evals-ssot-and-bootstrap-separation.md)  
**Status:** APPROVED  
**Date:** 2026-11-13  

---

## 1. Specification Overview

Defines exact file-system targets, module moves, interface contracts (`PreflightProbePort`, `ChannelTaxonomyPort`), SSOT schemas (`evals/datasets/`, `taxonomy.json`), container/CI configurations, and verification gates for consolidating the `pes` repository.

---

## 2. Removed, Retained (# FUTURE), and Untouched Scope

### 2.1 Strictly Untouched
- `playground/**` (no file moves, lint fixes, or deletions)
- `.agents/skills/stangler-doctor/references/**`

### 2.2 Removed Dormant Modules & Shims
- `src/cresmo/application/use_cases/transform_fluid_prose.py` (+ `TransformFluidProseUseCase` export & legacy test cases in `test_use_cases.py`)
- `src/cresmo/application/use_cases/fill_gaps.py` (+ `FillGapsUseCase` export & legacy test cases in `test_use_cases.py`)
- `src/cresmo/infrastructure/workers/` (`arq_worker.py`, `__init__.py`, `bind_arq_worker_factories`, and `test_arq_worker.py`)
- ADR-010 transition shims:
  - `src/cresmo/application/use_cases/discover_batch_sources.py`
  - `src/cresmo/application/use_cases/index_raw_transcripts.py`
  - `src/cresmo/infrastructure/adapters/obsidian_vault_adapter.py`
  - `src/cresmo/infrastructure/adapters/prompt_provider.py` (and `sys.modules.get("cresmo.infrastructure.adapters.prompt_provider")` fallback in `json_provider.py`)
- Stray debug hook: `breakpoint()` inside `src/cresmo/application/pipeline/coordinator.py`

### 2.3 Preserved with `# FUTURE / DEFERRED` Markers
- Commented future stages in `src/cresmo/domain/stage_registry.py` (`long_expander`, `wide_expander`, `atomic_inventory`, `atomic_batch`, `reconcile_mocs`)
- Deferred/future Use Cases: `IndexRawTranscriptsUseCase` + `use_cases/indexing/`, `ExpandCompendiumUseCase`, `DiscoverAtomicInventoryUseCase`, `SynthesizeAtomicBatchUseCase`, `ReconcileMOCsUseCase`
- Deferred Bounded Contexts & Adapters: `src/identity/`, `src/shared_kernel/`, `PostgresLedgerAdapter`, `persistence/models.py`, `PolarsBatchProcessor`, `SelectolaxHtmlParser`, `IamSettings` in `src/config.py`

---

## 3. Evals Consolidation & Application Engine (`evals/` & `src/cresmo/application/evals/`)

1. Delete `scripts/fluid_prose/llm_judge/{criterion_*.py, builder.py}` (`6` data modules + compiler) and `scripts/gap_filler/llm_judge/{criterion_*.py, builder.py}` (`7` data modules + compiler).
2. Store Golden Sets & samples strictly as JSON/JSONL/Markdown SSOT under `evals/datasets/`:
   - `evals/datasets/EVAL-001.jsonl`
   - `evals/datasets/fluid_prose_golden_set.json`
   - `evals/datasets/gap_filler_golden_set.json`
   - `evals/datasets/samples/`
3. Place runnable evaluation CLIs in `evals/`:
   - `evals/run_evals.py`
   - `evals/calibrate_judges.py`
   - `evals/benchmark_fluid_prose.py`
   - `evals/upload_golden_sets.py` (unified uploader replacing separate fluid_prose & gap_filler `upload_to_langfuse.py` scripts)
4. Extract pure/testable calibration domain & orchestration logic (`StageCalibrationSpec`, `MetricInfo`, `ConfusionMatrix`, `CalibrationResultSet`, `ItemEvaluationResult`, `ModelBenchmarkSummary`, `CalibrationCheckpointStore`, `resolve_model_spec`, `parse_stage_specs`, `parse_model_specs`, `compute_config_hash`, `load_stage_dataset`, `evaluate_single_item`, `run_stage_calibration`, `generate_calibration_report`, `save_calibration_report`) into `src/cresmo/application/evals/`.
5. Relocate the `13` `.txt` report files (`llm_generator_*.txt`, `llm_judge_*.txt`), `profile_run.svg`, and `import.log` into gitignored `reports/`.

---

## 4. `src/` Internal Layering & Port Contracts

### 4.1 Bootstrap Separation (`src/cresmo/bootstrap/`)
- Move `src/cresmo/presentation/composition.py` and `src/cresmo/presentation/factories/*` -> `src/cresmo/bootstrap/`.
- Extract single Langfuse client construction helper shared between `composition.py` and `telemetry_factory.py`.
- `src/cresmo/presentation/commands/` and CLI modules import from `cresmo.bootstrap`.

### 4.2 Pure Application Preflight & Services
- Define `PreflightProbePort` in `src/cresmo/application/ports/preflight.py`:
  - `check_http_endpoint(url: str, timeout: float = 3.0) -> bool`
  - `ensure_directory_writable(directory: Path) -> bool`
  - `has_executable(name: str) -> bool`
- Implement `PreflightProbeAdapter` in `src/cresmo/infrastructure/adapters/system/preflight_probe_adapter.py`.
- Refactor `src/cresmo/application/services/preflight.py` to accept `PreflightProbePort` (zero direct `urllib`, `os.access`, `mkdir`, or `shutil.which` imports).
- Move `src/cresmo/application/json_parser.py` -> `src/cresmo/application/services/json_parser.py`.

### 4.3 Domain Services & Externalized Channel Taxonomy
- Move `post_process_enriched_compendium` from `src/cresmo/domain/entities/compendium.py` to `src/cresmo/domain/services/compendium.py`.
- Externalize channel name & alias catalog (`GENERALIST_CHANNELS`, `INVESTIGATIVE_CHANNELS`, alias mappings) into `src/cresmo/infrastructure/resources/taxonomy.json`.
- Keep pure classification types/matching logic in `src/cresmo/domain/taxonomy.py`, define `ChannelTaxonomyPort` in `src/cresmo/application/ports/taxonomy.py` and `JsonTaxonomyCatalogAdapter` in `src/cresmo/infrastructure/adapters/prompts/taxonomy_catalog.py` (or `resources`), with `SyncFilterCriteria` accepting pure injected/catalog mappings without importing infrastructure.

### 4.4 Infrastructure Capability & Persistence Layout
- `src/cresmo/infrastructure/adapters/`:
  - `anonymization/anonymizer_adapter.py`
  - `data/polars_batch_processor.py` (`# FUTURE / DEFERRED`)
  - `judges/` (`composite_judge.py`, `criterion_parser.py`, `gemini_judge.py`, `langfuse_decorator.py`, `ollama_judge.py`, `preflight_decorator.py`, `typesafe_judge.py`)
  - `llm/` (`gemini_adapter.py`, `gemini_pool.py`, `ollama_critique_adapter.py`, `ollama_llm_adapter.py`)
  - `media/` (`cookie_extractor.py`, `feed.py`, `header_generator.py`, `native_media_ingestion_adapter.py`, `subtitles.py`)
  - `metrics/` (`noop_metrics_adapter.py`, `prometheus_metrics_adapter.py`)
  - `obsidian/` (`adapter.py`, `catalog.py`, `mocs.py`, `notes.py`, `transcripts.py`, `utils.py`)
  - `prompts/` (`builders.py`, `catalog.py`, `json_provider.py`, `langfuse_provider.py`, `taxonomy_catalog.py`)
  - `scrapers/` (`selectolax_html_parser.py` — `# FUTURE / DEFERRED`)
  - `system/` (`preflight_probe_adapter.py`)
  - `telemetry/` (`noop.py`, `opentelemetry_adapter.py`, `thread_naming.py`)
- `src/cresmo/infrastructure/persistence/`:
  - `sqlite_ledger_adapter.py`
  - `models.py` (`# FUTURE / DEFERRED`)
  - `postgres_ledger_adapter.py` (`# FUTURE / DEFERRED`)

### 4.5 Settings & Env Consolidation
- Align `CresmoSettings` & `DefaultPipelineSettings` with ADR-058: `fluid_dir = data_dir / "fluid_prose"`, `gap_filler_dir = data_dir / "gap_filler"`, `ensure_directories()` creates canonical stage directories.
- Route environment reads in `gemini_adapter.py`, `ollama_llm_adapter.py`, and `seed_prompts.py` strictly through `CresmoSettings`.

---

## 5. Tests, Tools, Docs, `.agents/`, Docker, & CI

1. Reorganize `tests/cresmo/unit/` into `domain/`, `application/`, `infrastructure/`, `bootstrap/`, and `presentation/`, rename `test_adr057_*` / `test_adr058_*` to target modules, and create `tests/cresmo/integration/`.
2. Move `tests/quality/` -> `tools/quality/`, updating `cresmo_mutation_sweeper.py` target maps and `pyproject.toml` `[tool.mutmut] also_copy` to copy only `.env` and runtime `.agents/skills/cresmo*/SKILL.md`.
3. Remove stale sibling `.md` duplicates inside `.agents/skills/cresmo*/`, untrack `.agents/skills/developing-with-streamlit`, remove/ignore `stangler skill.zip`.
4. Update `.dockerignore` (`!.agents/skills/cresmo*/SKILL.md`, ignore `mutants/`, `docs/`, `evals/`, `tools/`, `reports/`) and copy runtime `SKILL.md` files in `Dockerfile`.
5. Parameterize `docker-compose.yml` via `${VAR:-default}` + provide `env/compose.env.example`; fail fast in `docker/entrypoint.sh` when `ROLE=api`.
6. Untrack `mutants/`, `.coverage`, `.mutmut-cache`, `.vscode/`; remove tracked `lauro jardim.txt` & `projects.md`; move `cresmo_pipeline.md` -> `docs/architecture/` and `acl_ingestion_specification.md` -> `docs/archive/`; modernize `CONTEXT-MAP.md`.
7. Update `.github/workflows/ci.yml` to run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy --strict src/`, and `uv run pytest tests/ -v`.

---

## 6. Verification Acceptance Criteria

- `uv run ruff check .` exits `0`
- `uv run ruff format --check .` exits `0`
- `uv run mypy --strict src/` exits `0`
- `uv run pytest tests/ -v` passes with zero errors/regressions
- `uv run cresmo --help` and `uv run python evals/run_evals.py --help` execute cleanly
- Mutation testing gate on refactored domain/application modules yields `0` surviving mutants

