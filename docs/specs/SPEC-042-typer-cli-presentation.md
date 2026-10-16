# SPEC-042: Modern Typer Presentation CLI Specifications

**Status:** PROPOSED  
**Date:** 2026-10-13  
**Originating ADR:** [`docs/adr/ADR-042-typer-presentation-cli.md`](../adr/ADR-042-typer-presentation-cli.md)  
**Governing Method:** Doctor Stangler Architecture Method (TDD Red-Green-Refactor, Hexagonal/Clean Architecture, Fail-Fast)  
**Bounded Context:** Cresmo Knowledge Synthesis — Presentation Layer  

---

## 1. Domain & Presentation Invariants

1. **Root CLI Application (`cresmo.presentation.cli:app`):**
   - Must be an instance of `typer.Typer(no_args_is_help=True)`.
   - Running `cresmo` with no arguments prints the help message and exits with status code `2` (or `0` when `--help` is supplied).
   - All 8 subcommands must be registered directly: `run`, `check-config`, `sync`, `worker`, `dedupe`, `export-cookies`, `concat-master`, `seed-prompts`.
   - Eliminates implicit `argv` routing to `run`.
2. **Subcommand Contracts & Strong Typing:**
   - **`run`**:
     - Optional `--url` (`str | None`, defaults to None).
     - `--all` (`bool`, flag, defaults to True).
     - Optional `--manifest / --playlist` (`Path | None`, `exists=True`, `resolve_path=True`).
     - `--passes` (`int`, `min=1`, `max=10`, defaults to 3).
     - Optional `--batch-size` (`int | None`, `min=1`).
     - Optional `--lookback` (`int | None`, `min=0`).
     - `--dry-run` (`bool`, flag, defaults to False).
     - Optional `--channel` (`str | None`).
     - Optional `--category` (`str | None`).
     - Optional `--video` (`str | None`).
     - Optional `--device` (`str | None`, choices: `auto`, `cuda`, `cpu`, `mps`).
     - Optional `--concurrency` (`int | None`, `min=1`).
     - `--verbose / -v` (`bool`, flag, defaults to False).
   - **`check-config`**:
     - `--verbose / -v` (`bool`, flag, defaults to False).
     - Validates environment settings, directories, and preflight health fail-fast.
   - **`sync`**:
     - Optional `--channel` (`str | None`).
     - Optional `--category` (`str | None`).
     - Optional `--video` (`str | None`).
     - Optional `--playlist` (`Path | None`, `exists=True`, `resolve_path=True`).
     - Optional `--lookback` (`int | None`, `min=0`).
     - `--dry-run` (`bool`, flag, defaults to False).
     - `--no-filter` (`bool`, flag, defaults to False).
   - **`worker`**:
     - `--channel` (`str`, required option/argument).
     - `--poll-interval` (`int`, `min=10`, defaults to 300).
     - `--lookback` (`int`, `min=0`, defaults to 7).
     - Optional `--concurrency` (`int`, `min=1`, defaults to 1).
   - **`dedupe`**:
     - Optional `--vault` (`Path | None`, `dir_okay=True`, `resolve_path=True`).
     - `--dry-run` (`bool`, flag, defaults to False).
   - **`export-cookies`**:
     - `--browser` (`str`, defaults to "chrome").
     - Optional `--output` (`Path | None`, `resolve_path=True`).
   - **`concat-master`**:
     - Optional `--source-dir` (`Path | None`, `dir_okay=True`, `resolve_path=True`).
     - Optional `--output-file` (`Path | None`, `resolve_path=True`).
     - Optional `--channel` (`str | None`).
   - **`seed-prompts`**:
     - Optional `--vault` (`Path | None`, `dir_okay=True`, `resolve_path=True`).
     - `--force` (`bool`, flag, defaults to False).
3. **Exit Code Taxonomy Conformance:**
   - Exit codes must strictly conform to `src/cresmo/presentation/exit_codes.py`:
     - `EXIT_SUCCESS = 0`
     - `EXIT_INTERNAL_ERROR = 1`
     - `EXIT_CONFIG_OR_USAGE_ERROR = 2`
     - `EXIT_DOMAIN_VALIDATION_ERROR = 3`
     - `EXIT_RATE_LIMIT_EXCEEDED = 4`
     - `EXIT_INGESTION_ERROR = 5`
   - Exceptions caught in command handlers must be printed to `stderr` and re-raised via `raise typer.Exit(code=EXIT_*)`.

---

## 2. Test Specifications (Refractometry - Phase 2)

All tests must run hermetically using `typer.testing.CliRunner(mix_stderr=False)`.

### Test Suite 1: Root CLI & Dynamic Subcommand Registration (`tests/cresmo/unit/test_cli.py`)
- `test_root_cli_help_displays_all_subcommands`:
  - Run `runner.invoke(app, ["--help"])`.
  - Assert `result.exit_code == 0`.
  - Assert stdout contains `'run'`, `'sync'`, `'worker'`, `'check-config'`, `'dedupe'`, `'export-cookies'`, `'concat-master'`, `'seed-prompts'`.
- `test_root_cli_no_args_displays_help_and_exits`:
  - Run `runner.invoke(app, [])`.
  - Assert `result.exit_code in (0, 2)` and help message is rendered.
- `test_invalid_subcommand_returns_exit_config_or_usage_error`:
  - Run `runner.invoke(app, ["nonexistent-command"])`.
  - Assert `result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR` (code 2).

### Test Suite 2: Command Validation & Boundaries
- `test_run_command_validates_passes_boundary`:
  - Run `runner.invoke(app, ["run", "--passes", "0"])` (below min=1).
  - Assert `result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR` (code 2).
  - Run `runner.invoke(app, ["run", "--passes", "15"])` (above max=10).
  - Assert `result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR` (code 2).
- `test_run_command_validates_nonexistent_manifest_file`:
  - Run `runner.invoke(app, ["run", "--manifest", "/nonexistent/manifest.txt"])`.
  - Assert `result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR` (code 2) due to `exists=True`.

### Test Suite 3: Exception-to-Exit Code Mapping
- `test_run_command_maps_rate_limit_exceeded_to_exit_code_4`:
  - Mock `build_pipeline` raising `RateLimitExceededError`.
  - Run `runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])`.
  - Assert `result.exit_code == EXIT_RATE_LIMIT_EXCEEDED` (code 4).
- `test_run_command_maps_ingestion_error_to_exit_code_5`:
  - Mock pipeline raising `IngestionNetworkError`.
  - Run `runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])`.
  - Assert `result.exit_code == EXIT_INGESTION_ERROR` (code 5).
- `test_run_command_maps_domain_validation_error_to_exit_code_3`:
  - Mock pipeline raising `DomainValidationError`.
  - Run `runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])`.
  - Assert `result.exit_code == EXIT_DOMAIN_VALIDATION_ERROR` (code 3).
- `test_run_command_maps_preflight_error_to_exit_code_2`:
  - Mock preflight checker raising `PreflightError`.
  - Run `runner.invoke(app, ["run", "--url", "https://youtube.com/watch?v=123"])`.
  - Assert `result.exit_code == EXIT_CONFIG_OR_USAGE_ERROR` (code 2).

### Test Suite 4: Value Object Translation & Use Case Dispatch
- `test_run_command_translates_channel_option_to_channel_name_vo`:
  - Mock `build_pipeline` and `load_batch_sources`.
  - Run `runner.invoke(app, ["run", "--channel", "Spotniks", "--dry-run"])`.
  - Assert `BatchDiscoveryQuery` received `channel_name=ChannelName("Spotniks")`.
