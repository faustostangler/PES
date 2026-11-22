# ADR-067: Humble Presentation CLI and Run/Sync Use Cases

- **Status:** Accepted
- **Date:** 2026-11-22
- **Deciders:** Principal Socio-Technical Architect (Fausto Stangler / Antigravity)
- **Refines / Supersedes:**
  - Refines `ADR-002` (Humble Object CLI Boundary Enforcement)
  - Refines `ADR-010` (Zero Legacy Shims & Streaming-First Unification — eliminates superseded `commands/run.py` helpers)
  - Refines `ADR-053` (Purges deprecated `--no-crawl` flag once default-fast behavior stabilized)
  - Refines `ADR-026` (Clean Code Governance — removes Presentation `args: Any` and duplicated exception ladders)

---

## Context

Static and runtime audit of `src/cresmo/presentation/commands/` revealed severe Hexagonal Architecture violations and accumulated CLI debt:

1. **`run.py` (697 lines) Violated Humble Object & Dependency Rule (`ADR-001` / `ADR-002`):**
   - Directly imported `opentelemetry.trace`, `CredentialPoolExhaustedError` (`infrastructure/adapters/llm/gemini_pool.py`), `CresmoSettings` (`infrastructure/config`), `get_process_rss_bytes` (`infrastructure/system`), and `gc`.
   - Performed **in-place mutation** of Pydantic settings (`settings.days_lookback = args.lookback`) instead of immutable derivation via `model_copy(update=...)`.
   - Contained business orchestration: preflight sequencing, conditional warmup, single-video vs batch dispatch, dry-run inspection, fail-fast quota cooldown abortion (`ADR-041`), post-batch RAG master consolidation, and per-item telemetry draining + GC + Prometheus metrics emission.
   - Wrapped CLI arguments in an untyped dynamic inner `class _Args` with `args: Any` signatures.

2. **`sync.py` (389 lines) Performed Domain Discovery I/O in Presentation:**
   - Directly invoked `settings.ensure_directories()` and implemented private filesystem parsing `_read_manifest_lines()` duplicating `application/use_cases/discovery/manifests.py::read_manifest_lines`.
   - Mixed channel URL coercion, category filtering (`ChannelTaxonomyPort`), alphabetical sorting (`ADR-012`), and exit code exception ladders inside `handle_sync`.

3. **Duplicated Exception Ladders & `check_config` Infrastructure Leak:**
   - The exact 6-branch exception-to-exit-code block was copy-pasted across `run()`, `handle_run()`, and `handle_sync()`.
   - `check_config.py` imported `CresmoSettings` directly from `cresmo.infrastructure.config`.

4. **Dead / Destructive CLI Flags Across 8 Subcommands (12 Dead Flag Occurrences):**
   - `run`: `--all`, `--device`, `--concurrency`, `--verbose` / `-v` silently ignored (`_ = (...)`); `--no-crawl` kept only as deprecated no-op.
   - `sync`, `check-config`, `concat-master`, `export-cookies`, `seed-prompts`, `worker`: `--verbose` / `-v` silently discarded.
   - `dedupe --dry-run`: **destructive dead flag** — accepted `--dry-run`, printed `"Dry-run mode: True"`, and executed `use_case.execute()` mutating the Obsidian vault regardless.

---

## Decision

We enforce strict Hexagonal isolation across Presentation, Application, Domain, and Bootstrap:

### 1. Domain Quota Exhaustion Boundary & Process Runtime Port
- Introduce `QuotaPoolExhaustedError(RateLimitExceededError)` in `src/cresmo/domain/exceptions.py` carrying `retry_after_seconds: float`.
- Update `CredentialPoolExhaustedError` (`gemini_pool.py`) to subclass `(QuotaPoolExhaustedError, RuntimeError)` so Application use cases catch only the Domain exception (`QuotaPoolExhaustedError`) without importing from `infrastructure`.
- Introduce `ProcessRuntimePort(ABC)` and `NoOpProcessRuntimePort` in `src/cresmo/application/ports/runtime.py`, implemented by `SystemProcessRuntimeAdapter` in `src/cresmo/infrastructure/adapters/system/process_runtime_adapter.py`, abstracting `gc.collect()`, `get_process_rss_bytes()`, and file size inspection (`Path.stat().st_size`) out of pure Application logic.

