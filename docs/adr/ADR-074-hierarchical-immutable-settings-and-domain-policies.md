# ADR-074: Hierarchical Immutable Settings & Pure Domain Policies (Zero-Legacy DDD Hexagonal Redesign)

| Field          | Value                                                                                      |
|----------------|--------------------------------------------------------------------------------------------|
| **Status**     | ACCEPTED                                                                                   |
| **Date**       | 2026-11-23                                                                                 |
| **Authors**    | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)            |
| **Scope**      | Cresmo Knowledge Synthesis Bounded Context — Domain, Application, Infrastructure, Bootstrap, Presentation, Evals |
| **Supersedes** | ADR-069                                                                                    |
| **Relates**    | ADR-000, ADR-005, ADR-010, ADR-011, ADR-026, ADR-058, ADR-062, ADR-064, ADR-066, ADR-067, ADR-072, ADR-073 |

---

## 1. Context & Architectural Motivation

While [ADR-069](ADR-069-modular-domain-settings-package-and-infrastructure-environment.md) eliminated the monolithic `src/cresmo/infrastructure/config.py` file, it preserved flat attribute access and transitional backward compatibility across layers. A clean-slate SOTA-KISS and Hexagonal DDD audit exposed four structural violations:

1. **Application Layer Pollution & ISP Violation (`PipelineSettingsProtocol`):**
   - `src/cresmo/application/ports/settings.py` exposed 25+ mixed fields—including infrastructure vendor choices (`gemini_thinking_level`, `indexing_provider`) and concrete filesystem paths (`data_dir`, `raw_dir`, `playlist_path`)—into `CresmoPipeline`, `ConcatMasterUseCase`, `DiscoverBatchSourcesUseCase`, `RunSynthesisUseCase`, and `StageFactory`.
   - `StageFactory` fell back to seven dynamic `getattr(self.settings, "saturation_*", ...)` lookups because saturation thresholds were omitted from `PipelineSettingsProtocol`.
   - `ConcatMasterUseCase` and `CresmoPipeline` constructed filesystem paths (`data_dir / StageName.WIDE_EXPANDER.value`, `settings.raw_dir`) directly instead of querying `VaultRepositoryPort.resolve_stage_dir(...)`.

2. **Flat God Object via Multiple Inheritance (`CresmoSettings`):**
   - `CresmoSettings` inherited six `BaseSettings` classes into a ~70-field flat namespace.
   - `IngestionSettings` mixed media/worker concerns (`cookies`, `whisper_workers`) with synthesis stage budgets (`expansion_max_passes`, `long_expander_max_passes`, `concat_max_words`, `raw_index_max_attempts`).
   - `SaturationSettings` coupled vector embedding infrastructure (`embedding_provider`, `gemini_embedding_model`) with convergence thresholds (`saturation_*`).

3. **Legacy Compatibility Residue & Naming Drift:**
   - Four `@property` aliases (`gemini_api_key`, `max_retries`, `judge_calibration_models`, `generator_benchmark_models`), `__init__` parameter patches (`pipeline_version`, `gemini_api_key`), mirrored `ClassVar` constants on `CresmoSettings`, and ~20 inconsistent `AliasChoices` (`CRESMO_*` vs unprefixed `ALLCAPS` vs `lowercase`) violated `ADR-010` and `ADR-026` Rule 18.

4. **Impure Nested `BaseSettings` Sub-Models:**
   - Making sub-domain classes inherit `BaseSettings` caused standalone sub-models to read ambient `os.environ` outside the Composition Root and omitted `frozen=True` immutability.

---

## 2. Decision

We will replace the flat multi-inherited `CresmoSettings` and `PipelineSettingsProtocol` with **pure Domain Policy Value Objects**, a **hierarchical immutable `CresmoSettings` composition tree**, and **strict Hexagonal Interface Segregation (ISP) wiring**—with zero backward-compatibility shims (`ADR-010`).

