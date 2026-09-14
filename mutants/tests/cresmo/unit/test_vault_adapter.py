"""Unit tests for ObsidianVaultAdapter.

Tests atomic file persistence, YAML frontmatter formatting,
index synchronization, note deletion, subfolder routing,
and inbound WikiLink rewriting per SPEC-001 Section 4.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter


@pytest.fixture
def storage_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Fixture providing isolated temporary directories for vault, raw lake, and enriched compendiums."""
    vault_dir = tmp_path / "vault"
    raw_dir = tmp_path / "data" / "raw"
    enriched_dir = tmp_path / "data" / "enriched"
    vault_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    enriched_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir, raw_dir, enriched_dir


class TestObsidianVaultAdapter:
    """Hermetic unit tests for ObsidianVaultAdapter filesystem operations."""

    def test_save_and_get_raw_transcript(self, storage_paths: tuple[Path, Path, Path]) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        cid = ContentId("dQw4w9WgXcQ")
        raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Spoken speech transcript line 1.\nSpoken speech transcript line 2.",
        )

        adapter.save_raw_transcript(raw)
        retrieved = adapter.get_raw_transcript(cid)

        assert retrieved is not None
        assert retrieved.content_id == cid
        assert retrieved.channel_name == "Political Theory"
        assert "transcript line 1" in retrieved.body

    def test_get_raw_transcript_missing_returns_none(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        assert adapter.get_raw_transcript(ContentId("non_existent")) is None

    def test_save_and_get_enriched_compendium(self, storage_paths: tuple[Path, Path, Path]) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        cid = ContentId("dQw4w9WgXcQ")
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Political Theory",
            title=NoteTitle("Teoria das Elites"),
            body="A circulação das elites governa as dinâmicas institucionais.",
            complementary_info="Dados históricos e matrizes de poder.",
            pass_count=2,
            channel_id="UC_123",
            channel_category="politics",
            source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            video_date="20230517",
            video_description="Description text.",
        )

        adapter.save_enriched_compendium(compendium)
        retrieved = adapter.get_enriched_compendium(cid)

        assert retrieved is not None
        assert retrieved.content_id == cid
        assert retrieved.title.value == "Teoria das Elites"
        assert "circulação das elites" in retrieved.body
        assert "Dados históricos" in retrieved.complementary_info
        assert retrieved.channel_id == "UC_123"
        assert retrieved.channel_category == "politics"
        assert retrieved.video_date == "20230517"
        assert retrieved.video_description == "Description text."

    def test_get_enriched_compendium_missing_returns_none(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        assert adapter.get_enriched_compendium(ContentId("non_existent")) is None

    def test_save_and_get_atomic_note_with_index(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        title = NoteTitle("Vilfredo Pareto")
        note = AtomicNote(
            title=title,
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador da teoria da circulação das elites.",
            domain="Ciência Política",
            cluster="Elitismo Clássico",
            source="Teoria das Elites",
            aliases=("Pareto", "V. Pareto"),
            direct_relations=(NoteTitle("Gaetano Mosca"),),
            causal_matrix=CausalMatrix(
                cause="Heterogeneidade das faculdades humanas",
                effect="Formação contínua de minorias dirigentes",
                epistemic_attribution="Trattato di Sociologia Generale",
            ),
            cross_context=CrossContextRelations(
                precursors="Maquiavel",
                lateral_events="Positivismo sociológico",
                aftermath="Robert Michels",
            ),
        )

        adapter.save_atomic_note(note)
        adapter.update_index_entry(note)

        retrieved = adapter.get_atomic_note_by_title(title)
        assert retrieved is not None
        assert retrieved.title.value == "Vilfredo Pareto"
        assert retrieved.note_type == NoteType.ENTITY
        assert retrieved.domain == "Ciência Política"
        assert "Pareto" in retrieved.aliases
        assert NoteTitle("Gaetano Mosca") in retrieved.direct_relations
        assert retrieved.causal_matrix is not None
        assert retrieved.causal_matrix.cause == "Heterogeneidade das faculdades humanas"
        assert retrieved.cross_context is not None
        assert retrieved.cross_context.precursors == "Maquiavel"

        all_notes = adapter.get_all_atomic_notes()
        assert len(all_notes) == 1
        assert all_notes[0].title.value == "Vilfredo Pareto"

    def test_get_note_subfolder_routing(self) -> None:
        assert ObsidianVaultAdapter._get_note_subfolder(NoteType.ENTITY) == "entities"
        assert ObsidianVaultAdapter._get_note_subfolder(NoteType.PROCESS) == "processes"
        assert ObsidianVaultAdapter._get_note_subfolder(NoteType.CONCEPT) == "concepts"
        assert ObsidianVaultAdapter._get_note_subfolder(NoteType.EVENT) == "events"

    def test_delete_atomic_note_removes_file_and_cleans_index(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador da circulação das elites.",
            aliases=("Pareto",),
        )

        adapter.save_atomic_note(note)
        adapter.update_index_entry(note)

        # Confirm note exists before deletion
        assert adapter.get_atomic_note_by_title(note.title) is not None
        index_data = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert "vilfredo pareto" in index_data
        assert "pareto" in index_data

        # Delete atomic note
        adapter.delete_atomic_note(note)

        # File and index entries must be gone
        assert adapter.get_atomic_note_by_title(note.title) is None
        updated_index = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert "vilfredo pareto" not in updated_index
        assert "pareto" not in updated_index

    def test_remove_index_entry_handles_missing_and_corrupted_file(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        # Non-existent index path must return cleanly
        adapter.remove_index_entry("some_key")

        # Corrupted index JSON must return cleanly without crashing
        adapter.index_path.write_text("{corrupt_json: true", encoding="utf-8")
        adapter.remove_index_entry("some_key")

    def test_update_index_entry_handles_corrupt_index_gracefully(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        adapter.index_path.write_text("{corrupt_json: true", encoding="utf-8")

        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano formulador da circulação das elites.",
        )
        adapter.update_index_entry(note)

        # Index should be recovered and populated
        index_data = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert "vilfredo pareto" in index_data

    def test_save_map_of_content(self, storage_paths: tuple[Path, Path, Path]) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        moc = MapOfContent(
            title=NoteTitle("MOC Teoria Politica"),
            theme="Ciência Política",
            overview="Panorama estruturado das linhagens teóricas de poder e governo.",
            associated_notes=(NoteTitle("Vilfredo Pareto"), NoteTitle("Gaetano Mosca")),
        )

        adapter.save_map_of_content(moc)
        moc_file = vault_dir / "MOCs" / "MOC Teoria Politica.md"
        assert moc_file.exists()
        content = moc_file.read_text(encoding="utf-8")
        assert "MOC Teoria Politica" in content
        assert "[[Vilfredo Pareto]]" in content
        assert "[[Gaetano Mosca]]" in content

    def test_get_all_atomic_notes_and_get_by_title_exclude_mocs(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            definition="Sociólogo italiano pioneiro da circulação de elites.",
        )
        moc = MapOfContent(
            title=NoteTitle("Vilfredo Pareto"),  # MOC with identical title
            theme="Ciência Política",
            overview="MOC overview.",
            associated_notes=(NoteTitle("Vilfredo Pareto"),),
        )

        adapter.save_atomic_note(note)
        adapter.save_map_of_content(moc)

        # get_atomic_note_by_title should return the atomic note, never the MOC
        retrieved = adapter.get_atomic_note_by_title(note.title)
        assert retrieved is not None
        assert retrieved.note_type == NoteType.ENTITY

        # get_all_atomic_notes should return only atomic notes
        all_notes = adapter.get_all_atomic_notes()
        assert len(all_notes) == 1
        assert all_notes[0].note_type == NoteType.ENTITY

    def test_rewrite_wiki_links_rewrites_inbound_references(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        sub_dir = vault_dir / "concepts"
        sub_dir.mkdir(parents=True, exist_ok=True)
        target_file = sub_dir / "sample_referencing_note.md"
        target_file.write_text(
            "Conceito associado a [[D. Afonso Henriques]] e também a [[d. afonso henriques|Primeiro Rei de Portugal]].\n",
            encoding="utf-8",
        )

        other_file = sub_dir / "unrelated_note.md"
        other_file.write_text("Unrelated content [[Outro Conceito]].\n", encoding="utf-8")

        count = adapter.rewrite_wiki_links(
            old_title=NoteTitle("D. Afonso Henriques"),
            new_title=NoteTitle("Dom Afonso Henriques"),
        )

        assert count == 1
        updated_content = target_file.read_text(encoding="utf-8")
        assert "[[Dom Afonso Henriques]]" in updated_content
        assert "[[Dom Afonso Henriques|Primeiro Rei de Portugal]]" in updated_content

        unrelated_content = other_file.read_text(encoding="utf-8")
        assert "[[Outro Conceito]]" in unrelated_content

    def test_rewrite_wiki_links_identical_titles_returns_zero(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        count = adapter.rewrite_wiki_links(
            old_title=NoteTitle("Same Title"),
            new_title=NoteTitle("same title"),
        )
        assert count == 0
