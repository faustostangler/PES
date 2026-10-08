"""Obsidian adapter package for Cresmo vault repository.

Re-exports ObsidianVaultAdapter, sanitize_filename, and channel_to_slug.
"""

from cresmo.infrastructure.adapters.obsidian.adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.obsidian.utils import (
    ISO_DATE_COMPACT_LENGTH,
    MIN_NOTE_DEFINITION_LENGTH,
    channel_to_slug,
    sanitize_filename,
)

__all__ = [
    "ISO_DATE_COMPACT_LENGTH",
    "MIN_NOTE_DEFINITION_LENGTH",
    "ObsidianVaultAdapter",
    "channel_to_slug",
    "sanitize_filename",
]
