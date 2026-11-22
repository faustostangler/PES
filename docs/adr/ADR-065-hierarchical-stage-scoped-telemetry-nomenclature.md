# ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature & Dynamic Generation Naming

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-11-21                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Observability & Telemetry — Application, Infrastructure |
| **Relates** | ADR-000, ADR-016, ADR-027, ADR-035, ADR-036, ADR-037, ADR-041, ADR-063 |

---

## 1. Context & Architectural Motivation

Inspection of live Langfuse v4 trace trees and `LangfuseSpanProcessor` debug logs revealed three structural nomenclature flaws remaining after ADR-037 and ADR-063:

1. **Redundant Infix Verbs & Stage Prefixes:**
   - Tier 1 (`cresmo.synthesis_pipeline`) and Tier 1.1 (`cresmo.pipeline.coordinator`) introduced multi-word nouns while Tier 2 (`cresmo.stage.{stage_name}`) inserted an unnecessary `.stage.` infix before `{stage_name}`.
   - Tier 3B (`cresmo.stage.{stage_name}.evaluation`) repeated `.stage.` and used `.evaluation` rather than `.judge`, visually detaching evaluation nodes from generation nodes inside collapsed trace trees.

2. **Static Unscoped LLM Generation Observations (`cresmo.llm.generate`):**
   - Both `GeminiLLMAdapter._execute_transform` and `OllamaLLMAdapter._execute_transform` bound `@observe(name=LLM_GENERATION_SPAN_NAME, as_type="generation")` at class definition time using the static string `"cresmo.llm.generate"`.
   - In flattened cost/latency views, Langfuse generations could not be attributed at a glance to `fluid_prose` vs. `gap_filler`, nor could primary model attempts be separated from secondary model failover (`fallback_model_name`) attempts inside a single generation observation.

3. **Creation-Time Naming Requirement in `LangfuseSpanProcessor`:**
   - `LangfuseSpanProcessor` evaluates `should_export_span` twice per OpenTelemetry span lifecycle — at both `on_start` and `on_end`.
   - Updating `span.update_name(...)` inside the body of a wrapped function occurs *after* `on_start`, leaving start-time logs and processors with the stale static name. Dynamic stage-scoped names must therefore be resolved before `start_as_current_observation` is entered.

---

## 2. Banished Anti-Patterns

This ADR formally bans the following anti-pattern with **zero backward compatibility**:

* **`Static Unscoped Generation Naming*`**: Binding `@observe(name=...)` to a static module-level string on shared LLM adapters when executing inside named pipeline stages, masking both the originating stage and primary-vs-fallback model failover branches.
* **`Late Observation Renaming*`**: Calling `span.update_name(...)` after span creation instead of resolving the canonical stage-scoped name prior to `start_as_current_observation`.

---

## 3. Decision: Hierarchical Stage-Scoped Telemetry Nomenclature

### Pillar 1: Clean 4-Tier Hierarchical Tree
All trace and span identifiers enforce a concise flat-prefix hierarchy anchored under the `cresmo.` Bounded Context namespace:

```text
[Trace]        cresmo.pipeline
  └── [Root]   cresmo.coordinator
        └── [Stage]    cresmo.{stage_name}                              (e.g. cresmo.fluid_prose, cresmo.gap_filler)
              ├── [Gen]    cresmo.{stage_name}.generate[.pass_{N}]           (primary model; .pass_{N} when max_passes > 1)
              ├── [GenFB]  cresmo.{stage_name}.generate_fallback[.pass_{N}]  (model failover fallback)
              └── [Judge]  cresmo.{stage_name}.judge                         (LLM-as-a-judge evaluation)
```

| Tier | Previous (ADR-037 / ADR-063) | Canonical (ADR-065) | SSOT Symbol (`application/ports/telemetry.py`) |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Trace)** | `cresmo.synthesis_pipeline` | `cresmo.pipeline` | `PIPELINE_TRACE_NAME` |
| **Tier 1.1 (Root Span)** | `cresmo.pipeline.coordinator` | `cresmo.coordinator` | `PIPELINE_ROOT_SPAN_NAME` |
| **Tier 2 (Stage Span)** | `cresmo.stage.{stage_name}` | `cresmo.{stage_name}` | `format_stage_span_name(stage_name)` |
| **Tier 3A (Generation — Primary)** | `cresmo.llm.generate` | `cresmo.{stage_name}.generate` or `cresmo.{stage_name}.generate.pass_{N}` *(standalone: `cresmo.llm.generate[.pass_{N}]`)* | `format_stage_generation_span_name(stage_name, pass_num=...)` / `LLM_GENERATION_SPAN_NAME` |
| **Tier 3A (Generation — Fallback)** | *collapsed inside `cresmo.llm.generate`* | `cresmo.{stage_name}.generate_fallback` or `cresmo.{stage_name}.generate_fallback.pass_{N}` *(standalone: `cresmo.llm.generate_fallback[.pass_{N}]`)* | `format_stage_generation_span_name(stage_name, fallback=True, pass_num=...)` / `LLM_GENERATION_FALLBACK_SPAN_NAME` |
| **Tier 3B (Judge Span)** | `cresmo.stage.{stage_name}.evaluation` | `cresmo.{stage_name}.judge` | `format_stage_judge_span_name(stage_name)` |

Semantic separation between Tier 1 (`cresmo.pipeline`) and Tier 1.1 (`cresmo.coordinator`) preserves ADR-037's ban on `Homonymous Trace Root Redundancy*`. Existing attribute keys (`cresmo.stage.*` stage attributes, `cresmo.pipeline.*`, `cresmo.content.*`) remain unchanged.

