# SPEC-069: Modular Domain Settings Package and Pure Infrastructure Environment Helpers

**Status:** APPROVED  
**Date:** 2026-11-22  
**Governing ADR:** [`ADR-069`](../adr/ADR-069-modular-domain-settings-package-and-infrastructure-environment.md)  
**Relates To:** [`ADR-005`](../adr/ADR-005-multi-role-12factor-container-architecture.md), [`ADR-006`](../adr/ADR-006-resilient-workspace-root-discovery.md), [`ADR-010`](../adr/ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-026`](../adr/ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-048`](../adr/ADR-048-architectural-remediation-and-comprehensive-mutation-blindage.md), [`ADR-066`](../adr/ADR-066-hybrid-semantic-saturation-and-text-embedding-adapters.md), [`SPEC-005`](SPEC-005-operational-staging-validation.md), [`SPEC-062`](SPEC-062-structural-consolidation-and-hygiene.md), [`SPEC-066`](SPEC-066-hybrid-semantic-saturation.md), [`GLOSSARY`](../GLOSSARY.md)

---

## 1. Specification Overview & Architectural Invariants

Defines the exact module boundaries, public symbols, Pydantic Settings V2 field contracts, pure validation invariants, and filesystem environment helper signatures for decomposing `src/cresmo/infrastructure/config.py` into `src/cresmo/infrastructure/config/` and `src/cresmo/infrastructure/environment.py`.

### 1.1 Mandatory Engineering & Hexagonal Invariants
1. **Language & Typing:** All modules, docstrings, comments, and tests MUST be strictly in English, start with `from __future__ import annotations`, and pass `mypy --strict`.
2. **Import Hygiene:** NEVER use `src.` prefixes inside `src/`. Import exclusively via `cresmo.*`.
3. **Strict Hexagonal Dependency Direction (`Domain -> Application -> Infrastructure -> Bootstrap -> Presentation`):**
   - `src/cresmo/infrastructure/environment.py` and `src/cresmo/infrastructure/config/*` MUST reside strictly in `infrastructure/` and MUST contain **zero** imports from `cresmo.bootstrap` or `cresmo.presentation`.
   - `src/cresmo/application/ports/settings.py` (`PipelineSettingsProtocol`, `DefaultPipelineSettings`) remains pure Application code with zero `pydantic` or `infrastructure` imports.
4. **Pure Validation (`*Impure Validation Side-Effect*` Ban):**
   - Neither `CresmoSettings` nor any domain sub-settings class (`LlmSettings`, `TelemetrySettings`, `StorageSettings`, `IngestionSettings`, `SaturationSettings`, `JudgeSettings`) may perform filesystem `.exists()`, `.stat()`, or `mkdir()` I/O inside `@model_validator` or `@field_validator` hooks.
5. **Hard Deletion (`ADR-010`):**
   - Monolithic `src/cresmo/infrastructure/config.py` MUST be deleted once `src/cresmo/infrastructure/config/` is in place.

---

## 2. Infrastructure Environment Helpers (`src/cresmo/infrastructure/environment.py`)

Pure Infrastructure helper module isolating filesystem side-effects (directory creation and cookie file probing) from Pydantic configuration validation.

### 2.1 `StorageSettingsProtocol`
```python
@runtime_checkable
class StorageSettingsProtocol(Protocol):
    """Structural contract for runtime directory initialization."""

    @property
    def data_dir(self) -> Path: ...
    @property
    def vault_dir(self) -> Path: ...
    @property
    def mocs_dir(self) -> Path: ...
    @property
    def raw_dir(self) -> Path: ...
    @property
    def fluid_dir(self) -> Path: ...
    @property
    def gap_filler_dir(self) -> Path: ...
    @property
    def enriched_dir(self) -> Path: ...
    @property
    def master_dir(self) -> Path: ...
    @property
    def priority_texts_dir(self) -> Path: ...
```

