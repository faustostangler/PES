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

This ADR formally codifies the governance rules, anti-patterns, and required implementations to eliminate these smells across the codebase.

---

## 2. The Eight Clean Code Anti-Pattern Standards

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
