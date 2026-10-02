"""Domain Entities and Aggregates Package for Cresmo Knowledge Synthesis.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC per file)
"""

from __future__ import annotations

from cresmo.domain.entities.compendium import EnrichedCompendium
from cresmo.domain.entities.identity import (
    PIPELINE_SESSION_ID_PART_COUNT,
    JudgeFrictionMetric,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.entities.notes import (
    MIN_ATOMIC_NOTE_DEFINITION_LENGTH,
    AtomicNote,
    MapOfContent,
)
from cresmo.domain.entities.transcripts import (
    FluidTranscript,
    SourceTranscript,
    post_process_fluid_transcript,
)
from cresmo.domain.value_objects import (
    CandidateText,
    ChannelId,
    ChannelName,
    ContentId,
    NoteTitle,
    NoteType,
)

__all__ = [
    "MIN_ATOMIC_NOTE_DEFINITION_LENGTH",
    "PIPELINE_SESSION_ID_PART_COUNT",
    "AtomicNote",
    "CandidateText",
    "ChannelId",
    "ChannelName",
    "ContentId",
    "EnrichedCompendium",
    "FluidTranscript",
    "JudgeFrictionMetric",
    "MapOfContent",
    "NoteTitle",
    "NoteType",
    "PipelineSessionId",
    "SourceTranscript",
    "UserIdentity",
    "post_process_fluid_transcript",
]
