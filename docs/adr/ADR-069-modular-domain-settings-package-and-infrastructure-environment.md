# ADR-069: Modular Domain Settings Package and Pure Infrastructure Environment Helpers

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-11-22                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cresmo Knowledge Synthesis Bounded Context — Infrastructure, Bootstrap, Root Configuration |
| **Relates** | ADR-000, ADR-005, ADR-006, ADR-010, ADR-026, ADR-048, ADR-058, ADR-062, ADR-063, ADR-064, ADR-066 |

---

## 1. Context & Architectural Motivation

Centralized runtime configuration for the Cresmo engine accumulated inside a single 1,023-line module (`src/cresmo/infrastructure/config.py`). While `CresmoSettings` enforced 12-Factor validation via Pydantic Settings V2, auditing Wave 3 modularity and testability exposed three structural violations:

1. **`ADR-026` Bounded Modularity Violation (`*God Settings Monolith*`):**
   - `src/cresmo/infrastructure/config.py` conflated eight distinct configuration concerns inside one monolithic file: Free-Tier model catalogs and resource constants, LLM provider credentials and inference tunables, Langfuse/Prometheus/structlog telemetry settings, filesystem storage paths and filenames, media ingestion and worker pool ratios, `ADR-066` hybrid semantic saturation thresholds, quality judge and benchmark configurations, and `lru_cache` singleton lifecycle helpers.
   - Any modification to a single domain concern (such as adding `ADR-066` sliding-window saturation tunables or updating `ADR-064` Gemini Free-Tier models) required editing a thousand-line file shared by every subsystem.
2. **Filesystem I/O Coupled into Pydantic Validation (`*Impure Validation Side-Effect*`):**
   - `CresmoSettings._compute_worker_multiples` (`@model_validator(mode="after")`) performed live filesystem `.exists()` and `.stat()` probing across `self.cookies_file`, `self.data_dir / "cookies.txt"`, `_WORKSPACE_DIR / "data" / "cookies.txt"`, and `_WORKSPACE_DIR / ".yt_dlp_cookies.txt"` during `CresmoSettings()` instantiation.
   - `CresmoSettings.ensure_directories()` embedded `Path.mkdir(parents=True, exist_ok=True)` creation logic directly inside the settings class rather than delegating to an isolated infrastructure environment module.
   - Executing disk probing inside `@model_validator` turns pure configuration parsing into an impure, host-state-dependent operation, coupling hermetic unit tests to developer or container filesystems.
3. **Hexagonal Layering Risk for Environment Helpers (`*Infrastructure-to-Bootstrap Back-Reference*`):**
   - Extracting directory initialization and cookie file probing into standalone helpers must preserve strict Hexagonal dependency direction (`Domain -> Application -> Infrastructure -> Bootstrap -> Presentation`). Placing runtime environment helpers in `bootstrap/` or importing `cresmo.bootstrap` from `cresmo.infrastructure` would introduce an illegal upward dependency back-reference.

---

## 2. Banished Anti-Patterns

In strict compliance with `ADR-000`, `ADR-010` (**Zero Backward Compatibility / Zero Legacy Shims**), and `ADR-026`, this ADR formally bans:

* **`*God Settings Monolith*`**: Housing catalog constants, six unrelated operational sub-domains, and singleton lifecycle management inside a single monolithic `src/cresmo/infrastructure/config.py` file.
* **`*Impure Validation Side-Effect*`**: Performing filesystem `.exists()`, `.stat()`, or `mkdir()` I/O inside Pydantic `BaseSettings` validators (`@model_validator` / `@field_validator`) during configuration instantiation.
* **`*Infrastructure-to-Bootstrap Back-Reference*`**: Importing any `cresmo.bootstrap.*` or `cresmo.presentation.*` module from `src/cresmo/infrastructure/environment.py` or `src/cresmo/infrastructure/config/`.

---

## 3. Decision

### Pillar 1: Pure Infrastructure Environment Helpers (`src/cresmo/infrastructure/environment.py`)
Isolate filesystem environment side-effects into a dedicated Infrastructure module with **zero `cresmo.bootstrap` imports**:
- **`StorageSettingsProtocol` (`@runtime_checkable` `Protocol`):** Defines structural read access to all 9 canonical runtime directories (`data_dir`, `vault_dir`, `mocs_dir`, `raw_dir`, `fluid_dir`, `gap_filler_dir`, `enriched_dir`, `master_dir`, `priority_texts_dir`).
- **`ensure_runtime_directories(storage: StorageSettingsProtocol | Any) -> None`:** Idempotently creates (`mkdir(parents=True, exist_ok=True)`) all 9 runtime directories (`data_dir`, `vault_dir`, `mocs_dir`, `raw_dir`, `fluid_dir`, `gap_filler_dir`, `enriched_dir`, `master_dir`, `priority_texts_dir`).
- **`discover_cookies_file(data_dir: Path, workspace_dir: Path, configured: Path | None = None) -> Path | None`:** Performs deterministic candidate probing across `configured`, `data_dir / "cookies.txt"`, `workspace_dir / "data" / "cookies.txt"`, and `workspace_dir / ".yt_dlp_cookies.txt"`, returning the first valid non-empty cookies file or `None`.
- **Pure Validation Restoration:** Remove all filesystem `.exists()` / `.stat()` probing from `CresmoSettings._compute_worker_multiples` (relocated to `IngestionSettings._compute_worker_multiples`), keeping `BaseSettings` instantiation 100% pure.
- **Delegated Facade:** Preserve `CresmoSettings.ensure_directories()` as a thin delegating method invoking `ensure_runtime_directories(self)` so existing composition and CLI callers remain compatible.

