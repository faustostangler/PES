# ADR-034: Algorithmic (ID-ID) and Cognitive (TXT-TXT) Parity Standard across Telemetry, Observability, and Pipeline Contexts

**Status:** ACCEPTED  
**Date:** 2026-10-03  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-027`](ADR-027-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`ADR-032`](ADR-032-composite-channel-and-content-value-objects.md), [`ADR-033`](ADR-033-composite-value-objects-identity-parity-and-tenant-simplification.md)

---

## 1. Context & Problem Statement

Following the adoption of composite Value Objects in ADR-032 and ADR-033 (`Channel` and `Content`), runtime inspection of the OpenTelemetry adapter (`OpenTelemetryAdapter`), the quarantine protocol (`record_stage_quarantine`), and the pipeline stage execution fabric (`stage_runner.py`) revealed a persistent **cross-dimensional asymmetry (Unpaired Semantic Anti-pattern)** in telemetry attributes, span tags, and observability events:

1. **Unpaired Attribute Emission in Root Spans:**
   In `OpenTelemetryAdapter._build_session_span_attributes`, the root span initially instantiated:
   - `"cresmo.content.id"` (Machine Identifier / Algorithmic)
   - `"cresmo.channel.name"` (Human Display Name / Cognitive)
   
   Meanwhile, their respective orthogonal counterparts:
   - `"cresmo.channel.id"` (Machine Identifier / Algorithmic)
   - `"cresmo.content.title"` (Human Display Name / Cognitive)
   
   were conditionally appended 15 lines later under ad-hoc `if channel_id:` and `if content_title:` guards. Under minimal or raw metadata scenarios (e.g. CLI one-offs, unit tests, un-indexed local texts), the span was emitted with an asymmetric pair (`content.id` + `channel.name`), violating semantic parity.

2. **Asymmetric Langfuse Input Payloads:**
   In `_build_langfuse_input_payload`, channel aliases (`channel` and `channel_name`) were symmetrically guaranteed, while `content_title` was omitted from `input_payload` and `langfuse.input.content_title`. Furthermore, the algorithmic identifiers (`channel_id` and `content_id`) were conditionally copied only if already present in raw metadata, rather than guaranteed from the canonical session identity.

3. **Stage Spans and Quarantine Gaps:**
   In `stage_runner._measure_stage`, child stage spans were opened without diagnostic span attributes, relying solely on metric counters. In `quarantine.py`, `cresmo.channel.id` and `cresmo.content.title` were conditionally omitted if empty rather than falling back deterministically.

---

## 2. Invariants & Definitions

We define two immutable, orthogonal telemetry planes:

### 2.1 Algorithmic Plane (ID - ID Parity)
- **Purpose:** Machine consumption, indexing, cross-service correlation, distributed tracing, and database aggregation.
- **Constituents:**
  - `channel_id`: Platform or tenant channel identifier (e.g., `"UC_1234"`, `"priority_text"`, or slug fallback).
  - `content_id`: Platform or text content identifier (e.g., `"vid_abc123"`, `"text_hash"`).
- **Invariant:** Whenever `content.id` is emitted in any telemetry boundary, `channel.id` **MUST** be emitted simultaneously in the same payload/span/event. Neither may be omitted or conditionally discarded.

### 2.2 Cognitive Plane (TXT - TXT Parity)
- **Purpose:** Human comprehension, SRE dashboarding (Grafana, Datadog), Langfuse UI trace visualization, and non-technical auditing.
- **Constituents:**
  - `channel_name`: Human-readable creator or source channel name (e.g., `"Sandeco"`, `"Text Priority"`).
  - `content_title` (with canonical alias `title`): Human-readable media or article title (e.g., `"Machiavelli and the Modern State"`).
- **Invariant:** Whenever `channel.name` is emitted in any telemetry boundary, `content.title` **MUST** be emitted simultaneously. If an explicit title is unavailable, it must deterministically fallback to `content.id` or the file stem, guaranteeing non-empty representation.

---

## 3. Decision

We establish the **Universal Algorithmic (ID-ID) and Cognitive (TXT-TXT) Parity Standard** across all Cresmo components with **zero backward compatibility**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        UNIVERSAL PARITY MATRIX                         │
├────────────────────────────────────┬───────────────────────────────────┤
│    ALGORITHMIC PAIR (ID - ID)      │     COGNITIVE PAIR (TXT - TXT)    │
│    (For Machines & Aggregation)    │    (For Humans & Observability)   │
├────────────────────────────────────┼───────────────────────────────────┤
│  cresmo.content.id                 │  cresmo.content.title             │
│  cresmo.channel.id                 │  cresmo.channel.name              │
│  langfuse.input.content_id         │  langfuse.input.title             │
│  langfuse.input.channel_id         │  langfuse.input.channel_name      │
│  judge.content_id                  │  (in stage/span metadata)         │
│  judge.channel_id                  │                                   │
│  eval.content_id                   │                                   │
│  eval.channel_id                   │                                   │
└────────────────────────────────────┴───────────────────────────────────┘
```

