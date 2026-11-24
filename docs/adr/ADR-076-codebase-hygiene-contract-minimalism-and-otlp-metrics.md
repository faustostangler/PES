# ADR-076: Codebase Hygiene, Backward-Compatibility Purge, Contract Minimalism & OTLP Metrics

| Field          | Value                                                                                      |
|----------------|--------------------------------------------------------------------------------------------|
| **Status**     | ACCEPTED                                                                                   |
| **Date**       | 2026-11-24                                                                                 |
| **Authors**    | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)            |
| **Scope**      | Cresmo & Identity Bounded Contexts — Domain, Application, Infrastructure, Bootstrap, CLI   |
| **Refines**    | ADR-010, ADR-017, ADR-023, ADR-033, ADR-037, ADR-042, ADR-058, ADR-059, ADR-062, ADR-063, ADR-067, ADR-070, ADR-071, ADR-074 |
| **Supersedes** | ADR-023 §Pull-HTTP Exposition (superseded by Prometheus v3 Native OTLP HTTP push)          |

---

## 1. Context & Architectural Motivation

A full file-by-file audit across all 186 Python modules and 43 resource files in `src/cresmo/` plus `src/config.py` identified accumulated structural debt:
1. **Unwired Dead Stacks & Orphan Bytecode:** `PolarsBatchProcessor` (diverged schema vs. `BatchSource`), `SelectolaxHtmlParser`, and 58 orphaned `.pyc` files remained in the repository alongside unused `polars`, `pyarrow`, and `selectolax` dependencies.
2. **Legacy Backward-Compatibility Shims:** `src/config.py` re-exported 18 `cresmo` symbols; six Typer handlers retained `argparse.Namespace` shims (`args: Any = None`); `PipelineStageRunner`, `quarantine`, `coordinator`, `calibration_metrics`, `discovery/models`, `GeminiJudgeAdapter`, `OllamaLLMAdapter`, `ObsidianVaultAdapter`, and `OpenTelemetryAdapter` preserved fallback paths for retired v1/v2 formats (`content:` 3-part IDs, `/api/generate`, Langfuse v2 `.score()`, `TypedVerdict`, legacy vault stage names).
3. **Oversized Ports & Placebo Settings:** `VaultRepositoryPort` (18 methods), `LedgerRepositoryPort` (5 methods), `AnonymizerPort` (3 methods), `PromptProviderPort`, `LLMTransformationPort`, and `CritiqueSynthesizerPort` exposed unused methods, while 14 configuration fields in `CresmoSettings` had zero production consumers.
4. **Disconnected Prometheus Pull Metrics & High-Cardinality Labels:** `PrometheusMetricsAdapter` buffered metrics only in process RAM (`start_metrics_server` unwired), clashed with host port `9090`, broke ephemeral CLI runs, lacked emitters for 8 of 15 registered metrics, and attached unbounded `content_id`/`incident_id` labels.
5. **Barrel File Sprawl:** 19 operational/heavy packages maintained `__init__.py` re-export barrels that triggered eager imports and obscured canonical module ownership.

---

## 2. Decision

We execute a six-wave remediation under strict TDD Green (`pytest`), `mypy --strict`, and `ruff` (`select = ["E", "F", "W", "B", "I", "UP", "BLE", "RUF100"]`):

