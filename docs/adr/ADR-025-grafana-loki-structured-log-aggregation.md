# ADR-025: Grafana Loki Structured Log Aggregation for Cresmo Pipeline

| Field       | Value                                         |
|-------------|-----------------------------------------------|
| **Status**  | ACCEPTED                                      |
| **Date**    | 2026-09-29                                    |
| **Authors** | Lead Architect + AI Implementer               |
| **Scope**   | Cresmo Bounded Context — Infrastructure Layer |
| **Relates** | ADR-016, ADR-021, ADR-023                     |

---

## 1. Problem Context

### Forces at Play

The Cresmo observability stack currently covers **two of three** pillars of the Grafana
trifecta:

| Pillar      | Status          | Tool                    |
|-------------|-----------------|-------------------------|
| **Metrics** | ✅ Operational  | Prometheus → Grafana    |
| **Traces**  | ✅ Operational  | OpenTelemetry → Langfuse|
| **Logs**    | ❌ **Missing**  | stdlib `logging` → void |

**Critical gaps identified:**

1. **Log Entropy**: All 13+ modules emit unstructured text logs via `logging.getLogger(__name__)`
   to stdout/stderr. No centralized collection, indexing, or retention exists. Logs vanish
   when containers restart — violating 12-Factor App log-as-event-stream principles.

2. **No Correlation**: Prometheus alerts fire (e.g., `cresmo_pipeline_errors_total` spike),
   but operators cannot pivot from a metric → correlated log lines. Similarly, Langfuse traces
   show LLM latency but cannot surface the `logger.warning()` that preceded a retry.

3. **No Structured Format**: Raw text logs are unparseable by machines. Grep-based debugging
   on production containers is fragile, slow, and requires SSH access.

4. **Missing from stangler-doctor §7**: The Doctor Stangler Method explicitly mandates
   "Grafana Loki: Log aggregation for Kubernetes" in the Observability Stack (SKILL.md L703).

### Bounded Context

This decision affects only the **Infrastructure Layer** of the Cresmo bounded context.
The Domain and Application layers remain untouched — logging calls (`logger.info()`,
`logger.warning()`, etc.) continue to use stdlib semantics. The structured formatting
and collection happen entirely at infrastructure boundaries.

### Ubiquitous Language (from `docs/GLOSSARY.md`)

- **Golden Signals**: Latency, Traffic, Errors, Saturation (Prometheus)
- **Pipeline Session**: Root telemetry span correlating all stage child spans
- **Stage Span**: Child telemetry span demarcating a discrete pipeline stage
- **Structured Log Record**: JSON-formatted log event with trace correlation metadata

---

## 2. Decision

**We will** introduce Grafana Loki as the centralized log aggregation backend, emitting
structured JSON logs from the Python application via `python-json-logger`, collected by
Promtail from Docker container stdout, and queryable in Grafana alongside Prometheus
metrics — **because** this completes the observability trifecta with zero application
architecture changes, maintains 12-Factor log-as-event-stream compliance, and enables
metric→log and trace→log correlation using shared `trace_id` and `session_id` fields.

### SOTA-KISS Design Principles

| Principle | Application |
|-----------|-------------|
| **KISS**  | Zero new Python dependencies beyond `python-json-logger`. No log file rotation, no sidecar agents inside containers, no custom log drivers. Stdout-only. |
| **SOTA**  | Structured JSON with OpenTelemetry trace correlation fields. Grafana Loki label-based indexing. LogQL for operational queries. Promtail pipeline stages for field extraction. |
| **12-Factor** | Logs emitted as JSON event streams to stdout (Factor XI). No application-managed log files. |

---

## 3. Consequences

### Positive

- **Metric→Log correlation**: Grafana panel drill-down from Prometheus alert to correlated
  Loki log lines via shared labels (`channel_name`, `stage`, `content_id`).
- **Trace→Log correlation**: `trace_id` embedded in every structured log record enables
  Grafana Explore split-view between Langfuse traces and Loki logs.
- **Centralized retention**: Loki stores logs with configurable retention (default 744h/31d),
  surviving container restarts and redeployments.
- **Zero Domain pollution**: Domain and Application layers unchanged. Only Infrastructure
  `logging_config.py` and Docker Compose are modified.
- **Unified Grafana**: Single dashboard combining Golden Signals metrics + correlated logs.

### Negative

- **Resource overhead**: Loki + Promtail add ~150-300MB RAM to the monitoring stack.
  Acceptable for the self-hosted single-node deployment.
