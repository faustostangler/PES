# ADR-020: SOTA-KISS Architectural Canon — Concurrency Topology, Zero Primitive Obsession, Contract Integrity, and Boundary ACLs

**Status:** ACCEPTED  
**Date:** 2026-09-24  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, Zero Primitive Obsession, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-003`](ADR-003-pes-production-architecture.md), [`ADR-009`](ADR-009-streaming-batch-source-discovery-producer-consumer.md), [`ADR-010`](ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md)

---

## 1. Context & Architectural Motivation

As the Cresmo Strategic Knowledge Monolith matured through the execution of ADRs 001 to 019, several engineering invariants emerged across our high-throughput pipeline and multi-threaded discovery subsystems. While individual use cases and adapters were refactored for specific functional needs, a cohesive architectural canon was required to formally codify the **Doctor Stangler SOTA-KISS (State of the Art / Keep It Simple, Stupid)** principles.

Without an authoritative, codified architectural canon, distributed codebases inevitably suffer from seven distinct entropy vectors:
1. **Primitive Obsession Drift:** Domain semantics decaying into raw strings and ints (`str`, `dict`), transferring invariant validation burdens to downstream layers.
2. **Port Role Ambiguity:** Hexagonal ports named after concrete technologies (`llm_port`) rather than business intents (`llm_synthesis_port`), coupling callers to tools and creating configuration leakage.
3. **Use Case Interface Divergence:** Invocations splintering into ad-hoc verbs (`execute_for_channel`, `index_single_transcript`), escalating cognitive load and impeding generic dispatching.
4. **Contractual Paranoia (Vestigial Defensiveness):** Defensive duck-typing (`hasattr`) undermining abstract base class (ABC) guarantees and violating the Liskov Substitution Principle (LSP).
5. **Anonymous Concurrency Sinks:** Unnamed worker threads and pools (`ThreadPoolExecutor-0_1`) obscuring root causes during Linux thread dumps (`/proc/{pid}/task`), Linux CPU profiling, and SRE incident post-mortems.
6. **Asynchronous TOCTOU Vulnerabilities:** Race conditions caused by mutating shared callbacks between inspection and execution under multi-threaded streaming.
7. **Boundary Leakage (Driver Impedance Mismatch):** Infrastructure adapters allowing low-level database driver constraints (such as `sqlite3` refusing custom Python types) to coerce domain entities back into primitives.

This ADR establishes the **Seven SOTA-KISS Architectural Pillars** governing all present and future modules in the Cresmo workspace.

---

## 2. The Seven SOTA-KISS Architectural Pillars

```
+---------------------------------------------------------------------------------------------+
|                                    CRESMO SOTA-KISS CANON                                   |
+---------------------------------------------------------------------------------------------+
|  [P1] Zero Primitive Obsession    --> Immutable Value Objects + Central Sanitization        |
|  [P2] Role-Based Port Segregation --> ISP: Intent over Tech + Decoupled Calibration        |
|  [P3] Universal Invocation (KISS) --> Single Canonical .execute(...) Entrypoint             |
|  [P4] Contract Integrity          --> Fail-Fast Polymorphism (Eliminate hasattr Guards)     |
|  [P5] Thread Topology & APM       --> Canonical thread_name_prefix + Zero Anonymous Pools   |
|  [P6] Anti-TOCTOU State Isolation --> Local Snapshot Pattern + Reentrant Lock Isolation     |
|  [P7] Persistence ACL Shield      --> Driver Impedance Mismatch Absorbed at Adapter Layer   |
+---------------------------------------------------------------------------------------------+
```

---

### Pillar 1: Semântica de Domínio Estrita e Erradicação da Obsessão por Primitivos (Zero Primitive Obsession)

Raw language primitives (`str`, `int`, `float`, `dict`) MUST NEVER carry business rules or domain identity across architectural boundaries.

1. **Immutable Value Objects:**
   Domain concepts such as channel names, media IDs, and input modalities are encapsulated in `@dataclass(frozen=True)` or `Enum` classes (e.g., `ChannelName`, `ContentId`, `SourceModality`).
2. **Centralized Sanitization & Fail-Fast Invariants:**
   Validation occurs strictly within the Value Object constructor (`__post_init__`). Invariants (length bounds, trimming whitespace, path traversal prevention like `..`, `/`, `\`) are enforced once at construction. Invalid state cannot enter the domain.
3. **Polymorphic Interoperability & Ergonomics:**
   Value Objects provide ergonomic factory methods (`from_string()`), transparent equality comparison (`__eq__`) against raw primitives, canonical string conversion (`__str__`), and proper hashing (`__hash__`). This eliminates cognitive friction when passing Value Objects to standard logging or string formatting.

---

### Pillar 2: Especialização Funcional de Portas Hexagonais (Role-Based Port Segregation)

Hexagonal ports represent domain roles, NOT infrastructure technologies. In accordance with the Interface Segregation Principle (ISP):

1. **Segregation by Business Role:**
   Ports are named by the business intent they fulfill, never by technology alone. `LLMTransformationPort` is injected as `llm_synthesis_port` into synthesis use cases (Stages 2–6) and as `llm_indexing_port` into indexing use cases (Stage 1b).
2. **Decoupled Calibration:**
   Inference tunables are bound to specific business roles rather than global defaults. Configuration values (`llm_synthesis_temperature` vs. `llm_indexing_temperature`) remain segregated, preventing indexing parameter changes from degrading generative synthesis quality.

---

### Pillar 3: Uniformidade do Protocolo de Casos de Uso (Universal Command Invocation Protocol)

To eliminate cognitive load and enable generic middleware, decorators, and CLI dispatchers:

1. **Single Canonical Entrypoint (`execute`):**
   Every Use Case class in the application layer exposes a single, strongly-typed orchestrator method: `.execute(...)`.
2. **Elimination of Naming Drift:**
   Verbs qualifying the target entity (e.g., `execute_for_channel`, `index_single_transcript`) are prohibited as primary entrypoints. Where backwards compatibility is required during migrations, legacy methods are preserved strictly as thin pass-through delegates.
3. **Cognitive Load Reduction:**
   Presentation layers (CLI commands, API controllers, composition roots) invoke all business workflows through the same uniform protocol.

---

### Pillar 4: Integridade Contratual vs. Defensividade Vestigial (Contract Integrity over Runtime Paranoia)

Type safety and Abstract Base Classes (ABCs) represent binding contracts. Runtime defensiveness that second-guesses contracts is an anti-pattern.

1. **Lifecycle Guaranteed in Contract:**
   If an architectural port contract (such as `LLMTransformationPort`) defines a lifecycle hook (e.g., `warmup(timeout_seconds: float | None = None) -> None`), that method is guaranteed to exist by definition of the contract.
2. **Direct Polymorphic Invocation:**
   Code MUST NOT wrap contract calls in defensive runtime checks such as `if hasattr(port, "warmup"):`. Such guards violate the Liskov Substitution Principle (LSP) by treating typed dependencies as untyped dictionaries. Invocations must be direct, fail-fast, and trusted.

---

### Pillar 5: Observabilidade e Topologia Concorrente de Dia Zero (Thread Hierarchy & APM Visibility)

Anonymous concurrency is strictly forbidden. Operating systems, APMs (Pyroscope, Datadog, OpenTelemetry), and SRE engineers must be able to identify the exact origin and responsibility of every running thread from an OS process dump (`top -H`, `htop`, `/proc/{pid}/task`).

1. **Canonical Thread Prefixation:**
   All `ThreadPoolExecutor` instances MUST specify an explicit, business-aligned `thread_name_prefix`. Anonymous executors generating default names (e.g., `ThreadPoolExecutor-0_1`) are prohibited.
2. **Deterministic Thread Hierarchy:**
   The Cresmo concurrency tree is formalized as follows:

```
[PID] MainThread (Pipeline Consumer & Presentation Runtime)
  |
  +---> [Thread] CresmoCrawlerProducer (Daemon Background Crawler)
  |       |
  |       +---> [ThreadPool] CresmoChannelResolver_0..N (Parallel yt-dlp Video-to-Channel Resolver)
  |       |
  |       +---> [ThreadPool] CresmoFeedProber_0..N (Parallel YouTube Feed & Uploads Prober)
  |
  +---> [Thread] OllamaWarmupThread-{model} (Asynchronous Model Weight Preloader)
  |
  +---> [ThreadPool] TestSqliteLedgerWorker_0..N (Test Harness Concurrency Probes)
