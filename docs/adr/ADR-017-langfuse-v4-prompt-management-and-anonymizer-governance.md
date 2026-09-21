# ADR-017: Langfuse v4 Observations-First Telemetry, Resilient Prompt Management, and Anonymizer Governance

**Status:** PROPOSED  
**Date:** 2026-09-21  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, 12-Factor App, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-003`](ADR-003-pes-production-architecture.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md)

---

## 1. Context & Architectural Forces

In Cresmo's Hexagonal Modular Monolith, audio and video transcripts are synthesized through a 7-stage incremental pipeline ([ADR-007](ADR-007-pipeline-template-method-dry.md)). Observability was standardized in [ADR-016](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md) with OpenTelemetry semantic conventions, session replays (`content:{channel}:{content_id}`), and preliminary clinical scores (`judge_friction`, `session_coherence`).

### 1.1 Identified Architectural Deficits & Drivers

1. **Langfuse v4 Observations-First Evolution:**
   PES upgraded dependencies to `langfuse >= 4.15.2`. In Python SDK v4, Langfuse transitioned to an **observations-first data model** where correlating attributes propagate via `propagate_attributes()`, and custom spans must conform to smart default span filtering (`should_export_span`). In the existing adapters ([`gemini_adapter.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/infrastructure/adapters/gemini_adapter.py) and [`ollama_llm_adapter.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/infrastructure/adapters/ollama_llm_adapter.py)), legacy calls to `self._langfuse.update_current_generation(...)` fail silently inside catch-all exception blocks, preventing rich metadata and generation tokens from linking cleanly to traces.
2. **Span Pruning Vulnerability:**
   Langfuse v4 default span filtering drops non-GenAI OpenTelemetry spans unless created by `langfuse-sdk` or containing `gen_ai.*` attributes. Pipeline orchestrator spans (`cresmo.pipeline.execution`, `cresmo.stage.*`) risk being omitted from Langfuse trace trees if `should_export_span` is not configured explicitly.
3. **Hardcoded Prompt Templates (Lack of Centralized Governance):**
   All LLM prompts are currently static JSON files ([`prompts.json`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/infrastructure/resources/prompts.json)) and local Markdown skill files. Modifying prompts, adjusting temperature or model configs, or performing A/B tests across YouTube channels requires committing code, running test suites, and rebuilding Docker containers. Furthermore, generations in Langfuse are not linked to prompt template versions, leaving the Langfuse **Prompt Metrics** tab empty.
4. **Absence of a Reusable Anonymizer Port (LGPD / Security Risk):**
   Raw transcripts and HTTP metadata may inadvertently capture personally identifiable information (PII) such as presenter emails, names, or authorization headers/cookies. Currently, no sanitization layer exists. Anonymization must not be tightly coupled to Langfuse; it must exist as an independent, hexagonal **`AnonymizerPort`** usable across telemetry, database persistence, log sinks, and future bounded contexts.
5. **Preparedness for Future Datasets and CI/CD Quality Gating:**
   While golden benchmark datasets and CI/CD pipelines are slated for future implementation, the application architecture currently lacks an abstract contract for offline experiment execution (`dataset.run_experiment`) and multidimensional evaluation rubrics (`faithfulness`, `wikilink_density`, `concept_preservation`).

---

## 2. Decision

We will implement **Langfuse v4 Observations-First Telemetry**, a resilient **`LangfusePromptProvider`** with guaranteed local availability fallback, a decoupled **`AnonymizerPort`**, and a formal **Evaluation & Score Schema** in Cresmo.

### 2.1 Decoupled Anonymization Governance (`AnonymizerPort`)
We treat data privacy and LGPD compliance as a first-class architectural concern, independent of telemetry backends:
1. **Port Definition (`src/cresmo/application/ports.py`):**
   - `AnonymizerPort(ABC)` defines contracts for string masking (`mask_text`), structured dictionary sanitization (`mask_mapping`), and OpenTelemetry span patching (`mask_span_attributes`).
2. **Infrastructure Adapter (`src/cresmo/infrastructure/adapters/anonymizer_adapter.py`):**
   - `RegexAnonymizerAdapter`: Implements `AnonymizerPort` using compiled high-performance regex patterns to redact emails, phone numbers, bearer tokens, API keys, and cookie headers.
   - Deployed into Langfuse's export hook `mask_otel_spans` in [composition.py](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/presentation/composition.py), ensuring data is scrubbed at the memory boundary *before* leaving the process.
   - Reusable across any future use case or bounded context.

### 2.2 Resilient Prompt Management (`LangfusePromptProvider`)
1. **Hexagonal Contract Fulfillment:**
   - Implement `LangfusePromptProvider(PromptProviderPort)` in `src/cresmo/infrastructure/adapters/prompt_provider.py`.
2. **Guaranteed 100% Availability Pattern (Offline Resilience):**
   - Conforms strictly to [ADR-014](ADR-014-active-preflight-probes-and-fail-fast-observability.md). The provider wraps an injected fallback `JsonPromptProvider`.
   - When Langfuse is reachable:
     ```python
     prompt = self._langfuse.get_prompt(
         name=prompt_name,
         label=self._label,
         fallback=fallback_template,
     )
     ```
   - When Langfuse is offline, unreachable, or in test environments:
     Degrades immediately to `JsonPromptProvider`, guaranteeing zero network hangs or execution failures.
3. **Prompt-to-Trace Linking:**
   - LLM generation calls receive the resolved prompt reference, automatically populating the Langfuse **Prompt Metrics** tab (median latency, token usage, cost, and eval scores per version).

### 2.3 Observations-First Telemetry Alignment (Langfuse v4)
1. **Explicit Span Filtering Allowlist:**
   - In `resolve_langfuse_client` ([`composition.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/presentation/composition.py)), configure `should_export_span`:
     ```python
     def should_export_cresmo_span(span) -> bool:
         if is_default_export_span(span):
             return True
         scope = getattr(span, "instrumentation_scope", None)
         return scope is not None and scope.name.startswith("cresmo.")
     ```
   - Prevents Langfuse v4 from dropping pipeline root and stage spans while keeping unwanted third-party noise filtered.
