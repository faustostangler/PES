# SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework

**Conforms to:** [`ADR-039`](../adr/ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md)  
**Status:** APPROVED  
**Date:** 2026-10-10  

---

## 1. Specification Overview

Defines the concrete interfaces, domain value objects, mechanical validation rules, and offline calibration harness for Stage 1 (`fluid_prose`) of the Cresmo pipeline.

---

## 2. Domain Model Specifications

### 2.1 `JudgeCriterion` Enum Expansion
Located in `src/cresmo/domain/value_objects/quality.py`:

```python
class JudgeCriterion(str, Enum):
    ORALITY_REMOVAL = "orality_removal"
    SEMANTIC_FAITHFULNESS = "semantic_faithfulness"
    NER_PRESERVATION = "ner_preservation"
    STRUCTURAL_COMPLIANCE = "structural_compliance"
    EPISTEMIC_CRITIQUE = "epistemic_critique"
    AUTHORIAL_VOICE = "authorial_voice"
    INVENTORY_COHERENCE = "inventory_coherence"
    INDEX_SYNTHESIS_QUALITY = "index_synthesis_quality"
```

### 2.2 Mechanical Validator Interface
Located in `src/cresmo/domain/services/mechanical_validator.py`:

```python
def validate_fluid_prose_mechanical_invariants(text: str) -> list[str]:
    """Validate deterministic mechanical and syntactic invariants.
    
    Returns a list of violation messages. Empty list indicates full compliance.
    """
```

Rules:
1. `LINE_1_HEADING`: Line 1 must begin with `## ` (after stripping leading blank lines).
2. `NO_FRONTMATTER`: Text must not start with or contain YAML frontmatter blocks `---`.
3. `NO_EM_DASH`: Text must contain zero em-dashes `—`.
4. `NO_BULLETS`: Text must contain zero bullet lines (`* `, `- `, `+ `).
5. `NO_TABLES`: Text must contain zero markdown table markers (`|`).
6. `NO_BLOCKQUOTES`: Text must contain zero blockquote lines (`>`).

---

## 3. Semantic Rubric Specifications (LLM-as-a-Judge)

Each semantic criterion is scored in $[0.0, 1.0]$. The pass threshold is individual: each required criterion must score $\ge 0.80$ for the overall evaluation to pass.

1. **`ORALITY_REMOVAL`**:
   - Score 1.0: Pure 3rd person objective narrative; zero conversational filler words ("né", "tipo", "sabe").
   - Score 0.0: Any YouTube meta-speech, sales pitches, subscriptions, likes, comments, or sponsor plugs.
2. **`SEMANTIC_FAITHFULNESS`**:
   - Score 1.0: Complete retention of thesis, arguments, and causal claims. Zero unsanctioned external inventions.
3. **`EPISTEMIC_CRITIQUE`**:
   - Score 1.0: Legitimate in-line attribution highlighting factual errors or bias ("O interlocutor afirma X; no entanto, os registros apontam Y"), and accurate mapping of conceptual gaps for downstream `gap-filler`.
   - Score 0.0: Acceptance of blatant falsehoods uncritically, or introduction of model's own factual errors.
4. **`NER_PRESERVATION`**:
   - Score 1.0: All names, institutions, historical treaties, and dates retained and normalized to canonical encyclopedic spelling. Big-Endian dates.
5. **`STRUCTURAL_COMPLIANCE`**:
   - Score 1.0: Progressive thematic/chronological spine untangling conversational loops, using `##` and `###` headers.
6. **`AUTHORIAL_VOICE`**:
   - Score 1.0: Detective Narrator register, second-order mechanisms, methodological naturalism, zero moralistic outrage, zero binary antitheses ("não X, mas Y").

---

## 4. Calibration Harness (`scripts/calibrate_fluid_prose_judge.py`)

Emits scores to Langfuse:
- `judge_exact_match`
- `judge_is_tp`, `judge_is_fp`, `judge_is_fn`, `judge_is_tn`
Calculates:
- $\text{Accuracy} = (TP + TN) / \text{Valid Rows}$
- $\text{Precision} = TP / (TP + FP)$
- $\text{Recall} = TP / (TP + FN)$
- $\text{F1} = 2 \times (\text{Precision} \times \text{Recall}) / (\text{Precision} + \text{Recall})$