### Pillar 1: Pure Domain Policy Value Objects (`src/cresmo/domain/value_objects/`)
1. Relocate `DEFAULT_LANGUAGE` to `src/cresmo/domain/value_objects/constants.py`.
2. Introduce immutable, construction-time validated Policy Value Objects in `src/cresmo/domain/value_objects/policies.py` (`@dataclass(frozen=True, slots=True)`, zero Pydantic/I/O dependencies, raising `DomainValidationError` and rejecting `bool` for numeric fields):
   - **`StageExecutionPolicy`:** `expansion_max_passes` (`[1, 10]`), `long_expander_max_passes` (`[1, 10]`), `judge_max_attempts` (`>= 1`), `judge_blocking`, `synthesis_temperature` (`None` or `[0.0, 2.0]`), `saturation_thresholds: SaturationThresholds`.
   - **`DiscoveryPolicy`:** `lookback_days` (`>= 0`), `discovery_workers` (`>= 1`), `queue_maxsize` (`>= 1`), `enable_channel_crawler`.
   - **`CompendiumRolloverPolicy`:** `max_words` (`>= 1`).
3. **Delete `src/cresmo/application/ports/settings.py`** (`PipelineSettingsProtocol` and `DefaultPipelineSettings`) completely.
4. Introduce **`DiscoveryPaths`** (`@dataclass(frozen=True)`) in `cresmo.application.use_cases.discovery.models` for explicit path injection into `DiscoverBatchSourcesUseCase`.
5. Update `StageFactory`, `CresmoPipeline`, `ConcatMasterUseCase`, `DiscoverBatchSourcesUseCase`, and `RunSynthesisUseCase` to accept only their narrow policy objects and delegate stage path resolution to `VaultRepositoryPort.resolve_stage_dir(...)`.

### Pillar 2: Hierarchical Immutable Composed Settings Tree (`src/cresmo/infrastructure/config/`)
1. Only **`CresmoSettings`** inherits `pydantic_settings.BaseSettings`, configured with:
   - `env_prefix="CRESMO_"`
   - `env_nested_delimiter="__"`
   - `frozen=True`, `extra="ignore"`
2. All nested settings sections are pure `pydantic.BaseModel` classes with `ConfigDict(frozen=True, extra="forbid")` organized by bounded sub-domain (max 2–3 levels):
   - `llm` (`llm.py`): `LlmSettings` (`gemini: GeminiSettings`, `ollama: OllamaSettings`, `indexing_provider`)
   - `embeddings` (`embeddings.py`): `EmbeddingSettings` (`provider`, `gemini_model`, `gemini_dimensions`, `ollama_model`)
   - `pipeline` (`pipeline.py`): `PipelineSettings` (`language`, `batch_size`, `concat_max_words`, `raw_index_max_chars`, `stages: StageBudgetsSettings`, `saturation: SaturationSettings`)
   - `judge` (`judge.py`): `JudgeSettings` (`provider`, `fallback_provider`, `blocking`, `max_attempts`, `pass_threshold`, `benchmark_models`, `gemini: JudgeGeminiSettings`, `typesafe: TypeSafeSettings`, `gap_filler: GapFillerJudgeSettings`)
   - `ingestion` (`ingestion.py`): `IngestionSettings` (`cookies: CookieSettings`, `workers: WorkerPoolSettings`, `whisper_model`, `days_lookback`, `enable_channel_crawler`, `keep_audio`)
   - `storage` (`storage.py`): `StorageSettings` (`data_dir`, `vault_dir`, filenames/dirnames, custom paths, and derived `@property` directories)
   - `observability` (`observability.py`): `ObservabilitySettings` (`langfuse: LangfuseSettings`, `prometheus: PrometheusSettings`, `logging: LoggingSettings`, `runtime: RuntimeTelemetrySettings`)
3. Sequence leaf fields populated from env strings (`llm.gemini.api_keys`, `judge.benchmark_models`) use `Annotated[tuple[...], NoDecode]` with pure validators supporting comma-separated strings and JSON arrays without overriding `settings_customise_sources`.
4. `WorkerPoolSettings` computes derived `subtitle` (`5 * whisper`) and `channel_discovery` (`10 * whisper`) ratios cleanly inside `@model_validator(mode="after")` using `object.__setattr__` while remaining frozen afterward.
5. Delete `ClassVar` mirrors on `CresmoSettings`, all `AliasChoices`, all `@property` shims (`max_retries`, `gemini_api_key`, `judge_calibration_models`, `generator_benchmark_models`), and obsolete `saturation.py` / `telemetry.py` modules. Constants live exclusively in `catalog.py`.
6. `CresmoSettings` provides explicit translation methods (`to_stage_execution_policy()`, `to_discovery_policy()`, `to_compendium_rollover_policy()`) at the Infrastructure-to-Application boundary.

