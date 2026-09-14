# ADR-006: Resilient Workspace Root Discovery via Anchor Markers

**Status:** APPROVED  
**Date:** 2026-09-14  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context

In the initial implementation of configuration resolution ([`src/cresmo/infrastructure/config.py`](../../src/cresmo/infrastructure/config.py)) and candidate skill directory lookups ([`src/cresmo/infrastructure/adapters/prompt_provider.py`](../../src/cresmo/infrastructure/adapters/prompt_provider.py)), root directory determination relied on a **Structural Rigid Depth** calculation:

```python
_WORKSPACE_DIR = Path(__file__).resolve().parents[3]
```

While functional under strict directory conformity, this approach carried a hidden architectural risk:
1. **Coupling to Directory Depth:** Any refactoring or relocation of configuration files (e.g., moving `config.py` into a nested settings package) silently broke path resolution or caused files to be loaded from incorrect parent boundaries.
2. **Brittle Prompt Provider Traversal:** Candidate search for `.agents/skills` across varying depth levels (`parents[4]`) lacked resilience when packages were run from different execution contexts or containerized layouts.

---

## 2. Decision

We replace the hard-coded depth calculations with **Anchor Marker Resolution** implemented through the dedicated, lightweight infrastructure module [`src/cresmo/infrastructure/paths.py`](../../src/cresmo/infrastructure/paths.py).

### 2.1 Decoupled Paths Module (Single Responsibility Principle)
To prevent polluting [`src/cresmo/infrastructure/config.py`](../../src/cresmo/infrastructure/config.py) with filesystem traversal mechanics, `find_workspace_root()` is isolated in `paths.py` with zero external dependencies (pure `pathlib`).

### 2.2 Anchor Marker Specification
The algorithm traverses upward starting from the given path (or `__file__`) through all parents until it discovers at least one project anchor marker:
1. `pyproject.toml` (Primary repository root anchor)
2. `.git` (VCS boundary anchor)

If neither anchor is found (e.g., in unconventional deeply nested runtime environments without markers), it gracefully falls back to `parents[3]` preserving backward compatibility.

### 2.3 Centralized Consumption
All infrastructure components that require locating repository-level assets (`.env`, `data/`, `vault/`, `.agents/skills`) must consume `find_workspace_root()` from `cresmo.infrastructure.paths` or the derived `CresmoSettings` properties rather than calculating ad-hoc `parents[N]`.

---

## 3. Verification & Test Coverage

- Unit tests added in [`tests/cresmo/unit/test_config.py`](../../tests/cresmo/unit/test_config.py) explicitly verify:
  - Natural discovery of `pyproject.toml` from the live workspace.
  - Discovery from deeply nested synthetic subdirectories.
  - Graceful fallback when no anchor markers exist.
- Regression suite passing at 100% (323 passed tests).
- Formatted and validated against `ruff`.

---

## 4. Consequences & Impact

### Positive
1. **Refactoring Safety:** Modules within `src/` can be moved or nested without breaking environment loading or skills resolution.
2. **Multi-Context Portability:** Consistent behavior across local development, Docker containers, and CI/CD test runners.
3. **Explicit Failure Semantics:** Root discovery is deterministic, self-documenting, and thoroughly tested in the TDD suite.

### Negative / Trade-offs
1. Requires repository roots to contain at least one recognized anchor marker (`pyproject.toml` or `.git`).
