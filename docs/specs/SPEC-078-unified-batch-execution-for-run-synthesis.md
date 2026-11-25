# SPEC-078: Unified Batch Execution for RunSynthesisUseCase

- **Related ADR:** [ADR-078](../adr/ADR-078-unified-batch-execution-for-run-synthesis.md)
- **Status:** Accepted
- **Date:** 2026-11-25

---

## 1. `RunSynthesisOutcome` Contract (`src/cresmo/application/use_cases/run_synthesis.py`)

`RunSynthesisOutcome` (frozen dataclass with `slots=True`) contains only unified batch fields:
- `status: RunExitStatus`
- `batch_id: BatchId | None = None`
- `completed: int = 0`
- `skipped: int = 0`
- `failed: int = 0`
- `total_items: int = 0`
- `dry_run: bool = False`
- `empty_sources: bool = False`
- `dry_run_validated: int = 0`
- `dry_run_total: int = 0`
- `manifest_display: str = "data/playlist.txt"`
- `scan_raw: bool = False`

Removed fields: `mode`, `single_stages_completed`, `single_final_chars`, `single_content_id`, `single_dry_run_chars`, `single_dry_run_url`.

---

## 2. Behavioral Invariants

1. **Single-URL Dispatch (`request.url` truthy):**
   - `discover_sources_factory` is NOT invoked.
   - Sources list is `[BatchSource(kind=SourceModality.URL, target=request.url)]`.
   - When `request.dry_run=True`: routes to `_execute_batch_dry_run`, returning `RunExitStatus.SUCCESS` with `dry_run=True`, `dry_run_total=1`, and `dry_run_validated=1` (on transcript) or `0` (on `None`, emitting `BatchItemEventKind.DRY_RUN_FAILED`).
   - When `request.dry_run=False`: routes to `_execute_batch_run`, generating a `BatchId`, passing `batch_id=batch_id` to `pipeline.run_for_video(...)`, executing `_drain_telemetry_and_memory(pipeline)` in `finally:`, and running `_consolidate_master(pipeline, on_event)` if `completed > 0`.
2. **Quota & Error Handling on Single-URL:**
   - `QuotaPoolExhaustedError` aborts immediately with `RunExitStatus.RATE_LIMITED`, `failed=1`, `total_items=1`, and `BatchItemEventKind.QUOTA_ABORT`.
   - `RateLimitExceededError`, `IngestionNetworkError`, and `Exception` are recorded as `failed=1`, `total_items=1`, returning `RunExitStatus.INTERNAL_ERROR`.
3. **Presentation Rendering (`src/cresmo/presentation/commands/run.py`):**
   - `_render_outcome` handles only `empty_sources`, `dry_run`, and `Batch Synthesis Summary [Batch: {batch_label}]:`.
