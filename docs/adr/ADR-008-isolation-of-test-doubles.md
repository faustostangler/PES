# ADR-008: Isolation of Test Doubles to `tests/doubles/` and Production Code Purity

**Status:** ACCEPTED  
**Date:** 2026-09-16  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, `<RULE[user_global]>`)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context

In [`src/cresmo/infrastructure/adapters/mock_adapters.py`](../../src/cresmo/infrastructure/adapters/mock_adapters.py), the codebase maintained in-memory mock adapters (`MockMediaIngestionPort`, `MockLLMTransformationPort`, `MockVaultRepositoryPort`, `MockLedgerRepositoryPort`) implementing the application ports.

### The Problem
1. **Production Code Pollution**: Test doubles and spies were located directly in `src/cresmo/infrastructure/adapters/`, violating the separation between production code and test scaffolding.
2. **Mutation Testing Distortion**: Mutation testing tooling (`mutmut run`) analyzes the entire `src/` directory tree. It generated **146 AST mutants** on mock adapters that are never executed in production, distorting real infrastructure quality metrics and slowing down CI/CD test mutation cycles.
3. **Hexagonal Purity**: Test doubles are test fixtures, not production infrastructure adapters. Production infrastructure should only contain real adapters interacting with system I/O (`ObsidianVaultAdapter`, `SqliteLedgerAdapter`, `GeminiLLMAdapter`, `NativeMediaIngestionAdapter`).

---

## 2. Decision

We extract and relocate all in-memory mock adapters from `src/cresmo/infrastructure/adapters/mock_adapters.py` into a dedicated test doubles module in `tests/doubles/mock_adapters.py`:

1. **New Test Double Location**: `tests/doubles/mock_adapters.py`.
2. **Import Updates**: Update test suites (`tests/cresmo/unit/test_use_cases.py`, `tests/cresmo/unit/test_unify_duplicates.py`, `tests/cresmo/unit/test_pipeline.py`, `tests/cresmo/unit/test_mock_adapters.py`) to import from `tests.doubles.mock_adapters`.
3. **Decommissioning**: Remove `src/cresmo/infrastructure/adapters/mock_adapters.py` from the production codebase.
4. **Mutmut Quality Gate**: Mutation testing on `src/cresmo/` now measures 100% genuine production code.

---

## 3. Consequences

### Positive
- **Zero Test Scaffolding in Production**: `src/` contains solely production-grade code.
- **Accurate Mutation Metrics**: Mutation scores for `Infrastructure` now reflect real adapter resilience without 146 artificial mock mutants.
- **Faster Test & Mutation Cycles**: Eliminates execution of mutation runs against mock code.

### Negative / Trade-offs
- Tests that import `mock_adapters` must reference `tests.doubles.mock_adapters`. No production code imported them, so there is zero impact on production runtime.

---

## 4. Alternatives Considered

1. **Keep `mock_adapters.py` in `src/` and filter mutmut configs**:
   - *Rejected*: Adds complex exception rules in `pyproject.toml` and leaves dead/test-only code in production deployable artifacts.
2. **Inline Mocks using `unittest.mock.MagicMock` in every test**:
   - *Rejected*: Reusable in-memory adapters with state tracking provide superior readability and hermetic testing over repetitious mock boilerplate across use cases.
