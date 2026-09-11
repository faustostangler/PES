# SPEC-003: Channel Synchronization, SQLite WAL Ledger & Preflight Governance

**Linked ADR:** [`ADR-003: PES Production Architecture — Consolidated 13-Chapter Synthesis`](../adr/ADR-003-pes-production-architecture.md)  
**Status:** APPROVED  
**Date:** 2026-09-11  
**Bounded Context:** Channel Synchronization, Batch Queue Orchestration & Resilient State Persistence  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Overview & Objectives

This specification translates the architectural decisions finalized in [`ADR-003`](../adr/ADR-003-pes-production-architecture.md) (Chapters 01, 02, 03, 10, 11, 12, 13) into precision test specifications and frozen acceptance criteria for:
1. **Domain Value Objects**: Strongly typed representations for `DiscoveredMediaItem`, `ChannelFeedQuery`, `PipelineStatus`, `SyncSummary`, and `LedgerEntry`.
2. **ACID SQLite WAL Ledger Adapter** (`SqliteLedgerAdapter`): Concurrency-safe, persistent idempotency tracking using SQLite in WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`), replacing fragile plain JSON file storage.
3. **Preflight Environmental Validator** (`PreflightHealthChecker`): Ultra-fast (<10ms) bootstrap diagnostics verifying credentials (`SecretStr`), directory permissions, and external binaries (`ffmpeg`) before executing I/O.
4. **Channel Synchronization Orchestrator** (`SyncChannelUseCase`): Application use case coordinating channel feed polling, lookback window filtering, ledger idempotency checks, and batch execution dispatching.
5. **CLI Presentation Subcommands** (`cresmo sync` & `cresmo worker`): Humble Object command-line interfaces for one-shot batch synchronization and continuous background worker polling.

---

## 2. Bounded Context & Architecture Invariants

- **Zero Business Logic in Presentation**: CLI commands (`sync`, `worker`) act strictly as argument parsers and signal routers, delegating 100% of orchestration to `SyncChannelUseCase` and `ChannelPollingDaemon`.
- **ACID Idempotency Guarantee**: Media items already marked `COMPLETED` in the SQLite ledger must never trigger duplicate LLM inference calls unless explicit `--force-refresh` is provided.
- **Fail-Fast Environmental Invariants**: If `PreflightHealthChecker` detects missing credentials or non-writable paths, execution halts immediately with exit code `2` before network or disk operations are started.
- **Pure Dependency Injection**: All use cases and adapters are wired exclusively at the Composition Root (`src/cresmo/presentation/composition.py`).

---

## 3. Test Strategy Classification

| Level | Target Module | Scope & Verification | Mock Boundary |
|---|---|---|---|
| **Unit** | `src/cresmo/domain/value_objects.py` | Construction-time invariants for `DiscoveredMediaItem`, `ChannelFeedQuery`, `PipelineStatus`, `SyncSummary`, `LedgerEntry`. | None (pure domain objects). |
| **Unit** | `src/cresmo/infrastructure/adapters/sqlite_ledger_adapter.py` | Schema initialization, WAL mode verification, `is_processed`, `mark_processed`, `get_entry`, concurrent multi-process reads/writes. | Real temporary SQLite file (`tmp_path / "ledger.db"`). |
| **Unit** | `src/cresmo/application/services/preflight.py` | Credential presence validation, directory write probe, binary path lookups (`shutil.which`). | Mocked OS / binary lookups where needed. |
| **Unit** | `src/cresmo/application/use_cases/sync_channel.py` | Lookback filtering, idempotency skip logic, error trapping per item, summary calculation. | Mocked `MediaIngestionPort`, `LedgerRepositoryPort`, `CresmoPipeline`. |
| **Integration** | `src/cresmo/presentation/cli.py` (`cresmo sync`) | CLI argument parsing, flags propagation (`--lookback`, `--max-videos`, `--dry-run`), exit code mapping. | Mocked `SyncChannelUseCase`. |

---

## 4. Acceptance Criteria & Scenarios (Given-When-Then)

### 4.1 Domain Value Objects

#### Scenario 1.1: `DiscoveredMediaItem` construction validates URL and non-empty metadata
- **Given**: Valid parameters (`content_id=ContentId("dQw4w9WgXcQ")`, `title="Quantum Physics 101"`, `published_at=datetime.now(timezone.utc)`, `media_url="https://youtube.com/watch?v=dQw4w9WgXcQ"`, `channel_name="ScienceHub"`).
- **When**: `DiscoveredMediaItem(...)` is instantiated.
- **Then**: An immutable, frozen object is created with all attributes preserved.
- **When**: Instantiated with empty `title` or invalid `media_url`.
- **Then**: Raises `DomainValidationError`.

#### Scenario 1.2: `ChannelFeedQuery` validates lookback and max limits
- **Given**: Target channel URL `"https://www.youtube.com/@Veritasium"`.
- **When**: Instantiated with `lookback_days=7`, `max_videos=10`.
- **Then**: Validated successfully with positive non-zero constraints.
- **When**: Instantiated with `lookback_days <= 0` or `max_videos <= 0`.
- **Then**: Raises `DomainValidationError`.

#### Scenario 1.3: `PipelineStatus` enumeration values
- **Given**: Status strings: `"COMPLETED"`, `"SKIPPED_IDEMPOTENT"`, `"FAILED_INGESTION"`, `"FAILED_TRANSFORMATION"`.
- **When**: Parsed or queried.
- **Then**: Matches enum members `PipelineStatus.COMPLETED`, `PipelineStatus.SKIPPED_IDEMPOTENT`, etc.

---

### 4.2 SQLite WAL Ledger Adapter (`SqliteLedgerAdapter`)

#### Scenario 2.1: Automatic schema initialization and WAL mode verification
- **Given**: A non-existent database file path (`tmp_path / "cresmo_ledger.db"`).
- **When**: `SqliteLedgerAdapter(db_path)` is initialized.
- **Then**:
  - Creates the SQLite file on disk.
  - Executes `PRAGMA journal_mode=WAL;` and verifies mode is `wal` (or `memory` in hermetic in-memory tests).
  - Executes `PRAGMA synchronous=NORMAL;`.
  - Creates the `cresmo_ledger` table with schema:
    `content_id TEXT PRIMARY KEY, media_url TEXT, title TEXT, channel_name TEXT, status TEXT, notes_count INTEGER, error_message TEXT, started_at TEXT, completed_at TEXT`.

#### Scenario 2.2: Idempotency query (`is_processed`)
- **Given**: An empty ledger database.
- **When**: `is_processed(ContentId("dQw4w9WgXcQ"))` is called.
- **Then**: Returns `False`.
- **When**: An entry for `ContentId("dQw4w9WgXcQ")` with status `COMPLETED` is inserted.
- **Then**: `is_processed(ContentId("dQw4w9WgXcQ"))` returns `True`.

#### Scenario 2.3: Recording processed content (`mark_processed` & `save_entry`)
- **Given**: A valid `LedgerEntry` with status `COMPLETED`.
- **When**: `adapter.save_entry(entry)` or `adapter.mark_processed(content_id)` is invoked.
- **Then**: Entry is committed atomically. Subsequent `get_entry(content_id)` returns an identical `LedgerEntry`.

#### Scenario 2.4: Concurrent read/write resilience
- **Given**: Multiple threads or child processes accessing the same SQLite database file.
- **When**: Concurrent insertions and queries execute simultaneously.
- **Then**: Transactions complete without `sqlite3.OperationalError: database is locked` due to WAL mode and configured `busy_timeout=5000`.

---

### 4.3 Preflight Environmental Validator (`PreflightHealthChecker`)

#### Scenario 3.1: All environmental invariants satisfied
- **Given**: Valid `CresmoSettings` with non-empty `gemini_api_key`, writable `vault_dir`, writable `sqlite_dir`, and `ffmpeg` present in system `PATH`.
- **When**: `checker.check_all()` is executed.
- **Then**: Returns `PreflightResult(is_healthy=True, errors=[])` in <10ms.

#### Scenario 3.2: Missing API key aborts preflight
- **Given**: `gemini_api_key` is empty or unset.
- **When**: `checker.check_all()` is executed.
- **Then**: Returns `PreflightResult(is_healthy=False, errors=["Missing required GEMINI_API_KEY credential"])`.

#### Scenario 3.3: Non-writable vault directory aborts preflight
- **Given**: `vault_dir` points to a read-only or inaccessible filesystem path.
- **When**: `checker.check_all()` is executed.
- **Then**: Returns `PreflightResult(is_healthy=False, errors=["Vault directory is not writable: ..."])`.

---

### 4.4 Channel Synchronization Use Case (`SyncChannelUseCase`)

#### Scenario 4.1: Channel sync filters out-of-window videos
- **Given**: Feed discovery returns 3 videos:
  - Video A: published 2 days ago.
  - Video B: published 5 days ago.
  - Video C: published 20 days ago.
  - Query: `lookback_days=7`.
- **When**: `sync_use_case.execute(query)` runs.
- **Then**: Only Video A and Video B are evaluated; Video C is excluded by the lookback filter.

#### Scenario 4.2: Channel sync skips already-processed items idempotently
- **Given**: Video A is already marked `COMPLETED` in `LedgerRepositoryPort`. Video B is new.
- **When**: `sync_use_case.execute(query)` runs with `force_refresh=False`.
- **Then**:
  - Video A is skipped without invoking `CresmoPipeline`.
  - Video B is passed to `CresmoPipeline.run_for_video`.
  - `SyncSummary` reports `skipped_count=1`, `processed_count=1`, `failed_count=0`.

#### Scenario 4.3: Channel sync handles individual item failure gracefully
- **Given**: Video B fails during LLM transformation (`RateLimitExceededError`).
- **When**: `sync_use_case.execute(query)` runs.
- **Then**:
  - Failure is recorded in SQLite ledger with status `FAILED_TRANSFORMATION`.
  - The use case does not crash the entire batch; it continues to subsequent items.
  - `SyncSummary` reports `failed_count=1`, `status=PipelineStatus.COMPLETED` (batch concluded with partial errors).

#### Scenario 4.4: Dry-run mode queries and filters without writing
- **Given**: Operator supplies `dry_run=True`.
- **When**: `sync_use_case.execute(query, dry_run=True)` runs.
- **Then**: Discovered videos are filtered and printed, but neither `CresmoPipeline` nor SQLite ledger writes are triggered.

---

### 4.5 CLI Subcommands (`cresmo sync` & `cresmo worker`)

#### Scenario 5.1: `cresmo sync --channel <url>` execution
- **Given**: Valid channel URL `"https://youtube.com/@ChannelName"`.
- **When**: Operator executes `cresmo sync --channel https://youtube.com/@ChannelName --lookback 14 --max-videos 5`.
- **Then**: CLI parses arguments, builds dependencies via Composition Root, invokes `SyncChannelUseCase`, prints tabular batch summary to stdout, and exits with code `0`.

