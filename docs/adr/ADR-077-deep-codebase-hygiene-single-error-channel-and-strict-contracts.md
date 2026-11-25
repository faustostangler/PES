# ADR-077: Deep Codebase Hygiene, Single Error Channel, Strict Contracts & Operational Telemetry Parity

| Field          | Value                                                                                      |
|----------------|--------------------------------------------------------------------------------------------|
| **Status**     | ACCEPTED                                                                                   |
| **Date**       | 2026-11-24                                                                                 |
| **Authors**    | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)            |
| **Scope**      | Cresmo Bounded Context — Domain, Application, Infrastructure, Bootstrap, Presentation, Packaging |
| **Refines**    | ADR-010, ADR-019, ADR-023, ADR-029, ADR-031, ADR-058, ADR-064, ADR-066, ADR-067, ADR-068, ADR-071, ADR-073, ADR-074, ADR-075, ADR-076 |

---

## 1. Context & Architectural Motivation

Following ADR-076, a full 225-file audit of `src/cresmo/` (182 Python modules + 43 resources), `docker/monitoring/`, and `pyproject.toml` uncovered latent bugs, surviving backward-compatibility shims, placebo configuration chains, and boundary leaks:

1. **Dual-Channel Error Handling & Phantom Result Fields (`PipelineResult`):** `PipelineResult` carried `success`, `error_message`, `synthesized_notes`, `reconciled_mocs`, and `duplicates_unified`, even though `CresmoPipeline` always signals failures via typed exceptions and never populates deferred atomic outputs.
2. **Pre-ADR-058 `enriched_dir` & Derived Path Sprawl:** `ObsidianVaultAdapter.__init__` accepted 8 paths (including dead `enriched_dir` and `fluid_dir`), duplicating `data_dir / stage.value` across `StorageSettings`, `environment.py`, and `TranscriptVaultHandler`.
3. **Media Ingestion Leaky Plumbing & Unwired Metrics:** `MediaIngestionPort.ingest_single_video` carried retired `keep_audio`, `output_dir`, and per-call `whisper_model` overrides across 4 layers; `build_media_ingestion_adapter` omitted `metrics_port`, silently dropping `MEDIA_INGESTION_DURATION`, while `NativeMediaIngestionAdapter` emitted high-cardinality `channel_id` labels.
4. **Judge Stage-Name Routing & Template Contract Drift:** `GeminiJudgeAdapter` and `OllamaJudgeAdapter` retained `PromptKey(f"judge_{stage_name}")` fallback routing duplicating ~45 lines of orchestration; `reconcile_mocs/user.md` (`{{existing_mocs}}`) and `raw_index_synthesis/user.md` (`{{channel_name}}`) leaked literal Mustache tags; 4 deferred judge prompts still expected `'true'/'false'` strings instead of JSON criteria.
5. **Sync Ledger Double-Writes & Silent `--force-refresh` Bug:** `SyncChannelUseCase` duplicated 4 `LedgerRepositoryPort` writes per item after ADR-076 moved ledger ownership into `CresmoPipeline.execute()`, and omitted `force_reprocess=force_refresh` on `pipeline.run_for_video()`.
6. **Fragmented Warmup, `stream_queue.full()` Bug, Placebo `synthesis_temperature` & Hexagonal Leaks:** `CresmoPipeline` re-ran `warmup()` on every item; `discover_batch_sources.py` probed `getattr(stream_queue, "full", ...)` breaking `queue.Queue.put(..., timeout=...)`; `OllamaSettings.synthesis_temperature` traversed 6 files to `_ = temperature`; `export_cookies.py` imported `infrastructure.*` directly; `seed_prompts.py` performed eager import-time catalog loading and `subprocess` execution; `application/services/preflight.py` imported `pydantic.SecretStr`.
7. **Unemitted Metrics & Packaging Bloat:** `MetricName` held 3 unimplemented DORA placeholders and 4 unemitted Golden Signals; `pyproject.toml` included `pytest`, `debugpy`, `playground/` ML/plotting packages, and unused libraries in production `[project].dependencies`.

---

## 2. Decision

We execute an 8-wave remediation under strict TDD Green (`pytest`), `mypy --strict`, and `ruff`:

