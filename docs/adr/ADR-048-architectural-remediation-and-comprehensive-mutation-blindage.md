# ADR-048: Architectural Remediation and Comprehensive Mutation Blindage

**Status:** ACCEPTED  
**Date:** 2026-10-31  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-002`](ADR-002-cresmo-presentation-cli.md), [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-018`](ADR-018-identity-and-access-management-bounded-context-and-sveltekit-bff.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-030`](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md)

---

## 1. Context & Architectural Motivation

An exhaustive static and mutation analysis across `src/`, `tests/`, and `mutants/src/` revealed two categories of technical debt: critical Hexagonal Architecture boundary leaks and severe blind spots in the automated mutation testing quality gate.

### 1.1 Hexagonal Layering & Dependency Inversion Violations
1. **Infrastructure -> Presentation Leakage (`arq_worker.py`):**
   `src/cresmo/infrastructure/workers/arq_worker.py` directly imports `build_stage_runner` and `resolve_shared_settings` from `cresmo.presentation.composition`. Infrastructure components must never depend on the presentation layer. Settings resolution belongs to configuration infrastructure, and worker task runners must receive domain stage executors via Dependency Injection or registration hooks.
2. **Presentation Direct Repository Access (`identity/presentation/routes.py`):**
   Endpoints `GET /tokens` and `DELETE /tokens/{token_id}` access `container.pat_repo` directly, bypassing the Application Use Case layer. This breaks the Hexagonal invariant that Presentation exclusively invokes Application Use Cases.
3. **Duplicated Security Principal Contract:**
   `src/identity/application/dtos.py` defines `AuthenticatedUserDTO` with identical methods and attributes (`has_role`, `has_scope`) as `AuthenticatedUser` in `src/shared_kernel/security.py`, violating DRY and cross-context cohesion in the Shared Kernel.
4. **Active P0 Syntax Blocker on HEAD:**
   `src/cresmo/presentation/cli.py:105` contains stray characters (`exis        res = app(...)`) causing an `IndentationError` when loading the CLI entrypoint.

### 1.2 Mutation Sweeper & Gate Blind Spots
1. **Multi-Context Blindness:** `run_mutation_gate.py` only validates `mutants/src/cresmo`, leaving `src/identity` (15 modules) and `src/shared_kernel` completely unverified.
2. **Omitted Modules & Test Drift:** 7 active `cresmo` modules lack `.meta` files, 9 modules in `MODULE_TEST_MAP` are omitted from execution waves, 18 existing test suites are unmapped, and an orphaned `run_parser.py.meta` remains after CLI refactoring.
3. **False SIGXCPU (-24) Timeouts:** `cresmo_mutation_sweeper.py` seeds test durations with `0.05s`, causing `mutmut` process pool workers to enforce overly restrictive CPU limits on judge and LLM adapter tests.
4. **Infinite Loops on Mutation in `distiller.py`:** Unbounded `while not is_valid:` loops in `distiller.py` spin indefinitely when retry increments or break statements are mutated.

---

## 2. Decision

We implement a prioritized, two-stage remediation:

### 2.1 Stage 1: Hexagonal Architectural Sanitization
1. **P0 Fix:** Remove `exis` in `src/cresmo/presentation/cli.py` and enforce hermetic CLI runner error handling.
2. **Decouple Infrastructure Worker:**
   - Relocate `get_shared_settings` and `resolve_shared_settings` to `src/cresmo/infrastructure/config.py`.
   - Maintain backward compatibility by re-exporting them from `src/cresmo/presentation/factories/settings_factory.py`.
   - Provide `register_stage_runner_factory` hook in `src/cresmo/infrastructure/workers/arq_worker.py` to allow Composition Root to inject stage runners without infrastructure importing presentation.
3. **IAM PAT Application Layer Completion:**
   - Create `ListPersonalAccessTokensUseCase` and `RevokePersonalAccessTokenUseCase` in `src/identity/application/use_cases/manage_pat.py`.
   - Update `src/identity/presentation/routes.py` and `IdentityContainer` to route all PAT queries and revocations through these use cases.
4. **Shared Kernel Principal Unification:**
   - Refactor `AuthenticatedUserDTO` in `src/identity/application/dtos.py` to inherit from or map cleanly to `shared_kernel.security.AuthenticatedUser`.

### 2.2 Stage 2: Comprehensive Multi-Wave Mutation Hardening
- **Wave 0 (Tooling & Baseline):** Upgrade `cresmo_mutation_sweeper.py` and `run_mutation_gate.py` to support `identity`, `shared_kernel`, and all `cresmo` modules; remove `run_parser.py.meta`; replace fake duration seeds with safe adaptive CPU floors.
- **Wave 1 (Domain & Shared Kernel 100%):** Hermetic unit tests achieving **100% kill rate (0 survivors)** across `shared_kernel`, `identity.domain`, and `cresmo.domain`.
- **Wave 2 (Identity Context):** Unit/integration coverage achieving **0 survivors** in `identity.domain`/`application` and **< 5%** in `identity.infrastructure`.
- **Wave 3 (Cresmo Application):** Replace unbounded `while` loops in `distiller.py` with bounded iterations; add unit suites for `indexing/*`, `discovery/*`, and `json_parser.py` achieving **0 survivors and 0 timeouts**.
- **Wave 4 (Cresmo Infrastructure):** Cover unmapped infrastructure modules (`models.py`, `arq_worker.py`, `catalog.py`, `utils.py`, `judges/*`, `prompts/*`) achieving **>= 95.0% kill rate**.
- **Wave 5 (Presentation & Pre-Commit Audit):** Add presentation factory tests; verify full suite with `pytest`, `run_mutation_gate.py --enforce-all`, `ruff`, and `mypy --strict`.

---

## 3. Consequences

### Positive
- Strict compliance with Clean and Hexagonal Architecture: zero reverse dependencies (`Infrastructure -> Presentation`) and zero bypassed application layers.
- Full mutation test coverage across the entire codebase (`shared_kernel`, `identity`, `cresmo`), raising global kill rate from 78.5% to >= 95.0% (100% in domain/application).
- Eradication of false timeouts and infinite loop regressions.

### Negative / Trade-offs
- Execution requires sequential wave testing and AST re-generation for modules with drift.

---

## 4. Compliance & Verification
- **SPEC:** `docs/specs/SPEC-048-architectural-remediation-and-comprehensive-mutation-blindage.md`
- **Quality Gate:** `tests/quality/run_mutation_gate.py --enforce-all` must exit with code 0.
