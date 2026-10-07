# ADR-036: Clean Telemetry Namespacing & In-Context Observation ID Binding

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-10-07                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Telemetry & Observability — Domain, Application, Infrastructure |
| **Relates** | ADR-000, ADR-016, ADR-021, ADR-027, ADR-029, ADR-030, ADR-031, ADR-035 |

---

## 1. Context & Architectural Motivation

In Cresmo's multi-stage cognitive synthesis pipeline (e.g. `fluid_prose`, `raw_indexing`, `gap_filler`, `atomic_batch`), stages employ automated LLM-as-a-Judge evaluators ([ADR-029](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), [ADR-030](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md)) to score outputs against domain quality criteria (`semantic_faithfulness`, `structural_compliance`, `orality_removal`, `ner_preservation`, etc.).

An operational audit of trace `6b114ae59bf5dbdc38c0f992c1d89f2d` in Langfuse revealed two critical observability smells:

1. **Unbound Trace-Level Scoring (Anti-Pattern):**
   - The telemetry decorator `LangfuseJudgeDecorator` emitted evaluations passing only `trace_id=effective_trace_id` without specifying `observation_id`.
   - In Langfuse, scores without an `observation_id` are anchored globally to the Trace Root header rather than to the specific stage execution span (`cresmo.stage.{stage_name}`).
   - As a consequence, inspecting an individual stage span in the waterfall tree showed zero associated scores, obscuring which phase produced which evaluation.

2. **Flat Global Score Collision (Anti-Pattern):**
   - Common criteria (such as `semantic_faithfulness` and `structural_compliance`) are evaluated across multiple independent pipeline stages (e.g., both in `fluid_prose` and `gap_filler`).
   - Emitting them with naked criterion names (`name="semantic_faithfulness"`) causes metric collision in Langfuse UI dashboards, trace table aggregates, and analytical trend lines, where scores from distinct stages are flattened into a single ambiguous column.

---

## 2. Banished Anti-Patterns

This ADR formally bans two observability anti-patterns codified in [ADR-000](ADR-000-patterns-antipatterns.md):

* **`Unbound Trace-Level Scoring*`**: Emitting stage or sub-operation evaluation scores directly to the root trace without binding them to their emitting OpenTelemetry/Langfuse `observation_id`.
* **`Flat Global Score Collision*`**: Emitting bare criterion names across multiple pipeline stages without stage-prefix namespacing, corrupting metric cardinality and dashboard aggregation.

---

## 3. Decision: The SOTA-KISS Clean Telemetry Standard

We establish a two-pillar Clean Telemetry standard across all stage evaluation and telemetry adapters:

```
+---------------------------------------------------------------------------------------------------+
|                                 SOTA-KISS CLEAN TELEMETRY STANDARD                                |
+---------------------------------------------------------------------------------------------------+
|  1. Metric Namespacing  --> score.name = f"{stage_name}.{criterion.value}"                        |
|                             Example: 'fluid_prose.semantic_faithfulness' vs                       |
|                                      'gap_filler.semantic_faithfulness'                           |
|  2. Observation Binding --> score.observation_id = active_span.span_id (16-char hex string)       |
|                             Binds score directly to 'cresmo.stage.{stage_name}' span drawer       |
+---------------------------------------------------------------------------------------------------+
```

### Pillar 1: Stage-Prefixed Metric Namespacing (`score.name`)
Every evaluation score emitted to telemetry backends (Langfuse, Prometheus, OpenTelemetry Events) MUST be prefixed with the active stage name:
- **Format:** `{stage_name}.{criterion_name}`
- **Examples:**
  - `fluid_prose.orality_removal`
  - `fluid_prose.semantic_faithfulness`
  - `raw_indexing.index_synthesis_quality`
  - `atomic_inventory.inventory_coherence`
- **Benefit:** Independent time-series analytics, stage-specific quality trend charts in Langfuse, and isolated sorting/filtering columns in the trace catalog.

### Pillar 2: Active In-Context Observation ID Binding (`observation_id`)
Every stage evaluation score MUST be bound to the 64-bit hex OpenTelemetry span ID (`016x`) of the active stage span:
- `PipelineStageRunner._evaluate_candidate` extracts the active OpenTelemetry span ID from `trace.get_current_span().get_span_context().span_id`.
- The extracted ID is propagated via `EvaluationContext.observation_id`.
- `LangfuseJudgeDecorator` forwards `observation_id` to `langfuse_client.create_score` / `langfuse_client.score`.
- **Benefit:** In the Langfuse UI tree/waterfall, clicking on `cresmo.stage.{stage_name}` immediately reveals the exact scores and LLM reasoning within that span's inspector drawer, and the trace Scores table provides direct clickable navigation badges to the originating span.

### Pillar 3: Domain `EvaluationContext` Enrichment
The domain value object `EvaluationContext` in `src/cresmo/domain/value_objects/quality.py` is augmented with:
```python
observation_id: str | None = None
```
Maintaining pure domain decoupling (strings only, no framework imports).

### Pillar 4: Graceful Degradation & Non-Blocking Fallback
Telemetry emission must remain strictly non-blocking per ADR-014 and ADR-026:
- If `observation_id` is absent (e.g. running outside an active OpenTelemetry stage context), `LangfuseJudgeDecorator` and `OpenTelemetryAdapter` gracefully omit the parameter without failing.
- Telemetry exceptions during score emission are caught and logged with warning level, never interrupting pipeline processing.

---

## 4. Consequences & Benefits

* **Positive:** Complete in-context visibility in Langfuse UI: scores appear under their exact stage span.
* **Positive:** Zero metric collision across stages sharing criteria (`semantic_faithfulness`, `structural_compliance`).
* **Positive:** Granular quality dashboards per stage in Langfuse Analytics.
* **Positive:** Retains 100% backward compatibility when executed without active distributed tracing contexts.
