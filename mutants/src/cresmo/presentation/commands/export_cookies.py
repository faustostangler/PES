"""Command handler for cresmo export-cookies.

Extracts and validates YouTube authentication cookies directly from installed browsers
(Firefox, Chrome, Chromium, Brave, Edge) into Netscape format files.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-004: Native Media Ingestion Decommissioning
    - SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from cresmo.infrastructure.adapters.cookie_extractor import (
    export_cookies_from_browser,
    has_valid_auth_cookies,
)
from cresmo.presentation.composition import resolve_shared_settings
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_SUCCESS,
)


def export_cookies(
    browser: Annotated[
        str,
        typer.Option(
            "--browser",
            help="Target browser to extract cookies from (default: firefox)",
        ),
    ] = "firefox",
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            resolve_path=True,
            help="Destination path for Netscape cookies file (default: data/cookies.txt)",
        ),
    ] = None,
    require_auth: Annotated[
        bool,
        typer.Option(
            "--require-auth",
            help="Strictly require authenticated session cookies (SID, SSID, LOGIN_INFO)",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Force re-extraction even if a valid cookie file already exists",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Extract YouTube session cookies from browser into target Netscape file."""
    _ = verbose
    code = handle_export_cookies(
        None,
        browser=browser,
        output=output,
        require_auth=require_auth,
        force=force,
    )
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_export_cookies(
    args: Any = None,
    browser: str = "firefox",
    output: Path | None = None,
    require_auth: bool = False,
    force: bool = False,
) -> int:
    """Extract YouTube session cookies from browser into target Netscape file.

    Args:
        args: Parsed CLI argument namespace or None.
        browser: Browser name string.
        output: Destination output Path or None.
        require_auth: Strictly require authenticated cookies flag.
        force: Force re-extraction flag.

    Returns:
        Process exit code integer.
    """
    target_browser = getattr(args, "browser", browser) if args is not None else browser
    target_output = getattr(args, "output", output) if args is not None else output
    target_require_auth = (
        getattr(args, "require_auth", require_auth) if args is not None else require_auth
    )
    target_force = getattr(args, "force", force) if args is not None else force

    try:
        settings = resolve_shared_settings()
        output_file = target_output or settings.cookies_file or (settings.data_dir / "cookies.txt")
        output_path = Path(output_file).resolve()

        if output_path.exists() and not target_force and has_valid_auth_cookies(output_path):
            sys.stdout.write(
                f"[cookies] Valid authenticated cookies already exist: {output_path} "
                f"({output_path.stat().st_size} bytes). Use --force to re-extract.\n"
            )
            return EXIT_SUCCESS

        sys.stdout.write(
            f"[cookies] Extracting YouTube cookies from browser '{target_browser}'...\n"
        )
        success = export_cookies_from_browser(
            browser=target_browser,
            output_file=output_path,
            require_auth=target_require_auth,
            verbose=True,
        )

        if not success:
            sys.stderr.write(
                f"[cookies] ERROR: Failed to extract YouTube cookies from '{target_browser}'.\n"
                f"[cookies] Action required: Please open {target_browser.capitalize()}, log in to YouTube, "
                f"and then run 'cresmo export-cookies --browser {target_browser}'.\n"
            )
            return EXIT_INGESTION_ERROR

        sys.stdout.write(f"[cookies] Successfully saved cookies to: {output_path}\n")
        return EXIT_SUCCESS

    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[cookies] Error during cookie extraction: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
