# SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification

**Context:** Cresmo Knowledge Synthesis & Pipeline Execution Subsystem  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** ACCEPTED SPECIFICATION  
**Governing ADR:** [`ADR-030`](../adr/ADR-030-stage-quality-gate-and-evaluator-retry-fabric.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`SPEC-008`](SPEC-008-metrics-port-and-prometheus-sre-dora.md), [`SPEC-010`](SPEC-010-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`SPEC-011`](SPEC-011-fluid-prose-detranscription-and-gap-filler-decoupling.md), [`SPEC-012`](SPEC-012-quality-judge-evaluators-and-adapters.md)

---

## 1. Domain Entities & Value Objects

In `src/cresmo/domain/value_objects/quality.py`:

### 1.1 `StageEvaluationSpec` (Value Object)
- Attributes:
  - `raw_text: str` (Source or input reference text)
  - `candidate_extractor: Callable[[Any], str]` (Extracts the candidate string to evaluate from the stage return object)
  - `required_criteria: tuple[JudgeCriterion, ...]` (Criteria to evaluate)
  - `metadata: dict[str, Any] = field(default_factory=dict)` (Optional stage and domain metadata)
  - `max_attempts: int = 1` (Maximum generation attempts if evaluation fails, must be $\ge 1$)
- Invariants:
  - Raises `ValueError` if `max_attempts < 1`.

---

## 2. Application Layer: `PipelineStageRunner.run_evaluated_stage`

In `src/cresmo/application/pipeline/stage_runner.py`:

### 2.1 Dependencies
`PipelineStageRunner` receives:
- `telemetry_port: TelemetryPort`
- `metrics_port: MetricsPort`
- `llm_judge: LlmJudgePort | None = None`
- `judge_blocking: bool = False`
- `judge_max_attempts: int = 1`

### 2.2 Method Signature
```python
def run_evaluated_stage(
    self,
    stage_name: str,
    fn: Callable[[], _StageRet],
    *,
    channel_name: ChannelName,
    content_id: ContentId,
    eval_spec: StageEvaluationSpec | None = None,
    channel_id: ChannelId | None = None,
    fatal: bool = True,
    fallback: _StageRet | None = None,
) -> _StageRet | None:
```

### 2.3 Evaluation & Retry Loop Workflow
1. If `eval_spec is None` or `self.llm_judge is None`:
   - Delegate directly to `self.run_stage(...)`.
2. Compute `effective_max_attempts = max(eval_spec.max_attempts, self.judge_max_attempts)`.
3. Loop for `attempt = 1 .. effective_max_attempts`:
   a. Execute `candidate = self.run_stage(stage_name, fn, channel_name=channel_name, content_id=content_id, channel_id=channel_id, fatal=fatal, fallback=fallback)`.
   b. If `candidate is None`: return `fallback`.
   c. Extract candidate text: `candidate_text = eval_spec.candidate_extractor(candidate)`.
   d. Format trace ID: Retrieve active span context or construct fallback `f"cresmo_{channel_name.value}_{content_id.value}"`.
   e. Construct `EvaluationContext(stage_name=stage_name, raw_text=eval_spec.raw_text, candidate_text=candidate_text, metadata={**eval_spec.metadata, "attempt": attempt}, trace_id=active_trace_id, required_criteria=eval_spec.required_criteria)`.
   f. Call `evaluation = self.llm_judge.evaluate(context)`.
   g. Record judge evaluation metrics (`cresmo_judge_evaluations_total` with `stage`, `passed`, `attempt`).
   h. If `evaluation.passed`:
      - Return `candidate`.
   i. If not passed and `attempt < effective_max_attempts`:
      - Log retry warning.
      - Increment `cresmo_judge_retries_total`.
      - Loop to next generation attempt.
4. If loop completes with failure:
   - If `self.judge_blocking is True`:
     - Raise `DomainValidationError(f"{stage_name} quality evaluation failed threshold after {effective_max_attempts} attempts: {evaluation.overall_score:.2f}")`.
   - Else (`judge_blocking is False`):
     - Log warning and return `candidate`.

---

## 3. Acceptance Test Matrix

| Test ID | Component | Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- |
| `TC-STAGE-001` | `StageEvaluationSpec` | `max_attempts < 1` | `ValueError` raised |
| `TC-STAGE-002` | `PipelineStageRunner` | `eval_spec=None` | Executes `run_stage` once, no judge invocation |
| `TC-STAGE-003` | `PipelineStageRunner` | `llm_judge=None` | Executes `run_stage` once, no judge invocation |
| `TC-STAGE-004` | `PipelineStageRunner` | Judge passes on attempt 1 | Returns candidate immediately, 1 execution |
| `TC-STAGE-005` | `PipelineStageRunner` | Judge fails on attempt 1, passes on attempt 2 | Executes `fn` twice, returns candidate from attempt 2 |
| `TC-STAGE-006` | `PipelineStageRunner` | Judge fails all attempts, `judge_blocking=False` | Logs warning, returns candidate |
| `TC-STAGE-007` | `PipelineStageRunner` | Judge fails all attempts, `judge_blocking=True` | Raises `DomainValidationError` |
| `TC-STAGE-008` | `CresmoPipeline` | Stage 1 `fluid_prose` via `run_evaluated_stage` | Validates fluid prose output seamlessly |