### Pillar 3: Strict Hexagonal ISP Wiring & Uniform Env Contract
1. Bootstrap factories (`src/cresmo/bootstrap/`) read `CresmoSettings` once at the Composition Root, pass narrow sub-models (`GeminiSettings`, `LlmSettings`, `StorageSettings`, `ObservabilitySettings`) to adapters, and translate domain policies for use cases.
2. All environment variables follow the single canonical contract `CRESMO_<SECTION>__<SUBSECTION>__<FIELD>` across `.env`, `.env.example`, `docker-compose.yml`, `docker/entrypoint.sh`, and `.github/workflows/ci.yml`.

---

## 3. Bounded Context & Domain Model Impact

- **Bounded Context:** Cresmo Knowledge Synthesis (`src/cresmo/`). Root `AppConfig` (`src/config.py`) retains `iam: IamSettings` and `cresmo: CresmoSettings` with zero cross-context leakage.
- **Domain Model:** Adds `StageExecutionPolicy`, `DiscoveryPolicy`, `CompendiumRolloverPolicy`, and `DEFAULT_LANGUAGE`. Zero Pydantic or `pydantic-settings` dependencies introduced into `src/cresmo/domain/` or `src/cresmo/application/`.

---

## 4. Alternatives Considered

1. **Keep Flat Multiple-Inheritance `CresmoSettings` and Standardize Only `AliasChoices`:**
   - Rejected: preserves the ~70-field God Object, keeps mixed concerns in `IngestionSettings`/`SaturationSettings`, and fails to remove `PipelineSettingsProtocol` vendor leakage from Application.
2. **Per-Section `BaseSettings` with Separate Vendor `env_prefix`es (`GEMINI_`, `LANGFUSE_`):**
   - Rejected: reintroduces inconsistent environment prefixes and allows nested `BaseSettings` to bypass root `.env` / `SettingsConfigDict` isolation in tests. Having a single `CRESMO_` + `__` boundary in `CresmoSettings` keeps all nested models pure, frozen `BaseModel`s.
3. **Deep 4+ Level Nesting (`settings.cresmo.pipeline.stages.gap_filler.judge.weights`):**
   - Rejected per SOTA-KISS: `CresmoSettings` already scopes the `cresmo` context, and capping nesting at 2–3 levels avoids verbose call-sites.

---

## 5. Consequences, Security & LGPD

- **Positive:**
  - Complete Hexagonal purity: Domain and Application layers depend only on immutable Domain Policy Value Objects and `VaultRepositoryPort`.
  - Strict ISP across Bootstrap factories, Adapters, and Use Cases (`getattr` configuration lookups eliminated).
  - Single canonical `UPPER_SNAKE_CASE` env contract (`CRESMO_*__*`) and `snake_case` Python attributes (`frozen=True`, `extra="forbid"`).
- **Breaking (`ADR-010`):**
  - `PipelineSettingsProtocol` and `DefaultPipelineSettings` are deleted.
  - All flat `CresmoSettings` attributes, legacy aliases, and unprefixed/`.env` legacy variable names are removed.
- **Security & LGPD:**
  - `llm.gemini.api_keys`, `judge.typesafe.api_key`, and `observability.langfuse.secret_key` remain wrapped in Pydantic `SecretStr`, preventing accidental plaintext serialization in logs or traces.

---

## 6. Test & Mutation Strategy

- **Unit Tests (Domain Policies):** 100% branch and line coverage on `src/cresmo/domain/value_objects/policies.py` covering defaults, immutability, boundary limits, `bool` rejection, non-finite float rejection, and `SaturationThresholds` validation.
- **Unit Tests (Config Tree):** Verify all 7 sub-trees, `frozen=True`, `extra="forbid"`, `NoDecode` comma/JSON decoding, `WorkerPoolSettings` frozen scaling, `LangfuseSettings.environment` regex, and `CRESMO_*__*` `.env`/env loading.
- **Verification Gate:** Zero residual legacy symbol references, full `pytest` suite green, `ruff check` & `ruff format --check` clean, `mypy --strict` zero errors.
