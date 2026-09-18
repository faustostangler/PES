# ADR-011: Zero Hardcoded Tunables, Self-Healing Output Validation, and Unified Inference Observability

**Status:** APPROVED  
**Date:** 2026-09-17  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Related ADRs:** [ADR-001](ADR-001-cresmo-modular-monolith-strangling.md), [ADR-005](ADR-005-multi-role-12factor-container-architecture.md), [ADR-010](ADR-010-zero-legacy-shims-and-streaming-first-unification.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context & Identified Anti-Patterns

During the ongoing evolution of the Cresmo domain and pipeline orchestration, four structural anti-patterns were identified:

### 1.1 Anti-Pattern: Hardcoded Prompts in Application/Adapter Logic
* **Definition:** Defining raw prompt text, prompt templates, or multi-line fallback prompt strings directly inside Python source files (`.py`) rather than centralized resource files (`prompts.json`).
* **Consequence:** Violates the Single Source of Truth (SSOT) principle established in ADR-001. Prompts cannot be tuned or audited independently of code deployment, leading to drift between the external configuration and embedded fallbacks.

### 1.2 Anti-Pattern: Scattered Magic Numbers & Operational Tunables
* **Definition:** Hardcoding inference parameters—such as sampling temperatures (`temperature=0.2`), token ceilings, target generation languages, or timeout numbers—directly in use cases or adapter method bodies.
* **Consequence:** Violates 12-Factor App (Factor III: Config). Prevents operators from adjusting inference behavior across environments (local development, CI/CD, batch processing, cloud production) without modifying source code.

### 1.3 Anti-Pattern: Asymmetric or Missing Observability
* **Definition:** Telemetry (e.g. Langfuse generation tracking, token metrics, latency instrumentation) implemented only on cloud providers (Gemini) while leaving local models (Ollama) as opaque black boxes.
* **Consequence:** Degrades Site Reliability Engineering (SRE) visibility, impedes comparative cost/latency benchmarking between local and web inference, and breaks distributed tracing across offline runs.

### 1.4 Anti-Pattern: Passive Acceptance of Malformed Generative Output
* **Definition:** Relying solely on downstream string slicing or accepting generative outputs that include forbidden meta-labels (e.g., `Key concepts:`, `Palavras-chave:`) without automated corrective feedback to the model.
* **Consequence:** Degrades downstream indexing, vector search, and Knowledge Vault cleanliness.

---

## 2. Decision

We establish four binding architectural standards:

### 2.1 Centralized Operational Tunables via Pydantic (`config.py`)
1. All inference parameters, default temperatures, and target languages must be defined within `CresmoSettings` in `src/cresmo/infrastructure/config.py`:
   - `language: str = Field(default="Português do Brasil", validation_alias=AliasChoices("language", "CRESMO_LANGUAGE"))`
   - `llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0, validation_alias=AliasChoices("llm_temperature", "CRESMO_LLM_TEMPERATURE"))`
   - `raw_index_temperature: float = Field(default=0.2, ge=0.0, le=2.0, validation_alias=AliasChoices("raw_index_temperature", "CRESMO_RAW_INDEX_TEMPERATURE"))`
2. **Dependency Injection:** Use cases and Adapters must accept these tunables via their constructors (`__init__`) and pass them explicitly. No magic numbers may exist in method bodies.

### 2.2 Zero Hardcoded Prompts in Python Code
1. All prompt tasks, templates, and system instructions must live exclusively in `src/cresmo/infrastructure/resources/prompts.json`.
2. Python adapters (`JsonPromptProvider`) must only perform safe string formatting (`_safe_format`) using keys present in the JSON catalog, never providing multi-line prompt string fallbacks in code.

### 2.3 Unified Langfuse Telemetry Across All Providers (Web & Local)
1. Both `GeminiLLMAdapter` and `OllamaLLMAdapter` must implement Langfuse observability via `@observe(as_type="generation")`.
2. The `LLMTransformationPort.transform` contract uniformly accepts telemetry metadata:
   - `trace_id: str | None = None`
   - `session_id: str | None = None`
   - `user_id: str | None = None`
3. Local Ollama responses must map `prompt_eval_count` (input tokens), `eval_count` (output tokens), and execution durations into Langfuse generation spans.
4. The Presentation Composition Root (`composition.py`) must inject the configured `Langfuse` client into both adapters.

### 2.4 Self-Healing Verification & Rewrite Loops
1. When a use case imposes strict formatting constraints (e.g. `raw_index` requiring Line 1 to be strictly comma-separated concepts without labels like `Key concepts:`):
   - The use case must validate the output against forbidden framing regexes.
   - If invalid, the use case initiates a bounded `while` loop requesting a corrective rewrite from the model (`max_rewrites = 3`).
   - Defensive sanitation is executed as a final guarantee before persisting into vault and catalog files.

---

## 3. Consequences & Impact

### Positive
1. **12-Factor Compliance:** Complete environment configuration via `.env` variables without touching codebase logic.
2. **Single Source of Truth:** Prompts are decoupled from runtime code; language and temperature are globally governable.
3. **Observability Parity:** Complete visibility into cost, latency, and tokens whether running 100% offline with local Ollama or online with Google Gemini.
4. **Data Quality Assurance:** Self-healing retry loops eliminate structural formatting anomalies before reaching the Markdown knowledge lake.

### Negative / Trade-offs
- Slight latency penalty during initial model formatting errors when triggering rewrite loops. Mitigated by bounding retries to `max_rewrites = 3` and refining system instructions upfront.
