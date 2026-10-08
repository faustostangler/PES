"""Obsidian Second Brain Vault Repository Adapter.

Implements VaultRepositoryPort using atomic filesystem writes, YAML frontmatter serialization,
and tiered index management. Acts as an Anti-Corruption Layer (ACL) shielding domain entities
from markdown serialization quirks.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-003: PES Production Architecture & Telemetry
    - SPEC-001: Core Knowledge Synthesis Specifications
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance (Modularization)
"""

from cresmo.infrastructure.adapters.obsidian import (
    ISO_DATE_COMPACT_LENGTH,
    MIN_NOTE_DEFINITION_LENGTH,
    ObsidianVaultAdapter,
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