1. **Domain Strict Contracts & Pure Helpers:** Guard `_patch_python313_threading_shutdown()` with `sys.version_info[:2] == (3, 13)`; strip `source_extractor`, `candidate_extractor`, and `max_passes` from `StageDefinition`; move `resolve_max_passes()` onto `StageExecutionPolicy` (dropping `synthesis_temperature`); purge `.strip()` shims, `Channel.url`, `Content.create()`, `Content.__init__` `| Any`/`hasattr`, `RawIndexEntry.{summary,excerpt}`, `CriterionScore.confidence`, `PipelineStatus.FAILED_INGESTION`, `ChatPrompt.get_last_user_content`, `extract_extra_info_section`, and `compute_maxsim_novelty` unused 3rd return element; introduce `normalize_entity_title_for_matching` in `domain/services/entity_matching.py`; consolidate `extract_source_text` as SSOT; trim 12 unused re-exports from `domain/value_objects/__init__.py`.
2. **Ports, Services & Evals Minimalism:** Narrow `MediaIngestionPort.ingest_single_video(video_url)` to 1 argument; narrow `PreflightProbePort` to 3 FS/OS methods and `PreflightHealthChecker` to local blocking checks with pure `str | None` API key (purging `pydantic.SecretStr`); narrow `VaultRepositoryPort` stage methods to `StageName`; drop `extra_metadata`/`pipeline_version`/`git_sha` from `SessionTelemetrySpec` and `add_event`/`record_error` from `TelemetrySpan` protocol; move `ResilientEmbeddingAdapter` active provider onto `provider_name`; add shared `application/services/frontmatter.py` (`parse_frontmatter` + Zero-Read `read_frontmatter_header`); remove `DORA_*` from `MetricName` while retaining/wiring the 4 operational Golden Signals; trim 14 unused re-exports from `application/ports/__init__.py`.
3. **Single Error Channel, Single Ledger Owner & Pipeline Cleanup:**
   - Remove `success`, `error_message`, `synthesized_notes`, `reconciled_mocs`, `duplicates_unified` from `PipelineResult` (`slots=True`), and align `RunSynthesisUseCase`, `SyncChannelUseCase`, and `run.py` linearly around exceptions.
   - Forward `force_reprocess=force_refresh` in `SyncChannelUseCase` and delegate `RUNNING`/`COMPLETED`/`FAILED_TRANSFORMATION` ledger writes solely to `CresmoPipeline.execute()`.
   - Make `CresmoPipeline.warmup()` idempotent (`_warmup_dispatched`), invoked once per run/sync outside per-item loops, warming both synthesis and critique ports via `PipelineStageRunner.warmup()`.
   - Shrink `StageFactory.build_stage(stage_name, *, max_passes=None)` with `dataclasses.replace` cache cloning; remove `getattr`/`hasattr` across `pipeline/`; remove `stream_queue.full()` hack; remove `batch_size` from `sync` CLI/`SyncBatchRequest`/`composition.py` (while **retaining** `PipelineSettings.batch_size` annotated for post-refactor `SynthesizeAtomicBatchUseCase`); fix `# FUTURE / DEFERRED` modules (`discover_atomic_inventory`, `reconcile_mocs`, `indexing/distiller`) by passing explicit `judge_prompt_key` and `channel_name`, retiring ADR-010/029 inline judge fallbacks and `parse_judge_boolean`.
   - Retain operator stdout traces (`[STAGE]` and `[SPAN DEBUG]`) per explicit Lead Architect directive.
