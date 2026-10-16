# ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform

**Status:** ACCEPTED  
**Date:** 2026-09-26  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, SRE, 12-Factor App)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-010`](ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-017`](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md)

---

## 1. Context & Problem Statement

The Cresmo Modular Monolith has achieved end-to-end cognitive synthesis orchestration, combining media ingestion, multi-pass fluid prose, longitudinal and synchronic expansion, atomic note extraction, and MOC reconciliation. Deep GenAI observability is currently governed by **Langfuse v4** ([ADR-016](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [ADR-017](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md)), which tracks LLM token consumption, inference latency, prompt versions, and judge evaluation friction scores.

### 1.1 Identified Architectural Deficits

However, the system currently lacks standardized, high-performance time-series telemetry for **Site Reliability Engineering (SRE)** and **Engineering Velocity**:

1. **Absence of Prometheus Golden Signals (SRE):**
   - *Latency:* No time-series histogram tracks media download duration (yt-dlp/audio extraction) isolated from LLM generation time.
   - *Traffic:* No rate metrics track throughput of transcripts processed per channel, notes generated per minute, or discovery feed polling velocity.
   - *Errors:* No structured operational counters categorize infrastructure crashes (`RateLimitExceededError`, `IngestionNetworkError`, `PreflightError`, `DomainValidationError`) apart from unstructured stdout/stderr text.
   - *Saturation:* No metrics measure the streaming discovery queue depth (`stream_queue.maxsize = 50`) or process memory resident set size (`RSS`) post-garbage collection.

2. **Absence of Delivery Performance Metrics (DORA 4 Keys):**
   - The project lacks a codified measurement framework for DORA metrics (**Deployment Frequency**, **Lead Time for Changes**, **Change Failure Rate**, and **Time to Restore Service**). While the system is currently developed and executed in a local-first environment, engineering excellence requires establishing the metric contracts, event schema, and local observation points now, preparing seamless hook points for automated CI/CD when deployed remotely.

3. **Risk of Domain Pollution:**
   - Injecting third-party metrics clients (e.g. `prometheus_client`) directly into domain entities or use cases would violate Hexagonal Architecture and the Clean Architecture boundaries enforced across the workspace.

---

## 2. Decision

We establish the **Prometheus SRE Golden Signals and DORA Metrics Platform** in Cresmo under the Doctor Stangler Architecture Method:

### 2.1 Hexagonal Segregation: Introduction of `MetricsPort`
We introduce an explicit, dedicated **`MetricsPort`** in [`src/cresmo/application/ports/metrics.py`](../../src/cresmo/application/ports/metrics.py), adhering to the **Interface Segregation Principle (ISP)**. It remains completely distinct from `TelemetryPort` (which governs trace trees and Langfuse GenAI session replays):

- **Domain and Application Layers:** Rely strictly on `MetricsPort` and pure Value Objects (`MetricName`, `MetricLabels`). No imports of `prometheus_client` or time-series libraries are permitted outside `src/cresmo/infrastructure/adapters/`.
- **Infrastructure Layer:**
  - `PrometheusMetricsAdapter`: Implements `MetricsPort` using `prometheus_client`, managing registered counters, histograms, and gauges with thread-safe registries.
  - `NoOpMetricsAdapter`: Hermetic null-object implementation used during unit tests or when metrics collection is disabled, guaranteeing sub-millisecond execution and zero network overhead.

### 2.2 Prometheus Golden Signals Schema
The following canonical metric names and label schemas are standardized across Cresmo:

#### 1. Latency (Histograms in seconds with explicit exponential/logarithmic bucket arrays)
- `cresmo_pipeline_stage_duration_seconds{stage, channel_id, channel_name, status}`: Execution duration of pipeline synthesis stages (`raw_indexing`, `fluid_prose`, `expansion`, `inventory`, `atomic_batch`, `mocs`, `duplicate_unification`).
- `cresmo_media_ingestion_duration_seconds{channel_id, channel_name, modality, status}`: Time taken by `MediaIngestionPort` to probe metadata and download subtitles or audio.
- `cresmo_llm_request_duration_seconds{model, system, role}`: Roundtrip duration of external LLM API calls.

#### 2. Traffic (Monotonically increasing Counters)
- `cresmo_transcripts_processed_total{channel_id, channel_name, content_id, status, modality}`: Total count of transcript units consumed by the pipeline (`status="completed|skipped_idempotent|failed"`).
- `cresmo_atomic_notes_synthesized_total{channel_id, channel_name, content_id, note_type}`: Total count of discrete Obsidian atomic notes synthesized.
- `cresmo_batch_sources_discovered_total{channel_id, channel_name, modality}`: Total count of media items emitted by the discovery generator.

#### 3. Errors (Counters partitioned by failure taxonomy)
- `cresmo_pipeline_errors_total{error_type, channel_id, channel_name, content_id, stage}`: Count of unhandled or caught pipeline failures (`error_type="rate_limit|network|domain_validation|preflight|internal"`).
- `cresmo_judge_retry_count_total{channel_id, channel_name, content_id, pass_type}`: Total count of iterative rewrite cycles triggered by LLM-as-a-judge validation failures.
- `cresmo_ingestion_failures_total{channel_id, channel_name, content_id, reason}`: Failures encountered during media extraction (`reason="video_unavailable|no_subtitles|private_video"`).

#### 4. Saturation (Gauges reflecting instantaneous pressure)
- `cresmo_discovery_queue_size`: Number of pending `BatchSource` items buffered in the bounded discovery queue (`stream_queue`, max capacity 50).
- `cresmo_process_resident_memory_bytes`: Physical resident memory (RSS) occupied by the Python runtime, recorded in memory hygiene checkpoints.
- `cresmo_gc_collections_total{generation}`: Count of Python garbage collection sweeps triggered per ADR-020 memory hygiene.

---

### 2.3 DORA Metrics Architecture & Delivery Pipeline Contracts

We adopt the **DORA Four Keys** to measure engineering efficiency and operational stability:

1. **Deployment Frequency (DF):**
   - Metric: `cresmo_dora_deployments_total{environment, role, status}`.
   - Evaluated as the frequency of successful releases or container restarts manifesting active code updates.
2. **Lead Time for Changes (LTTC):**
   - Metric: `cresmo_dora_lead_time_seconds{branch, release_tag}`.
   - Evaluated as the duration between the git commit timestamp and its execution activation.
3. **Change Failure Rate (CFR):**
   - Metric: Ratio of `cresmo_dora_failed_deployments_total` over `cresmo_dora_deployments_total`.
   - Triggers when active preflight checks (`cresmo check-config`, `cresmo-check`) fail or when a deployment causes an immediate crash loop.
4. **Time to Restore Service (TTRS / MTTR):**
   - Metric: `cresmo_dora_restore_duration_seconds{incident_id}`.
   - Measured as the elapsed time from incident detection (preflight failure or critical alert) until recovery validation.

#### CI/CD & Remote Deployment Phasing:
> [!IMPORTANT]
> **TODO(CI-CD): Deferred Remote Integration**  
> Because current development and execution are strictly local (local workstation, local Docker Compose, direct CLI runs), all remote CI/CD workflows (GitHub Actions workflows `.github/workflows/deploy.yml`, automated release taggers, remote webhook dispatchers, and cloud alerting webhooks) are marked with explicit **TODO** anchors and deferred to Phase 6.  
> In the current phase, DORA metric primitives are implemented locally via:
> 1. Local execution and configuration verification markers (`cresmo check-config`).
> 2. SQLite Ledger deployment audit rows (`cresmo_ledger.db`).
> 3. Direct Prometheus metric exposition on local runtime instances.

---

### 2.4 Infrastructure Topology (SOTA-KISS: All Running vs Nothing Running)
In accordance with ADR-005 and the project `Makefile`, observability services are orchestrated declaratively without runtime fragmentation:

1. **`docker-compose.monitoring.yml`:**
   - Defines `cresmo-prometheus` (Prometheus v3.x image) and `cresmo-grafana` (Grafana v11.x image).
   - Mounts declarative provisioning configs (`docker/monitoring/prometheus.yml`, `docker/monitoring/grafana/provisioning/`).
   - Standard ports: Prometheus on `9090`, Grafana on `3001` (avoiding conflict with Langfuse on `3000`).
2. **`Makefile` Unification:**
   - Updated compose file binding:
     ```makefile
     COMPOSE_FILES := -f docker-compose.langfuse.yml -f docker-compose.monitoring.yml -f docker-compose.yml
     ```
   - Running `make up` activates all three pillars simultaneously: Execution Worker + GenAI Observability (Langfuse) + SRE Observability (Prometheus/Grafana).
   - Running `make down` terminates all containers cleanly.

---

## 3. Consequences & Trade-offs

### Positive
- **Isolated Telemetry Concerns:** Operational time-series metrics (Prometheus) do not pollute the GenAI trace tree (Langfuse), and domain use cases do not depend on external monitoring SDKs.
- **Immediate Detection of Bottlenecks:** Golden Signals immediately expose whether ingestion, local Ollama indexing, or Gemini synthesis is saturating the queue or exhausting rate limits.
- **Fail-Fast Memory Governance:** Process RSS and GC collection metrics verify that ADR-020 memory hygiene holds true during 100+ video batch processing runs.
- **Future-Proof DORA Alignment:** The data contracts for DORA metrics are standardized now in code, ensuring zero architectural rework when remote CI/CD pipelines are activated.

### Negative / Trade-offs
- **Additional Container Footprint:** Running Prometheus and Grafana locally consumes ~250MB additional RAM when `make up` is invoked.
- **Adapter Maintenance:** Adding a new pipeline stage requires instrumenting its duration via `MetricsPort` alongside the existing `TelemetryPort` span.

### Neutral
- The system operates 100% transparently with `NoOpMetricsAdapter` when Docker Compose monitoring containers are not running, ensuring CLI agility during one-off executions.

---

## 4. Alternatives Considered

1. **Overloading `TelemetryPort` with Time-Series Counters:**
   - *Rejected:* Violates the Interface Segregation Principle (ISP). OpenTelemetry tracing deals with hierarchical span trees and contextual logs; Prometheus deals with multi-dimensional floating-point time series. Combining them produces bloated adapters and tight coupling.
2. **Direct Prometheus Client Calls in Use Cases (`prometheus_client.Counter` inside `expand_longitudinal_synchronic.py`):**
   - *Rejected:* Violates Hexagonal Architecture. Domain and application logic must remain pure Python, free of infrastructure frameworks.
3. **Cloud-Only Observability (Datadog, New Relic, GCP Cloud Monitoring):**
   - *Rejected:* Violates the local-first 12-Factor KISS architecture of the project. Developers must be able to inspect real-time metrics locally offline with `make up`.

---

## 5. Domain & Architectural Terminology Updates
The following terms are formally adopted into [`docs/GLOSSARY.md`](../GLOSSARY.md):
- **`MetricsPort`**: Hexagonal port defining contracts for Prometheus time-series counters, histograms, and gauges.
- **`Prometheus Golden Signals`**: SRE operational metrics framework monitoring Latency, Traffic, Errors, and Saturation.
- **`DORA Four Keys`**: DevOps delivery performance metrics tracking Deployment Frequency, Lead Time for Changes, Change Failure Rate, and Time to Restore Service.
- **`PrometheusMetricsAdapter`**: Production infrastructure adapter implementing `MetricsPort` via `prometheus_client`.
