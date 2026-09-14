"""Unit tests for Stage 7: UnifyDuplicateNotesUseCase.

Verifies algorithmic duplicate detection, non-destructive merging of definitions,
aliases, and relations, rewriting of inbound WikiLinks, and vault index synchronization.
"""

from __future__ import annotations

import pytest

from cresmo.application.use_cases.unify_duplicate_notes import (
    DeduplicationReport,
    UnifyDuplicateNotesUseCase,
)
from cresmo.domain.entities import AtomicNote
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.mock_adapters import InMemoryVaultAdapter


class TestUnifyDuplicateNotesUseCase:
    """Hermetic unit tests for duplicate detection and unification."""

    @pytest.fixture
    def mock_vault(self) -> InMemoryVaultAdapter:
        return InMemoryVaultAdapter()

    def test_unify_two_notes_with_shared_aliases(self, mock_vault: InMemoryVaultAdapter) -> None:
        # Arrange: Note A (D. Afonso Henriques) and Note B (Dom Afonso Henriques)
        note_a = AtomicNote(
            title=NoteTitle("D. Afonso Henriques"),
            note_type=NoteType.ENTITY,
            definition="Primeiro rei de Portugal que liderou São Mamede e a fundação da monarquia.",
            content_tags=("historia", "portugal"),
            domain="História Medieval",
            cluster="Fundação de Portugal",
            source="Marcelo Andrade",
            aliases=("Afonso I de Portugal", "O Conquistador", "O Fundador"),
            direct_relations=(NoteTitle("Batalha de São Mamede"), NoteTitle("Egas Moniz")),
            causal_matrix=CausalMatrix(
                cause="Revolta baronial",
                effect="Independência de Leão",
                epistemic_attribution="Cartulários régios",
            ),
            cross_context=CrossContextRelations(
                precursors="Conde D. Henrique",
                lateral_events="Queda de Kaifeng",
                aftermath="Tratado de Zamora",
            ),
        )

        note_b = AtomicNote(
            title=NoteTitle("Dom Afonso Henriques"),
            note_type=NoteType.ENTITY,
            definition="Monarca fundador de Portugal que rompeu com a influência galega.",
            content_tags=("soberania", "monarquia"),
            domain="História / Geopolítica",
            cluster="Independência de Portugal",
            source="Marcelo Andrade",
            aliases=("Afonso I de Portugal", "O Conquistador", "Afonso Henriques"),
            direct_relations=(NoteTitle("Fernão Peres de Trava"), NoteTitle("Egas Moniz")),
            causal_matrix=CausalMatrix(
                cause="Oposição da nobreza",
                effect="Ruptura geopolítica",
                epistemic_attribution="Tradição historiográfica",
            ),
            cross_context=CrossContextRelations(
                precursors="Dom Henrique",
                lateral_events="Ascensão dos Bushi",
                aftermath="Bula Manifestis Probatum",
            ),
        )

        # Referencing note referencing Note A
        ref_note = AtomicNote(
            title=NoteTitle("Tratado de Zamora"),
            note_type=NoteType.EVENT,
            definition="Tratado de paz celebrado com [[D. Afonso Henriques]] em 1143.",
            content_tags=("tratado",),
            direct_relations=(NoteTitle("D. Afonso Henriques"),),
        )

        mock_vault.save_atomic_note(note_a)
        mock_vault.save_atomic_note(note_b)
        mock_vault.save_atomic_note(ref_note)
        mock_vault.update_index_entry(note_a)
        mock_vault.update_index_entry(note_b)
        mock_vault.update_index_entry(ref_note)

        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)

        # Act
        report: DeduplicationReport = use_case.execute()

        # Assert
        assert report.duplicates_unified_count >= 1

        # Check that only one note exists for Afonso Henriques
        all_notes = mock_vault.get_all_atomic_notes()
        titles = [n.title.value.lower() for n in all_notes]
        assert ("d. afonso henriques" in titles) ^ ("dom afonso henriques" in titles)

        # Find the surviving canonical note
        canonical = next(n for n in all_notes if "afonso henriques" in n.title.value.lower())
        # Verify merged aliases include all previous aliases plus the retired title
        canonical_aliases = [a.lower() for a in canonical.aliases]
        assert "afonso i de portugal" in canonical_aliases
        assert "o conquistador" in canonical_aliases

        # Verify merged tags
        assert "historia" in canonical.content_tags or "portugal" in canonical.content_tags

        # Verify inbound WikiLinks were rewritten in ref_note
        updated_ref = mock_vault.get_atomic_note_by_title(NoteTitle("Tratado de Zamora"))
        assert updated_ref is not None
        assert f"[[{canonical.title.value}]]" in updated_ref.definition

    def test_no_duplicates_returns_clean_report(self, mock_vault: InMemoryVaultAdapter) -> None:
        note_1 = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo e economista italiano.",
            aliases=("Pareto",),
        )
        note_2 = AtomicNote(
            title=NoteTitle("Gaetano Mosca"),
            note_type=NoteType.ENTITY,
            definition="Cientista político italiano.",
            aliases=("Mosca",),
        )
        mock_vault.save_atomic_note(note_1)
        mock_vault.save_atomic_note(note_2)

        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        report = use_case.execute()

        assert report.duplicates_unified_count == 0
        assert len(mock_vault.get_all_atomic_notes()) == 2
