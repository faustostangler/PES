"""Unit tests for PreflightHealthChecker.

Verifies fast environmental diagnostic checks (credentials, directory permissions,
binary dependencies) and fail-fast exception propagation per SPEC-003.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

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
        )

        def mock_which(cmd: str | None) -> str | None:
            if cmd == "ffmpeg":
                return None
            return "/usr/bin/some_binary"

        with patch("shutil.which", side_effect=mock_which):
            result = checker.check_all()
            assert not result.is_healthy
            assert result.errors == ("System binary 'ffmpeg' not found in PATH",)

            with pytest.raises(PreflightError, match="System binary 'ffmpeg' not found in PATH"):
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

    def test_preflight_result_with_warnings(self) -> None:
        from cresmo.application.services.preflight import PreflightResult

        result = PreflightResult(
            is_healthy=True,
            errors=(),
            warnings=("Langfuse unreachable, telemetry bypassed",),
        )
        assert result.is_healthy
        assert len(result.warnings) == 1
        assert "Langfuse" in result.warnings[0]
        # Should not raise
        result.assert_healthy()

    def test_probe_http_endpoint_success(self) -> None:
        from cresmo.application.services.preflight import probe_http_endpoint

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            assert probe_http_endpoint(
                "http://localhost:3000/api/public/health", timeout_seconds=0.5
            )

    def test_probe_http_endpoint_connection_refused(self) -> None:
        import urllib.error

        from cresmo.application.services.preflight import probe_http_endpoint

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("[Errno 111] Connection refused"),
        ):
            assert not probe_http_endpoint(
                "http://localhost:3000/api/public/health", timeout_seconds=0.5
            )

    def test_probe_http_endpoint_timeout(self) -> None:
        from cresmo.application.services.preflight import probe_http_endpoint

        with patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out")):
            assert not probe_http_endpoint(
                "http://localhost:3000/api/public/health", timeout_seconds=0.5
            )

    def test_probe_http_endpoint_server_error(self) -> None:
        from cresmo.application.services.preflight import probe_http_endpoint

        mock_resp = MagicMock()
        mock_resp.status = 503
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            assert not probe_http_endpoint(
                "http://localhost:3000/api/public/health", timeout_seconds=0.5
            )

    def test_preflight_checker_probes(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
        )

        with patch("cresmo.application.services.preflight.probe_http_endpoint", return_value=True):
            assert checker.check_langfuse_probe("http://localhost:3000") is True
            assert checker.check_ollama_probe("http://localhost:11434") is True

        with patch("cresmo.application.services.preflight.probe_http_endpoint", return_value=False):
            assert checker.check_langfuse_probe("http://localhost:3000") is False
            assert checker.check_ollama_probe("http://localhost:11434") is False

    def test_probe_http_endpoint_request_details(self) -> None:
        import urllib.request

        from cresmo.application.services.preflight import probe_http_endpoint

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        orig_req = urllib.request.Request
        recorded_headers = None

        def mock_req(
            url: str, *args: Any, headers: dict[str, str] | None = None, **kwargs: Any
        ) -> Any:
            nonlocal recorded_headers
            recorded_headers = headers
            if headers is not None:
                return orig_req(url, *args, headers=headers, **kwargs)
            return orig_req(url, *args, **kwargs)

        with (
            patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen,
            patch("urllib.request.Request", side_effect=mock_req),
        ):
            res = probe_http_endpoint("http://localhost:3000/api/public/health")
            assert res is True
            assert mock_urlopen.call_count == 1
            call_req = mock_urlopen.call_args[0][0]
            assert mock_urlopen.call_args[1]["timeout"] == 1.0
            assert call_req.full_url == "http://localhost:3000/api/public/health"
            assert call_req.method == "GET"
            assert call_req.get_method() == "GET"
            assert recorded_headers == {"User-Agent": "CresmoPreflightProbe/1.0"}

    def test_probe_http_endpoint_status_boundary(self) -> None:
        from cresmo.application.services.preflight import probe_http_endpoint

        mock_resp_499 = MagicMock()
        mock_resp_499.status = 499
        mock_resp_499.__enter__.return_value = mock_resp_499

        with patch("urllib.request.urlopen", return_value=mock_resp_499):
            assert probe_http_endpoint("http://example.com", timeout_seconds=1.0) is True

        mock_resp_500 = MagicMock()
        mock_resp_500.status = 500
        mock_resp_500.__enter__.return_value = mock_resp_500

        with patch("urllib.request.urlopen", return_value=mock_resp_500):
            assert probe_http_endpoint("http://example.com", timeout_seconds=1.0) is False

    def test_probe_http_endpoint_exception_matrix(self) -> None:
        import urllib.error

        from cresmo.application.services.preflight import probe_http_endpoint

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError(
                "http://example.com", 500, "Error", cast(Any, {}), None
            ),
        ):
            assert probe_http_endpoint("http://example.com") is False

        with patch("urllib.request.urlopen", side_effect=OSError("Network unreachable")):
            assert probe_http_endpoint("http://example.com") is False

        with patch("urllib.request.urlopen", side_effect=ValueError("Unexpected")):
            assert probe_http_endpoint("http://example.com") is False

    def test_preflight_checker_url_normalization(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key="plain_str_key",
            vault_dir=str(tmp_path / "vault"),
            sqlite_ledger_path=str(tmp_path / "data" / "ledger.db"),
            check_ffmpeg=True,
            langfuse_host="http://localhost:3000/",
            ollama_base_url="http://localhost:11434/",
        )

        with patch(
            "cresmo.application.services.preflight.probe_http_endpoint", return_value=True
        ) as mock_probe:
            res_lf = checker.check_langfuse_probe("http://localhost:3000/", timeout_seconds=2.5)
            assert res_lf is True
            mock_probe.assert_called_with(
                "http://localhost:3000/api/public/health", timeout_seconds=2.5
            )

            # Test default timeout_seconds in check_langfuse_probe
            mock_probe.reset_mock()
            res_lf_def = checker.check_langfuse_probe("http://localhost:3000/")
            assert res_lf_def is True
            mock_probe.assert_called_with(
                "http://localhost:3000/api/public/health", timeout_seconds=1.0
            )

            mock_probe.reset_mock()
            res_ol = checker.check_ollama_probe("http://localhost:11434/", timeout_seconds=3.5)
            assert res_ol is True
            mock_probe.assert_called_with("http://localhost:11434/api/version", timeout_seconds=3.5)

            # Test default timeout_seconds in check_ollama_probe
            mock_probe.reset_mock()
            res_ol_def = checker.check_ollama_probe("http://localhost:11434/")
            assert res_ol_def is True
            mock_probe.assert_called_with("http://localhost:11434/api/version", timeout_seconds=1.0)

            # Test trailing X is NOT stripped (kills rstrip('XX/XX') mutant)
            mock_probe.reset_mock()
            assert checker.check_langfuse_probe("http://localhost:3000/apiX") is True
            mock_probe.assert_called_with(
                "http://localhost:3000/apiX/api/public/health", timeout_seconds=1.0
            )

            mock_probe.reset_mock()
            assert checker.check_ollama_probe("http://localhost:11434/apiX") is True
            mock_probe.assert_called_with(
                "http://localhost:11434/apiX/api/version", timeout_seconds=1.0
            )

    def test_check_all_telemetry_and_ollama_probe_failure(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "data" / "ledger.db"

        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
        )

        with (
            patch.object(checker, "check_langfuse_probe", return_value=False) as mock_lf,
            patch.object(checker, "check_ollama_probe", return_value=False) as mock_ol,
        ):
            result = checker.check_all(probe_telemetry=True, probe_ollama=True)
            mock_lf.assert_called_once_with("http://localhost:3000")
            mock_ol.assert_called_once_with("http://localhost:11434")

            assert not result.is_healthy
            assert (
                "Langfuse server at 'http://localhost:3000' is unreachable. Telemetry disabled."
                in result.warnings
            )
            assert (
                "Local Ollama daemon at 'http://localhost:11434' is unreachable." in result.errors
            )

    def test_check_all_telemetry_and_ollama_probe_success(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "data" / "ledger.db"

        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
        )

        with (
            patch.object(checker, "check_langfuse_probe", return_value=True),
            patch.object(checker, "check_ollama_probe", return_value=True),
        ):
            result = checker.check_all(probe_telemetry=True, probe_ollama=True)
            assert result.is_healthy
            assert len(result.warnings) == 0
            assert len(result.errors) == 0

    def test_check_all_oserror_on_vault_and_ledger_directories(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "bad_vault"
        ledger_path = tmp_path / "bad_ledger" / "db.sqlite"
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
        )

        orig_mkdir = Path.mkdir

        def selective_mkdir(
            self: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False
        ) -> None:
            if "bad_vault" in str(self) or "bad_ledger" in str(self):
                raise OSError("Disk failure")
            orig_mkdir(self, mode=mode, parents=parents, exist_ok=exist_ok)

        with patch.object(Path, "mkdir", selective_mkdir):
            result = checker.check_all()
            assert not result.is_healthy
            assert any(
                f"Cannot access vault directory '{vault_dir}': Disk failure" == err
                for err in result.errors
            )
            assert any(
                f"Cannot access SQLite ledger directory '{ledger_path.parent}': Disk failure" == err
                for err in result.errors
            )

    def test_check_all_ledger_directory_unwritable(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "ledger" / "db.sqlite"
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
        )

        def mock_access(path: object, mode: int) -> bool:
            return str(path).endswith("vault")

        with patch("os.access", side_effect=mock_access):
            result = checker.check_all()
            assert not result.is_healthy
            assert any(
                f"SQLite ledger directory is not writable: '{ledger_path.parent}'" == err
                for err in result.errors
            )

    def test_check_all_api_key_variants(self, tmp_path: Path) -> None:
        c1 = PreflightHealthChecker(
            gemini_api_key="valid_plain_str",
            vault_dir=tmp_path / "vault1",
            sqlite_ledger_path=tmp_path / "db1.sqlite",
            check_ffmpeg=False,
        )
        assert c1.check_all().is_healthy is True

        c2 = PreflightHealthChecker(
            gemini_api_key=None,
            vault_dir=tmp_path / "vault2",
            sqlite_ledger_path=tmp_path / "db2.sqlite",
            check_ffmpeg=False,
        )
        res2 = c2.check_all()
        assert res2.is_healthy is False
        assert "Missing required GEMINI_API_KEY credential" in res2.errors

        c3 = PreflightHealthChecker(
            gemini_api_key="   ",
            vault_dir=tmp_path / "vault3",
            sqlite_ledger_path=tmp_path / "db3.sqlite",
            check_ffmpeg=False,
        )
        res3 = c3.check_all()
        assert res3.is_healthy is False
        assert "Missing required GEMINI_API_KEY credential" in res3.errors

    def test_assert_healthy_multiple_errors_message(self) -> None:
        from cresmo.application.services.preflight import PreflightResult

        res = PreflightResult(
            is_healthy=False,
            errors=("First error", "Second error"),
        )
        with pytest.raises(PreflightError) as exc_info:
            res.assert_healthy()
        assert "Preflight health check failed: First error; Second error" == str(exc_info.value)

    def test_check_all_mkdir_parents_and_exist_ok(self, tmp_path: Path) -> None:
        deep_vault = tmp_path / "deep" / "nested" / "vault"
        deep_ledger = tmp_path / "deep_ledger" / "nested" / "ledger.db"

        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=deep_vault,
            sqlite_ledger_path=deep_ledger,
            check_ffmpeg=False,
        )
        res1 = checker.check_all()
        assert res1.is_healthy is True
        assert deep_vault.exists()
        assert deep_ledger.parent.exists()

        # Existing directories require exist_ok=True
        res2 = checker.check_all()
        assert res2.is_healthy is True

    def test_check_all_telemetry_and_ollama_defaults(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
        )
        with (
            patch.object(
                checker,
                "check_langfuse_probe",
                side_effect=AssertionError("Should not probe telemetry by default"),
            ),
            patch.object(
                checker,
                "check_ollama_probe",
                side_effect=AssertionError("Should not probe ollama by default"),
            ),
        ):
            res = checker.check_all()
            assert res.is_healthy is True
            assert len(res.warnings) == 0
            assert len(res.errors) == 0
