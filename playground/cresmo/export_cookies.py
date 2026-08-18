#!/usr/bin/env python3
"""Programmatic YouTube Cookie Exporter for Cresmo / yt-dlp.

Extracts clean YouTube and Google authentication cookies directly from installed browsers
(Firefox, Chrome, Chromium, Brave, Edge) into a standardized Netscape format cookie file.

On Linux:
- Firefox stores cookies without OS keyring locks, making it the primary reliable source.
- Chrome/Chromium cookies are extracted with keyring decryption fallback.
"""

import argparse
import http.cookiejar
from pathlib import Path
import re
import sys
import time

try:
    import yt_dlp.cookies
except ImportError:
    print("Error: yt-dlp is required. Install it with: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)

# --- Browser & Cookie Defaults ---
SUPPORTED_BROWSERS: list[str] = ["firefox", "chrome", "chromium", "brave", "edge", "opera", "vivaldi"]
DEFAULT_COOKIE_FILE: Path = Path(__file__).parent.resolve() / ".yt_dlp_cookies.txt"
DEFAULT_TARGET_DOMAINS: tuple[str, ...] = ("youtube.com", "google.com", "ytimg.com")
IGNORED_SUBDOMAINS: tuple[str, ...] = (
    "takeout",
    "docs",
    "mail",
    "drive",
    "cloud",
    "meet",
    "chat",
    "play",
    "store",
    "admin",
    "sites",
    "groups",
    "photos",
)
BROWSER_PRIORITY_ORDER: list[str] = ["chrome", "chromium", "firefox", "brave", "edge"]
DEFAULT_MAX_AGE_HOURS: int = 12

# --- Cookie Validation Limits ---
MAX_COOKIE_NAME_LENGTH: int = 200
MAX_COOKIE_VALUE_LENGTH: int = 2000
MAX_COOKIE_EXPIRY: int = 2147483647
MIN_COOKIE_FILE_BYTES: int = 50

# --- Compiled Regexes ---
COOKIE_NAME_REGEX: re.Pattern[str] = re.compile(r"^[!-~]+$")
COOKIE_VALUE_REGEX: re.Pattern[str] = re.compile(r"^[ -~]+$")


def export_cookies_from_browser(
    browser: str,
    output_file: Path | str = DEFAULT_COOKIE_FILE,
    domains: tuple[str, ...] = DEFAULT_TARGET_DOMAINS,
    verbose: bool = True,
) -> bool:
    """Extract cookies from a single browser and save to Netscape cookie file."""
    output_path = Path(output_file).resolve()
    temp_path = output_path.with_suffix(".tmp")

    if verbose:
        print(f"🔍 Checking browser: '{browser}'...")

    try:
        cj = yt_dlp.cookies.extract_cookies_from_browser(browser)
    except Exception as e:
        if verbose:
            print(f"   ⚠️  Could not read '{browser}': {e}", file=sys.stderr)
        return False

    if not cj:
        return False

    # Filter and construct Netscape cookies
    mcj = http.cookiejar.MozillaCookieJar(str(temp_path))
    valid_count = 0
    yt_count = 0

    for c in cj:
        domain = (c.domain or "").lower()
        if not any(domain.endswith(d) for d in domains):
            continue

        # Skip noise subdomains
        if any(sub in domain for sub in IGNORED_SUBDOMAINS):
            continue

        # Crucial check: Cookie value MUST be non-empty (filters encrypted/locked entries)
        if not c.name or not c.value or len(c.value.strip()) == 0:
            continue

        if len(c.name) > MAX_COOKIE_NAME_LENGTH or len(c.value) > MAX_COOKIE_VALUE_LENGTH:
            continue
        if not COOKIE_NAME_REGEX.match(c.name) or not COOKIE_VALUE_REGEX.match(c.value):
            continue

        if c.expires and c.expires > MAX_COOKIE_EXPIRY:
            c.expires = MAX_COOKIE_EXPIRY

        mcj.set_cookie(c)
        valid_count += 1
        if "youtube.com" in domain:
            yt_count += 1

    if valid_count == 0:
        if verbose:
            print(f"   ⚠️  '{browser}' had no readable (decrypted) YouTube cookies.")
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mcj.save(ignore_discard=True, ignore_expires=True)
    temp_path.replace(output_path)

    if verbose:
        print(f"   ✅ Saved {valid_count} active cookies ({yt_count} YouTube-specific) from '{browser}' -> {output_path.name}")

    return True


def export_cookies_auto(
    output_file: Path | str = DEFAULT_COOKIE_FILE,
    verbose: bool = True,
) -> bool:
    """Scan all installed browsers and save the best set of unencrypted YouTube cookies."""
    output_path = Path(output_file).resolve()
    if verbose:
        print("🚀 [Cookie Exporter] Auto-refreshing YouTube authentication cookies...")

    for browser in BROWSER_PRIORITY_ORDER:
        if export_cookies_from_browser(browser=browser, output_file=output_path, verbose=verbose):
            if verbose:
                print(f"✓ Cookies successfully configured for pipeline: {output_path.name}\n")
            return True

    if verbose:
        print("⚠️ [Cookie Exporter] Could not extract cookies from installed browsers. Public endpoints will be used.\n", file=sys.stderr)
    return False


def ensure_cookies(
    output_file: Path | str = DEFAULT_COOKIE_FILE,
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    verbose: bool = False,
) -> None:
    """Ensure a valid cookie file exists. Refreshes if missing or older than max_age_hours."""
    out_p = Path(output_file).resolve()
    should_refresh = True

    if not out_p.exists() or out_p.stat().st_size < MIN_COOKIE_FILE_BYTES:
        should_refresh = True
    else:
        age_seconds = time.time() - out_p.stat().st_mtime
        if age_seconds > (max_age_hours * 3600):
            should_refresh = True
        else:
            should_refresh = False

    if should_refresh:
        export_cookies_auto(output_file=out_p, verbose=verbose)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export YouTube cookies to .yt_dlp_cookies.txt programmatically.")
    parser.add_argument(
        "--browser", "-b",
        type=str,
        default="auto",
        choices=["auto"] + SUPPORTED_BROWSERS,
        help="Specific browser to extract from, or 'auto' (default: auto).",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(DEFAULT_COOKIE_FILE),
        help=f"Destination Netscape file path (default: {DEFAULT_COOKIE_FILE}).",
    )

    args = parser.parse_args()

    if args.browser == "auto":
        success = export_cookies_auto(output_file=args.output, verbose=True)
    else:
        success = export_cookies_from_browser(browser=args.browser, output_file=args.output, verbose=True)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
