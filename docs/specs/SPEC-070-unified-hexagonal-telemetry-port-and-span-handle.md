# SPEC-070: Unified Hexagonal Telemetry Port & Typed Span Handle

- **Related ADR:** [ADR-070](../adr/ADR-070-unified-hexagonal-telemetry-port-and-span-handle.md)
- **Status:** Accepted
- **Date:** 2026-11-22

---

## 1. Application Port Contracts (`src/cresmo/application/ports/telemetry.py`)

### 1.1 Types & Value Objects
- `TelemetryAttributeValue: TypeAlias = str | int | float | bool | tuple[str, ...]`
- `SpanKind(StrEnum)`:
  - `SPAN = "span"`
  - `GENERATION = "generation"`
- `SessionTelemetrySpec` (frozen dataclass with `slots=True`):
  - Fields:
    - `session_id: PipelineSessionId`
    - `user_id: UserIdentity`
    - `channel_tenant_id: str | None = None`
    - `trace_name: str | None = None`
    - `channel_id: str = ""`
    - `channel_name: str = ""`
    - `content_id: str = ""`
    - `content_title: str = ""`
    - `source: str = "transcript"`
    - `raw_characters: int = 0`
    - `raw_words: int = 0`
    - `gap_filler_passes: int = 1`
    - `force_reprocess: bool = False`
    - `batch_id: str | None = None`
    - `video_url: str | None = None`
    - `publication_date: str | None = None`
    - `pipeline_version: str | None = None`
    - `git_sha: str | None = None`
    - `extra_metadata: Mapping[str, TelemetryAttributeValue] = field(default_factory=dict)`
  - Construction invariants (`__post_init__`):
    - `raw_characters < 0` -> raises `ValueError("raw_characters must be >= 0")`
    - `raw_words < 0` -> raises `ValueError("raw_words must be >= 0")`
    - `gap_filler_passes < 1` or `isinstance(gap_filler_passes, bool)` -> raises `ValueError("gap_filler_passes must be >= 1")`

### 1.2 `TelemetrySpan` Protocol & `NoOpTelemetrySpan`
- `TelemetrySpan(Protocol)`:
  - `@property def trace_id(self) -> str | None`
  - `@property def span_id(self) -> str | None`
  - `def set_attributes(self, attributes: Mapping[str, TelemetryAttributeValue]) -> None`
  - `def set_input(self, payload: Mapping[str, Any] | Sequence[Any] | str) -> None`
  - `def set_output(self, payload: Mapping[str, Any] | Sequence[Any] | str) -> None`
  - `def add_event(self, name: str, attributes: Mapping[str, TelemetryAttributeValue] | None = None) -> None`
  - `def record_error(self, exc: BaseException) -> None`
- `NoOpTelemetrySpan` implements `TelemetrySpan`: `trace_id` and `span_id` return `None`; all mutating methods are pure no-ops.
- Singleton `NOOP_TELEMETRY_SPAN: Final[NoOpTelemetrySpan] = NoOpTelemetrySpan()`.

### 1.3 `TelemetryPort` ABC (5 Methods) & Single `NoOpTelemetryPort`
- `TelemetryPort(ABC)`:
  1. `@abstractmethod def start_session(self, spec: SessionTelemetrySpec) -> AbstractContextManager[TelemetrySpan]`
  2. `@abstractmethod def start_span(self, name: str, *, kind: SpanKind = SpanKind.SPAN, attributes: Mapping[str, TelemetryAttributeValue] | None = None, stage_name: str | None = None, record_exceptions: bool = True, flush_on_exit: bool = False) -> AbstractContextManager[TelemetrySpan]`
  3. `@abstractmethod def current_span(self) -> TelemetrySpan`
  4. `@abstractmethod def record_score(self, *, name: str, value: float, comment: str | None = None, trace_id: str | None = None, observation_id: str | None = None) -> None`
  5. `def flush(self) -> None` (default no-op)
