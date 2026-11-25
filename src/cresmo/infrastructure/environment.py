"""Runtime filesystem environment helpers for Cresmo infrastructure.

Provides explicit, side-effect-controlled helpers for runtime directory creation
and Netscape cookies file discovery outside Pydantic settings initialization.

Conforms to:
    - ADR-006: Resilient Workspace Root Discovery
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from cresmo.domain.stage_registry import StageName

__all__ = [
    "StorageSettingsProtocol",
    "discover_cookies_file",
    "ensure_runtime_directories",
]


@runtime_checkable
class StorageSettingsProtocol(Protocol):
    """Structural protocol for storage settings exposing runtime directory paths."""

    @property
    def data_dir(self) -> Path:
        """Root directory for staged media transcripts and processing ledger."""
        ...

    @property
    def vault_dir(self) -> Path:
        """Root directory for Obsidian Second Brain knowledge graph vault."""
        ...

    @property
    def mocs_dir(self) -> Path:
        """Subdirectory within vault housing Maps of Content."""
        ...

    @property
    def master_dir(self) -> Path:
        """Directory for consolidated master compendiums per channel category."""
        ...

    @property
    def priority_texts_dir(self) -> Path:
        """Absolute path to the priority texts directory."""
        ...


def ensure_runtime_directories(storage: StorageSettingsProtocol) -> None:
    """Create all runtime storage directories idempotently in deterministic order.

    Args:
        storage: Storage settings object exposing runtime directory properties.
    """
    for directory in (
        storage.data_dir,
        storage.vault_dir,
        storage.mocs_dir,
        storage.master_dir,
        storage.priority_texts_dir,
        *(storage.data_dir / stage.value for stage in StageName),
    ):
        directory.mkdir(parents=True, exist_ok=True)


def discover_cookies_file(
    data_dir: Path,
    workspace_dir: Path,
    configured: Path | None = None,
) -> Path | None:
    """Discover the first existing, non-empty Netscape cookies file in priority order.

    Checks candidate locations sequentially:
        1. ``configured`` (when not ``None``)
        2. ``data_dir / "cookies.txt"``
        3. ``workspace_dir / "data" / "cookies.txt"``
        4. ``workspace_dir / ".yt_dlp_cookies.txt"``

    Args:
        data_dir: Base Cresmo data directory.
        workspace_dir: Resolved workspace root directory.
        configured: Optional explicitly configured cookies file path.

    Returns:
        First candidate path that exists as a regular non-empty file, or ``None``.
    """
    candidates: list[Path] = []
    if configured is not None:
        candidates.append(configured)
    candidates.extend(
        (
            data_dir / "cookies.txt",
            workspace_dir / "data" / "cookies.txt",
            workspace_dir / ".yt_dlp_cookies.txt",
        )
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    return None
