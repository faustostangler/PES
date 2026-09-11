"""Preflight Environmental Diagnostics and Health Checker.

Verifies environmental invariants (credentials, storage permissions, and
system binary dependencies like ffmpeg) in <10ms before executing resource-intensive
pipelines, adhering to ADR-003 and SPEC-003.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from pydantic import SecretStr

from cresmo.domain.exceptions import PreflightError


@dataclass(frozen=True)
class PreflightResult:
    """Immutable diagnostic report detailing environment readiness."""

    is_healthy: bool
    errors: tuple[str, ...]

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
    ) -> None:
        """Initialize health checker with system dependencies to probe.

        Args:
            gemini_api_key: SecretStr or string containing the API credential.
            vault_dir: Second Brain vault root directory.
            sqlite_ledger_path: Path to the SQLite WAL ledger database.
            check_ffmpeg: Whether to verify presence of ffmpeg in PATH.
        """
        self._api_key = gemini_api_key
        self._vault_dir = Path(vault_dir)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._check_ffmpeg = check_ffmpeg

    def check_all(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

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

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )
