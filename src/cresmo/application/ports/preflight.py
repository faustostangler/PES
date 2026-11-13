"""Application Port for preflight system, filesystem, and HTTP probing.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Hexagonal Ports & Adapters)
- ADR-014: Active Preflight Probes & Fail-Fast Observability
- ADR-062: Structural Consolidation, Evals SSOT & Bootstrap Separation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class PreflightProbePort(ABC):
    """Port abstracting filesystem, binary, and HTTP runtime environment probes."""

    @abstractmethod
    def ensure_directory(self, path: Path) -> None:
        """Create directory tree if absent, raising OSError on failure.

        Args:
            path: Target filesystem directory path.
        """

    @abstractmethod
    def is_writable(self, path: Path) -> bool:
        """Check whether an existing directory accepts write operations.

        Args:
            path: Directory path to inspect.

        Returns:
            True if writable, False otherwise.
        """

    @abstractmethod
    def executable_exists(self, binary_name: str) -> bool:
        """Check whether an executable binary is available on system PATH.

        Args:
            binary_name: Executable command name (e.g. 'ffmpeg').

        Returns:
            True if resolved on PATH, False otherwise.
        """

    @abstractmethod
    def probe_http(self, url: str, timeout_seconds: float = 1.0) -> bool:
        """Execute lightweight HTTP GET probe returning True for status < 500.

        Args:
            url: Full HTTP/HTTPS probe URL.
            timeout_seconds: Socket timeout in seconds.

        Returns:
            True if reachable and status < 500, False otherwise.
        """
