# ADR-003: PES Production Architecture — Consolidated 13-Chapter Synthesis

**Status:** APPROVED  
**Date:** 2026-09-11  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context

Following the initial strangling of legacy scripts into a clean domain core ([`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md)) and the CLI presentation baseline ([`ADR-002`](ADR-002-cresmo-presentation-cli.md)), the complete technical landscape was systematically grilled through all 13 reference chapters of the Doctor Stangler method.

This ADR consolidates the hard technical trade-offs and structural invariants agreed upon to guarantee enterprise reliability, sub-zero change failure rate, and sovereign operational scalability.

---

## 2. Architecture Decisions by Dimension

### 2.1 Computing & Storage (Chapters 01 & 04)
- **ACID WAL Ledger:** Replaced plain JSON storage with `SqliteLedgerAdapter` utilizing `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` to enable concurrent multi-process access without lock contention.
- **Dynamic Resource Budgeting:** `ComputeBudgetPolicy` dynamically throttles worker concurrency based on real-time CPU cores and available GPU VRAM.
- **Ephemeral Media Hygiene:** `ScratchStorageService` manages temporary downloads/audio files on dedicated storage mounts using RAII context managers and POSIX signal handlers (`SIGINT`/`SIGTERM`).
- **Resilient Transport:** `ResilientTransportPolicy` governs pooled HTTP keep-alive, granular TCP socket timeouts (`connect=10s`, `read=60s`), and exponential jittered retries via `tenacity`.
- **SSOT Containerization:** Single multi-stage Debian-slim container (`MultiRoleContainer`) dispatching `api`, `worker`, and `cli` roles via non-root `EntrypointDispatcher` supervised by `tini` as PID 1, with segregated volumes (`VolumeTopology`) and cgroups v2 resource limits.

### 2.2 Domain & Application Layer (Chapters 02, 03 & 09)
- **Hexagonal Port Decoupling:** `MediaIngestionPort`, `LLMTransformationPort`, `VaultRepositoryPort`, `LedgerRepositoryPort`, and `PromptRepositoryPort`.
- **Typed Error Hierarchy:** Complete segregation between pure domain rule violations (`CresmoDomainError`) and external infrastructure failures (`CresmoInfrastructureError`).
- **Channel Batch Synchronization:** `SyncChannelUseCase` coordinates channel feed polling, lookback filtering, and prioritized dispatching via `BatchQueueOrchestrator` (`HIGH` vs. `STANDARD` priority queues).
- **Fail-Fast Environmental Invariants:** `PreflightHealthChecker` verifies credentials, storage permissions, and binary dependencies (`ffmpeg`) in <10ms before executing I/O.
- **Stage Checkpointing:** `StageCheckpointPolicy` skips re-invoking LLM inference when intermediate artifacts (`raw`, `enriched`) already exist in the Vault, enabling instant crash recovery unless overridden by `--force-refresh`.
- **Deterministic Cognitive Pipeline:** AI reasoning is organized as an explicit, typed state machine across application use cases (`FillGapsFluidProseUseCase` $\rightarrow$ `DiscoverAtomicInventoryUseCase` $\rightarrow$ `SynthesizeAtomicBatchUseCase` $\rightarrow$ `ReconcileMocUseCase`), replacing non-deterministic autonomous agent loops.
- **Sectional Context Slicing:** During batch synthesis of $\le 5$ notes, prompts are injected only with global thesis metadata, specific thematic chapters where the concepts reside, and the inventory title manifest, reducing input prompt tokens by 80–90%.

### 2.3 Deep Learning & AI Architecture (Chapters 05, 06 & 07)
- **Two-Phase Atomic Synthesis:** Decouples the extraction of 100–150+ atomic notes per video into a global holistic inventory indexing pass (`DiscoverAtomicInventoryUseCase`) followed by chunked, schema-constrained retrieval batches of $\le 5$ notes per LLM call (`SynthesizeAtomicBatchUseCase`).
- **Three-Layer Safety Guardrails:** Structural isolation via XML tags (`<untrusted_source_transcript>`), negative prompt constraints, and asynchronous/sampled Langfuse LLM-as-a-judge quality evaluations (EVAL-001).
- **Speech-to-Text Engine:** `FasterWhisperEngine` via CTranslate2 C++ engine with INT8/FP16 quantization and integrated Silero VAD (`VoiceActivityFilter`) to eliminate silence hallucination loops and accelerate local transcription up to $4\times$.
- **Hierarchical Thematic Enrichment:** Three-pass long-form transcript processing (`ThematicOutline` $\rightarrow$ Sectional Deep Expansion $\rightarrow$ Compendium Stitching) to overcome the 8,192 output token limit.
- **Pluggable Multi-Provider Architecture:** `LLMAdapterFactory` in Composition Root supporting `GeminiLLMAdapter` as cloud primary and `OllamaLLMAdapter` as local-first offline fallback.
- **Dual Prompt Repository:** `PromptRepositoryPort` with `LangfusePromptAdapter` (remote versioning with TTL caching) and `LocalFilesystemPromptAdapter` (version-controlled Markdown fallback).

### 2.4 MLOps, CI/CD & Automation (Chapters 08 & 10)
- **Hexagonal Telemetry Interceptor:** `TracingLLMTransformationDecorator` intercepts inference calls and publishes traces to Langfuse using `TraceContext` propagated via `contextvars`, with fail-silent resilience.
- **Three-Tier Evaluation Strategy:** Inline deterministic validation (zero cost) + sampled asynchronous LLM-as-a-judge in production + CI/CD regression test gate against a curated `GoldenDataset` in Langfuse.
- **In-Process Ingestion Automation:** `ChannelPollingDaemon` running an async event loop in the worker role with atomic `HeartbeatHealthCheck` and adaptive backoff, accompanied by transparent one-shot CLI execution.
- **Parallel Multi-Stage CI Pipeline:** GitHub Actions workflow with fast feedback (<20s) for `ruff` and `mypy --strict`, mirrored TDD test gates with $\ge 85\%$ coverage, and conditional deep quality gates (`mutmut` mutation testing and Trivy OCI container scans).

### 2.5 Security, Observability & FinOps (Chapters 11, 12 & 13)
- **Secret Governance Policy:** All credentials encapsulated in `pydantic.SecretStr`, supporting Docker secrets and environment variables with zero plaintext leakage in logs or inspect metadata.
- **Rootless Container Hardening:** Container executes as `appuser:10001`, `read_only: true` root filesystem, `cap_drop: [ALL]`, and `no-new-privileges: true`.
- **Vault Sandbox Isolation:** `ObsidianVaultAdapter` resolves canonical absolute paths (`Path.resolve()`) and strictly enforces `path.is_relative_to(vault_root.resolve())` before file writes, preventing path traversal attacks.
- **Prometheus Golden Signals & Domain Metrics:** SRE metrics (latency histograms, traffic counters, error rates, saturation gauges) segregated from Ubiquitous Language domain business metrics (note creation throughput by typology, EVAL-001 quality scores, audio acceleration ratio).
- **Structured JSON Logging & Trace Correlation:** 12-Factor App JSON logs on `stdout` binding `trace_id` (`cresmo-{content_id}`) across Loki, Prometheus exemplars, Langfuse traces, and Sentry incident breadcrumbs.
- **Hardware Acceleration Policy:** Startup auto-discovery of GPU/CUDA and free VRAM with graceful degradation to multi-core CPU with INT8 quantization.
- **Inference Cost Governance Policy:** Predictive pre-execution token/cost estimation in the CLI, configurable spending ceiling (`MAX_RUN_BUDGET_USD`) with clean transaction completion and paused state in SQLite, and cognitive model tiering (`gemini-2.5-flash`/Ollama for inventory/batches vs. `gemini-2.5-pro` for compendiums/MOCs).

---

## 3. Consequences & Impact

### Positive
1. **Zero Hallucination & Token Safety:** Two-phase synthesis and sectional context slicing ensure reliable generation of 100–150+ notes per lecture without context window exhaustion.
2. **Crash Resilience & Idempotency:** SQLite WAL ledger and stage checkpoints allow instant resumption after power loss or network failure.
3. **True Sovereign Portability:** Runs seamlessly on developer GPUs, headless cloud servers, and CPU CI/CD runners with zero code modifications.
4. **Comprehensive Observability:** Correlated metrics, logs, traces, and evals provide immediate root-cause diagnosis.

### Negative / Trade-offs
1. Requires disciplined adherence to ports and adapters in the Composition Root.
2. Initial setup of local SQLite WAL and Docker volume permissions requires explicit host directory alignment.
