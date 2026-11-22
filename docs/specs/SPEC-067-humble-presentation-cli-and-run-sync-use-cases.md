# SPEC-067: Humble Presentation CLI & Run/Sync Use Cases

- **Related ADR:** [ADR-067](../adr/ADR-067-humble-presentation-cli-and-run-sync-use-cases.md)
- **Status:** Accepted
- **Date:** 2026-11-22

---

## 1. Domain & Application Port Contracts

### 1.1 `QuotaPoolExhaustedError` (`src/cresmo/domain/exceptions.py`)
- Subclasses `RateLimitExceededError`.
- Constructor: `__init__(self, message: str = "", *, retry_after_seconds: float = 0.0) -> None`.
- Stores `self.retry_after_seconds = max(0.0, float(retry_after_seconds))`.
- `CredentialPoolExhaustedError` (`src/cresmo/infrastructure/adapters/llm/gemini_pool.py`) inherits `(QuotaPoolExhaustedError, RuntimeError)` and forwards `retry_after_seconds`.

### 1.2 `ProcessRuntimePort` (`src/cresmo/application/ports/runtime.py`)
- Abstract base class exporting:
  - `collect_garbage(self) -> int`
  - `get_process_rss_bytes(self) -> float`
  - `get_file_size_bytes(self, path: Path) -> int`
- `NoOpProcessRuntimePort` returns `0`, `0.0`, `0`.
- `SystemProcessRuntimeAdapter` (`src/cresmo/infrastructure/adapters/system/process_runtime_adapter.py`) executes `gc.collect()`, delegates RSS query to `get_process_rss_bytes()`, and returns `path.stat().st_size`.

---

## 2. `RunSynthesisUseCase` (`src/cresmo/application/use_cases/run_synthesis.py`)

### 2.1 Immutable DTOs
- `RunExitStatus(StrEnum)`: `"success"`, `"rate_limited"`, `"ingestion_error"`, `"internal_error"`.
- `BatchItemEventKind(StrEnum)`: `"preflight_warning"`, `"discovery_progress"`, `"skipped_artifact"`, `"skipped_idempotent"`, `"completed"`, `"dry_run_text"`, `"dry_run_url"`, `"dry_run_failed"`, `"item_rate_limited"`, `"item_network_error"`, `"item_failed"`, `"quota_abort"`, `"master_warning"`, `"master_consolidated"`.
- `BatchItemEvent` (frozen dataclass with `slots=True`): `kind`, `message`, optional `item_prefix`, `content_id`, `target`.
- `RunSynthesisRequest` (frozen dataclass with `slots=True`): `url`, `manifest`, `passes=3`, `batch_size=None`, `dry_run=False`, `force_reprocess=False`, `lookback=None`, `channel_max_videos=50`, `scan_raw=False`, `crawl=False`, `web_index=False`, `channels=()`, `categories=()`, `video_ids=()`.
- `RunSynthesisOutcome` (frozen dataclass with `slots=True`): `status: RunExitStatus`, `mode: str` (`"single"` or `"batch"`), `batch_id: BatchId | None`, `completed: int`, `skipped: int`, `failed: int`, `aborted_by_quota: bool`, `total_items: int`, `dry_run: bool`, `empty_sources: bool`, `master_parts_generated: int`, `master_channels_count: int`, `single_notes_count: int`, `single_mocs_count: int`, `single_duplicates_unified: int`, `single_content_id: str | None`, `single_dry_run_chars: int | None`, `single_dry_run_url: str | None`, `dry_run_validated: int`, `dry_run_total: int`, `manifest_display: str`, `scan_raw: bool`, `error_message: str | None`.

### 2.2 Behavioral Invariants
1. Execute `preflight_checker.check_all().assert_healthy()` **before** invoking `pipeline_factory()`. Emit `"preflight_warning"` event per warning.
2. Call `pipeline.warmup()` only when `not request.web_index`.
3. Single-video mode (`request.url` is truthy):
   - `dry_run=True`: call `pipeline.ingest_raw_transcript.execute(video_url=request.url)`. Return `RunExitStatus.INGESTION_ERROR` if `None`; otherwise `SUCCESS` with `single_dry_run_chars`.
   - `dry_run=False`: call `pipeline.run_for_video(...)`. If `already_processed`, return `SUCCESS` with `skipped=1`. If `success`, attempt best-effort single-channel `concat_master.execute(ChannelName(raw.channel.name))` (catching non-fatal exceptions into `"master_warning"` event) and return `SUCCESS` with `completed=1`. Otherwise return `INTERNAL_ERROR`.
