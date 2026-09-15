"""Filesystem Path Discovery and Repository Anchor Resolution.

Provides lightweight, dependency-free utilities for traversing and locating
workspace roots and project markers per Clean/Hexagonal Architecture.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["find_workspace_root"]


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_find_workspace_root__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_find_workspace_root__mutmut)
def find_workspace_root(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_orig(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_1(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = None
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_2(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path and Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_3(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(None)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_4(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() and (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_5(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory * "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_6(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "XXpyproject.tomlXX").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_7(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "PYPROJECT.TOML").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_8(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory * ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_9(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / "XX.gitXX").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_10(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".GIT").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_11(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path and Path(__file__)).resolve().parents[3]


def x_find_workspace_root__mutmut_12(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(None)).resolve().parents[3]


def x_find_workspace_root__mutmut_13(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution.

    Traverses upward from start_path (or __file__) looking for project anchor markers
    ('pyproject.toml' or '.git'). Falls back gracefully to parents[3] if no marker is found.

    Args:
        start_path: Optional starting filesystem path. Defaults to __file__.

    Returns:
        Absolute Path to the resolved workspace root directory.
    """
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[4]

mutants_x_find_workspace_root__mutmut['_mutmut_orig'] = x_find_workspace_root__mutmut_orig # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_1'] = x_find_workspace_root__mutmut_1 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_2'] = x_find_workspace_root__mutmut_2 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_3'] = x_find_workspace_root__mutmut_3 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_4'] = x_find_workspace_root__mutmut_4 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_5'] = x_find_workspace_root__mutmut_5 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_6'] = x_find_workspace_root__mutmut_6 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_7'] = x_find_workspace_root__mutmut_7 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_8'] = x_find_workspace_root__mutmut_8 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_9'] = x_find_workspace_root__mutmut_9 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_10'] = x_find_workspace_root__mutmut_10 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_11'] = x_find_workspace_root__mutmut_11 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_12'] = x_find_workspace_root__mutmut_12 # type: ignore # mutmut generated
mutants_x_find_workspace_root__mutmut['x_find_workspace_root__mutmut_13'] = x_find_workspace_root__mutmut_13 # type: ignore # mutmut generated
