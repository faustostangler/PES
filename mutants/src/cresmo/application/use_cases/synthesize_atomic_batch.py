"""Use Case: Synthesize Atomic Note Batches.

Generates rich AtomicNote domain aggregates from an AtomicEntityInventory in small,
controlled batches (default: <= 5), enforcing incremental vault persistence and
tiered index reconciliation.

Conforms to:
- SPEC-001: §1 (Batched Atomic Synthesis)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import json
import re
from typing import Any, Final

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.exceptions import (
    DomainValidationError,
    NoteTypologyError,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    ChannelId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
    PromptKey,
)

# Honorific prefixes stripped during entity normalization to prevent duplicate notes
_HONORIFIC_PREFIXES: tuple[str, ...] = ("dom ", "dona ", "d. ", "d ")
_PUNCT_COLLAPSE_RE = re.compile(r"[\s\-_.,()]+")
_MIN_HONORIFIC_NORMALIZED_LENGTH: Final[int] = 4


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__norm_honorific__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__norm_honorific__mutmut)
def _norm_honorific(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_orig(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_1(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = None
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_2(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.upper().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_3(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(None):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_4(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = None
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_5(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            return
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def x__norm_honorific__mutmut_6(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(None, cleaned).strip()


def x__norm_honorific__mutmut_7(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", None).strip()


def x__norm_honorific__mutmut_8(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(cleaned).strip()


def x__norm_honorific__mutmut_9(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", ).strip()


def x__norm_honorific__mutmut_10(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub("XX XX", cleaned).strip()

mutants_x__norm_honorific__mutmut['_mutmut_orig'] = x__norm_honorific__mutmut_orig # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_1'] = x__norm_honorific__mutmut_1 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_2'] = x__norm_honorific__mutmut_2 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_3'] = x__norm_honorific__mutmut_3 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_4'] = x__norm_honorific__mutmut_4 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_5'] = x__norm_honorific__mutmut_5 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_6'] = x__norm_honorific__mutmut_6 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_7'] = x__norm_honorific__mutmut_7 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_8'] = x__norm_honorific__mutmut_8 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_9'] = x__norm_honorific__mutmut_9 # type: ignore # mutmut generated
mutants_x__norm_honorific__mutmut['x__norm_honorific__mutmut_10'] = x__norm_honorific__mutmut_10 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__build_existing_lookups__mutmut)
def _build_existing_lookups(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_orig(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_1(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = None
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_2(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = None
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_3(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = None
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_4(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.upper()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_5(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = None
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_6(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.upper()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_7(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = None
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_8(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(None)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_9(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) > _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def x__build_existing_lookups__mutmut_10(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = None
    return lookup, norm_lookup

mutants_x__build_existing_lookups__mutmut['_mutmut_orig'] = x__build_existing_lookups__mutmut_orig # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_1'] = x__build_existing_lookups__mutmut_1 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_2'] = x__build_existing_lookups__mutmut_2 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_3'] = x__build_existing_lookups__mutmut_3 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_4'] = x__build_existing_lookups__mutmut_4 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_5'] = x__build_existing_lookups__mutmut_5 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_6'] = x__build_existing_lookups__mutmut_6 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_7'] = x__build_existing_lookups__mutmut_7 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_8'] = x__build_existing_lookups__mutmut_8 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_9'] = x__build_existing_lookups__mutmut_9 # type: ignore # mutmut generated
mutants_x__build_existing_lookups__mutmut['x__build_existing_lookups__mutmut_10'] = x__build_existing_lookups__mutmut_10 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__partition_inventory_items__mutmut)
def _partition_inventory_items(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_orig(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_1(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = None
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_2(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = None
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_3(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = None
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_4(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.upper()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_5(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = None
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_6(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(None)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_7(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key not in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_8(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(None)
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_9(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key not in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_10(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(None)
        else:
            pending.append((title, note_type))
    return synthesized, pending


def x__partition_inventory_items__mutmut_11(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append(None)
    return synthesized, pending

mutants_x__partition_inventory_items__mutmut['_mutmut_orig'] = x__partition_inventory_items__mutmut_orig # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_1'] = x__partition_inventory_items__mutmut_1 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_2'] = x__partition_inventory_items__mutmut_2 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_3'] = x__partition_inventory_items__mutmut_3 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_4'] = x__partition_inventory_items__mutmut_4 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_5'] = x__partition_inventory_items__mutmut_5 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_6'] = x__partition_inventory_items__mutmut_6 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_7'] = x__partition_inventory_items__mutmut_7 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_8'] = x__partition_inventory_items__mutmut_8 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_9'] = x__partition_inventory_items__mutmut_9 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_10'] = x__partition_inventory_items__mutmut_10 # type: ignore # mutmut generated
mutants_x__partition_inventory_items__mutmut['x__partition_inventory_items__mutmut_11'] = x__partition_inventory_items__mutmut_11 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__parse_single_atomic_note__mutmut)
def _parse_single_atomic_note(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_orig(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_1(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = None
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_2(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get(None)
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_3(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("XXtitleXX")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_4(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("TITLE")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_5(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) and not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_6(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_7(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_8(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = None
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_9(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get(None)
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_10(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("XXtypeXX")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_11(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("TYPE")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_12(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = None
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_13(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(None)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_14(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = None
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_15(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = None

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_16(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = None
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_17(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(None).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_18(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get(None, "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_19(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", None)).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_20(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_21(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", )).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_22(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("XXdefinitionXX", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_23(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("DEFINITION", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_24(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "XXXX")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_25(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = None
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_26(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get(None, [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_27(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", None)
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_28(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get([])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_29(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", )
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_30(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("XXdirect_relationsXX", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_31(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("DIRECT_RELATIONS", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_32(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = None

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_33(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(None)

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_34(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(None) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_35(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) or r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_36(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = ""
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_37(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = None
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_38(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get(None)
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_39(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("XXcausal_matrixXX")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_40(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("CAUSAL_MATRIX")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_41(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = None

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_42(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=None,
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_43(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=None,
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_44(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=None,
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_45(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_46(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_47(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_48(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(None),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_49(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get(None, "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_50(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", None)),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_51(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_52(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", )),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_53(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("XXcauseXX", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_54(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("CAUSE", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_55(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "XXXX")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_56(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(None),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_57(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get(None, "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_58(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", None)),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_59(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_60(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", )),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_61(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("XXeffectXX", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_62(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("EFFECT", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_63(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "XXXX")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_64(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(None),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_65(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get(None, "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_66(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", None)),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_67(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_68(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", )),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_69(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("XXepistemic_attributionXX", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_70(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("EPISTEMIC_ATTRIBUTION", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_71(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "XXXX")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_72(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = ""
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_73(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = None
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_74(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get(None)
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_75(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("XXcross_contextXX")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_76(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("CROSS_CONTEXT")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_77(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = None

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_78(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=None,
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_79(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=None,
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_80(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=None,
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_81(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_82(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_83(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_84(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(None),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_85(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get(None, "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_86(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", None)),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_87(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_88(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", )),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_89(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("XXprecursorsXX", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_90(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("PRECURSORS", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_91(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "XXXX")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_92(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(None),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_93(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get(None, "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_94(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", None)),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_95(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_96(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", )),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_97(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("XXlateral_eventsXX", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_98(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("LATERAL_EVENTS", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_99(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "XXXX")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_100(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(None),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_101(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get(None, "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_102(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", None)),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_103(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_104(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", )),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_105(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("XXaftermathXX", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_106(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("AFTERMATH", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_107(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "XXXX")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_108(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = None
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_109(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get(None, [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_110(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", None)
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_111(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get([])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_112(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", )
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_113(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("XXaliasesXX", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_114(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("ALIASES", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_115(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = None
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_116(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(None)
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_117(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) or a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_118(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = None
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_119(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get(None, [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_120(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", None)
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_121(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get([])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_122(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", )
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_123(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("XXcontent_tagsXX", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_124(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("CONTENT_TAGS", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_125(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = None

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_126(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(None)

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_127(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) or t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_128(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=None,
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_129(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=None,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_130(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=None,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_131(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=None,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_132(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=None,
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_133(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=None,
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_134(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=None,
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_135(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=None,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_136(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=None,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_137(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=None,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_138(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=None,
    )


def x__parse_single_atomic_note__mutmut_139(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_140(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_141(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_142(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_143(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_144(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_145(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_146(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_147(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_148(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_149(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        )


def x__parse_single_atomic_note__mutmut_150(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(None),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_151(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(None),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_152(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get(None, compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_153(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", None)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_154(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get(compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_155(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", )),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_156(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("XXdomainXX", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_157(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("DOMAIN", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_158(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(None),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_159(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get(None, "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_160(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", None)),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_161(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_162(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", )),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_163(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("XXclusterXX", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_164(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("CLUSTER", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_165(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "XXXX")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_166(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(None),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_167(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get(None, compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_168(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", None)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_169(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get(compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_170(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", )),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_171(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("XXsourceXX", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


def x__parse_single_atomic_note__mutmut_172(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get("type")
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("SOURCE", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )

mutants_x__parse_single_atomic_note__mutmut['_mutmut_orig'] = x__parse_single_atomic_note__mutmut_orig # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_1'] = x__parse_single_atomic_note__mutmut_1 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_2'] = x__parse_single_atomic_note__mutmut_2 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_3'] = x__parse_single_atomic_note__mutmut_3 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_4'] = x__parse_single_atomic_note__mutmut_4 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_5'] = x__parse_single_atomic_note__mutmut_5 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_6'] = x__parse_single_atomic_note__mutmut_6 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_7'] = x__parse_single_atomic_note__mutmut_7 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_8'] = x__parse_single_atomic_note__mutmut_8 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_9'] = x__parse_single_atomic_note__mutmut_9 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_10'] = x__parse_single_atomic_note__mutmut_10 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_11'] = x__parse_single_atomic_note__mutmut_11 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_12'] = x__parse_single_atomic_note__mutmut_12 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_13'] = x__parse_single_atomic_note__mutmut_13 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_14'] = x__parse_single_atomic_note__mutmut_14 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_15'] = x__parse_single_atomic_note__mutmut_15 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_16'] = x__parse_single_atomic_note__mutmut_16 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_17'] = x__parse_single_atomic_note__mutmut_17 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_18'] = x__parse_single_atomic_note__mutmut_18 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_19'] = x__parse_single_atomic_note__mutmut_19 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_20'] = x__parse_single_atomic_note__mutmut_20 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_21'] = x__parse_single_atomic_note__mutmut_21 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_22'] = x__parse_single_atomic_note__mutmut_22 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_23'] = x__parse_single_atomic_note__mutmut_23 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_24'] = x__parse_single_atomic_note__mutmut_24 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_25'] = x__parse_single_atomic_note__mutmut_25 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_26'] = x__parse_single_atomic_note__mutmut_26 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_27'] = x__parse_single_atomic_note__mutmut_27 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_28'] = x__parse_single_atomic_note__mutmut_28 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_29'] = x__parse_single_atomic_note__mutmut_29 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_30'] = x__parse_single_atomic_note__mutmut_30 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_31'] = x__parse_single_atomic_note__mutmut_31 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_32'] = x__parse_single_atomic_note__mutmut_32 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_33'] = x__parse_single_atomic_note__mutmut_33 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_34'] = x__parse_single_atomic_note__mutmut_34 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_35'] = x__parse_single_atomic_note__mutmut_35 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_36'] = x__parse_single_atomic_note__mutmut_36 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_37'] = x__parse_single_atomic_note__mutmut_37 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_38'] = x__parse_single_atomic_note__mutmut_38 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_39'] = x__parse_single_atomic_note__mutmut_39 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_40'] = x__parse_single_atomic_note__mutmut_40 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_41'] = x__parse_single_atomic_note__mutmut_41 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_42'] = x__parse_single_atomic_note__mutmut_42 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_43'] = x__parse_single_atomic_note__mutmut_43 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_44'] = x__parse_single_atomic_note__mutmut_44 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_45'] = x__parse_single_atomic_note__mutmut_45 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_46'] = x__parse_single_atomic_note__mutmut_46 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_47'] = x__parse_single_atomic_note__mutmut_47 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_48'] = x__parse_single_atomic_note__mutmut_48 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_49'] = x__parse_single_atomic_note__mutmut_49 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_50'] = x__parse_single_atomic_note__mutmut_50 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_51'] = x__parse_single_atomic_note__mutmut_51 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_52'] = x__parse_single_atomic_note__mutmut_52 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_53'] = x__parse_single_atomic_note__mutmut_53 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_54'] = x__parse_single_atomic_note__mutmut_54 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_55'] = x__parse_single_atomic_note__mutmut_55 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_56'] = x__parse_single_atomic_note__mutmut_56 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_57'] = x__parse_single_atomic_note__mutmut_57 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_58'] = x__parse_single_atomic_note__mutmut_58 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_59'] = x__parse_single_atomic_note__mutmut_59 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_60'] = x__parse_single_atomic_note__mutmut_60 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_61'] = x__parse_single_atomic_note__mutmut_61 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_62'] = x__parse_single_atomic_note__mutmut_62 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_63'] = x__parse_single_atomic_note__mutmut_63 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_64'] = x__parse_single_atomic_note__mutmut_64 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_65'] = x__parse_single_atomic_note__mutmut_65 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_66'] = x__parse_single_atomic_note__mutmut_66 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_67'] = x__parse_single_atomic_note__mutmut_67 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_68'] = x__parse_single_atomic_note__mutmut_68 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_69'] = x__parse_single_atomic_note__mutmut_69 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_70'] = x__parse_single_atomic_note__mutmut_70 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_71'] = x__parse_single_atomic_note__mutmut_71 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_72'] = x__parse_single_atomic_note__mutmut_72 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_73'] = x__parse_single_atomic_note__mutmut_73 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_74'] = x__parse_single_atomic_note__mutmut_74 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_75'] = x__parse_single_atomic_note__mutmut_75 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_76'] = x__parse_single_atomic_note__mutmut_76 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_77'] = x__parse_single_atomic_note__mutmut_77 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_78'] = x__parse_single_atomic_note__mutmut_78 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_79'] = x__parse_single_atomic_note__mutmut_79 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_80'] = x__parse_single_atomic_note__mutmut_80 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_81'] = x__parse_single_atomic_note__mutmut_81 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_82'] = x__parse_single_atomic_note__mutmut_82 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_83'] = x__parse_single_atomic_note__mutmut_83 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_84'] = x__parse_single_atomic_note__mutmut_84 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_85'] = x__parse_single_atomic_note__mutmut_85 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_86'] = x__parse_single_atomic_note__mutmut_86 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_87'] = x__parse_single_atomic_note__mutmut_87 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_88'] = x__parse_single_atomic_note__mutmut_88 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_89'] = x__parse_single_atomic_note__mutmut_89 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_90'] = x__parse_single_atomic_note__mutmut_90 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_91'] = x__parse_single_atomic_note__mutmut_91 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_92'] = x__parse_single_atomic_note__mutmut_92 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_93'] = x__parse_single_atomic_note__mutmut_93 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_94'] = x__parse_single_atomic_note__mutmut_94 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_95'] = x__parse_single_atomic_note__mutmut_95 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_96'] = x__parse_single_atomic_note__mutmut_96 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_97'] = x__parse_single_atomic_note__mutmut_97 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_98'] = x__parse_single_atomic_note__mutmut_98 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_99'] = x__parse_single_atomic_note__mutmut_99 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_100'] = x__parse_single_atomic_note__mutmut_100 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_101'] = x__parse_single_atomic_note__mutmut_101 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_102'] = x__parse_single_atomic_note__mutmut_102 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_103'] = x__parse_single_atomic_note__mutmut_103 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_104'] = x__parse_single_atomic_note__mutmut_104 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_105'] = x__parse_single_atomic_note__mutmut_105 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_106'] = x__parse_single_atomic_note__mutmut_106 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_107'] = x__parse_single_atomic_note__mutmut_107 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_108'] = x__parse_single_atomic_note__mutmut_108 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_109'] = x__parse_single_atomic_note__mutmut_109 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_110'] = x__parse_single_atomic_note__mutmut_110 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_111'] = x__parse_single_atomic_note__mutmut_111 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_112'] = x__parse_single_atomic_note__mutmut_112 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_113'] = x__parse_single_atomic_note__mutmut_113 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_114'] = x__parse_single_atomic_note__mutmut_114 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_115'] = x__parse_single_atomic_note__mutmut_115 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_116'] = x__parse_single_atomic_note__mutmut_116 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_117'] = x__parse_single_atomic_note__mutmut_117 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_118'] = x__parse_single_atomic_note__mutmut_118 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_119'] = x__parse_single_atomic_note__mutmut_119 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_120'] = x__parse_single_atomic_note__mutmut_120 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_121'] = x__parse_single_atomic_note__mutmut_121 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_122'] = x__parse_single_atomic_note__mutmut_122 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_123'] = x__parse_single_atomic_note__mutmut_123 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_124'] = x__parse_single_atomic_note__mutmut_124 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_125'] = x__parse_single_atomic_note__mutmut_125 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_126'] = x__parse_single_atomic_note__mutmut_126 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_127'] = x__parse_single_atomic_note__mutmut_127 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_128'] = x__parse_single_atomic_note__mutmut_128 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_129'] = x__parse_single_atomic_note__mutmut_129 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_130'] = x__parse_single_atomic_note__mutmut_130 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_131'] = x__parse_single_atomic_note__mutmut_131 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_132'] = x__parse_single_atomic_note__mutmut_132 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_133'] = x__parse_single_atomic_note__mutmut_133 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_134'] = x__parse_single_atomic_note__mutmut_134 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_135'] = x__parse_single_atomic_note__mutmut_135 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_136'] = x__parse_single_atomic_note__mutmut_136 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_137'] = x__parse_single_atomic_note__mutmut_137 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_138'] = x__parse_single_atomic_note__mutmut_138 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_139'] = x__parse_single_atomic_note__mutmut_139 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_140'] = x__parse_single_atomic_note__mutmut_140 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_141'] = x__parse_single_atomic_note__mutmut_141 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_142'] = x__parse_single_atomic_note__mutmut_142 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_143'] = x__parse_single_atomic_note__mutmut_143 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_144'] = x__parse_single_atomic_note__mutmut_144 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_145'] = x__parse_single_atomic_note__mutmut_145 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_146'] = x__parse_single_atomic_note__mutmut_146 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_147'] = x__parse_single_atomic_note__mutmut_147 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_148'] = x__parse_single_atomic_note__mutmut_148 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_149'] = x__parse_single_atomic_note__mutmut_149 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_150'] = x__parse_single_atomic_note__mutmut_150 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_151'] = x__parse_single_atomic_note__mutmut_151 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_152'] = x__parse_single_atomic_note__mutmut_152 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_153'] = x__parse_single_atomic_note__mutmut_153 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_154'] = x__parse_single_atomic_note__mutmut_154 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_155'] = x__parse_single_atomic_note__mutmut_155 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_156'] = x__parse_single_atomic_note__mutmut_156 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_157'] = x__parse_single_atomic_note__mutmut_157 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_158'] = x__parse_single_atomic_note__mutmut_158 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_159'] = x__parse_single_atomic_note__mutmut_159 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_160'] = x__parse_single_atomic_note__mutmut_160 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_161'] = x__parse_single_atomic_note__mutmut_161 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_162'] = x__parse_single_atomic_note__mutmut_162 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_163'] = x__parse_single_atomic_note__mutmut_163 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_164'] = x__parse_single_atomic_note__mutmut_164 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_165'] = x__parse_single_atomic_note__mutmut_165 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_166'] = x__parse_single_atomic_note__mutmut_166 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_167'] = x__parse_single_atomic_note__mutmut_167 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_168'] = x__parse_single_atomic_note__mutmut_168 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_169'] = x__parse_single_atomic_note__mutmut_169 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_170'] = x__parse_single_atomic_note__mutmut_170 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_171'] = x__parse_single_atomic_note__mutmut_171 # type: ignore # mutmut generated
mutants_x__parse_single_atomic_note__mutmut['x__parse_single_atomic_note__mutmut_172'] = x__parse_single_atomic_note__mutmut_172 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class SynthesizeAtomicBatchUseCase:
    """Batched Atomic Note synthesis and incremental reconciliation orchestrator."""

    @_mutmut_mutated(mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut)
    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_orig(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_1(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 6,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_2(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is not None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_3(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError(None)
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_4(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("XXllm_synthesis_port must be providedXX")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_5(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("LLM_SYNTHESIS_PORT MUST BE PROVIDED")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_6(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is not None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_7(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError(None)
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_8(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("XXvault_port must be providedXX")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_9(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("VAULT_PORT MUST BE PROVIDED")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_10(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = None
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_11(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = None
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_12(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = None
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_13(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(None, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_14(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, None)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_15(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_16(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, )
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_17(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(2, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_18(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = None
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_19(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = None

    def xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_20(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider and NoOpPromptProviderPort()

    @_mutmut_mutated(mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut)
    def _synthesize_chunk(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_orig(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_1(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = None

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_2(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"XXtitleXX": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_3(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"TITLE": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_4(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "XXtypeXX": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_5(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "TYPE": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_6(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = None
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_7(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            None,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_8(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=None,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_9(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=None,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_10(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=None,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_11(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=None,
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_12(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_13(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_14(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_15(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_16(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_17(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(None, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_18(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=None),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_19(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_20(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_21(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=True),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_22(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = None
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_23(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=None,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_24(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=None,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_25(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_26(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_27(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_28(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_29(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = None
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_30(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_31(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = None
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_32(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=None,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_33(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=None,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_34(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=None,
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_35(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=None,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_36(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=None,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_37(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_38(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_39(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_40(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_41(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_42(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = None
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_43(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(None)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_44(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_45(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                None
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_46(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(None).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_47(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = None
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_48(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) or (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_49(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(None, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_50(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, None)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_51(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_52(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, )):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_53(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(None)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_54(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(None)
                notes.append(note)
        return notes

    def xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_55(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id
            if isinstance(compendium.channel_id, ChannelId)
            else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(None)
        return notes

    @_mutmut_mutated(mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut)
    def execute(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_orig(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_1(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = None
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_2(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = None
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_3(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(None)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_4(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = None

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_5(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            None, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_6(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, None, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_7(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, None
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_8(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_9(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_10(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_11(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(None, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_12(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, None, self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_13(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), None):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_14(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_15(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_16(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), ):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_17(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(1, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_18(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = None
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_19(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i - self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_20(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(None)

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_21(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(None, compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_22(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, None, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_23(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=None))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_24(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(compendium, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_25(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, user=user))

        return synthesized_notes

    def xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_26(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, ))

        return synthesized_notes

mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['_mutmut_orig'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_1'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_2'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_3'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_4'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_5'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_6'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_7'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_8'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_9'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_10'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_11'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_12'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_13'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_14'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_15'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_16'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_17'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_18'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_19'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut['xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_20'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ__init____mutmut_20 # type: ignore # mutmut generated

mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['_mutmut_orig'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_1'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_2'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_3'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_4'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_5'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_6'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_7'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_8'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_9'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_10'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_11'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_12'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_13'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_14'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_15'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_16'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_17'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_17 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_18'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_18 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_19'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_19 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_20'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_20 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_21'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_21 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_22'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_23'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_23 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_24'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_24 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_25'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_25 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_26'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_26 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_27'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_27 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_28'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_28 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_29'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_29 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_30'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_30 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_31'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_31 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_32'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_32 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_33'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_33 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_34'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_34 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_35'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_35 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_36'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_36 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_37'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_37 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_38'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_38 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_39'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_39 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_40'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_40 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_41'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_41 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_42'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_42 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_43'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_43 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_44'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_44 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_45'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_45 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_46'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_46 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_47'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_47 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_48'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_48 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_49'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_49 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_50'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_50 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_51'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_51 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_52'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_52 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_53'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_53 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_54'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_54 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut['xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_55'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁ_synthesize_chunk__mutmut_55 # type: ignore # mutmut generated

mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['_mutmut_orig'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_1'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_2'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_3'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_4'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_5'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_6'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_7'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_8'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_9'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_10'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_11'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_12'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_13'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_14'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_15'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_16'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_17'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_18'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_19'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_20'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_21'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_22'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_23'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_24'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_25'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut['xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_26'] = SynthesizeAtomicBatchUseCase.xǁSynthesizeAtomicBatchUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