- `NoOpTelemetryPort(TelemetryPort)`:
  - `start_session` yields `NOOP_TELEMETRY_SPAN`.
  - `start_span` binds `active_telemetry_stage(stage_name)` iff `stage_name is not None`, then yields `NOOP_TELEMETRY_SPAN`.
  - `current_span` returns `NOOP_TELEMETRY_SPAN`.
  - `record_score` and `flush` are no-ops.
- Preserves all ADR-065 naming/contextvar symbols (`PIPELINE_TRACE_NAME`, `PIPELINE_ROOT_SPAN_NAME`, `LLM_GENERATION_SPAN_NAME`, `LLM_GENERATION_FALLBACK_SPAN_NAME`, `format_stage_span_name`, `format_stage_generation_span_name`, `format_stage_judge_span_name`, `format_stage_saturation_span_name`, `resolve_llm_generation_span_name`, `active_telemetry_stage`, `active_telemetry_pass`, `get_active_telemetry_stage`, `get_active_telemetry_pass`).
- Removed symbols (`ADR-010`): `start_pipeline_session`, `start_stage_span`, `start_stage_evaluation_span`, `start_stage_saturation_span`, `record_judge_evaluation`, `record_session_coherence`, `record_session_output`, `record_stage_io`.

---

## 2. Infrastructure Telemetry Modules (`src/cresmo/infrastructure/adapters/telemetry/`)

### 2.1 `otel_span.py` (`OTelTelemetrySpan`)
- Wraps an OpenTelemetry `Span` with `is_root: bool = False`.
- `trace_id`: returns 32-char lowercase hex (`format(ctx.trace_id, "032x")`) when span is recording and `ctx.trace_id != 0`; else `None`.
- `span_id`: returns 16-char lowercase hex (`format(ctx.span_id, "016x")`) when span is recording and `ctx.span_id != 0`; else `None`.
- `set_attributes(attributes)`: no-op if not recording; skips non-OTel values cleanly and writes `str | int | float | bool | tuple[str, ...]` via `span.set_attribute`.
- `set_input(payload)`: no-op if not recording; serializes non-`str` via `json.dumps(payload, default=str)`; sets `input.value` and `langfuse.observation.input`, plus `langfuse.trace.input` iff `is_root`.
- `set_output(payload)`: no-op if not recording; serializes non-`str` via `json.dumps(payload, default=str)`; sets `output.value` and `langfuse.observation.output`, plus `langfuse.trace.output` iff `is_root`. When `is_root` and `isinstance(payload, Mapping)`, also sets `cresmo.output.<key> = str(val)` for each key/value (ADR-037/063).
- `add_event(name, attributes)`: no-op if not recording; delegates to `span.add_event(name, attributes=dict(attributes) if attributes else None)`.
- `record_error(exc)`: no-op if not recording; invokes `span.record_exception(exc)`, `span.set_status(trace.StatusCode.ERROR, str(exc))`, and `span.set_attribute("langfuse.observation.level", "ERROR")`.
- `wrap_current_otel_span(*, is_root: bool = False) -> TelemetrySpan`: returns `OTelTelemetrySpan(current, is_root=is_root)` if `current` is recording, else `NOOP_TELEMETRY_SPAN`.

### 2.2 `session_mapper.py` (Pure Mapping Functions — Zero OTel/Langfuse Imports)
- `parse_session_parts(session_id: PipelineSessionId) -> tuple[str, str]`: parses `{channel}:{content}` or `content:{channel}:{content}`.
- `resolve_root_operation_name(trace_name: str | None) -> tuple[str, str]`:
  - Returns `(resolved_trace_name, root_operation)`.
  - `trace_name is None` or in `("cresmo.pipeline.execution", "cresmo.synthesis_pipeline", PIPELINE_TRACE_NAME)` -> `(trace_name or PIPELINE_TRACE_NAME, PIPELINE_ROOT_SPAN_NAME)`.
  - Custom `trace_name` -> `(trace_name, trace_name)`.
