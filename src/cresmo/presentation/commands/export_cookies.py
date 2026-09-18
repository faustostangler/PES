"""Command handler for cresmo export-cookies.

Extracts and validates YouTube authentication cookies directly from installed browsers
(Firefox, Chrome, Chromium, Brave, Edge) into Netscape format files.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-004: Native Media Ingestion Decommissioning
    - SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cresmo.infrastructure.adapters.cookie_extractor import (
    SUPPORTED_BROWSERS,
    export_cookies_from_browser,
    has_valid_auth_cookies,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'export-cookies' subcommand parser with argument options.

    Args:
        subparsers: Root CLI subparsers action object.
    """
    cookie_parser = subparsers.add_parser(
        "export-cookies",
        help="Extract and validate YouTube authentication cookies from installed web browsers",
    )
    cookie_parser.add_argument(
        "--browser",
        choices=list(SUPPORTED_BROWSERS),
        default="firefox",
        help="Target browser to extract cookies from (default: firefox)",
    )
    cookie_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Destination path for Netscape cookies file (default: data/cookies.txt)",
    )
    cookie_parser.add_argument(
        "--require-auth",
        action="store_true",
        default=False,
        help="Strictly require authenticated session cookies (SID, SSID, LOGIN_INFO)",
    )
    cookie_parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force re-extraction even if a valid cookie file already exists",
    )
    cookie_parser.set_defaults(handler=handle_export_cookies)


def handle_export_cookies(args: argparse.Namespace) -> int:
    """Extract YouTube session cookies from browser into target Netscape file.

    Args:
        args: Parsed CLI argument namespace containing browser name, output path, and flags.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        output_file = args.output or settings.cookies_file or (settings.data_dir / "cookies.txt")
        output_path = Path(output_file).resolve()

        if output_path.exists() and not args.force and has_valid_auth_cookies(output_path):
            sys.stdout.write(
                f"[cookies] Valid authenticated cookies already exist: {output_path} "
                f"({output_path.stat().st_size} bytes). Use --force to re-extract.\n"
            )
            return EXIT_SUCCESS

        sys.stdout.write(f"[cookies] Extracting YouTube cookies from browser '{args.browser}'...\n")
        success = export_cookies_from_browser(
            browser=args.browser,
            output_file=output_path,
            require_auth=args.require_auth,
            verbose=True,
        )

        if not success:
            sys.stderr.write(
                f"[cookies] ERROR: Failed to extract YouTube cookies from '{args.browser}'.\n"
                f"[cookies] Action required: Please open {args.browser.capitalize()}, log in to YouTube, "
                f"and then run 'cresmo export-cookies --browser {args.browser}'.\n"
            )
            return EXIT_INGESTION_ERROR

        sys.stdout.write(f"[cookies] Successfully saved cookies to: {output_path}\n")
        return EXIT_SUCCESS

    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[cookies] Error during cookie extraction: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
