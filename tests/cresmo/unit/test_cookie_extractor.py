"""Unit tests for YouTube cookie extraction adapter and CLI subcommand."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cresmo.infrastructure.adapters.cookie_extractor import (
    ensure_cookies_file,
    export_cookies_from_browser,
    has_valid_auth_cookies,
)
from cresmo.presentation.cli import main
from cresmo.presentation.exit_codes import EXIT_INGESTION_ERROR, EXIT_SUCCESS


class TestCookieExtractor:
    """Validate Netscape cookie validation and extraction behavior."""

    def test_has_valid_auth_cookies_returns_false_for_missing_or_empty_file(
        self, tmp_path: Path
    ) -> None:
        missing_file = tmp_path / "non_existent.txt"
        assert not has_valid_auth_cookies(missing_file)

        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("too short")
        assert not has_valid_auth_cookies(empty_file)

    def test_has_valid_auth_cookies_returns_true_for_auth_tokens(self, tmp_path: Path) -> None:
        valid_cookie_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSID\tsample_session_token",
        ]
        valid_cookie_file.write_text("\n".join(lines))
        assert has_valid_auth_cookies(valid_cookie_file)

    def test_has_valid_auth_cookies_returns_false_if_no_auth_tokens(self, tmp_path: Path) -> None:
        guest_cookie_file = tmp_path / "guest_cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tPREF\tf1=50000000",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tYSC\txyz12345",
        ]
        guest_cookie_file.write_text("\n".join(lines))
        assert not has_valid_auth_cookies(guest_cookie_file)

    def test_export_cookies_from_browser_handles_exception_gracefully(self, tmp_path: Path) -> None:
        out_file = tmp_path / "extracted.txt"
        with patch("yt_dlp.cookies.extract_cookies_from_browser", side_effect=Exception("DB locked")):
            result = export_cookies_from_browser("firefox", out_file, verbose=False)
            assert result is False
            assert not out_file.exists()

    def test_ensure_cookies_file_reuses_valid_existing_file(self, tmp_path: Path) -> None:
        existing_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSID\tsample_session_token",
        ]
        existing_file.write_text("\n".join(lines))

        with patch("cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser") as mock_exp:
            resolved = ensure_cookies_file(existing_file, browser="firefox", max_age_hours=24)
            assert resolved == existing_file
            mock_exp.assert_not_called()


class TestExportCookiesCLICommand:
    """Validate cresmo export-cookies CLI command."""

    def test_export_cookies_cli_success(self, tmp_path: Path) -> None:
        out_file = tmp_path / "test_cookies.txt"
        with patch(
            "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
            return_value=True,
        ) as mock_exp:
            exit_code = main(["export-cookies", "--browser", "firefox", "--output", str(out_file), "--force"])
            assert exit_code == EXIT_SUCCESS
            mock_exp.assert_called_once()

    def test_export_cookies_cli_failure_returns_ingestion_error(self, tmp_path: Path) -> None:
        out_file = tmp_path / "test_cookies.txt"
        with patch(
            "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
            return_value=False,
        ):
            exit_code = main(["export-cookies", "--browser", "chrome", "--output", str(out_file), "--force"])
            assert exit_code == EXIT_INGESTION_ERROR
