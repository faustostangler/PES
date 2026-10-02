# ADR-031: Standardized StageDescriptor, SourceTranscript, CandidateText, and Closed-Loop Reflection Quality Fabric

**Status:** ACCEPTED  
**Date:** 2026-10-01  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-010`](ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-029`](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), [`ADR-030`](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md)

---

## 1. Context & Architectural Motivation

In [ADR-030](ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md), we introduced `PipelineStageRunner` to centralize telemetry instrumentation, OpenTelemetry trace binding, and basic quality gate checks.

However, as we prepare to standardize and refactor all pipeline stages starting from `fluid_transcript` (`fluid_prose`), several systemic design gaps have emerged:

1. **Heterogeneous Stage Input Signatures (Primitive Obsession & Inconsistency):**
   - Different stages receive disparate input structures (`RawTranscript`, `FluidTranscript`, `EnrichedCompendium`, raw dictionaries).
   - There is no unified, polymorphic domain concept representing the *source text* entering a pipeline stage.
2. **Missing Standardized CandidateText Value Object:**
   - LLM generation outputs are treated as raw Python strings (`str`) rather than strongly-typed, self-validating Domain Value Objects (`CandidateText`), leading to primitive obsession and bypassing domain invariant checks.
3. **Unstructured & Untyped Judge Verdicts:**
   - In [ADR-029](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), `JudgeEvaluation` only supported scalar float scores and a boolean `passed` flag.
   - Modern decision models (such as **TypeSafe AI System One / Jev**) and rigorous LLM-as-a-judge patterns operate on discrete, typed judgment primitives:
     - **`NOUL` (Binary / Boolean):** Pass/Fail, Yes/No assertions (e.g. orality purged, NER preserved, structural formatting valid).
     - **`CHOICE` (Categorical):** Selection among discrete predefined options.
     - **`SCORE` (Continuous Scaled):** Bounded scalar ratings $[0.0, 1.0]$ with qualitative rubric criteria.
   - The domain lacks a unified `VerdictType` and `TypedVerdict` representation to standardize multi-provider evaluator responses.
4. **Blind Retries (Absence of Closed-Loop Reflection):**
   - When a quality gate fails in ADR-030, the retry mechanism simply re-invokes the generative LLM blindly with identical prompts, relying solely on sampling temperature.
   - High-performance agentic pipelines require **Closed-Loop Reflection / Self-Correction**: injecting the judge's failure critique or actionable improvement suggestions into subsequent attempts.
5. **Scattered Stage Definitions & Leaky Orchestrator:**
   - In `coordinator.py`, stage prompts, evaluation specifications, and post-processing logic are manually assembled inline, violating Single Responsibility (SRP) and creating monolithic sprawl.

---

## 2. Decision

We establish the **Standardized Stage Execution Architecture**, built around:
1. **`SourceTranscript` Domain Aggregate**: The canonical input contract across all pipeline stages. Conforming strictly to ADR-010 (Zero Legacy Shims), `RawTranscript` is completely decommissioned and eliminated with zero backwards compatibility.
2. **`CandidateText` Value Object**: Strongly-typed, validated container for intermediate LLM transformation outputs.
3. **`VerdictType` and `TypedVerdict`**: Polymorphic evaluation returns (`NOUL`, `CHOICE`, `SCORE`) for `LlmJudgePort`.
4. **`StageDescriptor[TSource, TOutput]`**: Reusable Template Method specification encapsulating transform prompts, judge prompts, evaluation specifications, and optional post-processors.
5. **Closed-Loop Reflection Fabric**: Injecting judge critique and improvement suggestions into subsequent retry prompts.
6. **Pipeline Truncation / Quarantine**: Commenting downstream unrefactored stages in `coordinator.py` to isolate Stage 1 (`fluid_transcript`) as the reference implementation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CresmoPipeline (Coordinator)                    │
│   fluid_transcript = self.stage_runner.execute_stage(                  │
│       stage_descriptor=self.fluid_prose_descriptor,                   │
│       source=source_transcript,                                        │
│       session_id=session_id,                                           │
│   )                                                                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ executes template
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         PipelineStageRunner                            │
│                                                                        │
│   Loop (attempt = 1 .. max_attempts):                                  │
│     1. prompt = descriptor.build_transform_prompt(source, critique)    │
│     2. candidate_text: CandidateText = llm_transform(prompt)           │
│     3. if not descriptor.has_evaluation: break                         │
│     4. verdict: JudgeEvaluation = judge.evaluate(                      │
│            EvaluationContext(source, candidate_text, spec)             │
│        )                                                               │
│     5. if verdict.passed: break                                        │
│     6. critique = verdict.extract_critique()                           │
│     7. emit_telemetry_retry(stage, attempt, critique)                  │
│                                                                        │
│   Post-Processing:                                                     │
│     result: TOutput = descriptor.post_process(candidate_text, source)  │
│     return result                                                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Architecture

