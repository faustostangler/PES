# EVAL-001: Cresmo Synthesis Langfuse Telemetry & Eval Rubrics

**Context**: Cresmo Knowledge Synthesis  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION  
**Governing ADR**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  

---

## 1. Clinical Telemetry Plan

Every generative call across the Cresmo pipeline executed through `LLMTransformationPort` must emit structured telemetry to Langfuse.

### 1.1 Trace Taxonomy
- `trace_id`: Deterministically computed as `cresmo-{content_id}` (e.g. `cresmo-dQw4w9WgXcQ`).
- `session_id`: Unique execution run identifier (e.g. `cresmo-run-20260910-180000`).
- `user_id`: Operator or channel identifier.
- `tags`: `["cresmo", category, channel_name, stage_label]`.

### 1.2 Span Hierarchy
```
PipelineRun [Root Trace]
├── Stage_1_RawTranscript [Span]
├── Stage_2_GapFiller [Span]
│   └── expand_pass_1 [Generation]
│   └── expand_pass_2 [Generation]
├── Stage_3_Expander [Span]
│   └── longue_duree_expansion [Generation]
│   └── axial_synchronic_expansion [Generation]
├── Stage_4_Inventory [Span]
│   └── inventory_discovery [Generation]
├── Stage_5_Batch [Span]
│   └── batch_synthesis_01 [Generation]
│   └── batch_synthesis_02 [Generation]
└── Stage_6_MOC [Span]
    └── moc_reconciliation [Generation]
```

### 1.3 Prompt Version Registry
All prompt templates must be versioned and registered in Langfuse:
- `cresmo-stage2-gapfiller:v1.0.0`
- `cresmo-stage3-expander-longitudinal:v1.0.0`
- `cresmo-stage3-expander-synchronic:v1.0.0`
- `cresmo-stage4-inventory:v1.0.0`
- `cresmo-stage5-batch:v1.0.0`
- `cresmo-stage6-moc:v1.0.0`

---

## 2. Quantitative Eval Rubrics & Quality Gates

The pipeline enforces hard thresholds evaluated post-generation. Any output falling below a blocking threshold will halt the pipeline and mark synthesis as failed.

| Dimension | ADR Objective | Evaluation Method | Threshold Score | Blocking Policy |
|---|---|---|---|---|
| **`faithfulness`** | Factual grounding in raw spoken transcript; zero invented statements. | LLM-as-judge comparing output claims against source raw transcript. | **`score ≥ 0.80`** | **BLOCKING**: Synthesis rejected if `< 0.80`. |
| **`relevance`** | High conceptual density; adherence to Braudelian/Jaspers frameworks. | Semantic cosine similarity against domain reference embeddings. | **`score ≥ 0.75`** | **BLOCKING**: Re-prompt required if `< 0.75`. |
| **`hallucination`** | Complete absence of fabricated historical entities or false attributions. | LLM-as-judge entity-by-entity attribution audit. | **`score ≤ 0.10`** | **BLOCKING**: Pipeline halted if `> 0.10`. |
| **`toxicity`** | Clean discourse; elimination of aggressive or non-objective bias. | Rule-based classifier. | **`score ≤ 0.05`** | **BLOCKING**: Pipeline halted if `> 0.05`. |

---

## 3. Post-Operative Verification Protocol

In Phase 4 (Treatment), `stangler-treatment` will query Langfuse using the trace ID:
```bash
python -m cresmo.infrastructure.telemetry.verify_evals --trace-id cresmo-{content_id}
```
The implementation is not certified as complete until all 4 Eval dimensions pass their thresholds.
