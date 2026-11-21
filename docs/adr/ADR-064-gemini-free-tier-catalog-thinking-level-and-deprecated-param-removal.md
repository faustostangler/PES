# ADR-064: Gemini Free-Tier Catalog, `thinking_level` Governance, Deprecated Parameter Removal & Adapter Hardening

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-11-20                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Infrastructure / Cognitive & Configuration (`src/config.py`, `src/cresmo/infrastructure/`, `src/cresmo/bootstrap/`, `evals/`) |
| **Relates** | ADR-000, ADR-005, ADR-011, ADR-026, ADR-029, ADR-041, ADR-062, ADR-063 |

---

## 1. Context & Architectural Motivation

Live production profiling and Gemini API documentation inspection (November 2026) uncovered five interconnected defects causing atypical multi-minute latency, silent fallbacks, and deprecated parameter warnings across `GeminiLLMAdapter`, `GeminiJudgeAdapter`, and `CresmoSettings`:

1. **Uncontrolled Dynamic Thinking Overhead:**
   - Neither `GeminiLLMAdapter` nor `GeminiJudgeAdapter` populated `types.ThinkingConfig(thinking_level=...)` on `GenerateContentConfig`.
   - `gemini-3.8-flash` defaults to `medium` dynamic thinking and `gemini-4-hydrogen` defaults to `high`, causing synchronous `generate_content` requests to stall during multi-step internal reasoning before emitting output tokens.
   - `max_output_tokens=8192` is shared between thinking tokens and response tokens on Gemini 3.x/4 models, creating truncation risks whenever reasoning spikes.

2. **Suboptimal Default Model & Dead Same-Model Fallback:**
   - `DEFAULT_GEMINI_MODEL` and `gemini_fallback_model` were both set to `"gemini-3.8-flash"`, evaluating `self.fallback_model_name != self.model_name` to `False` and rendering model failover completely inactive.
   - Meanwhile, `gemini-3.5-flash-lite` provides the lowest latency, `minimal`/`low`/`medium`/`high` thinking support, and generous Free-Tier availability for high-throughput synthesis and evaluation.

3. **Incomplete Free-Tier Model Enumeration in Configuration:**
   - Operators lacked a typed, documented SSOT catalog of every Google Gemini API Free-Tier text and multimodal model (`Gemini 4 Hydrogen`, `Gemini 3.8 Flash`, `Gemini 3.6 Flash`, `Gemini 3.5 Flash-Lite`, `Gemini 3.1 Flash-Lite`, `Gemini 3 Flash Preview`, `Gemma 4 31B/26B`, and legacy `Gemini 2.5` series) segregated from Paid-only models (`gemini-4-carbon`, `gemini-4-argon`, `gemini-4-neon`, `gemini-3.1-pro-preview`).

4. **Deprecated Sampling Parameters & Duplicated Transient Retry Logic:**
   - Gemini 3.5 Flash-Lite, 3.6 Flash, 3.8 Flash, and Gemini 4 deprecate `temperature`, `top_p`, and `top_k` (ignored now and returning HTTP 400 in upcoming model versions). Yet `GeminiLLMAdapter`, `GeminiJudgeAdapter`, and `CresmoSettings.judge_temperature` still forwarded `temperature` into `GenerateContentConfig`.
   - `TRANSIENT_NETWORK_PATTERNS`, `_is_transient_genai_error`, and `_is_transient_cluster_error` were copy-pasted between `gemini_adapter.py` and `gemini_judge.py`, with silent 5-attempt retries against 300s sockets (~25-minute worst-case hang).

---

## 2. Banished Anti-Patterns

* **`UnboundedThinkingLatency*`**: Invoking Gemini 3.x/4 or Gemma 4 endpoints without explicit `thinking_level` configuration, inheriting high-latency server defaults silently.
* **`DeadSameModelFallback*`**: Configuring `gemini_fallback_model == gemini_model`, disabling secondary model resilience.
* **`DeprecatedGeminiSamplingParams*`**: Sending `temperature`, `top_p`, or `top_k` to Gemini 3.5+/4 endpoints instead of governing determinism via `system_instruction` and `thinking_level`.
* **`DuplicatedAdapterRetryLogic*`**: Copying transient HTTP/cluster error classifiers across LLM and Judge adapters instead of extracting a shared infrastructure helper (`gemini_common.py`).

---

## 3. Decision

### 3.1 Canonical Free-Tier Catalog & Fast Defaults
- **Primary & Judge Default:** `DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"`, `DEFAULT_JUDGE_GEMINI_MODEL = "gemini-3.5-flash-lite"`.
- **Distinct Fallback:** `DEFAULT_GEMINI_FALLBACK_MODEL = "gemini-3.6-flash"`.
- **Default Thinking & Output Ceiling:** `DEFAULT_GEMINI_THINKING_LEVEL = "low"`, `DEFAULT_GEMINI_MAX_OUTPUT_TOKENS = 32_768` (safe across Gemma 4's 32K ceiling and Gemini 3.5+/4's 64K sync cap).
- **Free-Tier Text & Multimodal Catalog (`GEMINI_FREE_TIER_MODELS` / `GeminiFreeTierModel`):** Defined as SSOT in `src/cresmo/infrastructure/config.py` and re-exported in root `src/config.py`:
  1. `gemini-3.5-flash-lite`
  2. `gemini-3.8-flash`
  3. `gemini-3.6-flash`
  4. `gemini-4-hydrogen`
  5. `gemini-3.1-flash-lite`
  6. `gemini-3-flash-preview`
  7. `gemma-4-31b-it`
  8. `gemma-4-26b-a4b-it`
  9. `gemini-2.5-flash-lite`
  10. `gemini-2.5-flash`
  11. `gemini-2.5-pro`
