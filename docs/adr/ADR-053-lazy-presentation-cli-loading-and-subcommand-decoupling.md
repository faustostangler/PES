# ADR-053: Lazy Presentation CLI Loading, Subcommand Decoupling, and Default-Fast Ingestion

## Status
ACCEPTED (Turn 3 — TDD Green + Refactor)

## Context
Running CLI subcommands or querying `--help` on the Cresmo CLI (`cresmo.presentation.cli`) experiences startup latency exceeding 60-70 seconds on developer environments, particularly on FUSE/NTFS storage volumes (`/dev/sda1` on `/mnt/gamer_d`).

Empirical runtime profiling (`python -X importtime`) reveals two primary latency bottlenecks:

### 1. Eager Module Cascading (Presentation Layer)
1. `src/cresmo/presentation/cli.py` statically imports all 8 subcommand handlers from `cresmo.presentation.commands`.
2. `src/cresmo/presentation/commands/__init__.py` unconditionally imports all subcommand modules (`run`, `sync`, `check_config`, `worker`, etc.).
3. Subcommand modules statically import `cresmo.presentation.composition` and adapter factories (`src/cresmo/presentation/factories/adapter_factory.py`).
4. Heavyweight external vendor frameworks are imported unconditionally at top level:
   - `NativeMediaIngestionAdapter` unconditionally imports `whisper` (which loads PyTorch/`torch`, C++ shared objects `libtorch*.so`, and model registries, incurring ~22s-45s alone).
   - `composition.py` unconditionally imports `langfuse` (~5.8s), `redis`, and `arq` (~5.5s).
5. Result: A user invoking a lightweight subcommand (e.g., `check-config`, `dedupe`, or `--help`) pays the latency and memory tax of the entire dependency graph (Whisper, PyTorch, Langfuse, Redis, Arq).

### 2. Slow Network Crawling Enabled by Default (Batch Discovery)
1. In `src/cresmo/presentation/commands/run.py` and `src/cresmo/infrastructure/config.py`, `enable_channel_crawler` defaults to `True`.
2. Running `cresmo run` without `--no-crawl` synchronously probes YouTube channel feeds over HTTP, causing significant network wait times before processing local seed items or raw transcripts.
3. Developers were forced to constantly pass `--no-crawl` (or define dedicated debug profiles in `.vscode/launch.json` like `"Cresmo: Run (Force Re-process, No Crawl)"`).

---

## Decision

### 1. Fast CLI ("CLI a Jato") & Lazy Subcommand Dispatching
- Refactor `src/cresmo/presentation/cli.py` to register Typer commands using lazy handler delegation. Subcommand modules are only imported upon command invocation.
- In `src/cresmo/presentation/commands/__init__.py`, eliminate eager top-level imports of heavy subcommands. Implement PEP 562 module-level `__getattr__` and `__dir__` to preserve backwards compatibility while deferring imports until attributes are accessed.

### 2. Lazy Infrastructure Runtime Loading (ADR-026 Rule 1 Extension)
- In `src/cresmo/infrastructure/adapters/native_media_ingestion_adapter.py`, remove top-level `import whisper`. Defer Whisper loading to `_transcribe_audio_native()` (or a lazy accessor property) so PyTorch is never loaded into `sys.modules` unless local audio fallback transcription is explicitly executed.
- In `src/cresmo/presentation/composition.py`, defer Langfuse client initialization and heavy adapter instantiation to the specific factory methods called by active use cases.

### 3. Default-Fast Ingestion Principle (Inverting Channel Crawling)
- Invert the crawler default: `cresmo run` MUST be fast by default.
- Set `CresmoSettings.enable_channel_crawler` default to `False`.
- In `src/cresmo/presentation/commands/run.py`:
  - Introduce explicit opt-in `--crawl` flag (`crawl: bool = False`) to enable channel feed crawling.
  - Maintain `--no-crawl` as a deprecated backward-compatible no-op.
  - Default execution processes local seeds, priority lists, and lakes with zero network crawler overhead.

### 4. Streamline VSCode Debug Tooling (`.vscode/launch.json`)
- Clean up `.vscode/launch.json` by removing redundant `--no-crawl` flags and consolidating duplicate profiles (e.g. duplicate `Seed Prompts`).
- Keep lean, clear profiles for core developer flows.

---

## Consequences

- **Positive**:
  - `cresmo --help` and lightweight commands load in < 0.5s instead of ~70s.
  - PyTorch/Whisper and Langfuse are never loaded unless explicitly needed.
  - `cresmo run` executes immediately without network crawler starvation.
  - Full alignment with ADR-002 (Presentation CLI & Humble Object), ADR-009 (Streaming Batch Discovery), and ADR-026 (Clean Code Governance).
- **Negative / Trade-offs**:
  - First invocation of audio transcription in `run` will incur the Whisper/Torch load time, but isolated strictly to that operation.
