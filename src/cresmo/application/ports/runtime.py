"""Hexagonal Process Runtime Port and Null-Object implementation.

Conforms to:
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class ProcessRuntimePort(ABC):
    """Hexagonal Port abstracting OS process runtime operations for Application use cases."""

    @abstractmethod
    def collect_garbage(self) -> int:
        """Trigger garbage collection and return unreachable object count."""
        raise NotImplementedError

    @abstractmethod
    def get_process_rss_bytes(self) -> float:
        """Return resident set size (RSS) memory usage of the current process in bytes."""
        raise NotImplementedError

    @abstractmethod
    def get_file_size_bytes(self, path: Path) -> int:
        """Return size in bytes of the given file path."""
        raise NotImplementedError


class NoOpProcessRuntimePort(ProcessRuntimePort):
    """Hermetic Null-Object implementation of ProcessRuntimePort for offline/test runs."""

    def collect_garbage(self) -> int:
        """Return zero without invoking host garbage collector."""
        return 0

    def get_process_rss_bytes(self) -> float:
        """Return zero bytes RSS memory metric."""
        return 0.0

    def get_file_size_bytes(self, path: Path) -> int:
        """Return zero byte file size without filesystem inspection."""
        _ = path
        return 0
