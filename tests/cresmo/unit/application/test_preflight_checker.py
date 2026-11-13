"""Unit tests for PreflightHealthChecker and PreflightProbeAdapter.

Tests configuration, directory writability via PreflightProbePort, binary dependencies,
active HTTP probes, fail-fast invariants, and telemetry warnings per ADR-014 and SPEC-002.
"""

from __future__ import annotations

import os
import urllib.error
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from cresmo.application.ports.preflight import PreflightProbePort
from cresmo.application.services.preflight import (
    PreflightHealthChecker,
    PreflightResult,
)
from cresmo.domain.exceptions import PreflightError
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import (
    PreflightProbeAdapter,
    probe_http_endpoint,
)


class FakePreflightProbe(PreflightProbePort):
    """Hermetic in-memory PreflightProbePort fake with zero OS/network I/O."""

    def __init__(
        self,
        *,
        writable_paths: set[Path] | None = None,
        unwritable_paths: set[Path] | None = None,
        dir_errors: dict[Path, OSError] | None = None,
        binaries: set[str] | None = None,
        http_responses: dict[str, bool] | None = None,
        default_http_ok: bool = True,
    ) -> None:
        self.created_dirs: list[Path] = []
        self.http_calls: list[tuple[str, float]] = []
        self.writable_paths = writable_paths
        self.unwritable_paths = unwritable_paths or set()
        self.dir_errors = dir_errors or {}
        self.binaries = binaries if binaries is not None else {"ffmpeg"}
        self.http_responses = http_responses or {}
        self.default_http_ok = default_http_ok

    def ensure_directory(self, path: Path) -> None:
        if path in self.dir_errors:
            raise self.dir_errors[path]
        self.created_dirs.append(path)

    def is_writable(self, path: Path) -> bool:
        if path in self.unwritable_paths:
            return False
        if self.writable_paths is not None:
            return path in self.writable_paths
        return True

    def executable_exists(self, binary_name: str) -> bool:
        return binary_name in self.binaries

    def probe_http(self, url: str, timeout_seconds: float = 1.0) -> bool:
        self.http_calls.append((url, timeout_seconds))
        return self.http_responses.get(url, self.default_http_ok)


