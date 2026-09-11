# ADR-002: Cresmo Production CLI Entrypoint and Presentation Layer Orchestration

**Status:** APPROVED  
**Date:** 2026-09-10  
**Decision Makers:** Lead Architect (Fausto Stangler), Stereoscopist (Doctor Stangler Committee)  

---

## 1. Context

Following the completion and verification of [`ADR-001: Strangling Cresmo into Hexagonal Modular Monolith`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/docs/adr/ADR-001-cresmo-modular-monolith-strangling.md), the core knowledge synthesis engine resides cleanly in `src/cresmo/` (`domain/`, `application/`, `infrastructure/`). The engine orchestrates the 6 incremental synthesis stages with pure descriptive naming, 100% domain branch coverage, and frozen Langfuse Eval verification.

However, the modular monolith currently lacks an official **Presentation Layer** for operational consumption:
1. **Absence of a Production CLI**: Operators and automated pipelines must instantiate `CresmoPipeline` programmatically in Python code. The legacy CLI ([`playground/cresmo/cresmo_pipeline.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/playground/cresmo/cresmo_pipeline.py)) mixed argument parsing, `sys.path` monkey-patching, procedural file writes, and LLM calls inside a monolithic 2,017-line file.
2. **Missing Composition Root**: Production adapters (`LegacyIsbIngestionAdapter`, `GeminiLLMAdapter`, `ObsidianVaultAdapter`) need a centralized, deterministic wiring mechanism driven by [`CresmoSettings`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/infrastructure/config.py).
3. **Persistent Idempotency Ledger**: While [`LedgerRepositoryPort`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/application/ports.py) defines the contract for idempotency tracking, only `InMemoryLedgerAdapter` is currently implemented in `src/cresmo/infrastructure/adapters/mock_adapters.py`. Production execution requires a persistent, atomic `JsonLedgerAdapter` compatible with `processed_cresmo.json`.
4. **Standardized Process Control**: Production orchestration (cron jobs, shell runners, CI/CD) requires strict, well-defined CLI exit codes separating configuration errors, domain invariant rejections, API rate limits, and ingestion failures.

Ubiquitous Language definitions are documented in [`CONTEXT.md`](../../CONTEXT.md) and [`docs/GLOSSARY.md`](../GLOSSARY.md).

---

## 2. Decision

We will implement the Presentation Layer in `src/cresmo/presentation/` adhering to the **Humble Object Pattern**, driven by standard library `argparse` and supported by an atomic `JsonLedgerAdapter` in `src/cresmo/infrastructure/adapters/`:

1. **Humble Object CLI Controller (`src/cresmo/presentation/cli.py`)**:
   - Strips all business logic and orchestration from the presentation layer.
   - Implements subcommands:
     - `cresmo run --url <video_url>`: Executes the end-to-end synthesis pipeline for a single target video.
     - `cresmo check-config`: Validates environment settings (`.env`), API keys, and vault paths fail-fast without executing transformations.
   - Accepts operational overrides via CLI flags (`--batch-size`, `--passes`, `--dry-run`).
   - Uses Python's built-in `argparse` to eliminate extra external framework dependencies.

2. **Centralized Composition Root (`src/cresmo/presentation/composition.py`)**:
   - Acts as the pure Dependency Injection assembly root.
   - Reads validated configuration from `CresmoSettings()`.
   - Instantiates production adapters:
     - `LegacyIsbIngestionAdapter` as `MediaIngestionPort`.
     - `GeminiLLMAdapter` as `LLMTransformationPort`.
     - `ObsidianVaultAdapter` as `VaultRepositoryPort`.
     - `JsonLedgerAdapter` as `LedgerRepositoryPort`.
   - Injects dependencies into `CresmoPipeline` and returns the ready-to-execute orchestrator.

3. **Atomic File-Based Ledger Adapter (`src/cresmo/infrastructure/adapters/json_ledger_adapter.py`)**:
   - Implements `LedgerRepositoryPort`.
   - Persists completed `ContentId`s in `processed_cresmo.json` (or path configured in `CresmoSettings`).
   - Enforces atomic writes via `{target}.tmp.{uuid4()}` and `os.replace` to prevent file corruption during sudden crashes or SIGINT.

4. **Standardized CLI Exit Code Taxonomy**:
   - `0`: **Success** — Pipeline finished cleanly, notes and MOCs created or video already marked processed.
   - `1`: **Unexpected Internal Error** — Unhandled exception.
   - `2`: **Configuration / CLI Usage Error** — Missing mandatory arguments, invalid flags, or `pydantic.ValidationError` in `CresmoSettings`.
   - `3`: **Domain Invariant / Validation Error** — `DomainValidationError`, `CompendiumStructureError`, `TypologyViolationError`.
   - `4`: **Rate Limit / Quota Exceeded** — `RateLimitExceededError` (HTTP 429 from YouTube or Google Gemini API exhausted).
   - `5`: **Ingestion / Network Error** — `IngestionNetworkError` (download or Whisper transcription failure).

5. **Packaging Entrypoint (`pyproject.toml`)**:
   - Register the console script:
     ```toml
     [project.scripts]
     cresmo = "cresmo.presentation.cli:main"
     ```
   - Enables execution via `uv run cresmo run --url <url>` or direct binary execution when packaged.

---

## 3. Consequences

### Positive
- **Architectural Cohesion**: Hexagonal separation remains intact; the CLI is a humble translator with zero domain logic.
- **Fail-Fast Ergonomics**: Operators can run `cresmo check-config` to verify setup before initiating expensive LLM jobs.
- **Zero New Dependencies**: `argparse` is standard library; avoids adding `click` or `typer` to `pyproject.toml`.
- **Atomic Idempotency**: `JsonLedgerAdapter` guarantees no duplicate processing and cannot corrupt the ledger file on failure.
- **Deterministic Observability**: Exit codes enable unambiguous automation in cron scripts and container orchestration.

### Negative
- `argparse` requires slightly more boilerplate code than decorator-based libraries like `typer`.
- Terminal color formatting is restricted to ANSI escapes or standard stdout to avoid heavy UI dependencies.

### Neutral
- Existing unit tests for `src/cresmo/` remain completely untouched and valid.

---

## 4. Alternatives Considered

### Alternative A: Using `click` or `typer`
- **Pros**: Automatic help generation, type hints for arguments, shell auto-completion.
- **Cons**: Requires adding new dependencies (`click` or `typer`) to `pyproject.toml`, increasing lockfile surface.
- **Why rejected**: Standard library `argparse` fulfills 100% of our Humble Object requirements without bloating the project dependencies.

### Alternative B: Root-level procedural script (`run_cresmo.py`)
- **Pros**: Quick to write in 20 lines.
- **Cons**: Bypasses the presentation layer, encourages mixing environment variables and script logic, and breaks the Modular Monolith standard project layout.
- **Why rejected**: Violates the Clean Architecture Humble Object presentation pattern and recreates the technical debt of `playground/cresmo`.

---

## 5. Domain Model Impact

- **Domain Core (`src/cresmo/domain/`)**: **Zero changes**. Sacred, framework-free, and isolated.
- **Application Layer (`src/cresmo/application/`)**: **Zero changes**. `CresmoPipeline` and all use cases remain identical.
- **Infrastructure Layer (`src/cresmo/infrastructure/`)**:
  - Add `src/cresmo/infrastructure/adapters/json_ledger_adapter.py` implementing `LedgerRepositoryPort`.
  - Add `ledger_path: Path` to `CresmoSettings` in `config.py` with default `processed_cresmo.json`.
- **Presentation Layer (`src/cresmo/presentation/`)**:
  - Add `src/cresmo/presentation/__init__.py`.
  - Add `src/cresmo/presentation/composition.py` (Composition Root).
  - Add `src/cresmo/presentation/cli.py` (Humble Object CLI).

---

## 6. Compliance Checklist

- [x] Hexagonal Architecture layers respected (`presentation/` -> `application/` -> `domain/` <- `infrastructure/`)
- [x] Zero business logic in Presentation layer (Humble Object Pattern)
- [x] No framework dependencies added to Domain or Application layers
- [x] Test strategy defined (hermetic unit tests for CLI argument parsing and composition root with mock ports)
- [x] Fail-fast configuration validation via Pydantic Settings V2
- [x] Exit codes standardized and deterministic
- [x] Idempotency persisted atomically

---

## 7. References

- Predecessor ADR: [`docs/adr/ADR-001-cresmo-modular-monolith-strangling.md`](ADR-001-cresmo-modular-monolith-strangling.md)
- Context & Ubiquitous Language: [`CONTEXT.md`](../../CONTEXT.md)
- Ubiquitous Language Glossary: [`docs/GLOSSARY.md`](../GLOSSARY.md)
- Method Specification: [`.agents/skills/stangler-doctor/SKILL.md`](../../.agents/skills/stangler-doctor/SKILL.md)
