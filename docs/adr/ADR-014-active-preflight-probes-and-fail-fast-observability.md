# ADR-014: Active Preflight Probes and Fail-Fast Observability Architecture

**Status:** ACCEPTED  
**Date:** 2026-09-19  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, 12-Factor App)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-002`](ADR-002-cresmo-presentation-cli.md), [`ADR-003`](ADR-003-pes-production-architecture.md), [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md)  

---

## 1. Context & Architectural Problem Statement

In Cresmo's Hexagonal Modular Monolith, execution pipelines (`cresmo run`, `cresmo index-raw`) interact with attached backing services:
1. **Langfuse Server (`cresmo-langfuse-server`):** Self-hosted OpenTelemetry collector and LLM observability backend running via Docker Compose on `http://localhost:3000`.
2. **Ollama Daemon:** Local REST API server running on `http://localhost:11434` providing offline, zero-cost LLM inference.
3. **Local Storage & System Binaries:** Obsidian Second Brain vault, SQLite WAL ledger, and system tools (`ffmpeg`).

During local execution and development cycles, developer workstations experience machine restarts, container cold-starts, or background service restarts. If the Langfuse server container is stopped or still starting up when a CLI command is issued, the following operational breakdown occurs:

- **OpenTelemetry Background Retry Storm:**
  The Python `Langfuse` SDK constructor does not synchronously probe network connectivity upon instantiation. Instead, it initializes in-memory span buffers and immediately launches daemon background worker threads that loop attempting to export trace batches to `{host}/api/public/otel/v1/traces`.
- When `localhost:3000` is offline (e.g. `[Errno 111] Connection refused`), these background threads continuously emit unhandled retry warnings directly to `stderr`:
  ```text
  Transient error HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /api/public/otel/v1/traces (Caused by NewConnectionError("HTTPConnection(host='localhost', port=3000): Failed to establish a new connection: [Errno 111] Connection refused")) encountered while exporting span batch, retrying in 1.03s.
  ```
- This pollutes the CLI stream, obscures business progress logs, and confuses operators.
- Furthermore, CLI entry points previously lacked active preflight checks, allowing pipelines to proceed partially before failing unexpectedly during deep execution phases.

---

## 2. Alternatives Considered

1. **Auto-spawning Docker Containers from Python Code:**
   *Rejected.* Having application code call `subprocess.run(["docker", "compose", "up", ...])` directly violates Hexagonal separation of concerns, couples application code to the host Docker daemon socket, and breaks 12-Factor containerized execution (Factor IV: Backing services as attached resources).
2. **Passive Try/Except Wrapping around SDK Instantiation:**
   *Rejected.* As demonstrated by production telemetry analysis, the `Langfuse` constructor succeeds even when the server is dead; errors occur asynchronously in detached background threads beyond standard application `try/except` scope.
3. **Active Preflight Probe with Graceful Fallback & Actionable Guidance:**
   *Selected.* Implement a sub-second, non-blocking synchronous HTTP probe against the service health endpoint before client instantiation. If unreachable, gracefully bypass telemetry, purge environment variables, and output an actionable single-line remediation command.

---

## 3. Decision

We establish the **Active Preflight Probe** pattern across the Cresmo application and presentation layers:

### 3.1 Active Preflight Probe Invariant
Every external or containerized network backing service must be actively probed with a deterministic, fast timeout (default: $\le 1.0$ second) before instantiating client SDKs or spawning background worker threads.

### 3.2 Dual Classification of Backing Services
1. **Auxiliary Services (Observability / Telemetry — Langfuse):**
   - Health endpoint: `{langfuse_host}/api/public/health`.
   - Behavior on Probe Failure:
     - **Do NOT** instantiate `Langfuse` client (`langfuse_client = None`).
     - Purge `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` from `os.environ` to prevent OpenTelemetry autoinstrumentation from attempting background connections.
     - Emit a single, clear, actionable warning to `sys.stderr`:
       ```text
       [preflight] Langfuse server at http://localhost:3000 is unreachable. Telemetry disabled.
       To enable observability: docker compose -f docker-compose.langfuse.yml up -d
       ```
     - Pipeline execution continues uninterrupted without logging noise.
2. **Critical Services (Local Inference — Ollama):**
   - Health endpoint: `{ollama_base_url}/api/version`.
   - Behavior on Probe Failure:
     - If local indexing (`OllamaLLMAdapter`) is requested and the daemon is down, fail-fast immediately before processing documents:
       ```text
       [preflight] Local Ollama daemon at http://localhost:11434 is unreachable.
       Run 'ollama serve' or pass '--web-index' to use cloud Gemini API.
       ```
     - Prevents wasting compute or failing mid-way through large transcript batches.

### 3.3 Enhanced Preflight Diagnostics
1. `PreflightResult` in `src/cresmo/application/services/preflight.py` is extended with a `warnings: tuple[str, ...]` attribute to report non-fatal diagnostic findings without halting execution.
2. `PreflightHealthChecker` provides specialized network probe methods (`check_langfuse_probe`, `check_ollama_probe`) using standard library `urllib.request` with zero third-party overhead.
3. `cresmo run` and `cresmo index-raw` CLI entry points invoke preflight diagnostics at startup.

---

## 4. Architectural Consequences

### Positive Consequences
- **Zero Console Pollution:** Eliminates asynchronous OpenTelemetry connection retry loops when the local Langfuse container is stopped.
- **SRE Self-Healing & DX:** Provides immediate, copy-pasteable remediation commands (`docker compose -f docker-compose.langfuse.yml up -d` or `ollama serve`).
- **Fail-Fast Safety:** Prevents partial batch failures by validating critical dependencies before executing expensive I/O or token-consuming tasks.
- **Strict Hexagonal Discipline:** Application code remains completely decoupled from Docker internals while maintaining active environmental awareness.

### Negative Consequences
- Introduces an initial network probe overhead of $\le 5$ milliseconds when services are online, or up to 1.0s timeout if an endpoint is completely unresponsive without dropping TCP packets.