### Pillar 2: Modular Domain Settings Package (`src/cresmo/infrastructure/config/`)
Per `ADR-010`, delete monolithic `src/cresmo/infrastructure/config.py` completely and decompose it into a cohesive nine-module package under `src/cresmo/infrastructure/config/`:

1. **`catalog.py`:** Canonical `DEFAULT_*` constants (`DEFAULT_LANGFUSE_PROMPT_LABEL`, `DEFAULT_PROMPTS_RESOURCE_PACKAGE`, `DEFAULT_PROMPTS_RESOURCE_NAME`, `DEFAULT_TAXONOMY_RESOURCE_PACKAGE`, `DEFAULT_TAXONOMY_RESOURCE_NAME`, `DEFAULT_JUDGE_PASS_THRESHOLD`, `DEFAULT_GEMINI_MODEL`, `DEFAULT_GEMINI_FALLBACK_MODEL`, `DEFAULT_JUDGE_GEMINI_MODEL`, `DEFAULT_GEMINI_THINKING_LEVEL`, `DEFAULT_GEMINI_MAX_OUTPUT_TOKENS`, `DEFAULT_GEMINI_TIMEOUT_SECONDS`, `DEFAULT_BENCHMARK_MODELS`, `DEFAULT_JUDGE_CALIBRATION_MODELS`, `DEFAULT_GENERATOR_BENCHMARK_MODELS`), `GeminiFreeTierModel`, `GEMINI_FREE_TIER_MODELS`, `GeminiThinkingLevel`, `GEMINI_THINKING_LEVELS`, and `resolve_default_pipeline_version()`.
2. **`llm.py`:** `LlmSettings(BaseSettings)` encapsulating Gemini (`gemini_api_keys`, `gemini_api_key` property, `_normalize_gemini_credentials`, `gemini_model`, `gemini_fallback_model`, `gemini_thinking_level`, `gemini_max_output_tokens`, `gemini_timeout_seconds`, `_normalize_gemini_thinking_level`), Ollama (`ollama_base_url`, `ollama_model`, `ollama_timeout_seconds`, `ollama_warmup_timeout_seconds`, `ollama_keep_alive`, `ollama_num_predict`), `indexing_provider`, `language`, `llm_synthesis_temperature`, and `llm_indexing_temperature`.
3. **`telemetry.py`:** `TelemetrySettings(BaseSettings)` encapsulating Langfuse (`langfuse_secret_key`, `langfuse_public_key`, `langfuse_host`, `langfuse_environment`, `langfuse_prompt_label`, `langfuse_timeout_seconds`), Prometheus (`prometheus_enabled`, `prometheus_port`), structlog (`log_level`, `log_format`), release identity (`pipeline_version`, `git_sha`), `anonymization_enabled`, and preflight probe flags (`preflight_probe_timeout_seconds`, `enable_preflight_probes`).
4. **`storage.py`:** `StorageSettings(BaseSettings)` encapsulating `data_dir`, `vault_dir`, configurable filenames/dirnames (`sqlite_ledger_filename`, `playlist_filename`, `playlist_priority_filename`, `brain_csv_filename`, `priority_texts_dirname`), custom resource/cookie paths (`browser_headers_path`, `cookies_file`, `prompts_path`, `taxonomy_path`, `skills_dir`), and all derived `@property` paths (`raw_dir`, `fluid_dir`, `gap_filler_dir`, `enriched_dir`, `master_dir`, `index_path`, `mocs_dir`, `sqlite_ledger_path`, `brain_csv_path`, `playlist_path`, `playlist_priority_path`, `priority_texts_dir`).
5. **`ingestion.py`:** `IngestionSettings(BaseSettings)` encapsulating browser/cookie flags (`browser_cookies`, `auto_extract_cookies`, `enable_channel_crawler`, `require_auth_cookies`), `whisper_model`, `days_lookback`, worker pools (`whisper_workers`, `subtitle_workers`, `channel_discovery_workers`), `discovery_queue_maxsize`, `batch_size`, `keep_audio`, `expansion_max_passes` + `gap_filler_passes` property alias, `concat_max_words`, `raw_index_max_chars`, `raw_index_max_attempts`, `inventory_max_attempts`, and the pure `_compute_worker_multiples` model validator.
6. **`saturation.py`:** `SaturationSettings(BaseSettings)` encapsulating `ADR-066` `embedding_provider`, Gemini/Ollama embedding configuration (`gemini_embedding_model`, `gemini_embedding_dimensions`, `ollama_embedding_model`), all `saturation_*` thresholds including sliding-window parameters (`saturation_long_unit_word_cutoff`, `saturation_sliding_window_sentences`, `saturation_sliding_window_overlap`), `_normalize_embedding_provider`, and `_validate_saturation_sliding_window`.
7. **`judge.py`:** `JudgeSettings(BaseSettings)` encapsulating TypeSafe AI settings (`typesafe_api_key`, `typesafe_model`, `typesafe_base_url`), judge routing and thresholds (`judge_provider`, `judge_fallback_provider`, `judge_blocking`, `judge_max_attempts`, `max_retries` property alias, `judge_pass_threshold`), gap-filler judge configuration (`gap_filler_judge_threshold`, `gap_filler_judge_weights`), judge Gemini configuration (`judge_gemini_model`, `judge_gemini_thinking_level`, `_normalize_judge_thinking_level`), and `benchmark_models` with `judge_calibration_models` / `generator_benchmark_models` property aliases.
8. **`settings.py`:** `CresmoSettings(LlmSettings, TelemetrySettings, StorageSettings, IngestionSettings, SaturationSettings, JudgeSettings)` combining all six domain sub-settings bases via multiple inheritance while retaining all `ClassVar` constants, `model_config` `env_file` tuple, `settings_customise_sources`, `__init__` alias handling, `ensure_directories()`, and singleton helpers (`get_shared_settings()`, `reset_shared_settings()`, `resolve_shared_settings()`).
9. **`__init__.py`:** Re-exports all 20 original `config.py` `__all__` symbols plus all 6 domain sub-settings classes (`LlmSettings`, `TelemetrySettings`, `StorageSettings`, `IngestionSettings`, `SaturationSettings`, `JudgeSettings`).

