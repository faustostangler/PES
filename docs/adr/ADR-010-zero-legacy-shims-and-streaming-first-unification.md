# ADR-010: Zero Legacy Shims and Streaming-First Unification Principle

**Status:** APPROVED  
**Date:** 2026-09-17  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Supersedes:** ADR-009 Section 2.3 (Dual Interface)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context

During architectural transitions (such as introducing streaming producer-consumer concurrency in [ADR-009](ADR-009-streaming-batch-source-discovery-producer-consumer.md)), an anti-pattern commonly occurs: preserving deprecated interfaces, boolean dispatch flags (`stream=True/False`), and wrapper functions (`load_batch_sources_stream`) solely to avoid updating existing callers or test assertions.

### The Problem: Accidental Complexity & Dual Codepaths
1. **False Equivalence:** Exposing both `execute() -> list[BatchSource]` and `execute_stream() -> Iterator[BatchSource]` gives the false impression that two independent discovery engines exist, when `execute()` was merely an artificial `list(execute_stream())` wrapper.
2. **Interface Bloat in Presentation Layer:** Functions like `load_batch_sources(..., stream=False)` and `load_batch_sources_stream(...)` duplicate signatures and require developers to track arbitrary boolean flags.
3. **Cognitive Debt:** Deferring complete refactorings in the name of "backward compatibility" leaves transitional residue throughout domain and presentation layers, violating the KISS principle and Clean Architecture.

---

## 2. Decision

We establish two binding architectural rules for the PES / Cresmo ecosystem:

### 2.1 The Principle of Zero Legacy Shims (Uncompromising Complete Refactoring)
* **Zero Compatibility Shims:** Production code within bounded contexts must **never** retain deprecated methods, dual codepaths, or boolean mode toggles solely to avoid refactoring caller code or unit test suites.
* **Complete End-to-End Refactoring:** Whenever a superior architectural pattern is adopted (e.g., Streaming Producer-Consumer over Batch Materialization), all callers, presentation commands, and test suites must be updated simultaneously in the same atomic change.
* **Explicit Materialization:** If a caller requires a materialized collection (e.g., `--dry-run` computing total items upfront, or unit tests asserting collection length), the **caller is responsible** for explicitly executing `list(stream)`. The application use case remains purely streaming.

### 2.2 Streaming-First Discovery Unification
1. **`DiscoverBatchSourcesUseCase.execute` as Canonical Streaming Method:**
   - Signature: `def execute(self, query: BatchDiscoveryQuery | None = None) -> Iterator[BatchSource]:`
   - Yields fast-path priority items immediately and yields crawled channel items concurrently via background worker.
   - The redundant `execute_stream` method is **eliminated**.
2. **Presentation Layer Simplification (`src/cresmo/presentation/commands/run.py`):**
   - `load_batch_sources(query, settings=None, media_ingestion_port=None) -> Iterator[BatchSource]` is the single entry point.
   - The `stream: bool` parameter is **eliminated**.
   - The redundant helper `load_batch_sources_stream` is **eliminated**.
   - `execute_batch_dry_run` explicitly materializes via `sources = list(load_batch_sources(...))`.
   - `execute_batch_run` consumes the streaming iterator directly.

---

## 3. Verification & Test Coverage

1. **Use Case Tests:** All tests in `tests/cresmo/unit/test_discover_batch_sources.py` exercise `use_case.execute()`, wrapping with `list(...)` only where list-indexing or `len()` assertions are explicitly evaluated.
2. **CLI & Command Tests:** `tests/cresmo/unit/test_cli.py` tests invoke `load_batch_sources(...)` without boolean stream flags.
3. **Code Quality Gates:** 100% typing conformity via Mypy, Zero lint issues via Ruff, and 100% test pass rate across all unit tests.

---

## 4. Consequences & Impact

### Positive
1. **Single Source of Truth (SSOT):** One unified discovery interface across domain, application, presentation, and tests.
2. **Reduced Cognitive Load:** Developers and operators interact with a single, predictable streaming model.
3. **Adherence to Clean Code & KISS:** Eliminates shim wrappers, boolean flag bifurcation, and dead compatibility code.
4. **Architectural Precedent:** Mandates complete refactorings for future domain evolutions instead of accumulating transitional debt.

### Negative / Trade-offs
- Callers requiring deterministic upfront counts must explicitly invoke `list()` to drain the generator.