### Pillar 2: Pure Stdlib `contextvars` Stage & Pass Scopes (Zero Port Bloat)
To preserve strict Hexagonal purity (`Domain -> Application -> Infrastructure`) without adding stage or pass parameters to `LLMTransformationPort.transform(...)`:
- `src/cresmo/application/ports/telemetry.py` maintains pure stdlib `contextvars.ContextVar` scopes (`_ACTIVE_TELEMETRY_STAGE: ContextVar[str | None]` and `_ACTIVE_TELEMETRY_PASS: ContextVar[int | None]`) exposed via:
  - `active_telemetry_stage(stage_name: str)` (context manager with `reset(token)` cleanup and nesting support; clears `_ACTIVE_TELEMETRY_PASS` to `None` on stage entry so nested stages never inherit an outer pass number)
  - `get_active_telemetry_stage() -> str | None`
  - `active_telemetry_pass(pass_num: int)` (context manager validating positive pass index with `reset(token)` cleanup)
  - `get_active_telemetry_pass() -> int | None`
  - `resolve_llm_generation_span_name(stage_name: str | None = None, *, fallback: bool = False, pass_num: int | None = None) -> str`
- Both `measure_stage_execution` (`application/pipeline/stage_telemetry.py`) and concrete/no-op `start_stage_span` implementations (`OpenTelemetryAdapter`, `NoOpTelemetryAdapter`, `NoOpTelemetryPort`) activate `active_telemetry_stage(stage_name)`.
- `generate_stage_candidate` (`application/pipeline/stage_execution.py`) enters `active_telemetry_pass(pass_index)` for multi-pass stages (`max_passes > 1`), matching `trace_id` (`{active_trace_id}_pass_{N}`), while single-pass stages (`max_passes == 1`) leave `_ACTIVE_TELEMETRY_PASS` unset so observations stay concise (`cresmo.fluid_prose.generate`).
- `annotate_llm_span` emits `cresmo.pass_num` (int) on the active generation span whenever `get_active_telemetry_pass()` is not `None`.
- When `LLMTransformationPort.transform(...)` runs outside any active pipeline stage (standalone indexing scripts, critique synthesis outside stages, or direct adapter tests), `resolve_llm_generation_span_name` falls back deterministically to `cresmo.llm.generate[.pass_{N}]` (or `cresmo.llm.generate_fallback[.pass_{N}]`).

### Pillar 3: Creation-Time Dynamic Observation Wrapper & Failover Split
- `src/cresmo/infrastructure/adapters/telemetry/opentelemetry_adapter.py` exports `observe_llm_generation` and `observe_llm_generation_fallback`.
- Each call lazily imports `langfuse.observe` (preserving ADR-053/055 CLI startup speed), resolves the active stage name via `resolve_llm_generation_span_name(fallback=...)`, and enters `observe(name=span_name, as_type="generation")` so `start_as_current_observation` emits the canonical stage-scoped name at `on_start`.
- Both `GeminiLLMAdapter` and `OllamaLLMAdapter` apply `@observe_llm_generation` to `_execute_transform` (`InferenceObservabilityParity`).
- `GeminiLLMAdapter` separates primary model execution (`_execute_transform`, `@observe_llm_generation`) from secondary model failover (`_execute_fallback_transform`, `@observe_llm_generation_fallback`), emitting `cresmo.{stage_name}.generate` on primary attempts and a distinct sibling `cresmo.{stage_name}.generate_fallback` observation whenever non-429 failover triggers.
- **Deterministic Post-Span Flushing:** Both `measure_stage_execution` (`application/pipeline/stage_telemetry.py`) and `CresmoPipeline.execute` (`application/pipeline/coordinator.py`) invoke `telemetry_port.flush()` in an outer `finally` block *after* `start_stage_span` / `start_pipeline_session` exits, ensuring closed parent spans (`cresmo.{stage_name}` and `cresmo.coordinator`) are drained from `BatchSpanProcessor` immediately so Langfuse never renders their children as flattened orphans at the trace root.

---

## 4. Consequences & Supersession Lineage

* **Refines:**
  - **ADR-037:** Replaces 4-tier literal naming (`cresmo.synthesis_pipeline`, `pipeline.coordinator`, `cresmo.stage.{stage}`, `cresmo.llm.generate`, `cresmo.stage.{stage}.evaluation`) with `cresmo.pipeline` $\to$ `cresmo.coordinator` $\to$ `cresmo.{stage}` $\to$ `cresmo.{stage}.generate` / `cresmo.{stage}.generate_fallback` / `cresmo.{stage}.judge`.
  - **ADR-063:** Renames `SYNTHESIS_PIPELINE_TRACE_NAME` to `PIPELINE_TRACE_NAME` (`"cresmo.pipeline"`), upgrades `PIPELINE_ROOT_SPAN_NAME` to `"cresmo.coordinator"`, and replaces static `@observe(name=LLM_GENERATION_SPAN_NAME)` with dynamic creation-time stage-scoped observation wrappers.
* **Positive:** Uniform hierarchical tree readability in Langfuse v4, zero-boilerplate per-stage cost/latency filtering on generation nodes, clear attribution of fallback-model failovers, and `on_start`/`on_end` span name consistency.
* **Breaking:** Dashboards, Saved Views, or tests filtering on `cresmo.synthesis_pipeline`, `cresmo.pipeline.coordinator`, `cresmo.stage.*`, or `.evaluation` must migrate to `cresmo.pipeline`, `cresmo.coordinator`, `cresmo.{stage_name}`, `cresmo.{stage_name}.generate(_fallback)`, and `cresmo.{stage_name}.judge`.

