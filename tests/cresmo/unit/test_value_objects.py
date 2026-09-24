"""Unit tests for Cresmo Domain Value Objects.

Derived from SPEC-001 Section 2.1 & Section 5.
Verifies construction invariants, zero primitive obsession, and boundary validation.
"""

import pytest

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
    normalize_to_uploads_playlist_url,
)


class TestContentId:
    """SPEC-001 §2.1: ContentId validation."""

    def test_valid_content_id(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        assert cid.value == "dQw4w9WgXcQ"
        assert str(cid) == "dQw4w9WgXcQ"

    def test_empty_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("")

    def test_whitespace_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("   ")

    def test_invalid_characters_in_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("invalid/id#special!")


class TestNoteTitle:
    """SPEC-001 §2.1: NoteTitle validation & sanitization."""

    def test_valid_note_title(self) -> None:
        title = NoteTitle("Teoria das Elites")
        assert title.value == "Teoria das Elites"
        assert str(title) == "Teoria das Elites"

    def test_strips_brackets_from_title(self) -> None:
        title = NoteTitle("[[Teoria das Elites]]")
        assert title.value == "Teoria das Elites"

    def test_sanitizes_illegal_filesystem_characters(self) -> None:
        title = NoteTitle("Teoria / Elites: Modelo?")
        assert "/" not in title.value
        assert ":" not in title.value
        assert "?" not in title.value

    def test_empty_title_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            NoteTitle("")

    def test_generic_placeholder_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            NoteTitle("Untitled_Note")


class TestNoteType:
    """SPEC-001 §2.1: NoteType enum parsing."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("concept", NoteType.CONCEPT),
            ("CONCEPT", NoteType.CONCEPT),
            ("entity", NoteType.ENTITY),
            ("event", NoteType.EVENT),
            ("process", NoteType.PROCESS),
        ],
    )
    def test_valid_note_types(self, raw: str, expected: NoteType) -> None:
        assert NoteType.from_string(raw) == expected

    def test_invalid_note_type_raises_typology_error(self) -> None:
        with pytest.raises(
            NoteTypologyError,
            match=r"Invalid note typology 'invalid_type'\. Expected one of: \['concept', 'entity', 'event', 'process'\]",
        ):
            NoteType.from_string("invalid_type")


class TestCausalMatrix:
    """SPEC-001 §2.1: CausalMatrix validation."""

    def test_valid_causal_matrix(self) -> None:
        matrix = CausalMatrix(
            cause="Centralização fiscal",
            effect="Dependência municipal",
            epistemic_attribution="Tocqueville",
        )
        assert matrix.cause == "Centralização fiscal"
        assert matrix.effect == "Dependência municipal"
        assert matrix.epistemic_attribution == "Tocqueville"

    def test_whitespace_trimmed_in_causal_matrix(self) -> None:
        matrix = CausalMatrix(
            cause="  Causa  ",
            effect="  Efeito  ",
            epistemic_attribution="  Fonte  ",
        )
        assert matrix.cause == "Causa"
        assert matrix.effect == "Efeito"
        assert matrix.epistemic_attribution == "Fonte"

    def test_empty_cause_with_effect_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            CausalMatrix(cause="", effect="Efeito")


class TestAtomicEntityInventory:
    """SPEC-001 §2.1: AtomicEntityInventory validation."""

    def test_valid_inventory(self) -> None:
        t1 = NoteTitle("Conceito A")
        t2 = NoteTitle("Conceito B")
        inv = AtomicEntityInventory(items=((t1, NoteType.CONCEPT), (t2, NoteType.ENTITY)))
        assert len(inv.items) == 2

    def test_duplicate_titles_in_inventory_raises_validation_error(self) -> None:
        t1 = NoteTitle("Conceito A")
        with pytest.raises(DomainValidationError):
            AtomicEntityInventory(items=((t1, NoteType.CONCEPT), (t1, NoteType.ENTITY)))

    def test_empty_inventory_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            AtomicEntityInventory(items=())


class TestCrossContextRelations:
    """CrossContextRelations validation and stripping."""

    def test_cross_context_strips_whitespace(self) -> None:
        cc = CrossContextRelations(
            precursors="  Precursor  ",
            lateral_events="  Lateral  ",
            aftermath="  Aftermath  ",
        )
        assert cc.precursors == "Precursor"
        assert cc.lateral_events == "Lateral"
        assert cc.aftermath == "Aftermath"


class TestNormalizeToUploadsPlaylistUrl:
    """Tests for channel ID normalization to canonical uploads playlist (UU...) URLs."""

    def test_uc_channel_id_converted_to_uu_playlist(self) -> None:
        raw_id = "UCemIxU4HzIhVLeohT7eUUoA"
        assert (
            normalize_to_uploads_playlist_url(raw_id)
            == "https://www.youtube.com/playlist?list=UUemIxU4HzIhVLeohT7eUUoA"
        )

    def test_channel_url_with_uc_id_converted_to_uu_playlist(self) -> None:
        url = "https://www.youtube.com/channel/UCLTWPE7XrHEe8m_xAmNbQ-Q"
        assert (
            normalize_to_uploads_playlist_url(url)
            == "https://www.youtube.com/playlist?list=UULTWPE7XrHEe8m_xAmNbQ-Q"
        )

    def test_existing_playlist_url_preserved(self) -> None:
        url = "https://www.youtube.com/playlist?list=UULTWPE7XrHEe8m_xAmNbQ-Q"
        assert normalize_to_uploads_playlist_url(url) == url

    def test_user_handle_appends_videos_tab(self) -> None:
        handle_url = "https://www.youtube.com/@ancapsu"
        assert (
            normalize_to_uploads_playlist_url(handle_url)
            == "https://www.youtube.com/@ancapsu/videos"
        )

    def test_empty_string_returned_intact(self) -> None:
        assert normalize_to_uploads_playlist_url("") == ""


class TestMasterDocumentResult:
    """Tests for MasterDocumentResult value object invariant enforcement."""

    def test_valid_master_document_result(self) -> None:
        from pathlib import Path

        from cresmo.domain.value_objects import MasterDocumentResult

        res = MasterDocumentResult(
            channel_name="Fabio Akita",
            channel_category="tech_ai",
            output_path=Path("/tmp/master/tech_ai/Fabio_Akita_001.md"),
            part_number=1,
            word_count=450000,
            document_count=25,
            video_ids=("vid1", "vid2"),
        )
        assert res.channel_name == "Fabio Akita"
        assert res.channel_category == "tech_ai"
        assert res.part_number == 1
        assert res.word_count == 450000
        assert res.document_count == 25
        assert len(res.video_ids) == 2

    def test_invalid_channel_name_raises_domain_error(self) -> None:
        from pathlib import Path

        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import MasterDocumentResult

        with pytest.raises(DomainValidationError, match="cannot be empty or whitespace"):
            MasterDocumentResult(
                channel_name="   ",
                channel_category="tech_ai",
                output_path=Path("/tmp/out.md"),
                part_number=1,
                word_count=100,
                document_count=1,
                video_ids=("vid1",),
            )

    def test_invalid_part_number_raises_domain_error(self) -> None:
        from pathlib import Path

        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import MasterDocumentResult

        with pytest.raises(DomainValidationError, match="part_number must be >= 1"):
            MasterDocumentResult(
                channel_name="Channel",
                channel_category="tech_ai",
                output_path=Path("/tmp/out.md"),
                part_number=0,
                word_count=100,
                document_count=1,
                video_ids=("vid1",),
            )


class TestChannelName:
    def test_valid_channel_name(self) -> None:
        from cresmo.domain.value_objects import ChannelName

        cn = ChannelName("  Fabio Akita  ")
        assert cn.value == "Fabio Akita"
        assert str(cn) == "Fabio Akita"
        assert cn == "Fabio Akita"
        assert cn == ChannelName("Fabio Akita")

    def test_empty_or_whitespace_channel_name_raises(self) -> None:
        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import ChannelName

        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            ChannelName("")
        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            ChannelName("   ")

    def test_path_traversal_channel_name_raises(self) -> None:
        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import ChannelName

        with pytest.raises(DomainValidationError, match="path traversal"):
            ChannelName("../../etc/passwd")
        with pytest.raises(DomainValidationError, match="path traversal"):
            ChannelName("channel/subfolder")
        with pytest.raises(DomainValidationError, match="path traversal"):
            ChannelName("channel\\subfolder")

    def test_channel_name_too_long_raises(self) -> None:
        from cresmo.domain.exceptions import DomainValidationError
        from cresmo.domain.value_objects import ChannelName

        with pytest.raises(DomainValidationError, match="exceeds maximum length"):
            ChannelName("A" * 121)

    def test_from_string_factory(self) -> None:
        from cresmo.domain.value_objects import ChannelName

        cn = ChannelName.from_string("Veritasium")
        assert isinstance(cn, ChannelName)
        assert cn.value == "Veritasium"
        assert ChannelName.from_string(cn) is cn


class TestSourceModality:
    def test_source_modality_members(self) -> None:
        from cresmo.domain.value_objects import SourceModality

        assert SourceModality.FILE == "file"
        assert SourceModality.URL == "url"
        assert SourceModality("file") is SourceModality.FILE
        assert SourceModality("url") is SourceModality.URL
