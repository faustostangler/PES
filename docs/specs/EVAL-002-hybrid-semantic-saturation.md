# EVAL-002: Hybrid Semantic Saturation Evaluation Harness & Acceptance Matrix

**Context:** Cresmo Knowledge Synthesis  
**Phase:** Phase 2 — Refractometry & Phase 4 — Treatment  
**Status:** APPROVED SPECIFICATION  
**Governing Spec & ADR:** [`SPEC-066`](SPEC-066-hybrid-semantic-saturation.md), [`ADR-066`](../adr/ADR-066-hybrid-semantic-saturation-and-text-embedding-adapters.md)  
**Related Specs & ADRs:** [`EVAL-001`](EVAL-001-cresmo-synthesis.md), [`ADR-046`](../adr/ADR-046-unified-state-driven-gap-filler-prompt.md), [`ADR-065`](../adr/ADR-065-hierarchical-stage-scoped-telemetry-nomenclature.md)

---

## 1. Clinical Telemetry Plan

Every multi-pass stage executing hybrid semantic saturation (e.g., `gap_filler`) emits stage-scoped OpenTelemetry and Langfuse observations compliant with [`ADR-065`](../adr/ADR-065-hierarchical-stage-scoped-telemetry-nomenclature.md) and [`EVAL-001`](EVAL-001-cresmo-synthesis.md).

### 1.1 Trace Taxonomy
- `trace_id`: Deterministically scoped per stage execution (`{active_trace_id}_pass_{N}` for LLM generation calls within multi-pass stages).
- `session_id`: Canonical `PipelineSessionId` (`{channel_id}:{content_id}`).
- `tags`: `["cresmo", category, channel_name, stage_name]`.

### 1.2 Multi-Pass Saturation Span Hierarchy
```text
cresmo.pipeline [Trace]
└── cresmo.coordinator [Root Span]
    └── cresmo.{stage_name} [Stage Span]
        ├── cresmo.{stage_name}.generate.pass_1 [Generation]
        ├── cresmo.{stage_name}.saturation.pass_1 [Saturation Span]
        ├── cresmo.{stage_name}.generate.pass_2 [Generation]
        ├── cresmo.{stage_name}.saturation.pass_2 [Saturation Span]
        └── cresmo.{stage_name}.judge [Judge Span]
```

### 1.3 Required Span & Candidate Metadata Payloads
1. **`cresmo.{stage_name}.saturation.pass_{N}` Span Attributes:**
   - `cresmo.pass_num` (`int`)
   - `cresmo.saturation.is_saturated` (`bool`)
   - `cresmo.saturation.reason` (`disabled` | `explicit_sentinel` | `lexical_identity` | `semantic_plateau` | `novel_content`)
   - `cresmo.saturation.lexical_jaccard` (`float` in `[0.0, 1.0]`)
   - `cresmo.saturation.word_delta_ratio` (`float` in `[0.0, 1.0]`)
   - `cresmo.saturation.max_novelty` (`float` in `[0.0, 1.0]`)
   - `cresmo.saturation.novel_paragraphs` (`int`)
   - `cresmo.saturation.total_paragraphs` (`int`)
   - `cresmo.saturation.preserve_baseline` (`bool`)
   - `cresmo.saturation.provider` (`str`)
2. **`CandidateText.metadata["saturation_history"]`:**
   - Ordered `list[dict[str, Any]]` recording one entry per executed pass with `pass_index` and all fields from `SaturationVerdict.to_metadata_dict()`.

---

## 2. Eval Matrix

All five evaluation scenarios below are mandatory and deterministic under hermetic test doubles as well as live/local provider parity checks.

