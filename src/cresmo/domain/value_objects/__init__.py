"""Domain Value Objects for the Cresmo Knowledge Synthesis Bounded Context.

Implements immutable, self-validating Value Objects adhering to the Doctor Stangler Method
(Zero Primitive Obsession, construction-time invariant enforcement).

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-003: §2 (Channel Sync Models & Normalization Rules)
- ADR-001 (Modular Monolith Domain Integrity)
"""

from __future__ import annotations

from cresmo.domain.value_objects.constants import (
    MAX_CHANNEL_ID_LENGTH,
    MAX_CHANNEL_NAME_LENGTH,
    MAX_NOTE_TITLE_LENGTH,
    MIN_CANONICAL_CHANNEL_ID_LENGTH,
    MIN_CHANNEL_ID_LENGTH,
    RESERVED_DERIVED_DIRS,
    RESERVED_SYSTEM_FILENAMES,
    is_processable_transcript_file,
)
from cresmo.domain.value_objects.identity import (
    ChannelId,
    ChannelName,
    ContentId,
    SourceModality,
)
from cresmo.domain.value_objects.ledger import (
    LedgerEntry,
    MasterDocumentResult,
    RawIndexEntry,
)
from cresmo.domain.value_objects.media import (
    ChannelFeedQuery,
    DiscoveredMediaItem,
    PipelineStatus,
    normalize_to_uploads_playlist_url,
)
from cresmo.domain.value_objects.notes import (
    AtomicEntityInventory,
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.sync import (
    SyncFilterCriteria,
    SyncSummary,
)

__all__ = [
    "MAX_CHANNEL_ID_LENGTH",
    "MAX_CHANNEL_NAME_LENGTH",
    "MAX_NOTE_TITLE_LENGTH",
    "MIN_CANONICAL_CHANNEL_ID_LENGTH",
    "MIN_CHANNEL_ID_LENGTH",
    "RESERVED_DERIVED_DIRS",
    "RESERVED_SYSTEM_FILENAMES",
    "AtomicEntityInventory",
    "CausalMatrix",
    "ChannelFeedQuery",
    "ChannelId",
    "ChannelName",
    "ContentId",
    "CrossContextRelations",
    "DiscoveredMediaItem",
    "LedgerEntry",
    "MasterDocumentResult",
    "NoteTitle",
    "NoteType",
    "PipelineStatus",
    "PromptKey",
    "RawIndexEntry",
    "SourceModality",
    "SyncFilterCriteria",
    "SyncSummary",
    "is_processable_transcript_file",
    "normalize_to_uploads_playlist_url",
]
