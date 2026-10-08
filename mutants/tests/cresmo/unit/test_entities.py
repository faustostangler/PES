"""Unit tests for Cresmo Domain Entities and Aggregates.

Derived from SPEC-001 Section 2.2 & Section 5.
Verifies construction invariants, always-valid state, and exception mapping.
"""

import datetime

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    FluidTranscript,
    JudgeFrictionMetric,
    MapOfContent,
    PipelineSessionId,
    SourceTranscript,
    Transcript,
    UserIdentity,
    post_process_fluid_transcript,
)

from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CandidateText,
    CausalMatrix,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    NoteTitle,
    NoteType,
)


class TestSourceTranscript:
    """SPEC-001 §2.2 & ADR-031: SourceTranscript invariants."""

    def test_valid_source_transcript(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        pub = datetime.date(2023, 5, 12)
        transcript = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            body="Valid spoken transcript body text.",
            publication_date=pub,
        )
        assert transcript.content.id == cid
        assert transcript.channel.name == "Example Channel"
        assert transcript.content.body == "Valid spoken transcript body text."
        assert transcript.provenance.publication_date == pub

    def test_empty_body_raises_validation_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError):
            SourceTranscript(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                body="",
            )

    def test_source_transcript_channel_and_content_properties(self) -> None:
        from cresmo.domain.value_objects import Channel, Content

        cid = ContentId("dQw4w9WgXcQ")
        pub = datetime.date(2023, 5, 12)
        transcript = SourceTranscript(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            body="Valid spoken transcript body text.",
            title="My Cool Video",
            source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            publication_date=pub,
            channel_id=ChannelId("UC1234567890abcdef"),
            channel_category="Science",
        )
        ch = transcript.channel
        assert isinstance(ch, Channel)
        assert ch.name == "Example Channel"
        assert ch.id == ChannelId("UC1234567890abcdef")
        assert ch.category == "Science"

        cnt = transcript.content
        assert isinstance(cnt, Content)
        assert cnt.id == cid
        assert cnt.title == "My Cool Video"
        assert transcript.provenance.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert transcript.provenance.publication_date == pub


class TestEnrichedCompendium:
    """SPEC-001 §2.2: EnrichedCompendium invariants and edge cases."""

    def test_valid_enriched_compendium_with_all_fields(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        pub = datetime.date(2024, 3, 15)
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name="Example Channel",
            channel_id="UC1234567890abcdef",
            channel_category="Political Science",
            source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            video_description="Original video summary.",
            title=title,
            body="Continuous fluid prose analyzing institutional power dynamics.",
            complementary_info="Detailed historical and empirical datasets.",
            pass_count=3,
            publication_date=pub,
            video_date="2024-03-15",
        )
        assert comp.content_id == cid
        assert isinstance(comp.channel_name, ChannelName)
        assert comp.channel_name == ChannelName("Example Channel")
        assert comp.channel_name.value == "Example Channel"
        assert isinstance(comp.channel_id, ChannelId)
        assert comp.channel_id == ChannelId("UC1234567890abcdef")
        assert comp.channel_id.value == "UC1234567890abcdef"
        assert comp.channel_category == "Political Science"
        assert comp.source_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert comp.video_description == "Original video summary."
        assert comp.title == title
        assert comp.body == "Continuous fluid prose analyzing institutional power dynamics."
        assert comp.complementary_info == "Detailed historical and empirical datasets."
        assert comp.pass_count == 3
        assert comp.video_date == "2024-03-15"
        assert comp.publication_date == pub

    def test_defaults_when_minimal_fields_passed(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=title,
            body="Continuous fluid prose analyzing institutional power dynamics.",
            complementary_info="Detailed historical and empirical datasets.",
        )
        assert comp.pass_count == 1
        assert comp.channel_id is None
        assert comp.channel_category == ""
        assert comp.source_url == ""
        assert comp.publication_date is None
        assert comp.video_date == ""
        assert comp.video_description == ""

    def test_channel_id_as_channel_id_vo(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        ch_id = ChannelId("UC1234567890abcdef")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            channel_id=ch_id,
            title=NoteTitle("Title"),
            body="Body.",
            complementary_info="Info.",
        )
        assert comp.channel_id is ch_id

    def test_publication_date_harmonization_from_publication_date_only(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        pub = datetime.date(2024, 7, 10)
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=NoteTitle("Title"),
            body="Body.",
            complementary_info="Info.",
            publication_date=pub,
            video_date="",
        )
        assert comp.publication_date == pub
        assert comp.video_date == "2024-07-10"

    def test_publication_date_harmonization_from_iso_video_date(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=NoteTitle("Title"),
            body="Body.",
            complementary_info="Info.",
            publication_date=None,
            video_date="2024-07-10T15:30:00Z",
        )
        assert comp.publication_date == datetime.date(2024, 7, 10)
        assert comp.video_date == "2024-07-10T15:30:00Z"

    def test_publication_date_harmonization_invalid_video_date_fallback(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=NoteTitle("Title"),
            body="Body.",
            complementary_info="Info.",
            publication_date=None,
            video_date="not_a_valid_date",
        )
        assert comp.publication_date is None
        assert comp.video_date == "not_a_valid_date"

    def test_publication_date_takes_precedence_over_video_date(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        pub = datetime.date(2024, 1, 1)
        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=NoteTitle("Title"),
            body="Body.",
            complementary_info="Info.",
            publication_date=pub,
            video_date="2024-12-31",
        )
        assert comp.publication_date == pub
        assert comp.video_date == "2024-12-31"

    def test_missing_complementary_info_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(
            CompendiumStructureError,
            match=r"^EnrichedCompendium must contain a non-empty 'Informações Complementares' section\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="Continuous prose body.",
                complementary_info="",
            )
        with pytest.raises(
            CompendiumStructureError,
            match=r"^EnrichedCompendium must contain a non-empty 'Informações Complementares' section\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="Continuous prose body.",
                complementary_info="   \t  \n ",
            )

    def test_empty_body_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(
            CompendiumStructureError,
            match=r"^EnrichedCompendium body cannot be empty\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="",
                complementary_info="Complementary info.",
            )
        with pytest.raises(
            CompendiumStructureError,
            match=r"^EnrichedCompendium body cannot be empty\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="   \n \t  ",
                complementary_info="Complementary info.",
            )

    def test_markdown_tables_in_body_raises_structure_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(
            CompendiumStructureError,
            match=r"^EnrichedCompendium body must be continuous prose and cannot contain Markdown tables\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="Text with table:\n| Col 1 | Col 2 |\n|---|---|\n| A | B |",
                complementary_info="Complementary info.",
            )

    def test_pass_count_boundary_and_validation(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        title = NoteTitle("Teoria das Elites")

        comp = EnrichedCompendium(
            content_id=cid,
            channel_name=ChannelName("Example Channel"),
            title=title,
            body="Valid body.",
            complementary_info="Complementary info.",
            pass_count=1,
        )
        assert comp.pass_count == 1

        with pytest.raises(
            CompendiumStructureError,
            match=r"^pass_count must be at least 1\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="Valid body.",
                complementary_info="Complementary info.",
                pass_count=0,
            )
        with pytest.raises(
            CompendiumStructureError,
            match=r"^pass_count must be at least 1\.$",
        ):
            EnrichedCompendium(
                content_id=cid,
                channel_name=ChannelName("Example Channel"),
                title=title,
                body="Valid body.",
                complementary_info="Complementary info.",
                pass_count=-1,
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

    def test_definition_minimum_length_boundary(self) -> None:
        title = NoteTitle("Teoria das Elites")
        twenty_chars = "12345678901234567890"
        note = AtomicNote(
            title=title,
            note_type=NoteType.CONCEPT,
            definition=twenty_chars,
        )
        assert len(note.definition) == 20

    def test_short_definition_raises_validation_error(self) -> None:
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(
            DomainValidationError,
            match=r"^AtomicNote definition must contain at least 20 characters of contextual analysis\. Got: 'Too short'$",
        ):
            AtomicNote(
                title=title,
                note_type=NoteType.CONCEPT,
                definition="Too short",
            )

    def test_self_referential_relation_raises_error(self) -> None:
        title = NoteTitle("Teoria das Elites")
        with pytest.raises(
            SelfReferentialRelationError,
            match=r"^AtomicNote 'Teoria das Elites' cannot contain itself in direct_relations\.$",
        ):
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
        with pytest.raises(
            DomainValidationError,
            match=r"^MapOfContent must contain at least one associated note\.$",
        ):
            MapOfContent(
                title=title,
                theme="Tema",
                overview="Visão geral",
                associated_notes=(),
            )

    def test_duplicate_notes_in_moc_raises_validation_error(self) -> None:
        title = NoteTitle("MOC Duplicado")
        note_a = NoteTitle("Teoria das Elites")
        with pytest.raises(
            DomainValidationError,
            match=r"^Duplicate associated note 'Teoria das Elites' in MapOfContent\.$",
        ):
            MapOfContent(
                title=title,
                theme="Tema",
                overview="Visão geral",
                associated_notes=(note_a, note_a),
            )

    def test_unicode_case_preservation_for_duplicate_check(self) -> None:
        title = NoteTitle("MOC Sharp S")
        note_1 = NoteTitle("groß")
        note_2 = NoteTitle("gross")
        moc = MapOfContent(
            title=title,
            theme="Tema",
            overview="Visão geral",
            associated_notes=(note_1, note_2),
        )
        assert len(moc.associated_notes) == 2

    def test_source_transcript_empty_channel_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            SourceTranscript(content_id=cid, channel_name=ChannelName("   "), body="Valid body.")



class TestPipelineSessionId:
    """ADR-027, ADR-032 & ADR-033: PipelineSessionId canonical format {channel_id}:{content_id}."""

    def test_create_with_channel_name_only_produces_canonical_format(self) -> None:
        """When ChannelId is omitted, session format is {channel_name}:{content_id}."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Marcelo Andrade"),
            content_id=ContentId("9IbNJ0EsTxI"),
        )
        assert sid.value == "Marcelo Andrade:9IbNJ0EsTxI"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert sid.channel_id == "Marcelo Andrade"
        assert not hasattr(sid, "video_id")
        assert not hasattr(sid, "channel_token")

    def test_create_with_channel_id_prefers_id_over_name(self) -> None:
        """When ChannelId is available, the algorithmic session ID uses {channel_id}:{content_id}."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Marcelo Andrade"),
            content_id=ContentId("9IbNJ0EsTxI"),
            channel_id=ChannelId("UCxyz1234567890ab"),
        )
        assert sid.value == "UCxyz1234567890ab:9IbNJ0EsTxI"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert sid.channel_id == "UCxyz1234567890ab"
        assert not hasattr(sid, "video_id")
        assert not hasattr(sid, "channel_token")

    def test_create_with_channel_id_none_falls_back_to_name(self) -> None:
        """Explicit None channel_id falls back to ChannelName."""
        sid = PipelineSessionId.create(
            channel=ChannelName("Philosophy"),
            content_id=ContentId("abcd1234efgh"),
            channel_id=None,
        )
        assert sid.value == "Philosophy:abcd1234efgh"
        assert sid.channel_id == "Philosophy"
        assert not hasattr(sid, "video_id")

    def test_create_with_channel_and_content_value_objects(self) -> None:
        from cresmo.domain.value_objects import Channel, Content

        ch = Channel(name="Example Channel", id=ChannelId("UCxyz1234567890ab"))
        cnt = Content.create("9IbNJ0EsTxI")
        sid = PipelineSessionId.create(channel=ch, content_id=cnt)
        assert sid.value == "UCxyz1234567890ab:9IbNJ0EsTxI"
        assert sid.channel_id == "UCxyz1234567890ab"
        assert sid.content_id == "9IbNJ0EsTxI"

    def test_create_with_string_channel_still_works(self) -> None:
        """Passing a raw string for channel produces canonical {channel}:{content_id}."""
        sid = PipelineSessionId.create(
            channel="Raw String Channel",
            content_id="dQw4w9WgXcQ",
        )
        assert sid.value == "Raw String Channel:dQw4w9WgXcQ"
        assert sid.channel_id == "Raw String Channel"
        assert not hasattr(sid, "video_id")

    def test_legacy_three_part_format_backward_compatible(self) -> None:
        """Parsing legacy 'content:{channel}:{content_id}' remains supported."""
        sid = PipelineSessionId(value="content:Marcelo Andrade:9IbNJ0EsTxI")
        assert sid.channel_id == "Marcelo Andrade"
        assert sid.content_id == "9IbNJ0EsTxI"
        assert not hasattr(sid, "video_id")

    def test_empty_or_whitespace_session_id_raises_error(self) -> None:
        with pytest.raises(ValueError, match="^PipelineSessionId cannot be empty\\.$"):
            PipelineSessionId(value="")
        with pytest.raises(ValueError, match="^PipelineSessionId cannot be empty\\.$"):
            PipelineSessionId(value="   ")

    def test_canonical_two_parts_validation(self) -> None:
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: ':content123'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value=":content123")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'chan123:'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="chan123:")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: '   :content123'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="   :content123")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'chan123:   '\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="chan123:   ")

        sid = PipelineSessionId(value="chan123:content123")
        assert sid.channel_id == "chan123"
        assert sid.content_id == "content123"

    def test_legacy_three_parts_validation(self) -> None:
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'other:chan:content'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="other:chan:content")

        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'content::content123'\. Expected 'content:{channel}:{content_id}'\.$",
        ):
            PipelineSessionId(value="content::content123")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'content:chan:'\. Expected 'content:{channel}:{content_id}'\.$",
        ):
            PipelineSessionId(value="content:chan:")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'content:   :content123'\. Expected 'content:{channel}:{content_id}'\.$",
        ):
            PipelineSessionId(value="content:   :content123")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'content:chan:   '\. Expected 'content:{channel}:{content_id}'\.$",
        ):
            PipelineSessionId(value="content:chan:   ")

        sid = PipelineSessionId(value="content:my_chan:my_content")
        assert sid.channel_id == "my_chan"
        assert sid.content_id == "my_content"

    def test_other_part_counts_raise(self) -> None:
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'singlepart'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="singlepart")
        with pytest.raises(
            ValueError,
            match=r"^Invalid PipelineSessionId format: 'a:b:c:d'\. Expected '{channel_id}:{content_id}'\.$",
        ):
            PipelineSessionId(value="a:b:c:d")

    def test_create_with_channel_and_content_variants(self) -> None:
        from cresmo.domain.value_objects import Channel, ChannelId, ChannelName, Content, ContentId

        # Channel with id
        ch1 = Channel(name="Name1", id=ChannelId("UC_id1"))
        sid1 = PipelineSessionId.create(channel=ch1, content_id="vid1")
        assert sid1.value == "UC_id1:vid1"

        # Channel without id, explicit channel_id passed
        ch2 = Channel(name="Name2", id=None)
        sid2 = PipelineSessionId.create(channel=ch2, content_id="vid2", channel_id=ChannelId("UC_id2"))
        assert sid2.value == "UC_id2:vid2"

        # Channel without id, channel_id=None -> fallback to channel.name
        ch3 = Channel(name="Name3", id=None)
        sid3 = PipelineSessionId.create(channel=ch3, content_id="vid3", channel_id=None)
        assert sid3.value == "Name3:vid3"

        # channel as ChannelName
        sid4 = PipelineSessionId.create(channel=ChannelName("Name4"), content_id="vid4")
        assert sid4.value == "Name4:vid4"

        # channel as ChannelName with explicit channel_id
        sid5 = PipelineSessionId.create(
            channel=ChannelName("Name5"), content_id="vid5", channel_id=ChannelId("UC_id5")
        )
        assert sid5.value == "UC_id5:vid5"

        # channel as raw string with whitespace
        sid6 = PipelineSessionId.create(channel="  RawChannel  ", content_id="vid6")
        assert sid6.value == "RawChannel:vid6"

        # content_id as Content VO
        cnt7 = Content(id=ContentId("vid7"), title="Title7")
        sid7 = PipelineSessionId.create(channel="Chan7", content_id=cnt7)
        assert sid7.value == "Chan7:vid7"

        # content_id as ContentId VO
        sid8 = PipelineSessionId.create(channel="Chan8", content_id=ContentId("vid8"))
        assert sid8.value == "Chan8:vid8"

        # content_id as raw string with whitespace
        sid9 = PipelineSessionId.create(channel="Chan9", content_id="  vid9  ")
        assert sid9.value == "Chan9:vid9"


