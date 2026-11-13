# ADR-062: Structural Consolidation, JSON Evals SSOT, Bootstrap Separation, and Repository Hygiene

## Status
ACCEPTED

## Date
2026-11-13

## Context
A comprehensive structural audit of the `pes` workspace (`1,827` git-tracked files, multi-gigabyte research sandboxes, and accumulated ADR migrations from ADR-001 through ADR-061) exposed several layers of architectural drift, dual sources of truth, and repository bloat:
1. **Evals Dual Source of Truth & Split Location**: Evaluation assets are split across `tests/evals/` and `scripts/`, while `13` Python data modules (`criterion_*.py`, ~288 KB) store static literal dictionaries compiled by two `builder.py` scripts into `*.json` golden sets consumed by tests and scripts. Additionally, test files import helper logic directly from `scripts/calibrate_judges.py`.
2. **Dormant & Residual Execution Paths**: `TransformFluidProseUseCase` and `FillGapsUseCase` were superseded by `PipelineStageRunner`, and `arq_worker.py` (with `bind_arq_worker_factories`) lacks any Redis container or CLI caller while violating `CresmoSettings` by calling `os.getenv("REDIS_*")`. Meanwhile, planned Bounded Contexts (`identity/`, `shared_kernel/`, Postgres/Polars/Selectolax adapters) and commented `StageRegistry` stages remain deferred for future waves.
3. **Hexagonal Boundary & Bootstrap Mixing**: `src/cresmo/presentation/` hosts both Humble UI/CLI adapters and Dependency Injection composition/factories (`composition.py`, `factories/`), duplicating Langfuse initialization helpers across `composition.py` and `telemetry_factory.py`. Furthermore, `application/services/preflight.py` executes raw network and filesystem I/O (`urllib.request`, `mkdir`, `os.access`, `shutil.which`) directly in Application, `domain/taxonomy.py` embeds mutable editorial channel lists in code, `domain/entities/compendium.py` contains service post-processing logic, and `application/json_parser.py` sits at the root of `application/` outside `services/`.
4. **Residual Shims, Stray Debug Hooks & Config Drift**: Four ADR-010 compatibility shims remain active (`discover_batch_sources.py`, `index_raw_transcripts.py`, `obsidian_vault_adapter.py`, `prompt_provider.py` + `sys.modules` lookup in `json_provider.py`), `coordinator.py` retains a live `breakpoint()` before `StageName.GAP_FILLER`, `gemini_adapter.py`/`ollama_llm_adapter.py`/`seed_prompts.py` read `os.getenv`/`os.environ` directly, and `CresmoSettings` still creates `data/enriched` (`data/fluid`) diverging from ADR-058 (`data/fluid_prose`, `data/gap_filler`).
5. **Runtime Skills, Container, Mutation & Git Bloat**: `.agents/skills/cresmo*/` contains stale sibling `.md` duplicates alongside `SKILL.md` (not copied into the Docker image because `.dockerignore` ignores `.agents/`), `[tool.mutmut] also_copy` and `cresmo_mutation_sweeper.py` mirror `174 MB` of `.agents/`, and git tracks `802` files (`152 MB`) under `mutants/`, `.coverage`, `.vscode/`, `lauro jardim.txt`, and `projects.md`.

## Decision

### 1. Scope Governance: Untouched, Removed, and Deferred Assets
- **Keep Untouched**: `playground/` and `.agents/skills/stangler-doctor/references/` remain completely untouched.
- **Remove Dormant/Residual Modules & Shims**:
  - Delete `src/cresmo/application/use_cases/transform_fluid_prose.py`, `src/cresmo/application/use_cases/fill_gaps.py`, and their obsolete unit tests.
  - Delete `src/cresmo/infrastructure/workers/` (`arq_worker.py`, `bind_arq_worker_factories`, and `test_arq_worker.py`).
  - Delete the four ADR-010 transition shims (`discover_batch_sources.py`, `index_raw_transcripts.py`, `obsidian_vault_adapter.py`, `prompt_provider.py`) and remove the `sys.modules` facade hook in `json_provider.py`.
  - Remove the stray `breakpoint()` in `src/cresmo/application/pipeline/coordinator.py`.
- **Retain Commented/Deferred (`# FUTURE / DEFERRED`)**:
  - Preserve commented future stages in `StageRegistry` (`long_expander`, `wide_expander`, `atomic_inventory`, `atomic_batch`, `reconcile_mocs`) and planned use cases (`IndexRawTranscriptsUseCase` + `use_cases/indexing/`, `ExpandCompendiumUseCase`, `DiscoverAtomicInventoryUseCase`, `SynthesizeAtomicBatchUseCase`, `ReconcileMOCsUseCase`).
  - Preserve Grupo A architectural investments with explicit `# FUTURE / DEFERRED` module markers: `src/identity/`, `src/shared_kernel/`, `PostgresLedgerAdapter`, `database/models.py`, `PolarsBatchProcessor`, `SelectolaxHtmlParser`, and `IamSettings` in `src/config.py`.

