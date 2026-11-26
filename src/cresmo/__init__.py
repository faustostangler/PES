"""Cresmo Strategic Knowledge Monolith.

Hexagonal Clean Architecture package for multi-pass media ingestion, Socratic expansion,
atomic note synthesis, and Obsidian Second Brain vault reconciliation.
"""

from __future__ import annotations

import contextlib
import sys
import threading
from typing import Any, Final

__version__ = "0.1.0"

__all__ = ["__version__"]

_PYTHON_313_VERSION: Final[tuple[int, int]] = (3, 13)
_THREADING_DELETE_DUMMY_ATTR: Final[str] = "_DeleteDummyThreadOnDel"
_THREADING_ACTIVE_LIMBO_LOCK_ATTR: Final[str] = "_active_limbo_lock"
_THREADING_ACTIVE_ATTR: Final[str] = "_active"


def _patch_python313_threading_shutdown() -> None:
    """Safeguard against CPython 3.13 teardown bug where _active_limbo_lock is set to None.

    During interpreter shutdown, CPython module globals in threading are cleared to None.
    Foreign/dummy threads spawned by background HTTP/gRPC connection pools or telemetry
    workers invoke `_DeleteDummyThreadOnDel.__del__`, which in Python 3.13 blindly attempts
    `with _active_limbo_lock:`, triggering a noisy TypeError: 'NoneType' object does not support
    the context manager protocol.
    """
    dummy_cls = getattr(threading, _THREADING_DELETE_DUMMY_ATTR, None)
    if dummy_cls is not None:

        def _safe_dummy_del(self: Any) -> None:
            lock = getattr(threading, _THREADING_ACTIVE_LIMBO_LOCK_ATTR, None)
            if lock is not None:
                with contextlib.suppress(TypeError, KeyError, AttributeError), lock:
                    active = getattr(threading, _THREADING_ACTIVE_ATTR, None)
                    if active and active.get(self._tident) is self._dummy_thread:
                        active.pop(self._tident, None)

        dummy_cls.__del__ = _safe_dummy_del


if sys.version_info[:2] == _PYTHON_313_VERSION:
    _patch_python313_threading_shutdown()
