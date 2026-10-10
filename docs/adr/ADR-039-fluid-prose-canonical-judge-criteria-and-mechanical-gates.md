# ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates, and Calibration Framework

**Status:** ACCEPTED  
**Date:** 2026-10-10  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-017`](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-029`](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), [`ADR-030`](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-036`](ADR-036-clean-telemetry-namespacing-and-observation-binding.md)

---

## 1. Context & Architectural Motivation

In ADR-028, ADR-029, and ADR-031, we established the decoupled Stage 1 (`fluid_prose`), the `LlmJudgePort` abstraction, and the closed-loop retry loop in `PipelineStageRunner`.

However, the evaluation criteria for `fluid_prose` remained legacy placeholders (`ORALITY_REMOVAL`, `SEMANTIC_FAITHFULNESS`, `NER_PRESERVATION`, `STRUCTURAL_COMPLIANCE`) that were neither rigorously defined nor calibrated against real-world audio transcripts. Several architectural tensions remained:

1. **Undifferentiated Mechanical vs Semantic Quality Validation:**
   - LLMs are poor, expensive, and non-deterministic validators for syntactic invariants like zero em-dashes (`—`), zero markdown tables/bullets, and heading hierarchy (`##` on Line 1).
   - Evaluating formatting invariants via LLM prompts wastes tokens and introduces false positives/negatives.
2. **Ambiguity in Factual Fidelity vs Epistemic Correction:**
   - Raw YouTube video transcripts frequently contain factual lapses, historical inaccuracies, or overt ideological bias.
   - If the judge blindly scores "semantic faithfulness", it penalizes legitimate in-line analytical corrections. Conversely, if it permits arbitrary additions, it allows unsanctioned hallucinations.
3. **Lack of Zero-Tolerance Hard Gates for YouTube Spoken Noise:**
   - Orality removal was treated as a soft continuous rating. However, marketing CTAs ("subscribe to channel", "like the video", sponsorship plugs) represent total corruption of the second brain knowledge repository.
4. **Absence of Calibrated Golden Ground Truth:**
   - Without an offline calibration framework (confusion matrix: Accuracy, Precision, Recall, F1), LLM-as-a-judge evaluators cannot be safely run in blocking mode (`judge_blocking=True`).

---

## 2. Decision

We establish the **Canonical Fluid Prose Evaluation Framework**:

### 1. Two-Layered Evaluation Topology
- **Layer 1: Deterministic Mechanical Pre-flight Validator (Python Pure Function)**
  - Runs in $<1\text{ms}$ with 100% precision before any LLM judge invocation.
  - Invariants:
    1. Line 1 Contract: Document starts strictly with `##`.
    2. Zero YAML frontmatter (`---`).
    3. Zero em-dashes (`—`).
    4. Zero markdown tables, bullet points (`*`, `-`), numbered lists, LaTeX, or blockquotes (`>`).
    5. Bold (`**...**`) strictly on the first occurrence of named entities and key terms.
- **Layer 2: Semantic LLM-as-a-Judge (`LlmJudgePort`)**
  - Evaluates 6 canonical semantic criteria with individual Hard Gates ($\ge 0.80$):
    1. `ORALITY_REMOVAL`: Purges filler words ("né", "tipo", "sabe") and conversational 1st-person speech. **Hard Failure (0.0)** if any YouTube meta-speech (CTAs, likes, subscriptions, sales, sponsorships) remains.
    2. `SEMANTIC_FAITHFULNESS`: 100% core thesis and argument retention; zero unsanctioned hallucinations.
    3. `EPISTEMIC_CRITIQUE`: Validates legitimate in-line narrative corrections ("O interlocutor afirma X; no entanto...") of factual lapses/inventions, exposes strong bias, and pinpoints conceptual gaps for downstream `gap-filler` without introducing errors.
    4. `NER_NORMALIZATION`: Encyclopedic spelling correction of phonetically distorted names and Big-Endian date standardization without entity loss.
    5. `STRUCTURAL_REORGANIZATION`: Progressive, cohesive thematic/chronological narrative spine untangling oral digressions, with hierarchical headings (`##` and `###`).
    6. `AUTHORIAL_VOICE`: "Detective Narrator" register, second-order mechanisms, methodological naturalism, zero moralistic outrage, and **zero binary antitheses** ("não X, mas Y").

### 2. Domain Value Object Extension
We extend `JudgeCriterion` in `cresmo.domain.value_objects.quality` to include `EPISTEMIC_CRITIQUE` and `AUTHORIAL_VOICE`.

### 3. Offline Calibration Framework
We create `scripts/calibrate_fluid_prose_judge.py` following Langfuse Dataset Experiments SDK to compute Accuracy, Precision, Recall, and Confusion Matrices against human-labeled ground truth before promoting judges to blocking mode.

---

## 3. Consequences

### Positive
- **Deterministic Guardrails:** Syntax errors and forbidden typography are caught instantly in Python without LLM token cost.
- **Calibrated Semantics:** The LLM judge focuses exclusively on deep comprehension, voice, and epistemic fidelity.
- **Fail-Fast Safety:** Hard gates prevent corrupted compendia from propagating to downstream expanders.

### Negative / Trade-offs
- Adding `EPISTEMIC_CRITIQUE` and `AUTHORIAL_VOICE` requires updating prompt templates and multi-provider judge adapters.
