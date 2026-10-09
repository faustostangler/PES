"""Unit tests for UnifyDuplicateNotesUseCase.

Verifies algorithmic duplicate detection, non-destructive merging of definitions,
aliases, and relations, rewriting of inbound WikiLinks, and vault index synchronization.
"""

from __future__ import annotations

import pytest

from cresmo.application.use_cases.unify_duplicate_notes import (
    DeduplicationReport,
    DuplicateCluster,
    UnifyDuplicateNotesUseCase,
    _merge_aliases,
    _merge_causal_matrices,
    _merge_cross_contexts,
    _merge_definitions,
    _merge_direct_relations,
)
from cresmo.domain.entities import AtomicNote
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from tests.doubles.mock_adapters import InMemoryVaultAdapter


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

    def test_merge_aliases_case_exclusion_and_redundant_addition(self) -> None:
        canonical = AtomicNote(
            title=NoteTitle("Rome"),
            note_type=NoteType.ENTITY,
            definition="Ancient capital of the Roman Empire throughout antiquity.",
            aliases=("rome", "Capital", "ROME", "Caput Mundi"),
        )
        redundant = AtomicNote(
            title=NoteTitle("Roma"),
            note_type=NoteType.ENTITY,
            definition="Italian capital and historical center of Latin civilization.",
            aliases=("ROMA", "rome", "Eternal City"),
        )
        res = _merge_aliases(canonical, redundant)
        # Excludes canonical title 'Rome' case-insensitively ('rome', 'ROME')
        assert "rome" not in res
        assert "ROME" not in res
        # Includes redundant title 'Roma'
        assert "Roma" in res
        assert "Capital" in res
        assert "Caput Mundi" in res
        assert "Eternal City" in res
        assert "ROMA" in res
        assert res == tuple(sorted(res))

        # When redundant title matches canonical title case-insensitively, it is NOT added
        redundant_same_title = AtomicNote(
            title=NoteTitle("rome"),
            note_type=NoteType.ENTITY,
            definition="Same title different case and long enough definition string.",
            aliases=("Urbs",),
        )
        res_same = _merge_aliases(canonical, redundant_same_title)
        assert "rome" not in res_same
        assert "Urbs" in res_same

    def test_merge_direct_relations_excludes_self_references_and_deduplicates(self) -> None:
        canonical = AtomicNote(
            title=NoteTitle("Empire"),
            note_type=NoteType.CONCEPT,
            definition="Sovereignty system of hierarchical political domination.",
            direct_relations=(
                NoteTitle("imperium"),
                NoteTitle("IMPERIUM"),
                NoteTitle("Colony"),
                NoteTitle("Province"),
            ),
        )
        redundant = AtomicNote(
            title=NoteTitle("Imperium"),
            note_type=NoteType.CONCEPT,
            definition="Roman command authority in provincial territories.",
            direct_relations=(
                NoteTitle("empire"),
                NoteTitle("EMPIRE"),
                NoteTitle("colony"),
                NoteTitle("Legion"),
            ),
        )
        res = _merge_direct_relations(canonical, redundant)
        values = [r.value for r in res]
        lower_values = [r.value.lower() for r in res]
        # Excluded cross-titles that would become self-references after merge
        assert "empire" not in lower_values
        assert "imperium" not in lower_values
        # Colony deduplicated case-insensitively
        assert lower_values.count("colony") == 1
        assert "Province" in values
        assert "Legion" in values
        assert len(res) == 3

    def test_are_duplicates_min_honorific_length_boundary(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # Length 4: "Dom Abcd" vs "Abcd" -> normalized is "abcd" (len 4 == _MIN_HONORIFIC_NORMALIZED_LENGTH)
        note_4a = AtomicNote(
            title=NoteTitle("Dom Abcd"),
            note_type=NoteType.ENTITY,
            definition="Valid definition containing over twenty characters.",
        )
        note_4b = AtomicNote(
            title=NoteTitle("Abcd"),
            note_type=NoteType.ENTITY,
            definition="Valid definition containing over twenty characters.",
        )
        assert use_case._are_duplicates(note_4a, note_4b) is True

        # Length 3: "Dom Abc" vs "Abc" -> normalized is "abc" (len 3 < _MIN_HONORIFIC_NORMALIZED_LENGTH)
        note_3a = AtomicNote(
            title=NoteTitle("Dom Abc"),
            note_type=NoteType.ENTITY,
            definition="Valid definition containing over twenty characters.",
        )
        note_3b = AtomicNote(
            title=NoteTitle("Abc"),
            note_type=NoteType.ENTITY,
            definition="Valid definition containing over twenty characters.",
        )
        assert use_case._are_duplicates(note_3a, note_3b) is False

    def test_merge_notes_preserves_merged_direct_relations(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        canonical = AtomicNote(
            title=NoteTitle("Alpha Note"),
            note_type=NoteType.CONCEPT,
            definition="Definition Alpha containing over twenty characters.",
            direct_relations=(NoteTitle("Rel1"),),
        )
        redundant = AtomicNote(
            title=NoteTitle("Beta Note"),
            note_type=NoteType.CONCEPT,
            definition="Definition Beta containing over twenty characters.",
            direct_relations=(NoteTitle("Rel2"),),
        )
        merged = use_case._merge_notes(canonical, redundant)
        assert len(merged.direct_relations) == 2
        assert {r.value for r in merged.direct_relations} == {"Rel1", "Rel2"}

    def test_execute_definition_length_election_threshold(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        base_def = "x" * 100
        # Exactly +50 length difference: note_b does NOT overtake note_a
        def_plus50 = "y" * 150
        note_a = AtomicNote(
            title=NoteTitle("Candidate Alpha"),
            note_type=NoteType.CONCEPT,
            definition=base_def,
            aliases=("shared_alias",),
        )
        note_b = AtomicNote(
            title=NoteTitle("Candidate Beta"),
            note_type=NoteType.CONCEPT,
            definition=def_plus50,
            aliases=("shared_alias",),
        )
        mock_vault.save_atomic_note(note_a)
        mock_vault.save_atomic_note(note_b)
        mock_vault.update_index_entry(note_a)
        mock_vault.update_index_entry(note_b)

        report = use_case.execute()
        assert report.duplicates_unified_count == 1
        assert report.clusters[0].canonical_title == NoteTitle("Candidate Alpha")

        # Now test exactly +51: note_d DOES overtake note_c
        mock_vault_2 = InMemoryVaultAdapter()
        use_case_2 = UnifyDuplicateNotesUseCase(vault_port=mock_vault_2)
        def_plus51 = "z" * 151
        note_c = AtomicNote(
            title=NoteTitle("Candidate Gamma"),
            note_type=NoteType.CONCEPT,
            definition=base_def,
            aliases=("shared_alias_2",),
        )
        note_d = AtomicNote(
            title=NoteTitle("Candidate Delta"),
            note_type=NoteType.CONCEPT,
            definition=def_plus51,
            aliases=("shared_alias_2",),
        )
        mock_vault_2.save_atomic_note(note_c)
        mock_vault_2.save_atomic_note(note_d)
        mock_vault_2.update_index_entry(note_c)
        mock_vault_2.update_index_entry(note_d)

        report_2 = use_case_2.execute()
        assert report_2.duplicates_unified_count == 1
        assert report_2.clusters[0].canonical_title == NoteTitle("Candidate Delta")

    def test_execute_multi_note_cluster_and_additive_link_rewrites(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # Cluster of 3 duplicate notes: Prime, Alt1, Alt2
        note_prime = AtomicNote(
            title=NoteTitle("Prime Entity"),
            note_type=NoteType.ENTITY,
            definition="Primary definition of entity.",
            aliases=("shared_sym",),
        )
        note_alt1 = AtomicNote(
            title=NoteTitle("Alt1 Entity"),
            note_type=NoteType.ENTITY,
            definition="Alternative 1 definition.",
            aliases=("shared_sym",),
        )
        note_alt2 = AtomicNote(
            title=NoteTitle("Alt2 Entity"),
            note_type=NoteType.ENTITY,
            definition="Alternative 2 definition.",
            aliases=("shared_sym",),
        )
        # Referencing notes that will get rewritten
        ref1 = AtomicNote(
            title=NoteTitle("Reference One"),
            note_type=NoteType.CONCEPT,
            definition="Refers to [[Alt1 Entity]] and [[Alt1 Entity]].",
        )
        ref2 = AtomicNote(
            title=NoteTitle("Reference Two"),
            note_type=NoteType.CONCEPT,
            definition="Refers to [[Alt2 Entity]].",
        )
        mock_vault.save_atomic_note(note_prime)
        mock_vault.save_atomic_note(note_alt1)
        mock_vault.save_atomic_note(note_alt2)
        mock_vault.save_atomic_note(ref1)
        mock_vault.save_atomic_note(ref2)
        mock_vault.update_index_entry(note_prime)
        mock_vault.update_index_entry(note_alt1)
        mock_vault.update_index_entry(note_alt2)
        mock_vault.update_index_entry(ref1)
        mock_vault.update_index_entry(ref2)

        report = use_case.execute()
        assert report.duplicates_unified_count == 1
        assert report.total_links_rewritten == 2
        cluster = report.clusters[0]
        assert cluster.canonical_title == NoteTitle("Prime Entity")
        assert set(cluster.merged_titles) == {NoteTitle("Alt1 Entity"), NoteTitle("Alt2 Entity")}
        assert cluster.links_rewritten_count == 2
        assert isinstance(cluster, DuplicateCluster)

    def test_execute_interleaved_clusters_exercises_already_merged_tracking(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # Note1 and Note3 form Cluster Alpha (Note3 has longer definition +51, so Note3 overtakes Note1)
        # Note2 and Note4 form Cluster Beta
        # Interleaved in vault: [Note1, Note2, Note3, Note4]
        note1 = AtomicNote(
            title=NoteTitle("Entity 1A"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for first entity.",
            aliases=("alias_alpha",),
        )
        note2 = AtomicNote(
            title=NoteTitle("Entity 2A"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for second entity.",
            aliases=("alias_beta",),
        )
        note3 = AtomicNote(
            title=NoteTitle("Entity 1B"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for first entity." + (" extended analysis." * 10),
            aliases=("alias_alpha",),
        )
        note4 = AtomicNote(
            title=NoteTitle("Entity 2B"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for second entity.",
            aliases=("alias_beta",),
        )
        mock_vault.save_atomic_note(note1)
        mock_vault.save_atomic_note(note2)
        mock_vault.save_atomic_note(note3)
        mock_vault.save_atomic_note(note4)
        mock_vault.update_index_entry(note1)
        mock_vault.update_index_entry(note2)
        mock_vault.update_index_entry(note3)
        mock_vault.update_index_entry(note4)

        report = use_case.execute()
        assert report.duplicates_unified_count == 2
        cluster_alpha = next(
            c for c in report.clusters if c.canonical_title == NoteTitle("Entity 1B")
        )
        assert cluster_alpha.merged_titles == (NoteTitle("Entity 1A"),)
        cluster_beta = next(
            c for c in report.clusters if c.canonical_title == NoteTitle("Entity 2A")
        )
        assert cluster_beta.merged_titles == (NoteTitle("Entity 2B"),)

        # Confirm notes remaining in vault
        vault_titles = {n.title.value for n in mock_vault.get_all_atomic_notes()}
        assert vault_titles == {"Entity 1B", "Entity 2A"}

    def test_execute_sequential_clusters_kills_break_and_casing(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # Sequential clusters: [C1_A, C1_B, C2_A, C2_B]
        # At i=1, C1_B is visited; if 'break' instead of 'continue', C2 is never processed.
        c1_a = AtomicNote(
            title=NoteTitle("Group One Alpha"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for group one entity.",
            aliases=("alias_group_one",),
        )
        c1_b = AtomicNote(
            title=NoteTitle("Group One Beta"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for group one entity.",
            aliases=("alias_group_one",),
        )
        c2_a = AtomicNote(
            title=NoteTitle("Group Two Alpha"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for group two entity.",
            aliases=("alias_group_two",),
        )
        c2_b = AtomicNote(
            title=NoteTitle("Group Two Beta"),
            note_type=NoteType.ENTITY,
            definition="Short base definition for group two entity.",
            aliases=("alias_group_two",),
        )
        for note in (c1_a, c1_b, c2_a, c2_b):
            mock_vault.save_atomic_note(note)
            mock_vault.update_index_entry(note)

        report = use_case.execute()
        assert len(report.clusters) == 2
        assert report.duplicates_unified_count == 2
        vault_titles = {n.title.value for n in mock_vault.get_all_atomic_notes()}
        assert vault_titles == {"Group One Alpha", "Group Two Alpha"}

    def test_execute_canonical_overtake_tracking_kills_key_b_and_canonical_add_casing(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # [Alpha Note, Xray Note, Beta Note]
        # Alpha Note merges Beta Note, but Beta Note definition is >50 chars longer, so Beta becomes canonical.
        # Beta Note must be recorded in already_merged so that subsequent Xray Note does NOT match and delete it.
        alpha_note = AtomicNote(
            title=NoteTitle("Alpha Note"),
            note_type=NoteType.ENTITY,
            definition="Short base definition.",
            aliases=("shared_ab",),
        )
        xray_note = AtomicNote(
            title=NoteTitle("Xray Note"),
            note_type=NoteType.ENTITY,
            definition="Independent definition for xray entity.",
            aliases=("shared_xb",),
        )
        beta_note = AtomicNote(
            title=NoteTitle("Beta Note"),
            note_type=NoteType.ENTITY,
            definition="Short base definition." + (" Extra lengthy historical analysis." * 10),
            aliases=("shared_ab", "shared_xb"),
        )
        for note in (alpha_note, xray_note, beta_note):
            mock_vault.save_atomic_note(note)
            mock_vault.update_index_entry(note)

        report = use_case.execute()
        assert len(report.clusters) == 1
        assert report.clusters[0].canonical_title == NoteTitle("Beta Note")
        assert report.clusters[0].merged_titles == (NoteTitle("Alpha Note"),)
        vault_titles = {n.title.value for n in mock_vault.get_all_atomic_notes()}
        assert vault_titles == {"Beta Note", "Xray Note"}

    def test_execute_redundant_note_not_reprocessed_kills_key_a_casing(
        self, mock_vault: InMemoryVaultAdapter
    ) -> None:
        use_case = UnifyDuplicateNotesUseCase(vault_port=mock_vault)
        # [Note 1, Note 2, Note 3]
        # Note 1 ("Scipio Africanus") matches Note 2 ("Dom Publius") via alias.
        # Note 2 is merged into Note 1 and deleted from vault.
        # Note 2 matches Note 3 ("Publius") via honorific normalization ('Dom Publius' -> 'publius'),
        # but Note 1 ("Scipio Africanus") does NOT match Note 3.
        # When outer loop reaches index 1 (Note 2), key_a check must skip it;
        # otherwise Note 2 matches Note 3, resurrecting Note 2 in vault and creating a spurious cluster.
        note_1 = AtomicNote(
            title=NoteTitle("Scipio Africanus"),
            note_type=NoteType.ENTITY,
            definition="Prime general of the Roman Republic in Africa.",
            aliases=(),
        )
        note_2 = AtomicNote(
            title=NoteTitle("Dom Publius"),
            note_type=NoteType.ENTITY,
            definition="Honorific representation of Publius.",
            aliases=("scipio africanus",),
        )
        note_3 = AtomicNote(
            title=NoteTitle("Publius"),
            note_type=NoteType.ENTITY,
            definition="Common praenomen across patrician families.",
            aliases=(),
        )
        for note in (note_1, note_2, note_3):
            mock_vault.save_atomic_note(note)
            mock_vault.update_index_entry(note)

        report = use_case.execute()
        assert len(report.clusters) == 1
        assert report.clusters[0].canonical_title == NoteTitle("Scipio Africanus")
        assert report.clusters[0].merged_titles == (NoteTitle("Dom Publius"),)
        vault_titles = {n.title.value for n in mock_vault.get_all_atomic_notes()}
        assert vault_titles == {"Scipio Africanus", "Publius"}
        assert "Dom Publius" not in vault_titles