- `build_session_span_attributes(spec: SessionTelemetrySpec, *, pipeline_version: str, git_sha: str | None) -> tuple[dict[str, Any], list[str], dict[str, Any]]`:
  - Resolves algorithmic pair (`cresmo.channel.id`, `cresmo.content.id`), cognitive pair (`cresmo.channel.name`, `cresmo.content.title`), `cresmo.tenant_id`, `cresmo.user.*`, `cresmo.pipeline.version`, optional 8-char `cresmo.pipeline.git_sha`, optional `cresmo.batch_id`, first-class `cresmo.content.*` (`source`, `word_count`, `char_count`, optional `publication_date`), `cresmo.pipeline.gap_filler_passes`, `cresmo.pipeline.force_reprocess`, and `cresmo.metadata.<k>` for `spec.extra_metadata` keys not shadowing canonical keys.
  - Emits official Langfuse protocol keys ONLY: `langfuse.observation.type="span"`, `langfuse.session.id`, `langfuse.user.id`, `langfuse.trace.tags`, `langfuse.trace.name`. Zero loose `langfuse.input.*` keys (ADR-063).
  - Builds canonical `input_payload` dict with ID-ID parity (`channel_id`, `content_id`), TXT-TXT parity (`channel_name`, `content_title`), `raw_characters`, `raw_words`, optional `batch_id`, and optional `video_url`.
- `build_propagated_trace_metadata(attributes: Mapping[str, Any]) -> dict[str, str]`: truncates propagated values (`channel_id`, `channel_name`, `content_id`, `content_title`, `batch_id`) to 200 chars.

### 2.3 `genai.py` (Pure GenAI Semantic Conventions Builder)
- `build_genai_attributes(*, system: str, model: str, prompt_tokens: int, candidate_tokens: int, session_id: str | None = None, user_id: str | None = None, trace_id: str | None = None, temperature: float | None = None, max_tokens: int | None = None, thinking_level: str | None = None, thinking_tokens: int | None = None, pass_num: int | None = None) -> dict[str, TelemetryAttributeValue]`:
  - Emits `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`.
  - Conditionally emits `langfuse.session.id`, `langfuse.user.id`, `cresmo.trace_id`, `gen_ai.request.temperature` + `cresmo.temperature`, `gen_ai.request.max_tokens`, `cresmo.thinking_level`, `gen_ai.usage.reasoning_tokens`, and `cresmo.pass_num` (falling back to `get_active_telemetry_pass()` when `pass_num is None`).

### 2.4 `opentelemetry_adapter.py` (`OpenTelemetryAdapter`, < 500 LOC)
- Implements the 5 methods of `TelemetryPort`:
  - `start_session(spec)`: opens root span via `self._tracer.start_as_current_span(root_operation, attributes=session_attributes)`, sets root input via `wrapped.set_input(input_payload)`, activates `propagate_attributes(...)` when `self._langfuse is not None`, records errors on uncaught exceptions, and **flushes in outer `finally:` AFTER root span closes**.
  - `start_span(name, *, kind=SpanKind.SPAN, attributes=None, stage_name=None, record_exceptions=True, flush_on_exit=False)`: builds creation-time attributes `{"langfuse.observation.type": kind.value, ...}`, enters `active_telemetry_stage(stage_name)` if provided, opens `self._tracer.start_as_current_span(name, attributes=init_attrs)`, yields `OTelTelemetrySpan(otel_span)`, records exception on error iff `record_exceptions=True`, and flushes in outer `finally:` AFTER span closes iff `flush_on_exit=True`.
  - `current_span()`: delegates to `wrap_current_otel_span()`.
  - `record_score(*, name, value, comment=None, trace_id=None, observation_id=None)`: resolves missing `observation_id` from active recording span (`span_id`), adds `"telemetry_score"` event to active span, and invokes `create_score` (or fallback `score`) on `self._langfuse` when configured (fail-silent on backend error).
  - `flush()`: flushes `self._langfuse` (only when `self._langfuse is not None` — no spurious `langfuse.get_client()` fallback when running without Langfuse client!) and invokes `tracer_provider.force_flush(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)` when callable.
