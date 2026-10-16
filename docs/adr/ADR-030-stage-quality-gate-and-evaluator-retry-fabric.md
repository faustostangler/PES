# ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric

**Status:** ACCEPTED  
**Date:** 2026-10-01  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-028`](ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-029`](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md)

---

## 1. Context & Architectural Motivation

In [ADR-029](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), we established an isolated, hexagonal Quality Evaluation Subsystem governed by `LlmJudgePort` and resilient multi-provider adapters (`GeminiJudgeAdapter`, `OllamaJudgeAdapter`, `TypeSafeJudgeAdapter`, `LangfuseJudgeDecorator`).

However, the initial integration in [`src/cresmo/application/pipeline/coordinator.py`](../../src/cresmo/application/pipeline/coordinator.py) exposed an emerging architectural code smell:
1. **Duplicated Orchestration Logic (ADR-026 Rule 5):**
   Following the execution of `fluid_prose`, `coordinator.py` inline-assembled an `EvaluationContext`, extracted OpenTelemetry span contexts, called `self.llm_judge.evaluate(...)`, logged score summaries, and enforced `judge_blocking` checks across ~40 lines of procedural code.
2. **Impending Code Bloat Across Subsequent Stages:**
   The Cresmo Knowledge Synthesis pipeline consists of 8 sequential stages (`fluid_prose`, `raw_indexing`, `gap_filler`, `expansion`, `inventory`, `atomic_batch`, `mocs`, `duplicate_unification`). Replicating this evaluation block for every subsequent stage would bloat `coordinator.py` with over 300 lines of repetitive boilerplate, severely violating the Single Responsibility Principle (SRP) and the Template Method pattern established in ADR-007 and ADR-021.
3. **Absence of Closed-Loop Self-Healing (Retry on Failure):**
   Generative LLM stages occasionally suffer from transient hallucinations, format deviations, or temporary non-compliance. When the judge verdict is `passed=False`, a robust system should support configurable self-healing re-execution (retries) before either failing fast (`judge_blocking=True`) or logging telemetry sentinels (`judge_blocking=False`).

---

## 2. Decision

We establish the **Stage Quality Gate Fabric**, encapsulating stage execution, closed-loop evaluation, OpenTelemetry trace binding, and automated self-healing retries inside `PipelineStageRunner`.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CresmoPipeline (Coordinator)                    │
│   fluid_transcript = self.stage_runner.run_evaluated_stage(            │
│       "fluid_prose",                                                   │
│       lambda: self.transform_fluid_prose.execute(raw, ...),            │
│       eval_spec=StageEvaluationSpec(                                   │
│           raw_text=raw.body,                                           │
│           candidate_extractor=lambda res: res.body,                    │
│           required_criteria=(JudgeCriterion.ORALITY_REMOVAL, ...),     │
│       ),                                                               │
│       channel_name=channel_name,                                       │
│       content_id=content_id,                                           │
│   )                                                                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ delegates to
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        PipelineStageRunner                             │
│                                                                        │
│   Loop (attempt = 1 .. max_attempts):                                  │
│     1. candidate = run_stage(stage_name, fn, ...)                      │
│     2. if judge is None or eval_spec is None: return candidate         │
│     3. candidate_text = eval_spec.candidate_extractor(candidate)       │
│     4. context = EvaluationContext(raw, candidate_text, criteria, ...) │
│     5. verdict = judge.evaluate(context)                               │
│     6. if verdict.passed: return candidate                             │
│     7. if attempt < max_attempts: log warning & retry                  │
│                                                                        │
│   Attempts Exhausted:                                                  │
│     - if judge_blocking: raise DomainValidationError                   │
│     - else: log warning & return candidate                             │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Domain Layer: `StageEvaluationSpec` Value Object

In `src/cresmo/domain/value_objects/quality.py`, introduce an immutable specification value object:

```python
@dataclass(frozen=True, slots=True)
class StageEvaluationSpec:
    """Specification of quality evaluation criteria and extractors for a pipeline stage."""

    raw_text: str
    candidate_extractor: Callable[[Any], str]
    required_criteria: tuple[JudgeCriterion, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 1

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")
```

### 2.2 Application Layer: `PipelineStageRunner.run_evaluated_stage`

In `src/cresmo/application/pipeline/stage_runner.py`:
1. Inject optional dependencies into `PipelineStageRunner`:
   - `llm_judge: LlmJudgePort | None = None`
   - `judge_blocking: bool = False`
   - `judge_max_attempts: int = 1`
2. Implement `run_evaluated_stage`:
   - Executes `fn` via the standard `run_stage` telemetry and timing wrapper.
   - If `eval_spec` is provided and `self.llm_judge` is present:
     - Extracts the candidate text using `eval_spec.candidate_extractor`.
     - Automatically resolves the active OpenTelemetry trace ID.
     - Invokes `self.llm_judge.evaluate(context)`.
     - If verdict passes, returns the candidate immediately.
     - If verdict fails and `attempt < max_attempts`, logs retry warning and executes a fresh generation attempt.
     - If all attempts are exhausted:
       - Raises `DomainValidationError` when `self.judge_blocking is True`.
       - Logs warning and returns the candidate when `self.judge_blocking is False` (telemetry mode).

### 2.3 Single Source of Truth in `coordinator.py`

`CresmoPipeline` delegates all stage quality assessments through `self.stage_runner.run_evaluated_stage(...)`:
- Eliminates code duplication across all 8 pipeline stages.
- Preserves the clean Template Method design of `coordinator.py`.
- Enables progressive adoption: any stage can activate automated evaluation simply by attaching a `StageEvaluationSpec`.

---

## 3. Consequences

### Positive
- **DRY & High Cohesion:** Eliminates repetitive `EvaluationContext` and trace boilerplate from `coordinator.py`.
- **Closed-Loop Self-Healing:** Generative pipeline stages automatically re-attempt extraction when evaluation criteria fail.
- **Zero-Bypass Hermeticity:** In test environments or when `llm_judge is None`, stages execute with zero overhead and full backward compatibility.
- **Metric Uniformity:** SRE metrics for evaluation verdicts, attempts, and latencies are recorded systematically at the runner level.

### Negative / Trade-offs
- Multiple generative retries on failing stages increase latency and API token consumption, bounded by `max_attempts` (default: 1 in unit tests, configurable in settings).
