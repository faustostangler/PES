# SPEC-014: Standardized StageDescriptor, Closed-Loop Reflection, and Fail-Fast Quarantine Specification

**Context:** Cresmo Knowledge Synthesis & Pipeline Execution Subsystem  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** APPROVED SPECIFICATION  
**Governing ADR:** [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`SPEC-008`](SPEC-008-metrics-port-and-prometheus-sre-dora.md), [`SPEC-010`](SPEC-010-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`SPEC-011`](SPEC-011-fluid-prose-detranscription-and-gap-filler-decoupling.md), [`SPEC-012`](SPEC-012-quality-judge-evaluators-and-adapters.md), [`SPEC-013`](SPEC-013-stage-quality-gate-and-evaluator-fabric.md)  

---

## 1. Overview & Objectives

This specification codifies the precision contracts, domain invariants, application template orchestrator, and acceptance test criteria for the **Standardized Stage Execution Architecture** introduced in [ADR-031](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md).

It formalizes:
1. **Domain Input & Intermediate Contracts:** Replacement of deprecated `RawTranscript` with canonical `SourceTranscript` (`ChannelName` VO) and introduction of `CandidateText` VO.
2. **Polymorphic Judge Verdicts:** `VerdictType` (`NOUL`, `CHOICE`, `SCORE`) and `TypedVerdict`.
3. **Domain Catalog:** `StageRegistry` and immutable `StageSpec` definitions.
4. **Application Template Orchestrator:** `StageDescriptor[TSource, TOutput]`, `StageFactory`, and `PipelineStageRunner.execute_stage(...)`.
5. **Closed-Loop Reflection:** Dynamic prompt critique injection via `CritiqueSynthesizerPort`.
6. **Fail-Fast Quarantine Protocol:** 4-step fail-fast quarantine handling on exhausted retry failures (`StageQuarantinedError`).

---

## 2. Domain Entities, Value Objects & Exceptions

### 2.1 `SourceTranscript` Aggregate
In [`src/cresmo/domain/entities.py`](../../src/cresmo/domain/entities.py):
- **Contract**: Canonical input aggregate across all pipeline stages. Replaces `RawTranscript` with zero legacy shims per ADR-010.
- **Attributes**:
  - `content_id: ContentId`: Canonical media identifier.
  - `channel_name: ChannelName`: Strongly-typed creator/channel name.
  - `body: str`: Verbatim spoken audio or canonical source prose.
  - `title: str = ""`: Video or document title.
  - `source_url: str = ""`: Origin URL.
  - `publication_date: datetime.date | None = None`
  - `upload_date: datetime.date | None = None`
  - `channel_id: ChannelId | None = None`
  - `channel_category: str = ""`
  - `video_description: str = ""`
  - `metadata: dict[str, Any]`
- **Invariants**:
  - `body` cannot be empty or whitespace-only (`DomainValidationError`).
  - `channel_name` must be a valid `ChannelName` Value Object.
  - String inputs for `channel_name` and `channel_id` are automatically coerced to their respective Value Objects.

### 2.2 `CandidateText` Value Object
In [`src/cresmo/domain/value_objects/quality.py`](../../src/cresmo/domain/value_objects/quality.py):
- **Contract**: Strongly-typed container for intermediate LLM transformation outputs.
- **Attributes**:
  - `text: str`: Generated text payload.
  - `stage_name: str`: Identifier of the producing stage.
  - `metadata: dict[str, Any] = field(default_factory=dict)`
- **Invariants**:
  - `text` must not be empty or whitespace-only (`DomainValidationError("CandidateText for '<stage>' cannot be empty.")`).

### 2.3 `VerdictType` & `TypedVerdict` Value Objects
In [`src/cresmo/domain/value_objects/quality.py`](../../src/cresmo/domain/value_objects/quality.py):
- **`VerdictType` (Enum)**:
  - `NOUL = "noul"`: Binary/boolean pass-fail assertion (TypeSafe / rubric style).
  - `CHOICE = "choice"`: Categorical classification selection.
  - `SCORE = "score"`: Continuous normalized rating $[0.0, 1.0]$.
- **`TypedVerdict`**:
  - `criterion: JudgeCriterion`
  - `verdict_type: VerdictType`
  - `passed: bool`
  - `score: float`
  - `choice_value: str | None = None`
  - `confidence: float | None = None`
  - `reasoning: str = ""`
  - `improvement_suggestion: str = ""`

