# SPEC-002: Cresmo Production CLI & Presentation Layer Specifications

**Linked ADR:** [`ADR-002: Cresmo Production CLI Entrypoint and Presentation Layer Orchestration`](../adr/ADR-002-cresmo-presentation-cli.md) & [`ADR-003: PES Production Architecture`](../adr/ADR-003-pes-production-architecture.md)  
**Status:** APPROVED  
**Date:** 2026-09-11  
**Bounded Context:** Cresmo Knowledge Synthesis — Presentation & Infrastructure Adapters  

---

## 1. Overview & Objectives

Derives the precision test specifications and frozen acceptance criteria from [`ADR-002`](../adr/ADR-002-cresmo-presentation-cli.md) and [`ADR-003`](../adr/ADR-003-pes-production-architecture.md). This specification covers:
1. The **Humble Object CLI** controller in `src/cresmo/presentation/cli.py` driven by `argparse` (`run`, `sync`, `check-config`, `worker`).
2. The **Composition Root** factory in `src/cresmo/presentation/composition.py` wiring `LLMAdapterFactory`, `PromptRepositoryPort`, and `PreflightHealthChecker`.
3. The **ACID SQLite WAL Ledger Adapter** in `src/cresmo/infrastructure/adapters/sqlite_ledger_adapter.py` (`SqliteLedgerAdapter`).
4. The **Process Exit Code Taxonomy** mapping CLI executions to deterministic shell exit codes.


---

## 2. Bounded Context & Architecture Invariants

- **Zero Business Logic in Presentation**: The CLI module must not perform transcript manipulation, LLM prompt formatting, or direct filesystem writes. All execution delegates strictly to `CresmoPipeline`.
- **Pure Dependency Injection**: Infrastructure adapters are wired exclusively in `composition.py`. Application use cases and domain entities never instantiate concrete adapters.
- **Fail-Fast Configuration**: Any missing required environment variable (`GEMINI_API_KEY`, invalid paths) must abort execution immediately with exit code `2` during CLI startup.
- **Atomic Persistence Guarantee**: `JsonLedgerAdapter` must never leave a half-written or corrupted JSON file on disk, even if interrupted by `SIGINT` or power failure.

---

## 3. Test Strategy Classification

| Level | Target Module | Scope & Verification | Mock Boundary |
|---|---|---|---|
| **Unit** | `src/cresmo/presentation/cli.py` | Argument parsing, flag overrides, help messages, stdout formatting, exception-to-exit-code mapping. | Mock `build_pipeline` and `CresmoPipeline`. |
| **Unit** | `src/cresmo/presentation/composition.py` | Factory wiring: validates that `build_pipeline` instantiates and injects all 4 ports into `CresmoPipeline`. | Mock concrete adapter constructors or verify interface conformance. |
| **Unit** | `src/cresmo/infrastructure/adapters/json_ledger_adapter.py` | Idempotency querying (`is_processed`), atomic updating (`mark_processed`), auto-creation of missing file/parent directories, handling corrupted JSON. | Real temporary filesystem directory (`tmp_path`). |
| **Integration** | `cresmo run` & `cresmo check-config` | End-to-end CLI execution via `main(argv=[...])`. | Hermetic test environment with mocked LLM/Ingestion. |

---

## 4. Acceptance Criteria & Scenarios (Given-When-Then)

### 4.1 CLI Argument Parsing & Execution

#### Scenario 1.1: `cresmo run --url <valid_url>` executes pipeline successfully
- **Given**: Valid environment configuration and a YouTube video URL.
- **When**: Operator runs `main(["run", "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ"])`.
- **Then**: `CresmoPipeline.run_for_video` is invoked with `video_url="https://youtube.com/watch?v=dQw4w9WgXcQ"`, and exit code `0` is returned.

#### Scenario 1.2: `cresmo run` accepts operational flag overrides
- **Given**: Operator provides `--passes 2` and `--batch-size 8`.
- **When**: Operator runs `main(["run", "--url", "...", "--passes", "2", "--batch-size", "8"])`.
- **Then**: `CresmoPipeline` is initialized with `batch_size=8`, and `run_for_video` receives `gap_filler_passes=2`.

#### Scenario 1.3: `cresmo run --dry-run` performs ingestion without LLM calls
- **Given**: Valid video URL with `--dry-run` flag.
- **When**: Operator runs `main(["run", "--url", "...", "--dry-run"])`.
- **Then**: CLI invokes only the ingestion use case, prints metadata to stdout, and exits with code `0`.

