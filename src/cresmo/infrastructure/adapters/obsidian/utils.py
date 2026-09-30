"""Obsidian filesystem utilities, sanitization, and atomic file writes.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import uuid4

from cresmo.domain.value_objects import ChannelName

ISO_DATE_COMPACT_LENGTH: int = 8
MIN_NOTE_DEFINITION_LENGTH: int = 20

_ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|%]')
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$")


def sanitize_filename(name: str | ChannelName) -> str:
    """Sanitize note title for safe filesystem path representation.

    Args:
        name: Raw string candidate or ChannelName for a filename.

    Returns:
        Filesystem-safe string with illegal characters replaced by underscores.
    """
    return _ILLEGAL_FILENAME_CHARS.sub("_", str(name).strip())


def channel_to_slug(name: str | ChannelName) -> str:
    """Convert channel name to safe slug with underscores instead of whitespace.

    Args:
        name: Channel title, ChannelName, or category name.

    Returns:
        Clean slug safe for folder naming.
    """
    clean = re.sub(r"\s+", "_", str(name).strip())
    return _ILLEGAL_FILENAME_CHARS.sub("_", clean)


def atomic_write(target_path: Path, content: str) -> None:
    """Atomically write text content using temp-file replace pattern.

    Writes content to an ephemeral UUID temporary file in the target directory
    before executing an atomic rename (os.replace). Prevents corrupted half-written
    files during system crashes or power interruptions.

    Args:
        target_path: Final destination filesystem path.
        content: Complete text content to persist.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = target_path.parent / f"{target_path.name}.tmp.{uuid4().hex}"
    temp_file.write_text(content, encoding="utf-8")
    os.replace(temp_file, target_path)
