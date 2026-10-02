# ADR-026: SOTA-KISS Code Smell & Anti-Pattern Governance — Clean Code Hygiene, Zero Magic Numbers, and Cross-Platform Reliability

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-09-29                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Canon — All Layers (Domain, Application, Infrastructure, Presentation) |
| **Relates** | ADR-001, ADR-005, ADR-011, ADR-014, ADR-019, ADR-020, ADR-021     |

---

## 1. Context & Architectural Motivation

As the Cresmo Knowledge Synthesis Modular Monolith continues to expand in throughput, multi-tenant execution, and operational observability, maintaining low cognitive load and zero architectural entropy requires codifying explicit hygiene standards.

During the recursive architectural audit across all layers (Domain, Application, Infrastructure, and Presentation), eight distinct categories of recurring code smells and anti-patterns were cataloged:

1. **Imports Intercalados e Imports Locais Desnecessários (Violação PEP 8 / `E402`, `PLC0415`):** Modules placing variables, logger definitions, TypeVars, or eager side-effect executions inside import blocks, as well as burying standard imports inside functions.
2. **Números Mágicos, Códigos de Status e Sentinelas (Hardcoded Magic Numbers / `PLR2004`):** Unnamed literal values (e.g., `timeout=2.0`, `timeout_millis=2000`, `timeout=0.2`), raw HTTP status codes (`200`, `404`, `429`), sentinel fallbacks (`sort_date = 99999999`), and hardcoded string length boundaries scattered across functions.
3. **Supressão Genérica, Silenciosa e Falta de Encadeamento de Exceções (`BLE001`, `S110`, `B904`, `SIM105`):** Broad exception absorption (`except Exception: pass`), unchained exception re-raising, and raw `try-except-pass` constructs that blind observability and corrupt troubleshooting.
4. **Acoplamento de Sistema Operacional e Caminhos Temporários Inseguros (`S108`):** Linux-specific memory metrics (`ru_maxrss * 1024` on Darwin) and hardcoded non-portable temporary paths (e.g. `Path("/tmp/cresmo_worker.heartbeat")`).
5. **"God Files", Módulos Monolíticos e Complexidade Ciclomática Excessiva (`PLR0912`, `PLR0915`):** Files exceeding 500–1000 lines (e.g. `ports.py`, `value_objects.py`, `discover_batch_sources.py`, `pipeline.py`) accumulating disparate concerns with high branch complexity (>12 branches).
6. **Uso de `assert` para Validação de Produção (Zero Production Asserts / `S101`):** Using `assert` statements for dependency validation or control flow that get stripped under `python -O`.
7. **Explosão de Lista de Parâmetros e Obsessão por Primitivos (`PLR0913`, `PLR0917`):** Functions and constructors accepting 6 to 10+ raw primitive parameters instead of cohesive Parameter Objects or Pydantic DTOs.
8. **Código Morto e Parâmetros Assinatura Inutilizados (`ARG001`, `ARG002`):** Methods and functions receiving arguments that are never consumed within the execution body.
9. **Constantes Operacionais e Linhagem em Escopo Global de Módulo / `__init__.py` (Violação 12-Factor Fator III, ADR-005, ADR-011):** Defining runtime operational tags, pipeline versions, or tunable parameters as global variables in module files or `__init__.py` instead of centralizing in `CresmoSettings` (Pydantic Settings V2).
10. **Defensive Fallback Cascading e Instanciação Tardia Oculta (Violação DI & Single Source of Truth):** Declaring optional configuration parameters (`settings: CresmoSettings | None = None`) with inline fallback (`settings or CresmoSettings()`) inside internal functions. This causes unintended disk/env re-reads, bypasses memoized settings factories, and silently drops runtime CLI overrides.

This ADR formally codifies the governance rules, anti-patterns, and required implementations to eliminate these smells across the codebase.

---

## 2. The Clean Code Anti-Pattern Standards

```
+---------------------------------------------------------------------------------------------------+
|                                   ADR-026 ANTI-PATTERN GOVERNANCE                                 |
+---------------------------------------------------------------------------------------------------+
|  [Rule 1] Strict Import Topography      --> Zero Interleaved Code; Top-Level PEP 8 Triad Layout   |
|  [Rule 2] Zero Magic Literals           --> SSOT Named Constants, HTTPStatus, & Pydantic Settings |
|  [Rule 3] Anti-Swallowing & Chaining    --> Narrow Exceptions, Mandatory Logs, & 'raise from'     |
|  [Rule 4] OS-Agnostic Runtime & Storage --> Deterministic Unit Normalization & Safe Temp Paths    |
|  [Rule 5] Bounded Modularity (KISS)     --> Strict File Size, Cohesion, & Cyclomatic Limits       |
|  [Rule 6] Zero Production Asserts       --> Explicit Exceptions for Dependency & Runtime Wiring   |
|  [Rule 7] Cohesive Parameter Bundling   --> Max 5 Parameters; Pydantic DTOs / Parameter Objects   |
|  [Rule 8] Signature Hygiene & Dead Code --> Zero Dangling Unused Parameters Across Concrete Code  |
|  [Rule 9] SSOT Operational Settings     --> Pydantic Settings V2; Zero Global Configs in __init__ |
|  [Rule 10] Anti-Defensive Cascading     --> Early Strict DI; Zero 'settings or Settings()' Inlines|
|  [Rule 11] Anti-Bifurcated Construction --> SSOT Factory Composition; Zero Raw Constructor Bypasses|
|  [Rule 12] Anti-Shadow State Variables  --> Single Canonical Attribute Naming; Zero State Aliasing|
|  [Rule 13] Anti-Middle Man & Builders   --> Direct Invocations & Direct Pure DI; Zero Trampolines   |
|  [Rule 14] Liskov Substitution & SOLID  --> Upfront Port Typing, Full Subtype Interchangeability   |
+---------------------------------------------------------------------------------------------------+
```