4. **SSOT Storage (`vault_dir` + `data_dir` + `StageName`) & Config Hygiene:** Delete `enriched_dir` and `fluid_dir` from `StorageSettings`, `environment.py`, `ObsidianVaultAdapter(vault_dir, data_dir)`, and `TranscriptVaultHandler(data_dir)`; delete `OllamaSettings.synthesis_temperature`, `CresmoSettings.__init__`, `GEMINI_FREE_TIER_MODELS`, `logging_config.get_logger`, `LedgerEntryRow.payload`, and `sqlite://` shim in `PostgresLedgerAdapter`; move `resolve_git_sha` to `infrastructure/system.py`.
5. **Compositional Adapters & Fail-Fast Prompt Contracts:**
   - Extract pure `evaluate_prompt_judge()` in `adapters/judges/prompt_judge_runner.py` with fail-fast `judge_prompt_key` validation (zero stage-name fallback) shared by `GeminiJudgeAdapter` and `OllamaJudgeAdapter`.
   - Extract `resolve_gemini_credential_pool`, `chat_prompt_to_genai_contents`, `post_ollama_json` (`httpx` with `close()`), `MetricsLLMTransformationDecorator`, and `probe_service_health`.
   - Enforce strict Mustache tag resolution (`TemplateRenderer.render(..., strict=True)` and `find_unresolved_tags`) in `JsonPromptProvider` and `LangfusePromptProvider`; consolidate `JsonPromptProvider(language=...)`; inject explicit `catalog` & `default_language` into `LangfusePromptProvider`.
   - Wire `INGESTION_FAILURES`, `MEDIA_INGESTION_DURATION` (low-cardinality, no `channel_id`), `LLM_REQUEST_DURATION`, `BATCH_SOURCES_DISCOVERED`, and `DISCOVERY_QUEUE_SIZE`.
6. **Bootstrap & Humble Presentation:** Delete `settings_factory.py` and `_LazyLangfuse` proxy; route `export_cookies.py` and `seed_prompts.py` through `bootstrap/composition.py` with lazy catalog loading; unify CLI exception handling via `handle_cli_exception()`; remove `_lazy_command_stub` from `cli.py`.
7. **Resources, Grafana, Empty Dirs & `pyproject.toml`:** Remove `{{existing_mocs}}` from `reconcile_mocs/user.md`; translate `gap_filler`/`long_expander`/`wide_expander` `user.md` to English; migrate 4 deferred judge prompts to JSON criterion output; remove `langfuse_slug` override in `prompts.json`; remove DORA panels & `{channel_id}` filters from `cresmo-golden-signals.json`; delete 4 empty residual directories; move `playground/` deps and `asyncpg` out of `[project].dependencies` and prune unused packages (`pytest`, `debugpy`, `watchdog`, `lxml`, `redis`, `arq`, `alembic`).

---

## 3. Bounded Context & Domain Model Impact

- **Cresmo Domain:** `StageExecutionPolicy.resolve_max_passes()` owns pass budgets; `normalize_entity_title_for_matching()` centralizes honorific matching; `PipelineStatus.FAILED_INGESTION` and write-only VO fields retired.
- **Cresmo Application:** `PipelineResult` models success-only states (Single Error Channel); `frontmatter.py` unifies YAML parsing without breaking Zero-Read scanning.
- **Observability:** `MetricName` enforces strict typing (`name: MetricName`) across `MetricsPort`; `"channel_id"` added to `HIGH_CARDINALITY_LABELS`.

---

## 4. Alternatives Considered

1. **Keep `PipelineResult.success` / `error_message` alongside exceptions:** Rejected; creates split-brain error handling and unreachable `else` branches.
2. **Introduce `BasePromptJudgeAdapter` & `BaseGeminiAdapter` inheritance:** Rejected; functional composition (`evaluate_prompt_judge`, `resolve_gemini_credential_pool`) avoids inheritance coupling and keeps `mutmut` surface minimal.
3. **Retain `ObsidianVaultAdapter` 8-path constructor:** Rejected; 6 of 8 paths are deterministic derivatives of `vault_dir` and `data_dir`.

---

## 5. Consequences, Security & Verification

- **Positive:** Resolves silent `--force-refresh`, judge fallback, queue backpressure, and unwired ingestion metrics bugs; shrinks `mutmut` surface; removes heavy ML packages from production container builds.
- **Negative / Trade-offs:** Breaking signature refinements on internal ports (`MediaIngestionPort`, `ObsidianVaultAdapter`, `StageFactory`, `PipelineResult`) requiring lockstep test updates.
- **Verification Gate:** `uv run ruff check src/ tests/ evals/`, `uv run mypy src/cresmo/ src/identity/ src/shared_kernel/`, `uv run pytest tests/ -q`, and `uv lock` must all pass with exit code 0.
