"""Preflight Environmental Diagnostics and Health Checker.

Verifies environmental invariants (credentials, storage permissions, and system binary
dependencies like ffmpeg) in <10ms before executing resource-intensive pipelines,
adhering to fail-fast principles per ADR-003, ADR-005 (12-Factor App), and SPEC-005.
"""

from __future__ import annotations

import os
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import SecretStr

from cresmo.domain.exceptions import PreflightError


def probe_http_endpoint(url: str, timeout_seconds: float = 1.0) -> bool:
    """Active preflight probe verifying whether an HTTP endpoint is reachable and responsive.

    Performs a fast, non-blocking synchronous HTTP GET request with a short socket timeout,
    shielding callers from connection hangs and OpenTelemetry retry loops per ADR-014.

    Args:
        url: Target HTTP/HTTPS endpoint URL to probe.
        timeout_seconds: Granular socket timeout in seconds (default: 1.0s).

    Returns:
        True if server responds with HTTP status < 500; False if connection fails,
        refuses connection, times out, or returns a 5xx server error.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CresmoPreflightProbe/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            return int(response.status) < 500
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False
    except Exception:  # noqa: BLE001
        return False


@dataclass(frozen=True)
class PreflightResult:
    """Immutable diagnostic report detailing environment readiness."""

    is_healthy: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def assert_healthy(self) -> None:
        """Raise PreflightError immediately if any health check failed."""
        if not self.is_healthy:
            reasons = "; ".join(self.errors)
            raise PreflightError(f"Preflight health check failed: {reasons}")


class PreflightHealthChecker:
    """Bootstrap diagnostic service enforcing fail-fast environmental invariants."""

    def __init__(
        self,
        gemini_api_key: SecretStr | str | None,
        vault_dir: Path | str,
        sqlite_ledger_path: Path | str,
        check_ffmpeg: bool = True,
        langfuse_host: str | None = None,
        ollama_base_url: str | None = None,
    ) -> None:
        """Initialize health checker with system dependencies to probe.

        Args:
            gemini_api_key: SecretStr or string containing the API credential.
            vault_dir: Second Brain vault root directory.
            sqlite_ledger_path: Path to the SQLite WAL ledger database.
            check_ffmpeg: Whether to verify presence of ffmpeg in PATH.
            langfuse_host: Optional Langfuse server host for telemetry probe.
            ollama_base_url: Optional Ollama base URL for local inference probe.
        """
        self._api_key = gemini_api_key
        self._vault_dir = Path(vault_dir)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._check_ffmpeg = check_ffmpeg
        self._langfuse_host = langfuse_host
        self._ollama_base_url = ollama_base_url

    def check_langfuse_probe(self, host: str, timeout_seconds: float = 1.0) -> bool:
        """Active preflight probe to verify if Langfuse server health endpoint is responding.

        Args:
            host: Root Langfuse host (e.g. 'http://localhost:3000').
            timeout_seconds: Socket timeout in seconds.

        Returns:
            True if Langfuse is healthy and ready; False otherwise.
        """
        normalized_host = host.rstrip("/")
        probe_url = f"{normalized_host}/api/public/health"
        return probe_http_endpoint(probe_url, timeout_seconds=timeout_seconds)

    def check_ollama_probe(self, base_url: str, timeout_seconds: float = 1.0) -> bool:
        """Active preflight probe to verify if local Ollama daemon is responding.

        Args:
            base_url: Root Ollama endpoint URL (e.g. 'http://localhost:11434').
            timeout_seconds: Socket timeout in seconds.

        Returns:
            True if Ollama daemon is running and reachable; False otherwise.
        """
        normalized_url = base_url.rstrip("/")
        probe_url = f"{normalized_url}/api/version"
        return probe_http_endpoint(probe_url, timeout_seconds=timeout_seconds)

    def check_all(
        self,
        probe_telemetry: bool = False,
        probe_ollama: bool = False,
    ) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if not raw_key.strip():
            errors.append("Missing required GEMINI_API_KEY credential")

        # 2. Verify Obsidian Vault Directory Accessibility
        try:
            self._vault_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(self._vault_dir, os.W_OK):
                errors.append(f"Vault directory is not writable: '{self._vault_dir}'")
        except OSError as exc:
            errors.append(f"Cannot access vault directory '{self._vault_dir}': {exc}")

        # 3. Verify SQLite Ledger Directory Accessibility
        try:
            ledger_dir = self._sqlite_ledger_path.parent
            ledger_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(ledger_dir, os.W_OK):
                errors.append(f"SQLite ledger directory is not writable: '{ledger_dir}'")
        except OSError as exc:
            errors.append(
                f"Cannot access SQLite ledger directory '{self._sqlite_ledger_path.parent}': {exc}"
            )

        # 4. Verify ffmpeg binary in PATH
        if self._check_ffmpeg and shutil.which("ffmpeg") is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        # 5. Optional active telemetry probe
        if (
            probe_telemetry
            and self._langfuse_host
            and not self.check_langfuse_probe(self._langfuse_host)
        ):
            warnings.append(
                f"Langfuse server at '{self._langfuse_host}' is unreachable. Telemetry disabled."
            )

        # 6. Optional active local Ollama probe
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
