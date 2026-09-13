"""Stage 7 Use Case: Vault Entity Resolution & Duplicate Note Unification.

Detects duplicate entities in the Obsidian Second Brain vault using shared aliases,
cross-referencing title-to-alias mappings, and honorific normalization.
Non-destructively merges duplicate notes, rewrites inbound [[WikiLinks]] across the
entire vault and Maps of Content (MOCs), synchronizes _index.json, and cleans up
redundant files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import AtomicNote
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
)


@dataclass(frozen=True)
class DuplicateCluster:
    """Represents a set of duplicate notes resolved to a single canonical identity."""

    canonical_title: NoteTitle
    merged_titles: tuple[NoteTitle, ...]
    links_rewritten_count: int


@dataclass(frozen=True)
class DeduplicationReport:
    """Summary of the Stage 7 vault deduplication execution."""

    clusters: tuple[DuplicateCluster, ...]

    @property
    def duplicates_unified_count(self) -> int:
        return len(self.clusters)

    @property
    def total_links_rewritten(self) -> int:
        return sum(c.links_rewritten_count for c in self.clusters)


class UnifyDuplicateNotesUseCase:
    """Stage 7: Graph Entity Resolution and Duplicate Unification."""

    def __init__(self, vault_port: VaultRepositoryPort) -> None:
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
        return norm_a == norm_b and len(norm_a) >= 4

    def _merge_notes(self, canonical: AtomicNote, redundant: AtomicNote) -> AtomicNote:
        """Merge redundant note into canonical note non-destructively."""
        canonical_lower = canonical.title.value.lower()
        merged_aliases_set: set[str] = set()
        for a in canonical.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        for a in redundant.aliases:
            if a.lower() != canonical_lower:
                merged_aliases_set.add(a)
        if redundant.title.value.lower() != canonical_lower:
            merged_aliases_set.add(redundant.title.value)

        merged_aliases = tuple(sorted(merged_aliases_set))

        # 2. Merge tags
        merged_tags = tuple(sorted(set(canonical.content_tags) | set(redundant.content_tags)))

        # 3. Merge direct relations (excluding self references)
        excluded_titles = {canonical.title.value.lower(), redundant.title.value.lower()}
        merged_relations_dict: dict[str, NoteTitle] = {}
        for r in canonical.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r
        for r in redundant.direct_relations:
            if r.value.lower() not in excluded_titles:
                merged_relations_dict[r.value.lower()] = r

        merged_relations = tuple(merged_relations_dict.values())

        # 4. Merge definitions
        def_canonical = canonical.definition.strip()
        def_redundant = redundant.definition.strip()
        if def_canonical == def_redundant or def_redundant in def_canonical:
            merged_def = def_canonical
        elif def_canonical in def_redundant:
            merged_def = def_redundant
        else:
            merged_def = f"{def_canonical}\n\n{def_redundant}"

        # 5. Merge causal matrix
        merged_cm: CausalMatrix | None = canonical.causal_matrix
        if redundant.causal_matrix is not None:
            if merged_cm is None:
                merged_cm = redundant.causal_matrix
            else:
                cause = merged_cm.cause or redundant.causal_matrix.cause
                effect = merged_cm.effect or redundant.causal_matrix.effect
                attrib = (
                    merged_cm.epistemic_attribution or redundant.causal_matrix.epistemic_attribution
                )
                merged_cm = CausalMatrix(cause=cause, effect=effect, epistemic_attribution=attrib)

        # 6. Merge cross context
        merged_cc: CrossContextRelations | None = canonical.cross_context
        if redundant.cross_context is not None:
            if merged_cc is None:
                merged_cc = redundant.cross_context
            else:
                pre = merged_cc.precursors or redundant.cross_context.precursors
                lat = merged_cc.lateral_events or redundant.cross_context.lateral_events
                aft = merged_cc.aftermath or redundant.cross_context.aftermath
                merged_cc = CrossContextRelations(precursors=pre, lateral_events=lat, aftermath=aft)

        domain = canonical.domain or redundant.domain
        cluster = canonical.cluster or redundant.cluster
        source = canonical.source or redundant.source

        return AtomicNote(
            title=canonical.title,
            note_type=canonical.note_type,
            definition=merged_def,
            content_tags=merged_tags,
            domain=domain,
            cluster=cluster,
            source=source,
            aliases=merged_aliases,
            direct_relations=merged_relations,
            causal_matrix=merged_cm,
            cross_context=merged_cc,
        )

    def execute(self) -> DeduplicationReport:
        """Execute Stage 7 duplicate unification across the entire vault graph."""
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
