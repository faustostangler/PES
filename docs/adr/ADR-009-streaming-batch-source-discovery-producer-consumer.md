# ADR-009: Streaming Batch Source Discovery via Producer-Consumer Pattern

**Status:** APPROVED  
**Date:** 2026-09-17  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-010`](ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-012`](ADR-012-multi-criteria-sync-filtering-and-alphabetical-feed-ordering.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md)  

---

## 1. Context

In Cresmo's batch execution mode (`cresmo run`), batch source discovery was performed synchronously via `DiscoverBatchSourcesUseCase.execute(query) -> list[BatchSource]`.

### The Problem: Pre-Ingestion Starvation & High Latency
1. **Synchronous Blocking:** The use case synchronously executed:
   - Priority file scanning (local filesystem, < 5ms).
   - Priority playlist parsing (local filesystem, < 5ms).
   - Remote seed resolution (`yt-dlp` network probes).
   - Upload feed crawling across all historical channels (`yt-dlp` playlist queries).
2. **Resource Idleness:** While `yt-dlp` performed dozens of HTTP requests querying channel feeds (taking 15–90 seconds), the pipeline sat idle. Standalone priority videos and local priority texts were already known and ready for ingestion at $t=0$, yet their downloading was delayed until the entire crawling phase finished.
3. **User Experience (DX):** The user experienced an extended pause with no transcript download progress, reducing interactive responsiveness.

---

## 2. Decision

We implement the **Producer-Consumer Pattern with Streaming Queue** in `DiscoverBatchSourcesUseCase`, allowing pipeline stages to overlap I/O discovery with download ingestion.

### 2.1 Fast-Path Priority Ejection ($t=0$)
Priority sources (local markdown/text compendiums in `priority_texts_dir` and videos in `playlist_priority_path`) are resolved immediately from disk and yielded to the consumer in the first milliseconds of execution before the background crawler is launched.

### 2.2 Background Crawler Producer Thread
If `enable_channel_crawler=True` and `media_ingestion_port` is available:
- Channel feed resolution and upload probing run in a dedicated background worker thread (`CresmoCrawlerProducer`).
- Discovered videos are filtered against the local raw lake and thread-safe deduplication sets, then pushed to a thread-safe `queue.Queue[BatchSource | None | Exception]`.
- A sentinel (`None`) signals completion of discovery.
- A `threading.Event` allows graceful cancellation if the consumer terminates early.

### 2.3 Concurrency Topology & Named Thread Pools (ADR-020 Pillar 5)
Inside the `CresmoCrawlerProducer` thread, secondary network operations run in named, bounded thread pools to guarantee deterministic APM and Linux thread profiling:
- **`CresmoChannelResolver`**: `ThreadPoolExecutor(thread_name_prefix="CresmoChannelResolver")` for concurrent parent channel discovery from video seeds.
- **`CresmoFeedProber`**: `ThreadPoolExecutor(thread_name_prefix="CresmoFeedProber")` for concurrent probing of recent channel uploads within the lookback window.

### 2.4 Anti-TOCTOU State Isolation & Local Snapshot Pattern (ADR-020 Pillar 6)
To eliminate Time-of-Check to Time-of-Use race conditions when pushing discovered items to consumer queues:
- The accumulator callback invocation uses a local variable snapshot:
  ```python
  cb = self.on_source_added
  if cb is not None:
      cb(src)
  ```
- All modifications to internal source sets in `_BatchSourceAccumulator` are guarded by reentrant mutex locks (`self._lock`).

### 2.5 Streaming Generator & Dual Interface
`DiscoverBatchSourcesUseCase` exposes:
- `execute_stream(query) -> Iterator[BatchSource]`: Yields items incrementally as soon as they become available.
- `execute(query) -> list[BatchSource]`: Maintains 100% backward compatibility by returning `list(self.execute_stream(query))`.

### 2.6 Presentation Layer Integration
In `src/cresmo/presentation/commands/run.py`:
- `execute_batch_run` consumes from `execute_stream()`.
- Priority items begin downloading immediately, while crawler log notifications and feed queries run concurrently in the background.

---

## 3. Verification & Test Coverage

- Unit tests in `tests/cresmo/unit/test_discover_batch_sources.py` verifying:
  - Fast-path priority items yielded before background crawler finishes.
  - Correct termination with Sentinel (`None`).
  - Thread safety and deduplication across priority and crawled sources.
  - Backward compatibility of `execute()` returning complete consolidated list.
- CLI verification in `tests/cresmo/unit/test_cli.py`.

---

## 4. Consequences & Impact

### Positive
1. **Zero-Latency Ingestion:** High-priority items begin downloading within milliseconds of command startup.
2. **I/O Overlapping:** Channel crawling time is masked behind actual transcript download and LLM synthesis time.
3. **Clean Architecture Intact:** Uses standard library concurrency (`queue.Queue`, `threading.Thread`) without framework pollution in application use cases.
4. **Resilience & Graceful Degradation:** If crawler fails or hits rate limits, priority items have already been processed without disruption.

### Negative / Trade-offs
- The total item count in batch execution is dynamic rather than fixed upfront in the CLI status output.
