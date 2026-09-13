"""Domain Entities and Aggregates for the Cresmo Knowledge Synthesis context.

Enforces business invariants strictly at construction time (Always Valid State).
No persistence models or external framework dependencies in this layer.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)

_TABLE_PATTERN = re.compile(r"\|.*\|.*\n\|[\s:-]+\|", re.MULTILINE)


@dataclass(frozen=True)
class RawTranscript:
    """Stage 1 Aggregate: Verbatim spoken transcript and origin metadata."""

    content_id: ContentId
    channel_name: str
    body: str
    title: str = ""
    source_url: str = ""
    upload_date: datetime.date | None = None
    channel_id: str = ""
    channel_category: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        if not self.channel_name.strip():
            raise DomainValidationError("channel_name cannot be empty.")
        if not self.body.strip():
            raise DomainValidationError("RawTranscript body cannot be empty or whitespace.")


@dataclass(frozen=True)
class EnrichedCompendium:
    """Stage 2 & 3 Aggregate: Multi-pass enriched fluid prose compendium."""

    content_id: ContentId
    channel_name: str
    title: NoteTitle
    body: str
    complementary_info: str
    pass_count: int = 1
    channel_id: str = ""
    channel_category: str = ""
    source_url: str = ""
    video_date: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        b = self.body.strip()
        ci = self.complementary_info.strip()

        if not b:
            raise CompendiumStructureError("EnrichedCompendium body cannot be empty.")
        if not ci:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )
        if _TABLE_PATTERN.search(b):
            raise CompendiumStructureError(
                "EnrichedCompendium body must be continuous prose and cannot contain Markdown tables."
            )
        if self.pass_count < 1:
            raise CompendiumStructureError("pass_count must be at least 1.")


@dataclass(frozen=True)
class AtomicNote:
    """Stage 4 & 5 Aggregate: Self-contained semantic unit in the Second Brain vault."""

    title: NoteTitle
    note_type: NoteType
    definition: str
    content_tags: tuple[str, ...] = ()
    domain: str = ""
    cluster: str = ""
    source: str = ""
    aliases: tuple[str, ...] = ()
    direct_relations: tuple[NoteTitle, ...] = ()
    causal_matrix: CausalMatrix | None = None
    cross_context: CrossContextRelations | None = None

    def __post_init__(self) -> None:
        d = self.definition.strip()
        if len(d) < 20:
            raise DomainValidationError(
                f"AtomicNote definition must contain at least 20 characters of contextual analysis. Got: '{d}'"
            )

        title_key = self.title.value.lower()
        for rel in self.direct_relations:
            if rel.value.lower() == title_key:
                raise SelfReferentialRelationError(
                    f"AtomicNote '{self.title.value}' cannot contain itself in direct_relations."
                )


@dataclass(frozen=True)
class MapOfContent:
    """Stage 6 Aggregate: Synthesis node reconciling clusters of Atomic Notes."""

    title: NoteTitle
    theme: str
    overview: str
    associated_notes: tuple[NoteTitle, ...]

    def __post_init__(self) -> None:
        if not self.associated_notes:
            raise DomainValidationError("MapOfContent must contain at least one associated note.")

        seen: set[str] = set()
        for note in self.associated_notes:
            key = note.value.lower()
            if key in seen:
                raise DomainValidationError(
                    f"Duplicate associated note '{note.value}' in MapOfContent."
                )
            seen.add(key)
