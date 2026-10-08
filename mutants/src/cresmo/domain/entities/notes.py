"""AtomicNote and MapOfContent domain aggregates.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.exceptions import (
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)

MIN_ATOMIC_NOTE_DEFINITION_LENGTH: int = 20


@dataclass(frozen=True)
class AtomicNote:
    """AtomicNote Aggregate: Self-contained semantic unit in the Second Brain vault.

    Encapsulates an autonomous concept, entity, event, or dynamic process formatted
    as an Obsidian Markdown note with bidirectional WikiLinks.

    Attributes:
        title: Unique, validated note title.
        note_type: Canonical typology classification (concept, entity, event, process).
        definition: Dense contextual analysis and synthesis (minimum 20 characters).
        content_tags: Associated thematic tags.
        domain: Primary knowledge domain.
        cluster: Thematic cluster or subfield.
        source: Provenance reference link or compendium title.
        aliases: Alternative terminology or synonyms.
        direct_relations: Sequence of related NoteTitles (triples).
        causal_matrix: Optional ternary causality model (cause, effect, attribution).
        cross_context: Optional historical/lateral/consequential triad.

    Invariants:
        1. definition length must be >= 20 characters (rejects vacuous stubs per SPEC-001: §2.2).
        2. title cannot appear in direct_relations (prevents self-referential graph cycles).
    """

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
        cleaned_definition = self.definition.strip()
        if len(cleaned_definition) < MIN_ATOMIC_NOTE_DEFINITION_LENGTH:
            raise DomainValidationError(
                f"AtomicNote definition must contain at least {MIN_ATOMIC_NOTE_DEFINITION_LENGTH} "
                f"characters of contextual analysis. Got: '{cleaned_definition}'"
            )

        # Graph invariant: enforce acyclic direct relations (no self-loops)
        title_key = self.title.value.lower()
        for rel in self.direct_relations:
            if rel.value.lower() == title_key:
                raise SelfReferentialRelationError(
                    f"AtomicNote '{self.title.value}' cannot contain itself in direct_relations."
                )


@dataclass(frozen=True)
class MapOfContent:
    """MapOfContent Aggregate: Synthesis node reconciling clusters of Atomic Notes.

    Functions as an index anchor (MOC) in the Obsidian vault, organizing
    autonomous atomic notes into coherent thematic hierarchies with zero orphaned notes.

    Attributes:
        title: Validated MOC note title.
        theme: Macro epistemic subject or cluster name.
        overview: Synthetic prose framing the structural relationships of member notes.
        associated_notes: Non-empty sequence of validated NoteTitles.

    Invariants:
        1. associated_notes cannot be empty.
        2. associated_notes cannot contain duplicate titles (case-insensitive).
    """

    title: NoteTitle
    theme: str
    overview: str
    associated_notes: tuple[NoteTitle, ...]

    def __post_init__(self) -> None:
        if not self.associated_notes:
            raise DomainValidationError("MapOfContent must contain at least one associated note.")

        # Invariant check: prevent duplicate node entries in MOC graph
        seen: set[str] = set()
        for note in self.associated_notes:
            key = note.value.lower()
            if key in seen:
                raise DomainValidationError(
                    f"Duplicate associated note '{note.value}' in MapOfContent."
                )
            seen.add(key)
