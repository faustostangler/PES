# ADR-072: Langfuse Tracing Environment Governance

- **Status:** Accepted
- **Date:** 2026-11-22
- **Bounded Context:** Cresmo (`Infrastructure/Config`, `Bootstrap/TelemetryFactory`, `Presentation/CLI`)
- **Supersedes / Amends:** Amends `ADR-069` / `SPEC-069` (`TelemetrySettings.langfuse_environment`)

## Context

Langfuse organizes traces, observations, scores, and sessions by a first-class `environment` attribute (`LANGFUSE_TRACING_ENVIRONMENT` in the official SDK). Environments are created automatically on first ingestion, are persistent, and must satisfy Langfuse's strict naming contract: regex `^(?!langfuse)[a-z0-9-_]{1,40}$` (lowercase letters, digits, hyphens, underscores; max 40 characters; cannot start with `"langfuse"`).

Previously in Cresmo:
1. `TelemetrySettings.langfuse_environment` defaulted to `"development"` without `AliasChoices` for `LANGFUSE_TRACING_ENVIRONMENT` or `LANGFUSE_ENVIRONMENT`, and without fail-fast format validation.
2. `resolve_langfuse_client` in `src/cresmo/bootstrap/factories/telemetry_factory.py` fell back to `"development"`, did not mirror `LANGFUSE_TRACING_ENVIRONMENT` into `os.environ`, and `_clean_langfuse_env()` did not clear it on circuit-break/error.
3. `.env` and `.env.example` did not declare `LANGFUSE_TRACING_ENVIRONMENT`.

## Decision

1. **Canonical Default (`staging`):**
   - Introduce `DEFAULT_LANGFUSE_ENVIRONMENT: str = "staging"` and `LANGFUSE_ENVIRONMENT_PATTERN: str = r"^(?!langfuse)[a-z0-9-_]{1,40}$"` in `src/cresmo/infrastructure/config/catalog.py`, re-exported via `CresmoSettings` and `cresmo.infrastructure.config`.
   - Set `TelemetrySettings.langfuse_environment` default to `DEFAULT_LANGFUSE_ENVIRONMENT` (`"staging"`).
2. **Standard Environment Variable Resolution & Fail-Fast Validation:**
   - Map `langfuse_environment` with `validation_alias=AliasChoices("langfuse_environment", "LANGFUSE_TRACING_ENVIRONMENT", "LANGFUSE_ENVIRONMENT")`.
   - Normalize input via `strip().lower()` and validate strictly against `LANGFUSE_ENVIRONMENT_PATTERN` in a Pydantic `field_validator` so invalid environment names fail fast at startup before any trace ingestion.
3. **Bootstrap Synchronization & Cleanup:**
   - `resolve_langfuse_client` resolves `langfuse_environment` with fallback `DEFAULT_LANGFUSE_ENVIRONMENT`, passes `"environment"` to `Langfuse(...)`, and sets `os.environ["LANGFUSE_TRACING_ENVIRONMENT"]` so implicit OTel/Langfuse integrations remain aligned.
   - `_clean_langfuse_env()` pops `LANGFUSE_TRACING_ENVIRONMENT` alongside the other Langfuse environment variables when telemetry is bypassed or fails initialization.
4. **CLI Diagnostics & `.env` Override:**
   - `cresmo check-config` displays the resolved `env=<langfuse_environment>` when Langfuse telemetry is enabled.
   - `.env.example` documents `LANGFUSE_TRACING_ENVIRONMENT="staging"` and `.env` explicitly sets `LANGFUSE_TRACING_ENVIRONMENT="staging"`.

## Consequences

- **Positive:** Prevents accidental pollution of `"default"` or `"production"` Langfuse environments, enforces Langfuse's naming constraints at config load time, and guarantees 12-Factor parity between Pydantic settings and SDK environment variables.
- **Negative / Trade-offs:** Any caller passing uppercase or invalid characters (e.g., spaces, slashes, `"langfuse-..."`, >40 chars) will fail fast at configuration load instead of silently failing or creating malformed environments at ingestion time.