- **New dependency**: `python-json-logger` added to `pyproject.toml` (lightweight, well-maintained).
- **Log volume**: Structured JSON logs are ~2-3x larger than plain text. Mitigated by Loki's
  native compression and label-based chunking.

### Neutral

- **No breaking changes**: Existing `logger.info()` / `logger.warning()` calls continue
  to work identically. The formatter change is transparent to all callers.

---

## 4. Alternatives Considered

### Alternative A: Docker Loki Log Driver

**Approach**: Configure Docker daemon with `--log-driver=loki` to ship container logs
directly to Loki without Promtail.

**Pros**: Zero application changes. No Promtail container.
**Cons**: Requires Docker daemon reconfiguration (breaks other containers), no structured
field extraction, no `trace_id` correlation, no multi-line log handling. Rejected because
it provides no structured metadata and requires system-wide Docker daemon changes.

### Alternative B: structlog

**Approach**: Replace stdlib `logging` with `structlog` for native structured logging.

**Pros**: More Pythonic structured logging, native context binding.
**Cons**: Requires modifying every `logger = logging.getLogger(__name__)` call across 13+
modules. High blast radius, high regression risk. Rejected in favor of `python-json-logger`
which works as a drop-in `Formatter` on the existing stdlib `logging.Handler` — zero call-site
changes.

### Alternative C: Fluentd / Fluent Bit

**Approach**: Use Fluent Bit as the log collector instead of Promtail.

**Pros**: More general-purpose, supports multiple outputs.
**Cons**: Heavier configuration, not native to Grafana ecosystem, requires separate
dashboard integration. Rejected because Promtail is purpose-built for Loki with native
label extraction and minimal configuration.

---

## 5. Domain Model Impact

### New Value Objects / Types

None. Logging is an infrastructure concern — no domain model changes.

### New / Modified Ports

None. The existing `TelemetryPort` remains unchanged. Logging configuration is a
cross-cutting infrastructure concern wired at the composition root.

### New Infrastructure Adapters

| Adapter | Location | Responsibility |
|---------|----------|----------------|
| `logging_config.py` | `src/cresmo/infrastructure/logging_config.py` | Centralized `dictConfig` with JSON formatter, trace correlation filter, and Loki-compatible field injection |

### Modified Files

| File | Change |
|------|--------|
| `pyproject.toml` | Add `python-json-logger>=3.3.0` dependency |
| `docker-compose.monitoring.yml` | Add `cresmo-loki` and `cresmo-promtail` services |
| `docker/monitoring/promtail.yml` | Promtail scrape config for Docker container logs |
| `docker/monitoring/loki.yml` | Loki storage and retention config |
| `docker/monitoring/grafana/provisioning/datasources/loki.yml` | Grafana Loki datasource auto-provisioning |
| `docker/pes-cresmo.service` | Already includes monitoring compose — no change needed |
| `src/cresmo/presentation/cli.py` | Call `configure_logging()` at entrypoint |
| `src/cresmo/infrastructure/config.py` | Add `log_level`, `log_format` settings |
| `.env.example` | Add `LOG_LEVEL`, `LOG_FORMAT` entries |

---

## 6. Observability Plan

| Signal | Instrument | Label/Field |
|--------|------------|-------------|
| Log ingestion rate | Loki internal metrics | `job=cresmo` |
| Log errors | Loki `{level="ERROR"}` | `module`, `stage`, `content_id` |
| Trace correlation | JSON field `otelTraceID` | Links to Langfuse trace |
| Session correlation | JSON field `session_id` | Links to pipeline session |

---

## 7. LGPD / Security Assessment

- **PII in logs**: The existing `RegexAnonymizerAdapter` (ADR-017) masks PII in telemetry
  span attributes. Log messages may contain content_ids and channel names (public data),
  but never user credentials or personal data. The `python-json-logger` formatter does not
  add any PII fields.
- **Loki access**: Loki endpoint is bound to `127.0.0.1` — not exposed externally.
  Grafana access requires authentication.

---

## 8. ADR Quality Gate Checklist

- [x] Hexagonal Architecture layers respected
- [x] No framework dependencies in Domain layer
- [x] Domain model uses Value Objects — no Primitive Obsession
- [x] Entities enforce invariants at instantiation
- [x] Domain models are separate from persistence models
- [x] Test strategy defined (see Implementation Plan Phase 2)
- [x] Observability plan included (§6)
- [x] LGPD/Security implications assessed (§7)
- [x] Ubiquitous Language terms added (Structured Log Record)
- [x] Alternatives considered and rejection rationale documented (§4)
- [x] No cross-context boundary violations
- [x] No LLM interaction — Langfuse Ingestion Strategy not required