### 2. SOTA-KISS Evaluation Consolidation & JSON Golden Set SSOT
- Consolidate `scripts/` and `tests/evals/` into `evals/` (`run_evals.py`, `calibrate_judges.py`, `benchmark_fluid_prose.py`, unified `upload_golden_sets.py`) with datasets in `evals/datasets/` (`EVAL-001.jsonl`, `fluid_prose_golden_set.json`, `gap_filler_golden_set.json`, `samples/`).
- Eliminate the `13` static `criterion_*.py` modules and `2` `builder.py` scripts; `.json` files in `evals/datasets/` are the sole SSOT, validated directly by `pytest` (`test_fluid_prose_golden_set.py`, `test_gap_filler_golden_set.py`).
- Extract reusable calibration engine primitives tested by unit tests (`StageCalibrationSpec`, `ConfusionMatrix`, `CalibrationCheckpointStore`, `CalibrationResultSet`, `run_stage_calibration`, reporting helpers) into `src/cresmo/application/evals/` so `tests/` never imports `evals/` or `scripts/`.
- Relocate generated `.txt` benchmark/judge reports, `profile_run.svg`, and `import.log` into gitignored `reports/`, keeping resumable checkpoints in `data/calibration_checkpoints/`.

### 3. Hexagonal Boundaries, Bootstrap Separation, and Adapter Capability Layout
- **Bootstrap Layer**: Relocate `src/cresmo/presentation/composition.py` and `src/cresmo/presentation/factories/` to `src/cresmo/bootstrap/`, unifying duplicated Langfuse client helpers into one shared helper and leaving `presentation/` strictly as Humble CLI/commands.
- **Pure Application Services**:
  - Introduce `PreflightProbePort` (`src/cresmo/application/ports/preflight.py`) and `PreflightProbeAdapter` (`src/cresmo/infrastructure/adapters/system/preflight_probe_adapter.py`), removing direct `urllib.request`, `mkdir`, `os.access`, and `shutil.which` calls from `application/services/preflight.py`.
  - Move `src/cresmo/application/json_parser.py` to `src/cresmo/application/services/json_parser.py`.
- **Pure Domain Services & Externalized Taxonomy**:
  - Extract `post_process_enriched_compendium` out of `domain/entities/compendium.py` into `domain/services/compendium.py`.
  - Externalize editorial channel lists out of `src/cresmo/domain/taxonomy.py` into `src/cresmo/infrastructure/resources/taxonomy.json` backed by `JsonTaxonomyCatalogAdapter` implementing `ChannelTaxonomyPort` (`application/ports/taxonomy.py`), keeping `domain/taxonomy.py` and `domain/value_objects/sync.py` 100% pure with zero `domain -> infrastructure` dependency.
- **Infrastructure Capability & Persistence Organization**:
  - Group flat adapters under `src/cresmo/infrastructure/adapters/{anonymization,data,judges,llm,media,metrics,obsidian,prompts,scrapers,system,telemetry}/`.
  - Consolidate SQLite & deferred PostgreSQL persistence (`sqlite_ledger_adapter.py`, `models.py`, `postgres_ledger_adapter.py`) under `src/cresmo/infrastructure/persistence/`.
- **Configuration & Settings Alignment**:
  - Align `CresmoSettings` and `DefaultPipelineSettings` defaults with ADR-058 (`fluid_dir -> data/fluid_prose`, `gap_filler_dir -> data/gap_filler`, preserving `enriched_dir` compatibility alias only where required by `concat_master` / adapters) and ensure `ensure_directories()` materializes canonical stage directories.
  - Eliminate remaining direct `os.getenv`/`os.environ` accesses in `gemini_adapter.py`, `ollama_llm_adapter.py`, and `seed_prompts.py` in favor of injected `CresmoSettings`.

### 4. Tests, Tools, Docs, Containers, `.agents/`, and CI Hygiene
- **Tests & Quality Tooling**: Reorganize `tests/cresmo/unit/` into `{domain,application,infrastructure,bootstrap,presentation}/`, rename `test_adr057_*` / `test_adr058_*` to target modules, create `tests/cresmo/integration/`, and relocate `tests/quality/` to `tools/quality/`.
- **Runtime Skills SSOT**: Keep `SKILL.md` as sole markdown definition inside each `.agents/skills/cresmo*/` folder (removing stale sibling `.md` duplicates), untrack `.agents/skills/developing-with-streamlit`, remove/ignore `stangler skill.zip`, un-ignore `!.agents/skills/cresmo*/SKILL.md` in `.dockerignore` and copy runtime skills into `Dockerfile`, and restrict `mutmut` / sweeper copies exclusively to runtime `.agents/skills/cresmo*/SKILL.md`.
- **Docs, Containers & CI**: Retain `CONTEXT.md` at root, modernize `CONTEXT-MAP.md`, move `cresmo_pipeline.md` to `docs/architecture/` and `acl_ingestion_specification.md` to `docs/archive/`, remove tracked root files (`lauro jardim.txt`, `projects.md`) and tracked bloat (`mutants/`, `.coverage`, `.mutmut-cache`, `.vscode/`), parameterize `docker-compose.yml` (`${VAR:-default}` + `env/compose.env.example`), fail explicitly on `ROLE=api` in `docker/entrypoint.sh`, and run full `pytest tests/` + `mypy --strict src/` + `ruff` in `.github/workflows/ci.yml`.

## Consequences
- Zero dual sources of truth for Golden Sets, prompts, and runtime skill instructions.
- Strict compliance with Hexagonal dependency direction (`Domain -> Application -> Infrastructure/Presentation/Bootstrap`) and zero test-to-script imports.
- Lean git index (`mutants/` and `.vscode/` untracked), fast Docker & Mutmut builds, and full CI coverage across all Bounded Contexts.