class TestUserIdentity:
    """ADR-027 & SPEC-010: UserIdentity taxonomy for IAM, CLI, and Workers."""

    def test_worker_identity(self) -> None:
        """Worker identity generates system:worker with provider system."""
        user = UserIdentity.worker()
        assert user.value == "system:worker"
        assert user.is_anonymous is False
        assert user.provider == "system"
        assert user.subject == "worker"

    def test_worker_identity_custom_name(self) -> None:
        """Worker identity accepts custom worker identifier."""
        user = UserIdentity.worker(name="channel_sync")
        assert user.value == "system:channel_sync"
        assert user.is_anonymous is False
        assert user.provider == "system"
        assert user.subject == "channel_sync"

    def test_worker_identity_whitespace_fallback(self) -> None:
        u1 = UserIdentity.worker(name="")
        assert u1.value == "system:worker"
        assert u1.subject == "worker"
        u2 = UserIdentity.worker(name="   ")
        assert u2.value == "system:worker"
        assert u2.subject == "worker"
        u3 = UserIdentity.worker(name="  cron_daemon  ")
        assert u3.value == "system:cron_daemon"
        assert u3.subject == "cron_daemon"

    def test_identified_iam_user(self) -> None:
        """Identified IAM user generates user:iam:{username}."""
        user = UserIdentity.identified(subject="alice", provider="iam")
        assert user.value == "user:iam:alice"
        assert user.is_anonymous is False
        assert user.provider == "iam"
        assert user.subject == "alice"

    def test_identified_defaults_and_normalization(self) -> None:
        import inspect

        assert inspect.signature(UserIdentity.identified).parameters["provider"].default is None


        u1 = UserIdentity.identified(subject="bob")
        assert u1.value == "user:oauth:bob"
        assert u1.is_anonymous is False
        assert u1.provider == "oauth"
        assert u1.subject == "bob"


        u2 = UserIdentity.identified(subject="carol", provider="   ")
        assert u2.value == "user:oauth:carol"
        assert u2.provider == "oauth"
        assert u2.subject == "carol"

        u3 = UserIdentity.identified(subject="  dave  ", provider="  OAuth  ")
        assert u3.value == "user:oauth:dave"
        assert u3.is_anonymous is False
        assert u3.provider == "oauth"
        assert u3.subject == "dave"

    def test_identified_empty_subject_raises_error(self) -> None:
        with pytest.raises(
            ValueError, match="^Identified UserIdentity requires a non-empty subject\\.$"
        ):
            UserIdentity.identified(subject="")
        with pytest.raises(
            ValueError, match="^Identified UserIdentity requires a non-empty subject\\.$"
        ):
            UserIdentity.identified(subject="   ", provider="iam")

    def test_anonymous_user(self) -> None:
        """Anonymous user generates anonymous with provider anonymous."""
        user = UserIdentity.anonymous()
        assert user.value == "anonymous"
        assert user.is_anonymous is True
        assert user.provider == "anonymous"
        assert user.subject == ""

    def test_anonymous_user_with_token(self) -> None:
        """Anonymous user with token generates anon:{token}."""
        user = UserIdentity.anonymous(token="guest_123")
        assert user.value == "anon:guest_123"
        assert user.is_anonymous is True
        assert user.provider == "anonymous"
        assert user.subject == ""

        u_empty = UserIdentity.anonymous(token="")
        assert u_empty.value == "anonymous"
        assert u_empty.is_anonymous is True
        assert u_empty.provider == "anonymous"
        assert u_empty.subject == ""

    def test_from_channel(self) -> None:
        with pytest.raises(ValueError, match="^Channel name cannot be empty\\.$"):
            UserIdentity.from_channel(channel="")
        with pytest.raises(ValueError, match="^Channel name cannot be empty\\.$"):
            UserIdentity.from_channel(channel="   ")

        user = UserIdentity.from_channel(channel="  Marcelo Andrade  ")
        assert user.value == "channel:Marcelo Andrade"
        assert user.is_anonymous is True
        assert user.provider == "channel"
        assert user.subject == "Marcelo Andrade"

    def test_empty_user_identity_raises_error(self) -> None:
        with pytest.raises(ValueError, match="^UserIdentity cannot be empty\\.$"):
            UserIdentity(value="")
        with pytest.raises(ValueError, match="^UserIdentity cannot be empty\\.$"):
            UserIdentity(value="   ")