### 3.1 OpenTelemetry Adapter Unification (`OpenTelemetryAdapter`)
1. In `_build_session_span_attributes`:
   - Resolve `content_id = session_id.content_id` and `channel_id = str(effective_metadata.get("channel_id") or session_id.channel_id).strip()`.
   - Resolve `channel_name = str(effective_metadata.get("channel_name") or effective_metadata.get("channel") or channel_name or session_id.channel_id).strip()`.
   - Resolve `content_title = str(effective_metadata.get("title") or effective_metadata.get("content_title") or content_id).strip()`.
   - Instantiate both pairs atomically and unconditionally in the initial dictionary:
     ```python
     # 1. Algorithmic Pair (ID - ID Parity)
     "cresmo.content.id": content_id,
     "cresmo.channel.id": channel_id,

     # 2. Cognitive Pair (TXT - TXT Parity)
     "cresmo.channel.name": channel_name,
     "cresmo.content.title": content_title,
     ```
2. In `_build_langfuse_input_payload`:
   - Enforce symmetrical emission of `content_id` and `channel_id` in `langfuse.input` attributes and payload.
   - Symmetrically populate both `title` and `content_title` aliases, as well as `channel` and `channel_name` aliases.
3. In `record_judge_evaluation` and `record_session_coherence`:
   - Include `judge.channel_id` alongside `judge.content_id`.
   - Include `eval.channel_id` alongside `eval.content_id`.

### 3.2 Quarantine Protocol Unification (`quarantine.py`)
1. In `record_stage_quarantine`:
   - Symmetrically set:
     - `span.set_attribute("cresmo.content.id", content_id.value)`
     - `span.set_attribute("cresmo.channel.id", effective_channel_id)`
     - `span.set_attribute("cresmo.channel.name", channel_name_string)`
     - `span.set_attribute("cresmo.content.title", effective_content_title)`
   - Guarantee `effective_channel_id` falls back to `channel_name_string` and `effective_content_title` falls back to `content_id.value`.

### 3.3 Stage Runner Diagnostics (`stage_runner.py`)
1. Pass stage attributes containing both pairs (`channel_id`, `content_id`, `channel_name`, `content_title`) to `start_stage_span`.
2. Ensure `run_stage` accepts `content_title: str = ""` to preserve parity through helper layers.

---

## 4. Consequences

### Positive:
- **Zero Ambiguity:** Dashboards, traces, and metrics are completely symmetrical; searching by channel or content in Grafana Loki, OpenTelemetry APM, or Langfuse yields predictable results.
- **Elimination of Broken Telemetry:** Spans will never possess half a pair (e.g. ID without paired ID, or Name without paired Title).
- **Strict Compliance with Akita Method & Stangler Doctor:** Domain purity is mirrored into infrastructural telemetry with fail-fast determinism.

### Negative / Trade-offs:
- **Breaking Changes:** Any downstream test or observer expecting `cresmo.channel.id` or `cresmo.content.title` to be absent under empty metadata must be updated to expect the canonical fallback values.
