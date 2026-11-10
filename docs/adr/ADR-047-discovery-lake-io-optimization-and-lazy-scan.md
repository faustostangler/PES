# ADR-047: Discovery Lake I/O Optimization and On-Demand Lake Scanning

**Status:** ACCEPTED  
**Date:** 2026-10-25  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md), [`CONTEXT.md`](../../CONTEXT.md)  
**Related ADRs:** [`ADR-002`](ADR-002-cresmo-presentation-cli.md), [`ADR-009`](ADR-009-streaming-batch-source-discovery-producer-consumer.md), [`ADR-012`](ADR-012-multi-criteria-sync-filtering-and-alphabetical-feed-ordering.md), [`ADR-042`](ADR-042-typer-presentation-cli.md)

---

## 1. Context & Architectural Motivation

Empirical profiling via `py-spy top` during `cresmo run --no-crawl --dry-run` against a real-world repository state with 1,071 raw transcript files in `data/raw/` revealed severe I/O bottlenecks in the batch discovery phase prior to pipeline execution:

1. **Massive Symlink Resolution Latency (`posixpath.realpath` - 15.53s):**
   `LakeScannerService` invokes `Path.resolve()` for every discovered transcript file across priority files and lake files (`lake_scanner.py:112` and `lake_scanner.py:212`). On Linux, `resolve()` performs synchronous `stat()` and symlink inspection syscalls across all path components. With 1,071 files, this single operation consumes over 15 seconds of execution time.
2. **Whole-File Disk Read Latency & Memory Pressure (`manifests.py:54` - 6.64s):**
   `extract_raw_file_metadata()` calls `path.read_text(encoding="utf-8")` to parse YAML frontmatter. This reads entire multi-megabyte raw transcript bodies into memory, only to inspect the first ~20 lines for `---` delimited metadata (`video_id`, `channel`).
3. **Eager Lake Scanning Default Anti-Pattern (`commands/run.py`):**
   The CLI `run` subcommand defaults to eager disk lake scanning (`scan_raw = not args.no_scan_raw = True`). In typical day-to-day runs targeting single videos or manifest playlists, scanning 1,070+ lake files is unnecessary and adds significant latency.

---

## 2. Decision

We implement three targeted, non-breaking performance optimizations across the discovery domain and presentation CLI:

### 2.1 Pure In-Memory Path Resolution (`src/cresmo/application/use_cases/discovery/lake_scanner.py`)
Replace `pf.resolve()` and `rf.resolve()` with `pf.absolute()` and `rf.absolute()`.
`Path.absolute()` produces a normalized absolute path string without making physical filesystem syscalls to resolve symlinks, reducing path resolution time from ~15.5s to under 2ms.

### 2.2 Streaming Frontmatter Extraction (`src/cresmo/application/use_cases/discovery/manifests.py`)
Refactor `extract_raw_file_metadata(path: Path)` to use a buffered stream (`with path.open("r", encoding="utf-8") as f:`).
The parser reads line-by-line and terminates immediately upon encountering the closing frontmatter delimiter (`---`) or a safe line limit (e.g. 50 lines). This avoids loading full transcript bodies into RAM and drastically cuts file read latency.

### 2.3 On-Demand Lake Scanning Inversion (`src/cresmo/presentation/commands/run.py`)
Invert the default behavior of lake scanning in the `cresmo run` CLI command:
- Deprecate `--no-scan-raw` and introduce `--scan-raw` with default `False`.
- By default, batch discovery processes only prioritized targets (explicit URL, `--manifest` playlist, and priority texts), skipping the recursive lake walk.
- When `--scan-raw` is explicitly supplied, lake scanning is performed on-demand.
- Update `test_cli.py` and `test_run_command.py` to assert the inverted flag semantics.

---

## 3. Consequences

### Positive
- Discovery startup time drops from >22s to <500ms for default CLI invocations.
- Zero memory spikes from reading 1,000+ full markdown files into RAM simultaneously.
- Ergonomic CLI defaults: fast execution for explicit URLs and manifest playlists without lake overhead.

### Negative / Trade-offs
- Users wishing to discover and backfill all unprocessed raw lake files must explicitly pass `--scan-raw`.

---

## 4. Compliance & Verification
- **SPEC:** `docs/specs/SPEC-047-discovery-lake-io-optimization-and-lazy-scan.md`
- **Tests:** Unit tests in `tests/cresmo/unit/test_discover_batch_sources.py`, `tests/cresmo/unit/test_cli.py`, and `tests/cresmo/unit/test_run_command.py`.