### 2. Application Orchestration Extraction (`RunSynthesisUseCase` & `SyncBatchUseCase`)
- Extract all `run` orchestration into `src/cresmo/application/use_cases/run_synthesis.py`:
  - Frozen request/outcome/event DTOs (`RunSynthesisRequest`, `RunSynthesisOutcome`, `BatchItemEvent`, `BatchItemEventKind`, `RunExitStatus`).
  - Fail-fast `PreflightHealthChecker.check_all().assert_healthy()` **before** invoking `pipeline_factory()` so invalid configuration or missing binaries never construct SDK clients or SQLite connections.
  - Typed observer callback (`on_event: Callable[[BatchItemEvent], None]`) decoupled from `sys.stdout`/`sys.stderr`.
  - Per-item `finally:` cleanup executing telemetry flush, `runtime_port.collect_garbage()`, and `Process` RSS/GC Prometheus metrics via `metrics_port`.
- Extract all `sync` orchestration into `src/cresmo/application/use_cases/sync_batch.py`:
  - Frozen DTOs (`SyncBatchRequest`, `SyncBatchOutcome`, `SyncTargetEvent`, `SyncTargetEventKind`).
  - Reuses canonical `read_manifest_lines` (`discovery/manifests.py`) and enforces `ADR-012` case-insensitive alphabetical ordering.
  - Removes redundant outer OpenTelemetry `"cresmo.cli"` wrapper span (`CresmoPipeline` owns canonical `cresmo.pipeline` session traces per `ADR-065`).

### 3. Immutable Fresh Settings Derivation & Directory Setup in Bootstrap
- Add `load_fresh_settings(overrides: dict[str, Any] | None = None)` in `bootstrap/factories/settings_factory.py` creating a fresh `CresmoSettings()` instance with immutable `model_copy(update=overrides)` overrides (replacing in-place mutation and removing `CresmoSettings` imports from `run.py` and `check_config.py`).
- Add `build_run_synthesis_use_case(...)`, `build_sync_batch_use_case(...)`, and `build_process_runtime_adapter()` in `bootstrap/`, moving `ensure_runtime_directories(settings)` for `sync` into `build_sync_batch_use_case`.

### 4. Unified CLI Error Handler & Purge of All 12 Dead CLI Flags (`ADR-010`)
- Create `src/cresmo/presentation/error_handler.py` centralizing `map_exception_to_exit_code`, `format_cli_error`, and `handle_cli_exception`.
- Refactor `run.py` (~150 lines) and `sync.py` (~130 lines) to pure typed Humble Objects accepting `RunSynthesisRequest` and `SyncBatchRequest`.
- Remove legacy Presentation exports (`execute_batch_dry_run`, `execute_batch_run`, `execute_single_video_run`, `load_batch_sources`, `_Args`) per `ADR-010`.
- Purge all dead flags:
  - `run`: remove `--all`, `--device`, `--concurrency`, `--verbose`/`-v`, `--no-crawl`.
  - `sync`, `check-config`, `concat-master`, `export-cookies`, `seed-prompts`, `worker`: remove `--verbose`/`-v`.
  - `dedupe`: remove destructive `--dry-run` (retain live `--verbose`/`-v`).

---

## Banned Anti-Patterns
1. **`*Fat CLI Orchestrator*`**: Placing batch loops, quota break policies, manifest loading, or RAG consolidation inside `presentation/commands/`.
2. **`*Presentation-to-Infrastructure Leak*`**: Importing `cresmo.infrastructure.*` or SDK clients (`opentelemetry.trace`, `gc`) inside `run.py`, `sync.py`, or `check_config.py`.
3. **`*In-Place Settings Mutation*`**: Mutating Pydantic settings fields (`settings.days_lookback = ...`) instead of passing overrides to `load_fresh_settings`.
4. **`*Dead CLI Flag*`**: Declaring Typer options that are ignored (`_ = ...`) or perform destructive mutations despite no-op flags (`dedupe --dry-run`).
5. **`*Duplicated Exit-Code Try/Except*`**: Repeating multi-exception mappings outside `presentation/error_handler.py`.

---

## Consequences
- `presentation/commands/run.py`, `sync.py`, and `check_config.py` pass strict AST import-purity checks with zero `cresmo.infrastructure`, `opentelemetry`, or `gc` imports.
- All orchestration logic becomes 100% hermetic and mutation-testable inside `application/use_cases/{run_synthesis,sync_batch}.py` with 0 surviving mutants.
- Invoking any removed dead CLI flag fails fast with non-zero usage exit status instead of silently misbehaving.