---

### Rule 1: Strict Import Topography & Zero Interleaved Execution (PEP 8 Compliance)

#### 1.1 The Anti-Pattern
Placing `logger = logging.getLogger(__name__)`, `TypeVar`, module-level assignments, or executable code blocks (such as eager plugin loading or monkey-patching) before or between `import` statements. Additionally, burying imports inside functions (`PLC0415`) without architectural necessity.

```python
# ANTI-PATTERN: Interleaving variables, code, or local imports within modules
import logging
logger = logging.getLogger(__name__)
_StageRet = TypeVar("_StageRet")

from cresmo.application.ports import TelemetryPort  # VIOLATION: Interleaved import

def my_function():
    import threading  # VIOLATION: Unnecessary local import of standard library
    from cresmo.domain.value_objects import normalize_to_uploads_playlist_url  # VIOLATION
```

#### 1.2 The Standard & Remediation
* All module imports MUST strictly reside at the very top of the file, immediately following the module docstring and `from __future__ import annotations`.
* Imports must be structured into three contiguous groups separated by a single blank line:
  1. Standard Library imports
  2. Third-party vendor imports
  3. Local Cresmo package imports
* Variable assignments (`logger = ...`, `TypeVar`, `_StageRet`) MUST be placed AFTER all imports are declared.
* Side effects (such as eager plugin initialization) MUST NOT execute at module import time; they must be encapsulated in explicit startup hooks or bootstrap functions within `composition.py`.
* Local imports (`PLC0415`) are strictly prohibited unless dealing with an optional, extremely heavy vendor library specifically isolated within a dedicated lazy-loading adapter.

---

### Rule 2: Zero Magic Numbers, Status Codes & Centralized Parameterization

#### 2.1 The Anti-Pattern
Hardcoding literal numbers for network timeouts, queue poll intervals, batch limits, cache durations, HTTP status codes, or sentinel fallback values directly inside function calls without contextual naming.

```python
# ANTI-PATTERN: Magic numbers and status codes without semantic context
with urllib.request.urlopen(req, timeout=2.0) as response:  # VIOLATION: Magic timeout
    if response.status == 200:  # VIOLATION: Magic HTTP status
        ...
if exc.code == 429:  # VIOLATION: Magic HTTP status
    ...
sort_date = 99999999  # VIOLATION: Magic sentinel fallback
if len(channel_id) > 64:  # VIOLATION: Magic boundary length
    ...
```

#### 2.2 The Standard & Remediation
* Any numeric literal representing time, retries, thresholds, or buffer sizes MUST be declared as a named, typed constant at the top of the module or encapsulated in `CresmoSettings` (Pydantic Settings V2).
* All HTTP status comparisons MUST use the standard library `http.HTTPStatus` enum (`HTTPStatus.OK`, `HTTPStatus.NOT_FOUND`, `HTTPStatus.TOO_MANY_REQUESTS`).
* Domain boundary limits (such as maximum name or ID lengths) MUST be hoisted to named constants in domain value object definitions (`MAX_CHANNEL_NAME_LENGTH = 120`, `MAX_CHANNEL_ID_LENGTH = 64`).
* Sentinel fallback values must be explicitly named (e.g. `SENTINEL_FALLBACK_SORT_DATE = 99_999_999`).
* Example:
  ```python
  from http import HTTPStatus
  
  DEFAULT_HEALTHCHECK_TIMEOUT_SECONDS: float = 2.0
  OTEL_FLUSH_TIMEOUT_MS: int = 2000
  QUEUE_STREAM_TIMEOUT_SECONDS: float = 0.2
  SENTINEL_FALLBACK_SORT_DATE: int = 99_999_999
  
  if response.status == HTTPStatus.OK:
      ...
  ```

---

### Rule 3: Explicit Exception Handling, Anti-Swallowing & Exception Chaining

