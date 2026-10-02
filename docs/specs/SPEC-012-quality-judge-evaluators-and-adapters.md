# SPEC-012: Quality Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry Specification

**Context:** Cresmo Knowledge Synthesis & Evaluation Subsystem  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** ACCEPTED SPECIFICATION  
**Governing ADR:** [`ADR-029`](../adr/ADR-029-unified-quality-judge-port-and-evaluator-adapters.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`SPEC-008`](SPEC-008-metrics-port-and-prometheus-sre-dora.md), [`SPEC-010`](SPEC-010-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`SPEC-011`](SPEC-011-fluid-prose-detranscription-and-gap-filler-decoupling.md)

---

## 1. Domain Entities & Value Objects

In `src/cresmo/domain/value_objects/quality.py`:

### 1.1 `JudgeCriterion` (Enum)
Evaluation criteria across pipeline stages:
- `ORALITY_REMOVAL = "orality_removal"`: Purging of verbal crutches, hesitations, filler words.
- `SEMANTIC_FAITHFULNESS = "semantic_faithfulness"`: Factual fidelity without hallucinations or omitted core arguments.
- `NER_PRESERVATION = "ner_preservation"`: Retention and accurate spelling of named entities, titles, and proper nouns.
- `STRUCTURAL_COMPLIANCE = "structural_compliance"`: Continuous prose markdown compliance without forbidden tables or stray lists.
- `INVENTORY_COHERENCE = "inventory_coherence"`: Integrity and validity of extracted atomic entity inventories.
- `INDEX_SYNTHESIS_QUALITY = "index_synthesis_quality"`: Conceptual density and paratactic accuracy of raw index entries.

### 1.2 `CriterionScore` (Value Object)
- Attributes:
  - `criterion: JudgeCriterion`
  - `score: float` (Invariant: $0.0 \le \text{score} \le 1.0$)
  - `confidence: float | None = None` (Invariant: if provided, $0.0 \le \text{confidence} \le 1.0$)
  - `passed: bool`
  - `reasoning: str = ""`
- Invariant enforcement: Raises `ValueError` if `score` or `confidence` are outside $[0.0, 1.0]$.

### 1.3 `JudgeEvaluation` (Value Object)
- Attributes:
  - `target_stage: str` (e.g. `"fluid_prose"`, `"raw_indexing"`, `"atomic_inventory"`)
  - `passed: bool`
  - `overall_score: float` (Invariant: $0.0 \le \text{overall_score} \le 1.0$)
  - `criteria_scores: tuple[CriterionScore, ...]`
  - `provider: str` (e.g. `"gemini"`, `"ollama"`, `"typesafe"`, `"composite"`)
  - `latency_ms: float = 0.0`
  - `trace_id: str | None = None`
- Helper query: `get_score(criterion: JudgeCriterion) -> CriterionScore | None`.

### 1.4 `EvaluationContext` (Value Object)
- Attributes:
  - `stage_name: str`
  - `raw_text: str`
  - `candidate_text: str`
  - `metadata: dict[str, Any] = field(default_factory=dict)`
  - `trace_id: str | None = None`
  - `required_criteria: tuple[JudgeCriterion, ...] = ()`

---

## 2. Application Layer Port

In `src/cresmo/application/ports/llm_judge_port.py`:

```python
class LlmJudgePort(ABC):
    """Hexagonal Application Port for semantic quality evaluation and LLM-as-a-Judge."""

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against ground-truth context across required criteria."""
```

---

## 3. Infrastructure Adapters

In `src/cresmo/infrastructure/adapters/judges/`:

### 3.1 `GeminiJudgeAdapter`
- Active primary evaluator using Google GenAI SDK (`gemini-3.5-flash-lite`, temperature 0.0).
- Uses batch structured JSON output schema to return all required criteria in a single roundtrip.
- Handles empty/malformed responses gracefully with retry or safe fallback representation.

