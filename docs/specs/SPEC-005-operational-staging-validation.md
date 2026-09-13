# SPEC-005: Operational Staging Validation & Smoke Testing Engine

**Author**: Principal Socio-Technical Architect  
**Status**: APPROVED  
**Date**: 2026-09-11  
**Governing ADRs**: 
- [`docs/adr/ADR-003-pes-production-architecture.md`](../adr/ADR-003-pes-production-architecture.md)
- [`docs/adr/ADR-004-native-media-ingestion-decommissioning.md`](../adr/ADR-004-native-media-ingestion-decommissioning.md)

---

## 1. Problem Statement & Scope

Following the successful implementation of the Modular Monolith Core (`src/cresmo`), Channel Synchronization (`SPEC-003`), and Native Media Ingestion (`SPEC-004`), the system must be empirically verified against live upstream systems in an operational staging environment.

The objective of **Etapa III (Trilha 1)** is to execute controlled, non-destructive smoke tests and full-cycle validations proving:
1. **Upstream Connectivity**: Live ingestion of YouTube subtitles (timedtext JSON3) and audio extraction via `NativeMediaIngestionAdapter`.
2. **Generative Synthesis**: Multi-pass expansion and batched atomic note generation via `GeminiLLMAdapter`.
3. **Storage & Vault Integrity**: Atomic persistence of `raw/`, `enriched/`, and `wiki/` notes with valid YAML frontmatter and `[[WikiLinks]]` via `ObsidianVaultAdapter`.
4. **Idempotency & Auditing**: Atomic ledger persistence in `cresmo_ledger.db` under SQLite WAL mode via `SqliteLedgerAdapter`.
5. **Dry-Run Protection**: Strict guarantee that `--dry-run` operations perform zero LLM calls, zero ledger writes, and zero note modifications.

---

## 2. Staging Execution Matrix

| Test ID | Operation | Command | Expected Outcome | Verification Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **STG-01** | Preflight Diagnostics | `cresmo check-config` | Exit Code `0` | All paths writable; `GEMINI_API_KEY` present; SQLite directory valid. |
| **STG-02** | Single-Video Dry-Run | `cresmo run --url <url> --dry-run` | Exit Code `0` | Subtitle ingested; character count logged; 0 LLM calls; 0 wiki notes created. |
| **STG-03** | Channel Sync Dry-Run | `cresmo sync --channel <url> --dry-run --lookback 7 --max-videos 2` | Exit Code `0` | Feed scanned; candidate count logged; 0 ledger writes; 0 LLM calls. |
| **STG-04** | Live E2E Synthesis | `cresmo run --url <url> --passes 1` | Exit Code `0` | Full 6-stage execution; notes generated; MOC reconciled; ledger marked `COMPLETED`. |
| **STG-05** | Vault & Ledger Audit | Python verification script | Exit Code `0` | SQLite entry verified; YAML frontmatter valid; WikiLinks sanitized without raw brackets. |

---

## 3. Environmental Pre-requisites & Multi-Env Configuration

To eliminate fragile secret duplication across directories, `CresmoSettings` shall resolve `.env` files across standard hierarchical locations:
$$\text{.env (CWD)} \longrightarrow \text{<workspace_root>/.env} \longrightarrow \text{playground/cresmo/.env}$$

```python
model_config = SettingsConfigDict(
    env_file=(
        ".env",
        str(_WORKSPACE_DIR / ".env"),
        str(_WORKSPACE_DIR / "playground" / "cresmo" / ".env"),
    ),
    env_file_encoding="utf-8",
    extra="ignore",
)
```

---

## 4. Verification & Audit Report Gate

Upon execution of STG-01 through STG-05, the findings shall be consolidated in `docs/staging/STAGING-VERIFICATION-REPORT-001.md` documenting:
- Timestamps, duration, and hardware acceleration discovery.
- Total token usage and latency.
- Ingestion mechanism utilized (native JSON3 subtitles vs. Whisper fallback).
- Vault structural inspection (YAML frontmatter and WikiLink syntax).
- SQLite ledger audit record verification.
