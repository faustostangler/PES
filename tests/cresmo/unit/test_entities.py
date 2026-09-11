"""Unit tests for Cresmo Domain Entities and Aggregates.

Derived from SPEC-001 Section 2.2 & Section 5.
Verifies construction invariants, always-valid state, and exception mapping.
"""

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ContentId,
    NoteTitle,
    NoteType,
)


class TestRawTranscript:
    """SPEC-001 §2.2: RawTranscript invariants."""

    def test_valid_raw_transcript(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        transcript = RawTranscript(
            content_id=cid,
            channel_name="Example Channel",
            body="Valid spoken transcript body text.",
        )
        assert transcript.content_id == cid
        assert transcript.channel_name == "Example Channel"
        assert transcript.body == "Valid spoken transcript body text."

    def test_empty_body_raises_validation_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError):
            RawTranscript(
                content_id=cid,
                channel_name="Example Channel",
                body="",
            )


class TestEnrichedCompendium:
    """SPEC-001 §2.2: EnrichedCompendium invariants."""

    def test_valid_enriched_compendium(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            title=title,
            body="Continuous fluid prose analyzing institutional power dynamics.",
            complementary_info="Detailed historical and empirical datasets.",
            pass_count=3,
        )
        assert comp.content_id == cid
        assert comp.pass_count == 3

    def test_missing_complementary_info_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(CompendiumStructureError):
            EnrichedCompendium(
                content_id=cid,
                channel_name="Example Channel",
                title=title,
                body="Continuous prose body.",
                complementary_info="",
            )

    def test_markdown_tables_in_body_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(CompendiumStructureError):
            EnrichedCompendium(
                content_id=cid,
                channel_name="Example Channel",
                title=title,
                body="Text with table:\n| Col 1 | Col 2 |\n|---|---|\n| A | B |",
                complementary_info="Complementary info.",
            )


class TestAtomicNote:
    """SPEC-001 §2.2: AtomicNote invariants."""

    def test_valid_atomic_note(self) -> None:
        title = NoteTitle("Teoria das Elites")
        note = AtomicNote(
            title=title,
            note_type=NoteType.CONCEPT,
            definition="A circulação das elites postula que minorias organizadas governam maiorias desorganizadas.",
            causal_matrix=CausalMatrix(
                cause="Desorganização da massa", effect="Governo oligárquico"
            ),
            direct_relations=(NoteTitle("Vilfredo Pareto"),),
        )
        assert note.title == title
        assert note.note_type == NoteType.CONCEPT

    def test_short_definition_raises_validation_error(self) -> None:
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(DomainValidationError):
            AtomicNote(
                title=title,
                note_type=NoteType.CONCEPT,
                definition="Too short",
            )

    def test_self_referential_relation_raises_error(self) -> None:
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(SelfReferentialRelationError):
            AtomicNote(
                title=title,
                note_type=NoteType.CONCEPT,
                definition="A circulação das elites postula que minorias organizadas governam maiorias.",
                direct_relations=(title,),
            )


class TestMapOfContent:
    """SPEC-001 §2.2: MapOfContent invariants."""

    def test_valid_map_of_content(self) -> None:
        title = NoteTitle("MOC Teoria Política")
        note_a = NoteTitle("Teoria das Elites")
        note_b = NoteTitle("Institucionalismo")
        moc = MapOfContent(
            title=title,
            theme="Ciência Política",
            overview="Visão panorâmica das teorias estruturais de poder.",
            associated_notes=(note_a, note_b),
        )
        assert len(moc.associated_notes) == 2

    def test_empty_associated_notes_raises_validation_error(self) -> None:
        title = NoteTitle("MOC Vazio")
        with pytest.raises(DomainValidationError):
            MapOfContent(
                title=title,
                theme="Tema",
                overview="Visão geral",
                associated_notes=(),
            )

    def test_duplicate_notes_in_moc_raises_validation_error(self) -> None:
        title = NoteTitle("MOC Duplicado")
        note_a = NoteTitle("Teoria das Elites")
        with pytest.raises(DomainValidationError):
            MapOfContent(
                title=title,
                theme="Tema",
                overview="Visão geral",
                associated_notes=(note_a, note_a),
            )

    def test_raw_transcript_empty_channel_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError, match="channel_name cannot be empty"):
            RawTranscript(content_id=cid, channel_name="   ", body="Valid body.")

    def test_enriched_compendium_empty_body_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(CompendiumStructureError, match="body cannot be empty"):
            EnrichedCompendium(
                content_id=cid,
                channel_name="Channel",
                title=NoteTitle("Title"),
                body="   ",
                complementary_info="Complementary info.",
            )

    def test_enriched_compendium_invalid_pass_count_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(CompendiumStructureError, match="pass_count must be at least 1"):
            EnrichedCompendium(
                content_id=cid,
                channel_name="Channel",
                title=NoteTitle("Title"),
                body="Valid body.",
                complementary_info="Complementary info.",
                pass_count=0,
            )