### 2.2 `ensure_runtime_directories`
```python
def ensure_runtime_directories(storage: StorageSettingsProtocol | Any) -> None:
    """Idempotently create all 9 canonical Cresmo runtime directories."""
```
- **Behavioral Contract:**
  - Invokes `Path.mkdir(parents=True, exist_ok=True)` across all 9 canonical directories in deterministic order:
    1. `storage.data_dir`
    2. `storage.vault_dir`
    3. `storage.mocs_dir`
    4. `storage.raw_dir`
    5. `storage.fluid_dir`
    6. `storage.gap_filler_dir`
    7. `storage.enriched_dir`
    8. `storage.master_dir`
    9. `storage.priority_texts_dir`

### 2.3 `discover_cookies_file`
```python
def discover_cookies_file(
    data_dir: Path,
    workspace_dir: Path,
    configured: Path | None = None,
) -> Path | None:
    """Probe candidate cookie file locations and return the first existing non-empty path."""
```
- **Behavioral Contract:**
  - Evaluates candidates in strict precedence order:
    1. `configured` (when not `None`)
    2. `data_dir / "cookies.txt"`
    3. `workspace_dir / "data" / "cookies.txt"`
    4. `workspace_dir / ".yt_dlp_cookies.txt"`
  - Returns the first candidate path that exists as a non-empty file (`candidate.exists() and candidate.stat().st_size > 0`), or `None` if no candidate satisfies the check.
  - Executes only when explicitly invoked by runtime environment callers (such as bootstrap adapter factories or CLI commands), never during `BaseSettings` validation.

---

## 3. Modular Domain Settings Package (`src/cresmo/infrastructure/config/`)

Delete `src/cresmo/infrastructure/config.py` and replace it with the following 9 modules:

### 3.1 `catalog.py`
Houses shared domain/provider catalog types, default constants, and version resolution:
- **Resource & Threshold Constants:** `DEFAULT_LANGFUSE_PROMPT_LABEL = "production"`, `DEFAULT_PROMPTS_RESOURCE_PACKAGE = "cresmo.infrastructure.resources"`, `DEFAULT_PROMPTS_RESOURCE_NAME = "prompts.json"`, `DEFAULT_TAXONOMY_RESOURCE_PACKAGE = "cresmo.infrastructure.resources"`, `DEFAULT_TAXONOMY_RESOURCE_NAME = "taxonomy.json"`, `DEFAULT_JUDGE_PASS_THRESHOLD = 0.9`.
- **Gemini Catalog (`ADR-064`):** `GeminiFreeTierModel` (`Literal[...]`), `GEMINI_FREE_TIER_MODELS` (`tuple[str, ...]`), `GeminiThinkingLevel` (`Literal["minimal", "low", "medium", "high", "xhigh"]`), `GEMINI_THINKING_LEVELS` (`tuple[str, ...]`), `DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"`, `DEFAULT_GEMINI_FALLBACK_MODEL = "gemini-3.6-flash"`, `DEFAULT_JUDGE_GEMINI_MODEL = DEFAULT_GEMINI_MODEL`, `DEFAULT_GEMINI_THINKING_LEVEL: GeminiThinkingLevel = "low"`, `DEFAULT_GEMINI_MAX_OUTPUT_TOKENS = 32_768`, `DEFAULT_GEMINI_TIMEOUT_SECONDS = 300.0`.
- **Benchmark Catalogs:** `DEFAULT_BENCHMARK_MODELS`, `DEFAULT_JUDGE_CALIBRATION_MODELS`, `DEFAULT_GENERATOR_BENCHMARK_MODELS`.
- **Dynamic Version Helper (`ADR-063`):** `resolve_default_pipeline_version() -> str` reading `importlib.metadata.version("pes")` (falling back to `"0.0.0-dev"`) and returning `f"cresmo:v{pkg_version}"`.