- Paid-only models (`gemini-4-carbon`, `gemini-4-argon`, `gemini-4-neon`, `gemini-3.1-pro-preview`) are deliberately excluded from `GEMINI_FREE_TIER_MODELS`.
- `resolve_model_spec` in `src/cresmo/application/evals/calibration_runner.py` and `evals/benchmark_fluid_prose.py` recognizes both `gemini*` and `gemma*` prefixes as provider `"gemini"`.

### 3.2 `ThinkingLevelPolicy` & Model-Aware Clamping (`gemini_common.py`)
`CresmoSettings` introduces `gemini_thinking_level` (`GEMINI_THINKING_LEVEL` / `CRESMO_GEMINI_THINKING_LEVEL`, default `"low"`) and `judge_gemini_thinking_level` (`JUDGE_GEMINI_THINKING_LEVEL` / `CRESMO_JUDGE_GEMINI_THINKING_LEVEL`, default `"low"`), plus `gemini_max_output_tokens` (`GEMINI_MAX_OUTPUT_TOKENS` / `CRESMO_GEMINI_MAX_OUTPUT_TOKENS`, default `32768`, bounds `256..1_048_576`).

To ensure changing `GEMINI_MODEL` across any entry in `GEMINI_FREE_TIER_MODELS` never raises HTTP 400 on unsupported thinking levels, `resolve_effective_thinking_level` and `build_thinking_config` in `src/cresmo/infrastructure/adapters/llm/gemini_common.py` apply deterministic model-aware clamping:

| Model Family | Supported Levels | Clamping Behavior |
| :--- | :--- | :--- |
| `gemma-4-*` | `minimal`, `high` | `minimal`/`low` $\to$ `minimal`; `medium`/`high`/`xhigh` $\to$ `high` |
| `gemini-4-hydrogen` | `low`, `medium`, `high`, `xhigh` | `minimal` $\to$ `low`; others preserved |
| `gemini-3.8-*`, `gemini-4-*` (non-hydrogen), `gemini-3.1-pro*`, `gemini-2.5-*` | `low`, `medium`, `high` | `minimal` $\to$ `low`; `xhigh` $\to$ `high` |
| `gemini-3.5-flash-lite`, `gemini-3.6-flash`, `gemini-3-flash-preview`, `gemini-3.1-flash-lite`, other | `minimal`, `low`, `medium`, `high` | `xhigh` $\to$ `high`; others preserved |

When `GeminiLLMAdapter` fails over to `fallback_model_name`, it recomputes `build_thinking_config(active_model, requested_thinking_level)` specifically for the fallback model and logs the fallback warning.

### 3.3 Removal of Deprecated Gemini Sampling Parameters
- Remove `temperature` from `types.GenerateContentConfig` in both `GeminiLLMAdapter` and `GeminiJudgeAdapter`.
- Remove `default_temperature` from `GeminiLLMAdapter.__init__`, `temperature` from `GeminiJudgeAdapter.__init__`, and `judge_temperature` / `DEFAULT_JUDGE_TEMPERATURE` from `CresmoSettings` and `src/cresmo/bootstrap/factories/`.
- Preserve `temperature: float | None = None` on `LLMTransformationPort.transform(...)` and `llm_synthesis_temperature` / `llm_indexing_temperature` on `CresmoSettings` strictly for local `OllamaLLMAdapter` LSP compatibility (documented as Ollama-only; ignored by `GeminiLLMAdapter`).
- Extend `LLMTransformationPort.transform(...)` with optional keyword-only `thinking_level: str | None = None` and `PipelineSettingsProtocol` / `DefaultPipelineSettings` with `gemini_thinking_level`.

### 3.4 Shared Resilience, Retry Bounds & Thinking Telemetry
- Extract `TRANSIENT_NETWORK_PATTERNS`, `is_transient_genai_error`, `is_transient_cluster_error`, and `log_gemini_retry_attempt` into `src/cresmo/infrastructure/adapters/llm/gemini_common.py` (preserving backward-compatible symbol imports in `gemini_adapter.py` and `gemini_judge.py`).
- Bound tenacity cluster retries on `5xx`/network errors to `stop_after_attempt(3)` with structured `before_sleep=log_gemini_retry_attempt` visibility.
- Extend `annotate_llm_span(...)` in `src/cresmo/infrastructure/adapters/telemetry/opentelemetry_adapter.py` with optional `thinking_level` (`cresmo.thinking_level`) and `thinking_tokens` (`gen_ai.usage.reasoning_tokens`, extracted from `usage_metadata.thoughts_token_count`).

---

## 4. Consequences

* **Positive:** Dramatically lower inference latency by defaulting to `gemini-3.5-flash-lite` with `thinking_level="low"`, clean fallback to `gemini-3.6-flash`, zero HTTP 400 risk when swapping any of the 11 Free-Tier models, future-proof compliance against Gemini 4 parameter deprecations, and unified retry/thinking telemetry.
* **Negative / Breaking:** Callers passing `GeminiLLMAdapter(..., default_temperature=...)`, `GeminiJudgeAdapter(..., temperature=...)`, or `CresmoSettings(judge_temperature=...)` must remove those deprecated arguments; downstream tests and `evals/benchmark_fluid_prose.py` are updated in tandem.