class TestJudgeFrictionMetric:
    """ADR-013 & ADR-016: LLM Judge Friction Metrics."""

    def test_invalid_iterations_raises(self) -> None:
        with pytest.raises(ValueError, match="^iterations must be >= 1$"):
            JudgeFrictionMetric(iterations=0, max_iterations=3, verdict="PASS")
        with pytest.raises(ValueError, match="^iterations must be >= 1$"):
            JudgeFrictionMetric(iterations=-1, max_iterations=3, verdict="PASS")

    def test_invalid_max_iterations_raises(self) -> None:
        with pytest.raises(ValueError, match="^max_iterations must be >= 1$"):
            JudgeFrictionMetric(iterations=1, max_iterations=0, verdict="PASS")
        with pytest.raises(ValueError, match="^max_iterations must be >= 1$"):
            JudgeFrictionMetric(iterations=1, max_iterations=-2, verdict="PASS")

    def test_friction_ratio_boundary_and_calculations(self) -> None:
        m1 = JudgeFrictionMetric(iterations=1, max_iterations=3, verdict="PASS")
        assert m1.friction_ratio == 0.0

        m2 = JudgeFrictionMetric(iterations=1, max_iterations=1, verdict="PASS")
        assert m2.friction_ratio == 0.0

        m3 = JudgeFrictionMetric(iterations=2, max_iterations=3, verdict="PASS")
        assert m3.friction_ratio == 0.5

        m4 = JudgeFrictionMetric(iterations=3, max_iterations=3, verdict="FAIL")
        assert m4.friction_ratio == 1.0

        m5 = JudgeFrictionMetric(iterations=5, max_iterations=3, verdict="FAIL")
        assert m5.friction_ratio == 1.0



class TestChannelCompositeValueObjectAndTenantKey:
    """ADR-032 & ADR-033: Composite Channel VO with Identity VOs and intrinsic tenant_key."""

    def test_channel_composition_with_string_name_and_identity_vo(self) -> None:
        """Channel encapsulates validated string name and strongly-typed ChannelId."""
        from cresmo.domain.value_objects import Channel, ChannelId

        ch = Channel(
            name="Marcelo Andrade",
            id=ChannelId("UCP3CtEXi5nxbhei_aBfIOVA"),
            category="history",
            url="https://www.youtube.com/channel/UCP3CtEXi5nxbhei_aBfIOVA",
        )
        assert ch.name == "Marcelo Andrade"
        assert isinstance(ch.name, str)
        assert isinstance(ch.id, ChannelId)
        assert ch.id.value == "UCP3CtEXi5nxbhei_aBfIOVA"
        assert ch.category == "history"
        assert ch.tenant_key == "channel:UCP3CtEXi5nxbhei_aBfIOVA"

    def test_channel_tenant_key_fallback_to_name_when_id_none(self) -> None:
        """When ChannelId is omitted, tenant_key uses the channel name."""
        from cresmo.domain.value_objects import Channel

        ch = Channel(name="Philosophy Channel")
        assert ch.id is None
        assert ch.tenant_key == "channel:Philosophy Channel"

    def test_channel_name_validation_invariants(self) -> None:
        """Channel enforces ChannelName invariants directly upon construction."""
        from cresmo.domain.value_objects import Channel

        with pytest.raises(DomainValidationError, match="Channel name cannot be empty"):
            Channel(name="")

        with pytest.raises(DomainValidationError, match="path traversal"):
            Channel(name="evil/channel")

        with pytest.raises(DomainValidationError, match="exceeds maximum length"):
            Channel(name="A" * 121)

    def test_channel_tenant_id_class_decommissioned(self) -> None:
        """ChannelTenantId is completely deleted and no longer importable per ADR-033."""
        import cresmo.domain.entities as entities_mod

        assert not hasattr(entities_mod, "ChannelTenantId")
        assert "ChannelTenantId" not in entities_mod.__all__


class TestAdr038PureValueObjectTriadComposition:
    """ADR-038: Pure Value Object Triad Composition and Symmetrical Parity."""

    def test_source_transcript_pure_triad_composition(self) -> None:
        from cresmo.domain.entities import SourceTranscript
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            Content,
            ContentId,
            MediaProvenance,
        )

        channel = Channel(
            id=ChannelId("UCP3CtEXi5nxbhei_aBfIOVA"),
            name="Marcelo Andrade",
            category="history",
            url="https://www.youtube.com/channel/UCP3CtEXi5nxbhei_aBfIOVA",
        )
        provenance = MediaProvenance(
            url="https://youtu.be/9IbNJ0EsTxI",
            description="Video description about Afonso Henriques.",
            publication_date=datetime.date(2026, 1, 15),
        )
        content = Content(
            id=ContentId("9IbNJ0EsTxI"),
            title="AFONSO HENRIQUES: o fundador de Portugal",
            body="Raw spoken audio transcript without edit.",
        )

        source = SourceTranscript(channel=channel, provenance=provenance, content=content)

        # 1. Verification of pure Triad composition (ADR-038)
        assert source.channel is channel
        assert source.provenance is provenance
        assert source.content is content

        # 2. Algorithmic Pair (ID - ID Parity)
        assert source.channel.id is not None
        assert source.channel.id.value == "UCP3CtEXi5nxbhei_aBfIOVA"
        assert source.content.id.value == "9IbNJ0EsTxI"
        assert not hasattr(source.channel, "channel_id")
        assert not hasattr(source.content, "content_id")

        # 3. Cognitive Pair (TXT - TXT Parity)
        assert source.channel.name == "Marcelo Andrade"
        assert source.content.title == "AFONSO HENRIQUES: o fundador de Portugal"
        assert not hasattr(source.channel, "channel_name")
        assert not hasattr(source.content, "content_title")

        # 4. Pure Triad accessors
        assert source.content.body == "Raw spoken audio transcript without edit."
        assert source.provenance.url == "https://youtu.be/9IbNJ0EsTxI"
        assert source.provenance.publication_date == datetime.date(2026, 1, 15)

    def test_fluid_transcript_pure_triad_composition(self) -> None:
        from cresmo.domain.entities import FluidTranscript
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            Content,
            ContentId,
            MediaProvenance,
        )

        channel = Channel(id=ChannelId("UC1234567890"), name="History Channel", category="history")
        provenance = MediaProvenance(url="https://youtube.com/watch?v=abc", description="Desc")
        content = Content(
            id=ContentId("abc"),
            title="Clean Title",
            body="Continuous fluid prose narrative.",
        )

        fluid = FluidTranscript(channel=channel, provenance=provenance, content=content)

        assert fluid.channel is channel
        assert fluid.provenance is provenance
        assert fluid.content is content
        assert fluid.content.body == "Continuous fluid prose narrative."
        assert fluid.content.id == ContentId("abc")
        assert fluid.channel.id == ChannelId("UC1234567890")

    def test_transcript_aggregate_lifecycle_container(self) -> None:
        from cresmo.domain.entities import FluidTranscript, SourceTranscript, Transcript
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            Content,
            ContentId,
            MediaProvenance,
        )

        ch = Channel(id=ChannelId("UCtest123456"), name="Test Channel")
        prov = MediaProvenance(url="https://test.url")
        src_content = Content(id=ContentId("vid_01"), title="Raw Title", body="Raw body")
        fluid_content = Content(id=ContentId("vid_01"), title="Fluid Title", body="Fluid body")

        source = SourceTranscript(channel=ch, provenance=prov, content=src_content)
        fluid = FluidTranscript(channel=ch, provenance=prov, content=fluid_content)

        aggregate = Transcript(source=source, fluid=fluid)
        assert aggregate.source is source
        assert aggregate.fluid is fluid
        assert aggregate.channel == ch
        assert aggregate.provenance == prov
        assert aggregate.content == fluid_content

    def test_post_process_fluid_transcript_preserves_pure_triad(self) -> None:
        from cresmo.domain.entities import (
            CandidateText,
            SourceTranscript,
            post_process_fluid_transcript,
        )
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            Content,
            ContentId,
            MediaProvenance,
        )

        ch = Channel(id=ChannelId("UCtest123456"), name="Test Channel", category="history")
        prov = MediaProvenance(url="https://source.url", description="Origin desc")
        src_content = Content(id=ContentId("vid_02"), title="Original Title", body="Raw body text")

        source = SourceTranscript(channel=ch, provenance=prov, content=src_content)
        candidate = CandidateText(
            text="# Synthesized H1 Title\n\nFluid prose without orality noise.",
            stage_name="fluid_prose",
        )

        fluid = post_process_fluid_transcript(candidate, source)

        # Retains the exact Channel and Provenance Value Objects from source
        assert fluid.channel is source.channel
        assert fluid.provenance is source.provenance
        # Transforms Content with extracted title and body
        assert fluid.content.id == source.content.id
        assert fluid.content.title == "Synthesized H1 Title"
        assert fluid.content.body == "Fluid prose without orality noise."

    def test_symmetrical_parity_channel_content(self) -> None:
        """ADR-038: Algorithmic Parity (channel_id - content_id) and Cognitive Parity (channel_name - content_title)."""
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.domain.entities import (
            FluidTranscript,
            PipelineSessionId,
            SourceTranscript,
            Transcript,
            UserIdentity,
        )
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            ChannelName,
            Content,
            ContentId,
            MediaProvenance,
        )

        ch = Channel(
            channel_name="Marcelo Andrade",
            channel_id="UCxyz1234567890ab",
            category="history",
        )
        assert ch.name == "Marcelo Andrade"
        assert ch.id == ChannelId("UCxyz1234567890ab")
        assert not hasattr(ch, "channel_id")
        assert not hasattr(ch, "channel_name")

        content = Content(
            content_id="9IbNJ0EsTxI",
            content_title="A Gênese Estrutural do Condado Portucalense",
            body="Prosa contínua e densa.",
        )
        assert content.id == ContentId("9IbNJ0EsTxI")
        assert content.title == "A Gênese Estrutural do Condado Portucalense"
        assert not hasattr(content, "content_id")
        assert not hasattr(content, "content_title")

        prov = MediaProvenance(url="https://youtube.com/watch?v=9IbNJ0EsTxI")

        src = SourceTranscript(channel=ch, provenance=prov, content=content)
        # Check SourceTranscript parity via Value Objects
        assert src.channel.id == ChannelId("UCxyz1234567890ab")
        assert src.content.id == ContentId("9IbNJ0EsTxI")
        assert src.channel.name == "Marcelo Andrade"
        assert src.content.title == "A Gênese Estrutural do Condado Portucalense"

        fluid = FluidTranscript(channel=ch, provenance=prov, content=content)
        # Check FluidTranscript parity via Value Objects
        assert fluid.channel.id == ChannelId("UCxyz1234567890ab")
        assert fluid.content.id == ContentId("9IbNJ0EsTxI")
        assert fluid.channel.name == "Marcelo Andrade"
        assert fluid.content.title == "A Gênese Estrutural do Condado Portucalense"

        root_tx = Transcript(source=src, fluid=fluid)
        # Check Transcript root aggregate parity via Value Objects
        assert root_tx.channel is not None and root_tx.channel.id == ChannelId(
            "UCxyz1234567890ab"
        )
        assert root_tx.content is not None and root_tx.content.id == ContentId(
            "9IbNJ0EsTxI"
        )
        assert root_tx.channel is not None and root_tx.channel.name == "Marcelo Andrade"
        assert (
            root_tx.content is not None
            and root_tx.content.title == "A Gênese Estrutural do Condado Portucalense"
        )

        # Check PipelineExecutionContext parity
        sid = PipelineSessionId.create(channel=ch, content_id=content)
        ctx = PipelineExecutionContext(
            session_id=sid,
            user_identity=UserIdentity.anonymous(),
            channel=ch,
            content=content,
        )
        assert ctx.channel.id == ChannelId("UCxyz1234567890ab")
        assert ctx.content.id == ContentId("9IbNJ0EsTxI")
        assert ctx.channel.name == "Marcelo Andrade"
        assert ctx.content.title == "A Gênese Estrutural do Condado Portucalense"


class TestSourceTranscriptInvariantsAndEdgeCases:
    """Rigorous invariant and boundary tests for SourceTranscript aggregate."""

    def test_init_defaults_when_minimal_args_passed(self) -> None:
        st = SourceTranscript(channel_name="Minimal Channel", body="Spoken prose.")
        assert st.content.title == ""
        assert st.provenance.url == ""
        assert st.channel.category == ""
        assert st.provenance.description == ""
        assert st.provenance.publication_date is None
        assert st.metadata == {}
        assert st.channel.id is None

    def test_init_content_id_fallback_to_unknown(self) -> None:
        st1 = SourceTranscript(channel_name="Channel A", body="Spoken prose.", content_id=None)
        assert st1.content.id == ContentId("unknown")
        assert st1.content.id.value == "unknown"

        st2 = SourceTranscript(channel_name="Channel B", body="Spoken prose.")
        assert st2.content.id == ContentId("unknown")
        assert st2.content.id.value == "unknown"

    def test_init_channel_name_empty_or_none_raises_error(self) -> None:
        with pytest.raises(DomainValidationError, match="Channel name cannot be empty"):
            SourceTranscript(channel_name=None, body="Spoken prose.")
        with pytest.raises(DomainValidationError, match="Channel name cannot be empty"):
            SourceTranscript(channel_name="", body="Spoken prose.")

    def test_init_publication_and_upload_date_resolution(self) -> None:
        pub = datetime.date(2023, 1, 1)
        upl = datetime.date(2022, 1, 1)
        st_both = SourceTranscript(channel_name="C", body="B", publication_date=pub, upload_date=upl)
        assert st_both.provenance.publication_date == pub

        st_upl = SourceTranscript(channel_name="C", body="B", publication_date=None, upload_date=upl)
        assert st_upl.provenance.publication_date == upl

        st_none = SourceTranscript(channel_name="C", body="B", publication_date=None, upload_date=None)
        assert st_none.provenance.publication_date is None

    def test_init_all_primitive_args(self) -> None:
        pub = datetime.date(2024, 1, 15)
        st = SourceTranscript(
            channel_name="My Channel",
            channel_id=ChannelId("UC_prim_1"),
            channel_category="Education",
            source_url="https://youtu.be/prim123",
            video_description="Comprehensive explanation of primitives.",
            publication_date=pub,
            content_id="prim123",
            title="Primitive Invariants",
            body="Spoken audio verbatim text.",
            metadata={"custom": "meta"},
        )
        assert st.channel.name == "My Channel"
        assert st.channel.id == ChannelId("UC_prim_1")
        assert st.channel.category == "Education"
        assert st.provenance.url == "https://youtu.be/prim123"
        assert st.provenance.description == "Comprehensive explanation of primitives."
        assert st.provenance.publication_date == pub
        assert st.content.id == ContentId("prim123")
        assert st.content.title == "Primitive Invariants"
        assert st.content.body == "Spoken audio verbatim text."
        assert st.metadata == {"custom": "meta"}

    def test_init_body_validation_exact_error_message(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^SourceTranscript body cannot be empty or whitespace\.$",
        ):
            SourceTranscript(channel_name="C", body="")
        with pytest.raises(
            DomainValidationError,
            match=r"^SourceTranscript body cannot be empty or whitespace\.$",
        ):
            SourceTranscript(channel_name="C", body="   \n\t  ")
        with pytest.raises(
            DomainValidationError,
            match=r"^SourceTranscript body cannot be empty or whitespace\.$",
        ):
            SourceTranscript(channel_name="C", body=None)

    def test_init_metadata_handling(self) -> None:
        st_none = SourceTranscript(channel_name="C", body="B", metadata=None)
        assert st_none.metadata == {}
        st_dict = SourceTranscript(channel_name="C", body="B", metadata={"key": "val"})
        assert st_dict.metadata == {"key": "val"}

    def test_create_factory_all_args(self) -> None:
        pub = datetime.date(2024, 6, 1)
        st = SourceTranscript.create(
            channel_name="Full Channel",
            channel_id="UCfull123",
            channel_category="Technology",
            source_url="https://youtube.com/watch?v=full123",
            publication_date=pub,
            video_description="Deep technical analysis.",
            content_id="full123",
            title="Architecture Mastery",
            body="Verbatim transcript content.",
            metadata={"source": "api", "version": 1},
        )
        assert st.channel.name == "Full Channel"
        assert st.channel.id == ChannelId("UCfull123")
        assert st.channel.category == "Technology"
        assert st.provenance.url == "https://youtube.com/watch?v=full123"
        assert st.provenance.description == "Deep technical analysis."
        assert st.provenance.publication_date == pub
        assert st.content.id == ContentId("full123")
        assert st.content.title == "Architecture Mastery"
        assert st.content.body == "Verbatim transcript content."
        assert st.metadata == {"source": "api", "version": 1}

    def test_create_factory_defaults(self) -> None:
        st = SourceTranscript.create(
            channel_name="Default Channel",
            content_id="def123",
            body="Verbatim content.",
        )
        assert st.channel.name == "Default Channel"
        assert st.channel.id is None
        assert st.channel.category == ""
        assert st.provenance.url == ""
        assert st.provenance.description == ""
        assert st.provenance.publication_date is None
        assert st.content.id == ContentId("def123")
        assert st.content.title == ""
        assert st.content.body == "Verbatim content."
        assert st.metadata == {}

    def test_create_factory_metadata_none(self) -> None:
        st = SourceTranscript.create(
            channel_name="Default Channel",
            content_id="def123",
            body="Verbatim content.",
            metadata=None,
        )
        assert st.metadata == {}


class TestFluidTranscriptInvariantsAndEdgeCases:
    """Rigorous invariant and boundary tests for FluidTranscript aggregate."""

    def test_init_defaults_when_minimal_args_passed(self) -> None:
        ft = FluidTranscript(channel_name="Clean Channel", body="Fluid prose content.")
        assert ft.content.title == ""
        assert ft.provenance.url == ""
        assert ft.channel.category == ""
        assert ft.provenance.description == ""
        assert ft.provenance.publication_date is None
        assert ft.metadata == {}
        assert ft.channel.id is None

    def test_init_with_value_objects(self) -> None:
        ch = Channel(name="VO Channel", id=ChannelId("UC_vo"), category="art")
        prov = MediaProvenance.create(url="https://url", description="desc", publication_date="2024-01-01")
        cnt = Content(id=ContentId("vo_id"), title="VO Title", body="Clean prose.")
        ft = FluidTranscript(channel=ch, provenance=prov, content=cnt, metadata={"a": 1})
        assert ft.channel is ch
        assert ft.provenance is prov
        assert ft.content is cnt
        assert ft.metadata == {"a": 1}

    def test_init_content_id_fallback_to_unknown(self) -> None:
        ft1 = FluidTranscript(channel_name="Channel A", body="Fluid prose.", content_id=None)
        assert ft1.content.id == ContentId("unknown")
        assert ft1.content.id.value == "unknown"

        ft2 = FluidTranscript(channel_name="Channel B", body="Fluid prose.")
        assert ft2.content.id == ContentId("unknown")
        assert ft2.content.id.value == "unknown"

    def test_init_channel_name_empty_or_none_raises_error(self) -> None:
        with pytest.raises(DomainValidationError, match="Channel name cannot be empty"):
            FluidTranscript(channel_name=None, body="Fluid prose.")
        with pytest.raises(DomainValidationError, match="Channel name cannot be empty"):
            FluidTranscript(channel_name="", body="Fluid prose.")

    def test_init_publication_and_upload_date_resolution(self) -> None:
        pub = datetime.date(2023, 1, 1)
        upl = datetime.date(2022, 1, 1)
        ft_both = FluidTranscript(channel_name="C", body="B", publication_date=pub, upload_date=upl)
        assert ft_both.provenance.publication_date == pub

        ft_upl = FluidTranscript(channel_name="C", body="B", publication_date=None, upload_date=upl)
        assert ft_upl.provenance.publication_date == upl

        ft_none = FluidTranscript(channel_name="C", body="B", publication_date=None, upload_date=None)
        assert ft_none.provenance.publication_date is None

    def test_init_all_primitive_args(self) -> None:
        pub = datetime.date(2024, 1, 15)
        ft = FluidTranscript(
            channel_name="My Fluid Channel",
            channel_id=ChannelId("UC_fluid_prim"),
            channel_category="Science",
            source_url="https://youtu.be/fluidprim",
            video_description="Comprehensive fluid description.",
            publication_date=pub,
            content_id="fluidprim123",
            title="Fluid Primitive Invariants",
            body="Continuous narrative without orality.",
            metadata={"custom": "fluid_meta"},
        )
        assert ft.channel.name == "My Fluid Channel"
        assert ft.channel.id == ChannelId("UC_fluid_prim")
        assert ft.channel.category == "Science"
        assert ft.provenance.url == "https://youtu.be/fluidprim"
        assert ft.provenance.description == "Comprehensive fluid description."
        assert ft.provenance.publication_date == pub
        assert ft.content.id == ContentId("fluidprim123")
        assert ft.content.title == "Fluid Primitive Invariants"
        assert ft.content.body == "Continuous narrative without orality."
        assert ft.metadata == {"custom": "fluid_meta"}

    def test_init_body_validation_exact_error_message(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^FluidTranscript body cannot be empty or whitespace\.$",
        ):
            FluidTranscript(channel_name="C", body="")
        with pytest.raises(
            DomainValidationError,
            match=r"^FluidTranscript body cannot be empty or whitespace\.$",
        ):
            FluidTranscript(channel_name="C", body="   \n\t  ")
        with pytest.raises(
            DomainValidationError,
            match=r"^FluidTranscript body cannot be empty or whitespace\.$",
        ):
            FluidTranscript(channel_name="C", body=None)

    def test_init_rejects_markdown_tables(self) -> None:
        table_start = "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |"
        with pytest.raises(
            CompendiumStructureError,
            match=r"^FluidTranscript body must be continuous prose and cannot contain Markdown tables\.$",
        ):
            FluidTranscript(channel_name="C", body=table_start)

        table_middle = "Leading paragraph text.\n\n| Header 1 | Header 2 |\n| :--- | ---: |\n| Val 1 | Val 2 |"
        with pytest.raises(
            CompendiumStructureError,
            match=r"^FluidTranscript body must be continuous prose and cannot contain Markdown tables\.$",
        ):
            FluidTranscript(channel_name="C", body=table_middle)

    def test_init_metadata_handling(self) -> None:
        ft_none = FluidTranscript(channel_name="C", body="B", metadata=None)
        assert ft_none.metadata == {}
        ft_dict = FluidTranscript(channel_name="C", body="B", metadata={"key": "val"})
        assert ft_dict.metadata == {"key": "val"}

    def test_create_factory_all_args(self) -> None:
        pub = datetime.date(2024, 7, 1)
        ft = FluidTranscript.create(
            channel_name="Full Channel",
            channel_id="UCfluid123",
            channel_category="Science",
            source_url="https://youtube.com/watch?v=fluid123",
            publication_date=pub,
            video_description="Fluid synthesis explanation.",
            content_id="fluid123",
            title="Fluid Dynamics",
            body="Continuous fluid narrative prose.",
            metadata={"step": 2, "quality": "high"},
        )
        assert ft.channel.name == "Full Channel"
        assert ft.channel.id == ChannelId("UCfluid123")
        assert ft.channel.category == "Science"
        assert ft.provenance.url == "https://youtube.com/watch?v=fluid123"
        assert ft.provenance.description == "Fluid synthesis explanation."
        assert ft.provenance.publication_date == pub
        assert ft.content.id == ContentId("fluid123")
        assert ft.content.title == "Fluid Dynamics"
        assert ft.content.body == "Continuous fluid narrative prose."
        assert ft.metadata == {"step": 2, "quality": "high"}

    def test_create_factory_defaults(self) -> None:
        ft = FluidTranscript.create(
            channel_name="Default Channel",
            content_id="def456",
            body="Continuous prose without tables.",
        )
        assert ft.channel.name == "Default Channel"
        assert ft.channel.id is None
        assert ft.channel.category == ""
        assert ft.provenance.url == ""
        assert ft.provenance.description == ""
        assert ft.provenance.publication_date is None
        assert ft.content.id == ContentId("def456")
        assert ft.content.title == ""
        assert ft.content.body == "Continuous prose without tables."
        assert ft.metadata == {}

    def test_create_factory_metadata_none(self) -> None:
        ft = FluidTranscript.create(
            channel_name="Default Channel",
            content_id="def456",
            body="Continuous prose.",
            metadata=None,
        )
        assert ft.metadata == {}


