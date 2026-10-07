# ADR-037: Lean Telemetry Topography, Chronological Stage Evaluation Spans, and Zero-Duplication Governance

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-10-07                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Observability & SRE — Domain, Application, Infrastructure |
| **Relates** | ADR-000, ADR-016, ADR-021, ADR-027, ADR-029, ADR-030, ADR-031, ADR-034, ADR-035, ADR-036 |

---

## 1. Context & Architectural Motivation

Operational inspection of trace `d84fc9da5454054101c949405505857c` and ClickHouse storage tables revealed four critical observability defects in Cresmo's telemetry infrastructure:

1. **Homonymous Trace Root Redundancy:**
   - Both the top-level Langfuse Trace entity and its Root OpenTelemetry span shared the exact same name: `cresmo.pipeline.execution`.
   - In distributed systems, a **Trace** represents the holistic business transaction (e.g. `cresmo.synthesis_pipeline`), while a **Root Span** represents the application orchestration unit (e.g. `pipeline.coordinator`). Identical naming creates cognitive clutter in visualization dashboards.

2. **Synthetic Payload Bloat and Alias Duplication:**
   - Input payloads duplicated identical values across alias keys (`channel` vs `channel_name`, `title` vs `content_title`).
   - The serialized JSON string was dumped across 4 redundant attributes: `input.value`, `langfuse.observation.input`, `langfuse.input`, and `langfuse.trace.input`.
   - Static channel and content metadata were repeatedly injected into every child stage span, despite being natively inherited from the root trace context.

3. **The Blind Evaluation Black Hole:**
   - Candidate quality evaluation (`_evaluate_candidate`) executed without a demarcating OpenTelemetry child span.
   - The evaluation duration, criteria checklist, and LLM critique text were invisible in the waterfall timeline.
   - Consequently, judge scores bound to the active stage span appeared in the node header *before* `cresmo.llm.generate`, violating the chronological reality of the feedback loop.

4. **Unrecorded Stage I/O:**
   - Clicking intermediate stage spans (`cresmo.stage.fluid_prose`) in Langfuse showed empty `Input` and `Output` panels, obscuring the textual transformation between cognitive stages.

---

## 2. Banished Anti-Patterns

This ADR formally bans four observability anti-patterns with **zero backward compatibility**:

* **`Homonymous Trace Root Redundancy*`**: Naming the global trace container and the application root span with the exact same identifier.
* **`Payload Alias Duplication*`**: Replicating identical values under alias keys (`channel`/`channel_name`) or multi-key serialized JSON dumps.
* **`Blind Evaluation Black Hole*`**: Executing LLM-as-a-judge candidate audits without a dedicated, time-bounded child span.
* **`Unrecorded Stage I/O*`**: Emitting stage spans without structured domain input (source text stats) and output (synthesized candidate text stats).

---

## 3. Decision: The 4-Tier Lean Telemetry Architecture

We establish a clean, strictly chronological 4-tier telemetry topography:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Tier 1: [Trace] cresmo.synthesis_pipeline (Business Transaction & FinOps)              │
│   └── Tier 1.1: [Span] pipeline.coordinator (Application Orchestration & I/O)          │
│         │                                                                              │
│         └── Tier 2: [Span] cresmo.stage.{stage_name}                                   │
│               │   • Input:  Domain source text payload & word count                    │
│               │   • Output: Approved synthesized candidate & word count                │
│               │                                                                        │
│               ├── Tier 3A: [Generation] cresmo.llm.generate (attempt: N, critique: B)  │
│               │                                                                        │
│               └── Tier 3B: [Span] cresmo.stage.{stage_name}.evaluation (attempt: N)    │
│                     • Chronologically AFTER generation                                 │
│                     • In-Context Scores: {stage_name}.{criterion}                      │
│                     • Output: {"verdict": "PASS", "overall_score": 0.95, "critique": …}│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Pillar 1: Semantic Separation of Trace and Root Span
- **Trace Name:** `cresmo.synthesis_pipeline` (represents the end-to-end synthesis run).
- **Root Span Name:** `pipeline.coordinator` (represents `PipelineCoordinator.execute`).

### Pillar 2: Chronological Stage Evaluation Span (`Tier 3B`)
- Candidate evaluation MUST be wrapped in a dedicated child span: `cresmo.stage.{stage_name}.evaluation`.
- All evaluation scores emitted by `LangfuseJudgeDecorator` or `TelemetryPort.record_score` MUST bind to this span's `observation_id`.
- The evaluation span records:
  - **Attributes:** `judge.attempt`, `judge.stage_name`, `judge.verdict`, `judge.overall_score`.
  - **Input:** Candidate text preview and requested quality criteria.
  - **Output:** Judgment verdict, overall score, and reflection critique.

### Pillar 3: Lean I/O Payloads (Zero-Duplication Governance)
- **Elimination of Aliases:** Payload dictionaries must use canonical DDD identifiers only: `channel_id`, `channel_name`, `content_id`, `content_title`, `batch_id`, `source_type`. All legacy alias keys (`channel`, `title`) are eliminated.
- **Single Source of OTel Ingestion:** Span inputs use `input.value` and `langfuse.observation.input`. Outputs use `output.value` and `langfuse.observation.output`.
- **Elimination of Sub-Span Over-Propagation:** Child stage spans do not re-emit static `channel_name` or `content_title` attributes already present at the root trace level.

---

## 4. Consequences & Migration Guide

* **Positive:**
  - Waterfalls in Langfuse and OpenTelemetry collectors reflect the true causal timeline: candidate generation precedes candidate evaluation.
  - Score badges are visually located inside the evaluation span, directly below generation.
  - ClickHouse storage volume is reduced by eliminating redundant duplicate keys and attributes.
  - Intermediate stages now expose inputs and outputs in the Langfuse inspector.
* **Negative / Breaking:**
  - Zero backward compatibility: Downstream dashboards relying on legacy trace name `cresmo.pipeline.execution` or redundant attributes `langfuse.input.channel` must update queries to use canonical identifiers.