#### 3.1 The Anti-Pattern
Using broad `except Exception:` blocks with `pass`, suppressing all errors (even unexpected defects such as `AttributeError`, `TypeError`, or out-of-memory errors), re-raising exceptions without proper chaining (`B904`), and using bare `try-except-pass` instead of context managers or diagnostic logs.

```python
# ANTI-PATTERN: Silent exception swallowing and unchained re-raising
try:
    meta = yaml.safe_load(frontmatter)
except Exception:  # noqa: BLE001, S110 - VIOLATION: Swallowing everything
    pass

try:
    modality = SourceModality(self.kind.strip().lower())
except ValueError:
    raise ValueError("Invalid modality")  # VIOLATION: B904 missing 'from None' or 'from err'
```

#### 3.2 The Standard & Remediation
1. **Narrow Exception Typing:** Catch ONLY the specific expected exceptions (e.g., `(yaml.YAMLError, ValueError, KeyError)`).
2. **Mandatory Diagnostic Logging:** Even when graceful degradation is intentional, code MUST emit a structured diagnostic log:
   ```python
   except yaml.YAMLError as exc:
       logger.debug("Failed to parse YAML frontmatter for %s, retaining defaults: %s", content_id.value, exc)
   ```
3. **Exception Chaining (`B904`):** When raising a new exception inside an `except` block, explicitly specify the cause using `from exc` or sever the context cleanly using `from None`:
   ```python
   except ValueError as exc:
       raise ValueError(f"Invalid modality '{self.kind}'") from exc
   ```
4. **Contextlib Suppression Governance (`SIM105`):** Use `with contextlib.suppress(SpecificException):` ONLY when failure is provably benign and non-diagnostic; otherwise use explicit try/except with structured diagnostic logging.
5. **Fault Isolation Boundaries:** If catching `Exception` is strictly necessary at an outer boundary (e.g. an asynchronous background worker loop to prevent thread death), the exception MUST be logged with `logger.warning("Worker failure: %s", exc, exc_info=True)` and increment an error counter in `MetricsPort`.

---

### Rule 4: Cross-Platform Runtime Abstraction & Safe Storage Paths

#### 4.1 The Anti-Pattern
Assuming a single operating system kernel behavior when querying system metrics (e.g. Linux vs Darwin memory counters) or using hardcoded paths like `/tmp/cresmo_worker.heartbeat` (`S108`).

```python
# ANTI-PATTERN: Hardcoded assumption that ru_maxrss is always in kilobytes
rss_bytes = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)

# ANTI-PATTERN: Insecure, non-portable hardcoded temporary path
heartbeat_file = Path("/tmp/cresmo_worker.heartbeat")  # VIOLATION: S108 & Windows incompatible
```

#### 4.2 The Standard & Remediation
* All system resource inspection MUST normalize units using cross-platform detection:
  * On Linux, `ru_maxrss` is in **Kilobytes** (requiring `* 1024` for bytes).
  * On Darwin (macOS), `ru_maxrss` is already in **Bytes**.
  ```python
  import sys
  import resource

  def get_process_rss_bytes() -> float:
      """Return resident set size in bytes, normalizing Linux and Darwin kernel differences."""
      raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
      if sys.platform == "darwin":
          return float(raw_rss)
      return float(raw_rss * 1024)
  ```
* All runtime status, lock, and heartbeat files MUST be rooted in `settings.data_dir` or dynamically resolved via `tempfile.gettempdir()`, never hardcoded to `/tmp/`.

---

### Rule 5: Bounded Modularity, Anti-"God Files", & Complexity Control (KISS Principle)

#### 5.1 The Anti-Pattern
Accumulating disparate responsibilities within a single file or class, resulting in modules exceeding 500–1000 lines, or functions with high cyclomatic complexity (`PLR0912` > 12 branches) or excessive statements (`PLR0915` > 50 statements).
* *Examples in Codebase:*
  * `application/ports.py` (1036 lines): Single file defining every port across all domains.
  * `domain/value_objects.py` (1027 lines): All value objects merged into a monolithic file.
  * `application/use_cases/discover_batch_sources.py` (916 lines): Accumulating regex parsing, web scraping, channel resolution, and multi-threaded queue streaming.

#### 5.2 The Standard & Remediation
1. **Single Responsibility Principle (SRP):** Each module must have one reason to change.
2. **Decomposition Threshold:** Files exceeding ~500 lines are candidates for architectural refactoring into focused sub-components:
   * **Parsing & Taxonomy:** Isolate regular expressions and string transformers into pure value objects or taxonomy strategies.
   * **Concurrency & Streaming:** Isolate queue streaming coordination from payload evaluation.
   * **Ports Segregation:** Segregate ports into cohesive modules (e.g. `ports/media.py`, `ports/telemetry.py`, `ports/storage.py`, `ports/llm.py`) unified by an aggregate `__init__.py` facade.
