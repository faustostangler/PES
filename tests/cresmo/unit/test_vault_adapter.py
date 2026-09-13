"""Unit tests for ObsidianVaultAdapter.

Tests atomic file persistence, YAML frontmatter formatting,
and index synchronization.
"""

from __future__ import annotations

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

    def test_save_and_get_enriched_compendium(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
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
        )

        adapter.save_enriched_compendium(compendium)
        retrieved = adapter.get_enriched_compendium(cid)

        assert retrieved is not None
        assert retrieved.content_id == cid
        assert retrieved.title.value == "Teoria das Elites"
        assert "circulação das elites" in retrieved.body
        assert "Dados históricos" in retrieved.complementary_info

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
