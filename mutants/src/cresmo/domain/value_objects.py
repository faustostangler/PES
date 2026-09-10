"""Domain Value Objects for the Cresmo Knowledge Synthesis context.

Implements immutable, self-validating Value Objects adhering to the Doctor Stangler Method
(Zero Primitive Obsession, construction-time invariant enforcement).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError

_CONTENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")
_BRACKETS_PATTERN = re.compile(r"\[\[(.*?)\]\]")
_ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|%]')


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁNoteTypeǁfrom_string__mutmut: MutantDict = {}  # type: ignore


class NoteType(str, Enum):
    """Canonical typology classification for Obsidian Second Brain atomic notes."""

    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    PROCESS = "process"

    @classmethod
    @_mutmut_mutated(mutants_xǁNoteTypeǁfrom_string__mutmut, is_classmethod = True)
    def from_string(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}")

    @classmethod
    def xǁNoteTypeǁfrom_string__mutmut_orig(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}")

    @classmethod
    def xǁNoteTypeǁfrom_string__mutmut_1(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = None
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}")

    @classmethod
    def xǁNoteTypeǁfrom_string__mutmut_2(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().upper()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}")

    @classmethod
    def xǁNoteTypeǁfrom_string__mutmut_3(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().lower()
        for member in cls:
            if member.value != normalized:
                return member
        raise NoteTypologyError(f"Invalid note typology '{raw}'. Expected one of: {[m.value for m in cls]}")

    @classmethod
    def xǁNoteTypeǁfrom_string__mutmut_4(cls, raw: str) -> NoteType:
        """Parse and normalize case-insensitive typology string."""
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise NoteTypologyError(None)

mutants_xǁNoteTypeǁfrom_string__mutmut['_mutmut_orig'] = NoteType.xǁNoteTypeǁfrom_string__mutmut_orig # type: ignore # mutmut generated
mutants_xǁNoteTypeǁfrom_string__mutmut['xǁNoteTypeǁfrom_string__mutmut_1'] = NoteType.xǁNoteTypeǁfrom_string__mutmut_1 # type: ignore # mutmut generated
mutants_xǁNoteTypeǁfrom_string__mutmut['xǁNoteTypeǁfrom_string__mutmut_2'] = NoteType.xǁNoteTypeǁfrom_string__mutmut_2 # type: ignore # mutmut generated
mutants_xǁNoteTypeǁfrom_string__mutmut['xǁNoteTypeǁfrom_string__mutmut_3'] = NoteType.xǁNoteTypeǁfrom_string__mutmut_3 # type: ignore # mutmut generated
mutants_xǁNoteTypeǁfrom_string__mutmut['xǁNoteTypeǁfrom_string__mutmut_4'] = NoteType.xǁNoteTypeǁfrom_string__mutmut_4 # type: ignore # mutmut generated


@dataclass(frozen=True)
class ContentId:
    """Strongly-typed unique identifier for a raw media item or transcript."""

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val or not _CONTENT_ID_PATTERN.match(val):
            raise DomainValidationError(
                f"Invalid ContentId '{self.value}'. Must match ^[a-zA-Z0-9_-]{{8,64}}$ without whitespace."
            )
        object.__setattr__(self, "value", val)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoteTitle:
    """Canonical title for an Atomic Note in the Second Brain vault."""

    value: str

    def __post_init__(self) -> None:
        raw = self.value.strip()
        # Strip [[ and ]] if present
        sanitized = _BRACKETS_PATTERN.sub(r"\1", raw).strip()
        # Strip illegal filesystem characters
        sanitized = _ILLEGAL_CHARS_PATTERN.sub("", sanitized).strip()

        if not sanitized or len(sanitized) > 200:
            raise DomainValidationError(
                f"NoteTitle must be between 1 and 200 characters. Got: '{self.value}' (sanitized: '{sanitized}')"
            )

        if sanitized.lower() in {"untitled", "untitled_note"}:
            raise DomainValidationError(f"Generic placeholder title '{self.value}' is prohibited.")

        object.__setattr__(self, "value", sanitized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CausalMatrix:
    """Immutable ternary attribution model of causality for an Atomic Note."""

    cause: str
    effect: str
    epistemic_attribution: str = ""

    def __post_init__(self) -> None:
        c = self.cause.strip()
        e = self.effect.strip()
        ea = self.epistemic_attribution.strip()

        if (c or e) and (not c or not e):
            raise DomainValidationError(
                f"CausalMatrix requires both 'cause' and 'effect' to be non-empty. Got cause='{c}', effect='{e}'."
            )

        object.__setattr__(self, "cause", c)
        object.__setattr__(self, "effect", e)
        object.__setattr__(self, "epistemic_attribution", ea)


@dataclass(frozen=True)
class CrossContextRelations:
    """Immutable triad connecting a concept across historical, lateral, and consequential axes."""

    precursors: str = ""
    lateral_events: str = ""
    aftermath: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", self.precursors.strip())
        object.__setattr__(self, "lateral_events", self.lateral_events.strip())
        object.__setattr__(self, "aftermath", self.aftermath.strip())


@dataclass(frozen=True)
class AtomicEntityInventory:
    """Discovery manifest of unique named entities discovered across an Enriched Compendium."""

    items: tuple[tuple[NoteTitle, NoteType], ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise DomainValidationError("AtomicEntityInventory cannot be empty.")

        seen_titles: set[str] = set()
        for title, _ in self.items:
            key = title.value.lower()
            if key in seen_titles:
                raise DomainValidationError(f"Duplicate title '{title.value}' detected in AtomicEntityInventory.")
            seen_titles.add(key)