- File `src/cresmo/infrastructure/adapters/telemetry/noop.py` is deleted (`NoOpTelemetryPort` is the single Null-Object).

---

## 3. Application & Adapter Consumer Contracts

### 3.1 `coordinator.py` (`CresmoPipeline`)
- Constructs `SessionTelemetrySpec` from `raw`, `user_identity`, `gap_filler_passes`, `force_reprocess`, `batch_id`.
- Opens `with self.telemetry_port.start_session(session_spec) as root_span:`.
- On idempotent skip: calls `root_span.set_output({"status": "SKIPPED_IDEMPOTENT", "reason": "Existing content already processed", "content_id": content.id.value})`.
- On completion: calls `root_span.set_output(...)` with `stages_completed = [step.value for step in conveyor_steps]` and `stage = conveyor_steps[-1].value` (ready for upcoming `atomic_notes` stages).
- No redundant manual `try ... finally: self.telemetry_port.flush()` wrapper (`start_session` guarantees post-span flush on both normal return and exception).

### 3.2 `stage_telemetry.py`, `stage_runner.py`, `stage_execution.py`, `quarantine.py`
- **AST Import Purity Invariant**: ZERO imports of `opentelemetry` or `langfuse` anywhere in `src/cresmo/application/` or `src/cresmo/domain/`.
- `measure_stage_execution` opens `telemetry_port.start_span(format_stage_span_name(stage_name), stage_name=stage_name, attributes=prefixed_attrs, record_exceptions=True, flush_on_exit=True)` and yields `TelemetrySpan` (no duplicate `active_telemetry_stage`, no `trace.get_current_span()`).
- `PipelineStageRunner.execute_stage` writes stage input/output via `stage_span.set_input(...)` and `stage_span.set_output(...)`, passes `telemetry_port=self.telemetry_port` to `record_stage_quarantine`, and removes mid-loop redundant `flush()` calls.
- `PipelineStageRunner.record_session_completion` & `record_session_completion_telemetry` remain intact for `atomic_notes` readiness, emitting Prometheus metrics + `telemetry_port.record_score(name="session_coherence", ...)` + `active_span.set_output(...)` + `active_span.add_event("session_coherence", ...)`.
- `resolve_active_trace_id` accepts `telemetry_port: TelemetryPort | None = None` / `span: TelemetrySpan | None = None`, using `active_span.trace_id` before deterministic `cresmo_{ch_token}_{cid}` fallback.
- `generate_stage_candidate` opens saturation snapshots via `telemetry_port.start_span(format_stage_saturation_span_name(stage_name, pass_num=pass_index), attributes=...)`.
- `evaluate_stage_candidate` opens `runner.telemetry_port.start_span(format_stage_judge_span_name(stage_config.stage_name), attributes={"judge.stage_name": ..., "judge.attempt": attempt}) as eval_span`, derives `active_trace_id` from `eval_span.trace_id` (or deterministic fallback) and `observation_id = eval_span.span_id`, and attaches verdict attributes + output via `eval_span.set_attributes(...)` / `eval_span.set_output(...)`.
- `record_stage_quarantine` accepts `telemetry_port: TelemetryPort | None = None` and attaches quarantine attributes via `(telemetry_port or NoOpTelemetryPort()).current_span().set_attributes(...)`.

