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


def _merge_aliases(canonical: AtomicNote, redundant: AtomicNote) -> tuple[str, ...]:
    """Merge and sort aliases excluding the canonical note's title."""
    canonical_lower = canonical.title.value.lower()
    merged_aliases_set: set[str] = {
        a for a in (*canonical.aliases, *redundant.aliases) if a.lower() != canonical_lower
    }
    if redundant.title.value.lower() != canonical_lower:
        merged_aliases_set.add(redundant.title.value)
    return tuple(sorted(merged_aliases_set))


def _merge_direct_relations(canonical: AtomicNote, redundant: AtomicNote) -> tuple[NoteTitle, ...]:
    """Merge direct relations excluding self-referencing titles."""
    excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
    merged_relations_dict: dict[str, NoteTitle] = {}
    for r in (*canonical.direct_relations, *redundant.direct_relations):
        if r.value.lower() not in excluded_titles:
            merged_relations_dict[r.value.lower()] = r
    return tuple(merged_relations_dict.values())


def _merge_definitions(canonical_def: str, redundant_def: str) -> str:
    """Merge definitions preserving full content without verbatim repetition."""
    def_canonical = canonical_def.strip()
    def_redundant = redundant_def.strip()
    if def_canonical == def_redundant or def_redundant in def_canonical:
        return def_canonical
    if def_canonical in def_redundant:
        return def_redundant
    return f"{def_canonical}\n\n{def_redundant}"


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


class UnifyDuplicateNotesUseCase:
    """Graph Entity Resolution and Duplicate Unification orchestrator."""

    def __init__(self, vault_port: VaultRepositoryPort) -> None:
        """Initialize use case with vault persistence port.

        Args:
            vault_port: Port providing vault atomic note read/write/delete operations.
        """
        self.vault_port = vault_port

    def _normalize_for_matching(self, title: str) -> str:
        """Strip honorifics, punctuation, and leading/trailing articles for similarity."""
        cleaned = title.lower().strip()
        for prefix in ("dom ", "dona ", "d. ", "d "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return re.sub(r"[\s\-_.,()]+", " ", cleaned).strip()

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

    def execute(self) -> DeduplicationReport:
        """Execute duplicate unification across the entire vault graph."""
        notes = self.vault_port.get_all_atomic_notes()
        if not notes:
            return DeduplicationReport(clusters=())

        clusters_found: list[DuplicateCluster] = []
        already_merged: set[str] = set()

        for i in range(len(notes)):
            note_a = notes[i]
            key_a = note_a.title.value.lower()
            if key_a in already_merged:
                continue

            current_canonical = note_a
            merged_titles_in_cluster: list[NoteTitle] = []
            total_rewritten = 0

            for j in range(i + 1, len(notes)):
                note_b = notes[j]
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