3. **Cyclomatic Complexity Limit (`PLR0912`):** No function should exceed 12 branches. High-branch functions (e.g. `classify_channel`, `_merge_notes`, `_extract_individual_objects`) must be refactored into lookup dispatch dictionaries or polymorphic strategies.

---

### Rule 6: Zero Production Asserts (Proibição de `assert` em Código de Produção)

#### 6.1 The Anti-Pattern
Using `assert` statements in presentation, application, or infrastructure code to validate dependency injection, configuration state, or business invariants.

```python
# ANTI-PATTERN: Using assert for production dependency wiring
assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."  # VIOLATION
```
* **Failure Vector:** When Python runs with optimizations (`python -O` or `PYTHONOPTIMIZE=1`), all `assert` statements are stripped from the generated bytecode (`.pyc`). The validation is completely bypassed in production, leading to silent failures or catastrophic null pointer crashes later.

#### 6.2 The Standard & Remediation
* Production code MUST NEVER rely on `assert` for runtime validation or dependency wiring.
* Instead, raise explicit, typed exceptions with clear diagnostic messages:
  ```python
  if pipeline.ledger_port is None:
      raise RuntimeError("Ledger port must be wired for channel sync.")
  ```
* `assert` statements are permitted exclusively within the `tests/` directory as pytest verification assertions.

---

### Rule 7: Cohesive Parameter Bundling & Primitive Obsession Control

#### 7.1 The Anti-Pattern
Functions and constructors accepting 6 to 10+ individual primitive parameters (`PLR0913`, `PLR0917`).
* *Examples:* `KnowledgeSynthesisPipeline.__init__` (10 parameters), `IndexRawTranscriptsUseCase.__init__` (9 parameters), `_collect_channel_urls` (6 parameters).

#### 7.2 The Standard & Remediation
* No function or constructor should exceed 5 positional parameters.
* When a function requires multiple related configurations, bundle them into a typed Pydantic DTO, dataclass, or Domain Parameter Object (e.g. `PipelineDependencies`, `SyncFilterCriteria`, `IngestionOptions`).
* Use keyword-only arguments (`*`) for constructors with optional dependencies to ensure explicit wiring readability.

---

### Rule 8: Dead Code & Signature Hygiene (Zero Dangling Parameters)

#### 8.1 The Anti-Pattern
Declaring parameters in function or method signatures that are never used in the function body (`ARG001`, `ARG002`), indicating API drift or incomplete refactorings.
* *Example:* `_collect_channel_urls` in `sync.py` receiving `settings`, `lookback`, `max_videos` without consuming them.

#### 8.2 The Standard & Remediation
* Concrete functions and methods must not accept unconsumed arguments. Remove dead parameters from call sites and function signatures.
* When adhering to external interfaces or ABCs where certain arguments are deliberately unneeded in specific adapters (e.g. `NoOpTelemetryAdapter`), prefix the argument name with an underscore (e.g. `_session_id`, `_user_id`) to signal intentional non-use to static analyzers.

---

### Rule 9: Zero Module-Level Operational Constants & Package Root Cleanliness

#### 9.1 The Anti-Pattern
Declaring operational configurations, pipeline version identifiers, or telemetry tags (such as `PIPELINE_VERSION = "cresmo:v2"`) as global module variables or inside the package root `__init__.py`.
* **Violations:**
  1. **12-Factor App (Factor III: Config):** Hardcoded module globals cannot be reconfigured per environment (`.env`, Docker staging, canary deployments) without modifying and recommitting code.
  2. **Inverted Dependency:** Infrastructure adapters (e.g., `OpenTelemetryAdapter`) end up importing operational constants from the package root `__init__.py` (`from cresmo import PIPELINE_VERSION`), coupling low-level adapters to high-level package entrypoints.
  3. **Conflation of Distribution Artifact vs Runtime Lineage:** Conflates static Python packaging metadata (`__version__` per PEP 396/PEP 621) with dynamic execution lineage.

```python
# ANTI-PATTERN: Operational lineage or tunables hardcoded in __init__.py
# src/cresmo/__init__.py
__version__ = "0.1.0"
PIPELINE_VERSION = "cresmo:v2"  # VIOLATION: Operational tunable in package root!
```

#### 9.2 The Standard & Remediation
1. **Packaging Metadata Only in `__init__.py`:** The package root `__init__.py` MUST strictly contain packaging metadata (`__version__` and `__all__`).
2. **Centralized SSOT in `CresmoSettings`:** All operational identifiers, pipeline versions, and telemetry lineage tags MUST be declared as fields in `CresmoSettings` (`src/cresmo/infrastructure/config.py`) using Pydantic Settings V2:
   ```python
   pipeline_version: str = Field(
       default="cresmo:v2",
       description="Canonical pipeline version tag emitted to OpenTelemetry spans and Langfuse traces.",
       validation_alias=AliasChoices("PIPELINE_VERSION", "pipeline_version"),
   )
   ```
