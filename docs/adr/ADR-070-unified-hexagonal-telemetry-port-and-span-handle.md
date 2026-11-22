# ADR-070: Unified Hexagonal Telemetry Port, Typed Span Handle, and Single-Path Instrumentation

- **Status:** Accepted
- **Date:** 2026-11-22
- **Deciders:** Principal Socio-Technical Architect (Fausto Stangler / Antigravity)
- **Scope:** Cross-Cutting Observability & Telemetry — Application, Infrastructure, Bootstrap
- **Refines / Supersedes:**
  - Refines `ADR-001` (Hexagonal Dependency Rule — purges `opentelemetry` and `langfuse.*` from `application/`)
  - Refines `ADR-003` & `ADR-011` (Unified Inference Observability via injected `TelemetryPort` instead of `@observe` + global span mutation)
  - Refines `ADR-010` (Zero Legacy Shims — eliminates duplicate `NoOpTelemetryAdapter` and `LangfuseJudgeDecorator`)
  - Refines `ADR-016`, `ADR-027`, `ADR-035`, `ADR-036`, `ADR-037`, `ADR-063`, `ADR-065` (preserves 100% of 4-tier hierarchical naming, zero attribute duplication, dynamic version/`git_sha`, and deterministic post-span flush semantics while unifying implementation)
  - Refines `ADR-026` (Rule 5 Bounded Modularity < 500 LOC — splits 825-line `opentelemetry_adapter.py` into focused modules)

---

## 1. Context & Architectural Forces

Architectural audit starting from `src/cresmo/application/pipeline/coordinator.py` down through pipeline orchestration, quarantine, LLM adapters, judge decorators, and telemetry infrastructure exposed severe standardization drift:

1. **Direct Hexagonal Boundary Violations (`application/` Coupled to `opentelemetry` & `langfuse.*`):**
   - Four application modules (`stage_telemetry.py`, `stage_execution.py`, `quarantine.py`, `stage_runner.py`) directly imported `from opentelemetry import trace`.
   - Application functions mutated ambient OpenTelemetry spans via `trace.get_current_span()`, invoking SDK-specific methods (`record_exception`, `set_status(trace.StatusCode.ERROR, ...)`, `get_span_context().span_id`) and writing vendor protocol keys (`"langfuse.observation.level"`, `"langfuse.observation.output"`, `"output.value"`).

2. **Six Competing Telemetry Registration Patterns:**
   - `coordinator.py` called `TelemetryPort.start_pipeline_session()` + `record_session_output()`.
   - `stage_telemetry.py` mixed `TelemetryPort.start_stage_span()` with direct `opentelemetry.trace` error recording and duplicated `active_telemetry_stage()`.
   - `stage_execution.py` opened spans via `TelemetryPort` (`start_stage_evaluation_span`, `start_stage_saturation_span`) while bypassing the port with `trace.get_current_span()` to extract `observation_id` and attach evaluation output.
   - `quarantine.py` ignored `TelemetryPort` altogether and mutated `trace.get_current_span()`.
   - `GeminiLLMAdapter` and `OllamaLLMAdapter` bypassed `TelemetryPort` using `@observe_llm_generation` (direct `langfuse.observe`), global `annotate_llm_span()`, and copy-pasted `langfuse.get_client().flush()`.
   - `LangfuseJudgeDecorator` accepted a raw `langfuse_client` and called `create_score`/`score` + `flush()` directly, bypassing `TelemetryPort.record_score()`.

