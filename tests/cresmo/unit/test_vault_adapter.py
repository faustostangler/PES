"""Unit tests for ObsidianVaultAdapter.

Tests atomic file persistence, YAML frontmatter formatting,
index synchronization, note deletion, subfolder routing,
and inbound WikiLink rewriting per SPEC-001 Section 4.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import (
    CausalMatrix,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    CrossContextRelations,
    MediaProvenance,
    NoteTitle,
    NoteType,
    RawIndexEntry,
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
        raw = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Spoken speech transcript line 1.\nSpoken speech transcript line 2.",
        )

        adapter.save_transcript(raw)
        retrieved = adapter.get_raw_transcript(cid)

        assert retrieved is not None
        assert retrieved.content.id == cid
        assert retrieved.channel.name == "Political Theory"
        assert "transcript line 1" in retrieved.content.body
        # ADR-038 parity assertions
        assert retrieved.channel.name == "Political Theory"
        assert retrieved.content.id == cid

    def test_custom_injected_mocs_dir_and_index_path(
        self, storage_paths: tuple[Path, Path, Path], tmp_path: Path
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        custom_mocs = tmp_path / "custom_mocs"
        custom_index = tmp_path / "custom_catalog.json"

        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
            mocs_dir=custom_mocs,
            index_path=custom_index,
        )

        assert adapter.mocs_dir == custom_mocs.resolve()
        assert adapter.index_path == custom_index.resolve()

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
            channel_name=ChannelName("Political Theory"),
            title=NoteTitle("Teoria das Elites"),
            body="A circulação das elites governa as dinâmicas institucionais.",
            complementary_info="Dados históricos e matrizes de poder.",
            pass_count=2,
            channel_id=ChannelId("UC_123"),
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
        assert retrieved.channel_id == ChannelId("UC_123")
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
            content_tags=("sociologia", "política"),
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
        assert retrieved.cluster == "Elitismo Clássico"
        assert retrieved.source == "Teoria das Elites"
        assert retrieved.content_tags == ("sociologia", "política")
        assert "Pareto" in retrieved.aliases
        assert NoteTitle("Gaetano Mosca") in retrieved.direct_relations
        assert retrieved.causal_matrix is not None
        assert retrieved.causal_matrix.cause == "Heterogeneidade das faculdades humanas"
        assert retrieved.causal_matrix.effect == "Formação contínua de minorias dirigentes"
        assert retrieved.causal_matrix.epistemic_attribution == "Trattato di Sociologia Generale"
        assert retrieved.cross_context is not None
        assert retrieved.cross_context.precursors == "Maquiavel"
        assert retrieved.cross_context.lateral_events == "Positivismo sociológico"
        assert retrieved.cross_context.aftermath == "Robert Michels"

        # Check raw saved markdown file content & format
        saved_file = vault_dir / "entities" / "Vilfredo Pareto.md"
        assert saved_file.exists()
        raw_text = saved_file.read_text(encoding="utf-8")
        assert "title: Vilfredo Pareto\n" in raw_text
        assert "cluster: Elitismo Clássico\n" in raw_text
        # Verify sort_keys=False preserves insertion order (title before aliases)
        assert raw_text.index("title:") < raw_text.index("aliases:")
        assert "source: Teoria das Elites\n" in raw_text
        assert "política" in raw_text
        # Verify sort_keys=False preserves logical frontmatter order
        assert raw_text.index("title:") < raw_text.index("domain:") < raw_text.index("tags:")
        # Verify section spacing and headers
        assert "\n\n# [[Vilfredo Pareto]]\n\n## Definição & Análise Contextual\n" in raw_text
        assert "\n## Conexões & Relações Diretas\n- [[Gaetano Mosca]]\n\n" in raw_text
        assert "\n- Atribuição Epistêmica: Trattato di Sociologia Generale\n\n" in raw_text
        assert "\n- Eventos Laterais: Positivismo sociológico\n" in raw_text
        assert "\n- Desdobramentos: Robert Michels\n" in raw_text
        assert "XXXX" not in raw_text

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

        # Create MOC with same title: must NOT be deleted by delete_atomic_note
        moc_file = vault_dir / "MOCs" / "Vilfredo Pareto.md"
        moc_file.parent.mkdir(parents=True, exist_ok=True)
        moc_file.write_text("Preserved MOC content", encoding="utf-8")

        # Confirm note exists before deletion
        assert adapter.get_atomic_note_by_title(note.title) is not None
        index_data = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert "vilfredo pareto" in index_data
        assert "pareto" in index_data

        # Delete atomic note with spy on Path.unlink to verify missing_ok=True
        orig_unlink = Path.unlink
        unlinked_calls: list[dict[str, Any]] = []

        def spy_unlink(self_path: Path, *args: Any, **kwargs: Any) -> None:
            unlinked_calls.append(kwargs)
            orig_unlink(self_path, *args, **kwargs)

        with patch.object(Path, "unlink", spy_unlink):
            adapter.delete_atomic_note(note)

        assert any(call.get("missing_ok") is True for call in unlinked_calls)

        # File and index entries must be gone, but MOC preserved
        assert adapter.get_atomic_note_by_title(note.title) is None
        assert moc_file.is_file()
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
        assert moc_file.is_file()
        content = moc_file.read_text(encoding="utf-8")
        expected_exact = (
            "---\n"
            "title: MOC Teoria Politica\n"
            "type: moc\n"
            "theme: Ciência Política\n"
            "---\n\n"
            "# [[MOC Teoria Politica]]\n\n"
            "Panorama estruturado das linhagens teóricas de poder e governo.\n\n"
            "## Notas Associadas\n"
            "- [[Vilfredo Pareto]]\n"
            "- [[Gaetano Mosca]]\n"
        )
        assert content == expected_exact
        assert "\\u" not in content

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
        # File 1 has a single link (tests count > 0 vs count > 1)
        target_file_1 = sub_dir / "sample_referencing_note_1.md"
        target_file_1.write_text(
            "Conceito associado a [[D. Afonso Henriques]].\n",
            encoding="utf-8",
        )
        # File 2 has an aliased link (tests pipe group and multiple file counter)
        target_file_2 = sub_dir / "sample_referencing_note_2.md"
        target_file_2.write_text(
            "Conceito associado a [[d. afonso henriques|Primeiro Rei de Portugal]].\n",
            encoding="utf-8",
        )

        other_file = sub_dir / "unrelated_note.md"
        other_file.write_text("Unrelated content [[Outro Conceito]].\n", encoding="utf-8")

        count = adapter.rewrite_wiki_links(
            old_title=NoteTitle("D. Afonso Henriques"),
            new_title=NoteTitle("Dom Afonso Henriques"),
        )

        assert count == 2
        updated_content_1 = target_file_1.read_text(encoding="utf-8")
        assert "[[Dom Afonso Henriques]]" in updated_content_1

        updated_content_2 = target_file_2.read_text(encoding="utf-8")
        assert "[[Dom Afonso Henriques|Primeiro Rei de Portugal]]" in updated_content_2

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

        sub_dir = vault_dir / "concepts"
        sub_dir.mkdir(parents=True, exist_ok=True)
        target_file = sub_dir / "note_with_same_title.md"
        target_file.write_text("Content linking to [[Same Title]].\n", encoding="utf-8")

        count = adapter.rewrite_wiki_links(
            old_title=NoteTitle("Same Title"),
            new_title=NoteTitle("same title"),
        )
        assert count == 0
        # Content must NOT be rewritten when titles are case-insensitively identical
        assert "[[Same Title]]" in target_file.read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("raw_name", "expected"),
        [
            ("Normal Title", "Normal Title"),
            ("Title/With/Slashes", "Title_With_Slashes"),
            ("Title\\With\\Backslashes", "Title_With_Backslashes"),
            ("Title:With:Colons", "Title_With_Colons"),
            ("Title*With*Asterisks", "Title_With_Asterisks"),
            ("Title?With?Questions", "Title_With_Questions"),
            ('Title"With"Quotes', "Title_With_Quotes"),
            ("Title<With>Brackets", "Title_With_Brackets"),
            ("Title|With|Pipes", "Title_With_Pipes"),
            ("Title%With%Percent", "Title_With_Percent"),
            ('  All \\/*?:"<>|% Chars  ', "All __________ Chars"),
        ],
    )
    def test_sanitize_filename_exhaustive(self, raw_name: str, expected: str) -> None:
        from cresmo.infrastructure.adapters.obsidian_vault_adapter import sanitize_filename

        assert sanitize_filename(raw_name) == expected

    def test_get_raw_transcript_no_frontmatter_fallback(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        raw_file = raw_dir / "ChannelFolder" / "no_fm_1234.md"
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_text(
            "Plain markdown body with no yaml frontmatter at all.", encoding="utf-8"
        )

        transcript = adapter.get_raw_transcript(ContentId("no_fm_1234"))
        assert transcript is not None
        assert transcript.content.id == ContentId("no_fm_1234")
        assert transcript.channel.name == "ChannelFolder"
        assert transcript.provenance.url == f"file://{raw_file.resolve()}"
        assert transcript.provenance.description == ""
        assert transcript.content.title == "no_fm_1234"
        assert transcript.content.body == "Plain markdown body with no yaml frontmatter at all."

    def test_get_raw_transcript_invalid_date_handled_gracefully(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        raw_file = raw_dir / "ChannelFolder" / "bad_date12.md"
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_text(
            "---\nvideo_title: 'Bad Date'\nupload_date: '99999999'\n---\nBody with bad date",
            encoding="utf-8",
        )

        transcript = adapter.get_raw_transcript(ContentId("bad_date12"))
        assert transcript is not None
        assert transcript.provenance.publication_date is None

    def test_get_enriched_compendium_no_frontmatter_returns_none(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        file_path = enriched_dir / "comp123456.md"
        file_path.write_text("No frontmatter header in compendium.", encoding="utf-8")

        assert adapter.get_enriched_compendium(ContentId("comp123456")) is None

    def test_get_atomic_note_os_error_or_missing_frontmatter(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        concepts_dir = vault_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        corrupted = concepts_dir / "Corrupted Note.md"
        corrupted.write_text("No frontmatter here.", encoding="utf-8")

        assert adapter.get_atomic_note_by_title(NoteTitle("Corrupted Note")) is None

        with patch("pathlib.Path.read_text", side_effect=OSError("Permission denied")):
            assert adapter.get_atomic_note_by_title(NoteTitle("Corrupted Note")) is None

    def test_get_atomic_note_invalid_type_and_short_definition_fallbacks(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        concepts_dir = vault_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        note_file = concepts_dir / "Fallback Note.md"
        note_file.write_text(
            "---\ntitle: 'Fallback Note'\ntype: 'invalid_unrecognized_type'\n---\nShort",
            encoding="utf-8",
        )

        note = adapter.get_atomic_note_by_title(NoteTitle("Fallback Note"))
        assert note is not None
        assert note.note_type == NoteType.CONCEPT
        assert "Definição contextual de Fallback Note" in note.definition

    def test_rewrite_wiki_links_ignores_unreadable_files(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        concepts_dir = vault_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        bad_file = concepts_dir / "Bad_Note.md"
        bad_file.write_text("Reference to [[Old Title]].", encoding="utf-8")
        good_file = concepts_dir / "Good_Note.md"
        good_file.write_text("Reference to [[Old Title]].", encoding="utf-8")

        orig_read = Path.read_text

        def selective_read(self_path: Path, *args: Any, **kwargs: Any) -> str:
            if self_path == bad_file:
                raise OSError("Disk read error")
            return orig_read(self_path, *args, **kwargs)

        with patch.object(Path, "read_text", selective_read):
            count = adapter.rewrite_wiki_links(NoteTitle("Old Title"), NoteTitle("New Title"))
            assert count == 1
        assert "[[New Title]]" in good_file.read_text(encoding="utf-8")

    def test_master_document_persistence_and_clearing(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        master_dir = vault_dir.parent / "master"
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
            master_dir=master_dir,
        )

        # 1. Enriched files discovery
        ch_dir = enriched_dir / "Fabio Akita"
        ch_dir.mkdir(parents=True, exist_ok=True)
        f1 = ch_dir / "vid1.md"
        f2 = ch_dir / "vid2.md"
        f1.write_text("file 1", encoding="utf-8")
        f2.write_text("file 2", encoding="utf-8")

        files = adapter.get_enriched_files_for_channel(ChannelName("Fabio Akita"))
        assert len(files) == 2
        assert f1 in files and f2 in files

        # 2. Save master document sequentially twice (tests exist_ok=True on cat_dir.mkdir)
        out_path_1 = adapter.save_master_document(
            channel_name=ChannelName("Fabio Akita"),
            channel_category="tech_ai",
            part_number=1,
            content="Aggregated master content part 1",
        )
        out_path_2 = adapter.save_master_document(
            channel_name=ChannelName("Fabio Akita"),
            channel_category="tech_ai",
            part_number=2,
            content="Aggregated master content part 2",
        )
        assert out_path_1.exists()
        assert out_path_1.name == "Fabio_Akita_001.md"
        assert out_path_1.parent.name == "tech_ai"
        assert out_path_1.read_text(encoding="utf-8") == "Aggregated master content part 1"

        assert out_path_2.exists()
        assert out_path_2.name == "Fabio_Akita_002.md"
        assert out_path_2.read_text(encoding="utf-8") == "Aggregated master content part 2"

        # 3. Clear master documents with spy on Path.unlink to verify missing_ok=True
        orig_unlink = Path.unlink
        unlinked_calls: list[dict[str, Any]] = []

        def spy_unlink(self_path: Path, *args: Any, **kwargs: Any) -> None:
            unlinked_calls.append(kwargs)
            orig_unlink(self_path, *args, **kwargs)

        with patch.object(Path, "unlink", spy_unlink):
            adapter.clear_master_documents_for_channel(
                channel_name=ChannelName("Fabio Akita"),
                channel_category="tech_ai",
            )
        assert not out_path_1.exists()
        assert not out_path_2.exists()
        assert any(call.get("missing_ok") is True for call in unlinked_calls)

        # 4. Clear master documents when directory is a file (guarded glob to test exists/is_dir logic)
        non_dir_cat = master_dir / "file_category"
        non_dir_cat.touch()

        def guarded_cat_glob(self_path: Path, pattern: str) -> Any:
            if self_path == non_dir_cat:
                raise AssertionError("glob called on non-directory cat_dir")
            return []

        with patch.object(Path, "glob", guarded_cat_glob):
            adapter.clear_master_documents_for_channel(
                channel_name=ChannelName("Fabio Akita"),
                channel_category="file_category",
            )

    def test_raw_index_channel_and_brain_csv_persistence(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        entry1 = RawIndexEntry(
            video_id=ContentId("vid11111111"),
            url="https://youtube.com/watch?v=vid11111111",
            title="Video Um",
            channel_name=ChannelName("Canal Teste"),
            key_concept="Conceito Um",
            synthesis="Síntese paratática do primeiro vídeo.",
            channel_category="history",
        )
        entry2 = RawIndexEntry(
            video_id=ContentId("vid22222222"),
            url="https://youtube.com/watch?v=vid22222222",
            title="Video Dois",
            channel_name=ChannelName("Canal Teste"),
            key_concept="Conceito Dois",
            synthesis="Síntese paratática do segundo vídeo.",
            channel_category="history",
        )

        # 1. Initial indexed check
        assert adapter.get_indexed_video_ids_for_channel(ChannelName("Canal Teste")) == set()

        # 2. Append entry 1
        adapter.append_channel_index_entry(ChannelName("Canal Teste"), entry1)
        adapter.append_brain_csv_entry(entry1)

        indexed = adapter.get_indexed_video_ids_for_channel(ChannelName("Canal Teste"))
        assert indexed == {"vid11111111"}

        # Check channel index file content
        canal_path = adapter.get_channel_index_path(ChannelName("Canal Teste"))
        assert canal_path.exists()
        assert canal_path.name == "_index_Canal Teste.md"
        md_text = canal_path.read_text(encoding="utf-8")
        assert "# Canal: Canal Teste" in md_text
        assert "vid11111111" in md_text
        assert "Conceito Um" in md_text

        # 3. Append entry 2
        adapter.append_channel_index_entry(ChannelName("Canal Teste"), entry2)
        adapter.append_brain_csv_entry(entry2)

        indexed = adapter.get_indexed_video_ids_for_channel(ChannelName("Canal Teste"))
        assert indexed == {"vid11111111", "vid22222222"}
        assert all(isinstance(x, ContentId) for x in indexed)

        # 4. Check brain.csv content
        csv_path = raw_dir.parent / "brain.csv"
        assert csv_path.exists()
        csv_text = csv_path.read_text(encoding="utf-8")
        assert '"channel_category";"channel_name";"filename";"key_concept";"synthesis"' in csv_text
        assert (
            '"history";"Canal Teste";"vid11111111.md";"Conceito Um";"Síntese paratática do primeiro vídeo."'
            in csv_text
        )
        assert (
            '"history";"Canal Teste";"vid22222222.md";"Conceito Dois";"Síntese paratática do segundo vídeo."'
            in csv_text
        )

    def test_default_and_custom_paths_initialization(
        self, storage_paths: tuple[Path, Path, Path], tmp_path: Path
    ) -> None:
        """Verify default directory resolution and custom data_dir/master_dir resolution."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        custom_data = tmp_path / "custom_data"
        custom_master = tmp_path / "custom_master"

        # Defaults when data_dir, master_dir, index_path, mocs_dir are None
        adapter_default = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        assert adapter_default.data_dir == raw_dir.parent.resolve()
        assert adapter_default.master_dir == (adapter_default.data_dir / "master").resolve()
        assert adapter_default.master_dir.name == "master"
        assert adapter_default.mocs_dir == (vault_dir / "MOCs").resolve()
        assert adapter_default.mocs_dir.name == "MOCs"
        assert adapter_default.index_path == (vault_dir / "_index.json").resolve()
        assert adapter_default.index_path.name == "_index.json"

        # Custom data_dir and master_dir
        adapter_custom = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
            data_dir=custom_data,
            master_dir=custom_master,
        )
        assert adapter_custom.data_dir == custom_data.resolve()
        assert adapter_custom.master_dir == custom_master.resolve()

    def test_atomic_write_delegation(
        self, storage_paths: tuple[Path, Path, Path], tmp_path: Path
    ) -> None:
        """Verify _atomic_write helper method writes expected text content."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        target = tmp_path / "sub" / "atomic_test.txt"
        adapter._atomic_write(target, "atomic write test content")
        assert target.is_file()
        assert target.read_text(encoding="utf-8") == "atomic write test content"

    def test_get_note_path_and_parse_file_delegation(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify _get_note_path and _parse_atomic_note_file handler delegations."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        note = AtomicNote(
            title=NoteTitle("Direct Path Test"),
            note_type=NoteType.CONCEPT,
            definition="Definition text with at least 20 chars for domain validation.",
        )
        note_path = adapter._get_note_path(note)
        assert note_path == vault_dir / "concepts" / "Direct Path Test.md"

        # Save and verify _parse_atomic_note_file delegation
        adapter.save_atomic_note(note)
        parsed = adapter._parse_atomic_note_file(note_path)
        assert parsed is not None
        assert parsed.title == note.title
        assert parsed.definition == note.definition

    def test_remove_index_entry_delegation(self, storage_paths: tuple[Path, Path, Path]) -> None:
        """Verify remove_index_entry handler delegation removes targeted index entry."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        note = AtomicNote(
            title=NoteTitle("Index Remove Test"),
            note_type=NoteType.CONCEPT,
            definition="Definition text with at least 20 chars for domain validation.",
        )
        adapter.update_index_entry(note)
        key = "index remove test"
        raw_index = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert key in raw_index

        adapter.remove_index_entry(key)
        raw_index_after = json.loads(adapter.index_path.read_text(encoding="utf-8"))
        assert key not in raw_index_after

    def test_parse_atomic_note_file_edge_cases(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify boundary definition length, self-relation exclusion, and section parsing fallbacks."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        # 1. Definition length exactly 20 chars: must be preserved, not replaced by fallback
        exact_20_chars = "12345678901234567890"
        note_file = vault_dir / "concepts" / "Exact Def Note.md"
        note_file.parent.mkdir(parents=True, exist_ok=True)
        content_exact = f"""---
title: Exact Def Note
type: concept
---

# [[Exact Def Note]]

## Definição & Análise Contextual
{exact_20_chars}
"""
        note_file.write_text(content_exact, encoding="utf-8")
        parsed_exact = adapter._parse_atomic_note_file(note_file)
        assert parsed_exact is not None
        assert parsed_exact.definition == exact_20_chars

        # 2. Self-relation filtering with case variations & valid external relation
        self_rel_file = vault_dir / "concepts" / "Self Loop Note.md"
        content_self_rel = """---
type: concept
---

# [[Self Loop Note]]

## Definição & Análise Contextual
Definição conceitual com mais de vinte caracteres para passar na validação.

## Conexões & Relações Diretas
- [[Self Loop Note]]
- [[self loop note]]
- [[SELF LOOP NOTE]]
- [[External Concept]]
"""
        self_rel_file.write_text(content_self_rel, encoding="utf-8")
        parsed_self_rel = adapter._parse_atomic_note_file(self_rel_file)
        assert parsed_self_rel is not None
        # Inherits title from file_path.stem when missing in frontmatter
        assert parsed_self_rel.title.value == "Self Loop Note"
        # Self-relations filtered out, external concept kept
        assert parsed_self_rel.direct_relations == (NoteTitle("External Concept"),)

        # 3. Partial causal matrix and cross-context defaults
        partial_file = vault_dir / "concepts" / "Partial Sections Note.md"
        content_partial = """---
title: Partial Sections Note
type: 12345
---

# [[Partial Sections Note]]

## Definição & Análise Contextual
Definição conceitual com mais de vinte caracteres para passar na validação.

## Matriz Causal
- Causa: Condição Geradora Primária
- Efeito: Efeito Estrutural Resultante

## Redes de Conexão (Cross-Context)
- Precursores: Precursores Históricos Relevantes
"""
        partial_file.write_text(content_partial, encoding="utf-8")
        parsed_partial = adapter._parse_atomic_note_file(partial_file)
        assert parsed_partial is not None
        # Non-string type falls back to CONCEPT
        assert parsed_partial.note_type == NoteType.CONCEPT
        assert parsed_partial.causal_matrix is not None
        assert parsed_partial.causal_matrix.cause == "Condição Geradora Primária"
        assert parsed_partial.causal_matrix.effect == "Efeito Estrutural Resultante"
        assert parsed_partial.causal_matrix.epistemic_attribution == ""
        assert parsed_partial.cross_context is not None
        assert parsed_partial.cross_context.precursors == "Precursores Históricos Relevantes"
        assert parsed_partial.cross_context.lateral_events == ""
        assert parsed_partial.cross_context.aftermath == ""

    def test_remove_index_entry_indentation_and_unicode(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify _index.json formatting preserves 2-space indentation and unescaped unicode after removal."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )
        note1 = AtomicNote(
            title=NoteTitle("Conceito de Ação"),
            note_type=NoteType.CONCEPT,
            definition="Definição teórica com caracteres unicode acentuados para teste.",
        )
        note2 = AtomicNote(
            title=NoteTitle("Conceito de Padrão"),
            note_type=NoteType.CONCEPT,
            definition="Outra definição teórica com caracteres unicode acentuados.",
        )
        adapter.update_index_entry(note1)
        adapter.update_index_entry(note2)

        raw_index_text = adapter.index_path.read_text(encoding="utf-8")
        assert "Conceito de Ação" in raw_index_text
        assert "Conceito de Padrão" in raw_index_text
        assert '\n  "conceito de ação": {' in raw_index_text

        # Remove one entry; the other must remain with exact indent=2 and unescaped unicode
        adapter.remove_index_entry("conceito de padrão")
        raw_after = adapter.index_path.read_text(encoding="utf-8")
        assert "conceito de padrão" not in raw_after
        assert "Conceito de Ação" in raw_after
        assert "\\u" not in raw_after
        assert '\n  "conceito de ação": {' in raw_after
        assert not '\n   "conceito de ação": {' in raw_after
        assert not '\n    "conceito de ação": {' in raw_after

    def test_update_index_entry_payload_and_alias_mapping_exhaustive(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify update_index_entry payload integrity, aliases, path, and json formatting."""
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
            domain="Sociologia das Elites",
            cluster="Teoria Sociológica",
            aliases=("Pareto", "V. Pareto"),
        )
        adapter.update_index_entry(note)

        raw_text = adapter.index_path.read_text(encoding="utf-8")
        # Ensure indent=2 formatting
        assert '\n  "vilfredo pareto": {' in raw_text
        assert not '\n   "vilfredo pareto": {' in raw_text
        assert not '\n    "vilfredo pareto": {' in raw_text
        # Ensure ensure_ascii=False formatting (unicode characters not escaped)
        assert "Sociologia das Elites" in raw_text
        assert "\\u" not in raw_text

        index = json.loads(raw_text)
        expected_path = "entities/Vilfredo Pareto.md"
        expected_payload = {
            "title": "Vilfredo Pareto",
            "type": "entity",
            "domain": "Sociologia das Elites",
            "cluster": "Teoria Sociológica",
            "aliases": ["Pareto", "V. Pareto"],
            "path": expected_path,
        }

        # Validate exact keys and values in primary title
        primary_entry = index.get("vilfredo pareto")
        assert primary_entry is not None
        assert set(primary_entry.keys()) == {"title", "type", "domain", "cluster", "aliases", "path"}
        assert primary_entry["title"] == "Vilfredo Pareto"
        assert primary_entry["type"] == "entity"
        assert primary_entry["domain"] == "Sociologia das Elites"
        assert primary_entry["cluster"] == "Teoria Sociológica"
        assert primary_entry["aliases"] == ["Pareto", "V. Pareto"]
        assert primary_entry["path"] == expected_path

        # Validate alias mappings pointing to exact entry_payload (not None)
        assert index.get("pareto") == expected_payload
        assert index.get("v. pareto") == expected_payload
        assert index.get("pareto") is not None
        assert index.get("v. pareto") is not None

    def test_parse_atomic_note_file_metadata_and_section_fallbacks_exhaustive(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify parse_atomic_note_file handles absent metadata, title priority, and section defaults."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir,
            raw_dir=raw_dir,
            enriched_dir=enriched_dir,
        )

        # 1. Frontmatter with explicit title distinct from filename stem
        note_file_1 = vault_dir / "concepts" / "FilenameStem.md"
        note_file_1.parent.mkdir(parents=True, exist_ok=True)
        content_1 = """---
title: Explicit Note Title
type: concept
---

# [[Explicit Note Title]]

## Definição & Análise Contextual
Definição conceitual com mais de vinte caracteres para passar na validação.
"""
        note_file_1.write_text(content_1, encoding="utf-8")
        parsed_1 = adapter._parse_atomic_note_file(note_file_1)
        assert parsed_1 is not None
        # Explicit title in frontmatter must override filename stem
        assert parsed_1.title.value == "Explicit Note Title"
        assert parsed_1.title.value != "FilenameStem"
        # Missing domain, cluster, source, aliases, tags must default to empty strings/tuples
        assert parsed_1.domain == ""
        assert len(parsed_1.domain) == 0
        assert parsed_1.cluster == ""
        assert len(parsed_1.cluster) == 0
        assert parsed_1.source == ""
        assert len(parsed_1.source) == 0
        assert parsed_1.aliases == ()
        assert parsed_1.content_tags == ()
        assert parsed_1.causal_matrix is None
        assert parsed_1.cross_context is None

        # 2. Causal matrix with only epistemic attribution (missing cause and effect)
        # And Cross-context with only aftermath (missing precursors and lateral events)
        note_file_2 = vault_dir / "concepts" / "PartialSections.md"
        content_2 = """---
title: Partial Sections
type: concept
domain: Economia
cluster: Mercados
source: Livro A
tags:
  - economia
  - mercados
aliases:
  - PS
---

# [[Partial Sections]]

## Definição & Análise Contextual
Definição conceitual com mais de vinte caracteres para passar na validação.

## Matriz Causal
- Atribuição Epistêmica: Escola Austríaca

## Redes de Conexão (Cross-Context)
- Desdobramentos: Regulação Governamental Aumentada
"""
        note_file_2.write_text(content_2, encoding="utf-8")
        parsed_2 = adapter._parse_atomic_note_file(note_file_2)
        assert parsed_2 is not None
        assert parsed_2.domain == "Economia"
        assert parsed_2.cluster == "Mercados"
        assert parsed_2.source == "Livro A"
        assert parsed_2.content_tags == ("economia", "mercados")
        assert parsed_2.aliases == ("PS",)

        assert parsed_2.causal_matrix is not None
        assert parsed_2.causal_matrix.cause == ""
        assert len(parsed_2.causal_matrix.cause) == 0
        assert parsed_2.causal_matrix.effect == ""
        assert len(parsed_2.causal_matrix.effect) == 0
        assert parsed_2.causal_matrix.epistemic_attribution == "Escola Austríaca"

        assert parsed_2.cross_context is not None
        assert parsed_2.cross_context.precursors == ""
        assert len(parsed_2.cross_context.precursors) == 0
        assert parsed_2.cross_context.lateral_events == ""
        assert len(parsed_2.cross_context.lateral_events) == 0
        assert parsed_2.cross_context.aftermath == "Regulação Governamental Aumentada"

        # 3. Causal matrix with cause and effect (missing epistemic attribution)
        # And Cross-context with precursors and lateral events (missing aftermath)
        note_file_3 = vault_dir / "concepts" / "PartialSectionsOpposite.md"
        content_3 = """---
title: Partial Sections Opposite
type: concept
---

# [[Partial Sections Opposite]]

## Definição & Análise Contextual
Definição conceitual com mais de vinte caracteres para passar na validação.

## Matriz Causal
- Causa: Expansão Monetária
- Efeito: Inflação de Preços

## Redes de Conexão (Cross-Context)
- Precursores: Queda das Taxas de Juros
- Eventos Laterais: Boom Imobiliário
"""
        note_file_3.write_text(content_3, encoding="utf-8")
        parsed_3 = adapter._parse_atomic_note_file(note_file_3)
        assert parsed_3 is not None
        assert parsed_3.causal_matrix is not None
        assert parsed_3.causal_matrix.cause == "Expansão Monetária"
        assert parsed_3.causal_matrix.effect == "Inflação de Preços"
        assert parsed_3.causal_matrix.epistemic_attribution == ""
        assert len(parsed_3.causal_matrix.epistemic_attribution) == 0

        assert parsed_3.cross_context is not None
        assert parsed_3.cross_context.precursors == "Queda das Taxas de Juros"
        assert parsed_3.cross_context.lateral_events == "Boom Imobiliário"
        assert parsed_3.cross_context.aftermath == ""
        assert len(parsed_3.cross_context.aftermath) == 0

    def test_save_and_get_raw_transcript_rich_metadata_and_escaping(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify save_transcript and get_raw_transcript preserve quotes, dates, ids, and multiline descriptions."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("vid_rich_123")
        channel = Channel(
            name='Canal "Socio-Político"',
            id=ChannelId("UC_abc_999"),
            category='Categoria "Alpha"',
        )
        provenance = MediaProvenance.create(
            url="https://youtube.com/watch?v=vid_rich_123",
            description="Linha descritiva 1\nLinha descritiva 2",
            publication_date=date(2023, 11, 25),
        )
        content = Content.create(
            id=cid,
            title='Título com "Aspas"',
            body="Transcrição de áudio completa.\nSegunda linha.",
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )

        adapter.save_transcript(transcript)

        # 1. Assert exact file location and formatted content on disk
        saved_file = raw_dir / "Canal _Socio-Político_" / "vid_rich_123.md"
        assert saved_file.is_file()
        raw_text = saved_file.read_text(encoding="utf-8")
        assert 'video_title: "Título com \\"Aspas\\""\n' in raw_text
        assert "video_id: vid_rich_123\n" in raw_text
        assert 'channel_name: "Canal \\"Socio-Político\\""\n' in raw_text
        assert "channel_id: UC_abc_999\n" in raw_text
        assert 'channel_category: "Categoria \\"Alpha\\""\n' in raw_text
        assert "url: https://youtube.com/watch?v=vid_rich_123\n" in raw_text
        assert "video_date: 20231125\n" in raw_text
        assert "video_description: |\n  Linha descritiva 1\n  Linha descritiva 2\n" in raw_text
        assert "---\n\nTranscrição de áudio completa.\nSegunda linha." in raw_text

        # 2. Retrieve via adapter and assert domain entity parity
        retrieved = adapter.get_raw_transcript(cid)
        assert retrieved is not None
        assert retrieved.content.id == cid
        assert retrieved.content.title == 'Título com "Aspas"'
        assert retrieved.content.body == "Transcrição de áudio completa.\nSegunda linha."
        assert retrieved.channel.name == 'Canal "Socio-Político"'
        assert retrieved.channel.id == ChannelId("UC_abc_999")
        assert retrieved.channel.category == 'Categoria "Alpha"'
        assert retrieved.provenance.url == "https://youtube.com/watch?v=vid_rich_123"
        assert retrieved.provenance.description == "Linha descritiva 1\nLinha descritiva 2"
        assert retrieved.provenance.publication_date == date(2023, 11, 25)

    def test_save_and_get_raw_transcript_defaults_and_fallbacks(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify save_transcript and get_raw_transcript handle optional/none fields gracefully."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("vid_min_456")
        channel = Channel(name="Simple Channel")
        provenance = MediaProvenance.create(
            url="https://youtube.com/watch?v=min",
            description="",
            publication_date=None,
        )
        content = Content.create(
            id=cid,
            title="",  # Empty title triggers fallback to content.id.value
            body="Minimum transcript body.",
        )
        transcript = SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )

        adapter.save_transcript(transcript)

        saved_file = raw_dir / "Simple Channel" / "vid_min_456.md"
        assert saved_file.is_file()
        raw_text = saved_file.read_text(encoding="utf-8")
        assert 'video_title: "vid_min_456"\n' in raw_text
        assert "channel_id: unknown_channel\n" in raw_text
        assert 'channel_category: "uncategorized"\n' in raw_text
        assert "video_date: \n" in raw_text
        assert "video_description: |\n\n" in raw_text

        retrieved = adapter.get_raw_transcript(cid)
        assert retrieved is not None
        assert retrieved.content.id == cid
        assert retrieved.channel.id == ChannelId("unknown_channel")
        assert retrieved.channel.category == "uncategorized"
        assert retrieved.provenance.publication_date is None
        assert retrieved.provenance.description == ""

    def test_get_raw_transcript_alternative_frontmatter_keys(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_raw_transcript parses alternate frontmatter aliases for channel, title, and domain."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("vid_alt_789")
        ch_folder = raw_dir / "FolderChannelName"
        ch_folder.mkdir(parents=True, exist_ok=True)
        raw_file = ch_folder / "vid_alt_789.md"
        raw_file.write_text(
            """---
title: Alternative Title Key
channel: Alternative Channel Key
domain: Alternative Category Key
source_url: https://youtube.com/watch?v=source_alt
upload_date: 20240315
video_description: Alternative description text
---

Alternative transcript body with extra content.
""",
            encoding="utf-8",
        )

        retrieved = adapter.get_raw_transcript(cid)
        assert retrieved is not None
        assert retrieved.content.title == "Alternative Title Key"
        assert retrieved.channel.name == "Alternative Channel Key"
        assert retrieved.channel.category == "Alternative Category Key"
        assert retrieved.provenance.url == "https://youtube.com/watch?v=source_alt"
        assert retrieved.provenance.publication_date == date(2024, 3, 15)
        assert retrieved.provenance.description == "Alternative description text"
        assert retrieved.content.body == "Alternative transcript body with extra content."

        # Parent directory fallback when channel keys are missing
        cid2 = ContentId("vid_folder_fallback")
        raw_file2 = ch_folder / "vid_folder_fallback.md"
        raw_file2.write_text(
            """---
video_title: Fallback Channel Parent
---
Body text.
""",
            encoding="utf-8",
        )
        retrieved2 = adapter.get_raw_transcript(cid2)
        assert retrieved2 is not None
        assert retrieved2.channel.name == "FolderChannelName"

    def test_save_and_get_enriched_compendium_rich_metadata_and_escaping(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify save_enriched_compendium and get_enriched_compendium with full metadata and escaping."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("comp_rich_001")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName('Canal "Avançado"'),
            title=NoteTitle("Compêndio Epistêmico"),
            body="Corpo analítico denso e estruturado.",
            complementary_info="Matriz complementar de factualidade e genealogia.",
            pass_count=3,
            channel_id=ChannelId("UC_comp_777"),
            channel_category='Categoria "Beta"',
            source_url="https://youtube.com/watch?v=comp_rich_001",
            video_date="20240520",
            video_description="Linha 1\nLinha 2",
        )

        adapter.save_enriched_compendium(comp)

        saved_file = enriched_dir / "Canal _Avançado_" / "comp_rich_001.md"
        assert saved_file.is_file()
        raw_text = saved_file.read_text(encoding="utf-8")
        assert 'video_title: "Compêndio Epistêmico"\n' in raw_text
        assert "video_id: comp_rich_001\n" in raw_text
        assert 'channel_name: "Canal \\"Avançado\\""\n' in raw_text
        assert "channel_id: UC_comp_777\n" in raw_text
        assert 'channel_category: "Categoria \\"Beta\\""\n' in raw_text
        assert "url: https://youtube.com/watch?v=comp_rich_001\n" in raw_text
        assert "video_date: 20240520\n" in raw_text
        assert "pass_count: 3\n" in raw_text
        assert "video_description: |\n  Linha 1\n  Linha 2\n" in raw_text
        assert (
            "---\n\n# Compêndio Epistêmico\n\n"
            "Corpo analítico denso e estruturado.\n\n"
            "## Informações Complementares\n\n"
            "Matriz complementar de factualidade e genealogia."
        ) in raw_text

        retrieved = adapter.get_enriched_compendium(cid)
        assert retrieved is not None
        assert retrieved.content_id == cid
        assert retrieved.title.value == "Compêndio Epistêmico"
        assert retrieved.channel_name == ChannelName('Canal "Avançado"')
        assert retrieved.channel_id == ChannelId("UC_comp_777")
        assert retrieved.channel_category == 'Categoria "Beta"'
        assert retrieved.source_url == "https://youtube.com/watch?v=comp_rich_001"
        assert retrieved.video_date == "20240520"
        assert retrieved.pass_count == 3
        assert retrieved.video_description == "Linha 1\nLinha 2"
        assert retrieved.body == "Corpo analítico denso e estruturado."
        assert retrieved.complementary_info == "Matriz complementar de factualidade e genealogia."

    def test_save_and_get_enriched_compendium_defaults_and_fallbacks(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify save_enriched_compendium and get_enriched_compendium default fallback behavior."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("comp_min_002")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Simple Channel"),
            title=NoteTitle("Minimal Compendium"),
            body="Minimal compendium body.",
            complementary_info="Informações complementares mínimas.",
            pass_count=1,
            channel_id=None,
            channel_category="",
            source_url="",
            video_date="",
            video_description="",
        )

        adapter.save_enriched_compendium(comp)

        saved_file = enriched_dir / "Simple Channel" / "comp_min_002.md"
        assert saved_file.is_file()
        raw_text = saved_file.read_text(encoding="utf-8")
        assert "channel_id: unknown_channel\n" in raw_text
        assert 'channel_category: "uncategorized"\n' in raw_text
        assert "video_description: |\n\n" in raw_text

        retrieved = adapter.get_enriched_compendium(cid)
        assert retrieved is not None
        assert retrieved.channel_id == ChannelId("unknown_channel")
        assert retrieved.channel_category == "uncategorized"
        assert retrieved.video_description == ""
        assert retrieved.complementary_info == "Informações complementares mínimas."

    def test_get_enriched_compendium_alternative_frontmatter_and_formatting(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_enriched_compendium handles alternative keys and bodies without title headers."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        cid = ContentId("comp_alt_003")
        ch_folder = enriched_dir / "FolderEnriched"
        ch_folder.mkdir(parents=True, exist_ok=True)
        file_path = ch_folder / "comp_alt_003.md"
        file_path.write_text(
            """---
channel: Alternative Channel
domain: Domain Economy
source_url: https://youtube.com/watch?v=alt_comp
video_date: 20240401
video_description: Alternative comp desc
---

Body without hash title heading directly here.

## Informações Complementares

Informações complementares analíticas para teste.
""",
            encoding="utf-8",
        )

        retrieved = adapter.get_enriched_compendium(cid)
        assert retrieved is not None
        assert retrieved.channel_name == ChannelName("Alternative Channel")
        assert retrieved.title.value == "comp_alt_003"  # Falls back to file_path.stem
        assert retrieved.channel_category == "Domain Economy"
        assert retrieved.source_url == "https://youtube.com/watch?v=alt_comp"
        assert retrieved.video_date == "20240401"
        assert retrieved.video_description == "Alternative comp desc"
        assert retrieved.pass_count == 1
        assert retrieved.body == "Body without hash title heading directly here."
        assert retrieved.complementary_info == "Informações complementares analíticas para teste."

        # Test: channel_name and channel both omitted: falls back to file_path.parent.name
        cid2 = ContentId("comp_parent_fallback")
        file_path2 = ch_folder / "comp_parent_fallback.md"
        file_path2.write_text(
            """---
title: Explicit Title Only
---
# Explicit Title Only

Body text here.

## Informações Complementares

Complementary data.
""",
            encoding="utf-8",
        )
        retrieved2 = adapter.get_enriched_compendium(cid2)
        assert retrieved2 is not None
        assert retrieved2.channel_name == ChannelName("FolderEnriched")
        assert retrieved2.title.value == "Explicit Title Only"
        assert retrieved2.body == "Body text here."
        assert retrieved2.complementary_info == "Complementary data."

    def test_get_enriched_files_for_channel_comprehensive_filtering(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_enriched_files_for_channel enforces existence, is_dir, and filename filters."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )

        # 1. Non-existent channel directory returns empty list
        assert adapter.get_enriched_files_for_channel(ChannelName("NonExistent")) == []

        # 2. Channel path is a file, not a directory: returns empty list without calling glob
        file_as_channel = enriched_dir / "FileChannel"
        file_as_channel.touch()
        orig_glob = Path.glob

        def guarded_glob(self_path: Path, pattern: str) -> Any:
            if self_path == file_as_channel:
                raise AssertionError("glob called on non-directory file_as_channel")
            return orig_glob(self_path, pattern)

        with patch.object(Path, "glob", guarded_glob):
            assert adapter.get_enriched_files_for_channel(ChannelName("FileChannel")) == []

        # 3. Channel directory with mixed valid and invalid files
        ch_dir = enriched_dir / "TestChannel"
        ch_dir.mkdir(parents=True, exist_ok=True)
        valid1 = ch_dir / "001_video.md"
        valid2 = ch_dir / "002_video.md"
        ignored_index = ch_dir / "_index.md"
        ignored_hidden = ch_dir / ".hidden.md"
        ignored_txt = ch_dir / "notes.txt"
        sub_dir = ch_dir / "nested.md"
        sub_dir.mkdir()  # Directory with .md extension: is_file() is False

        valid1.write_text("v1", encoding="utf-8")
        valid2.write_text("v2", encoding="utf-8")
        ignored_index.write_text("index", encoding="utf-8")
        ignored_hidden.write_text("hidden", encoding="utf-8")
        ignored_txt.write_text("txt", encoding="utf-8")

        result = adapter.get_enriched_files_for_channel(ChannelName("TestChannel"))
        assert result == [valid1, valid2]

    def test_get_raw_transcript_empty_metadata_fallbacks(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_raw_transcript handles frontmatter where optional keys are absent or empty."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        ch_folder = raw_dir / "EmptyMetadataChannel"
        ch_folder.mkdir(parents=True, exist_ok=True)
        raw_file = ch_folder / "empty_meta_123.md"
        raw_file.write_text(
            """---
channel_name: EmptyMetadataChannel
---
Body text only.
""",
            encoding="utf-8",
        )

        retrieved = adapter.get_raw_transcript(ContentId("empty_meta_123"))
        assert retrieved is not None
        assert retrieved.content.title == ""
        assert len(retrieved.content.title) == 0
        assert retrieved.channel.id is None
        assert retrieved.channel.category == ""
        assert len(retrieved.channel.category) == 0
        assert retrieved.provenance.url == ""
        assert len(retrieved.provenance.url) == 0
        assert retrieved.provenance.publication_date is None

    def test_get_enriched_compendium_empty_metadata_and_body_stripping(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_enriched_compendium handles empty metadata and multi-line body heading stripping."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        ch_folder = enriched_dir / "EmptyMetaEnriched"
        ch_folder.mkdir(parents=True, exist_ok=True)
        comp_file = ch_folder / "empty_comp_456.md"
        comp_file.write_text(
            """---
channel_name: EmptyMetaEnriched
title: Compendium Title
---
# Compendium Title
Line 1 of body
Line 2 of body

## Informações Complementares

Informações complementares para teste.
""",
            encoding="utf-8",
        )

        retrieved = adapter.get_enriched_compendium(ContentId("empty_comp_456"))
        assert retrieved is not None
        assert retrieved.channel_id is None
        assert retrieved.channel_category == ""
        assert len(retrieved.channel_category) == 0
        assert retrieved.source_url == ""
        assert len(retrieved.source_url) == 0
        assert retrieved.video_date == ""
        assert len(retrieved.video_date) == 0
        # Line 1 of body must be present (kills body_lines[2:] mutant!)
        assert retrieved.body.startswith("Line 1 of body")
        assert "Line 2 of body" in retrieved.body

    def test_get_enriched_compendium_missing_complementary_raises_error(
        self, storage_paths: tuple[Path, Path, Path]
    ) -> None:
        """Verify get_enriched_compendium fails when Informações Complementares is absent."""
        vault_dir, raw_dir, enriched_dir = storage_paths
        adapter = ObsidianVaultAdapter(
            vault_dir=vault_dir, raw_dir=raw_dir, enriched_dir=enriched_dir
        )
        ch_folder = enriched_dir / "NoCompChannel"
        ch_folder.mkdir(parents=True, exist_ok=True)
        comp_file = ch_folder / "no_comp_789.md"
        comp_file.write_text(
            """---
channel_name: NoCompChannel
title: Missing Comp Section
---
# Missing Comp Section

Only body here, no complementary section.
""",
            encoding="utf-8",
        )

        with pytest.raises(CompendiumStructureError):
            adapter.get_enriched_compendium(ContentId("no_comp_789"))



