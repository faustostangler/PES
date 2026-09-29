# SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform Specification

**Status:** APPROVED (FROZEN)  
**Date:** 2026-09-26  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, SRE, 12-Factor App)  
**Governing ADR:** [`docs/adr/ADR-023-prometheus-sre-golden-signals-and-dora-metrics-platform.md`](../adr/ADR-023-prometheus-sre-golden-signals-and-dora-metrics-platform.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Objective & Scope

This specification establishes the exact behavioral contracts, type definitions, numerical invariants, boundary limits, and acceptance criteria for implementing the **`MetricsPort`**, **`PrometheusMetricsAdapter`**, **SRE Golden Signals**, and **DORA Metrics** in the Cresmo Modular Monolith.

It formalizes the separation between:
1. **GenAI / LLM Observability:** Hierarchical traces, token usage, and qualitative evaluation scores governed by `TelemetryPort` and Langfuse v4 ([ADR-016](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md)).
2. **Infrastructure & Operational Confiability:** Time-series Golden Signals (Latency, Traffic, Errors, Saturation) governed by `MetricsPort` and Prometheus v3.x.
3. **Engineering Velocity (DORA Four Keys):** Quantitative delivery metrics measuring deployment frequency, lead time, change failure rate, and recovery time.

---

## 2. Ubiquitous Language (Metrics & SRE Context)

- **`MetricsPort`**: Hexagonal application port defining contracts for emitting multi-dimensional time-series metrics.
- **`Prometheus Golden Signals`**: Four essential operational metrics defined by Google SRE:
  - *Latency:* Time taken to service a request or stage.
  - *Traffic:* Measure of demand placed on the system (transcripts/second, notes/minute).
  - *Errors:* Rate of requests or operations that fail.
  - *Saturation:* Measure of system fraction utilization (queue depth, memory usage).
- **`DORA Metrics`**: The four key delivery metrics defined by DevOps Research and Assessment:
  - *Deployment Frequency (DF):* Rate of successful software releases to target environments.
  - *Lead Time for Changes (LTTC):* Duration from commit creation to production execution.
  - *Change Failure Rate (CFR):* Percentage of deployments causing production degradation or preflight failure.
  - *Time to Restore Service (TTRS):* Time taken to recover from a production outage or failed deployment.
- **`NoOpMetricsAdapter`**: Hermetic null-object implementation executing all metric calls as immediate zero-cost no-ops.
- **`PrometheusMetricsAdapter`**: Infrastructure adapter translating `MetricsPort` calls into `prometheus_client` collectors.

---

## 3. Application Port Definition (`src/cresmo/application/ports.py`)

### 3.1 Contract Interface

```python
class MetricsPort(ABC):
    """Hexagonal Port defining time-series operational and domain metrics contracts."""

    @abstractmethod
    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter by a non-negative value.

        Args:
            name: Canonical metric name conforming to Prometheus naming rules.
            value: Increment value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.
        """

    @abstractmethod
    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution.

        Args:
            name: Canonical metric name.
            value: Observed duration or size value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.
        """

    @abstractmethod
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge.

        Args:
            name: Canonical metric name.
            value: Arbitrary numeric value.
            labels: Optional dimensional key-value pairs.
        """
```

---

## 4. Canonical Metric Schema & Invariants

### 4.1 Prometheus SRE Golden Signals

| Signal | Metric Name | Type | Standard Bucket Array / Range | Required Labels |
|---|---|---|---|---|
| **Latency** | `cresmo_pipeline_stage_duration_seconds` | Histogram | `[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]` | `stage`, `channel_id`, `channel_name`, `status` |
| **Latency** | `cresmo_media_ingestion_duration_seconds` | Histogram | `[0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 45.0, 90.0, 180.0, 300.0]` | `channel_id`, `channel_name`, `modality`, `status` |
| **Latency** | `cresmo_llm_request_duration_seconds` | Histogram | `[0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 60.0]` | `model`, `system`, `role` |
| **Traffic** | `cresmo_transcripts_processed_total` | Counter | Monotonic `val >= 0.0` | `channel_id`, `channel_name`, `content_id`, `status`, `modality` |
| **Traffic** | `cresmo_atomic_notes_synthesized_total` | Counter | Monotonic `val >= 0.0` | `channel_id`, `channel_name`, `content_id`, `note_type` |
| **Traffic** | `cresmo_batch_sources_discovered_total` | Counter | Monotonic `val >= 0.0` | `channel_id`, `channel_name`, `modality` |
| **Errors** | `cresmo_pipeline_errors_total` | Counter | Monotonic `val >= 0.0` | `error_type`, `channel_id`, `channel_name`, `content_id`, `stage` |
| **Errors** | `cresmo_judge_retry_count_total` | Counter | Monotonic `val >= 0.0` | `channel_id`, `channel_name`, `content_id`, `pass_type` |
| **Errors** | `cresmo_ingestion_failures_total` | Counter | Monotonic `val >= 0.0` | `channel_id`, `channel_name`, `content_id`, `reason` |
| **Saturation** | `cresmo_discovery_queue_size` | Gauge | Integer `[0, queue_maxsize]` | None (global queue) |
| **Saturation** | `cresmo_process_resident_memory_bytes` | Gauge | Bytes `val >= 0` | `role` |
| **Saturation** | `cresmo_gc_collections_total` | Counter | Monotonic `val >= 0` | `generation` (`0`, `1`, `2`) |

### 4.2 DORA Four Keys Schema

| DORA Key | Metric Name | Type | Calculation / Collection Logic |
|---|---|---|---|
| **Deployment Frequency** | `cresmo_dora_deployments_total` | Counter | Incremented on container start / successful release activation with `environment="production|local"`, `status="success|failure"`. |
| **Lead Time for Changes** | `cresmo_dora_lead_time_seconds` | Gauge / Histogram | Difference between release commit timestamp and runtime activation timestamp. |
| **Change Failure Rate** | Derived Ratio | PromQL Expression | `sum(rate(cresmo_dora_failed_deployments_total[30d])) / sum(rate(cresmo_dora_deployments_total[30d]))` |
| **Time to Restore Service** | `cresmo_dora_restore_duration_seconds` | Histogram | Elapsed seconds between preflight/healthcheck alert firing and subsequent healthy recovery check. |

---

## 5. Local-First Strategy & Deferred CI/CD Matrix

> [!IMPORTANT]
> **Phased Implementation Governance:**  
> The Cresmo project is currently developed and run in a **strictly local-first** environment (local terminal, local docker compose, local Obsidian vault). Full automated cloud CI/CD pipelines are formally scheduled for Phase 6.

### CI/CD Deferral Tracking

| Component | Current Local Status (Phase 1-5) | Future Remote Status (Phase 6 - Deferred) |
|---|---|---|
| **Deployment Frequency Tracking** | Emitted locally upon container/process startup and configuration verification (`cresmo check-config`). | **TODO(CI-CD-01)**: GitHub Actions workflow (`.github/workflows/deploy.yml`) emitting deployment webhook to Prometheus Pushgateway. |
| **Lead Time for Changes** | Computed locally using `git log -1 --format=%ct` vs startup time. | **TODO(CI-CD-02)**: GitHub Actions calculating `merge_commit_timestamp - first_commit_timestamp` and recording metric. |
| **Change Failure Rate** | Emitted when `preflight_res.assert_healthy()` raises `PreflightError` in container entrypoint. | **TODO(CI-CD-03)**: ArgoCD sync failure hooks and automated rollback incident markers. |
| **Time to Restore Service** | Monitored locally via Prometheus alert state transitions. | **TODO(CI-CD-04)**: Sentry and PagerDuty incident resolution webhooks exporting MTTR to Prometheus. |

---

## 6. Acceptance Criteria (Given-When-Then)

### Scenario 1: Counter Increment Validation
- **Given** an initialized `PrometheusMetricsAdapter`.
- **When** `increment_counter("cresmo_transcripts_processed_total", 1.0, {"channel_id": "UC_sandeco", "channel_name": "sandeco", "content_id": "yt_123", "status": "completed", "modality": "url"})` is called.
- **Then** the underlying Prometheus counter increases by exactly `1.0`.
- **And** calling `increment_counter` with a negative value raises `ValueError` (Counter non-negative invariant).

### Scenario 2: Latency Histogram Observation
- **Given** an initialized `PrometheusMetricsAdapter`.
- **When** `observe_histogram("cresmo_pipeline_stage_duration_seconds", 3.45, {"stage": "fluid_prose", "channel_id": "UC_sandeco", "channel_name": "sandeco", "status": "success"})` is called.
- **Then** the observation is placed into the appropriate histogram bucket (`5.0` bucket count incremented).
- **And** calling `observe_histogram` with a negative duration raises `ValueError`.

### Scenario 3: Saturation Gauge Setting
- **Given** an active `stream_queue` with 12 items.
- **When** `set_gauge("cresmo_discovery_queue_size", 12.0)` is executed.
- **Then** the Prometheus gauge value equals `12.0`.
- **When** the queue drains to 0 items and `set_gauge("cresmo_discovery_queue_size", 0.0)` is called.
- **Then** the gauge value reflects `0.0`.

### Scenario 4: Hermetic NoOp Fallback
- **Given** an initialized `NoOpMetricsAdapter`.
- **When** any method (`increment_counter`, `observe_histogram`, `set_gauge`) is called with arbitrary values or labels.
- **Then** execution completes silently in < 0.001ms with zero exceptions.
- **And** no background threads or network sockets are opened.

### Scenario 5: Pipeline Stage Duration Recording
- **Given** a `CresmoPipeline` wired with a live `MetricsPort`.
- **When** `pipeline.execute(raw)` completes the `expansion` stage.
- **Then** `observe_histogram` is invoked with `name="cresmo_pipeline_stage_duration_seconds"`, `labels={"stage": "expansion", "channel_id": raw.channel_id.value if raw.channel_id else "", "channel_name": raw.channel_name.value, "status": "success"}`.

### Scenario 6: Ingestion Latency Recording
- **Given** a `NativeMediaIngestionAdapter` wired with `MetricsPort`.
- **When** `ingest_single_video(video_url)` finishes downloading subtitles via `yt-dlp`.
- **Then** `observe_histogram` is invoked with `name="cresmo_media_ingestion_duration_seconds"`, `labels={"channel_id": ch_id.value if ch_id else "", "channel_name": channel_name, "modality": "url", "status": "success"}`.

### Scenario 7: Memory Hygiene RSS Recording
- **Given** a batch execution in `execute_batch_run`.
- **When** the `finally` block executes `gc.collect()`.
- **Then** `set_gauge` is invoked with `name="cresmo_process_resident_memory_bytes"` and the current process RSS bytes.

### Scenario 8: Local Scraping Endpoint Exposition
- **Given** the Cresmo background worker or API running with metrics enabled.
- **When** an HTTP GET request is made to `http://localhost:9090/metrics` (or configured port).
- **Then** the response status is `200 OK`.
- **And** the body contains valid Prometheus exposition text formatted with `# TYPE` and `# HELP` headers for all registered `cresmo_*` metrics.

---

## 7. Test Strategy Classification

| Level | Target | Test File | Method |
|---|---|---|---|
| **Unit** | `MetricsPort` contract & `NoOpMetricsAdapter` | `tests/cresmo/unit/test_metrics_port.py` | Hermetic mock verification, boundary value tests. |
| **Unit** | `PrometheusMetricsAdapter` | `tests/cresmo/unit/test_prometheus_adapter.py` | Isolated registry inspection (`CollectorRegistry`), label validation. |
| **Integration** | Pipeline & Ingestion instrumentation | `tests/cresmo/unit/test_pipeline_telemetry.py` | Verify pipeline use cases invoke `MetricsPort` with canonical labels. |
| **Integration** | Local HTTP Scraper endpoint | `tests/cresmo/integration/test_metrics_endpoint.py` | Scrape `/metrics` endpoint and parse Prometheus text payload. |
| **Mutation Gate** | Mutant killer across metrics adapters | `mutmut run --paths-to-mutate src/cresmo/infrastructure/adapters/prometheus_metrics_adapter.py` | Target: 0 survived mutants. |
