"""Domain Value Objects for Atomic Notes, Typology, and Graph Relations.

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects.constants import MAX_NOTE_TITLE_LENGTH

_BRACKETS_PATTERN = re.compile(r"\[\[(.*?)\]\]")
_ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|%]')


class NoteType(str, Enum):
    """Canonical typology classification for Obsidian Second Brain atomic notes.

    Restricts note classification strictly to authorized categories per SPEC-001: §2.1:
    - CONCEPT: Abstract principles, mental models, theories.
    - ENTITY: Specific people, organizations, historical objects, locations.
    - EVENT: Demarcated historical or contemporary happenings.
    - PROCESS: Dynamical procedures, systemic flows, algorithmic sequences.
    """

    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    PROCESS = "process"

    @classmethod
    def from_string(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string.

        Args:
            raw: Raw typology string from LLM synthesis or frontmatter.

        Returns:
            Normalized NoteType enum member.

        Raises:
            NoteTypologyError: If the raw string does not match any valid typology.
        """
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(
            f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}"
        )


@dataclass(frozen=True)
class NoteTitle:
    """Canonical title for an Atomic Note in the Obsidian Second Brain vault.

    Invariants:
        Length between 1 and 200 characters. Automatically sanitizes WikiLink brackets
        and filesystem reserved characters while rejecting generic placeholders.
    """

    value: str

    def __post_init__(self) -> None:
        raw = self.value.strip()
        # ACL sanitization: strip [[ and ]] if LLM output included raw WikiLinks
        sanitized = _BRACKETS_PATTERN.sub(r"\1", raw).strip()
        # Filesystem isolation: remove characters prohibited on POSIX and Windows
        sanitized = _ILLEGAL_CHARS_PATTERN.sub("", sanitized).strip()

        if not sanitized or len(sanitized) > MAX_NOTE_TITLE_LENGTH:
            raise DomainValidationError(
                f"NoteTitle must be between 1 and {MAX_NOTE_TITLE_LENGTH} characters. Got: '{self.value}' (sanitized: '{sanitized}')"
            )

        if sanitized.lower() in {"untitled", "untitled_note"}:
            raise DomainValidationError(f"Generic placeholder title '{self.value}' is prohibited.")

        object.__setattr__(self, "value", sanitized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CausalMatrix:
    """Immutable ternary attribution model of causality for an Atomic Note.

    Attributes:
        cause: The primary generating condition or preceding mechanism.
        effect: The resultant dynamic outcome or structural change.
        epistemic_attribution: Conceptual framework, thinker, or source establishing causality.

    Invariants:
        Per SPEC-001: §2.1, either both cause and effect are populated, or both are empty.
        Partial causality (cause without effect or vice-versa) is illegal.
    """

    cause: str
    effect: str
    epistemic_attribution: str = ""

    def __post_init__(self) -> None:
        cleaned_cause = self.cause.strip()
        cleaned_effect = self.effect.strip()
        cleaned_epistemic_attribution = self.epistemic_attribution.strip()

        # Invariant enforcement: causality requires relational pairs (cause and effect)
        if (cleaned_cause or cleaned_effect) and (not cleaned_cause or not cleaned_effect):
            raise DomainValidationError(
                f"CausalMatrix requires both 'cause' and 'effect' to be non-empty. "
                f"Got cause='{cleaned_cause}', effect='{cleaned_effect}'."
            )

        object.__setattr__(self, "cause", cleaned_cause)
        object.__setattr__(self, "effect", cleaned_effect)
        object.__setattr__(self, "epistemic_attribution", cleaned_epistemic_attribution)


@dataclass(frozen=True)
class CrossContextRelations:
    """Immutable triad connecting a concept across historical, lateral, and consequential axes.

    Attributes:
        precursors: Ancestral intellectual, historical, or systemic conditions.
        lateral_events: Synchronous or parallel occurrences in other domains.
        aftermath: Long-term downstream repercussions or systemic legacies.
    """

    precursors: str = ""
    lateral_events: str = ""
    aftermath: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", self.precursors.strip())
        object.__setattr__(self, "lateral_events", self.lateral_events.strip())
        object.__setattr__(self, "aftermath", self.aftermath.strip())


@dataclass(frozen=True)
class AtomicEntityInventory:
    """Discovery manifest of unique named entities discovered across an Enriched Compendium.

    Attributes:
        items: Sequence of tuples pairing validated NoteTitle and NoteType.

    Invariants:
        Per SPEC-001: §2.1, inventory cannot be empty and must contain zero duplicate titles
        (case-insensitive normalization) to guarantee deterministic batch partitioning.
    """

    items: tuple[tuple[NoteTitle, NoteType], ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise DomainValidationError("AtomicEntityInventory cannot be empty.")

        seen_titles: set[str] = set()
        for title, _ in self.items:
            key = title.value.lower()
            if key in seen_titles:
                raise DomainValidationError(
                    f"Duplicate title '{title.value}' detected in AtomicEntityInventory."
                )
            seen_titles.add(key)
