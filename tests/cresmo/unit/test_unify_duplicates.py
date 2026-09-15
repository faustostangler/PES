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

    @pytest.mark.parametrize(
        ("input_title", "expected"),
        [
            ("Dom Afonso Henriques", "afonso henriques"),
            ("dom afonso henriques", "afonso henriques"),
            ("Dona Maria I", "maria i"),
            ("dona maria i", "maria i"),
            ("D. Pedro II", "pedro ii"),
            ("d. pedro ii", "pedro ii"),
            ("D João VI", "joão vi"),
            ("d joão vi", "joão vi"),
            ("  dom   manuel  ", "manuel"),
            ("Batalha de São Mamede (1128)", "batalha de são mamede 1128"),
            ("Tratado_de-Zamora...1143", "tratado de zamora 1143"),
            ("Vilfredo Pareto", "vilfredo pareto"),
        ],
    )
    def test_normalize_for_matching_exhaustive(
        self,
        mock_vault: InMemoryVaultAdapter,
        input_title: str,
        expected: str,
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        assert use_case._normalize_for_matching(input_title) == expected

    def test_are_duplicates_evaluation_branches(self, mock_vault: InMemoryVaultAdapter) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)

        base_note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador da circulação de elites e ótimo paretiano.",
            aliases=("Pareto", "V. Pareto"),
        )

        # 1. Identical titles (self-comparison) -> False
        assert use_case._are_duplicates(base_note, base_note) is False

        # 2. Title in aliases
        alias_match_note = AtomicNote(
            title=NoteTitle("Pareto"),
            note_type=NoteType.ENTITY,
            definition="Economista e pensador italiano pioneiro da teoria das elites.",
        )
        assert use_case._are_duplicates(base_note, alias_match_note) is True
        assert use_case._are_duplicates(alias_match_note, base_note) is True

        # 3. Shared alias
        shared_alias_note = AtomicNote(
            title=NoteTitle("Vilfredo Federico Damaso Pareto"),
            note_type=NoteType.ENTITY,
            definition="Pensador e economista pioneiro na formulação do bem-estar social.",
            aliases=("Pareto",),
        )
        assert use_case._are_duplicates(base_note, shared_alias_note) is True

        # 4. Honorific normalization match (len >= 4)
        honorific_note_a = AtomicNote(
            title=NoteTitle("Dom Afonso"),
            note_type=NoteType.ENTITY,
            definition="Rei fundador de Portugal e líder guerreiro na Batalha de Ourique.",
        )
        honorific_note_b = AtomicNote(
            title=NoteTitle("D. Afonso"),
            note_type=NoteType.ENTITY,
            definition="Rei fundador de Portugal e líder militar histórico em Guimarães.",
        )
        assert use_case._are_duplicates(honorific_note_a, honorific_note_b) is True

        # 5. Honorific normalization short length (< 4) -> False
        short_note_a = AtomicNote(
            title=NoteTitle("Dom A"),
            note_type=NoteType.ENTITY,
            definition="Short title A definition containing sufficient characters for domain validation.",
        )
        short_note_b = AtomicNote(
            title=NoteTitle("D. A"),
            note_type=NoteType.ENTITY,
            definition="Short title B definition containing sufficient characters for domain validation.",
        )
        assert use_case._are_duplicates(short_note_a, short_note_b) is False

        # 6. Completely unrelated notes -> False
        unrelated_note = AtomicNote(
            title=NoteTitle("Niccolò Machiavelli"),
            note_type=NoteType.ENTITY,
            definition="Filósofo político florentino autor de O Príncipe e Discursos.",
            aliases=("Maquiavel",),
        )
        assert use_case._are_duplicates(base_note, unrelated_note) is False

    def test_merge_notes_definition_subsets_and_concatenation(
        self,
        mock_vault: InMemoryVaultAdapter,
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)

        canonical = AtomicNote(
            title=NoteTitle("Teoria das Elites"),
            note_type=NoteType.CONCEPT,
            definition="Modelo sociológico sobre circulação de elites formulado por Pareto e Mosca.",
            domain="Ciência Política",
        )
        redundant_subset = AtomicNote(
            title=NoteTitle("Circulação de Elites"),
            note_type=NoteType.CONCEPT,
            definition="Modelo sociológico sobre circulação de elites",
            domain="Sociologia",
            cluster="Elitismo",
            source="Fabio Akita",
        )

        merged_subset = use_case._merge_notes(canonical, redundant_subset)
        assert merged_subset.definition == canonical.definition
        assert merged_subset.domain == "Ciência Política"
        assert merged_subset.cluster == "Elitismo"
        assert merged_subset.source == "Fabio Akita"

        # Redundant superset case
        canonical_short = AtomicNote(
            title=NoteTitle("Teoria das Elites"),
            note_type=NoteType.CONCEPT,
            definition="Modelo sociológico sobre circulação",
        )
        merged_superset = use_case._merge_notes(canonical_short, redundant_subset)
        assert merged_superset.definition == redundant_subset.definition

        # Disjoint definitions case
        redundant_disjoint = AtomicNote(
            title=NoteTitle("Circulação de Elites"),
            note_type=NoteType.CONCEPT,
            definition="Visão alternativa sobre grupos oligárquicos em disputa.",
        )
        merged_disjoint = use_case._merge_notes(canonical, redundant_disjoint)
        assert (
            merged_disjoint.definition
            == f"{canonical.definition}\n\n{redundant_disjoint.definition}"
        )

    def test_merge_notes_causal_matrix_and_cross_context(
        self,
        mock_vault: InMemoryVaultAdapter,
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)

        canonical_no_cm = AtomicNote(
            title=NoteTitle("Lei de Ferro da Oligarquia"),
            note_type=NoteType.CONCEPT,
            definition="Formulaçao de Robert Michels sobre organizações partidárias modernas.",
        )
        redundant_with_cm = AtomicNote(
            title=NoteTitle("Oligarquia de Ferro"),
            note_type=NoteType.CONCEPT,
            definition="Organizações inevitavelmente viram oligarquias segundo Robert Michels.",
            causal_matrix=CausalMatrix(
                cause="Burocratização partidária",
                effect="Concentração de poder",
                epistemic_attribution="Michels (1911)",
            ),
            cross_context=CrossContextRelations(
                precursors="Max Weber",
                lateral_events="Sindicalismo revolucionário",
                aftermath="Fascismo italiano",
            ),
        )

        # Merge when canonical has None for causal_matrix and cross_context
        merged = use_case._merge_notes(canonical_no_cm, redundant_with_cm)
        assert merged.causal_matrix == redundant_with_cm.causal_matrix
        assert merged.cross_context == redundant_with_cm.cross_context

        # Merge when both have partial attributes
        canonical_partial = AtomicNote(
            title=NoteTitle("Lei de Ferro da Oligarquia"),
            note_type=NoteType.CONCEPT,
            definition="Formulaçao de Robert Michels em Sociologia dos Partidos Políticos.",
            causal_matrix=CausalMatrix(
                cause="Especialização técnica",
                effect="Rigidez burocrática",
                epistemic_attribution="",
            ),
            cross_context=CrossContextRelations(
                precursors="Karl Marx",
                lateral_events="",
                aftermath="",
            ),
        )
        merged_partial = use_case._merge_notes(canonical_partial, redundant_with_cm)
        assert merged_partial.causal_matrix is not None
        assert merged_partial.causal_matrix.cause == "Especialização técnica"
        assert merged_partial.causal_matrix.effect == "Rigidez burocrática"
        assert merged_partial.causal_matrix.epistemic_attribution == "Michels (1911)"
        assert merged_partial.cross_context is not None
        assert merged_partial.cross_context.precursors == "Karl Marx"
        assert merged_partial.cross_context.lateral_events == "Sindicalismo revolucionário"
        assert merged_partial.cross_context.aftermath == "Fascismo italiano"

    def test_execute_empty_vault_returns_empty_report(
        self,
        mock_vault: InMemoryVaultAdapter,
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        report = use_case.execute()
        assert report.duplicates_unified_count == 0
        assert report.total_links_rewritten == 0
        assert report.clusters == ()
