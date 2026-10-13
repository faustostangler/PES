# SPEC-041: Gemini Credential Pool and Quota-Aware Failover Rotation

**Status:** APPROVED  
**Date:** 2026-10-13  
**Originating ADR:** [`docs/adr/ADR-041-gemini-credential-pool-and-quota-failover.md`](../adr/ADR-041-gemini-credential-pool-and-quota-failover.md)  
**Governing Method:** Doctor Stangler Architecture Method (TDD Red-Green-Refactor, Hexagonal/Clean Architecture, Fail-Fast)  

---

## 1. Domain & Infrastructure Invariants

1. **`GeminiCredentialPool` Component:**
   - Invariants:
     - `lease()` returns a tuple `(key_str, client, alias)` representing the first non-cooled-down key in the declared order.
     - `report_quota_exhausted(key_str, retry_delay_seconds)` marks the key in cooldown until `time.monotonic() + retry_delay_seconds`.
     - When index 0 recovers from cooldown, the next `lease()` immediately picks index 0 again.
     - If all keys are in cooldown, `lease()` raises `CredentialPoolExhaustedError` with `retry_after_seconds = min(cooldown_expirations) - now`.
     - Thread-safe using `threading.Lock`.
     - Aliases are strictly masked: `f"key#{idx}:{hashlib.sha256(k.encode()).hexdigest()[:4]}"`.
2. **Settings Parsing:**
   - `CresmoSettings` parses `GEMINI_API_KEYS` (comma-separated or list of strings) into `list[SecretStr]`.
   - Backward-compatible with `GEMINI_API_KEY`.
3. **HTTP 429 Scoping:**
   - Rotation happens ONLY on HTTP 429.
   - HTTP 503 does NOT trigger cooldown or key rotation.

---

## 2. Test Specifications (Refractometry - Phase 2)

### Test 1: `test_credential_pool_leases_first_key_by_default`
- Pool initialized with `["key-primary", "key-secondary"]`.
- `pool.lease()[0]` must return `"key-primary"`.

### Test 2: `test_credential_pool_rotates_to_secondary_on_quota_exhausted`
- Key `"key-primary"` reported with `retry_delay_seconds=100.0`.
- Next `pool.lease()[0]` must return `"key-secondary"`.

### Test 3: `test_credential_pool_reverts_to_primary_once_cooldown_expires`
- Key `"key-primary"` reported with `retry_delay_seconds=0.01`.
- Sleep 0.02s.
- `pool.lease()[0]` returns `"key-primary"`.

### Test 4: `test_credential_pool_exhausted_raises_fail_fast`
- Both keys reported exhausted with 50s cooldown.
- Calling `pool.lease()` raises `CredentialPoolExhaustedError`.

### Test 5: `test_settings_parses_comma_separated_keys`
- `CresmoSettings(gemini_api_keys="key1,key2")` yields `2` items in `settings.gemini_api_keys`.
