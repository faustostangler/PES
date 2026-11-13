"""Unit tests for Cresmo Domain Entities and Aggregates.

Derived from SPEC-001 Section 2.2 & Section 5.
Verifies construction invariants, always-valid state, and exception mapping.
"""

import datetime

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    JudgeFrictionMetric,
    MapOfContent,
    PipelineSessionId,
    StageTranscript,
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


class TestChannelUrlAndContentCreation:
    """Tests for Channel URL fallback and Content URL extraction factory."""

    def test_channel_url_dynamic_fallback(self) -> None:
        ch1 = Channel(name="MyChannel", id=ChannelId("UC_auto_url_1"))
        assert ch1.url == "https://www.youtube.com/channel/UC_auto_url_1"

        ch2 = Channel(
            name="MyChannel", id=ChannelId("UC_auto_url_1"), url="https://youtube.com/@custom"
        )
        assert ch2.url == "https://youtube.com/@custom"

        ch3 = Channel(
            name="MyChannel",
            id=ChannelId("UC_auto_url_1"),
            url="https://www.youtube.com/channel/UC_auto_url_1",
        )
        assert ch3.url == "https://www.youtube.com/channel/UC_auto_url_1"

        ch4 = Channel(name="MyChannel")
        assert ch4.url == "https://www.youtube.com/@MyChannel"

    def test_content_create_with_inferred_id_from_url(self) -> None:
        cnt = Content.create(
            url="https://youtube.com/watch?v=extracted_abc", title="Title", text="Body"
        )
        assert cnt.id == ContentId("extracted_abc")


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
            StageTranscript(content_id=cid, channel_name=ChannelName("   "), text="Valid body.")


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
        sid2 = PipelineSessionId.create(
            channel=ch2, content_id="vid2", channel_id=ChannelId("UC_id2")
        )
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
        from cresmo.domain.entities import StageTranscript
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
            text="Raw spoken audio transcript without edit.",
        )

        source = StageTranscript(channel=channel, provenance=provenance, content=content)

        # 1. Verification of pure Triad composition (ADR-038)
        assert source.channel is channel
        assert source.provenance is provenance
        assert source.content.id == content.id
        assert source.content.title == content.title
        assert source.content.text == content.text
        assert source.content.session_id == "UCP3CtEXi5nxbhei_aBfIOVA:9IbNJ0EsTxI"

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
        assert source.content.text == "Raw spoken audio transcript without edit."
        assert source.provenance.url == "https://youtu.be/9IbNJ0EsTxI"
        assert source.provenance.publication_date == datetime.date(2026, 1, 15)

    def test_fluid_transcript_pure_triad_composition(self) -> None:
        from cresmo.domain.entities import StageTranscript
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
            text="Continuous fluid prose narrative.",
        )

        fluid = StageTranscript(channel=channel, provenance=provenance, content=content)

        assert fluid.channel is channel
        assert fluid.provenance is provenance
        assert fluid.content.id == content.id
        assert fluid.content.title == content.title
        assert fluid.content.text == content.text
        assert fluid.content.session_id == "UC1234567890:abc"
        assert fluid.content.text == "Continuous fluid prose narrative."
        assert fluid.content.id == ContentId("abc")
        assert fluid.channel.id == ChannelId("UC1234567890")

    def test_post_process_fluid_transcript_preserves_pure_triad(self) -> None:
        from cresmo.domain.entities import (
            CandidateText,
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
        src_content = Content(id=ContentId("vid_02"), title="Original Title", text="Raw body text")

        source = StageTranscript(channel=ch, provenance=prov, content=src_content)
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
        assert fluid.content.text == "Fluid prose without orality noise."

    def test_symmetrical_parity_channel_content(self) -> None:
        """ADR-038: Algorithmic Parity (channel_id - content_id) and Cognitive Parity (channel_name - content_title)."""
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.domain.entities import (
            PipelineSessionId,
            UserIdentity,
        )
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            Content,
            ContentId,
            MediaProvenance,
        )

        ch = Channel(
            name="Marcelo Andrade",
            id=ChannelId("UCxyz1234567890ab"),
            category="history",
        )
        assert ch.name == "Marcelo Andrade"
        assert ch.id == ChannelId("UCxyz1234567890ab")
        assert not hasattr(ch, "channel_id")
        assert not hasattr(ch, "channel_name")

        content = Content(
            id=ContentId("9IbNJ0EsTxI"),
            title="A Gênese Estrutural do Condado Portucalense",
            text="Prosa contínua e densa.",
        )
        assert content.id == ContentId("9IbNJ0EsTxI")
        assert content.title == "A Gênese Estrutural do Condado Portucalense"
        assert not hasattr(content, "content_id")
        assert not hasattr(content, "content_title")

        prov = MediaProvenance(url="https://youtube.com/watch?v=9IbNJ0EsTxI")

        src = StageTranscript(channel=ch, provenance=prov, content=content)
        # Check StageTranscript parity via Value Objects
        assert src.channel.id == ChannelId("UCxyz1234567890ab")
        assert src.content.id == ContentId("9IbNJ0EsTxI")
        assert src.channel.name == "Marcelo Andrade"
        assert src.content.title == "A Gênese Estrutural do Condado Portucalense"

        fluid = StageTranscript(channel=ch, provenance=prov, content=content)
        # Check StageTranscript parity via Value Objects
        assert fluid.channel.id == ChannelId("UCxyz1234567890ab")
        assert fluid.content.id == ContentId("9IbNJ0EsTxI")
        assert fluid.channel.name == "Marcelo Andrade"
        assert fluid.content.title == "A Gênese Estrutural do Condado Portucalense"

        # Check PipelineExecutionContext parity
        sid = PipelineSessionId.create(channel=ch, content_id=content)
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.anonymous(),
            channel=ch,
            content=Content(
                id=content.id, title=content.title, text=content.text, session_id=sid.value
            ),
        )
        assert ctx.channel.id == ChannelId("UCxyz1234567890ab")
        assert ctx.content.id == ContentId("9IbNJ0EsTxI")
        assert ctx.channel.name == "Marcelo Andrade"
        assert ctx.content.title == "A Gênese Estrutural do Condado Portucalense"
        assert ctx.content.session_id == sid.value