### 2.4 `StageRegistry` & `StageSpec`
In [`src/cresmo/domain/stage_registry.py`](../../src/cresmo/domain/stage_registry.py):
- **`StageSpec` (Data Class)**:
  - `transform_prompt_key: PromptKey | None = None`
  - `required_criteria: tuple[JudgeCriterion, ...] = ()`
  - `judge_prompt_key: PromptKey | None = None`
  - `post_processor: Callable[..., Any] | None = None`
  - `source_extractor: Callable[..., str] | None = None`
  - `candidate_extractor: Callable[..., str] | None = None`
  - `eval_metadata: dict[str, Any]`
- **`StageRegistry` (Domain Catalog)**:
  - Class-level registry `_SPECS: dict[str, StageSpec]`.
  - Methods: `get(stage_name: str) -> StageSpec`, `contains(stage_name: str) -> bool`, `register(stage_name: str, spec: StageSpec) -> None`, `all_stages() -> list[str]`.
  - Initial registered stage: `"fluid_prose"` (Stage 1 reference implementation).

### 2.5 `StageQuarantinedError`
In [`src/cresmo/domain/exceptions.py`](../../src/cresmo/domain/exceptions.py):
- Inherits from `DomainValidationError`.
- Attributes: `stage_name: str`, `content_id: str`, `attempts: int`, `critique: str`, `overall_score: float`.
- Formatted message: `f"Stage '{stage_name}' failed quality evaluation for '{content_id}' after {attempts} attempts (score: {overall_score:.2f}). Quarantined. Critique: {critique}"`.

---

## 3. Ports & Adapters: Critique Synthesis

### 3.1 `CritiqueSynthesizerPort`
In [`src/cresmo/application/ports/critique_synthesizer.py`](../../src/cresmo/application/ports/critique_synthesizer.py):
```python
class CritiqueSynthesizerPort(ABC):
    """Abstract port for synthesizing actionable improvement critique from failed judge evaluations."""

    @abstractmethod
    def synthesize(
        self,
        evaluation: JudgeEvaluation,
        stage_name: str,
    ) -> str:
        """Synthesize directed natural language critique instructing the next generation attempt."""
        ...
```

### 3.2 `OllamaCritiqueAdapter`
In [`src/cresmo/infrastructure/adapters/ollama_critique_adapter.py`](../../src/cresmo/infrastructure/adapters/ollama_critique_adapter.py):
- Implements `CritiqueSynthesizerPort` via local Ollama inference or fallback rule-based extraction.
- Extracts failing criteria reasoning and formats concise, directed improvement directives.

---

## 4. Application Layer: StageDescriptor & Execution Template

### 4.1 `StageDescriptor[TSource, TOutput]`
In [`src/cresmo/application/pipeline/stage_descriptor.py`](../../src/cresmo/application/pipeline/stage_descriptor.py):
- Generic container parameterized over `TSource` and `TOutput`.
- Attributes:
  - `stage_name: str`
  - `transform_prompt_key: PromptKey`
  - `judge_prompt_key: PromptKey | None = None`
  - `eval_spec: StageEvaluationSpec | None = None`
  - `post_processor: Callable[[CandidateText, TSource], TOutput] | None = None`
  - `temperature: float | None = None`
  - `max_attempts: int = 1`
  - `blocking: bool = False`

### 4.2 `StageFactory`
In [`src/cresmo/application/pipeline/stage_factory.py`](../../src/cresmo/application/pipeline/stage_factory.py):
- Resolves `StageSpec` from `StageRegistry.get(stage_name)` and combines it with runtime `PipelineSettings` (e.g. `judge_blocking`, `judge_max_attempts`, stage temperatures) to construct a configured `StageDescriptor`.

### 4.3 `PipelineStageRunner.execute_stage(...)`
In [`src/cresmo/application/pipeline/stage_runner.py`](../../src/cresmo/application/pipeline/stage_runner.py):
- **Signature**:
  ```python
  def execute_stage(
      self,
      stage: str | StageDescriptor[_TSource, _TOutput] | None = None,
      source: _TSource | None = None,
      *,
      descriptor: StageDescriptor[_TSource, _TOutput] | None = None,
      context: PipelineExecutionContext | None = None,
      channel_name: ChannelName | None = None,
      content_id: ContentId | None = None,
      session_id: str | None = None,
      user_id: str | None = None,
      prompt_provider: PromptProviderPort | None = None,
      llm_transformation_port: LLMTransformationPort | None = None,
      channel_id: ChannelId | None = None,
  ) -> _TOutput:
  ```
