"""Preflight Health Diagnostic Application Service for Cresmo.

Executes fail-fast configuration, binary, and filesystem checks via PreflightProbePort
before launching the synthesis pipeline.

Conforms to:
- ADR-003: PES Production Architecture & Telemetry
- ADR-014: Active Preflight Probes & Fail-Fast Observability
- SPEC-002: §3 (Preflight Diagnostics & Exit Code 2 Invariants)
- ADR-062: Structural Consolidation, Evals SSOT & Bootstrap Separation
- ADR-077: Strict Local Preflight Boundary (Zero Pydantic SecretStr Leakage)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from cresmo.application.ports.preflight import PreflightProbePort
from cresmo.domain.exceptions import PreflightError

PREFLIGHT_ERROR_SEPARATOR: Final[str] = "; "
REQUIRED_FFMPEG_BINARY: Final[str] = "ffmpeg"


@dataclass(frozen=True, slots=True)
class PreflightResult:
    """Immutable value object representing preflight system health status."""

    is_healthy: bool
    errors: tuple[str, ...]

    def assert_healthy(self) -> None:
        """Raise PreflightError if environment checks failed."""
        if not self.is_healthy:
            reasons = PREFLIGHT_ERROR_SEPARATOR.join(self.errors)
            raise PreflightError(f"Preflight health check failed: {reasons}")


class PreflightHealthChecker:
    """Application service executing runtime environment diagnostics via PreflightProbePort."""

    def __init__(
        self,
        *,
        gemini_api_key: str | None,
        vault_dir: Path,
        sqlite_ledger_path: Path,
        probe_port: PreflightProbePort,
        check_ffmpeg: bool = True,
        service_health_urls: dict[str, str] | None = None,
        probe_timeout_seconds: float = 1.0,
    ) -> None:
        """Initialize preflight health checker with target coordinates and probe port."""
        self._gemini_api_key = gemini_api_key
        self._vault_dir = Path(vault_dir)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._probe_port = probe_port
        self._check_ffmpeg = check_ffmpeg
        self._service_health_urls = dict(service_health_urls) if service_health_urls else {}
        self._probe_timeout_seconds = probe_timeout_seconds

    def check_all(self) -> PreflightResult:
        """Execute all local diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. API credential verification
        if not (self._gemini_api_key or "").strip():
            errors.append("Missing required GEMINI_API_KEY credential")

        # 2. Vault directory existence and write permissions
        try:
            self._probe_port.ensure_directory(self._vault_dir)
            if not self._probe_port.is_writable(self._vault_dir):
                errors.append(f"Vault directory is not writable: '{self._vault_dir}'")
        except OSError as exc:
            errors.append(f"Cannot access vault directory '{self._vault_dir}': {exc}")

        # 3. SQLite ledger directory existence and write permissions
        ledger_dir = self._sqlite_ledger_path.parent
        try:
            self._probe_port.ensure_directory(ledger_dir)
            if not self._probe_port.is_writable(ledger_dir):
                errors.append(f"SQLite ledger directory is not writable: '{ledger_dir}'")
        except OSError as exc:
            errors.append(f"Cannot access SQLite ledger directory '{ledger_dir}': {exc}")

        # 4. System binary dependencies
        if self._check_ffmpeg and not self._probe_port.executable_exists(REQUIRED_FFMPEG_BINARY):
            errors.append(f"System binary '{REQUIRED_FFMPEG_BINARY}' not found in PATH")

        # 5. Active backing service health probes (fail-fast with 'make up' guidance)
        for service_name, health_url in self._service_health_urls.items():
            if not self._probe_port.probe_http(
                health_url, timeout_seconds=self._probe_timeout_seconds
            ):
                errors.append(
                    f"Service '{service_name}' is unreachable at '{health_url}' "
                    "(run 'make up' to start required containers)"
                )

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )
