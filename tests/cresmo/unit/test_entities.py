"""Unit tests for Cresmo Domain Entities and Aggregates.

Derived from SPEC-001 Section 2.2 & Section 5.
Verifies construction invariants, always-valid state, and exception mapping.
"""

import datetime

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    ChannelTenantId,
    EnrichedCompendium,
    MapOfContent,
    PipelineSessionId,
    RawTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ChannelId,
    ChannelName,
    ContentId,
    NoteTitle,
    NoteType,
)


class TestRawTranscript:
    """SPEC-001 §2.2: RawTranscript invariants."""

    def test_valid_raw_transcript(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        pub = datetime.date(2023, 5, 12)
        transcript = RawTranscript(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            body="Valid spoken transcript body text.",
            publication_date=pub,
        )
        assert transcript.content_id == cid
        assert transcript.channel_name == ChannelName("Example Channel")
        assert isinstance(transcript.channel_name, ChannelName)
        assert transcript.body == "Valid spoken transcript body text."
        assert transcript.publication_date == pub
        assert transcript.upload_date == pub

    def test_empty_body_raises_validation_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError):
            RawTranscript(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                body="",
            )


class TestEnrichedCompendium:
    """SPEC-001 §2.2: EnrichedCompendium invariants."""

    def test_valid_enriched_compendium(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=title,
            body="Continuous fluid prose analyzing institutional power dynamics.",
            complementary_info="Detailed historical and empirical datasets.",
            pass_count=3,
            video_date="20240315",
        )
        assert comp.content_id == cid
        assert comp.pass_count == 3
        assert isinstance(comp.channel_name, ChannelName)
        assert comp.channel_name == ChannelName("Example Channel")
        assert comp.video_date == "20240315"
        assert comp.publication_date == datetime.date(2024, 3, 15)

    def test_missing_complementary_info_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(CompendiumStructureError):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
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
                channel_name=ChannelName("Example Channel"),
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
        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            RawTranscript(content_id=cid, channel_name=ChannelName("   "), body="Valid body.")

    def test_enriched_compendium_empty_body_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(CompendiumStructureError, match="body cannot be empty"):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Channel"),
                title=NoteTitle("Title"),
                body="   ",
                complementary_info="Complementary info.",
            )

    def test_enriched_compendium_invalid_pass_count_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(CompendiumStructureError, match="pass_count must be at least 1"):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Channel"),
                title=NoteTitle("Title"),
                body="Valid body.",
                complementary_info="Complementary info.",
                pass_count=0,
            )


