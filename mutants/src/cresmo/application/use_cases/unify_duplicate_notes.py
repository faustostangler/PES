"""Use Case: Vault Entity Resolution & Duplicate Note Unification.

Detects duplicate entities in the Obsidian Second Brain vault using shared aliases,
cross-referencing title-to-alias mappings, and honorific normalization.
Non-destructively merges duplicate notes, rewrites inbound [[WikiLinks]] across the
entire vault and Maps of Content (MOCs), synchronizes _index.json, and cleans up
redundant files.

Conforms to:
- SPEC-001: §1 (Graph Entity Resolution and Deduplication)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import AtomicNote
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True)
class DuplicateCluster:
    """Represents a set of duplicate notes resolved to a single canonical identity.

    Attributes:
        canonical_title: Canonical winning note title retained in vault.
        merged_titles: Tuple of redundant titles merged and redirected.
        links_rewritten_count: Number of markdown WikiLink references rewritten.
    """

    canonical_title: NoteTitle
    merged_titles: tuple[NoteTitle, ...]
    links_rewritten_count: int


@dataclass(frozen=True)
class DeduplicationReport:
    """Summary of the vault deduplication execution.

    Attributes:
        clusters: Tuple of all resolved duplicate clusters.
    """

    clusters: tuple[DuplicateCluster, ...]

    @property
    def duplicates_unified_count(self) -> int:
        """Total count of duplicate note clusters resolved."""
        return len(self.clusters)

    @property
    def total_links_rewritten(self) -> int:
        """Total count of inbound WikiLinks updated across vault markdown files."""
        return sum(c.links_rewritten_count for c in self.clusters)


_MIN_HONORIFIC_NORMALIZED_LENGTH: Final[int] = 4
mutants_x__merge_aliases__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__merge_aliases__mutmut)
def _merge_aliases(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_orig(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_1(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = None
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_2(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.upper()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_3(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = None
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_4(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.upper() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_5(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() == canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_6(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.upper() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_7(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() == canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_8(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(None)
    return tuple(sorted(merged_aliases_set))


def x__merge_aliases__mutmut_9(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(None)


def x__merge_aliases__mutmut_10(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(None))

mutants_x__merge_aliases__mutmut['_mutmut_orig'] = x__merge_aliases__mutmut_orig # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_1'] = x__merge_aliases__mutmut_1 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_2'] = x__merge_aliases__mutmut_2 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_3'] = x__merge_aliases__mutmut_3 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_4'] = x__merge_aliases__mutmut_4 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_5'] = x__merge_aliases__mutmut_5 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_6'] = x__merge_aliases__mutmut_6 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_7'] = x__merge_aliases__mutmut_7 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_8'] = x__merge_aliases__mutmut_8 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_9'] = x__merge_aliases__mutmut_9 # type: ignore # mutmut generated
mutants_x__merge_aliases__mutmut['x__merge_aliases__mutmut_10'] = x__merge_aliases__mutmut_10 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__merge_direct_relations__mutmut)
def _merge_direct_relations(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_orig(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_1(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = None
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_2(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.upper(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_3(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.upper()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_4(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = None
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_5(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = None
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_6(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = None
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_7(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.upper()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_8(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles or r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_9(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_10(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_11(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(None)
            merged_relations.append(r)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_12(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(None)
    return tuple(merged_relations)


def x__merge_direct_relations__mutmut_13(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    seen: set[str] = set()
    merged_relations: list[NoteTitle] = []
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        r_lower = r.value.lower()
        if r_lower not in excluded_titles and r_lower not in seen:
            seen.add(r_lower)
            merged_relations.append(r)
    return tuple(None)

mutants_x__merge_direct_relations__mutmut['_mutmut_orig'] = x__merge_direct_relations__mutmut_orig # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_1'] = x__merge_direct_relations__mutmut_1 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_2'] = x__merge_direct_relations__mutmut_2 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_3'] = x__merge_direct_relations__mutmut_3 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_4'] = x__merge_direct_relations__mutmut_4 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_5'] = x__merge_direct_relations__mutmut_5 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_6'] = x__merge_direct_relations__mutmut_6 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_7'] = x__merge_direct_relations__mutmut_7 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_8'] = x__merge_direct_relations__mutmut_8 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_9'] = x__merge_direct_relations__mutmut_9 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_10'] = x__merge_direct_relations__mutmut_10 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_11'] = x__merge_direct_relations__mutmut_11 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_12'] = x__merge_direct_relations__mutmut_12 # type: ignore # mutmut generated
mutants_x__merge_direct_relations__mutmut['x__merge_direct_relations__mutmut_13'] = x__merge_direct_relations__mutmut_13 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__merge_definitions__mutmut)
def _merge_definitions(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_orig(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_1(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = None
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_2(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = None
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_3(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant and def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_4(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical != def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_5(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant not in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


def x__merge_definitions__mutmut_6(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical not in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"

mutants_x__merge_definitions__mutmut['_mutmut_orig'] = x__merge_definitions__mutmut_orig # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_1'] = x__merge_definitions__mutmut_1 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_2'] = x__merge_definitions__mutmut_2 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_3'] = x__merge_definitions__mutmut_3 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_4'] = x__merge_definitions__mutmut_4 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_5'] = x__merge_definitions__mutmut_5 # type: ignore # mutmut generated
mutants_x__merge_definitions__mutmut['x__merge_definitions__mutmut_6'] = x__merge_definitions__mutmut_6 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__merge_causal_matrices__mutmut)
def _merge_causal_matrices(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_orig(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_1(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is not None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_2(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is not None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_3(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = None
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_4(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause and cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_5(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = None
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_6(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect and cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_7(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = None
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_8(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution and cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_9(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=None, effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_10(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=None, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_11(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, epistemic_attribution=None)


def x__merge_causal_matrices__mutmut_12(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(effect=effect, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_13(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, epistemic_attribution=attrib)


def x__merge_causal_matrices__mutmut_14(
    cm_a: CausalMatrix | None, cm_b: CausalMatrix | None
) -> CausalMatrix | None:
    """Merge two causal matrices preserving non-empty attributes."""
    if cm_b is None:
        return cm_a
    if cm_a is None:
        return cm_b
    cause = cm_a.cause or cm_b.cause
    effect = cm_a.effect or cm_b.effect
    attrib = cm_a.epistemic_attribution or cm_b.epistemic_attribution
    return CausalMatrix(cause=cause, effect=effect, )

mutants_x__merge_causal_matrices__mutmut['_mutmut_orig'] = x__merge_causal_matrices__mutmut_orig # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_1'] = x__merge_causal_matrices__mutmut_1 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_2'] = x__merge_causal_matrices__mutmut_2 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_3'] = x__merge_causal_matrices__mutmut_3 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_4'] = x__merge_causal_matrices__mutmut_4 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_5'] = x__merge_causal_matrices__mutmut_5 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_6'] = x__merge_causal_matrices__mutmut_6 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_7'] = x__merge_causal_matrices__mutmut_7 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_8'] = x__merge_causal_matrices__mutmut_8 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_9'] = x__merge_causal_matrices__mutmut_9 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_10'] = x__merge_causal_matrices__mutmut_10 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_11'] = x__merge_causal_matrices__mutmut_11 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_12'] = x__merge_causal_matrices__mutmut_12 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_13'] = x__merge_causal_matrices__mutmut_13 # type: ignore # mutmut generated
mutants_x__merge_causal_matrices__mutmut['x__merge_causal_matrices__mutmut_14'] = x__merge_causal_matrices__mutmut_14 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__merge_cross_contexts__mutmut)
def _merge_cross_contexts(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_orig(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_1(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is not None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_2(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is not None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_3(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = None
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_4(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors and cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_5(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = None
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_6(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events and cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_7(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = None
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_8(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath and cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_9(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=None, lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_10(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=None, aftermath=aft)


def x__merge_cross_contexts__mutmut_11(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=None)


def x__merge_cross_contexts__mutmut_12(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(lateral_events=lat, aftermath=aft)


def x__merge_cross_contexts__mutmut_13(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, aftermath=aft)


def x__merge_cross_contexts__mutmut_14(
    cc_a: CrossContextRelations | None, cc_b: CrossContextRelations | None
) -> CrossContextRelations | None:
    """Merge two cross-context relation triads preserving non-empty attributes."""
    if cc_b is None:
        return cc_a
    if cc_a is None:
        return cc_b
    pre = cc_a.precursors or cc_b.precursors
    lat = cc_a.lateral_events or cc_b.lateral_events
    aft = cc_a.aftermath or cc_b.aftermath
    return CrossContextRelations(precursors=pre, lateral_events=lat, )

mutants_x__merge_cross_contexts__mutmut['_mutmut_orig'] = x__merge_cross_contexts__mutmut_orig # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_1'] = x__merge_cross_contexts__mutmut_1 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_2'] = x__merge_cross_contexts__mutmut_2 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_3'] = x__merge_cross_contexts__mutmut_3 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_4'] = x__merge_cross_contexts__mutmut_4 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_5'] = x__merge_cross_contexts__mutmut_5 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_6'] = x__merge_cross_contexts__mutmut_6 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_7'] = x__merge_cross_contexts__mutmut_7 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_8'] = x__merge_cross_contexts__mutmut_8 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_9'] = x__merge_cross_contexts__mutmut_9 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_10'] = x__merge_cross_contexts__mutmut_10 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_11'] = x__merge_cross_contexts__mutmut_11 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_12'] = x__merge_cross_contexts__mutmut_12 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_13'] = x__merge_cross_contexts__mutmut_13 # type: ignore # mutmut generated
mutants_x__merge_cross_contexts__mutmut['x__merge_cross_contexts__mutmut_14'] = x__merge_cross_contexts__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class UnifyDuplicateNotesUseCase:
    """Graph Entity Resolution and Duplicate Unification orchestrator."""

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut)
    def __init__(self, vault_port: VaultRepositoryPort) -> None:
        """Initialize use case with vault persistence port.

        Args:
            vault_port: Port providing vault atomic note read/write/delete operations.
        """
        self.vault_port = vault_port

    def xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_orig(self, vault_port: VaultRepositoryPort) -> None:
        """Initialize use case with vault persistence port.

        Args:
            vault_port: Port providing vault atomic note read/write/delete operations.
        """
        self.vault_port = vault_port

    def xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1(self, vault_port: VaultRepositoryPort) -> None:
        """Initialize use case with vault persistence port.

        Args:
            vault_port: Port providing vault atomic note read/write/delete operations.
        """
        self.vault_port = None

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut)
    def _normalize_for_matching(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_orig(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = None
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.upper().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("XXdom XX", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("DOM ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "XXdona XX", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "DONA ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "XXd. XX", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "D. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "XXd XX"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "D "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(None):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = None
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                return
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(None, " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", None, cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", None).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(" ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", ).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"XX[\s\-_.,()]+XX", " ", cleaned).strip()

    def xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", "XX XX", cleaned).strip()

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut)
    def _are_duplicates(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_orig(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.upper() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() != note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.upper():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return True

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = None
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.upper()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = None

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.upper()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = None
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.upper() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = None

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.upper() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b and t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a not in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b not in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return False

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = None
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a | aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return False

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = None
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(None)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = None
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(None)
        return norm_a == norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b or len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a != norm_b and len(norm_a) >= _MIN_HONORIFIC_NORMALIZED_LENGTH

    def xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26(self, note_a: AtomicNote, note_b: AtomicNote) -> bool:
        """Evaluate whether two atomic notes represent the same domain entity."""
        if note_a.title.value.lower() == note_b.title.value.lower():
            return False

        t_a = note_a.title.value.lower()
        t_b = note_b.title.value.lower()

        aliases_a = {a.lower() for a in note_a.aliases}
        aliases_b = {a.lower() for a in note_b.aliases}

        # 1. Direct title in aliases match
        if t_a in aliases_b or t_b in aliases_a:
            return True

        # 2. Shared aliases collision
        shared_aliases = aliases_a & aliases_b
        if shared_aliases:
            return True

        # 3. Honorific prefix normalization match
        norm_a = self._normalize_for_matching(t_a)
        norm_b = self._normalize_for_matching(t_b)
        return norm_a == norm_b and len(norm_a) > _MIN_HONORIFIC_NORMALIZED_LENGTH

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut)
    def _merge_notes(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_orig(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = None
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(None, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, None)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, )
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = None
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(None)
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(None))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) & set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(None) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(None)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = None
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(None, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, None)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, )
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = None
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(None, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, None)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, )
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = None
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(None, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, None)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, )
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = None

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(None, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, None)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, )

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=None,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=None,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=None,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=None,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=None,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=None,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=None,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=None,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=None,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=None,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=None,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain and redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster and redundant.cluster,
            source=canonical.source or redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        merged_aliases = _merge_aliases(canonical, redundant)
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))
        merged_relations = _merge_direct_relations(canonical, redundant)
        merged_def = _merge_definitions(canonical.definition, redundant.definition)
        merged_cm = _merge_causal_matrices(canonical.causal_matrix, redundant.causal_matrix)
        merged_cc = _merge_cross_contexts(canonical.cross_context, redundant.cross_context)

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=canonical.domain or redundant.domain,
            cluster=canonical.cluster or redundant.cluster,
            source=canonical.source and redundant.source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    @_mutmut_mutated(mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut)
    def execute(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_orig(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = None
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=None)

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = None
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = None

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(None):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = None
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.upper()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a not in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                break

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = None
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = None
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = None

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 1

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i - 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 2 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = None
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.upper()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b not in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    break

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(None, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, None):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, ):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) >= len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) - 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 51:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = None
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = None
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = None
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = None

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = None

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(None, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, None)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, )

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(None)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(None)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(None)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = None
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        None, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, None
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten = rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten -= rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(None)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(None)
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.upper())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = None

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(None)
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.upper())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    None
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=None,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=None,
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=None,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(None),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(clusters_found))

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=None)

    def xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i, note_a in enumerate(notes):
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for note_b in notes[i + 1 :]:
                key_b = note_b.title.value.lower()
                if key_b in already_merged:
                    continue

                if self._are_duplicates(current_canonical, note_b):
                    # Elect canonical: note with longer definition or more relations
                    if len(note_b.definition) > len(current_canonical.definition) + 50:
                        canonical_candidate = note_b
                        redundant_candidate = current_canonical
                    else:
                        canonical_candidate = current_canonical
                        redundant_candidate = note_b

                    # Perform non-destructive merge
                    merged_canonical = self._merge_notes(canonical_candidate, redundant_candidate)

                    # Persist merged canonical note
                    self.vault_port.save_atomic_note(merged_canonical)
                    self.vault_port.update_index_entry(merged_canonical)

                    # Delete redundant note from filesystem and index
                    self.vault_port.delete_atomic_note(redundant_candidate)

                    # Rewrite inbound WikiLinks across vault & MOCs
                    rewritten = self.vault_port.rewrite_wiki_links(
                        redundant_candidate.title, merged_canonical.title
                    )
                    total_rewritten += rewritten

                    merged_titles_in_cluster.append(redundant_candidate.title)
                    already_merged.add(redundant_candidate.title.value.lower())
                    current_canonical = merged_canonical

            if merged_titles_in_cluster:
                already_merged.add(current_canonical.title.value.lower())
                clusters_found.append(
                    DuplicateCluster(
                        canonical_title=current_canonical.title,
                        merged_titles=tuple(merged_titles_in_cluster),
                        links_rewritten_count=total_rewritten,
                    )
                )

        return DeduplicationReport(clusters=tuple(None))

mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut['xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_normalize_for_matching__mutmut_21 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_are_duplicates__mutmut_26 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_26 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_27 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_28 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_29 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_30 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_31 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_32 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_33 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_34 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_35 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_36 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_37 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_38 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_39 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_40 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_41 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_42 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_43 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_44 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_45 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_46 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_47 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_48 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_49 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_50 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_51 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_52 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_53 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_54 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_55 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut['xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁ_merge_notes__mutmut_56 # type: ignore # mutmut generated

mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['_mutmut_orig'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut['xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62'] = UnifyDuplicateNotesUseCase.xǁUnifyDuplicateNotesUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