### Pillar 3: Flat `.env`, `src/config.py`, and `PipelineSettingsProtocol` Compatibility
- **Flat `.env` Preservation:** Composing `CresmoSettings` via flat inheritance of `BaseSettings` domain bases (rather than nested sub-model attributes requiring `env_nested_delimiter`) preserves 100% compatibility with every existing `.env` key, `AliasChoices`, and `CRESMO_*` environment variable.
- **Root `src/config.py` Preservation:** `AppConfig` (`src/config.py`) continues importing `CresmoSettings` and catalog constants from `cresmo.infrastructure.config` with zero changes to root configuration wiring.
- **Application Protocol Parity:** `CresmoSettings` preserves every property and type signature mandated by `PipelineSettingsProtocol` (`src/cresmo/application/ports/settings.py`).

---

## 4. Alternatives Considered

1. **Nested Sub-Model Composition (`settings.llm.gemini_model`, `settings.saturation.embedding_provider`):**
   - Rejected because switching from flat attributes (`settings.gemini_model`, `settings.embedding_provider`) to nested attributes would break `PipelineSettingsProtocol` conformance, require `env_nested_delimiter` migration across `.env` deployments, and trigger invasive caller rewrites across Bootstrap and Adapters without architectural gain.
2. **Keeping `ensure_runtime_directories` and `discover_cookies_file` in `src/cresmo/bootstrap/`:**
   - Rejected because `CresmoSettings.ensure_directories()` lives in `infrastructure/config/settings.py`; placing `ensure_runtime_directories` in `bootstrap/` would create an illegal `*Infrastructure-to-Bootstrap Back-Reference*`.
3. **Retaining `src/cresmo/infrastructure/config.py` as a Compatibility Shim Re-Exporting `config/`:**
   - Rejected per `ADR-010`: Python packages resolve `cresmo.infrastructure.config` directly via `src/cresmo/infrastructure/config/__init__.py`, making a sibling `config.py` redundant and ambiguous.

---

## 5. Consequences, Security & LGPD

- **Positive:**
  - Replaces a 1,023-line God module with focused, single-concern settings modules (`catalog`, `llm`, `telemetry`, `storage`, `ingestion`, `saturation`, `judge`, `settings`) while exposing independent sub-settings classes (`LlmSettings`, `TelemetrySettings`, etc.) for targeted adapter tests.
  - Eliminates filesystem I/O from Pydantic validation, making `CresmoSettings()` instantiation deterministic and fast.
  - Enforces strict Hexagonal boundaries (`environment.py` and `config/` contain zero `bootstrap` or `presentation` imports).
  - Preserves 100% backward compatibility for flat `.env` files, `src/config.py`, `bootstrap/factories/settings_factory.py`, and `PipelineSettingsProtocol`.
- **Breaking / Migration (`ADR-010`):**
  - `src/cresmo/infrastructure/config.py` is deleted and replaced by package `src/cresmo/infrastructure/config/`.
  - `CresmoSettings` no longer auto-mutates `cookies_file` via disk probing during `BaseSettings` validation; runtime callers needing fallback candidate discovery call `discover_cookies_file(...)` from `cresmo.infrastructure.environment`.
- **Security & LGPD:**
  - Secret fields (`gemini_api_keys`, `typesafe_api_key`, `langfuse_secret_key`) remain wrapped in Pydantic `SecretStr` inside their respective domain settings modules (`LlmSettings`, `JudgeSettings`, `TelemetrySettings`), preventing accidental secret serialization in logs or trace metadata.