### 3.2 `llm.py` — `LlmSettings(BaseSettings)`
| Symbol | Kind | Default / Contract |
| :--- | :--- | :--- |
| `gemini_api_keys` | `list[SecretStr]` | `default_factory=list` |
| `gemini_api_key` | `@property -> SecretStr` | Returns `gemini_api_keys[0]` or `SecretStr("")` |
| `_normalize_gemini_credentials` | `@model_validator(mode="before")` | Parses `gemini_api_keys` / `GEMINI_API_KEYS` / `gemini_api_key` / `GEMINI_API_KEY` from comma-separated `str`, `SecretStr`, or `list` |
| `gemini_model` | `str` | `DEFAULT_GEMINI_MODEL` |
| `gemini_fallback_model` | `str` | `DEFAULT_GEMINI_FALLBACK_MODEL` |
| `gemini_thinking_level` | `GeminiThinkingLevel` | `DEFAULT_GEMINI_THINKING_LEVEL`, aliases `CRESMO_GEMINI_THINKING_LEVEL`, `GEMINI_THINKING_LEVEL`, `gemini_thinking_level` |
| `_normalize_gemini_thinking_level` | `@field_validator("gemini_thinking_level", mode="before")` | Strips whitespace and lowercases `str` values |
| `gemini_max_output_tokens` | `int` | `DEFAULT_GEMINI_MAX_OUTPUT_TOKENS`, `ge=256, le=1_048_576` |
| `gemini_timeout_seconds` | `float` | `DEFAULT_GEMINI_TIMEOUT_SECONDS`, `ge=1.0` |
| `ollama_base_url` | `str` | `"http://localhost:11434"`, aliases `ollama_base_url`, `CRESMO_OLLAMA_URL`, `OLLAMA_URL` |
| `ollama_model` | `str` | `"qwen2.5:7b"`, aliases `ollama_model`, `CRESMO_OLLAMA_MODEL`, `OLLAMA_MODEL` |
| `ollama_timeout_seconds` | `float` | `300.0`, `ge=1.0` |
| `ollama_warmup_timeout_seconds` | `float` | `300.0`, `ge=1.0` |
| `ollama_keep_alive` | `str` | `"1h"` |
| `ollama_num_predict` | `int` | `0`, `ge=0` |
| `indexing_provider` | `str` | `"ollama"`, aliases `indexing_provider`, `CRESMO_INDEXING_PROVIDER` |
| `language` | `str` | `DEFAULT_LANGUAGE`, aliases `language`, `CRESMO_LANGUAGE` |
| `llm_synthesis_temperature` | `float` | `0.2`, `ge=0.0, le=2.0` |
| `llm_indexing_temperature` | `float` | `0.2`, `ge=0.0, le=2.0` |

### 3.3 `telemetry.py` — `TelemetrySettings(BaseSettings)`
| Symbol | Kind | Default / Contract |
| :--- | :--- | :--- |
| `langfuse_secret_key` | `SecretStr` | `SecretStr("")`, aliases `langfuse_secret_key`, `LANGFUSE_SECRET_KEY` |
| `langfuse_public_key` | `str` | `""`, aliases `langfuse_public_key`, `LANGFUSE_PUBLIC_KEY` |
| `langfuse_host` | `str` | `"https://cloud.langfuse.com"`, aliases `langfuse_host`, `LANGFUSE_HOST`, `LANGFUSE_BASE_URL` |
| `langfuse_environment` | `str` | `DEFAULT_LANGFUSE_ENVIRONMENT` (`"staging"`), aliases `langfuse_environment`, `LANGFUSE_TRACING_ENVIRONMENT`, `LANGFUSE_ENVIRONMENT`, validated against `^(?!langfuse)[a-z0-9-_]{1,40}$` (`ADR-072`) |
| `langfuse_prompt_label` | `str` | `DEFAULT_LANGFUSE_PROMPT_LABEL` |
| `langfuse_timeout_seconds` | `int` | `30` |
| `prometheus_enabled` | `bool` | `True` |
| `prometheus_port` | `int` | `9090` |
| `log_level` | `str` | `"WARNING"`, aliases `log_level`, `LOG_LEVEL`, `CRESMO_LOG_LEVEL` |
| `log_format` | `str` | `"json"`, aliases `log_format`, `LOG_FORMAT`, `CRESMO_LOG_FORMAT` |
| `pipeline_version` | `str` | `default_factory=resolve_default_pipeline_version`, `validation_alias="CRESMO_PIPELINE_VERSION"` |
| `git_sha` | `str \| None` | `None`, aliases `git_sha`, `GIT_SHA`, `CRESMO_GIT_SHA` |
| `anonymization_enabled` | `bool` | `True` |
| `preflight_probe_timeout_seconds` | `float` | `2.0` |
| `enable_preflight_probes` | `bool` | `True` |

