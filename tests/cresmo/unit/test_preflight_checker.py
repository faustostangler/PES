"""Unit tests for PreflightHealthChecker.

Verifies fast environmental diagnostic checks (credentials, directory permissions,
binary dependencies) and fail-fast exception propagation per SPEC-003.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from cresmo.application.services.preflight import (
    PreflightHealthChecker,
)
from cresmo.domain.exceptions import PreflightError


class TestPreflightHealthChecker:
    """Test suite for PreflightHealthChecker."""

    def test_healthy_environment_passes(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "data" / "ledger.db"

        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_secret_key_123"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
        )

        result = checker.check_all()
        assert result.is_healthy
        assert len(result.errors) == 0
        result.assert_healthy()

    def test_missing_api_key_fails(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr(""),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
        )

        result = checker.check_all()
        assert not result.is_healthy
        assert any("GEMINI_API_KEY" in err for err in result.errors)

        with pytest.raises(PreflightError, match="GEMINI_API_KEY"):
            result.assert_healthy()

    def test_missing_ffmpeg_binary_fails_when_enabled(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=True,
        )

        with patch("shutil.which", return_value=None):
            result = checker.check_all()
            assert not result.is_healthy
            assert any("ffmpeg" in err for err in result.errors)

            with pytest.raises(PreflightError, match="ffmpeg"):
                result.assert_healthy()

    def test_found_ffmpeg_binary_passes_when_enabled(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=True,
        )

        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            result = checker.check_all()
            assert result.is_healthy

    def test_unwritable_directory_fails(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
        )

        with patch("os.access", return_value=False):
            result = checker.check_all()
            assert not result.is_healthy
            assert any("not writable" in err for err in result.errors)
