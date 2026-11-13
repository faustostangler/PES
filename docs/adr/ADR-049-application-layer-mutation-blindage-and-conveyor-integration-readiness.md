# ADR-049: Application Layer Mutation Blindage (>=99.0%) and Conveyor Integration Readiness

**Status:** ACCEPTED  
**Date:** 2026-10-31  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-002`](ADR-002-cresmo-presentation-cli.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-048`](ADR-048-architectural-remediation-and-comprehensive-mutation-blindage.md)

---

## 1. Context & Architectural Motivation

Following the successful execution of ADR-048, which achieved 100.0% mutation blindage (0 survivors, 0 timeouts) across the Sacred Domain and verified 100% module completeness, the Application layer currently exhibits an 88.35% kill rate (4,930 killed / 5,580 total mutants, with 632 survivors and 18 timeouts across 10 functional modules).

The Lead Architect has directed:
1. Elevate Application layer mutation kill rate to **>= 99.0%** (reducing unkilled mutants from 650 down to <= 55 across the entire layer).
2. Prepare the codebase for immediate, clean merge into `main`, which will subsequently receive the merge from the `2026-10-17-cresmo-conveyor` branch.

### 1.1 Root Causes of Application Layer Mutation Survival
1. **Coarse-Grained Integration Test Mapping:**
   `MODULE_TEST_MAP` currently maps multiple granular application modules to high-level orchestration tests (`test_discover_batch_sources.py`, `test_index_raw_transcripts_use_case.py`). Subtle boundary conditions, default arguments, and fallback branches in lower-level use case helpers are exercised without exact value assertions.
2. **Defensive Invariant Testing Gaps:**
   - `src/cresmo/application/use_cases/indexing/validators.py` (113 survivors): Dictionary key validation, schema sanity checks, and type guards lack explicit boundary mutation tests.
   - `src/cresmo/application/use_cases/discovery/models.py` (66 survivors): `BatchSource` post-initialization invariants lack granular value assertions.
   - `src/cresmo/application/use_cases/discovery/lake_scanner.py` (153 survivors): `_matches_video_entry` prefix/suffix and slug-matching logic lacks edge-case coverage.
   - `src/cresmo/application/use_cases/indexing/distiller.py` (189 unkilled, including 18 timeouts): Prompt formatting, retry loop indices, and error fallback branches need targeted test harnesses.
   - `src/cresmo/application/use_cases/discovery/channel_crawler.py` (55 survivors) & `manifests.py` (36 survivors): Crawler state machines and markdown frontmatter extractors lack isolated failure injection.
   - `src/identity/application/use_cases/register_user.py` (6 survivors) & `manage_pat.py` (4 survivors): Default token prefix and entity field assignments need exact matching.
   - `src/cresmo/application/json_parser.py` (3 survivors): Balanced closing brace edge cases.

---

## 2. Decision

We establish an aggressive four-wave TDD surgery to elevate Application layer kill rate to >= 99.0%:

### 2.1 Wave A: Indexing Subsystem Hardening (`validators.py` & `distiller.py`)
- Implement dedicated unit test suites `tests/cresmo/unit/test_indexing_validators.py` and enhance `tests/cresmo/unit/test_index_raw_transcripts_use_case.py`.
- Cover all negative validation branches in `is_valid_raw_index_output`.
- Eliminate `extract_summary` and `extract_concepts` timeout mutants by testing bounded retries with deterministic mocks.

### 2.2 Wave B: Discovery Subsystem Hardening (`models.py`, `lake_scanner.py`, `channel_crawler.py`, `manifests.py`, `discover_batch_sources.py`)
- Implement `tests/cresmo/unit/test_discovery_models.py` for `BatchSource` and `TranscriptManifest` invariants.
- Implement `tests/cresmo/unit/test_lake_scanner.py` covering all regex, slug, and video entry pattern matching branches.
- Implement `tests/cresmo/unit/test_channel_crawler.py` and `tests/cresmo/unit/test_discovery_manifests.py`.

### 2.3 Wave C: Remaining IAM & Core Application Module Hardening
- Eliminate the 6 survivors in `register_user.py`, 4 survivors in `manage_pat.py`, and 3 survivors in `json_parser.py`.

### 2.4 Wave D: Gate Enforcement & Main Branch Merge
- Run `run_mutation_gate.py --enforce-domain --enforce-application --min-app-rate 99.0 --verify-completeness`.
- Verify full test suite (all green), Ruff, and Mypy strict.
- Execute merge into `main` cleanly with fast-forward or non-conflicting merge commit.

---

## 3. Consequences

### Positive
- Application layer achieves >= 99.0% mutation kill rate, guaranteeing exceptional reliability of business orchestrators.
- Eliminates brittle tests and replaces coarse end-to-end assertions with fast, isolated unit specifications.
- Clean integration path for subsequent merge with `2026-10-17-cresmo-conveyor`.

### Negative / Trade-offs
- Generation of detailed mutation profiles requires substantial CPU cycles during sweeper runs.
