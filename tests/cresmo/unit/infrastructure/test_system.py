"""Unit tests for cross-platform OS telemetry inspection helpers.

Conforms to ADR-026 Rule 4 (OS-Agnostic Telemetry & Safe Storage Paths).
"""

from __future__ import annotations

import resource
from unittest.mock import MagicMock, patch

from cresmo.infrastructure.system import get_process_rss_bytes


def test_get_process_rss_bytes_linux_scales_by_1024() -> None:
    """Linux kernel reports ru_maxrss in kilobytes; helper must multiply by 1024."""
    mock_rusage = MagicMock()
    mock_rusage.ru_maxrss = 50_000  # 50,000 KB

    with (
        patch("sys.platform", "linux"),
        patch("resource.getrusage", return_value=mock_rusage) as mock_getrusage,
    ):
        rss = get_process_rss_bytes()
        assert rss == 50_000 * 1024.0
        mock_getrusage.assert_called_once_with(resource.RUSAGE_SELF)


def test_get_process_rss_bytes_darwin_returns_raw_bytes() -> None:
    """Darwin (macOS) kernel reports ru_maxrss directly in bytes; no scaling."""
    mock_rusage = MagicMock()
    mock_rusage.ru_maxrss = 51_200_000  # 51.2 MB in bytes

    with (
        patch("sys.platform", "darwin"),
        patch("resource.getrusage", return_value=mock_rusage) as mock_getrusage,
    ):
        rss = get_process_rss_bytes()
        assert rss == 51_200_000.0
        mock_getrusage.assert_called_once_with(resource.RUSAGE_SELF)