| Eval ID | Scenario | Input & Preconditions | Expected Verdict & State | Required Behavioral & Telemetry Assertions |
| :--- | :--- | :--- | :--- | :--- |
| **`EVAL-SAT-001`** | **Lexical Identity Short-Circuit** | `baseline_text` and `current_text` share high word 3-gram overlap and near-identical length (`lexical_jaccard >= 0.95` and `word_delta_ratio <= 0.03` under default `SaturationThresholds`). | `is_saturated = True`<br>`reason = SaturationReason.LEXICAL_IDENTITY`<br>`preserve_baseline = True`<br>`max_novelty = 0.0`<br>`novel_paragraphs = 0`<br>`provider = "lexical"` | `TextEmbeddingPort.embed_batch` call count **MUST be `0`** (Layer 1 short-circuit prevents any embedding API/network/local call). `current_text` reverts to `baseline_text` in `generate_stage_candidate`. |
| **`EVAL-SAT-002`** | **Pure Paraphrase Plateau** | `current_text` rewrites `baseline_text` using synonym/syntactic variation that bypasses Layer 1 (`lexical_jaccard < 0.95` or `word_delta_ratio > 0.03`), while every semantic unit has cosine similarity `>= semantic_similarity_threshold` (`0.92`) against baseline units. | `is_saturated = True`<br>`reason = SaturationReason.SEMANTIC_PLATEAU`<br>`novel_paragraphs = 0`<br>`max_novelty <= 1.0 - 0.92` (`<= 0.08`)<br>`preserve_baseline = True` | `TextEmbeddingPort.embed_batch` invoked **exactly once** with `[*baseline_units, *current_units]`. `generate_stage_candidate` restores `baseline_text` (`preserve_baseline=True`) so paraphrase drift does not degrade verified facts, and halts early (unless final critique pass is pending). |
| **`EVAL-SAT-003`** | **Substantive Body or Extra Info Enrichment** | `current_text` introduces at least one semantically novel paragraph in either the main body OR the `### Extra Info` section whose maximum cosine similarity against `baseline_units` is `< semantic_similarity_threshold` (`0.92`). | `is_saturated = False`<br>`reason = SaturationReason.NOVEL_CONTENT`<br>`novel_paragraphs >= 1`<br>`max_novelty > 1.0 - 0.92` (`> 0.08`)<br>`preserve_baseline = False` | `segment_semantic_units` ignores Markdown headings (`##`, `### Extra Info`) while preserving both body and `### Extra Info` paragraphs. `generate_stage_candidate` keeps `current_text`, updates `previous_text = current_text` as the new baseline, and proceeds to `pass_{N+1}`. |
| **`EVAL-SAT-004`** | **Pass-1 Saturation (`baseline_text = source_text`)** | On `pass_index = 1` of a multi-pass stage (`max_passes > 1`), LLM output against `source_text` satisfies Layer 1 lexical identity or Layer 2 semantic plateau. Separate sub-case: Pass-1 output contains `<NO_NEW_GAPS/>` alongside novel body content. | **Saturated sub-case:** Immediate stop after Pass 1 (`passes_executed == 1`, `is_saturated = True`, `preserve_baseline = True` restores `source_text`).<br>**Sentinel sub-case:** `is_explicit_stop_sentinel(..., pass_index=1) == False`; `<NO_NEW_GAPS/>` is ignored on Pass 1 and honored only when `pass_index > 1` (`EXPLICIT_SENTINEL`). | `cresmo.{stage}.saturation.pass_1` span emitted with `cresmo.pass_num = 1`. `CandidateText.metadata["saturation_history"]` contains exactly 1 entry (`pass_index == 1`) when Pass 1 saturates immediately. |
| **`EVAL-SAT-005`** | **Resilient Fallback Parity (`Gemini/Ollama` -> `TfidfEmbeddingAdapter`)** | Primary `TextEmbeddingPort` (`GeminiEmbeddingAdapter` or `OllamaEmbeddingAdapter`) raises `EmbeddingInfrastructureError` (timeout, HTTP 429/503, socket failure). Separate sub-case: `HybridSaturationEvaluator(embedding_port=None)`. | **Resilient fallback sub-case:** `ResilientEmbeddingAdapter` logs `WARNING`, sets `last_provider_name == "tfidf_fallback"`, returns `TfidfEmbeddingAdapter` vectors; evaluator produces `SEMANTIC_PLATEAU` on plateau pairs and `NOVEL_CONTENT` on enriched pairs with `provider == "tfidf_fallback"`.<br>**`embedding_port=None` sub-case:** Degrades gracefully to Layer 1 + `NOVEL_CONTENT` (`is_saturated = False`, `preserve_baseline = False`, `provider = "degraded"`). | Zero unhandled `EmbeddingInfrastructureError` propagation through `ResilientEmbeddingAdapter` or `HybridSaturationEvaluator`. Empty input `[] -> []` and empty-vocabulary corpus return uniform zero vectors without raising `ValueError`. |

---

## 3. Quantitative Eval Gates & Blocking Thresholds

| Metric / Dimension | Definition | Threshold | Blocking Policy |
| :--- | :--- | :--- | :--- |
| **`layer1_short_circuit_rate`** | Fraction of `EVAL-SAT-001` lexical-identity pairs avoiding `embed_batch` calls | **`1.00`** (`0` embedding calls) | **BLOCKING**: Any embedding call on lexical identity fails gate. |
| **`paraphrase_plateau_recall`** | Detection rate of `SEMANTIC_PLATEAU` (`novel_paragraphs == 0`, `preserve_baseline=True`) across `EVAL-SAT-002` | **`>= 0.95`** | **BLOCKING**: Re-calibrate `semantic_similarity_threshold` if `< 0.95`. |
| **`enrichment_false_stop_rate`** | Rate at which `EVAL-SAT-003` substantive body or `### Extra Info` additions are wrongly marked saturated | **`== 0.00`** | **BLOCKING**: Zero premature halts on genuine enrichments permitted. |
| **`pass1_saturation_accuracy`** | Correct immediate stop on `EVAL-SAT-004` (`baseline_text = source_text`) + sentinel suppression on Pass 1 | **`1.00`** | **BLOCKING**: Pipeline must honor Pass-1 fixed-point baseline and Pass-1 sentinel ignore rule. |
| **`resilient_fallback_parity`** | Pass rate on `EVAL-SAT-005` under simulated `GeminiEmbeddingAdapter`/`OllamaEmbeddingAdapter` outage and `embedding_port=None` | **`1.00`** (`last_provider_name == "tfidf_fallback"`) | **BLOCKING**: Pipeline must never crash on embedding infrastructure outage. |

---

## 4. Verification Protocol

Execute static, unit, integration, and mutation verification suites after implementation:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest tests/ -v
```

For targeted Phase 4 mutation verification on domain/application saturation modules (`prose_syntax_guard.py`, `convergence.py`, `convergence_evaluator.py`, `hybrid_saturation.py`):

```bash
uv run mutmut run
```
