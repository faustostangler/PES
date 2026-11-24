"""YouTube Cookie Extraction and Management Adapter for Cresmo.

Extracts clean YouTube and Google authentication cookies directly from installed browsers
(Firefox, Chrome, Chromium, Brave, Edge) into a standardized Netscape format cookie file.

On Linux:
- Firefox stores cookies without OS keyring locks in SQLite, making it the most reliable source.
- Chrome/Chromium cookies use keyring decryption with graceful fallback.

Conforms to:
    - ADR-004: Native Media Ingestion Decommissioning
    - SPEC-004: Native Media Ingestion Specification
"""

from __future__ import annotations

import http.cookiejar
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yt_dlp
    import yt_dlp.cookies
except ImportError:
    yt_dlp = None

AUTH_COOKIE_NAMES: frozenset[str] = frozenset(
    {
        "SID",
        "SSID",
        "HSID",
        "SAPISID",
        "APISID",
        "LOGIN_INFO",
        "__Secure-1PSID",
        "__Secure-3PSID",
        "__Secure-1PAPISID",
        "__Secure-3PAPISID",
    }
)

SUPPORTED_BROWSERS: tuple[str, ...] = (
    "firefox",
    "chrome",
    "chromium",
    "brave",
    "edge",
    "opera",
    "vivaldi",
)

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

MAX_COOKIE_NAME_LENGTH: int = 200
MAX_COOKIE_VALUE_LENGTH: int = 2000
MAX_COOKIE_EXPIRY: int = 2147483647
MIN_COOKIE_FILE_BYTES: int = 50

COOKIE_NAME_REGEX: re.Pattern[str] = re.compile(r"^[!-~]+$")
COOKIE_VALUE_REGEX: re.Pattern[str] = re.compile(r"^[ -~]+$")


def has_valid_auth_cookies(cookie_file: Path) -> bool:
    """Check if the existing cookie file contains valid authenticated session tokens.

    Args:
        cookie_file: Filesystem path to the Netscape cookie jar file.

    Returns:
        True if the file exists, exceeds minimum byte threshold, and contains
        at least one known YouTube/Google authentication cookie token.
    """
    if not cookie_file.exists() or cookie_file.stat().st_size < MIN_COOKIE_FILE_BYTES:
        return False
    try:
        content = cookie_file.read_text(encoding="utf-8", errors="ignore")
        return any(
            f"\t{auth_token}\t" in content or content.endswith(f"\t{auth_token}")
            for auth_token in AUTH_COOKIE_NAMES
        )
    except OSError:
        return False


def _extract_raw_cookies(browser: str, verbose: bool) -> Any:
    """Safely invoke yt_dlp browser cookie extraction."""
    if yt_dlp is None:
        if verbose:
            sys.stderr.write("yt-dlp is not installed; cannot extract cookies.\n")
        return None

    try:
        return yt_dlp.cookies.extract_cookies_from_browser(browser)
    except Exception as exc:  # noqa: BLE001 - yt-dlp can raise sqlite/crypto/os errors across platforms
        if verbose:
            sys.stderr.write(f"Could not read cookies from '{browser}': {exc}\n")
        return None


def _is_valid_cookie(c: Any, domains: tuple[str, ...]) -> bool:
    """Validate whether cookie matches target domains and satisfies security invariants."""
    domain = (c.domain or "").lower()
    if not any(domain.endswith(d) for d in domains):
        return False

    if any(sub in domain for sub in IGNORED_SUBDOMAINS):
        return False

    if not c.name or not c.value or len(c.value.strip()) == 0:
        return False

    if len(c.name) > MAX_COOKIE_NAME_LENGTH or len(c.value) > MAX_COOKIE_VALUE_LENGTH:
        return False

    return bool(COOKIE_NAME_REGEX.match(c.name) and COOKIE_VALUE_REGEX.match(c.value))


def _sanitize_cookie(c: Any) -> None:
    """Clamp integer expiry timestamp to avoid 32-bit overflow."""
    if c.expires and c.expires > MAX_COOKIE_EXPIRY:
        c.expires = MAX_COOKIE_EXPIRY


def export_cookies_from_browser(
    browser: str,
    output_file: Path | str,
    domains: tuple[str, ...] = DEFAULT_TARGET_DOMAINS,
    require_auth: bool = False,
    verbose: bool = False,
) -> bool:
    """Extract cookies from a single browser and save to Netscape cookie file.

    Args:
        browser: Browser identifier ('firefox', 'chrome', etc.).
        output_file: Destination path for the generated Netscape cookie jar.
        domains: Target domain filters to include (defaults to YouTube/Google domains).
        require_auth: If True, requires presence of authenticated session tokens to succeed.
        verbose: If True, prints status messages to stdout/stderr.

    Returns:
        True if cookies were successfully extracted and persisted; False otherwise.
    """
    output_path = Path(output_file).resolve()
    temp_path = output_path.with_suffix(".tmp")

    cj = _extract_raw_cookies(browser, verbose)
    if not cj:
        return False

    mcj = http.cookiejar.MozillaCookieJar(str(temp_path))
    valid_count = 0
    yt_count = 0
    has_auth_cookies = False

    for c in cj:
        if not _is_valid_cookie(c, domains):
            continue

        _sanitize_cookie(c)
        if c.name in AUTH_COOKIE_NAMES:
            has_auth_cookies = True

        mcj.set_cookie(c)
        valid_count += 1
        if "youtube.com" in (c.domain or "").lower():
            yt_count += 1

    if valid_count == 0 or (require_auth and not has_auth_cookies):
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mcj.save(ignore_discard=True, ignore_expires=True)
    temp_path.replace(output_path)

    if verbose:
        auth_tag = " [Authenticated Session]" if has_auth_cookies else " [Guest/Unauthenticated]"
        sys.stdout.write(
            f"[cookies] Saved {valid_count} active cookies ({yt_count} YouTube-specific{auth_tag}) "
            f"from '{browser}' -> {output_path.name}\n"
        )

    return True
