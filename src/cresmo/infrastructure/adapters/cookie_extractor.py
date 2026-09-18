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
import time
from pathlib import Path

try:
    import yt_dlp.cookies
except ImportError:
    yt_dlp = None  # type: ignore[assignment]

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

    if yt_dlp is None:
        if verbose:
            sys.stderr.write("yt-dlp is not installed; cannot extract cookies.\n")
        return False

    try:
        cj = yt_dlp.cookies.extract_cookies_from_browser(browser)
    except Exception as exc:  # noqa: BLE001 - yt-dlp can raise sqlite/crypto/os errors across platforms
        if verbose:
            sys.stderr.write(f"Could not read cookies from '{browser}': {exc}\n")
        return False

    if not cj:
        return False

    mcj = http.cookiejar.MozillaCookieJar(str(temp_path))
    valid_count = 0
    yt_count = 0
    has_auth_cookies = False

    for c in cj:
        domain = (c.domain or "").lower()
        if not any(domain.endswith(d) for d in domains):
            continue

        if any(sub in domain for sub in IGNORED_SUBDOMAINS):
            continue

        if not c.name or not c.value or len(c.value.strip()) == 0:
            continue

        if len(c.name) > MAX_COOKIE_NAME_LENGTH or len(c.value) > MAX_COOKIE_VALUE_LENGTH:
            continue
        if not COOKIE_NAME_REGEX.match(c.name) or not COOKIE_VALUE_REGEX.match(c.value):
            continue

        if c.expires and c.expires > MAX_COOKIE_EXPIRY:
            c.expires = MAX_COOKIE_EXPIRY

        if c.name in AUTH_COOKIE_NAMES:
            has_auth_cookies = True

        mcj.set_cookie(c)
        valid_count += 1
        if "youtube.com" in domain:
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


def export_cookies_auto(
    output_file: Path | str,
    preferred_browser: str | None = "firefox",
    verbose: bool = False,
) -> bool:
    """Scan installed browsers in priority order and save the best set of YouTube cookies.

    Executes a two-tier extraction strategy:
    1. First pass: scans installed browsers specifically for authenticated session tokens.
    2. Second pass: if no authenticated session is found, falls back to guest/unauthenticated cookies.

    Args:
        output_file: Target path where the Netscape cookie jar will be saved.
        preferred_browser: Primary browser to attempt first (defaults to 'firefox').
        verbose: If True, outputs extraction telemetry to stdout.

    Returns:
        True if cookies were successfully extracted and written; False otherwise.
    """
    output_path = Path(output_file).resolve()

    # Prioritize preferred browser (e.g. firefox on Linux)
    priority: list[str] = []
    if preferred_browser and preferred_browser in SUPPORTED_BROWSERS:
        priority.append(preferred_browser)
    for b in ("firefox", "chrome", "chromium", "brave", "edge"):
        if b not in priority:
            priority.append(b)

    # 1. First pass: search strictly for authenticated browser sessions
    for browser in priority:
        if export_cookies_from_browser(
            browser=browser, output_file=output_path, require_auth=True, verbose=verbose
        ):
            return True

    # 2. Second pass: fallback to any valid browser cookies (guest/unauthenticated)
    for browser in priority:
        if export_cookies_from_browser(
            browser=browser, output_file=output_path, require_auth=False, verbose=verbose
        ):
            return True

    return False


def ensure_cookies_file(
    output_file: Path | str,
    browser: str | None = "firefox",
    max_age_hours: int = 12,
    verbose: bool = False,
) -> Path | None:
    """Ensure a valid authenticated cookie file exists on disk.

    Refreshes if missing, expired, or lacking authentication tokens.

    Args:
        output_file: Destination file path for the Netscape cookie file.
        browser: Preferred browser candidate for cookie extraction.
        max_age_hours: Maximum allowable file age before forcing a refresh (default: 12h).
        verbose: If True, outputs diagnostic messages.

    Returns:
        Path to a valid, verified cookie file, or None if unavailable.
    """
    out_path = Path(output_file).resolve()
    should_refresh = False

    if (
        not out_path.exists()
        or out_path.stat().st_size < MIN_COOKIE_FILE_BYTES
        or not has_valid_auth_cookies(out_path)
    ):
        should_refresh = True
    elif max_age_hours > 0:
        age_seconds = time.time() - out_path.stat().st_mtime
        if age_seconds > max_age_hours * 3600:
            should_refresh = True

    if should_refresh:
        success = False
        if browser:
            success = export_cookies_from_browser(
                browser=browser, output_file=out_path, require_auth=True, verbose=verbose
            )
        if not success:
            success = export_cookies_auto(
                output_file=out_path, preferred_browser=browser, verbose=verbose
            )
        if not success:
            return out_path if out_path.exists() and out_path.stat().st_size > 0 else None

    return out_path if out_path.exists() and out_path.stat().st_size > 0 else None