#### Scenario 1.4: `cresmo check-config` validates environment fail-fast
- **Given**: A configured `.env` file with valid `GEMINI_API_KEY` and accessible vault directory.
- **When**: Operator runs `main(["check-config"])`.
- **Then**: CLI prints configuration summary (vault root, active model variant, batch size) and exits with code `0` without making any API calls.

#### Scenario 1.5: `cresmo check-config` fails when required configuration is missing
- **Given**: Environment without `GEMINI_API_KEY`.
- **When**: Operator runs `main(["check-config"])`.
- **Then**: CLI outputs validation error details to stderr and exits with code `2`.

---

### 4.2 Standardized Process Exit Code Mapping

| Condition | Raised Exception / Trigger | Expected Exit Code | Expected Output Stream |
|---|---|---|---|
| Successful execution | `PipelineResult(success=True)` | `0` | `stdout: Success summary` |
| Idempotency skip | Content already in ledger | `0` | `stdout: Already processed` |
| Invalid flags / missing `--url` | `argparse.ArgumentError` / `SystemExit(2)` | `2` | `stderr: Usage help` |
| Missing env / invalid setting | `pydantic.ValidationError` | `2` | `stderr: Configuration error details` |
| Invalid domain entities/data | `DomainValidationError`, `CompendiumStructureError`, `TypologyViolationError` | `3` | `stderr: Domain validation failed: ...` |
| Upstream rate limit exceeded | `RateLimitExceededError` (HTTP 429) | `4` | `stderr: Rate limit exceeded: ...` |
| Ingestion network / Whisper failure | `IngestionNetworkError` | `5` | `stderr: Ingestion network error: ...` |
| Unhandled unexpected exception | `Exception` | `1` | `stderr: Unexpected error: ...` |

---

### 4.3 Atomic File-Based Ledger Adapter (`JsonLedgerAdapter`)

#### Scenario 3.1: Ledger initializes lazily if file does not exist
- **Given**: Target path `processed_cresmo.json` does not exist on disk.
- **When**: `is_processed(ContentId("dQw4w9WgXcQ"))` is called.
- **Then**: Returns `False` without error.

#### Scenario 3.2: Marking processed persists atomically
- **Given**: An empty or non-existent ledger file.
- **When**: `mark_processed(ContentId("dQw4w9WgXcQ"))` is called.
- **Then**: File is written atomically with JSON array `["dQw4w9WgXcQ"]`, and subsequent `is_processed(ContentId("dQw4w9WgXcQ"))` returns `True`.

#### Scenario 3.3: Idempotent addition prevents duplicates
- **Given**: Ledger already contains `["dQw4w9WgXcQ"]`.
- **When**: `mark_processed(ContentId("dQw4w9WgXcQ"))` is called again.
- **Then**: Ledger content remains `["dQw4w9WgXcQ"]` with no duplicate entries.

#### Scenario 3.4: Corrupted JSON recovery
- **Given**: Ledger file contains malformed non-JSON data.
- **When**: Adapter is initialized and read.
- **Then**: Raises `CresmoDomainError("Corrupted ledger file: ...")` or creates a timestamped backup before recovery.

---

### 4.4 Composition Root Factory (`build_pipeline`)

#### Scenario 4.1: Wires all 4 ports into `CresmoPipeline`
- **Given**: Valid `CresmoSettings`.
- **When**: `build_pipeline(settings)` is invoked.
- **Then**:
  - `pipeline.media_ingestion_port` is an instance of `LegacyIsbIngestionAdapter`.
  - `pipeline.llm_port` is an instance of `GeminiLLMAdapter`.
  - `pipeline.vault_port` is an instance of `ObsidianVaultAdapter`.
  - `pipeline.ledger_port` is an instance of `JsonLedgerAdapter`.

---

## 5. Console Script Registration

- In `pyproject.toml`:
  ```toml
  [project.scripts]
  cresmo = "cresmo.presentation.cli:main"
  ```
- Command invocation:
  ```bash
  uv run cresmo run --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
  uv run cresmo check-config
  ```

---

## 6. Verification Criteria

- [ ] All CLI test scenarios implemented in `tests/cresmo/unit/test_cli.py`.
- [ ] Ledger adapter tests implemented in `tests/cresmo/unit/test_json_ledger_adapter.py`.
- [ ] Composition root tests implemented in `tests/cresmo/unit/test_composition.py`.
- [ ] 0 regressions across existing 61 cresmo unit tests and 73 legacy playground tests.
- [ ] Static typing: `uvx pyright src/cresmo tests/cresmo` reports `0 errors, 0 warnings`.
- [ ] Linter: `uvx ruff check src/cresmo tests/cresmo` reports `All checks passed!`.