### 3.3 LLM Adapters, Judge Decorator, Bootstrap, and Logging
- `GeminiLLMAdapter` and `OllamaLLMAdapter`:
  - Accept `telemetry_port: TelemetryPort | None = None` (default `NoOpTelemetryPort()`).
  - Open `with self._telemetry.start_span(resolve_llm_generation_span_name(fallback=...), kind=SpanKind.GENERATION) as span:`, attach `span.set_input(prompt.to_dict_list())`, `span.set_attributes(build_genai_attributes(...))`, `span.set_output(response_text)`.
  - Zero `langfuse` imports, zero `opentelemetry` imports, zero `@observe_llm_generation`, zero inline `client.flush()`.
- `TelemetryJudgeDecorator` (`src/cresmo/infrastructure/adapters/judges/telemetry_decorator.py`):
  - Replaces `langfuse_decorator.py` (`LangfuseJudgeDecorator` deleted per `ADR-010`).
  - Accepts `inner_judge: LlmJudgePort` and `telemetry_port: TelemetryPort | None = None` (default `NoOpTelemetryPort()`).
  - Emits each criterion score via `self._telemetry.record_score(name=..., value=float(score.score), comment=score.reasoning, trace_id=effective_trace_id, observation_id=context.observation_id)` with fail-silent warning logging and zero inline `flush()`.
- `bootstrap/`:
  - `telemetry_factory.py`: retains `print("[SPAN DEBUG] ...")` temporarily (marked `TEMPORARY`) for live OTel export verification; `build_telemetry_adapter` returns `OpenTelemetryAdapter(...)` or `NoOpTelemetryPort()`.
  - `composition.py`, `adapter_factory.py`, `judge_factory.py`, `use_case_factory.py`: pass `telemetry_port` to LLM adapters and judge factory (retaining `langfuse_client` only for `build_telemetry_adapter` and `build_prompt_provider`).
- `logging_config.py`: extracts `_extract_otel_log_context() -> tuple[str, str, str]` shared by `CresmoOTelTraceCorrelationFilter` and `add_opentelemetry_context`.

---

## 4. Test Strategy & Acceptance Gates
1. **Hermetic Test Fake (`tests/doubles/telemetry_fake.py`)**: `InMemoryTelemetryPort`, `RecordedSpan`, `RecordedScore` recording spans, hierarchy (`parent_span_id`), attributes, input/output, events, errors, scores, and flush counts without OTel SDK dependencies.
2. **AST Architectural Purity Test (`tests/cresmo/unit/application/test_telemetry_hexagonal_purity.py`)**:
   - Scans every `.py` file under `src/cresmo/domain/` and `src/cresmo/application/`: asserts 0 imports of `opentelemetry` or `langfuse`.
   - Scans every `.py` file under `src/cresmo/infrastructure/adapters/llm/` and `src/cresmo/infrastructure/adapters/judges/`: asserts 0 imports of `opentelemetry` or `langfuse`.
   - Asserts `src/cresmo/infrastructure/adapters/telemetry/noop.py` and `src/cresmo/infrastructure/adapters/judges/langfuse_decorator.py` do not exist.
3. **Unit & Integration Suites**:
   - `SessionTelemetrySpec` invariant boundary tests (`raw_characters < 0`, `raw_words < 0`, `gap_filler_passes < 1`, bool pass).
   - Pure unit tests for `session_mapper.py`, `genai.py`, `otel_span.py`, `TelemetryJudgeDecorator`.
   - OTel SDK `InMemorySpanExporter` integration tests for `OpenTelemetryAdapter` + `CresmoPipeline` verifying ADR-065 4-tier tree, ADR-063 zero duplication, and post-span flush ordering.
   - All existing pipeline, stage runner, quarantine, LLM adapter, judge, logging, and bootstrap suites updated and passing.
4. **Quality Gates**:
   - `uv run pytest` (full suite green)
   - `uv run ruff check src/ tests/` (0 issues)
   - `uv run mypy src/` (`--strict`, 0 errors)
   - `mutmut` on core modified Application & Telemetry modules: **0 surviving mutants** in Domain/Application, `< 5%` (target 0%) in Infrastructure.
   - `stangler-scheimpflug` pre-commit architectural audit passed.