### 3.2 `OllamaJudgeAdapter`
- Local offline evaluator using Ollama HTTP endpoint (`/api/generate` or `/api/chat`).
- Ensures pipeline evaluation works in hermetic environments without internet connectivity.

### 3.3 `TypeSafeJudgeAdapter`
- Evaluator using TypeSafe AI (System One Jev) decision primitives (`Noul`, `Score`).
- Sends atomic questions in parallel over state `{ "raw": ..., "candidate": ... }`.
- Returns calibrated probabilities and confidence in ~100ms.
- Fully implemented and tested with mock fixtures; kept dormant behind configuration.

### 3.4 `ResilientCompositeJudgeAdapter`
- Implements `LlmJudgePort`. Wraps `primary: LlmJudgePort` and `fallback: LlmJudgePort`.
- Attempts primary evaluation. If primary raises any exception (network timeout, rate limit, quota error, server failure), logs a warning and calls the fallback adapter.

### 3.5 `LangfuseJudgeDecorator`
- Wraps any `LlmJudgePort` instance.
- Delegates evaluation to inner port.
- On receiving `JudgeEvaluation`, iterates over `criteria_scores` and calls:
  `langfuse_client.score(trace_id=eval.trace_id, name=score.criterion.value, value=score.score, comment=score.reasoning)`.
- If `langfuse_client` is None or unavailable, bypasses emission silently without error.

---

## 4. In-Code Judge Purge & Pipeline Hooking

1. **`DiscoverAtomicInventoryUseCase`:**
   - Remove inline prompt loading and `llm_synthesis_port.transform` call.
   - Inject `LlmJudgePort`.
   - Evaluate candidates using `JudgeCriterion.INVENTORY_COHERENCE`.

2. **`LLMTranscriptDistiller`:**
   - Remove inline judge prompts and `parse_judge_boolean` in `extract_summary`, `extract_concepts`, and `extract_synthesis`.
   - Inject `LlmJudgePort`.
   - Evaluate candidates using `JudgeCriterion.INDEX_SYNTHESIS_QUALITY`.

3. **`CresmoPipelineCoordinator` (`coordinator.py`):**
   - Inject `LlmJudgePort`.
   - After `fluid_prose` stage execution:
     - Run `llm_judge.evaluate(context)` with criteria `ORALITY_REMOVAL`, `SEMANTIC_FAITHFULNESS`, `NER_PRESERVATION`, `STRUCTURAL_COMPLIANCE`.
     - Log results; if `settings.judge_blocking=True` and `evaluation.passed=False`, raise `DomainValidationError`.

---

## 5. Acceptance Test Matrix

| Test ID | Component | Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- |
| `TC-JUDGE-001` | `CriterionScore` | Score outside $[0.0, 1.0]$ | `ValueError` raised |
| `TC-JUDGE-002` | `JudgeEvaluation` | Overall score calculated and queries work | `get_score(...)` returns matching criterion |
| `TC-JUDGE-003` | `GeminiJudgeAdapter` | Valid JSON response from Gemini API | Complete `JudgeEvaluation` parsed with all criteria |
| `TC-JUDGE-004` | `OllamaJudgeAdapter` | Valid JSON response from Ollama API | Complete `JudgeEvaluation` parsed |
| `TC-JUDGE-005` | `TypeSafeJudgeAdapter` | Mock TypeSafe API response with Nouls and Scores | Calibrated probabilities mapped to `JudgeEvaluation` |
| `TC-JUDGE-006` | `ResilientCompositeJudgeAdapter` | Primary fails with ConnectionError | Fallback invoked, evaluation returned with fallback provider |
| `TC-JUDGE-007` | `LangfuseJudgeDecorator` | Trace ID present and evaluation succeeds | `langfuse_client.score` called N times for N criteria |
| `TC-JUDGE-008` | `coordinator.py` | Stage 1 `fluid_prose` executes | Quality judge evaluates and emits scores to active trace |
