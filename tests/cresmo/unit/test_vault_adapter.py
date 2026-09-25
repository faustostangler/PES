"""Unit tests for ObsidianVaultAdapter.

Tests atomic file persistence, YAML frontmatter formatting,
index synchronization, note deletion, subfolder routing,
and inbound WikiLink rewriting per SPEC-001 Section 4.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ChannelId,
    ChannelName,
    ContentId,
    CrossContextRelations,
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
        raw = RawTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Spoken speech transcript line 1.\nSpoken speech transcript line 2.",
        )

        adapter.save_raw_transcript(raw)
        retrieved = adapter.get_raw_transcript(cid)

        assert retrieved is not None
        assert retrieved.content_id == cid
        assert retrieved.channel_name == ChannelName("Political Theory")
        assert "transcript line 1" in retrieved.body

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
        assert transcript.channel_name == ChannelName("ChannelFolder")
        assert "Plain markdown body" in transcript.body

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
        assert transcript.upload_date is None

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
        target = concepts_dir / "Note.md"
        target.write_text("Reference to [[Old Title]].", encoding="utf-8")

        with patch("pathlib.Path.read_text", side_effect=OSError("Disk read error")):
            count = adapter.rewrite_wiki_links(NoteTitle("Old Title"), NoteTitle("New Title"))
            assert count == 0

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

        # 2. Save master document
        out_path = adapter.save_master_document(
            channel_name=ChannelName("Fabio Akita"),
            channel_category="tech_ai",
            part_number=1,
            content="Aggregated master content part 1",
        )
        assert out_path.exists()
        assert out_path.name == "Fabio_Akita_001.md"
        assert out_path.parent.name == "tech_ai"
        assert out_path.read_text(encoding="utf-8") == "Aggregated master content part 1"

        # 3. Clear master documents
        adapter.clear_master_documents_for_channel(
            channel_name=ChannelName("Fabio Akita"),
            channel_category="tech_ai",
        )
        assert not out_path.exists()

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
