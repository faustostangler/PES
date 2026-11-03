# SPEC-049: Application Layer Mutation Blindage (>=99.0%) Specification

**Status:** ACCEPTED  
**Governing ADR:** [`ADR-049`](../adr/ADR-049-application-layer-mutation-blindage-and-conveyor-integration-readiness.md)  
**Target:** Application Layer Mutation Kill Rate >= 99.0% (Unkilled mutants <= 55 out of 5,580 total)

---

## 1. Scope & Modules to Harden

| Module | Current Total | Current Killed | Current Survivors | Timeouts | Target Kill Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cresmo/application/use_cases/indexing/validators.py` | 183 | 70 | 113 | 0 | >= 99.0% |
| `cresmo/application/use_cases/discovery/models.py` | 130 | 64 | 66 | 0 | >= 99.0% |
| `cresmo/application/use_cases/discovery/lake_scanner.py` | 331 | 178 | 153 | 0 | >= 99.0% |
| `cresmo/application/use_cases/indexing/distiller.py` | 368 | 179 | 171 | 18 | >= 98.0% |
| `cresmo/application/use_cases/discovery/channel_crawler.py` | 179 | 124 | 55 | 0 | >= 99.0% |
| `cresmo/application/use_cases/discovery/manifests.py` | 118 | 82 | 36 | 0 | >= 99.0% |
| `cresmo/application/use_cases/discovery/discover_batch_sources.py` | 256 | 231 | 25 | 0 | >= 99.0% |
| `identity/application/use_cases/register_user.py` | 49 | 43 | 6 | 0 | 100.0% |
| `identity/application/use_cases/manage_pat.py` | 122 | 118 | 4 | 0 | 100.0% |
| `cresmo/application/json_parser.py` | 119 | 116 | 3 | 0 | 100.0% |

---

## 2. Test Plan & Wave Sequencing

### Wave A: Indexing Subsystem
1. `tests/cresmo/unit/test_indexing_validators.py`:
   - Test every validation check in `is_valid_raw_index_output`: missing required keys (`title`, `slug`, `summary`, `concepts`), invalid types, empty strings, invalid concept structure.
2. `tests/cresmo/unit/test_index_raw_transcripts_use_case.py` / `test_distiller.py`:
   - Test `LLMTranscriptDistiller` retry boundaries, fallback prompt handling, summary extraction, and concept extraction.

### Wave B: Discovery Subsystem
1. `tests/cresmo/unit/test_discovery_models.py`:
   - Invariants of `BatchSource`, `TranscriptManifest`, path resolution.
2. `tests/cresmo/unit/test_lake_scanner.py`:
   - Unit tests for `_matches_video_entry`, pattern matching, slug comparison, prefix/suffix stripping.
3. `tests/cresmo/unit/test_channel_crawler.py` & `test_discovery_manifests.py`:
   - Crawling retry backoff, remote channel mapping, frontmatter parser edge cases.

### Wave C: IAM & Application Primitives
1. `tests/identity/unit/test_use_cases.py`:
   - Kill remaining 6 mutants in `register_user.py` and 4 mutants in `manage_pat.py`.
2. `tests/cresmo/unit/test_json_parser.py`:
   - Kill remaining 3 mutants in `_find_balanced_closing_brace`.

### Wave D: Gate & Git Integration
1. Update `run_mutation_gate.py` with `--min-app-rate 99.0`.
2. Verify:
   - Pytest global: 0 failures.
   - Ruff & Mypy: 0 errors.
   - Mutation gate: PASS.
3. Checkout `main` and merge `scan_pes_source`.
