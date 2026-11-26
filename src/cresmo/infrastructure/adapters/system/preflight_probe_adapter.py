"""Infrastructure adapter implementing PreflightProbePort via stdlib OS/HTTP APIs.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-014: Active Preflight Probes & Fail-Fast Observability
- ADR-062: Structural Consolidation, Evals SSOT & Bootstrap Separation
"""

from __future__ import annotations

import os
import shutil
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path
from typing import Final

from cresmo.application.ports.preflight import PreflightProbePort

DEFAULT_HTTP_PROBE_TIMEOUT_SECONDS: Final[float] = 1.0
_HTTP_GET_METHOD: Final[str] = "GET"
_HEADER_USER_AGENT: Final[str] = "User-Agent"
_PROBE_USER_AGENT_VALUE: Final[str] = "CresmoPreflightProbe/1.0"
_ATTR_STATUS: Final[str] = "status"


def probe_http_endpoint(
    url: str,
    timeout_seconds: float = DEFAULT_HTTP_PROBE_TIMEOUT_SECONDS,
) -> bool:
    """Execute lightweight HTTP GET probe returning True if status < 500.

    Args:
        url: Full HTTP or HTTPS URL to probe.
        timeout_seconds: Socket timeout in seconds (default: 1.0s).

    Returns:
        True if endpoint responded with HTTP status < 500, False on failure or timeout.
    """
    try:
        req = urllib.request.Request(
            url,
            method=_HTTP_GET_METHOD,
            headers={_HEADER_USER_AGENT: _PROBE_USER_AGENT_VALUE},
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            status = getattr(response, _ATTR_STATUS, HTTPStatus.OK)
            return bool(isinstance(status, int) and status < HTTPStatus.INTERNAL_SERVER_ERROR)
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        return False


class PreflightProbeAdapter(PreflightProbePort):
    """Concrete system probe adapter backed by pathlib, os.access, and shutil.which."""

    def ensure_directory(self, path: Path) -> None:
        """Create directory tree if absent, raising OSError on failure."""
        path.mkdir(parents=True, exist_ok=True)

    def is_writable(self, path: Path) -> bool:
        """Check whether an existing directory accepts write operations."""
        return os.access(path, os.W_OK)

    def executable_exists(self, binary_name: str) -> bool:
        """Check whether an executable binary is available on system PATH."""
        return shutil.which(binary_name) is not None