- **Execution Workflow**:
  1. **Resolve Descriptor**: If `stage` is a string, resolve via `self.stage_factory.build_stage(stage)`. If no factory is present, raise `ValueError`.
  2. **Resolve Provenance**: Extract `channel_name`, `content_id`, `channel_id`, `session_id`, `user_id` from `context` (or individual arguments).
  3. **Determine Attempts**: `effective_max_attempts = max(target_descriptor.max_attempts, self.judge_max_attempts)`.
  4. **Closed-Loop Generation Loop (`attempt = 1 .. effective_max_attempts`)**:
     a. **Prompt Assembly**: Retrieve template from `prompt_provider`. If `attempt > 1` and `critique` is present, append:
        ```text
        [DIRECIONAMENTO CRÍTICO / RETRY]
        Tentativa anterior falhou nos critérios de qualidade. Corrija rigorosamente:
        {critique}
        ```
     b. **Transformation**: Call `llm.transform(prompt=..., temperature=...)`.
     c. **Candidate Wrapping**: Instantiate `candidate = CandidateText(text=raw_output, stage_name=stage_name)`.
     d. **Evaluation Gate**: If `llm_judge` and `eval_spec` are active, evaluate candidate against required criteria.
     e. **Success Path**: If `evaluation.passed`, break out of loop.
     f. **Reflection on Failure**: If not passed and `attempt < effective_max_attempts`:
        - Invoke `self.critique_synthesizer.synthesize(evaluation, stage_name)` to generate targeted feedback.
        - Record OpenTelemetry retry span event and increment Prometheus `cresmo_judge_retries_total`.
  5. **Quarantine Handling (Exhausted Attempts with Failure)**:
     - If `target_descriptor.blocking` or `self.judge_blocking`:
       1. **Ledger Record**: Persist `LedgerEntry(content_id=..., channel_name=..., status=PipelineStatus.QUARANTINED, error_message=...)` via `ledger_port.save_entry(...)`.
       2. **Span Attribution**: Set OpenTelemetry span tags: `quarantined=True`, `quarantine.stage`, `quarantine.critique`, `quarantine.attempts`, `quarantine.overall_score`.
       3. **Prometheus Metric**: Increment `cresmo_stage_quarantines_total` counter with labels `stage` and `channel_name`.
       4. **Fail-Fast Exception**: Raise `StageQuarantinedError(...)`.
  6. **Post-Processing**: If `target_descriptor.post_processor` is configured, invoke `target_descriptor.post_processor(candidate, source)` and return result. Otherwise, return `candidate`.

---

## 5. Acceptance Test Matrix

| Test ID | Component | Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- |
| `TC-STAGE-009` | `CandidateText` | Empty text provided (`""` or `"   "`) | Raises `DomainValidationError` |
| `TC-STAGE-010` | `PipelineStageRunner` | String identifier `"fluid_prose"` with injected `StageFactory` | Resolves descriptor and executes successfully |
| `TC-STAGE-011` | `PipelineStageRunner` | String identifier `"fluid_prose"` without `StageFactory` | Raises `ValueError` ("without an injected StageFactory") |
| `TC-STAGE-012` | `PipelineStageRunner` | Judge passes on attempt 1 | Zero critique synthesis invoked, returns candidate on attempt 1 |
| `TC-STAGE-013` | `PipelineStageRunner` | Judge fails attempt 1, passes attempt 2 | `CritiqueSynthesizerPort` called once; critique injected into prompt for attempt 2; returns attempt 2 output |
| `TC-STAGE-014` | `PipelineStageRunner` | Judge fails all attempts, `blocking=True` | Executes all 4 quarantine protocol steps: SQLite ledger marked QUARANTINED, OTel span tagged, Prometheus counter incremented, raises `StageQuarantinedError` |
| `TC-STAGE-015` | `PipelineStageRunner` | Stage 1 with `post_process_fluid_transcript` | Strips H1 headers, strips accidental complementary sections, and outputs clean `FluidTranscript` |
