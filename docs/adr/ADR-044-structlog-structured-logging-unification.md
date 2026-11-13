# ADR-044: Structlog Structured Logging Unification and Stdlib Logging Elimination

**Status:** ACCEPTED (SUPERSEDES [`ADR-025`](ADR-025-grafana-loki-structured-log-aggregation.md) in part)  
**Date:** 2026-10-20  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md), [`CONTEXT.md`](../../CONTEXT.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-003`](ADR-003-pes-production-architecture.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-023`](ADR-023-prometheus-sre-golden-signals-and-dora-metrics-platform.md), [`ADR-025`](ADR-025-grafana-loki-structured-log-aggregation.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-035`](ADR-035-atomic-work-item-traces-and-sota-kiss-batch-correlation.md), [`ADR-037`](ADR-037-lean-telemetry-topography-and-chronological-evaluation.md)

---

## 1. Context & Architectural Motivation

In ADR-025, Grafana Loki structured log aggregation was introduced into Cresmo using standard library `logging` and `python-json-logger`. At the time, `structlog` was deferred (Alternative B) to minimize blast radius during the initial Loki rollout.

However, as codified in the **Doctor Stangler Technology Stack Reference** (`references/technology_stack_reference.md`, Layer 8: CLI, Observability & Telemetry):
```
| **Structured Logging** | **structlog** | JSON-formatted contextual logs carrying trace IDs and correlation context. |
```

Continuing to use stdlib `logging` presents several acute architectural liabilities:
1. **Unstructured String Interpolation**: `logger.info("msg %s", val)` encourages formatting strings instead of binding structured contextual attributes (`logger.info("msg", content_id=val)`).
2. **Context Bleed and Thread Locality**: stdlib `logging.LoggerAdapter` lacks modern async-safe, contextvars-aware context binding, causing trace and session attributes to decouple during async concurrency.
3. **Dual Telemetry Paradigms**: Developers must juggle stdlib `logging` formatting conventions alongside OpenTelemetry semantic conventions, violating the SOTA-KISS Single Source of Truth canon.
4. **Architectural Drift**: Having `technology_stack_reference.md` mandate `structlog` while code actively relied on stdlib `logging` violated the repository's strict unification standard.

---

## 2. Decision

We deprecate stdlib `logging` across the entire active Cresmo ecosystem and standardize on **`structlog`** as the universal structured logging engine.

### 2.1 Centralized Pipeline Configuration (`src/cresmo/infrastructure/logging_config.py`)
- Standardize `configure_logging(level, fmt)` using native `structlog.configure()`.
- Pipeline processors:
  * `structlog.contextvars.merge_contextvars`: Contextual binding across async tasks.
  * `structlog.stdlib.add_log_level`: Canonical level naming (`info`, `warning`, `error`).
  * `structlog.processors.TimeStamper(fmt="iso")`: ISO-8601 timestamps for Loki ingestion.
  * `CresmoOTelTraceCorrelationProcessor`: Injects `otelTraceID`, `otelSpanID`, and `session_id` into `event_dict` from active OpenTelemetry spans.
  * `structlog.processors.StackInfoRenderer()` & `structlog.processors.format_exc_info`.
  * Production (`fmt="json"`): `structlog.processors.JSONRenderer()`.
  * Development (`fmt="text"`): `structlog.dev.ConsoleRenderer()`.
- Route stdlib logging through `structlog.stdlib.ProcessorFormatter` so third-party dependencies (`httpx`, `google_genai`, `urllib3`) continue to emit formatted logs to stdout without dual handlers.

### 2.2 Call-Site Standardization (`src/cresmo/`)
- Replace `import logging` and `logging.getLogger(__name__)` with:
  ```python
  import structlog

  logger = structlog.get_logger(__name__)
  ```
- Eliminate legacy `%s` string formatting in favor of structured keyword arguments:
  ```python
  # Before
  logger.info("Processed video %s with status %s", content_id, status)

  # After
  logger.info("Video processed", content_id=content_id, status=status)
  ```
- Domain layer remains completely pure (zero logging imports).

---

## 3. Consequences

### Positive
- **Native Contextual Binding**: Contextual data (`batch_id`, `channel_name`, `content_id`) can be bound once via `structlog.contextvars.bind_contextvars()` and automatically emitted in all subsequent log entries.
- **Trace-Log-Metric Parity**: Seamless correlation between OpenTelemetry trace IDs and Grafana Loki log lines without manual filter hacks.
- **Clean Alignment**: Fulfills `technology_stack_reference.md` Layer 8 mandate with zero architectural ambiguity.

### Negative / Neutral
- All existing `src/cresmo/` call-sites must be updated to use `structlog.get_logger(__name__)`.