3. **DRY, SOLID (ISP/OCP/SRP), and YAGNI Violations:**
   - **Bloated, closed Port:** `TelemetryPort` exposed 10 bespoke methods (`start_pipeline_session`, `start_stage_span`, `start_stage_evaluation_span`, `start_stage_saturation_span`, `record_stage_io`, `record_session_output`, `record_judge_evaluation`, `record_session_coherence`, `record_score`, `flush`) all yielding `AbstractContextManager[Any]`. Every new pipeline stage or operation required modifying the Port ABC and every adapter/test double.
   - **Dead Port Methods (YAGNI):** `record_judge_evaluation` had 0 production callers; `record_session_coherence` had 0 active callers (while `record_session_completion_telemetry` must stay prepared for upcoming `atomic_notes` stages).
   - **Duplicate Null-Objects:** `NoOpTelemetryPort` (`application/ports/telemetry.py`) and `NoOpTelemetryAdapter` (`infrastructure/adapters/telemetry/noop.py`) duplicated identical no-op logic and drifted (`NoOpTelemetryAdapter` omitted `start_stage_saturation_span`).
   - **Monolithic Adapter (825 LOC):** `opentelemetry_adapter.py` violated ADR-026 Rule 5 (< 500 LOC), mixing identity parsing, attribute mapping, Langfuse decorators, global helpers, span creation, and flushing.
   - **Flush Storms:** Up to 7 synchronous `flush()` calls chained per execution (`GeminiLLMAdapter` -> `stage_runner` loop -> `LangfuseJudgeDecorator` -> `stage_runner` loop -> `stage_telemetry` -> `coordinator` -> `run_synthesis`).
   - **Stray Production Debug Print & Logging Duplication:** `telemetry_factory.py` printed `[SPAN DEBUG]` to stdout (breaking unit tests), and `logging_config.py` duplicated OTel trace/span/session extraction across stdlib filter and structlog processor.

4. **Upcoming `atomic_notes` Conveyor Readiness:**
   - The conveyor pipeline will sequentially integrate `long_expander`, `wide_expander`, `raw_indexing`, `atomic_inventory`, `atomic_batch`, `reconcile_mocs`, and `duplicate_unification` stages.
   - Telemetry must preserve the `record_session_completion` scaffolding and dynamically reflect all active conveyor stages without requiring Port modifications when `atomic_notes` lands.

---

## 2. Decision

We will **unify all distributed tracing, LLM generation observations, and evaluation scoring behind a 5-method `TelemetryPort` returning a typed, framework-agnostic `TelemetrySpan` handle, injected uniformly across Application and Infrastructure consumers**, because this restores strict Hexagonal isolation, enforces SOLID (OCP/ISP/DIP/SRP) and DRY, eliminates duplicate NoOp adapters and flush storms, and prepares the pipeline seam cleanly for `atomic_notes`.

### Pillar 1: Minimal Open-Closed `TelemetryPort` + Typed `TelemetrySpan` Handle (`application/ports/telemetry.py`)
- Define `SpanKind(StrEnum)` (`SPAN = "span"`, `GENERATION = "generation"`).
- Define frozen, invariant-validated Value Object `SessionTelemetrySpec` encapsulating canonical session metadata (`session_id: PipelineSessionId`, `user_id: UserIdentity`, `channel_tenant_id`, `trace_name`, `channel_id`, `channel_name`, `content_id`, `content_title`, `source`, `raw_characters >= 0`, `raw_words >= 0`, `gap_filler_passes >= 1`, `force_reprocess`, `batch_id`, `video_url`, `publication_date`, `pipeline_version`, `git_sha`, `extra_metadata`).
- Define `TelemetrySpan(Protocol)` exposing `trace_id: str | None`, `span_id: str | None`, `set_attributes(...)`, `set_input(...)`, `set_output(...)`, `add_event(...)`, and `record_error(...)`.
- Define singleton `NOOP_TELEMETRY_SPAN` (`NoOpTelemetrySpan`) and **single canonical Null-Object** `NoOpTelemetryPort(TelemetryPort)`.
- Slim `TelemetryPort(ABC)` to **5 orthogonal methods**:
  1. `start_session(spec: SessionTelemetrySpec) -> AbstractContextManager[TelemetrySpan]`
  2. `start_span(name: str, *, kind: SpanKind = SpanKind.SPAN, attributes: Mapping[str, TelemetryAttributeValue] | None = None, stage_name: str | None = None, record_exceptions: bool = True, flush_on_exit: bool = False) -> AbstractContextManager[TelemetrySpan]`
  3. `current_span() -> TelemetrySpan`
  4. `record_score(*, name: str, value: float, comment: str | None = None, trace_id: str | None = None, observation_id: str | None = None) -> None`
  5. `flush() -> None`
