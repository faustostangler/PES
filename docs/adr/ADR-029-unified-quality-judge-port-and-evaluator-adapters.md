# ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters with Langfuse Telemetry

**Status:** ACCEPTED  
**Date:** 2026-10-01  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md), [`ADR-017`](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md), [`ADR-024`](ADR-024-iterative-llm-as-a-judge-atomic-inventory-discovery.md), [`ADR-027`](ADR-027-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md)

---

## 1. Context & Architectural Motivation

In the current Cresmo Knowledge Synthesis Engine, quality assessment and semantic validation are scattered across disparate use cases and helper services through ad-hoc "in-the-code" LLM invocations:

1. **Scattered In-Code Evaluators:**
   - **Atomic Inventory Discovery:** In [`src/cresmo/application/use_cases/discover_atomic_inventory.py`](../../src/cresmo/application/use_cases/discover_atomic_inventory.py#L202-L217), the use case directly compiles prompt `PromptKey.JUDGE_ATOMIC_INVENTORY`, invokes `self.llm_synthesis_port.transform(...)`, and parses a boolean output with `parse_judge_boolean`.
   - **Catalog Conceptual Indexing:** In [`src/cresmo/application/use_cases/indexing/distiller.py`](../../src/cresmo/application/use_cases/indexing/distiller.py#L116-L124), three separate judge calls (`judge_raw_index_summary`, `judge_raw_index_concepts`, `judge_raw_index_synthesis`) are executed via `self.llm_indexing_port.transform(...)` and parsed as booleans.
2. **Missing Stage 1 (`fluid_prose`) Quality Gate:**
   - In [ADR-028](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), Stage 1 (`transform_fluid_prose`) was decoupled as the primary linguistic normalization stage. However, it currently lacks an automated evaluation gate to verify whether oralities were purged, factual claims preserved, and Named Entities correctly spelled.
3. **Impedance of Generative Models as Evaluators vs. Decision Models:**
   - Traditional LLM-as-a-judge patterns use generative chat models (e.g. Gemini) that generate autoregressive free-form text or JSON fences, suffering from token output latencies (1.5s–4s), schema parsing fragility, and uncalibrated confidence (overconfidence bias).
   - Emerging **System One Decision Models** (such as **Jev** from TypeSafe AI) provide non-autoregressive, calibrated probabilistic decisions (`Noul`, `Score`, `Choice`) in ~100ms with speculative parallel question fan-out.
4. **Lack of Resilient Fallback Chain and Telemetry Standardization:**
   - Evaluator failures directly crash or degrade synthesis pipelines without clean provider failover.
   - Evaluator results are not emitted systematically to Langfuse as structured scores (`client.score(...)`), preventing real-time observability, distribution analytics, and A/B prompt comparisons.

---

## 2. Decision

We establish an isolated, hexagonal Quality Evaluation Subsystem governed by a unified port (`LlmJudgePort`), rich domain value objects (`JudgeEvaluation`, `CriterionScore`, `EvaluationContext`), and resilient multi-provider adapters with automatic fallback and direct Langfuse score ingestion.

### 2.1 Domain Layer: Rich Value Objects & Invariants

In `src/cresmo/domain/value_objects/quality.py`, define pure, immutable domain representations:

```
┌───────────────────────────────────────────────────────────┐
│                    EvaluationContext                      │
│ - stage_name: str                                         │
│ - raw_text: str                                           │
│ - candidate_text: str                                     │
│ - metadata: dict[str, Any]                                │
│ - trace_id: str | None                                    │
│ - required_criteria: tuple[JudgeCriterion, ...]           │
└─────────────────────────────┬─────────────────────────────┘
                              │ evaluates into
                              ▼
┌───────────────────────────────────────────────────────────┐
│                     JudgeEvaluation                       │
│ - target_stage: str                                       │
│ - passed: bool                                            │
│ - overall_score: float (0.0 to 1.0)                       │
│ - criteria_scores: tuple[CriterionScore, ...]             │
│ - provider: str                                           │
│ - latency_ms: float                                       │
│ - trace_id: str | None                                    │
└───────────────────────────────────────────────────────────┘
```

1. **`JudgeCriterion` (Enum):**
   - `ORALITY_REMOVAL`: Purging of verbal crutches, hesitations, stutters, conversational filler.
   - `SEMANTIC_FAITHFULNESS`: Factual grounding without fabricated claims or omitted core arguments.
   - `NER_PRESERVATION`: Correct retention and spelling of named entities, titles, and concepts.
   - `STRUCTURAL_COMPLIANCE`: Conformance to continuous prose markdown without stray sections or lists.
   - `INVENTORY_COHERENCE`: Extraction quality for candidate atomic entity inventories.
   - `INDEX_SYNTHESIS_QUALITY`: Paratactic precision and density for raw catalog index entries.

2. **`CriterionScore` (Value Object):**
   - Enforces score $\in [0.0, 1.0]$, optional `confidence` $\in [0.0, 1.0]$, `passed: bool`, and explanatory `reasoning: str`.

3. **`JudgeEvaluation` (Value Object):**
   - Immutable snapshot of an evaluation verdict, calculating composite weighted scores and exposing helper query methods (`get_score(criterion)`).

### 2.2 Application Layer: The Unified Port

In `src/cresmo/application/ports/llm_judge_port.py`:

```python
class LlmJudgePort(ABC):
    """Hexagonal Application Port for semantic quality evaluation and LLM-as-a-Judge."""

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against ground-truth context across required criteria."""
```

### 2.3 Infrastructure Layer: Multi-Provider Adapters & Resilience Chain

In `src/cresmo/infrastructure/adapters/judges/`:

1. **`GeminiJudgeAdapter` (Active Primary):**
   - Evaluates criteria using Google Gemini API (`gemini-3.5-flash-lite` with `temperature=0.0`).
   - Uses chat-native prompt with structured JSON output schema and exponential retry.
2. **`OllamaJudgeAdapter` (Active Fallback):**
   - Evaluates criteria using local Ollama (`qwen2.5:7b`), ensuring hermetic, offline evaluation without external network dependencies.
3. **`TypeSafeJudgeAdapter` (Dormant SOTA Candidate):**
   - Evaluates criteria via TypeSafe AI / Jev (`jev-latest`) using atomic parallel primitives (`Noul`, `Score`).
   - Zero markdown parsing; returns calibrated probabilities and confidence in ~100ms.
   - Fully implemented, verified via unit tests, but kept dormant behind configuration.
4. **`ResilientCompositeJudgeAdapter` (Resilience Chain):**
   - Encapsulates fallback order: `Primary (Gemini) ──► Fallback (Ollama)`.
   - If primary fails (timeout, rate limit, quota error, server error), logs a failover warning and invokes the fallback adapter transparently.
5. **`LangfuseJudgeDecorator` (Telemetry Emission):**
   - Decorates any `LlmJudgePort` adapter.
   - Intercepts `JudgeEvaluation` and immediately transmits `langfuse_client.score(trace_id=..., name=criterion.value, value=score.score, comment=score.reasoning)`.

### 2.4 Purging In-Code Judges & Pipeline Integration

1. **Purge in `DiscoverAtomicInventoryUseCase`:**
   - Remove inline prompt fetching and `llm_synthesis_port.transform` call.
   - Inject `LlmJudgePort` into constructor.
   - Delegate validation to `llm_judge.evaluate(context)`.
2. **Purge in `LLMTranscriptDistiller`:**
   - Remove inline judge prompts and `parse_judge_boolean` in `extract_concepts`, `extract_summary`, and `extract_synthesis`.
   - Inject `LlmJudgePort`.
   - Delegate validation to `llm_judge.evaluate(...)`.
3. **Hook Stage 1 (`fluid_prose`) Quality Gate in `coordinator.py`:**
   - After `self.transform_fluid_prose.execute(raw)`, trigger `self.llm_judge.evaluate(...)` for `fluid_prose` across `ORALITY_REMOVAL`, `SEMANTIC_FAITHFULNESS`, `NER_PRESERVATION`, and `STRUCTURAL_COMPLIANCE`.
   - Emits scores to Langfuse under the active `trace_name="cresmo.pipeline.execution"`.
   - Tunable behavior: `judge_blocking=False` by default (telemetry sentinels / non-blocking warnings), switchable to `judge_blocking=True` via configuration.

---

## 3. Configuration & 12-Factor Settings

In `src/cresmo/infrastructure/config.py`:

```python
# Secrets & Credentials
typesafe_api_key: SecretStr = Field(
    default=SecretStr(""),
    validation_alias=AliasChoices("typesafe_api_key", "TYPESAFE_API_KEY"),
    description="TypeSafe AI API key for System One Jev evaluations.",
)

# Operational Tunables
judge_provider: str = Field(
    default="gemini",
    validation_alias=AliasChoices("judge_provider", "CRESMO_JUDGE_PROVIDER"),
    description="Primary quality judge provider ('gemini', 'typesafe', 'ollama').",
)
judge_fallback_provider: str = Field(
    default="ollama",
    description="Fallback quality judge provider when primary fails.",
)
judge_blocking: bool = Field(
    default=False,
    description="Whether failed quality evaluations raise DomainValidationError or log warning scores.",
)
```

---

## 4. Consequences

### Positive
- **Single Source of Truth for Quality:** Eliminates fragmented, unmaintainable in-code judge snippets across use cases.
- **Provider Agnostic:** Cleanly separates prompt/decision logic from use cases. Swapping Gemini for Jev or Ollama requires zero application code changes.
- **Calibrated Observability:** Every evaluation automatically emits structured scores into Langfuse traces, creating actionable dashboards and enabling data-driven prompt optimization.
- **Hermetic Fallback:** Pipelines survive cloud API outages through local Ollama fallback.

### Negative
- Additional latency if LLM judge runs synchronously on every stage (mitigated by using `gemini-3.5-flash-lite`, and in the future ~100ms Jev fan-out).

### Neutral
- Adds new configuration keys to `.env` (`TYPESAFE_API_KEY`, `CRESMO_JUDGE_PROVIDER`).

---

## 5. Alternatives Considered

1. **Keep Judges In-Line Inside Use Cases:**
   - *Rejected:* Violates Single Responsibility Principle and couples domain use cases to generative text models and parsing heuristics.
2. **Langfuse Cloud Remote Evaluators Only:**
   - *Rejected:* Asynchronous cloud evaluators cannot participate in retry loops within local processing workers or run offline.
3. **Hardcoding TypeSafe as Sole Evaluator Immediately:**
   - *Rejected:* Violates fail-fast resilience principles. We implement TypeSafe with full unit test coverage but maintain Gemini as active default and Ollama as local fallback, deferring primary cutover until early-access credentials and production stability are verified.

---

## 6. Langfuse Ingestion Strategy & Eval Matrix

| Stage | Evaluator Method | Criteria / Score Name | Threshold | Action on Failure |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (`fluid_prose`)** | Gemini / Jev Judge | `orality_removal` | $\ge 0.80$ | Warning log + Langfuse Score (blocking if enabled) |
| **Stage 1 (`fluid_prose`)** | Gemini / Jev Judge | `semantic_faithfulness` | $\ge 0.85$ | Warning log + Langfuse Score (blocking if enabled) |
| **Stage 1 (`fluid_prose`)** | Gemini / Jev Judge | `ner_preservation` | $\ge 0.80$ | Warning log + Langfuse Score (blocking if enabled) |
| **Stage 1 (`fluid_prose`)** | Rule / Regex + Judge | `structural_compliance`| $= 1.0$ | Warning log + Langfuse Score |
| **Stage 2 (`raw_indexing`)**| Gemini / Ollama Judge | `index_synthesis_quality` | $\ge 0.75$ | Corrective rewrite retry loop up to `max_rewrites` |
| **Stage 5 (`atomic_inv`)**  | Gemini / Jev Judge | `inventory_coherence` | $\ge 0.80$ | Discovery retry loop up to `max_rewrites` |

---

## 7. Compliance Verification Checklist

- [x] Hexagonal Architecture layers strictly respected (Domain $\rightarrow$ Application $\rightarrow$ Infrastructure)
- [x] No framework dependencies in Domain layer (`typing` and standard dataclasses only)
- [x] Domain model uses Value Objects (`JudgeEvaluation`, `CriterionScore`, `EvaluationContext`)
- [x] Value objects enforce invariants at instantiation
- [x] Test strategy defined (hermetic unit tests for all 3 adapters + composite fallback)
- [x] Langfuse Ingestion Strategy explicitly defined with score names and thresholds
- [x] Alternatives considered and rejection rationale documented