### 3.4 `storage.py` — `StorageSettings(BaseSettings)`
- **Root Directories:** `data_dir: Path` (`default_factory=lambda: _WORKSPACE_DIR / "data"`), `vault_dir: Path` (`default_factory=lambda: _WORKSPACE_DIR / "vault"`), where `_WORKSPACE_DIR = find_workspace_root()`.
- **Configurable Filenames & Optional Custom Paths:** `sqlite_ledger_filename` (`"cresmo_ledger.db"`), `playlist_filename` (`"playlist.txt"`), `playlist_priority_filename` (`"playlist-priority.txt"`), `brain_csv_filename` (`"brain.csv"`), `priority_texts_dirname` (`"priority"`), `browser_headers_path` (`None`), `cookies_file` (`None`, aliases `cookies_file`, `DEFAULT_COOKIES_FILE`, `CRESMO_COOKIES_FILE`), `prompts_path` (`None`), `taxonomy_path` (`None`), `skills_dir` (`None`).
- **Derived `@property -> Path` Accessors:**
  - `raw_dir` (`data_dir / "raw"`)
  - `fluid_dir` (`data_dir / "fluid_prose"`)
  - `gap_filler_dir` (`data_dir / "gap_filler"`)
  - `enriched_dir` (`data_dir / "enriched"`)
  - `master_dir` (`data_dir / "master"`)
  - `index_path` (`vault_dir / "_index.json"`)
  - `mocs_dir` (`vault_dir / "MOCs"`)
  - `sqlite_ledger_path` (`data_dir / sqlite_ledger_filename`)
  - `brain_csv_path` (`data_dir / brain_csv_filename`)
  - `playlist_path` (`data_dir / playlist_filename`)
  - `playlist_priority_path` (`data_dir / playlist_priority_filename`)
  - `priority_texts_dir` (`data_dir / priority_texts_dirname`)
- `StorageSettings` structurally satisfies `StorageSettingsProtocol`.

### 3.5 `ingestion.py` — `IngestionSettings(BaseSettings)`
- **Browser & Discovery Flags:** `browser_cookies` (`"firefox"`), `auto_extract_cookies` (`True`), `enable_channel_crawler` (`False`), `require_auth_cookies` (`False`).
- **Media & Worker Pools:** `whisper_model` (`"base"`), `days_lookback` (`365`), `whisper_workers` (`1`), `subtitle_workers` (`0`), `channel_discovery_workers` (`0`), `discovery_queue_maxsize` (`50`, `ge=1`).
- **Stage & Indexing Controls:** `batch_size` (`5`), `keep_audio` (`False`), `expansion_max_passes` (`5`, `ge=1, le=10`), `gap_filler_passes` (`@property -> int` returning `self.expansion_max_passes`), `concat_max_words` (`500_000`), `raw_index_max_chars` (`0`), `raw_index_max_attempts` (`2`, `ge=0`), `inventory_max_attempts` (`2`, `ge=0`).
- **Pure `@model_validator(mode="after")` `_compute_worker_multiples(self) -> Self`:**
  - When `self.subtitle_workers <= 0`: sets `self.subtitle_workers = max(1, self.whisper_workers * 5)`.
  - When `self.channel_discovery_workers <= 0`: sets `self.channel_discovery_workers = max(1, self.whisper_workers * 10)`.
  - Performs **zero** filesystem I/O (zero `.exists()` or `.stat()` calls).

