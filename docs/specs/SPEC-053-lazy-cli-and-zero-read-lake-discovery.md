# SPEC-053: Lazy Presentation CLI Loading, Subcommand Decoupling, and Zero-Read Lake Discovery

**Status:** ACCEPTED  
**Date:** 2026-11-09  
**Governing ADRs:** [`ADR-053`](../adr/ADR-053-lazy-presentation-cli-loading-and-subcommand-decoupling.md), [`ADR-055`](../adr/ADR-055-extreme-startup-latency-remediation-and-zero-read-lake-discovery.md)  
**Domain Layer:** `cresmo.presentation.cli`, `cresmo.application.use_cases.discovery`, `cresmo.infrastructure.adapters`

---

## 1. Specification Requirements

1. **Lazy CLI Dispatching (`cli.py`):**
   - `LazyCommandGroup` resolves and imports `cresmo.presentation.commands.<cmd>` strictly on subcommand invocation.
   - Importing `cresmo.presentation.cli` does not import `cresmo.application.pipeline`, `composition`, `yt_dlp`, `whisper`, `arq`, or `redis`.
2. **Default-Fast Batch Discovery (`run.py`, `discover_batch_sources.py`):**
   - `enable_channel_crawler` defaults to `False` (`--crawl` opt-in).
   - `LakeScannerService.scan_raw_lake()` is bypassed when `scan_raw=False` and `enable_channel_crawler=False`.
3. **Zero-Read Metadata Extraction (`lake_scanner.py`):**
   - `scan_raw_lake()` derives `content_id` from `rf.stem` and `channel_name` from `rf.parent.name` with zero file content reads.
4. **Deferred Adapter Initialization:**
   - `SqliteLedgerAdapter` defers `_init_db()` to first `_get_connection()` call.
   - `JsonPromptProvider` defers catalog loading to first `get_prompt()` / `catalog` access.
   - `NativeMediaIngestionAdapter` defers `yt_dlp` and `whisper` imports to operational execution methods.