3. **Explicit Dependency Injection:** Adapters requiring the pipeline version MUST receive it via constructor injection (`OpenTelemetryAdapter(..., pipeline_version=settings.pipeline_version)`) wired at the Composition Root (`composition.py`), never importing from `cresmo.__init__`.

---

### Rule 10: Anti-Defensive Fallback Cascading & Early Strict Dependency Injection

#### 10.1 The Anti-Pattern
Declaring optional configuration parameters (`settings: CresmoSettings | None = None`) in internal functions, services, or use cases with inline fallback logic:
```python
# ANTI-PATTERN: Defensive fallback cascading and late unshared instantiation
def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,  # Smelly optional parameter
) -> Iterator[BatchSource]:
    resolved_settings = settings or CresmoSettings()  # VIOLATION: Unintended I/O & unmemoized instance!
    ...
```
**Architectural Violations:**
1. **Bypasses Single Source of Truth & Memoization:** Chamar `CresmoSettings()` diretamente bypassa a fábrica centralizada `resolve_shared_settings()`, forçando o Pydantic a reler o sistema de arquivos, revalidar `.env` e instanciar múltiplos objetos desacoplados durante a mesma execução.
2. **Perda Silenciosa de Configurações Dinâmicas (Upstream Overrides):** Se o comando raiz modificou alguma propriedade (por exemplo, `settings.days_lookback = args.lookback`), uma função mais abaixo que faça fallback para `CresmoSettings()` perde silenciosamente esse override, operando com valores default incorretos.
3. **Assinaturas Falsas (Leaky / Dishonest Signatures):** Funções que não podem operar sem diretórios configurados (`vault_dir`, `raw_dir`) não são opcionais. Declarar `None` na assinatura comunica falsamente que a configuração é dispensável.

#### 10.2 The Standard & Remediation
1. **Early Resolution at Command Entrypoint:** CLI command handlers (`handle_run`, `handle_sync`, etc.) resolve the shared configuration once at the very top using `resolve_shared_settings()`:
   ```python
   settings = resolve_shared_settings()
   ```
2. **Strict Mandatory Injection in Internal Functions:** All downstream functions, adapters, and use cases require `settings: CresmoSettings` as an explicit, mandatory parameter (no `| None = None` and no `settings or CresmoSettings()` fallback):
   ```python
   def load_batch_sources(
       query: BatchDiscoveryQuery,
       settings: CresmoSettings,  # Strictly required
   ) -> Iterator[BatchSource]:
       # Use settings directly with zero defensive boilerplate
   ```
3. **Factory Resolution for Public Entrypoints:** Only top-level factory functions designed for public composition or test convenience may accept `settings: CresmoSettings | None = None`, and they MUST delegate exclusively to `resolve_shared_settings(settings)` rather than executing raw constructor fallbacks.

---

### Rule 11: Anti-Bifurcated Construction & Leaky Factory Bypass (Single Source of Truth)

#### 11.1 The Anti-Pattern
Implementing conditional branching in presentation commands, orchestrators, or callers that bifurcates object construction between a factory call and a direct concrete class constructor:
```python
# ANTI-PATTERN: Bifurcated Construction and Leaky Factory Bypass
if media_ingestion_port is None:
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
else:
    discovery_use_case = DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
```

**Architectural Violations:**
1. **Bypasses Single Source of Truth (SSOT):** When a dedicated factory (`build_discover_batch_sources_use_case`) exists, it must be the sole authority on constructing and wiring that Use Case. Bypassing the factory in an `else` branch duplicates constructor arguments and leaks concrete implementation details into the caller.
2. **Violation of SLAP (Single Level of Abstraction Principle) & DRY:** Presentation helpers (`load_batch_sources`) should orchestrate execution, not manage conditional infrastructure dependency resolution.
3. **Brittle Dependency Evolution:** If the Use Case constructor evolves (e.g., adding an anonymizer, ledger port, or telemetry wrapper), every bifurcated `else` branch breaks or fails to receive the new cross-cutting concern.

#### 11.2 The Standard & Remediation
1. **Factories as Open Ports Acceptors:** All use case and pipeline factories (`build_*`) MUST accept optional port overrides (`port: PortInterface | None = None`). If a port is provided, the factory injects it directly; if `None`, the factory constructs or resolves the default adapter.
   ```python
   def build_discover_batch_sources_use_case(
       settings: CresmoSettings | None = None,
       media_ingestion_port: MediaIngestionPort | None = None,
       progress_callback: Callable[[str], object] | None = None,
   ) -> DiscoverBatchSourcesUseCase:
       resolved_settings = resolve_shared_settings(settings)
       resolved_media_port = media_ingestion_port or build_media_ingestion_adapter(resolved_settings)
       return DiscoverBatchSourcesUseCase(
           media_ingestion_port=resolved_media_port,
           settings=resolved_settings,
           progress_callback=progress_callback,
       )
   ```