### 3.6 `saturation.py` — `SaturationSettings(BaseSettings)`
- **Embedding Backend (`ADR-066`):** `embedding_provider: Literal["gemini", "ollama", "tfidf"] = "gemini"`, `gemini_embedding_model: str = "gemini-embedding-001"`, `gemini_embedding_dimensions: int = 768` (`ge=1`), `ollama_embedding_model: str = "nomic-embed-text"`.
- **Saturation Thresholds & Sliding Window:**
  - `saturation_lexical_threshold: float = 0.95` (`gt=0.0, le=1.0`)
  - `saturation_max_word_delta: float = 0.03` (`ge=0.0, le=1.0`)
  - `saturation_semantic_threshold: float = 0.88` (`gt=0.0, le=1.0`)
  - `saturation_max_novel_paragraphs: int = 0` (`ge=0`)
  - `saturation_long_unit_word_cutoff: int = 120` (`ge=1`)
  - `saturation_sliding_window_sentences: int = 3` (`ge=1`)
  - `saturation_sliding_window_overlap: int = 1` (`ge=0`)
- **Validators:**
  - `_normalize_embedding_provider` (`@field_validator("embedding_provider", mode="before")`): strips and lowercases `str` inputs.
  - `_validate_saturation_sliding_window` (`@model_validator(mode="after")`): raises `ValueError` if `self.saturation_sliding_window_overlap >= self.saturation_sliding_window_sentences`.

### 3.7 `judge.py` — `JudgeSettings(BaseSettings)`
- **TypeSafe AI:** `typesafe_api_key` (`SecretStr("")`), `typesafe_model` (`"jev-latest"`), `typesafe_base_url` (`"https://api.typesafe.ai/v1"`).
- **Judge Routing & Thresholds:** `judge_provider` (`"gemini"`), `judge_fallback_provider` (`"ollama"`), `judge_blocking` (`False`), `judge_max_attempts` (`2`, `ge=1`), `max_retries` (`@property -> int` returning `self.judge_max_attempts`), `judge_pass_threshold` (`DEFAULT_JUDGE_PASS_THRESHOLD`, `ge=0.0, le=1.0`).
- **Gap-Filler Judge:** `gap_filler_judge_threshold` (`DEFAULT_JUDGE_PASS_THRESHOLD`, `ge=0.0, le=1.0`), `gap_filler_judge_weights` (`dict[str, float]` with the 7 `ADR-060` criterion weights).
- **Judge Gemini & Benchmarks:** `judge_gemini_model` (`DEFAULT_GEMINI_MODEL`), `judge_gemini_thinking_level` (`DEFAULT_GEMINI_THINKING_LEVEL`), `_normalize_judge_thinking_level` (`@field_validator("judge_gemini_thinking_level", mode="before")`), `benchmark_models` (`default_factory=lambda: list(DEFAULT_BENCHMARK_MODELS)`), `judge_calibration_models` (`@property` alias), `generator_benchmark_models` (`@property` alias).

### 3.8 `settings.py` — `CresmoSettings` & Singleton Lifecycle
```python
class CresmoSettings(
    LlmSettings,
    TelemetrySettings,
    StorageSettings,
    IngestionSettings,
    SaturationSettings,
    JudgeSettings,
):
    ...
```
- **ClassVars:** Preserves all 17 `ClassVar` attributes (`DEFAULT_LANGUAGE` through `DEFAULT_GENERATOR_BENCHMARK_MODELS`).
- **`model_config`:** `SettingsConfigDict` with the 4-tier `env_file` tuple (`".env"`, `str(_WORKSPACE_DIR / ".env")`, `str(_WORKSPACE_DIR / "vault" / ".env")`, `str(_WORKSPACE_DIR / "data" / ".env")`), `env_file_encoding="utf-8"`, `extra="ignore"`.
- **`settings_customise_sources`:** Preserves `_safe_decode` fallback splitting comma-separated `str` values for `gemini_api_keys`, `benchmark_models`, `judge_calibration_models`, and `generator_benchmark_models` across both `dotenv_settings` and `env_settings`.
- **`__init__`:** Preserves `_env_file` override injection, `gemini_api_key -> gemini_api_keys` keyword mapping, and `pipeline_version -> CRESMO_PIPELINE_VERSION` keyword normalization.
- **`ensure_directories(self) -> None`:** Delegates directly to `ensure_runtime_directories(self)` from `cresmo.infrastructure.environment`.
- **Singleton Helpers:**
  - `@functools.lru_cache(maxsize=1) def get_shared_settings() -> CresmoSettings`
  - `def reset_shared_settings() -> None`
  - `def resolve_shared_settings(settings: CresmoSettings | None = None) -> CresmoSettings`