class TestPreflightHealthChecker:
    """Hermetic test suite for PreflightHealthChecker using PreflightProbePort."""

    def test_requires_probe_port(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match=r"^probe_port is required\.$"):
            PreflightHealthChecker(
                gemini_api_key=SecretStr("valid_key"),
                vault_dir=tmp_path / "vault",
                sqlite_ledger_path=tmp_path / "data" / "ledger.db",
                probe_port=None,
            )

    def test_default_check_ffmpeg_enabled_fails_when_binary_missing(self, tmp_path: Path) -> None:
        probe = FakePreflightProbe(binaries=set())
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            probe_port=probe,
        )
        result = checker.check_all()
        assert result.is_healthy is False
        assert any("ffmpeg" in err.lower() for err in result.errors)

    def test_healthy_environment_passes(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "data" / "ledger.db"
        probe = FakePreflightProbe()
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_test_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
            probe_port=probe,
        )
        result = checker.check_all()
        assert result.is_healthy
        assert result.errors == ()
        assert result.warnings == ()
        assert vault_dir in probe.created_dirs
        assert ledger_path.parent in probe.created_dirs
        result.assert_healthy()

    def test_missing_api_key_fails(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("   "),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
            probe_port=FakePreflightProbe(),
        )
        result = checker.check_all()
        assert not result.is_healthy
        assert any("GEMINI_API_KEY" in err for err in result.errors)
        with pytest.raises(PreflightError):
            result.assert_healthy()

    def test_missing_ffmpeg_binary_fails_when_enabled(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_test_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=True,
            probe_port=FakePreflightProbe(binaries=set()),
        )
        result = checker.check_all()
        assert not result.is_healthy
        assert "System binary 'ffmpeg' not found in PATH" in result.errors

    def test_found_ffmpeg_binary_passes_when_enabled(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_test_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=True,
            probe_port=FakePreflightProbe(binaries={"ffmpeg"}),
        )
        result = checker.check_all()
        assert result.is_healthy

    def test_unwritable_directory_fails(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_test_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
            probe_port=FakePreflightProbe(unwritable_paths={vault_dir}),
        )
        result = checker.check_all()
        assert not result.is_healthy
        assert f"Vault directory is not writable: '{vault_dir}'" in result.errors

    def test_preflight_result_with_warnings(self) -> None:
        res = PreflightResult(
            is_healthy=True,
            errors=(),
            warnings=("Langfuse unreachable; telemetry bypassed",),
        )
        assert res.is_healthy
        res.assert_healthy()

    def test_preflight_checker_probes(self, tmp_path: Path) -> None:
        probe_ok = FakePreflightProbe(default_http_ok=True)
        checker_ok = PreflightHealthChecker(
            gemini_api_key=SecretStr("key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "ledger.db",
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
            probe_port=probe_ok,
        )
        assert checker_ok.check_langfuse_probe("http://localhost:3000") is True
        assert checker_ok.check_ollama_probe("http://localhost:11434") is True

        probe_fail = FakePreflightProbe(default_http_ok=False)
        checker_fail = PreflightHealthChecker(
            gemini_api_key=SecretStr("key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "ledger.db",
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
            probe_port=probe_fail,
        )
        assert checker_fail.check_langfuse_probe("http://localhost:3000") is False
        assert checker_fail.check_ollama_probe("http://localhost:11434") is False

    def test_preflight_checker_url_normalization(self, tmp_path: Path) -> None:
        probe = FakePreflightProbe(default_http_ok=True)
        checker = PreflightHealthChecker(
            gemini_api_key="plain_str_key",
            vault_dir=str(tmp_path / "vault"),
            sqlite_ledger_path=str(tmp_path / "data" / "ledger.db"),
            check_ffmpeg=True,
            langfuse_host="http://localhost:3000/",
            ollama_base_url="http://localhost:11434/",
            probe_port=probe,
        )

        assert checker.check_langfuse_probe("http://localhost:3000/", timeout_seconds=2.5) is True
        assert probe.http_calls[-1] == ("http://localhost:3000/api/public/health", 2.5)

        assert checker.check_langfuse_probe("http://localhost:3000/") is True
        assert probe.http_calls[-1] == ("http://localhost:3000/api/public/health", 2.0)

        assert checker.check_ollama_probe("http://localhost:11434/", timeout_seconds=3.5) is True
        assert probe.http_calls[-1] == ("http://localhost:11434/api/version", 3.5)

        assert checker.check_ollama_probe("http://localhost:11434/") is True
        assert probe.http_calls[-1] == ("http://localhost:11434/api/version", 1.0)

        assert checker.check_langfuse_probe("http://localhost:3000/apiX") is True
        assert probe.http_calls[-1] == ("http://localhost:3000/apiX/api/public/health", 2.0)

        assert checker.check_ollama_probe("http://localhost:11434/apiX") is True
        assert probe.http_calls[-1] == ("http://localhost:11434/apiX/api/version", 1.0)

    def test_check_langfuse_localhost_fallback_to_127(self, tmp_path: Path) -> None:
        probe = FakePreflightProbe(
            http_responses={
                "http://localhost:3000/api/public/health": False,
                "http://127.0.0.1:3000/api/public/health": True,
            },
            default_http_ok=False,
        )
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "ledger.db",
            check_ffmpeg=False,
            probe_port=probe,
        )
        assert checker.check_langfuse_probe("http://localhost:3000") is True
        assert probe.http_calls == [
            ("http://localhost:3000/api/public/health", 2.0),
            ("http://127.0.0.1:3000/api/public/health", 2.0),
        ]
        assert checker.check_langfuse_probe("https://cloud.langfuse.com") is False

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
            probe_port=FakePreflightProbe(default_http_ok=False),
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
            probe_port=FakePreflightProbe(default_http_ok=True),
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
        probe = FakePreflightProbe(
            dir_errors={
                vault_dir: OSError("Disk failure"),
                ledger_path.parent: OSError("Disk failure"),
            }
        )
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
            probe_port=probe,
        )

        result = checker.check_all()
        assert not result.is_healthy
        assert f"Cannot access vault directory '{vault_dir}': Disk failure" in result.errors
        assert (
            f"Cannot access SQLite ledger directory '{ledger_path.parent}': Disk failure"
            in result.errors
        )

    def test_check_all_ledger_directory_unwritable(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"
        ledger_path = tmp_path / "ledger" / "db.sqlite"
        probe = FakePreflightProbe(unwritable_paths={ledger_path.parent})
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=vault_dir,
            sqlite_ledger_path=ledger_path,
            check_ffmpeg=False,
            probe_port=probe,
        )

        result = checker.check_all()
        assert not result.is_healthy
        assert f"SQLite ledger directory is not writable: '{ledger_path.parent}'" in result.errors

    def test_check_all_api_key_variants(self, tmp_path: Path) -> None:
        c1 = PreflightHealthChecker(
            gemini_api_key="valid_plain_str",
            vault_dir=tmp_path / "vault1",
            sqlite_ledger_path=tmp_path / "db1.sqlite",
            check_ffmpeg=False,
            probe_port=FakePreflightProbe(),
        )
        assert c1.check_all().is_healthy is True

        c2 = PreflightHealthChecker(
            gemini_api_key=None,
            vault_dir=tmp_path / "vault2",
            sqlite_ledger_path=tmp_path / "db2.sqlite",
            check_ffmpeg=False,
            probe_port=FakePreflightProbe(),
        )
        res2 = c2.check_all()
        assert res2.is_healthy is False
        assert "Missing required GEMINI_API_KEY credential" in res2.errors

        c3 = PreflightHealthChecker(
            gemini_api_key="   ",
            vault_dir=tmp_path / "vault3",
            sqlite_ledger_path=tmp_path / "db3.sqlite",
            check_ffmpeg=False,
            probe_port=FakePreflightProbe(),
        )
        res3 = c3.check_all()
        assert res3.is_healthy is False
        assert "Missing required GEMINI_API_KEY credential" in res3.errors

    def test_assert_healthy_multiple_errors_message(self) -> None:
        res = PreflightResult(
            is_healthy=False,
            errors=("First error", "Second error"),
        )
        with pytest.raises(PreflightError) as exc_info:
            res.assert_healthy()
        assert "Preflight health check failed: First error; Second error" == str(exc_info.value)

    def test_check_all_telemetry_and_ollama_defaults(self, tmp_path: Path) -> None:
        checker = PreflightHealthChecker(
            gemini_api_key=SecretStr("valid_key"),
            vault_dir=tmp_path / "vault",
            sqlite_ledger_path=tmp_path / "data" / "ledger.db",
            check_ffmpeg=False,
            langfuse_host="http://localhost:3000",
            ollama_base_url="http://localhost:11434",
            probe_port=FakePreflightProbe(),
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


class TestPreflightProbeAdapter:
    """Unit tests for infrastructure PreflightProbeAdapter and probe_http_endpoint."""

    def test_ensure_directory_is_writable_and_executable_exists(self, tmp_path: Path) -> None:
        adapter = PreflightProbeAdapter()
        deep_dir = tmp_path / "deep" / "nested" / "vault"
        adapter.ensure_directory(deep_dir)
        assert deep_dir.exists()
        adapter.ensure_directory(deep_dir)
        assert adapter.is_writable(deep_dir) is True

        with patch("os.access", return_value=False) as mock_access:
            assert adapter.is_writable(deep_dir) is False
            mock_access.assert_called_once_with(deep_dir, os.W_OK)

        with patch("shutil.which", return_value="/usr/bin/ffmpeg") as mock_which:
            assert adapter.executable_exists("ffmpeg") is True
            mock_which.assert_called_once_with("ffmpeg")

        with patch("shutil.which", return_value=None):
            assert adapter.executable_exists("ffmpeg") is False

    def test_probe_http_delegates_to_probe_http_endpoint(self) -> None:
        adapter = PreflightProbeAdapter()
        with patch(
            "cresmo.infrastructure.adapters.system.preflight_probe_adapter.probe_http_endpoint",
            return_value=True,
        ) as mock_probe:
            assert adapter.probe_http("http://localhost:3000/health", timeout_seconds=2.5) is True
            mock_probe.assert_called_once_with("http://localhost:3000/health", timeout_seconds=2.5)

    def test_probe_http_endpoint_success_and_failures(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            assert (
                probe_http_endpoint("http://localhost:3000/api/public/health", timeout_seconds=0.5)
                is True
            )

        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("Refused")):
            assert not probe_http_endpoint(
                "http://localhost:3000/api/public/health", timeout_seconds=0.1
            )

        with patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out")):
            assert not probe_http_endpoint("http://localhost:3000/api/public/health")

        mock_resp_500 = MagicMock()
        mock_resp_500.status = 500
        mock_resp_500.__enter__.return_value = mock_resp_500
        with patch("urllib.request.urlopen", return_value=mock_resp_500):
            assert not probe_http_endpoint("http://localhost:3000/api/public/health")

    def test_probe_http_endpoint_request_details(self) -> None:
        import urllib.request

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        recorded_headers: dict[str, Any] = {}
        orig_req = urllib.request.Request

        def mock_req(url: str, method: str = "GET", headers: dict[str, Any] | None = None) -> Any:
            if headers:
                recorded_headers.update(headers)
            return orig_req(url, method=method, headers=headers or {})

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

    def test_probe_http_endpoint_status_boundary_and_exception_matrix(self) -> None:
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
