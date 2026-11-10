# ADR-055: Comprehensive Presentation CLI Lazy Dispatching, Zero-Read Lake Scanning, and Deferred Adapter Initialization

## Status
ACCEPTED

## Context
Running `cresmo run` or debugging through VS Code / Antigravity IDE (F5) encounters severe multi-stage startup latency on developer workstations when the repository and virtual environment reside on mechanical storage (`/dev/sda1` 5400 RPM SATA HDD, NTFS via FUSE):

1. **Presentation CLI Eager Cascading:**
   `src/cresmo/presentation/cli.py` statically imports all 8 command modules (`check_config`, `run`, `worker`, `sync`, etc.) and registers them on `app.command()`. This forces PEP 562 resolution of every command module at CLI launch, loading `cresmo.application.pipeline`, `native_media_ingestion_adapter` (`yt_dlp`), and `composition.py`.
2. **Module-Level Composition Side-Effects:**
   `src/cresmo/presentation/composition.py` executes `from cresmo.infrastructure.workers.arq_worker import ...` at the global module level, eagerly loading `arq` and `redis` (~9.2s).
3. **Synchronous Adapter Construction Overhead:**
   - `SqliteLedgerAdapter.__init__` executes synchronous connection, WAL PRAGMA configuration, and table/index DDL against disk on instantiation.
   - `JsonPromptProvider.__init__` crawls parent directories for `.git` and parses `prompts.json` synchronously.
   - `judge_factory.py` statically imports all judge providers (`gemini`, `ollama`, `typesafe`, `composite`) at module top-level.
   - `NativeMediaIngestionAdapter` statically imports `yt_dlp` at top-level.
   - `src/cresmo/presentation/commands/run.py:287` executes redundant `settings.ensure_directories()` right before `build_pipeline()` executes it again.
4. **Eager Lake Scanning & Full-File Frontmatter Reads (34.05s bottleneck at loop entry):**
   When `enumerate(sources, 1)` yields its first item at `run.py:443`, `DiscoverBatchSourcesUseCase._collect_fast_path_sources()` runs `LakeScannerService.scan_raw_lake()` unconditionally—even when `--scan-raw` is False and crawler is disabled.
   `scan_raw_lake()` opens and parses YAML frontmatter for 1,071 markdown files in `data/raw/` line-by-line (`extract_raw_file_metadata`), causing 1,071 mechanical disk seeks and freezing the CLI for over 34 seconds.

---

## Decision

### 1. Presentation CLI Lazy Dispatcher (`src/cresmo/presentation/cli.py`)
- Replace eager imports of command functions with a custom Click `LazyGroup` / Typer command dispatcher.
- Commands are registered with lightweight metadata and callbacks that defer `importlib.import_module("cresmo.presentation.commands.<cmd>")` until the specific subcommand is invoked by Click/Typer.
- Importing `cresmo.presentation.cli` will not import `cresmo.application.pipeline`, `composition.py`, `redis`, `arq`, or `yt_dlp`.

### 2. Isolate Worker Registration Side-Effects (`src/cresmo/presentation/composition.py`)
- Encapsulate `register_stage_runner_factory`, `register_media_ingestion_factory`, and `register_sync_channel_factory` inside `bind_arq_worker_factories()`.
- Remove top-level `import arq_worker`. Trigger binding only when starting the worker daemon in `worker.py`.

### 3. Zero-Read Metadata Extraction & Conditional Lake Scan (`src/cresmo/application/use_cases/discovery/`)
- In `discover_batch_sources.py`: skip `LakeScannerService.scan_raw_lake()` entirely when `q.scan_raw` is False and `q.enable_channel_crawler` is False.
- In `lake_scanner.py`: implement Zero-Read Metadata Extraction. Derive `canonical_vid` from `rf.stem` and `channel_name` from `rf.parent.name` without opening or reading the 1,071 `.md` files.

### 4. Deferred Adapter Initialization
- `SqliteLedgerAdapter`: Defer `_init_db()` to the first call of `_get_connection()`.
- `JsonPromptProvider`: Defer catalog loading to `get_prompt()` / `catalog` property access.
- `NativeMediaIngestionAdapter`: Defer `import yt_dlp` to operational download/extraction methods.
- `judge_factory.py`: Load only the judge adapter matching `settings.judge_provider`.
- `run.py`: Remove redundant `settings.ensure_directories()` at line 287.

### 5. VS Code Debugger Bytecode Cache Redirection (`.vscode/launch.json`)
- Add `"PYTHONPYCACHEPREFIX": "/home/stangler/.cache/pycache"` to launch profiles to divert Python `.pyc` caching to NVMe ext4.

---

## Consequences

### Positive
- Initial CLI load time drops from ~125s to <0.2s.
- `cresmo run` loop entry (`run.py:443`) delay drops from ~34s to <50ms.
- 0 bytes of disk read for metadata extraction across 1,071 lake files during discovery.
- `arq`, `redis`, `yt_dlp`, and unused LLM judge SDKs are never loaded when running `run` or lightweight subcommands.

### Negative / Trade-offs
- First call to SQLite ledger or prompt provider will incur initialization cost on demand during execution rather than at application bootstrap.

