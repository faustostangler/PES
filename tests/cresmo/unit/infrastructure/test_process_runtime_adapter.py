"""Hermetic unit tests for SystemProcessRuntimeAdapter and NoOpProcessRuntimePort.

Conforms to:
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cresmo.application.ports import NoOpProcessRuntimePort
from cresmo.infrastructure.adapters.system.process_runtime_adapter import (
    SystemProcessRuntimeAdapter,
)


def test_noop_process_runtime_port_returns_deterministic_zeros(tmp_path: Path) -> None:
    port = NoOpProcessRuntimePort()
    assert port.collect_garbage() == 0
    assert port.get_process_rss_bytes() == 0.0
    assert port.get_file_size_bytes(tmp_path / "nonexistent.txt") == 0


def test_system_process_runtime_adapter_delegates_runtime_calls(tmp_path: Path) -> None:
    target = tmp_path / "sample.md"
    target.write_bytes(b"hello world")
    adapter = SystemProcessRuntimeAdapter()

    with (
        patch(
            "cresmo.infrastructure.adapters.system.process_runtime_adapter.gc.collect",
            return_value=7,
        ) as mock_gc,
        patch(
            "cresmo.infrastructure.adapters.system.process_runtime_adapter.get_process_rss_bytes",
            return_value=12345.0,
        ) as mock_rss,
    ):
        assert adapter.collect_garbage() == 7
        assert adapter.get_process_rss_bytes() == 12345.0
        mock_gc.assert_called_once_with()
        mock_rss.assert_called_once_with()

    assert adapter.get_file_size_bytes(target) == 11
