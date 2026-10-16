"""Operating System and Process Runtime Inspection Utilities.

Provides cross-platform telemetry helpers that abstract kernel differences
between Linux, Darwin (macOS), and other platforms.

Conforms to:
    - ADR-026: Rule 4 (OS-Agnostic Telemetry & Safe Storage Paths)
"""

from __future__ import annotations

import resource
import sys

__all__ = ["get_process_rss_bytes"]


def get_process_rss_bytes() -> float:
    """Return resident set size in bytes, normalizing Linux and Darwin kernel differences.

    On Linux, getrusage().ru_maxrss is returned in kilobytes (multiplied by 1024 to get bytes).
    On Darwin (macOS), ru_maxrss is already reported directly in bytes.
    """
    raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return float(raw_rss)
    return float(raw_rss * 1024)