#### Scenario 5.2: `cresmo worker` daemon execution
- **Given**: Valid configuration and channel URL.
- **When**: Operator runs `cresmo worker --channel https://youtube.com/@ChannelName --poll-interval 300`.
- **Then**: CLI initializes `ChannelPollingDaemon`, starts non-blocking event loop, writes heartbeat file `/tmp/cresmo_worker.heartbeat`, and cleanly handles `SIGINT`/`SIGTERM` to exit with code `0`.

---

## 5. Verification Matrix & Quality Gates

- [ ] Value Objects unit test suite in `tests/cresmo/unit/test_channel_sync_vo.py`.
- [ ] SQLite WAL Ledger adapter unit test suite in `tests/cresmo/unit/test_sqlite_ledger_adapter.py`.
- [ ] Preflight checker unit test suite in `tests/cresmo/unit/test_preflight_checker.py`.
- [ ] Channel sync use case unit test suite in `tests/cresmo/unit/test_sync_channel_use_case.py`.
- [ ] CLI sync/worker test scenarios in `tests/cresmo/unit/test_cli.py`.
- [ ] 0 regressions across existing 80 unit tests.
- [ ] Static typing: `uv run mypy --strict src/cresmo tests/cresmo` passes cleanly.
- [ ] Linter & Formatter: `uv run ruff check src/cresmo tests/cresmo` passes cleanly.
