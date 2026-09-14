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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


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
mutants_xǁPreflightHealthCheckerǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut: MutantDict = {}  # type: ignore


class PreflightHealthChecker:
    """Bootstrap diagnostic service enforcing fail-fast environmental invariants."""

    @_mutmut_mutated(mutants_xǁPreflightHealthCheckerǁ__init____mutmut)
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

    def xǁPreflightHealthCheckerǁ__init____mutmut_orig(
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

    def xǁPreflightHealthCheckerǁ__init____mutmut_1(
        self,
        gemini_api_key: SecretStr | str | None,
        vault_dir: Path | str,
        sqlite_ledger_path: Path | str,
        check_ffmpeg: bool = False,
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

    def xǁPreflightHealthCheckerǁ__init____mutmut_2(
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
        self._api_key = None
        self._vault_dir = Path(vault_dir)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._check_ffmpeg = check_ffmpeg

    def xǁPreflightHealthCheckerǁ__init____mutmut_3(
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
        self._vault_dir = None
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._check_ffmpeg = check_ffmpeg

    def xǁPreflightHealthCheckerǁ__init____mutmut_4(
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
        self._vault_dir = Path(None)
        self._sqlite_ledger_path = Path(sqlite_ledger_path)
        self._check_ffmpeg = check_ffmpeg

    def xǁPreflightHealthCheckerǁ__init____mutmut_5(
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
        self._sqlite_ledger_path = None
        self._check_ffmpeg = check_ffmpeg

    def xǁPreflightHealthCheckerǁ__init____mutmut_6(
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
        self._sqlite_ledger_path = Path(None)
        self._check_ffmpeg = check_ffmpeg

    def xǁPreflightHealthCheckerǁ__init____mutmut_7(
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
        self._check_ffmpeg = None

    @_mutmut_mutated(mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_orig(self) -> PreflightResult:
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_1(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = None

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_2(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = None
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_3(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key and "")
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_4(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "XXXX")
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_5(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if raw_key.strip():
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_6(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if not raw_key.strip():
            errors.append(None)

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_7(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if not raw_key.strip():
            errors.append("XXMissing required GEMINI_API_KEY credentialXX")

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_8(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if not raw_key.strip():
            errors.append("missing required gemini_api_key credential")

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_9(self) -> PreflightResult:
        """Execute all diagnostics and return a comprehensive PreflightResult."""
        errors: list[str] = []

        # 1. Verify Gemini API Key
        raw_key = (
            self._api_key.get_secret_value()
            if isinstance(self._api_key, SecretStr)
            else (self._api_key or "")
        )
        if not raw_key.strip():
            errors.append("MISSING REQUIRED GEMINI_API_KEY CREDENTIAL")

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_10(self) -> PreflightResult:
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
            self._vault_dir.mkdir(parents=None, exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_11(self) -> PreflightResult:
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
            self._vault_dir.mkdir(parents=True, exist_ok=None)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_12(self) -> PreflightResult:
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
            self._vault_dir.mkdir(exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_13(self) -> PreflightResult:
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
            self._vault_dir.mkdir(parents=True, )
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_14(self) -> PreflightResult:
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
            self._vault_dir.mkdir(parents=False, exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_15(self) -> PreflightResult:
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
            self._vault_dir.mkdir(parents=True, exist_ok=False)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_16(self) -> PreflightResult:
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
            if os.access(self._vault_dir, os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_17(self) -> PreflightResult:
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
            if not os.access(None, os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_18(self) -> PreflightResult:
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
            if not os.access(self._vault_dir, None):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_19(self) -> PreflightResult:
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
            if not os.access(os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_20(self) -> PreflightResult:
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
            if not os.access(self._vault_dir, ):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_21(self) -> PreflightResult:
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
                errors.append(None)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_22(self) -> PreflightResult:
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
            errors.append(None)

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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_23(self) -> PreflightResult:
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
            ledger_dir = None
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_24(self) -> PreflightResult:
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
            ledger_dir.mkdir(parents=None, exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_25(self) -> PreflightResult:
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
            ledger_dir.mkdir(parents=True, exist_ok=None)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_26(self) -> PreflightResult:
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
            ledger_dir.mkdir(exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_27(self) -> PreflightResult:
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
            ledger_dir.mkdir(parents=True, )
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_28(self) -> PreflightResult:
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
            ledger_dir.mkdir(parents=False, exist_ok=True)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_29(self) -> PreflightResult:
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
            ledger_dir.mkdir(parents=True, exist_ok=False)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_30(self) -> PreflightResult:
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
            if os.access(ledger_dir, os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_31(self) -> PreflightResult:
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
            if not os.access(None, os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_32(self) -> PreflightResult:
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
            if not os.access(ledger_dir, None):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_33(self) -> PreflightResult:
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
            if not os.access(os.W_OK):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_34(self) -> PreflightResult:
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
            if not os.access(ledger_dir, ):
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_35(self) -> PreflightResult:
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
                errors.append(None)
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

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_36(self) -> PreflightResult:
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
                None
            )

        # 4. Verify ffmpeg binary in PATH
        if self._check_ffmpeg and shutil.which("ffmpeg") is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_37(self) -> PreflightResult:
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
        if self._check_ffmpeg or shutil.which("ffmpeg") is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_38(self) -> PreflightResult:
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
        if self._check_ffmpeg and shutil.which(None) is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_39(self) -> PreflightResult:
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
        if self._check_ffmpeg and shutil.which("XXffmpegXX") is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_40(self) -> PreflightResult:
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
        if self._check_ffmpeg and shutil.which("FFMPEG") is None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_41(self) -> PreflightResult:
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
        if self._check_ffmpeg and shutil.which("ffmpeg") is not None:
            errors.append("System binary 'ffmpeg' not found in PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_42(self) -> PreflightResult:
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
            errors.append(None)

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_43(self) -> PreflightResult:
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
            errors.append("XXSystem binary 'ffmpeg' not found in PATHXX")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_44(self) -> PreflightResult:
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
            errors.append("system binary 'ffmpeg' not found in path")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_45(self) -> PreflightResult:
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
            errors.append("SYSTEM BINARY 'FFMPEG' NOT FOUND IN PATH")

        return PreflightResult(
            is_healthy=len(errors) == 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_46(self) -> PreflightResult:
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
            is_healthy=None,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_47(self) -> PreflightResult:
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
            errors=None,
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_48(self) -> PreflightResult:
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
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_49(self) -> PreflightResult:
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
            )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_50(self) -> PreflightResult:
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
            is_healthy=len(errors) != 0,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_51(self) -> PreflightResult:
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
            is_healthy=len(errors) == 1,
            errors=tuple(errors),
        )

    def xǁPreflightHealthCheckerǁcheck_all__mutmut_52(self) -> PreflightResult:
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
            errors=tuple(None),
        )

mutants_xǁPreflightHealthCheckerǁ__init____mutmut['_mutmut_orig'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_1'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_2'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_3'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_4'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_5'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_6'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁ__init____mutmut['xǁPreflightHealthCheckerǁ__init____mutmut_7'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁ__init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['_mutmut_orig'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_orig # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_1'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_1 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_2'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_2 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_3'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_3 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_4'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_4 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_5'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_5 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_6'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_6 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_7'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_7 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_8'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_8 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_9'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_9 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_10'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_10 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_11'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_11 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_12'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_12 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_13'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_13 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_14'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_14 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_15'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_15 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_16'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_16 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_17'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_17 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_18'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_18 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_19'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_19 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_20'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_20 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_21'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_21 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_22'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_22 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_23'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_23 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_24'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_24 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_25'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_25 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_26'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_26 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_27'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_27 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_28'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_28 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_29'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_29 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_30'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_30 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_31'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_31 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_32'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_32 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_33'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_33 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_34'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_34 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_35'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_35 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_36'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_36 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_37'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_37 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_38'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_38 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_39'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_39 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_40'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_40 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_41'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_41 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_42'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_42 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_43'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_43 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_44'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_44 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_45'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_45 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_46'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_46 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_47'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_47 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_48'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_48 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_49'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_49 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_50'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_50 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_51'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_51 # type: ignore # mutmut generated
mutants_xǁPreflightHealthCheckerǁcheck_all__mutmut['xǁPreflightHealthCheckerǁcheck_all__mutmut_52'] = PreflightHealthChecker.xǁPreflightHealthCheckerǁcheck_all__mutmut_52 # type: ignore # mutmut generated