class TestPipelineSessionId:
    """ADR-027 & SPEC-010: PipelineSessionId canonical format {channel_id}:{video_id}."""

    def test_create_with_channel_name_only_produces_canonical_format(self) -> None:
        """When ChannelId is omitted, session format is {channel_name}:{video_id}."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Marcelo Andrade"),
            content_id=ContentId("9IbNJ0EsTxI"),
        )
        assert sid.value == "Marcelo Andrade:9IbNJ0EsTxI"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert sid.video_id == "9IbNJ0EsTxI"
        assert sid.channel_token == "Marcelo Andrade"
        assert not hasattr(sid, "channel_name")

    def test_create_with_channel_id_prefers_id_over_name(self) -> None:
        """When ChannelId is available, the algorithmic session ID uses {channel_id}:{video_id}."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Marcelo Andrade"),
            content_id=ContentId("9IbNJ0EsTxI"),
            channel_id=ChannelId("UCxyz1234567890ab"),
        )
        assert sid.value == "UCxyz1234567890ab:9IbNJ0EsTxI"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert sid.video_id == "9IbNJ0EsTxI"
        assert sid.channel_token == "UCxyz1234567890ab"
        assert not hasattr(sid, "channel_name")

    def test_create_with_channel_id_none_falls_back_to_name(self) -> None:
        """Explicit None channel_id falls back to ChannelName."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Philosophy"),
            content_id=ContentId("abcd1234efgh"),
            channel_id=None,
        )
        assert sid.value == "Philosophy:abcd1234efgh"
        assert sid.channel_token == "Philosophy"
        assert sid.video_id == "abcd1234efgh"

    def test_create_with_string_channel_still_works(self) -> None:
        """Passing a raw string for channel produces canonical {channel}:{content_id}."""
        sid = PipelineSessionId.create(
            channel="Raw String Channel",
            content_id="dQw4w9WgXcQ",
        )
        assert sid.value == "Raw String Channel:dQw4w9WgXcQ"
        assert sid.channel_token == "Raw String Channel"
        assert sid.video_id == "dQw4w9WgXcQ"

    def test_legacy_three_part_format_backward_compatible(self) -> None:
        """Parsing legacy 'content:{channel}:{content_id}' remains supported."""
        sid = PipelineSessionId(value="content:Marcelo Andrade:9IbNJ0EsTxI")
        assert sid.channel_token == "Marcelo Andrade"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert sid.video_id == "9IbNJ0EsTxI"

    def test_empty_session_id_raises_error(self) -> None:
        with pytest.raises(ValueError, match="PipelineSessionId cannot be empty"):
            PipelineSessionId(value="")

    def test_invalid_format_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid PipelineSessionId format"):
            PipelineSessionId(value="invalid_format_without_colons")


class TestUserIdentity:
    """ADR-027 & SPEC-010: UserIdentity taxonomy for IAM, CLI, and Workers."""

    def test_worker_identity(self) -> None:
        """Worker identity generates system:worker with provider system."""
        user = UserIdentity.worker()
        assert user.value == "system:worker"
        assert not user.is_anonymous
        assert user.provider == "system"
        assert user.subject == "worker"

    def test_worker_identity_custom_name(self) -> None:
        """Worker identity accepts custom worker identifier."""
        user = UserIdentity.worker(name="channel_sync")
        assert user.value == "system:channel_sync"
        assert not user.is_anonymous
        assert user.provider == "system"
        assert user.subject == "channel_sync"

    def test_identified_iam_user(self) -> None:
        """Identified IAM user generates user:iam:{username}."""
        user = UserIdentity.identified(subject="alice", provider="iam")
        assert user.value == "user:iam:alice"
        assert not user.is_anonymous
        assert user.provider == "iam"
        assert user.subject == "alice"

    def test_anonymous_user(self) -> None:
        """Anonymous user generates anonymous with provider anonymous."""
        user = UserIdentity.anonymous()
        assert user.value == "anonymous"
        assert user.is_anonymous
        assert user.provider == "anonymous"
        assert user.subject == ""

    def test_anonymous_user_with_token(self) -> None:
        """Anonymous user with token generates anon:{token}."""
        user = UserIdentity.anonymous(token="guest_123")
        assert user.value == "anon:guest_123"
        assert user.is_anonymous

    def test_empty_user_identity_raises_error(self) -> None:
        with pytest.raises(ValueError, match="UserIdentity cannot be empty"):
            UserIdentity(value="")

    def test_identified_empty_subject_raises_error(self) -> None:
        with pytest.raises(
            ValueError, match="Identified UserIdentity requires a non-empty subject"
        ):
            UserIdentity.identified(subject="   ", provider="iam")


class TestChannelTenantId:
    """Phase 1: ChannelTenantId must prefer ChannelId (stable) over ChannelName (mutable)."""

    def test_create_with_channel_name_only_backward_compatible(self) -> None:
        """Existing callers that pass only ChannelName still produce valid tenant IDs."""
        tid = ChannelTenantId.create(channel=ChannelName("Marcelo Andrade"))
        assert tid.value == "channel:Marcelo Andrade"
        assert tid.channel_token == "Marcelo Andrade"
        assert not hasattr(tid, "channel_name")

    def test_create_with_channel_id_prefers_id_over_name(self) -> None:
        """When ChannelId is available, the algorithmic key uses the stable ID."""
        tid = ChannelTenantId.create(
            channel=ChannelName("Marcelo Andrade"),
            channel_id=ChannelId("UCxyz1234567890ab"),
        )
        # Algorithmic key must use ChannelId, not ChannelName
        assert tid.value == "channel:UCxyz1234567890ab"
        assert tid.channel_token == "UCxyz1234567890ab"
        assert not hasattr(tid, "channel_name")

    def test_create_with_channel_id_none_falls_back_to_name(self) -> None:
        """Explicit None channel_id falls back to ChannelName."""
        tid = ChannelTenantId.create(
            channel=ChannelName("Philosophy"),
            channel_id=None,
        )
        assert tid.value == "channel:Philosophy"
        assert tid.channel_token == "Philosophy"

    def test_create_with_string_channel_still_works(self) -> None:
        """Passing a raw string for channel remains backward-compatible."""
        tid = ChannelTenantId.create(channel="Raw String")
        assert tid.value == "channel:Raw String"

    def test_empty_tenant_id_raises_error(self) -> None:
        with pytest.raises(ValueError, match="ChannelTenantId cannot be empty"):
            ChannelTenantId(value="")

    def test_invalid_format_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid ChannelTenantId format"):
            ChannelTenantId(value="bad_format")