2. **Unconditional Delegation in Callers:** Callers and presentation helpers delegate 100% of object construction to the factory in a single, clean invocation:
   ```python
   def load_batch_sources(
       query: BatchDiscoveryQuery,
       settings: CresmoSettings,
       media_ingestion_port: MediaIngestionPort | None = None,
   ) -> Iterator[BatchSource]:
       discovery_use_case = build_discover_batch_sources_use_case(
           settings=settings,
           media_ingestion_port=media_ingestion_port,
           progress_callback=lambda msg: sys.stdout.write(msg),
       )
       return discovery_use_case.execute(query=query)
   ```
3. **Decoupled Callers:** Presentation command modules (`run.py`, etc.) MUST NOT import concrete Use Case classes if a factory exists for them. They depend strictly on the factory and domain DTOs/queries.

---

### Rule 12: Anti-Shadow State Variables & Variable Aliasing

#### 12.1 The Anti-Pattern
Declaring temporary "shadow" state variables (such as `channel_for_metrics = "Unknown_Channel"` or `channel_id_for_metrics = ""`) before a `try` block to satisfy a `finally` or telemetry handler, while extracting or computing the primary domain variable (`channel_name`, `ch_id`) inside the `try` block, and subsequently synchronizing them with explicit aliasing assignments:
```python
# ANTI-PATTERN: Shadow State Variables and Redundant Variable Aliasing
channel_for_metrics = "Unknown_Channel"  # Shadow variable
channel_id_for_metrics = ""

try:
    ...
    body, channel_name = self._resolve_transcript_body(...)
    channel_for_metrics = channel_name  # Redundant aliasing / state synchronization

    transcript, ch_id = self._build_raw_transcript_aggregate(...)
    if ch_id:
        channel_id_for_metrics = ch_id.value  # Secondary shadow synchronization
    return transcript
finally:
    labels = {
        "channel_id": channel_id_for_metrics,
        "channel_name": channel_for_metrics,
    }
```
Another manifestation is loop shadow counters (e.g. maintaining `total_items += 1` inside an `enumerate(sources, 1)` loop instead of referencing `source_index` or deriving `completed + skipped + failed`).

**Architectural Violations:**
1. **Dual State & Variable Aliasing:** Maintaining two names for the same logical entity (`channel_for_metrics` vs `channel_name`) introduces cognitive overhead and state desynchronization risk if an early return or exception path updates one but not the other.
2. **Noise & Superfluous Synchronization Statements:** Lines like `channel_for_metrics = channel_name` exist solely as band-aids for disjointed variable scoping and violate DRY and KISS principles.
3. **Violates Ubiquitous Language & SSOT:** Domain and telemetry models should share canonical naming without artificial translation layers within the same function scope.

#### 12.2 The Standard & Remediation
1. **Initialize Canonical Identifiers at Function Scope:** Declare the canonical domain variables (`channel_name = "Unknown_Channel"`, `channel_id = ""`) with safe, fallback defaults directly at the function root before the `try` block.
2. **Assign Directly Without Aliasing:** Unpack or assign directly to the canonical variables inside the `try` block (`body, channel_name = ...`, `if ch_id: channel_id = ch_id.value`).
3. **Consume Canonical Variables in `finally` and Exit Handlers:** The `finally` block consumes the canonical variables directly with 100% safety and zero synchronization boilerplate:
   ```python
   channel_name = "Unknown_Channel"
   channel_id = ""

   try:
       ...
       body, channel_name = self._resolve_transcript_body(...)
       transcript, ch_id = self._build_raw_transcript_aggregate(
           video_url=video_url,
           info=info,
           body=body,
           channel_name=channel_name,
       )
       if ch_id:
           channel_id = ch_id.value
       return transcript
   finally:
       elapsed = time.perf_counter() - start_time
       self._metrics_port.observe_histogram(
           "cresmo_media_ingestion_duration_seconds",
           elapsed,
           labels={
               "channel_id": channel_id,
               "channel_name": channel_name,
               "modality": "url",
               "status": status,
           },
       )
   ```
4. **Derive Aggregates Instead of Shadow Counting:** Avoid shadow accumulator variables across loop iterations when the state is already captured by loop indices (`enumerate`) or partitioned outcome counters (`completed + skipped + failed`).

---

### Rule 13: Anti-Middle Man / Pass-Through Trampoline Methods & Builders (Remove Middle Man)

