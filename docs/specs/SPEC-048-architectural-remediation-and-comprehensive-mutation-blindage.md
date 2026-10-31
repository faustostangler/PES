# SPEC-048: Architectural Remediation and Comprehensive Mutation Blindage

**Status:** ACCEPTED  
**Governing ADR:** [`ADR-048`](../adr/ADR-048-architectural-remediation-and-comprehensive-mutation-blindage.md)  
**Date:** 2026-10-31  
**Domain Layers:** `shared_kernel`, `identity`, `cresmo`

---

## 1. Specification Requirements

### 1.1 Presentation Entrypoint Syntax Blocker (`src/cresmo/presentation/cli.py`)
- Remove stray `exis` at line 105.
- Ensure `main()` handles exceptions and terminates with valid integer exit code.

### 1.2 Infrastructure Worker Decoupling (`src/cresmo/infrastructure/workers/arq_worker.py`)
- `arq_worker.py` MUST NOT import anything from `cresmo.presentation`.
- Move `get_shared_settings()` and `resolve_shared_settings()` into `src/cresmo/infrastructure/config.py`.
- In `src/cresmo/presentation/factories/settings_factory.py`, re-export `get_shared_settings` and `resolve_shared_settings` for backward compatibility.
- Add `_STAGE_RUNNER_FACTORY: Callable[[CresmoSettings], PipelineStageRunner] | None = None` and `register_stage_runner_factory(fn)` to `arq_worker.py`.
- In `job_process_pipeline_stage`, resolve stage runner via `ctx.get("stage_runner")` -> `ctx.get("stage_runner_factory")` -> `_STAGE_RUNNER_FACTORY`. If unresolved, fail-fast with `RuntimeError`.

### 1.3 IAM Personal Access Token Use Cases (`src/identity/application/use_cases/manage_pat.py`)
- Define `ListPersonalAccessTokensUseCase`:
  - Input: `user_id: UserId`
  - Output: `list[PATListItemDTO]` containing token metadata (`id`, `name`, `token_prefix`, `scopes`, `created_at`, `expires_at`, `last_used_at`, `is_active`).
- Define `RevokePersonalAccessTokenUseCase`:
  - Input: `token_id: str`, `user_id: UserId`
  - Output: `bool` (True if token existed and was revoked, False otherwise).
- Update `IdentityContainer` in `src/identity/presentation/dependencies.py` to instantiate and provide these use cases.
- Update `src/identity/presentation/routes.py` `list_personal_access_tokens` and `revoke_personal_access_token` to call use cases instead of accessing `container.pat_repo`.

### 1.4 Shared Kernel Principal Unification (`src/shared_kernel/security.py`, `src/identity/application/dtos.py`)
- `AuthenticatedUser` in `src/shared_kernel/security.py` is the single source of truth for cross-context authorization.
- `AuthenticatedUserDTO` in `src/identity/application/dtos.py` MUST maintain exact compatibility with `AuthenticatedUser`, ensuring `has_role` and `has_scope` follow identical admin override semantics.

### 1.5 Infinite Loop Remediation in Distiller (`src/cresmo/application/use_cases/indexing/distiller.py`)
- Refactor the 3 `while not is_valid:` loops to bounded `for retries in range(max(0, self.max_rewrites) + 1):` loops with early break on `is_valid`.

### 1.6 Mutation Quality Gate Expansion (`tests/quality/`)
- Upgrade `cresmo_mutation_sweeper.py` and `run_mutation_gate.py`:
  - Support contexts `shared_kernel`, `identity`, `cresmo`.
  - Add all 7 unmapped `cresmo` modules (`polars_batch_processor`, `postgres_ledger_adapter`, `gemini_pool`, `criterion_parser`, `selectolax_html_parser`, `database/models.py`, `arq_worker.py`).
  - Add all 9 omitted modules to wave definitions.
  - Map all 18 unmapped test suites.
  - Delete `run_parser.py.meta`.
  - Replace static `0.05s` test duration seed with safe dynamic CPU timeout floor (min 5.0s per test).

---

## 2. Test Plan & Acceptance Criteria

1. **Architectural Sanitization:**
   - Unit tests verify `arq_worker` executes stage jobs with injected runner without importing presentation.
   - Unit tests verify `ListPersonalAccessTokensUseCase` and `RevokePersonalAccessTokenUseCase`.
   - Unit tests verify `AuthenticatedUser` and `AuthenticatedUserDTO` permission semantics.
2. **Quality Gate Verification:**
   - `pytest` 100% passing across entire test suite.
   - `ruff check src/ tests/` 0 violations.
   - `mypy --strict src/ tests/` 0 violations.
   - `run_mutation_gate.py` passes all configured wave thresholds.
