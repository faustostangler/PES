# ADR-042: Modern Typer Presentation CLI Driving Adapter

**Status:** ACCEPTED (SUPERSEDES [`ADR-002`](ADR-002-cresmo-presentation-cli.md))  
**Date:** 2026-10-13  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md), [`CONTEXT.md`](../../CONTEXT.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-002`](ADR-002-cresmo-presentation-cli.md) *(Superseded in part: presentation framework)*, [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-012`](ADR-012-multi-criteria-sync-filtering-and-alphabetical-feed-ordering.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-023`](ADR-023-prometheus-sre-golden-signals-and-dora-metrics-platform.md), [`ADR-025`](ADR-025-grafana-loki-structured-log-aggregation.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md)

---

## 1. Context & Architectural Motivation

In ADR-002, Cresmo adopted Python's standard library `argparse` to eliminate external dependencies while establishing the Humble Object CLI pattern. Over time, as Cresmo evolved into an enterprise-grade AI knowledge synthesis modular monolith with 8 distinct operational subcommands (`run`, `check-config`, `sync`, `worker`, `dedupe`, `export-cookies`, `concat-master`, `seed-prompts`), several architectural limitations of `argparse` surfaced:

1. **Primitive Obsession & Untyped Namespaces (`argparse.Namespace`):**
   Command handlers receive untyped `args: argparse.Namespace` objects, requiring manual `getattr()`, explicit type casts, and dynamic attribute probing. This violates the core Doctor Stangler canon against Primitive Obsession and hampers static type analysis (`mypy --strict`).
2. **Scattered Validation & Delayed Fail-Fast:**
   Boundary validations (e.g. integer bounds on `--passes`, directory checks, choice validations) had to be hand-coded inside parser helpers or deferred to domain models, instead of failing fast at the presentation boundary.
3. **Implicit Argument Routing Anti-Pattern:**
   `cli.py` contained dynamic heuristic fallback logic that rewrote `sys.argv` to default to `run` if an unrecognized token was passed, introducing non-deterministic CLI dispatch in containerized workflows.
4. **Poor Developer Experience (DX) & Terminal Ergonomics:**
   Standard `argparse` outputs plain, uncolored terminal text with limited formatting, lacking modern Rich-based visual hierarchy, autocompletion hooks, and clean exception-to-exit translations.
5. **Testing Friction:**
   Testing `argparse` CLI entrypoints required monkey-patching `sys.argv`, capturing stdout/stderr via fragile fixtures, and handling raw `SystemExit` catches, rather than using an isolated, memory-efficient test runner.

---

## 2. Decision

We replace `argparse` entirely with **Typer** (backed by **Click** and **Rich**), establishing `TyperCliDrivingAdapter` as the primary Hexagonal Driving Adapter in `src/cresmo/presentation/`. 

In accordance with the Lead Architect's directive (*"SOTA KISS, pure DDD, zero backward-compatibility shims"*), we perform a clean, non-compromised migration across the 13 reference domains:

### 2.1 Pure Hexagonal Driving Adapter (`src/cresmo/presentation/cli.py`)
- Instantiate a single root `app = typer.Typer(name="cresmo", help="Cresmo Knowledge Synthesis CLI", no_args_is_help=True, add_completion=True)`.
- Register each subcommand cleanly via `app.add_typer(...)` or `@app.command()`.
- Update `pyproject.toml` console script entrypoint directly to `cresmo = "cresmo.presentation.cli:app"`.
- Eliminate legacy implicit `argv` rewriting; missing or invalid subcommands display the root Typer help menu and exit with code `2`.

### 2.2 Strongly-Typed Command Signatures (`src/cresmo/presentation/commands/`)
- Every subcommand function signature declares explicit types using `typing.Annotated[..., typer.Option(...)]` or `typer.Argument(...)`.
- Parameter boundaries are enforced declaratively at the CLI layer (e.g. `Annotated[int, typer.Option(min=1, max=10)]` for `--passes`, `min=1` for `--max-videos`).
- File and directory arguments enforce existence and path resolution via `Annotated[Path, typer.Option(exists=True, resolve_path=True)]`.
- String inputs representing domain primitives are immediately converted into self-validating Value Objects (`ContentId`, `ChannelName`, `SyncFilterCriteria`, `BatchDiscoveryQuery`) before invoking application use cases.

### 2.3 Exception-to-Exit Translation & Exit Code Taxonomy
- Retain the canonical exit code taxonomy from `src/cresmo/presentation/exit_codes.py` (`0` Success, `1` Internal, `2` Usage/Config, `3` Domain Invariant, `4` Rate Limit, `5` Ingestion).
- Implement a centralized presentation error wrapper / handler that formats domain exceptions with `rich.console.Console(stderr=True).print(...)` and raises `typer.Exit(code=EXIT_*)`.
- Ensure deterministic resource release (`finally:` blocks in `composition.py`) runs prior to `typer.Exit()`.

### 2.4 12-Factor Process Security & Zero Secret Leakage
- Passwords, API tokens (`GEMINI_API_KEY`), and sensitive credentials must never be accepted as CLI options or positional arguments.
- Credentials are loaded exclusively via Pydantic `CresmoSettings` from environment variables and `.env`.
- CLI commands only accept filesystem paths to secure credential/cookie files with strict permission checks.

### 2.5 SRE Observability & Telemetry Flush
- Add global `--verbose / -v` flag on the Typer root / subcommands to control logging verbosity.
- Emit structured logs compatible with Grafana Loki and OpenTelemetry / Langfuse trace correlation.
- The composition root flushes pending Langfuse spans and Prometheus metrics before raising `typer.Exit()`.

### 2.6 Hermetic Testing with `typer.testing.CliRunner`
- Migrate unit and integration tests to use `CliRunner(mix_stderr=False)`.
- Tests assert exact exit codes, stdout summaries, and stderr diagnostics in memory without side effects or `sys.argv` pollution.

---

## 3. Causal Chain & Consequences

```
POSIX Terminal Execution
          │
          ▼
   Typer Root App (src/cresmo/presentation/cli.py)
          │  (Validates CLI options, paths, bounds fail-fast)
          ▼
Subcommand Driving Handler (src/cresmo/presentation/commands/*.py)
          │  (Converts primitives to Value Objects: ChannelName, ContentId)
          ▼
   Composition Root (src/cresmo/presentation/composition.py)
          │  (Wires Ports & Adapters, registers cleanup hooks)
          ▼
 Application Use Case (e.g. CresmoPipeline, SyncChannelUseCase)
          │
          ├── Success ──► Rich formatted summary ──► typer.Exit(code=0)
          └── Domain Error ──► Red stderr print ──► typer.Exit(code=EXIT_*)
```

### Positive Consequences
- **Type Safety & DX:** Full static type validation across CLI arguments with autocomplete and Rich visual terminal rendering.
- **Fail-Fast Boundary:** Invalid options, out-of-range bounds, and missing files fail immediately at the presentation gate before triggering expensive use case wiring.
- **Zero Primitive Obsession:** Eliminates `argparse.Namespace` in favor of typed arguments and immediate domain Value Object binding.
- **Pure Hexagonal Design:** Inner application layers remain completely unaware of Typer or Click.
- **Test Ergonomics:** Blazingly fast, deterministic unit testing via `CliRunner`.

### Negative Consequences
- **External Dependency:** Adds `typer>=0.12.0` (which pulls `click` and `rich`) to `pyproject.toml`.
- **Refactoring Scope:** All 8 subcommand modules and their corresponding test suites must be updated to the Typer paradigm.
