"""Preflight Health Diagnostic Application Service for Cresmo.

Executes fail-fast configuration, binary, filesystem, and optional HTTP service
checks via PreflightProbePort before launching the synthesis pipeline.

Conforms to:
- ADR-003: PES Production Architecture & Telemetry
- ADR-014: Active Preflight Probes & Fail-Fast Observability
- SPEC-002: §3 (Preflight Diagnostics & Exit Code 2 Invariants)
- ADR-062: Structural Consolidation, Evals SSOT & Bootstrap Separation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import SecretStr

from cresmo.application.ports.preflight import PreflightProbePort
from cresmo.domain.exceptions import PreflightError


@dataclass(frozen=True, slots=True)
class PreflightResult:
    """Immutable value object representing preflight system health status."""

    is_healthy: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def assert_healthy(self) -> None:
        """Raise PreflightError if environment checks failed."""
        if not self.is_healthy:
            reasons = "; ".join(self.errors)
            raise PreflightError(f"Preflight health check failed: {reasons}")


class PreflightHealthChecker:
    """Application service executing runtime environment diagnostics via PreflightProbePort."""

    def __init__(
        self,
        *,
        gemini_api_key: SecretStr | str | None,
        vault_dir: Path | str,
        sqlite_ledger_path: Path | str,
        probe_port: PreflightProbePort | None,
        check_ffmpeg: bool = True,
        langfuse_host: str | None = None,
        ollama_base_url: str | None = None,
    ) -> None:
        """Initialize preflight health checker with target coordinates and probe port."""
        if probe_port is None:
            raise ValueError("probe_port is required.")
        self._gemini_api_key = gemini_api_key
        self._vault_dir = Path(vault_dir)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._probe_port = probe_port
        self._check_ffmpeg = check_ffmpeg
        self._langfuse_host = langfuse_host
        self._ollama_base_url = ollama_base_url

    def _extract_secret(self, val: Any) -> str:
        """Extract raw secret string safely from SecretStr or str."""
        if isinstance(val, SecretStr):
            return val.get_secret_value().strip()
        if isinstance(val, str):
            return val.strip()
        return ""

    def check_langfuse_probe(self, host: str, timeout_seconds: float = 2.0) -> bool:
        """Active preflight probe verifying Langfuse server health endpoint response."""
        normalized_host = host.rstrip("/")
        probe_url = f"{normalized_host}/api/public/health"
        if self._probe_port.probe_http(probe_url, timeout_seconds=timeout_seconds):
            return True
        if "localhost" in normalized_host:
            fallback_url = probe_url.replace("localhost", "127.0.0.1")
            return self._probe_port.probe_http(fallback_url, timeout_seconds=timeout_seconds)
        return False

    def check_ollama_probe(self, base_url: str, timeout_seconds: float = 1.0) -> bool:
        """Active preflight probe verifying local Ollama daemon responsiveness."""
        normalized_url = base_url.rstrip("/")
        probe_url = f"{normalized_url}/api/version"
        return self._probe_port.probe_http(probe_url, timeout_seconds=timeout_seconds)

    def check_all(
        self,
        probe_telemetry: bool = False,
        probe_ollama: bool = False,
    ) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []
        warnings: list[str] = []

        # 1. API credential verification
        key_val = self._extract_secret(self._gemini_api_key)
        if not key_val:
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
        if self._check_ffmpeg and not self._probe_port.executable_exists("ffmpeg"):
            errors.append("System binary 'ffmpeg' not found in PATH")

        # 5. Optional active telemetry probe (non-blocking warning on failure)
        if (
            probe_telemetry
            and self._langfuse_host
            and not self.check_langfuse_probe(self._langfuse_host)
        ):
            warnings.append(
                f"Langfuse server at '{self._langfuse_host}' is unreachable. Telemetry disabled."
            )

        # 6. Optional active Ollama daemon probe
        if (
            probe_ollama
            and self._ollama_base_url
            and not self.check_ollama_probe(self._ollama_base_url)
        ):
            errors.append(f"Local Ollama daemon at '{self._ollama_base_url}' is unreachable.")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
