"""Obsidian filesystem utilities, sanitization, and atomic file writes.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Final
from uuid import uuid4

from cresmo.domain.value_objects import ChannelName

ISO_DATE_COMPACT_LENGTH: Final[int] = 8

_ILLEGAL_FILENAME_CHARS: Final[re.Pattern[str]] = re.compile(r'[\\/*?:"<>|%]')
_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\s+")
_FRONTMATTER_PATTERN: Final[re.Pattern[str]] = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$")
_ILLEGAL_CHAR_REPLACEMENT: Final[str] = "_"
_TEMP_FILE_MARKER: Final[str] = ".tmp."
_UTF8_ENCODING: Final[str] = "utf-8"


def sanitize_filename(name: str | ChannelName) -> str:
    """Sanitize note title for safe filesystem path representation.

    Args:
        name: Raw string candidate or ChannelName for a filename.

    Returns:
        Filesystem-safe string with illegal characters replaced by underscores.
    """
    return _ILLEGAL_FILENAME_CHARS.sub(_ILLEGAL_CHAR_REPLACEMENT, str(name).strip())


def channel_to_slug(name: str | ChannelName) -> str:
    """Convert channel name to safe slug with underscores instead of whitespace.

    Args:
        name: Channel title, ChannelName, or category name.

    Returns:
        Clean slug safe for folder naming.
    """
    clean = _WHITESPACE_PATTERN.sub(_ILLEGAL_CHAR_REPLACEMENT, str(name).strip())
    return _ILLEGAL_FILENAME_CHARS.sub(_ILLEGAL_CHAR_REPLACEMENT, clean)


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
    temp_file = target_path.parent / f"{target_path.name}{_TEMP_FILE_MARKER}{uuid4().hex}"
    temp_file.write_text(content, encoding=_UTF8_ENCODING)
    os.replace(temp_file, target_path)
