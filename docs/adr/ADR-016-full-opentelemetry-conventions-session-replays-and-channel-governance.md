# ADR-016: Full OpenTelemetry Semantic Conventions, Unified Session Replays, and Channel FinOps Governance

**Status:** ACCEPTED  
**Date:** 2026-09-20  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, 12-Factor App)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-003`](ADR-003-pes-production-architecture.md), [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md)

---

## 1. Context & Architectural Forces

In Cresmo's Hexagonal Modular Monolith, raw audio and video transcripts are ingested and transformed through sequential processing stages:
1. `raw_indexing`: Concept extraction, summarization, and iterative format verification (LLM-as-a-judge).
2. `fluid_prose`: Socratic gap-filling and multi-pass narrative expansion.
3. `expansion`: Longitudinal (Braudelian) and synchronic (Axial) contextualization.
4. `inventory`: Discovery of discrete atomic concepts and note taxonomies.
5. `atomic_batch`: Batch synthesis of markdown atomic notes enriched with Obsidian wikilinks.
6. `mocs`: Graph reconciliation and update of Maps of Content.
7. `duplicate_unification`: Graph entity deduplication.

### 1.1 Identified Architectural Deficits
Prior to this decision:
1. **Fragmented Trace Taxonomy:** Each pipeline stage generated disconnected traces or passed stage-specific string sessions (e.g. `raw_index_channel`, `stage2_fluid_prose_channel`). Traces spanning the same content item across stages 1 to 6 were decoupled, rendering the Langfuse **Session Replay** view fragmented and unable to visualize the holistic multi-stage knowledge evolution.
2. **Missing Cost Center (Tenant) Identity:** Use cases did not provide `user_id`. Consequently, the Langfuse **Users** dashboard remained unpopulated, precluding FinOps visibility into token expenditure, model latency, and error distribution per channel.
3. **Improper Langfuse SDK Attribute Binding:** Adapters placed `session_id` and `user_id` inside custom `metadata` dictionaries rather than native trace/span attributes. Furthermore, calls to `update_current_generation` on the raw `Langfuse` client instance triggered silent `AttributeError` exceptions.
4. **Uninstrumented LLM-as-a-Judge Friction:** ADR-013 introduced self-healing iterative rewrite loops (`max_rewrites = 3`), but lacked standardized telemetry measuring the friction ratio (retry frequency) per channel and prompt version.
5. **Lack of Session Coherence Scoring:** The system lacked an automated end-to-end evaluation rubric (EVAL-001) assessing whether the final atomic note graph faithfully retained the conceptual core of the raw transcript.

---

## 2. Decision

We establish **Full OpenTelemetry Semantic Conventions**, a unified **Session/User Taxonomy**, and a Hexagonal **`TelemetryPort`** in Cresmo:

### 2.1 Ubiquitous Identity Taxonomy
1. **Content Session Identity (`session_id`):**
   - Formalized via Value Object `PipelineSessionId`.
   - Ubiquitous format: `content:{channel_name}:{content_id}` (e.g. `content:sandeco:ep042_transformers`).
   - Bounds the entire multi-stage lifecycle of a single transcript into a contiguous OpenTelemetry trace tree and Langfuse Session Replay.
2. **User & Operator Identity (`user_id`):**
   - Formalized via Value Object `UserIdentity`.
   - Supports forward-compatible identity modalities:
     * **Anonymous (`anonymous` / `anon:{token}`):** Unauthenticated executions, local scripts, and public guest sessions.
     * **Identified (`user:{provider}:{subject}`):** Authenticated users via OAuth/OIDC login (e.g. `user:oauth:alice@corp.com`).
     * **Channel Fallback (`channel:{channel_name}`):** Headless background worker pipelines where the channel acts as the acting identity.
   - Conforms to Langfuse Users taxonomy, ensuring that once OAuth login is active, personal user quotas, audit trails, and per-user activity appear directly in the Langfuse Users view.
3. **Channel Cost Center Identity (`channel` / `tenant_id`):**
   - Formalized via Value Object `ChannelTenantId`.
   - Ubiquitous format: `channel:{channel_name}` (e.g. `channel:sandeco`).
   - Represents the primary organizational workspace, media source, and FinOps cost center, tracked as `cresmo.channel`, `cresmo.tenant_id`, and in `langfuse.trace.tags` for cross-dimensional cost analysis.

### 2.2 OpenTelemetry Span Hierarchy & Semantic Conventions
The pipeline coordinates traces via a 3-tier OpenTelemetry hierarchy:
- **Tier 1 — Root Span (`cresmo.pipeline.execution`):**
   - Created at pipeline entry (`_synthesize_transcript`).
   - Sets root attributes required by Langfuse:
     * `langfuse.session.id = PipelineSessionId.value`
     * `langfuse.user.id = UserIdentity.value`
     * `cresmo.content_id = ContentId.value`
     * `cresmo.channel = ChannelTenantId.channel_name`
     * `cresmo.tenant_id = ChannelTenantId.value`
     * `cresmo.user.is_anonymous = UserIdentity.is_anonymous`
     * `cresmo.user.provider = UserIdentity.provider`
     * `cresmo.user.subject = UserIdentity.subject` (if identified)
     * `langfuse.trace.tags = [channel_name, "cresmo:v2", f"auth:{user.provider}"]`
- **Tier 2 — Stage Child Spans (`cresmo.stageN.{stage_name}`):**
  - Created for each pipeline stage (`raw_indexing`, `fill_gaps`, `expansion`, `inventory`, `atomic_synthesis`, `mocs`, `duplicate_unification`).
  - Automatically inherit `session_id` and `user_id` via OpenTelemetry trace context propagation.
- **Tier 3 — Leaf Generation Spans (`cresmo.llm.generation`):**
  - Executed inside LLM adapters (`GeminiLLMAdapter`, `OllamaLLMAdapter`).
  - Standardized against official OpenTelemetry GenAI Semantic Conventions:
    * `gen_ai.system`: `"google"` or `"ollama"`
    * `gen_ai.request.model`: Model variant string
    * `gen_ai.usage.input_tokens`: Input prompt token count
    * `gen_ai.usage.output_tokens`: Candidate completion token count
    * `langfuse.observation.type`: `"generation"`

### 2.3 Hexagonal Port & Adapter Architecture
1. **Port Definition (`src/cresmo/application/ports.py`):**
   - `TelemetryPort(ABC)` defines contracts for session context management, stage span demarcation, judge evaluation recording, and session coherence scoring.
   - Domain layer remains 100% pure, interacting solely via Value Objects (`PipelineSessionId`, `ChannelTenantId`, `JudgeFrictionMetric`).
2. **Adapters (`src/cresmo/infrastructure/adapters/opentelemetry_adapter.py`):**
   - `OpenTelemetryAdapter`: Implements `TelemetryPort` using `opentelemetry.trace` and native Langfuse scoring APIs.
   - `NoOpTelemetryAdapter`: Fallback implementation deployed when the active preflight probe (ADR-014) reports that Langfuse/OTel is offline, guaranteeing zero overhead during disconnected or test execution.

### 2.4 Clinical Metrics & Evaluation (EVAL-001)
1. **LLM-as-a-Judge Friction Telemetry:**
   - On each judge cycle in Stage 1, the pipeline calculates:
     $$\text{friction\_ratio} = \frac{\text{iterations} - 1}{\text{max\_iterations}}$$
   - Recorded as a span event and Langfuse score (`judge_friction`) to pinpoint problematic channels or prompts.
2. **Session Coherence Scoring:**
   - Upon completion of Stage 6, the pipeline evaluates the semantic alignment and wikilink density between Stage 1 concepts and Stage 5 notes, recording a `session_coherence` score on the root session.

---

## 3. Consequences & Trade-offs

### Positive
1. **Complete Session Replay:** Engineers and domain experts can replay the entire multi-stage synthesis of any transcript chronologically within Langfuse, inspecting prompt diffs, token consumption, and latencies.
2. **Turnkey Channel FinOps:** Zero custom frontend required; Langfuse Users view immediately surfaces cost, token volume, and latency aggregated per YouTube/media channel.
3. **Vendor Independence:** Spans conform to CNCF OpenTelemetry standards, allowing seamless routing to Prometheus/Grafana Tempo/Jaeger in addition to Langfuse.
4. **Clinical Quality Feedback:** Friction ratios and session coherence provide objective, quantitative signals for prompt engineering and model selection.

### Negative & Mitigations
- **Context Propagation Overhead:** Managing nested spans across multiple use cases requires passing context cleanly. Mitigated by wrapping stages within Python context managers provided by `TelemetryPort`.
- **Preflight Dependency:** Network failures could trigger retry loops. Mitigated by strictly honoring ADR-014 preflight checks and deploying `NoOpTelemetryAdapter` when unreachable.

---

## 4. Langfuse Ingestion Strategy & Compliance Gate

- **Trace Taxonomy:**
  - `trace_id`: Deterministically derived or generated via OpenTelemetry tracer.
  - `session_id`: `content:{channel}:{content_id}`.
  - `user_id`: `channel:{channel}`.
  - `tags`: `[channel_name, f"provider:{provider}", f"stage:{stage_number}"]`.
- **Span Hierarchy:**
  `cresmo.pipeline.execution` (Root) $\rightarrow$ `cresmo.stageN.*` (Spans) $\rightarrow$ `cresmo.llm.generation` (Generations).
- **Score Schema:**
  - `judge_friction`: Float in $[0.0, 1.0]$ (Lower is better).
  - `session_coherence`: Float in $[0.0, 1.0]$ (Higher is better, threshold $\ge 0.80$).