### 3.9 `__init__.py` — Package Public Surface
Re-exports in `__all__`:
- All 20 original `src/cresmo/infrastructure/config.py` exports (`DEFAULT_BENCHMARK_MODELS`, `DEFAULT_GEMINI_FALLBACK_MODEL`, `DEFAULT_GEMINI_MAX_OUTPUT_TOKENS`, `DEFAULT_GEMINI_MODEL`, `DEFAULT_GEMINI_THINKING_LEVEL`, `DEFAULT_GEMINI_TIMEOUT_SECONDS`, `DEFAULT_GENERATOR_BENCHMARK_MODELS`, `DEFAULT_JUDGE_CALIBRATION_MODELS`, `DEFAULT_JUDGE_GEMINI_MODEL`, `DEFAULT_JUDGE_PASS_THRESHOLD`, `DEFAULT_LANGFUSE_PROMPT_LABEL`, `GEMINI_FREE_TIER_MODELS`, `GEMINI_THINKING_LEVELS`, `CresmoSettings`, `GeminiFreeTierModel`, `GeminiThinkingLevel`, `get_shared_settings`, `reset_shared_settings`, `resolve_default_pipeline_version`, `resolve_shared_settings`).
- All 6 domain sub-settings classes (`IngestionSettings`, `JudgeSettings`, `LlmSettings`, `SaturationSettings`, `StorageSettings`, `TelemetrySettings`).

---

## 4. Compatibility Contracts (`.env`, `src/config.py`, `PipelineSettingsProtocol`)

1. **Flat `.env` & Environment Variable Parity:**
   - Every field name and `AliasChoices` / `validation_alias` on `LlmSettings`, `TelemetrySettings`, `StorageSettings`, `IngestionSettings`, `SaturationSettings`, and `JudgeSettings` remains flat at the top level of `CresmoSettings`. Existing `.env` files require zero key renames or nested delimiters.
2. **`src/config.py` Parity:**
   - `AppConfig` (`src/config.py`) imports `CresmoSettings` and catalog constants from `cresmo.infrastructure.config` seamlessly without edits to `src/config.py`.
3. **`PipelineSettingsProtocol` Parity:**
   - `isinstance(CresmoSettings(_env_file=None), PipelineSettingsProtocol)` MUST evaluate to `True`, satisfying all 24 protocol properties required by Application Use Cases and `CresmoPipeline`.
4. **Pure Instantiation Guarantee:**
   - Instantiating `CresmoSettings(_env_file=None)` or any sub-settings class performs zero `mkdir`, `.exists()`, or `.stat()` calls for cookies or runtime directories; directory creation occurs exclusively via `ensure_runtime_directories` / `settings.ensure_directories()`, and cookie candidate probing occurs exclusively via `discover_cookies_file`.

---

## 5. Verification Acceptance Criteria

- `uv run ruff check .` exits `0`
- `uv run ruff format --check .` exits `0`
- `uv run mypy --strict src/` exits `0`
- `uv run pytest tests/ -v` passes with `0` errors across all unit and integration suites
- `src/cresmo/infrastructure/config.py` does not exist; `src/cresmo/infrastructure/config/` and `src/cresmo/infrastructure/environment.py` exist with zero `cresmo.bootstrap` or `cresmo.presentation` imports
- `isinstance(CresmoSettings(_env_file=None), PipelineSettingsProtocol)` is `True` and instantiating `CresmoSettings(_env_file=None)` performs zero cookie probing or directory creation side-effects
