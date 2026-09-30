"""Domain Constants and File Classification predicates for Cresmo Value Objects.

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- ADR-015: Reserved System Filenames and Derived Output Directory Isolation
"""

from __future__ import annotations

from pathlib import Path

MAX_CHANNEL_NAME_LENGTH: int = 120
MAX_CHANNEL_ID_LENGTH: int = 64
MIN_CHANNEL_ID_LENGTH: int = 2
MIN_CANONICAL_CHANNEL_ID_LENGTH: int = 4
MAX_NOTE_TITLE_LENGTH: int = 200

RESERVED_SYSTEM_FILENAMES: frozenset[str] = frozenset(
    {
        "_canal.md",
        "brain.csv",
        "cresmo_ledger.db",
        "cresmo_ledger.db-wal",
        "cresmo_ledger.db-shm",
        "playlist.txt",
        "playlist-priority.txt",
        "_index.json",
    }
)

RESERVED_DERIVED_DIRS: frozenset[str] = frozenset(
    {
        "enriched",
        "master",
        "vault",
        ".venv",
        "tests",
        "__pycache__",
    }
)


def is_processable_transcript_file(path: Path | str) -> bool:
    """Validate whether a path represents a candidate raw transcript and not a system artifact or index.

    Adheres to ADR-015:
    1. Suffix must strictly be .md or .txt (case-insensitive).
    2. Filename cannot start with '_' or '.' (hidden or system catalog).
    3. None of the directory components in path.parts may start with '_' or '.'.
    4. Filename cannot belong to RESERVED_SYSTEM_FILENAMES.
    5. Temporary, backup, or editor swap files (.tmp, .bak, .swp, ~) are excluded.
    6. Files residing inside derived output roots (enriched, master, vault) are excluded.

    Args:
        path: Path object or string path to validate.

    Returns:
        True if the file is an eligible raw transcript, False if it is a system artifact/index.
    """
    p = Path(path)
    name = p.name
    name_lower = name.lower()

    # Rule 1: Suffix must be .md or .txt
    suffix = p.suffix.lower()
    if suffix not in {".md", ".txt"}:
        return False

    # Rule 2: Filename cannot start with '_' or '.'
    if name.startswith(("_", ".")):
        return False

    # Rule 3: Hidden or system directory components (e.g. .git, .obsidian, _trash)
    for part in p.parts[:-1]:
        if part and part != "/" and part.startswith(("_", ".")):
            return False

    # Rule 4: Reserved system filenames
    if name_lower in RESERVED_SYSTEM_FILENAMES:
        return False

    # Rule 5: Temporary / backup / editor swap suffixes
    if name_lower.endswith((".tmp", ".bak", ".swp")) or name.endswith("~"):
        return False

    # Rule 6: Derived artifact directories when path is relative or encompasses multiple roots
    dir_parts_lower = {part.lower() for part in p.parts[:-1]}
    return not bool(dir_parts_lower.intersection(RESERVED_DERIVED_DIRS))