### 3.1 Domain Layer: Standardized Contracts & Value Objects

#### A. `SourceTranscript`
Standardizes input across all stages. Conforming to ADR-010 (Zero Legacy Shims), `RawTranscript` is fully eliminated and replaced with `SourceTranscript` across the domain, application, and test suites:
```python
@dataclass(frozen=True)
class SourceTranscript:
    content_id: ContentId
    channel_name: ChannelName
    body: str
    title: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    upload_date: datetime.date | None = None
    channel_id: ChannelId | None = None
    channel_category: str = ""
    video_description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
```

#### B. `CandidateText`
Validates intermediate generation output:
```python
@dataclass(frozen=True, slots=True)
class CandidateText:
    text: str
    stage_name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise DomainValidationError(f"CandidateText for '{self.stage_name}' cannot be empty.")
```

#### C. `VerdictType` and `TypedVerdict`
Categorizes judge evaluation returns:
```python
class VerdictType(str, Enum):
    NOUL = "noul"      # Boolean / Binary (TypeSafe / assertion style)
    CHOICE = "choice"  # Categorical selection
    SCORE = "score"    # Continuous normalized [0.0, 1.0]

@dataclass(frozen=True, slots=True)
class TypedVerdict:
    criterion: JudgeCriterion
    verdict_type: VerdictType
    passed: bool
    score: float
    choice_value: str | None = None
    confidence: float | None = None
    reasoning: str = ""
    improvement_suggestion: str = ""
```

---

### 3.2 Application Layer: `StageDescriptor` Template

Encapsulates all stage requirements into a single declarative structure:

```python
@dataclass(frozen=True)
class StageDescriptor(Generic[TSource, TOutput]):
    stage_name: str
    transform_prompt_key: PromptKey
    judge_prompt_key: PromptKey | None = None
    eval_spec: StageEvaluationSpec | None = None
    post_processor: Callable[[CandidateText, TSource], TOutput] | None = None
    temperature: float | None = None
    max_attempts: int = 1
    blocking: bool = False
```

---

### 3.3 Closed-Loop Reflection (Self-Correction Retry)

When a judge fails an evaluation on attempt $N < \text{max\_attempts}$:
1. The judge's `reasoning` and `improvement_suggestion` are extracted.
2. In attempt $N+1$, the user prompt is dynamically amended:
   ```
   [PREVIOUS ATTEMPT QUALITY FEEDBACK]
   The previous generation failed quality validation due to:
   - <Criterion>: <Reasoning>
   Please correct these defects and apply the following improvement:
   - <Improvement Suggestion>
   ```
3. OpenTelemetry and Prometheus record the retry with `status="reflection_retry"`.

---

## 4. Consequences & Impact

### Positive
- **DRY & Unified Extensibility:** Refactoring downstream stages (`raw_indexing`, `gap_filler`, `expansion`, etc.) will only require defining their respective `StageDescriptor` instances.
- **Closed-Loop Convergence:** Self-healing retries dramatically reduce hallucination rates and improve deterministic compliance.
- **Strong Typing (Zero Primitive Obsession):** `SourceTranscript`, `CandidateText`, and `TypedVerdict` eliminate untyped string plumbing.
- **Safe Isolation:** Commenting downstream stages allows verifying the entire end-to-end flow of Stage 1 in hermetic isolation.

### Neutral / Trade-offs
- Slight prompt token overhead on retry attempts when injecting reflection critique.
- Requires updating existing unit test doubles to handle `CandidateText` and `SourceTranscript`.
