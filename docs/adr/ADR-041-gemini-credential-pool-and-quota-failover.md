# ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation

**Status:** ACCEPTED  
**Date:** 2026-10-13  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-005`](ADR-005-multi-role-12factor-container-architecture.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-029`](ADR-029-unified-quality-judge-port-and-evaluator-adapters.md), [`ADR-039`](ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md)

---

## 1. Context & Architectural Motivation

Google GenAI Free Tier imposes severe rate limits per project/model (e.g. 20 requests/day on `gemini-3.5-flash`, 15 RPM). When hitting `429 RESOURCE_EXHAUSTED`, the server returns a `retryDelay` (which can span hours or seconds).

### 1.1 Problems with Current Single-Key Setup:
1. **Silent Fallthrough in `.env`:** Defining multiple `GEMINI_API_KEY=...` entries in `.env` silently overwrites earlier keys; only the last key is loaded.
2. **Infinite or Extended Silent Sleep:** Current tenacity retry blocks sleep for minutes without failover, hanging batch benchmarks or synthesis pipelines.
3. **Absence of Credential Failover:** The system has no mechanism to lease an alternate API key when the primary key's quota is exhausted.

---

## 2. Decision

We implement Strategy **A1 + B2** (Configuração 12-Factor via lista de chaves + Failover com Cooldown e fallback sucessivo baseado no `retryDelay` da API).

### 2.1 Configuration Schema in `CresmoSettings`
- Add `gemini_api_keys: list[SecretStr]` to `src/cresmo/infrastructure/config.py`.
- Support comma-separated strings in `.env` (`GEMINI_API_KEYS=key1,key2`) and backward-compatibility with single `GEMINI_API_KEY`.
- Validate that at least one valid key is present.
- Provide helper property `gemini_api_key` returning the primary key for backward compatibility.

### 2.2 Domain-Independent Infrastructure Component: `GeminiCredentialPool`
Located in `src/cresmo/infrastructure/adapters/gemini_pool.py`:
1. **Thread-Safe Key Leasing:**
   - Always attempts to lease the **first key** (index 0).
   - If key 0 is currently in cooldown (its cooldown expiration timestamp > `time.monotonic()`), it falls back to key 1, then key 2, etc.
   - If a key's cooldown timestamp has passed, it is automatically unblocked and ready to be leased again (returning to priority 0).
   - If ALL keys in the pool are currently in cooldown, it raises `CredentialPoolExhaustedError` immediately (fail-fast), containing the minimal wait time until the earliest key recovers. No indefinite hang!
2. **Quota Depletion Reporting:**
   - Method `report_quota_exhausted(key_str: str, retry_delay_seconds: float)` parses the server's `retryDelay` (or a safe minimum default like 60s) and marks that specific key in cooldown until `now + retry_delay_seconds`.
   - Obfuscated alias logging (e.g. `key#0:a3f9`) ensures actual secrets are NEVER written to logs.
3. **Client Cache:**
   - Caches `genai.Client` instances keyed by secret value to avoid re-instantiation overhead.

### 2.3 Strict 429 Scoping (No Rotation on 503)
- Rotation is triggered **ONLY** on HTTP 429 (`RESOURCE_EXHAUSTED`).
- HTTP 503 (`UNAVAILABLE` / high demand) is a backend cluster load error, NOT a credential quota depletion. On 503, standard tenacity retry backoff is executed without credential rotation.

### 2.4 Integration in Adapters
- Both `GeminiLLMAdapter` and `GeminiJudgeAdapter` accept an optional `credential_pool: GeminiCredentialPool`.
- When making calls, they acquire the current active client from `pool.get_active_client()`.
- On catching a 429 exception, they extract `retryDelay`, notify the pool, lease the next fallback key, and retry immediately with the new client.

---

## 3. Causal Chain & Consequences

```
HTTP 429 (Quota Exceeded)
       │
       ▼
Extract retryDelay from Google RPC violation (e.g. 3600s)
       │
       ▼
GeminiCredentialPool.mark_in_cooldown(active_key, 3600s)
       │
       ▼
Lease next available key (index + 1)
       │
       ├── Available ──► Immediate call with secondary genai.Client
       └── All Cooled Down ──► Fail-Fast CredentialPoolExhaustedError (no 5min hang)
```

### Positive Consequences
- Automatic seamless utilization of multiple GCP projects.
- Always prioritizes primary key (index 0) as soon as its cooldown expires.
- Zero silent 5-minute hanging on quota exhaustion.
- Complies with 12-Factor App and Clean Architecture (infrastructure adapter isolation).