#### 13.1 The Anti-Pattern
Declaring private wrapper methods or factory functions that take exact identical parameters and do nothing except forward them 1:1 to an internal collaborator, function, or concrete constructor:
```python
# ANTI-PATTERN 1: Middle Man / Pass-Through Trampoline Method
def _extract_concepts(
    self,
    video_id: ContentId,
    title: str,
    text: str,
    channel_name: ChannelName,
    channel_id: ChannelId | None = None,
    user: UserIdentity | None = None,
) -> str:
    return self._distiller.extract_concepts(
        video_id=video_id,
        title=title,
        text=text,
        channel_name=channel_name,
        channel_id=channel_id,
        user=user,
    )
```
Another common manifestation:
```python
def _load_transcript_from_file(self, file_path: Path) -> RawTranscript:
    return load_transcript_from_file(file_path)
```
A third critical manifestation in Dependency Injection / Presentation Composition:
```python
# ANTI-PATTERN 2: Pass-Through Factory Trampoline / Middle Man Builder
def build_critique_synthesizer_adapter(
    llm_transformation_port: LLMTransformationPort | None,
    prompt_provider: PromptProviderPort | None = None,
) -> CritiqueSynthesizerPort:
    return OllamaCritiqueAdapter(
        llm_transformation_port=llm_transformation_port,
        prompt_provider=prompt_provider,
    )
```

**Architectural Violations:**
1. **Middle Man Code Smell (Martin Fowler, Refactoring):** When a class, orchestrator, or factory function merely delegates calls to another collaborator or constructor without adding business logic, polymorphic dispatch, translation, validation, caching, secret resolution, or error handling, it acts as an unnecessary middle man.
2. **Indirection Without Abstraction (Cognitive Bloat & Speculative Generality):** Developers reading the execution flow or composition root must jump into a factory or private helper, only to find that it adds zero value and immediately delegates to a single deterministic concrete class.
3. **Signature Duplication & Fragility:** Every change to the collaborator's or adapter's constructor signature requires updating both the trampoline and the caller, duplicating parameter lists and type hints for no architectural benefit.

#### 13.2 The Standard & Remediation
1. **Remove Middle Man (Direct Collaborator Invocation):** Invoke the internal collaborator directly at the call site within the orchestrating method:
   ```python
   # INSTEAD OF self._extract_concepts(...):
   concept = self._distiller.extract_concepts(
       video_id=video_id,
       title=title,
       text=excerpt,
       channel_name=channel_name,
       channel_id=transcript.channel_id,
       user=user,
   )
   ```
2. **Eliminate Wrapper Methods for Module Functions:** When a standalone domain/infrastructure function is imported (e.g., `load_transcript_from_file`), call it directly (`raw = load_transcript_from_file(file_path)`) rather than wrapping it in a private instance method (`self._load_transcript_from_file`).
3. **Direct Instantiation in Pure DI Composition Roots (KISS vs Factory Justification):**
   - **Factories / Builders are justified IF AND ONLY IF:** they perform runtime polymorphic dispatch (e.g., switching between Gemini and Ollama based on `settings.indexing_provider` or `settings.judge_provider`), secret extraction/validation (`api_key.get_secret_value()`), or complex lifecycle management.
   - **Direct Instantiation:** When an adapter has a single deterministic implementation and takes already-resolved dependencies (e.g., `SqliteLedgerAdapter(db_path=...)` or `OllamaCritiqueAdapter(llm_transformation_port=..., prompt_provider=...)`), instantiate it directly within the Composition Root (`composition.py`). Do not introduce speculative factory functions that act as middle men:
     ```python
     # REMEDIATION: Direct Instantiation in Pure DI Composition Root
     critique_synthesizer = OllamaCritiqueAdapter(
         llm_transformation_port=llm_indexing_port,
         prompt_provider=prompt_provider,
     )
     ```
4. **Legitimate Delegators vs Trampolines:** Public Facades implementing an interface/port (e.g. `ObsidianVaultAdapter` implementing `VaultRepositoryPort` by delegating to sub-repositories) or methods adding ACL validation, telemetry spans, or error translation are legitimate. Pure zero-logic pass-throughs are prohibited.

---

### Rule 14: Liskov Substitution Principle (LSP) & SOLID Alignment across Ports, Adapters, and Factories

#### 14.1 The Anti-Pattern
Violations of the **Liskov Substitution Principle (LSP)** and core **SOLID** principles typically manifest in Python modular monoliths in three distinct smells:

1. **Leaky Subtype Inference & Untyped Factory Branching:**
   In dependency injection factories, instantiating concrete adapters within conditional branching (`if / elif / else`) without declaring the target Port interface upfront. This causes static type checkers (`mypy`, `pyright`) to infer wide, leaky union types (e.g. `TypeSafeJudgeAdapter | OllamaJudgeAdapter | GeminiJudgeAdapter`) instead of the unified Port abstraction (`LlmJudgePort`):
   ```python
   # ANTI-PATTERN: Implicit Leaky Subtype Assignment in Factory
   def build_llm_judge_adapter(settings: CresmoSettings) -> LlmJudgePort:
       provider = settings.judge_provider
       if provider == "typesafe":
           primary = TypeSafeJudgeAdapter(...)  # inferred as TypeSafeJudgeAdapter
       elif provider == "ollama":
           primary = OllamaJudgeAdapter(...)    # inferred as Union[TypeSafe, Ollama]
       else:
           primary = GeminiJudgeAdapter(...)    # union leakage
       
       # Downstream consumers may accidentally couple to concrete subtype specifics
       return ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)
   ```

