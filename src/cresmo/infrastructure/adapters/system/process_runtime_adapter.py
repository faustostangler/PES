"""Infrastructure adapter implementing ProcessRuntimePort via host OS primitives.

Conforms to:
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

import gc
from pathlib import Path

from cresmo.application.ports.runtime import ProcessRuntimePort
from cresmo.infrastructure.system import get_process_rss_bytes


class SystemProcessRuntimeAdapter(ProcessRuntimePort):
    """Concrete ProcessRuntimePort adapter wrapping gc, OS RSS telemetry, and filesystem stat."""

    def collect_garbage(self) -> int:
        """Execute full generational garbage collection and return collected object count."""
        return gc.collect()

    def get_process_rss_bytes(self) -> float:
        """Return current resident set size in bytes via host OS bindings."""
        return get_process_rss_bytes()

    def get_file_size_bytes(self, path: Path) -> int:
        """Return file size in bytes using POSIX/Windows stat."""
        return path.stat().st_size