class TestTranscriptAggregateProperties:
    """Rigorous invariant tests for Transcript aggregate properties."""

    def test_empty_container(self) -> None:
        t = Transcript(source=None, fluid=None)
        assert t.source is None
        assert t.fluid is None
        assert t.channel is None
        assert t.provenance is None
        assert t.content is None

    def test_source_only(self) -> None:
        st = SourceTranscript(channel_name="SrcChan", body="Raw body")
        t = Transcript(source=st, fluid=None)
        assert t.source is st
        assert t.fluid is None
        assert t.channel is st.channel
        assert t.provenance is st.provenance
        assert t.content is st.content

    def test_fluid_only(self) -> None:
        ft = FluidTranscript(channel_name="FluidChan", body="Fluid body")
        t = Transcript(source=None, fluid=ft)
        assert t.source is None
        assert t.fluid is ft
        assert t.channel is ft.channel
        assert t.provenance is ft.provenance
        assert t.content is ft.content

    def test_fluid_precedence_over_source(self) -> None:
        st = SourceTranscript(channel_name="SrcChan", body="Raw body")
        ft = FluidTranscript(channel_name="FluidChan", body="Fluid body")
        t = Transcript(source=st, fluid=ft)
        assert t.source is st
        assert t.fluid is ft
        assert t.channel is ft.channel
        assert t.channel is not st.channel
        assert t.provenance is ft.provenance
        assert t.provenance is not st.provenance
        assert t.content is ft.content
        assert t.content is not st.content


class TestPostProcessFluidTranscriptInvariantsAndRegex:
    """Rigorous invariant and regex matching tests for post_process_fluid_transcript."""

    def test_candidate_as_candidatetext_and_raw_str(self) -> None:
        st = SourceTranscript(channel_name="Chan", content_id="c1", title="Default Title", body="Raw")

        res1 = post_process_fluid_transcript("   Prose body text.   ", st)
        assert res1.content.body == "Prose body text."
        assert res1.content.title == "Default Title"

        cand = CandidateText(text="   Prose body text.   ", stage_name="s1")
        res2 = post_process_fluid_transcript(cand, st)
        assert res2.content.body == "Prose body text."
        assert res2.content.title == "Default Title"

    def test_title_h1_extraction_and_stripping(self) -> None:
        st = SourceTranscript(channel_name="Chan", content_id="c1", title="Old Title", body="Raw")
        text = "# Primary Extracted Heading\n\nThis is the remaining narrative body."
        res = post_process_fluid_transcript(text, st)
        assert res.content.title == "Primary Extracted Heading"
        assert res.content.body == "This is the remaining narrative body."

        text_spaced = "   #    Spaced Heading   \n\nBody text after."
        res_sp = post_process_fluid_transcript(text_spaced, st)
        assert res_sp.content.title == "Spaced Heading"
        assert res_sp.content.body == "Body text after."

    def test_fallback_titles_when_h1_missing(self) -> None:
        st_with_title = SourceTranscript(channel_name="Chan", content_id="c1", title="Original Title", body="Raw")
        res1 = post_process_fluid_transcript("Body without H1 header.", st_with_title)
        assert res1.content.title == "Original Title"

        st_no_title = SourceTranscript(channel_name="Chan", content_id="c1", title="", body="Raw")
        res2 = post_process_fluid_transcript("Body without H1 header.", st_no_title)
        assert res2.content.title == "Untitled Compendium"

    def test_complementary_sections_stripping(self) -> None:
        st = SourceTranscript(channel_name="Chan", content_id="c1", body="Raw")
        base = "Main core prose narrative that must be preserved."

        res1 = post_process_fluid_transcript(f"{base}\n\n## Informações Complementares\nDetails to drop.", st)
        assert res1.content.body == base

        res2 = post_process_fluid_transcript(f"{base}\n\n### Notas Complementares\nNotes to drop.", st)
        assert res2.content.body == base

        res3 = post_process_fluid_transcript(f"{base}\n\n## Informações Adicionais\nMore to drop.", st)
        assert res3.content.body == base

        res4 = post_process_fluid_transcript(f"{base}\n\n## **Informações Complementares**\nBold to drop.", st)
        assert res4.content.body == base

        res5 = post_process_fluid_transcript(f"{base}\n\n## informações complementares\nCase to drop.", st)
        assert res5.content.body == base

    def test_empty_body_raises_compendium_structure_error(self) -> None:
        st = SourceTranscript(channel_name="Chan", content_id="c_err_1", body="Raw")

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("# Only A Header\n", st)

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("# Header\n\n## Informações Complementares\nExtra notes.", st)

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("   \n   ", st)

    def test_preserves_pure_triad_and_content_id(self) -> None:
        ch = Channel(name="Preserved Channel", id=ChannelId("UC_preserve"))
        prov = MediaProvenance.create(url="https://url", description="desc")
        cnt = Content(id=ContentId("preserve_cid"), title="Orig", body="Body")
        st = SourceTranscript(channel=ch, provenance=prov, content=cnt)

        res = post_process_fluid_transcript("Processed prose body.", st)
        assert res.channel is ch
        assert res.provenance is prov
        assert res.content.id == ContentId("preserve_cid")
        assert res.content.id.value == "preserve_cid"
        assert res.content.body == "Processed prose body."
