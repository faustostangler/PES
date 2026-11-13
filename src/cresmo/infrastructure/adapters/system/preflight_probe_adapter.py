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
from pathlib import Path

from cresmo.application.ports.preflight import PreflightProbePort


def probe_http_endpoint(url: str, timeout_seconds: float = 1.0) -> bool:
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
            method="GET",
            headers={"User-Agent": "CresmoPreflightProbe/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            status = getattr(response, "status", 200)
            return bool(isinstance(status, int) and status < 500)
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        return False


class PreflightProbeAdapter(PreflightProbePort):
    """Concrete system probe adapter backed by pathlib, os.access, shutil.which, and urllib."""

    def ensure_directory(self, path: Path) -> None:
        """Create directory tree if absent, raising OSError on failure."""
        path.mkdir(parents=True, exist_ok=True)

    def is_writable(self, path: Path) -> bool:
        """Check whether an existing directory accepts write operations."""
        return os.access(path, os.W_OK)

    def executable_exists(self, binary_name: str) -> bool:
        """Check whether an executable binary is available on system PATH."""
        return shutil.which(binary_name) is not None

    def probe_http(self, url: str, timeout_seconds: float = 1.0) -> bool:
        """Execute lightweight HTTP GET probe returning True for status < 500."""
        return probe_http_endpoint(url, timeout_seconds=timeout_seconds)