class TestPostProcessFluidTranscriptInvariantsAndRegex:
    """Rigorous invariant and regex matching tests for post_process_fluid_transcript."""

    @staticmethod
    def _make_source(cid: str = "c1", title: str = "Default Title") -> StageTranscript:
        return StageTranscript(
            channel=Channel(name="Chan"),
            provenance=MediaProvenance.create(url=f"https://youtube.com/watch?v={cid}"),
            content=Content(id=ContentId(cid), title=title, text="Raw"),
        )

    def test_candidate_as_candidatetext_and_raw_str(self) -> None:
        st = self._make_source("c1", "Default Title")

        res1 = post_process_fluid_transcript("   Prose body text.   ", st)
        assert res1.content.text == "Prose body text."
        assert res1.content.title == "Default Title"

        cand = CandidateText(text="   Prose body text.   ", stage_name="s1")
        res2 = post_process_fluid_transcript(cand, st)
        assert res2.content.text == "Prose body text."
        assert res2.content.title == "Default Title"

    def test_title_h1_extraction_and_stripping(self) -> None:
        st = self._make_source("c1", "Old Title")
        text = "# Primary Extracted Heading\n\nThis is the remaining narrative body."
        res = post_process_fluid_transcript(text, st)
        assert res.content.title == "Primary Extracted Heading"
        assert res.content.text == "This is the remaining narrative body."

        text_spaced = "   #    Spaced Heading   \n\nBody text after."
        res_sp = post_process_fluid_transcript(text_spaced, st)
        assert res_sp.content.title == "Spaced Heading"
        assert res_sp.content.text == "Body text after."

    def test_fallback_titles_when_h1_missing(self) -> None:
        st_with_title = self._make_source("c1", "Original Title")
        res1 = post_process_fluid_transcript("Body without H1 header.", st_with_title)
        assert res1.content.title == "Original Title"

        st_no_title = self._make_source("c1", "")
        res2 = post_process_fluid_transcript("Body without H1 header.", st_no_title)
        assert res2.content.title == "Untitled Compendium"

    def test_complementary_sections_stripping(self) -> None:
        st = self._make_source("c1", "Default Title")
        base = "Main core prose narrative that must be preserved."

        res1 = post_process_fluid_transcript(f"{base}\n\n### Extra Info\nDetails to drop.", st)
        assert res1.content.text == base

        res2 = post_process_fluid_transcript(
            f"{base}\n\n### Notas Complementares\nNotes to drop.", st
        )
        assert res2.content.text == base

        res3 = post_process_fluid_transcript(
            f"{base}\n\n## Informações Adicionais\nMore to drop.", st
        )
        assert res3.content.text == base

        res4 = post_process_fluid_transcript(f"{base}\n\n## **Extra Info**\nBold to drop.", st)
        assert res4.content.text == base

        res5 = post_process_fluid_transcript(
            f"{base}\n\n## informações complementares\nCase to drop.", st
        )
        assert res5.content.text == base

    def test_empty_body_raises_compendium_structure_error(self) -> None:
        st = self._make_source("c_err_1", "Default Title")

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("# Only A Header\n", st)

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("# Header\n\n### Extra Info\nExtra notes.", st)

        with pytest.raises(
            CompendiumStructureError,
            match=r"^Generated fluid prose body is empty for 'c_err_1'\.$",
        ):
            post_process_fluid_transcript("   \n   ", st)

    def test_preserves_pure_triad_and_content_id(self) -> None:
        ch = Channel(name="Preserved Channel", id=ChannelId("UC_preserve"))
        prov = MediaProvenance.create(url="https://url", description="desc")
        cnt = Content(id=ContentId("preserve_cid"), title="Orig", text="Body")
        st = StageTranscript(channel=ch, provenance=prov, content=cnt)

        res = post_process_fluid_transcript("Processed prose body.", st)
        assert res.channel is ch
        assert res.provenance is prov
        assert res.content.id == ContentId("preserve_cid")
        assert res.content.id.value == "preserve_cid"
        assert res.content.text == "Processed prose body."