1. **Remove Dead Adapters & Orphan Artifacts:** Delete `PolarsBatchProcessor` (`adapters/data/`), `SelectolaxHtmlParser`, their unit tests, dependency entries (`polars`, `pyarrow`, `selectolax`, `prometheus-client`), and stale `.pyc` bytecode. Retain `discover_atomic_inventory.py`, `synthesize_atomic_batch.py`, `reconcile_mocs.py`, `indexing/`, and `PostgresLedgerAdapter` + `persistence/models.py` as explicit active/reserved implementations while fixing `reconcile_mocs` templates and pruning dead internal shims.
2. **Purge Backward-Compatibility Shims & Enforce Single Entrypoint:** Eliminate all `argparse` `args` shims, `src/config.py` (relocating `IamSettings` into `src/identity/infrastructure/settings.py`), 3-part session ID parsing, `TypedVerdict`, `/api/generate` and `.score()` fallbacks, duplicate text/judge/telemetry helpers, and `cresmo.__init__` logging side-effects. Unify CLI execution through `cresmo.presentation.cli:cli_entrypoint` (`no_args_is_help=True`) with centralized exception mapping in `main()`. Preserve explicit operator debug traces (`[SPAN DEBUG]`, `[STAGE]`) while active.
3. **Prompt Catalog Bijection Guardrail:** Enforce fail-fast validation in `load_prompt_catalog()` ensuring non-empty `skills` match `{{skill_block}}` / `{{<skill>}}` placeholders bijectively across `prompts.json` and Markdown templates.
4. **Port Minimalism & Unified Pipeline Ledger Persistence:**
   - Narrow `VaultRepositoryPort` (18 → 14 methods) and demote handler-internal helpers.
   - Narrow `LedgerRepositoryPort` (5 → 3 methods: `is_processed`, `save_entry`, `get_entry`) and persist `RUNNING`, `COMPLETED`, and `FAILED_TRANSFORMATION` states directly inside `CresmoPipeline.execute()`.
   - Narrow `AnonymizerPort` to `mask_mapping(data)`, remove `get_last_prompt_version`, remove `wait_for_warmup` and `thinking_level` from `LLMTransformationPort`, and remove `trace_id` from `CritiqueSynthesizerPort`.
5. **Configuration Single Source of Truth:** Remove 14 placebo config fields (`GapFillerJudgeSettings`, `JudgeSettings.fallback_provider`, `CookieSettings` collapsed to `cookies_file`, `WorkerPoolSettings.subtitle`, `keep_audio`, `inventory_max_attempts`, `PrometheusSettings.port`, `gap_filler_dir`, `brain_csv_*`, `GeminiFreeTierModel`, `JudgeProviderName` re-export) and wire `whisper_model` and `DEFAULT_PROMPTS_RESOURCE_*`.
6. **Prometheus v3 Native OTLP HTTP Metrics (`OtlpMetricsAdapter`):** Replace `prometheus_client` pull scraping with `OtlpMetricsAdapter` pushing via OpenTelemetry `OTLPMetricExporter` (`POST {endpoint}/api/v1/otlp/v1/metrics`), guarded by a fail-silent `probe_prometheus_ready` (`/-/ready`) preflight probe falling back to `NoOpMetricsPort`. Standardize 16 low-cardinality metrics in `MetricName(StrEnum)`, stripping `content_id`, `channel_name`, and `incident_id` labels.
7. **Zero-Barrel Policy:** Empty all 19 operational/adapter `__init__.py` barrels to a 1-line docstring, permitting `__init__.py` re-exports only in the 4 trimmed pure vocabulary/contract facades (`domain/value_objects`, `domain/entities`, `application/ports`, `infrastructure/config`) with `>= 10` consumers and zero heavy I/O dependencies.

---

## 3. Bounded Context & Domain Model Impact

- **IAM Bounded Context:** `IamSettings` / `IdentitySettings` consolidated inside `src/identity/infrastructure/settings.py`; `src/config.py` retired.
- **Cresmo Domain:** `ContentId` length invariants unified via `MIN_CONTENT_ID_LENGTH=1` and `MAX_CONTENT_ID_LENGTH=64` in `constants.py`; `EvaluationContext` carries `judge_prompt_key: PromptKey | None` so judges perform zero stage-name routing.
- **Cresmo Ports & Observability:** `MetricName(StrEnum)` and `MetricsPort.flush()` govern all metrics; `NoOpMetricsAdapter` retired in favor of `NoOpMetricsPort`.

---

## 4. Alternatives Considered

1. **Retain Legacy Shims & Pull Prometheus + Pushgateway:** Rejected; duplicates metric transport mechanisms, breaks ephemeral CLI counters via Pushgateway overwrites, and keeps dead mutation surface in `src/`.
2. **Keep All Package Barrels (`__init__.py`) Globally:** Rejected; eager imports hurt CLI startup latency and hide real dependency edges.

---

## 5. Consequences, Observability, Security & LGPD

- **Positive:** Smaller `mutmut` surface, zero placebo settings, strict `RUF100`/`BLE001` lint enforcement, unified pipeline ledger state across `run`/`sync`/`worker`, and low-cardinality Prometheus TSDB series via OTLP HTTP push.
- **Negative / Trade-offs:** Breaking changes for any external callers relying on retired `__init__.py` barrel imports, `args: Namespace` CLI handlers, or deleted `LedgerRepositoryPort` methods (`mark_processed`, `list_entries`); all internal callers and tests updated in lockstep.