```

3. **Production SRE & Profiling Value:**
   During thread contention or CPU saturation, profilers immediately attribute resource consumption to the precise sub-component (e.g., distinguishing network wait in `CresmoFeedProber` from CPU utilization in `MainThread`).

---

### Pillar 6: Coordenação Assíncrona Segura e Prevenção de TOCTOU (Anti-TOCTOU & State Isolation)

In multi-threaded streaming architectures (such as `DiscoverBatchSourcesUseCase`), mutable callback references and shared state must be protected against Time-of-Check to Time-of-Use (TOCTOU) race conditions.

1. **Local Snapshot Pattern:**
   When invoking mutable callback hooks (e.g., `self.on_source_added`), the reference must be captured in a thread-local variable before null-checking and execution:
   ```python
   # Anti-TOCTOU: Local snapshot prevents NoneType invocation if another thread clears callback
   cb = self.on_source_added
   if cb is not None:
       cb(src)
   ```
2. **Overlapped Producer-Consumer Streaming:**
   The producer crawler runs concurrently with the consumer pipeline. Shared mutable state (e.g., `_BatchSourceAccumulator._sources` and deduplication sets) is protected by reentrant mutex locks (`threading.Lock`), ensuring thread safety without deadlocks.
3. **Fast-Path Priority Ejection:**
   High-priority local texts and manifest items are collected and yielded at $t=0$ before the background crawler is spawned, eliminating startup starvation.

---

### Pillar 7: Anti-Corruption Layer (ACL) na Fronteira de Persistência (Driver Impedance Mismatch Shield)

Database drivers and underlying operating system APIs possess primitive constraints (e.g., `sqlite3.ProgrammingError: Error binding parameter: type 'ChannelName' is not supported`).

1. **Strict Adapter Responsibility:**
   The impedance mismatch between domain-rich Value Objects and primitive database drivers MUST be resolved exclusively within the infrastructure adapter.
2. **Domain Purity Preservation:**
   Under NO circumstances should domain models revert to primitives (`str`) or inherit from persistence frameworks to satisfy a database driver.
3. **Boundary Translation Protocol:**
   - **Outbound (Persistence):** The adapter explicitly translates domain Value Objects to driver-compatible primitives (e.g., `str(entry.channel_name)` in `SqliteLedgerAdapter.save_entry`).
   - **Inbound (Hydration):** The adapter reconstructs validated domain Value Objects from raw database rows (e.g., `ChannelName(str(row["channel_name"]))`).

---

## 3. Compliance Matrix & Verification

Every module and pull request must satisfy the verification gates defined by these seven pillars:

| Pillar | Gate / Tool | Verification Requirement |
|---|---|---|
| **P1: Zero Primitive Obsession** | Pytest / Mypy | Domain entities reject raw unvalidated strings; Value Objects are immutable. |
| **P2: Role-Based Port Segregation** | Architecture Review | Port parameters and attributes carry business intent suffixes (`llm_synthesis_port`, `llm_indexing_port`). |
| **P3: Universal Invocation** | Contract Tests | Use case orchestrators expose `.execute(...)` as their primary invocation. |
| **P4: Contract Integrity** | Ruff / Linter | Zero `hasattr` calls on ABC-defined interfaces; direct fail-fast polymorphic calls. |
| **P5: Thread Topology** | Code Inspection | Zero `ThreadPoolExecutor` without `thread_name_prefix`; all standalone threads explicitly named. |
| **P6: Anti-TOCTOU** | Concurrency Tests | Local snapshot pattern on all dynamic callbacks; reentrant lock protection on accumulators. |
| **P7: Persistence ACL Shield** | Integration Tests | SQLite, filesystem, and external adapters serialize/deserialize Value Objects cleanly with zero driver leakage. |

---

## 4. Consequences & Impact

### Positive
- **Architectural Cohesion:** Unifies nomenclature, concurrency, persistence, and domain modeling into a single, unambiguous engineering standard.
- **Flawless Observability:** Every thread, metric, and log line reflects business domain topology rather than generic runtime artifacts.
- **Fail-Fast Reliability:** Domain invariants, typing contracts, and persistence boundaries reject illegal state at inception rather than silently propagating errors.
- **Developer Experience (DX):** Predictable use case APIs (`.execute()`) and ergonomic Value Objects accelerate testing, debugging, and feature extension.

### Negative / Trade-Offs
- Requires discipline during code review to prevent developers from instantiating unnamed `ThreadPoolExecutor` instances or bypassing Value Objects with raw strings.