- Preserve all ADR-065 canonical naming functions (`format_stage_span_name`, `format_stage_generation_span_name`, `format_stage_judge_span_name`, `format_stage_saturation_span_name`, `resolve_llm_generation_span_name`) and pure-stdlib `contextvars` scopes (`active_telemetry_stage`, `active_telemetry_pass`, `get_active_telemetry_stage`, `get_active_telemetry_pass`).
- Delete dead `record_judge_evaluation`, `record_session_coherence`, bespoke `start_stage_*` / `record_stage_io` / `record_session_output` methods, and duplicate `infrastructure/adapters/telemetry/noop.py`.

### Pillar 2: Modular Infrastructure Adapter Decomposition (< 500 LOC per Module)
Split `src/cresmo/infrastructure/adapters/telemetry/` into focused single-responsibility modules:
1. `otel_span.py`: `OTelTelemetrySpan` translating `TelemetrySpan` calls to OTel span primitives and official Langfuse protocol attributes (`input.value`, `output.value`, `langfuse.observation.input/output/level`, `langfuse.trace.input/output`, root `cresmo.output.*`), plus `wrap_current_otel_span()`.
2. `session_mapper.py`: pure, OTel-free mapping functions translating `SessionTelemetrySpec` to ADR-034/035/063/065 attributes, tags, canonical root input payload, and Langfuse propagated metadata.
3. `genai.py`: pure `build_genai_attributes(...)` helper centralizing CNCF OTel GenAI Semantic Conventions (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.*`, `gen_ai.request.max_tokens`, `gen_ai.request.temperature`, `cresmo.thinking_level`, `cresmo.pass_num`, `cresmo.trace_id`, `langfuse.session.id`, `langfuse.user.id`).
4. `opentelemetry_adapter.py`: concise `OpenTelemetryAdapter(TelemetryPort)` implementing the 5 Port methods, supporting deterministic post-span flushing (`start_session` always flushes after root span exit; `start_span` flushes when `flush_on_exit=True`), and invoking Langfuse `create_score` (with `score` fallback) in `record_score`.

### Pillar 3: Single-Path Injection Across Application, LLM Adapters, Judges, and Bootstrap
- **Application (`coordinator.py`, `stage_runner.py`, `stage_telemetry.py`, `stage_execution.py`, `quarantine.py`):**
  - Zero imports of `opentelemetry` or `langfuse` anywhere in `src/cresmo/application/` or `src/cresmo/domain/`.
  - `coordinator.py` builds `SessionTelemetrySpec`, opens `with self.telemetry_port.start_session(spec) as root_span:`, writes summary via `root_span.set_output(...)`, and derives `stages_completed` dynamically from `conveyor_steps` for seamless `atomic_notes` onboarding.
  - `measure_stage_execution` opens `telemetry_port.start_span(format_stage_span_name(stage_name), stage_name=stage_name, attributes=..., flush_on_exit=True)` and yields `TelemetrySpan` (eliminating duplicate `active_telemetry_stage` and OTel error bypasses).
  - `stage_runner.py` writes stage input/output directly onto `stage_span` and preserves `record_session_completion(...)` (migrated to `record_score` + `current_span().set_output(...)` + `current_span().add_event("session_coherence", ...)`), keeping the `atomic_notes` seam 100% ready.
  - `stage_execution.py` uses `start_span(format_stage_judge_span_name(...))` and `start_span(format_stage_saturation_span_name(...))`, reading `eval_span.trace_id` and `eval_span.span_id` without OTel SDK imports.
  - `quarantine.py` accepts `telemetry_port: TelemetryPort | None = None` and attaches quarantine attributes via `telemetry_port.current_span().set_attributes(...)`.
- **Infrastructure LLM & Judge Adapters:**
  - `GeminiLLMAdapter` and `OllamaLLMAdapter` accept `telemetry_port: TelemetryPort | None = None` (default `NoOpTelemetryPort()`), open generation spans via `self._telemetry.start_span(resolve_llm_generation_span_name(fallback=...), kind=SpanKind.GENERATION)`, attach input/output and `build_genai_attributes(...)`, and purge `@observe_llm_generation`, `annotate_llm_span`, `langfuse` imports, unused `opentelemetry.trace` imports, and redundant `client.flush()` calls.
  - Replace `LangfuseJudgeDecorator` with `TelemetryJudgeDecorator(inner_judge, telemetry_port)` delegating criterion score emission to `telemetry_port.record_score(...)` without direct `langfuse_client` coupling or redundant flushes.
- **Bootstrap & Logging:**
  - `bootstrap/composition.py`, `adapter_factory.py`, `judge_factory.py`, and `use_case_factory.py` wire the single `TelemetryPort` instance (`OpenTelemetryAdapter` or `NoOpTelemetryPort`) across pipeline, LLM adapters, and judge decorator.
  - `telemetry_factory.py` removes the stray `print("[SPAN DEBUG] ...")` statement and returns `NoOpTelemetryPort()` directly when telemetry is disabled/unreachable.
  - `logging_config.py` extracts `_extract_otel_log_context()` shared by `CresmoOTelTraceCorrelationFilter` and `add_opentelemetry_context`.

---

## 3. Langfuse Ingestion Strategy (Mandatory LLM/AI Compliance)

1. **Trace Taxonomy:**
   - `trace_id`: Active 32-hex OpenTelemetry trace ID (deterministic fallback `cresmo_{channel_token}_{content_id}` when operating under `NoOpTelemetryPort`).
   - `session_id`: `PipelineSessionId` (`{channel_id}:{content_id}` or `{channel_name}:{content_id}`).
   - `user_id`: `UserIdentity.value` (`anonymous`, `system:worker`, `user:{provider}:{subject}`).
   - Contextual tags: `[channel_name, pipeline_version, f"auth:{user.provider}"]` + optional `git:{short_sha}` and `batch:{batch_id}`.
2. **Span Hierarchy (ADR-065 Preserved):**
   - Trace `cresmo.pipeline` -> Root `cresmo.coordinator` (`SpanKind.SPAN`, `is_root=True`) -> Stage `cresmo.{stage_name}` (`SpanKind.SPAN`) -> Children:
     - Primary LLM call: `cresmo.{stage_name}.generate[.pass_{N}]` (`SpanKind.GENERATION`, `langfuse.observation.type="generation"`, CNCF `gen_ai.*` attributes, input/output).
     - Fallback LLM call: `cresmo.{stage_name}.generate_fallback[.pass_{N}]` (`SpanKind.GENERATION`).
     - Judge evaluation: `cresmo.{stage_name}.judge` (`SpanKind.SPAN`, `judge.*` attributes + structured verdict output).
     - Saturation check: `cresmo.{stage_name}.saturation.pass_{N}` (`SpanKind.SPAN`, `cresmo.saturation.*` attributes).
     - Upcoming `atomic_notes` stages (`long_expander`, `wide_expander`, `raw_indexing`, `atomic_inventory`, `atomic_batch`, `reconcile_mocs`, `duplicate_unification`) automatically slot under `cresmo.{stage_name}` + `session_coherence` score/event on completion.
3. **Prompt Version Tracking:** Unchanged — `LangfusePromptProvider` remains decoupled behind `PromptProviderPort` and continues receiving `langfuse_client` at bootstrap for remote prompt registry lookups.
4. **Score Schema & Blocking Thresholds:** Unchanged from `ADR-029`/`ADR-030`/`ADR-060` (`TelemetryJudgeDecorator` emits `{stage_name}.{criterion}` numeric scores bound to `trace_id` and `observation_id`; `record_session_completion_telemetry` emits `session_coherence` in `[0.0, 1.0]`). Blocking thresholds remain governed by `StageConfig.blocking` and `JudgeSettings.judge_pass_threshold` (no new LLM model or rubric introduced).

---

## 4. Alternatives Considered

| Option | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **A. Unified 5-method `TelemetryPort` + `TelemetrySpan` injected across Application & Adapters (Selected)** | Single standard everywhere; 0 OTel imports in Application; preserves real provider tokens and primary/fallback generation split without breaking `LLMTransformationPort`; strict OCP/ISP/DRY/YAGNI; trivial hermetic TDD via `InMemoryTelemetryPort` | Updates Port signatures and telemetry test suites | **Accepted** |
| **B. Pure external `TracingLLMTransformationDecorator` wrapping `LLMTransformationPort`** | LLM adapters have zero telemetry references | Cannot capture real `prompt_token_count`, `candidates_token_count`, `thoughts_token_count`, `effective_thinking_level`, or split primary vs `fallback_model_name` spans without altering `LLMTransformationPort.transform() -> str` return type | **Rejected** |
| **C. Keep 10-method `TelemetryPort` and add more bespoke methods (`record_quarantine`, `record_evaluation_output`)** | Smaller immediate diff | Perpetuates method explosion (ISP/OCP violation), keeps 825-line adapter monolith, duplicate NoOp classes, and 7x flush cascade | **Rejected** |

---

## 5. Banned Anti-Patterns
1. **`*Application-to-OTel SDK Leak*`**: Importing `opentelemetry` or writing `"langfuse.*"` attribute keys inside `src/cresmo/application/` or `src/cresmo/domain/`.
2. **`*Bespoke Span Method Explosion*`**: Adding one-off `start_<feature>_span` or `record_<feature>_output` methods to `TelemetryPort` instead of using `start_span(...)` + `TelemetrySpan`.
3. **`*Duplicate Null-Object Drift*`**: Maintaining separate `NoOpTelemetryPort` and `NoOpTelemetryAdapter` classes.
4. **`*Inline Flush Cascade*`**: Calling `langfuse.get_client().flush()` inside leaf LLM adapters, judge decorators, or inner retry loops instead of boundary exits (`start_session` / `start_span(flush_on_exit=True)`).
5. **`*Ambient Global Span Bypass*`**: Calling `trace.get_current_span()` outside `src/cresmo/infrastructure/adapters/telemetry/` and `src/cresmo/infrastructure/logging_config.py`.

---

## 6. Consequences
- **Positive:** 100% AST-verified Hexagonal purity across `domain/` and `application/`; every telemetry consumer follows one uniform injectable contract; `opentelemetry_adapter.py` drops from 825 LOC to < 220 LOC across cohesive modules; `atomic_notes` conveyor stages require zero telemetry port changes; hermetic tests replace brittle `patch("...trace.get_current_span")` with `InMemoryTelemetryPort`.
- **Negative / Breaking:** Callers and tests referencing removed legacy methods (`start_pipeline_session`, `start_stage_span`, `start_stage_evaluation_span`, `start_stage_saturation_span`, `record_stage_io`, `record_session_output`, `record_session_coherence`, `record_judge_evaluation`, `NoOpTelemetryAdapter`, `LangfuseJudgeDecorator`) must migrate to the unified `TelemetryPort` / `TelemetrySpan` / `TelemetryJudgeDecorator` APIs.
- **Security / LGPD:** Preserves `ADR-017` export-stage PII masking hook (`mask_otel_spans` via `AnonymizerPort`) and `ADR-014` fail-fast preflight probe returning `NoOpTelemetryPort` with zero network threads when Langfuse is unreachable.
