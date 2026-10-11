"""Unit tests for 'cresmo export-cookies' presentation command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-004: Native Media Ingestion Decommissioning
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.infrastructure.adapters.cookie_extractor import SUPPORTED_BROWSERS
from cresmo.presentation.cli import main
from cresmo.presentation.commands.export_cookies import (
    handle_export_cookies,
    register_subparser,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_SUCCESS,
)


class TestExportCookiesCommand:
    """Test suite for cresmo export-cookies presentation command."""

    def test_register_subparser(self) -> None:
        """Verify export-cookies subparser configuration, argument flags, choices, and defaults."""
        mock_subparsers = MagicMock()
        mock_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_parser

        register_subparser(mock_subparsers)

        mock_subparsers.add_parser.assert_called_once_with(
            "export-cookies",
            help="Extract and validate YouTube authentication cookies from installed web browsers",
        )
        assert mock_parser.add_argument.call_count == 4
        mock_parser.add_argument.assert_any_call(
            "--browser",
            choices=list(SUPPORTED_BROWSERS),
            default="firefox",
            help="Target browser to extract cookies from (default: firefox)",
        )
        mock_parser.add_argument.assert_any_call(
            "--output",
            type=Path,
            default=None,
            help="Destination path for Netscape cookies file (default: data/cookies.txt)",
        )
        mock_parser.add_argument.assert_any_call(
            "--require-auth",
            action="store_true",
            default=False,
            help="Strictly require authenticated session cookies (SID, SSID, LOGIN_INFO)",
        )
        mock_parser.add_argument.assert_any_call(
            "--force",
            action="store_true",
            default=False,
            help="Force re-extraction even if a valid cookie file already exists",
        )
        mock_parser.set_defaults.assert_called_once_with(handler=handle_export_cookies)

    def test_cookies_already_exist_and_valid_without_force(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify existing valid cookie file skips extraction without --force and returns EXIT_SUCCESS."""
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="firefox",
            output=cookie_file,
            require_auth=False,
            force=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.has_valid_auth_cookies",
                return_value=True,
            ) as mock_has_valid,
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser"
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_SUCCESS
            mock_has_valid.assert_called_once_with(cookie_file.resolve())
            mock_export.assert_not_called()

            captured = capsys.readouterr()
            expected_msg = (
                f"[cookies] Valid authenticated cookies already exist: {cookie_file.resolve()} "
                f"({cookie_file.stat().st_size} bytes). Use --force to re-extract.\n"
            )
            assert captured.out == expected_msg
            assert captured.err == ""

    def test_cookies_already_exist_and_valid_with_force_re_extracts(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify --force overrides existing valid cookie check and triggers export."""
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="chrome",
            output=cookie_file,
            require_auth=True,
            force=True,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.has_valid_auth_cookies",
                return_value=True,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=True,
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_SUCCESS
            mock_export.assert_called_once_with(
                browser="chrome",
                output_file=cookie_file.resolve(),
                require_auth=True,
                verbose=True,
            )

            captured = capsys.readouterr()
            assert (
                f"[cookies] Extracting YouTube cookies from browser 'chrome'...\n"
                f"[cookies] Successfully saved cookies to: {cookie_file.resolve()}\n"
            ) == captured.out
            assert captured.err == ""

    def test_cookies_already_exist_but_invalid_triggers_extraction(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify invalid existing cookie file triggers re-extraction even without --force."""
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("invalid cookies", encoding="utf-8")

        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="brave",
            output=cookie_file,
            require_auth=False,
            force=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.has_valid_auth_cookies",
                return_value=False,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=True,
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_SUCCESS
            mock_export.assert_called_once_with(
                browser="brave",
                output_file=cookie_file.resolve(),
                require_auth=False,
                verbose=True,
            )

            captured = capsys.readouterr()
            assert (
                f"[cookies] Extracting YouTube cookies from browser 'brave'...\n"
                f"[cookies] Successfully saved cookies to: {cookie_file.resolve()}\n"
            ) == captured.out

    def test_extraction_failure_returns_ingestion_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify export failure outputs prescriptive guidance and returns EXIT_INGESTION_ERROR (5)."""
        cookie_file = tmp_path / "missing_cookies.txt"

        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="chromium",
            output=cookie_file,
            require_auth=True,
            force=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=False,
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_INGESTION_ERROR
            mock_export.assert_called_once_with(
                browser="chromium",
                output_file=cookie_file.resolve(),
                require_auth=True,
                verbose=True,
            )

            captured = capsys.readouterr()
            assert (
                captured.out == "[cookies] Extracting YouTube cookies from browser 'chromium'...\n"
            )
            assert captured.err == (
                "[cookies] ERROR: Failed to extract YouTube cookies from 'chromium'.\n"
                "[cookies] Action required: Please open Chromium, log in to YouTube, "
                "and then run 'cresmo export-cookies --browser chromium'.\n"
            )

    def test_unhandled_exception_returns_usage_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify unexpected runtime exceptions write to stderr and return EXIT_CONFIG_OR_USAGE_ERROR (2)."""
        args = argparse.Namespace(
            browser="firefox",
            output=tmp_path / "cookies.txt",
            require_auth=False,
            force=False,
        )

        with patch(
            "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
            side_effect=RuntimeError("Corrupted config store"),
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_CONFIG_OR_USAGE_ERROR

            captured = capsys.readouterr()
            assert captured.out == ""
            assert (
                captured.err == "[cookies] Error during cookie extraction: Corrupted config store\n"
            )

    def test_output_fallback_to_settings_cookies_file(self, tmp_path: Path) -> None:
        """Verify output path falls back to settings.cookies_file when --output is None."""
        target_cookies = tmp_path / "custom" / "my_cookies.txt"
        mock_settings = MagicMock()
        mock_settings.cookies_file = target_cookies
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="edge",
            output=None,
            require_auth=False,
            force=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=True,
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_SUCCESS
            mock_export.assert_called_once_with(
                browser="edge",
                output_file=target_cookies.resolve(),
                require_auth=False,
                verbose=True,
            )

    def test_output_fallback_to_data_dir_cookies_txt(self, tmp_path: Path) -> None:
        """Verify output path falls back to settings.data_dir / 'cookies.txt' when both args and setting are None."""
        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        args = argparse.Namespace(
            browser="firefox",
            output=None,
            require_auth=False,
            force=False,
        )

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=True,
            ) as mock_export,
        ):
            code = handle_export_cookies(args)
            assert code == EXIT_SUCCESS
            mock_export.assert_called_once_with(
                browser="firefox",
                output_file=(tmp_path / "cookies.txt").resolve(),
                require_auth=False,
                verbose=True,
            )

    def test_main_cli_dispatch_export_cookies(self, tmp_path: Path) -> None:
        """Verify main entrypoint invokes export-cookies and executes handler successfully."""
        cookie_path = tmp_path / "cli_cookies.txt"
        mock_settings = MagicMock()
        mock_settings.cookies_file = None
        mock_settings.data_dir = tmp_path

        with (
            patch(
                "cresmo.presentation.commands.export_cookies.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
                return_value=True,
            ) as mock_export,
        ):
            code = main(
                [
                    "export-cookies",
                    "--browser",
                    "chrome",
                    "--output",
                    str(cookie_path),
                    "--require-auth",
                    "--force",
                ]
            )
            assert code == EXIT_SUCCESS
            mock_export.assert_called_once_with(
                browser="chrome",
                output_file=cookie_path.resolve(),
                require_auth=True,
                verbose=True,
            )
