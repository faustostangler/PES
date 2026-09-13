# SPEC-006: Container Execution & CI/CD Pipeline Specification

**Status:** APPROVED  
**Date:** 2026-09-12  
**Governing Method:** Doctor Stangler Architecture Method (12-Factor App & IaC)  
**Governing ADR:** [`docs/adr/ADR-005-multi-role-12factor-container-architecture.md`](../adr/ADR-005-multi-role-12factor-container-architecture.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Objective & Scope

This specification defines the exact technical requirements, contracts, and validation criteria for containerizing the Cresmo Modular Monolith into a universal, multi-role, 12-Factor compliant Docker image (`pes-cresmo:latest`), alongside its declarative orchestration (`docker-compose.yml`) and automated continuous integration pipeline (`.github/workflows/ci.yml`).

---

## 2. Container Image Specification (`Dockerfile`)

### 2.1 Multi-Stage Build Stages

1. **Dependency Engine Stage (`uv-bin`):**
   - Source: `ghcr.io/astral-sh/uv:latest`
   - Purpose: Ephemeral binary copy of `/uv` and `/uvx` into `/bin/`.
2. **Runtime Stage (`runtime`):**
   - Base OS: `python:3.13-slim-bookworm`
   - System Packages: `ffmpeg` (audio conversion/extraction), `ca-certificates` (TLS validation), `curl` (container healthcheck).
   - Working Directory: `/app`
   - System User: `appuser:appuser` (UID: 1000, GID: 1000).

### 2.2 Layer Invariants & Caching Optimization

- **Environment Flags:**
  - `PYTHONUNBUFFERED=1`: Ensures real-time streaming of stdout/stderr logs.
  - `UV_COMPILE_BYTECODE=1`: Compiles `.pyc` files ahead of time for instant container startup.
  - `UV_LINK_MODE=copy`: Avoids hardlink cross-filesystem boundary issues inside container mounts.
  - `PATH="/app/.venv/bin:$PATH"`: Injects application virtualenv into system PATH.
- **Dependency Caching:**
  - `pyproject.toml` and `uv.lock` are copied first.
  - `uv sync --frozen --no-dev --no-install-project` resolves and caches third-party dependencies into `/app/.venv`.
- **Source Code Installation:**
  - `src/` and `docker/` are copied.
  - `uv sync --frozen --no-dev` installs the Cresmo package into `/app/.venv`.

---

## 3. Dynamic Entrypoint Contract (`docker/entrypoint.sh`)

### 3.1 Routing Matrix

The entrypoint must be a POSIX shell script (`#!/bin/sh`) enforcing `set -euo pipefail`. It dispatches execution according to the following precedence:

| Condition / Input | Target Execution | Example Invocation |
| :--- | :--- | :--- |
| First argument is a known cresmo command (`check-config`, `sync`, `dedupe`) | `exec uv run cresmo "$@"` | `docker run pes-cresmo check-config` |
| First argument begins with `-` (flag) | `exec uv run cresmo "$@"` | `docker run pes-cresmo --help` |
| `$ROLE == "cli"` | `exec uv run cresmo "$@"` | `docker run -e ROLE=cli pes-cresmo dedupe` |
| `$ROLE == "worker"` | `exec uv run cresmo sync --all` | `docker run -e ROLE=worker pes-cresmo` |
| `$ROLE == "api"` | `exec uv run uvicorn cresmo.presentation.api:app --host 0.0.0.0 --port "${PORT:-8000}"` | `docker run -e ROLE=api -p 8000:8000 pes-cresmo` |
| Arbitrary command provided (`sh`, `bash`, `pytest`) | `exec "$@"` | `docker run pes-cresmo pytest` |

---

## 4. Storage & Volume Binding Specifications

The container requires two dedicated mount points adhering to the Medallion Architecture:

```
Host Filesystem                      Container Filesystem
./data/            ===============>  /app/data/
  ├── raw/                             ├── raw/
  ├── enriched/                        ├── enriched/
  └── cresmo_ledger.db                 └── cresmo_ledger.db

./vault/           ===============>  /app/vault/
  ├── _index.json                      ├── _index.json
  ├── concepts/                        ├── concepts/
  ├── entities/                        ├── entities/
  ├── events/                          ├── events/
  ├── processes/                       ├── processes/
  └── MOCs/                            └── MOCs/
```

- In-container environment defaults:
  - `DATA_DIR=/app/data`
  - `VAULT_DIR=/app/vault`

---

## 5. Docker Compose Service Topology (`docker-compose.yml`)

The declarative compose topology defines the standard execution roles:

1. **`cresmo-runner` (CLI Task Runner):**
   - Profile: `tools`
   - Purpose: One-off interactive CLI operations (`check-config`, `dedupe`, `sync`).
   - Volumes: `./data:/app/data`, `./vault:/app/vault`.
   - Env file: `vault/.env` / `.env`.
2. **`cresmo-worker` (Background Worker):**
   - Profile: `default`
   - Purpose: Continuous daemon mode for channel polling and asynchronous knowledge synthesis.
   - Restart policy: `unless-stopped`.
   - Volumes: `./data:/app/data`, `./vault:/app/vault`.
3. **`cresmo-check` (Preflight Health Check):**
   - Profile: `tools`
   - Purpose: Instant healthcheck and configuration validation.
   - Command: `["check-config"]`

---

## 6. Continuous Integration Specification (`.github/workflows/ci.yml`)

The CI workflow runs on `ubuntu-latest` for every push and pull request targeting `main`:

### 6.1 Job 1: Quality Gate (`quality`)
1. Checkout repository with full depth.
2. Install `uv` via official GitHub Action (`astral-sh/setup-uv@v4`).
3. Set up Python 3.13 using `uv python install 3.13`.
4. Install all dependencies including dev tools: `uv sync --frozen`.
5. **Linting & Formatting Check:** `uv run ruff check .` and `uv run ruff format --check .`.
6. **Type Soundness:** `uv run mypy src/cresmo tests/cresmo --strict` (or configured flags).
7. **Hermetic Test Suite:** `uv run pytest tests/cresmo --cov=src/cresmo --cov-report=xml`.

### 6.2 Job 2: Container Verification (`docker`)
1. Set up Docker Buildx (`docker-buildx-action`).
2. Build container image: `docker build -t pes-cresmo:ci .`.
3. Verify entrypoint and config validation inside container:
   `docker run --rm pes-cresmo:ci cresmo check-config` (with dummy environment).

---

## 7. Acceptance & Verification Criteria

- [ ] Multi-stage `Dockerfile` successfully builds with `docker build -t pes-cresmo:latest .`.
- [ ] Container user is `appuser` (UID 1000) and cannot escalate to root.
- [ ] Running `docker run --rm --env-file vault/.env -v $(pwd)/data:/app/data -v $(pwd)/vault:/app/vault pes-cresmo:latest check-config` succeeds with returncode 0.
- [ ] Running `docker run --rm --env-file vault/.env -v $(pwd)/data:/app/data -v $(pwd)/vault:/app/vault pes-cresmo:latest dedupe` succeeds and outputs the graph deduplication summary.
- [ ] `docker-compose.yml` runs successfully with `docker compose run --rm cresmo-check`.
- [ ] CI workflow file `.github/workflows/ci.yml` is valid YAML and matches all quality checks.