4. Batch mode (`request.url` is `None`/empty):
   - Build `BatchDiscoveryQuery` where `enable_channel_crawler = True if request.crawl else getattr(settings, "enable_channel_crawler", False)`.
   - `dry_run=True`: materialize sources via `discover_sources_factory`, validate files via `is_processable_transcript_file` + `runtime_port.get_file_size_bytes(file_path)` and URLs via `pipeline.ingest_raw_transcript.execute(...)`.
   - `dry_run=False`: stream sources using a single `BatchId.generate()`.
     - Catch `QuotaPoolExhaustedError` to emit `"quota_abort"`, increment `failed`, set `aborted_by_quota=True`, and **immediately `break`**.
     - Catch `RateLimitExceededError`, `IngestionNetworkError`, and generic `Exception` as non-aborting item failures (`failed += 1`).
     - In per-item `finally:`: flush telemetry (`pipeline.telemetry_port.flush()`), run `runtime_port.collect_garbage()`, query `runtime_port.get_process_rss_bytes()`, and record `cresmo_process_resident_memory_bytes` + `cresmo_gc_collections_total` via `pipeline.metrics_port` (errors caught safely so cleanup never masks item results).
     - After loop: run `concat_master_factory(pipeline.vault_port).execute_all()` **iff** `completed > 0`.
     - Return `RATE_LIMITED` if `aborted_by_quota`, `SUCCESS` if `failed == 0`, else `INTERNAL_ERROR`.

---

## 3. `SyncBatchUseCase` (`src/cresmo/application/use_cases/sync_batch.py`)

### 3.1 Immutable DTOs
- `SyncTargetEventKind(StrEnum)`: `"video"`, `"channel"`.
- `SyncTargetEvent` (frozen dataclass with `slots=True`): `kind`, `target`, `total_discovered`, `processed`, `skipped`, `failed`, `duration_seconds`.
- `SyncBatchRequest` (frozen dataclass with `slots=True`): `channels=()`, `categories=()`, `video_ids=()`, `manifest=None`, `lookback=7*52*2`, `max_videos=250`, `batch_size=None`, `dry_run=False`, `force_refresh=False`.
- `SyncBatchOutcome` (frozen dataclass with `slots=True`): `channels_synced`, `total_discovered`, `total_processed`, `total_skipped`, `total_failed`, `no_matching_channels`, `mode_description`, `manifest_path`, `direct_video_mode`.

### 3.2 Behavioral Invariants
1. If `video_ids` non-empty: sync each video URL/ID directly with `max_videos=1`.
2. Otherwise: resolve target channels via explicit `channels` tokens OR `read_manifest_lines(request.manifest or default_manifest_path)` filtered by `SyncFilterCriteria` + `taxonomy_port`.
3. Sort resolved channel URLs strictly ascending case-insensitively (`sorted(channels, key=str.lower)` per `ADR-012`).
4. Report `no_matching_channels=True` with `mode_description` when zero channels match.

---

## 4. Presentation CLI Controller & Unified Error Handler

### 4.1 `presentation/error_handler.py`
- Canonical exception mapping:
  - `RateLimitExceededError` -> `EXIT_RATE_LIMIT_EXCEEDED` (4), `"Rate limit exceeded: {exc}"`
  - `IngestionNetworkError` -> `EXIT_INGESTION_ERROR` (5), `"Ingestion network error: {exc}"`
  - `PreflightError` -> `EXIT_CONFIG_OR_USAGE_ERROR` (2), `"Preflight error: {exc}"`
  - `SecurityViolationError` -> `EXIT_CONFIG_OR_USAGE_ERROR` (2), `"Security boundary violation: {exc}"`
  - `(DomainValidationError, CresmoDomainError)` -> `EXIT_DOMAIN_VALIDATION_ERROR` (3), `"Domain validation error: {exc}"`
  - `ValidationError` -> `EXIT_CONFIG_OR_USAGE_ERROR` (2), `"Configuration error: {exc}"`
  - `Exception` -> `EXIT_INTERNAL_ERROR` (1), `"{fallback_prefix}: {exc}"`

### 4.2 Purged Dead CLI Flags (12 Occurrences)
| Subcommand | Removed Flags | Exit Code When Passed |
| :--- | :--- | :--- |
| `run` | `--all`, `--device`, `--concurrency`, `--verbose`/`-v`, `--no-crawl` | Non-zero (`2`) |
| `sync` | `--verbose`/`-v` | Non-zero (`2`) |
| `check-config` | `--verbose`/`-v` | Non-zero (`2`) |
| `concat-master` | `--verbose`/`-v` | Non-zero (`2`) |
| `export-cookies` | `--verbose`/`-v` | Non-zero (`2`) |
| `seed-prompts` | `--verbose`/`-v` | Non-zero (`2`) |
| `worker` | `--verbose`/`-v` | Non-zero (`2`) |
| `dedupe` | `--dry-run` (destructive no-op; `--verbose`/`-v` retained) | Non-zero (`2`) |

### 4.3 Import Purity & Removal Invariants (`ADR-010`)
- `src/cresmo/presentation/commands/{run,sync,check_config}.py`: zero imports from `cresmo.infrastructure`, `opentelemetry`, or `gc`.
- `src/cresmo/application/use_cases/{run_synthesis,sync_batch}.py`: zero imports from `cresmo.infrastructure`, `opentelemetry`, `sys`, or `gc`.
- `src/cresmo/presentation/commands/__init__.py`: remove `execute_batch_dry_run`, `execute_batch_run`, `execute_single_video_run`, `load_batch_sources`.
