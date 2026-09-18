"""Filesystem Path Discovery and Repository Anchor Resolution.

Provides lightweight, dependency-free utilities for traversing and locating
workspace roots and project markers per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-006: Resilient Workspace Root Discovery
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["find_workspace_root"]


def find_workspace_root(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__ directory.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    # ACL boundary: Resolves path safely without assuming CWD matches the project root
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    # Fallback heuristic: src/cresmo/infrastructure/paths.py -> parents[3] is project root
    return (start_path or Path(__file__)).resolve().parents[3]