2. **Contract Precondition Strengthening or Postcondition Weakening:**
   Concrete adapters that alter method signatures, raise undeclared non-domain exceptions instead of standard domain errors, or fail to honor return type invariants established by the Port contract (e.g., failing to return a valid `JudgeEvaluation` for `LlmJudgePort.evaluate()`).

3. **Subtype Downcasting and `isinstance` Branching (Violation of OCP & LSP):**
   Downstream components (orchestrators, use cases, or composites) inspecting the concrete type of an injected Port via `isinstance(adapter, ConcreteAdapter)` to execute special-case logic, destroying the polymorphism guaranteed by Hexagonal Architecture.

#### 14.2 The Standard & Remediation

1. **Explicit Upfront Port Typing (Single Target Port Contract):**
   In all DI factory functions, declare the variable type explicitly as the abstract Port interface **before** the conditional resolution block. This enforces at compile time (via `mypy` / `pyright`) that every execution branch assigns an object that strictly satisfies the Port contract:
   ```python
   # STANDARD: Explicit Port Interface Declaration Upfront (LSP & Hexagonal DI)
   primary: LlmJudgePort
   provider = settings.judge_provider.lower().strip()
   if provider == "typesafe":
       primary = TypeSafeJudgeAdapter(
           api_key=settings.typesafe_api_key.get_secret_value(),
           model=settings.typesafe_model,
           base_url=settings.typesafe_base_url,
       )
   elif provider == "ollama":
       primary = OllamaJudgeAdapter(
           base_url=settings.ollama_base_url,
           model=settings.ollama_model,
           timeout_seconds=settings.ollama_timeout_seconds,
       )
   else:
       primary = GeminiJudgeAdapter(
           api_key=settings.gemini_api_key.get_secret_value(),
           model=settings.gemini_model,
       )
   ```

2. **Full Interchangeability of Implementations (LSP):**
   Any adapter implementing a Port (such as `GeminiJudgeAdapter`, `OllamaJudgeAdapter`, `TypeSafeJudgeAdapter`, or composite wrappers like `ResilientCompositeJudgeAdapter` and `LangfuseJudgeDecorator` for `LlmJudgePort`) must be 100% interchangeable at runtime without requiring any branch or adapter-specific handling from callers.

3. **SOLID Architectural Alignment:**
   - **Single Responsibility Principle (SRP):** Each adapter has one distinct responsibility (e.g. `GeminiJudgeAdapter` for Google GenAI structured inference, `LangfuseJudgeDecorator` for telemetry ingestion).
   - **Open/Closed Principle (OCP):** New providers are added by implementing the Port and registering a new branch in the factory, requiring zero modifications to domain use cases or orchestrators.
   - **Liskov Substitution Principle (LSP):** Derived adapters strictly honor Port contract invariants and return types.
   - **Interface Segregation Principle (ISP):** Hexagonal Ports remain lean and fine-grained (e.g. `LlmJudgePort` exposes only `evaluate(context)`, decoupled from generative text synthesis in `LLMTransformationPort`).
   - **Dependency Inversion Principle (DIP):** Domain and Application use cases depend solely on Port abstractions (`LlmJudgePort`), never on concrete infrastructure adapters or external SDKs.

---

## 3. Enforcement & Quality Gates


The following Ruff rules and architecture checks are enforced across the entire repository:

| Ruff Code | Rule Description | Severity | Target Scope |
| :--- | :--- | :--- | :--- |
| **`E402`** | Module level import not at top of file | **BLOCKING** | All files in `src/` and `tests/` |
| **`S101`** | Use of `assert` detected | **BLOCKING** | `src/` (strictly zero asserts) |
| **`PLR2004`**| Magic value used in comparison | **BLOCKING** | `src/` (hoist to constants / `HTTPStatus`) |
| **`B904`** | Unchained exception inside `except` | **BLOCKING** | `src/` (require `from exc` or `from None`) |
| **`BLE001`**| Blind exception catch (`except Exception:`) | **AUDITED** | Require narrow types or mandatory log |
| **`S110`** | `try-except-pass` silent swallowing | **BLOCKING** | Prohibited without narrow types & debug log |
| **`S108`** | Insecure usage of `/tmp` file | **BLOCKING** | Prohibited; use `tempfile` or `settings.data_dir` |
| **`PLC0415`**| Non-top-level import | **BLOCKING** | Cleaned up across all non-lazy components |
| **`PLR0913`**| Too many arguments in function (>5) | **AUDITED** | Refactor to DTO / Parameter Object |
| **`PLR0912`**| Too many branches (>12) | **AUDITED** | Refactor to strategy tables |
| **`ARG001`**| Unused function argument | **BLOCKING** | Cleaned up or prefixed with `_` |
| **`ARG002`**| Unused method argument | **AUDITED** | Prefix with `_` in NoOp / Null-Object adapters |
