# SPEC-047: Discovery Lake I/O Optimization and On-Demand Lake Scanning Specifications

**Status:** ACCEPTED  
**Governing ADR:** [`ADR-047`](../adr/ADR-047-discovery-lake-io-optimization-and-lazy-scan.md)  
**Date:** 2026-10-25  
**Domain Layer:** `cresmo.application.use_cases.discovery`, `cresmo.presentation.commands`

---

## 1. Specification Requirements

### 1.1 In-Memory Absolute Path Resolution (`lake_scanner.py`)
- In `LakeScannerService.collect_priority_texts`:
  - `pf.resolve()` MUST be replaced by `pf.absolute()`.
- In `LakeScannerService.scan_raw_lake`:
  - `rf.resolve()` MUST be replaced by `rf.absolute()`.
- Return types and semantics of `acc.add_source` remain strictly identical (`str(path.absolute())`).

### 1.2 Streaming YAML Frontmatter Parser (`manifests.py`)
- `extract_raw_file_metadata(path: Path) -> dict[str, str]`:
  - MUST open `path` using buffered line streaming (`with path.open("r", encoding="utf-8") as f:`).
  - First line MUST be checked for `---`. If absent, return empty metadata immediately.
  - Process subsequent lines until the closing `---` line is encountered or max limit (50 lines) is reached.
  - Parse `key: value` pairs from frontmatter lines, stripping whitespace and matching previous output schema.
  - Catch `(OSError, UnicodeDecodeError)` and return `{}` on corrupt or inaccessible files.

### 1.3 On-Demand Lake Scan CLI Flag (`commands/run.py`)
- `run` subcommand options:
  - Remove `--no-scan-raw`.
  - Add `--scan-raw`: `Annotated[bool, typer.Option("--scan-raw", help="Scan local raw transcript lake for unprocessed files (default: False)")] = False`.
- In `_build_batch_discovery_query(args, settings)`:
  - `scan_raw = getattr(args, "scan_raw", False)`.
- Help text and error handling conform to ADR-042 and Typer specifications.

---

## 2. Test Plan & Acceptance Criteria

1. **Unit Tests (`test_discover_batch_sources.py`):**
   - Verify `extract_raw_file_metadata` parses standard YAML frontmatter, ignores body content, and stops scanning at closing `---`.
   - Verify `LakeScannerService` registers sources with valid absolute paths.
2. **CLI Presentation Tests (`test_cli.py`, `test_run_command.py`):**
   - Verify `cresmo run` defaults to `scan_raw=False`.
   - Verify passing `--scan-raw` sets `scan_raw=True`.
3. **Verification Command:**
   - `pytest tests/cresmo/unit/test_discover_batch_sources.py tests/cresmo/unit/test_cli.py tests/cresmo/unit/test_run_command.py`
   - `ruff check src/ tests/`
   - `mypy --strict src/cresmo/application/use_cases/discovery/ src/cresmo/presentation/commands/run.py`