2. **Attribute Propagation (`propagate_attributes`):**
   - Update `OpenTelemetryAdapter` to leverage Langfuse v4 `propagate_attributes()`, ensuring `session_id`, `user_id`, `tenant_id`, and `tags` cleanly attach to all observations in the trace hierarchy.
3. **High-Signal Root Input/Output:**
   - Decorate the root span (`cresmo.pipeline.execution`) with human-readable, concise input summary (channel, title, excerpt) and output summary (note count, MOCs, dedup count) conforming to Langfuse tracing best practices.

### 2.4 Multidimensional Evaluation Strategy & Datasets Readiness
1. **Score Rubrics Definition:**
   - `judge_friction` (Stage 1): Ratio of retries ($\frac{\text{iterations}-1}{\text{max\_iterations}}$) in $[0.0, 1.0]$.
   - `faithfulness` (Stage 2/3): Numeric $[0.0, 1.0]$ evaluating whether the narrative compendium invented facts absent from raw transcripts (Target $\ge 0.85$).
   - `wikilink_density` (Stage 5): Numeric $[0.0, 1.0]$ evaluating graph connectivity in generated atomic notes.
   - `session_coherence` (Root/Stage 6): Holistic retention score between raw concepts and atomic notes.
2. **Datasets & CI/CD Future Protocol:**
   - Formalize the structure for future dataset curation (`cresmo-golden-corpus`) and offline experiment evaluation via `dataset.run_experiment()`, ready to be wired into CI/CD workflows when established.

---

## 3. Bounded Context & Hexagonal Architecture Layers

