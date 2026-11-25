"""Domain Entities and Aggregates Package for Cresmo Knowledge Synthesis.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC per file)
- ADR-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion
"""

from __future__ import annotations

from cresmo.domain.entities.identity import (
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.entities.notes import (
    AtomicNote,
    MapOfContent,
)
from cresmo.domain.entities.transcripts import (
    StageTranscript,
    extract_source_text,
    post_process_fluid_transcript,
)

__all__ = [
    "AtomicNote",
    "MapOfContent",
    "PipelineSessionId",
    "StageTranscript",
    "UserIdentity",
    "extract_source_text",
    "post_process_fluid_transcript",
]