Strict dependency rules are maintained:
```
┌────────────────────────────────────────────────────────┐
│ Domain (cresmo/domain)                                  │
│ - Value Objects: PipelineSessionId, ChannelTenantId,   │
│   ScoreName, EvaluationVerdict                         │
│ - Zero framework or external SDK dependencies          │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│ Application (cresmo/application)                       │
│ - Ports (ABCs): TelemetryPort, PromptProviderPort,     │
│   AnonymizerPort, LLMTransformationPort                │
│ - Use Cases: Pure orchestration, no I/O details        │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│ Infrastructure (cresmo/infrastructure/adapters)         │
│ - OpenTelemetryAdapter (implements TelemetryPort)      │
│ - LangfusePromptProvider (implements PromptProviderPort│
│ - RegexAnonymizerAdapter (implements AnonymizerPort)   │
│ - GeminiLLMAdapter, OllamaLLMAdapter                   │
│ Presentation (cresmo/presentation/composition.py)      │
│ - Injects mask_otel_spans, configures should_export_span│
└────────────────────────────────────────────────────────┘
```

---

## 4. Consequences & Trade-offs

### Positive
1. **Dynamic Prompt Iteration Without Deployment:** Prompts can be tuned, A/B tested, and rolled back in Langfuse without redeploying code.
2. **100% Availability & Zero Regressions:** Local JSON fallbacks guarantee that pipeline executions succeed even when Langfuse Cloud or local instances are offline.
3. **Universal Data Anonymization:** `AnonymizerPort` protects PII and sensitive tokens across telemetry and application boundaries, ensuring LGPD compliance.
4. **Accurate Generation Metrics:** Replacing broken `update_current_generation` calls with native v4 observation context enables exact token, latency, and cost tracking per prompt version.
5. **Future-Proof CI/CD Hook:** Dataset experiment architecture is established without blocking immediate pipeline operations.

### Negative & Mitigations
- **Network Overhead on Initial Prompt Fetch:** Mitigated by Langfuse SDK's built-in client-side cache and startup pre-warming.
- **Masking Performance:** Regex-based sanitization in `mask_otel_spans` could introduce CPU overhead. Mitigated by using pre-compiled regex patterns executed asynchronously on the OpenTelemetry batch worker thread.

---

## 5. Langfuse Ingestion Strategy & Compliance Gate

- **Trace Taxonomy:**
  - `trace_id`: Deterministically propagated via OpenTelemetry tracer.
  - `session_id`: `content:{channel}:{content_id}`.
  - `user_id`: `channel:{channel}` or identified OAuth subject.
  - `tags`: `[channel_name, "cresmo:v2", f"provider:{provider}"]`.
- **Span Hierarchy:**
  `cresmo.pipeline.execution` (Root) $\rightarrow$ `cresmo.stage.*` (Child Spans) $\rightarrow$ `cresmo.llm.generation` (Observation generations).
- **Prompt Tracking:**
  Each generation observation links its active `prompt_name` and `prompt_version`.
- **Data Protection:**
  All span attributes pass through `cresmo_mask_otel_spans` before network dispatch.

---

## 6. Alternatives Considered

1. **Alternative A: Keep Prompts Static in JSON and Only Use Langfuse for Traces**  
   *Pros:* Zero changes to prompt loading logic.  
   *Cons:* Prompt iteration requires full release cycles; Prompt Metrics dashboard remains dead; no prompt version correlation with output quality.  
   *Reason for Rejection:* Fails to leverage the primary benefits of an integrated AI engineering platform.

2. **Alternative B: Hard-Code Redaction Directly inside Langfuse Adapter**  
   *Pros:* Fast to write in a single file.  
   *Cons:* Violates Clean Architecture and Single Responsibility Principle; other modules (database logs, exports) cannot reuse the anonymizer.  
   *Reason for Rejection:* Rejected in favor of a first-class `AnonymizerPort`.

---

## 7. Quality Gate & Approval

- [x] Hexagonal Architecture layers strictly respected (Domain $\rightarrow$ Application $\rightarrow$ Infrastructure).
- [x] Zero framework or SDK dependencies in Domain.
- [x] Resilient offline fallback guaranteed (ADR-014 compliant).
- [x] LGPD and PII masking addressed via `AnonymizerPort`.
- [x] Langfuse v4 observations-first model and span filtering addressed.
