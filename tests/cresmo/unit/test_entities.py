"""Unit tests for Cresmo Domain Entities and Aggregates.

Derived from SPEC-001 Section 2.2 & Section 5.
Verifies construction invariants, always-valid state, and exception mapping.
"""

import datetime

import pytest

from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    PipelineSessionId,
    SourceTranscript,
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
        assert transcript.channel.channel_name == ChannelName("Example Channel")
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

    def test_source_transcript_empty_channel_raises_error(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            SourceTranscript(content_id=cid, channel_name=ChannelName("   "), body="Valid body.")

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
        assert source.channel.channel_id == source.channel.id
        assert source.content.content_id == source.content.id

        # 3. Cognitive Pair (TXT - TXT Parity)
        assert source.channel.name == "Marcelo Andrade"
        assert source.content.title == "AFONSO HENRIQUES: o fundador de Portugal"
        assert source.channel.channel_name.value == "Marcelo Andrade"
        assert source.content.content_title == "AFONSO HENRIQUES: o fundador de Portugal"

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
        assert ch.channel_id == ChannelId("UCxyz1234567890ab")
        assert ch.channel_name == ChannelName("Marcelo Andrade")
        assert ch.name == "Marcelo Andrade"
        assert ch.id == ChannelId("UCxyz1234567890ab")

        content = Content(
            content_id="9IbNJ0EsTxI",
            content_title="A Gênese Estrutural do Condado Portucalense",
            body="Prosa contínua e densa.",
        )
        assert content.content_id == ContentId("9IbNJ0EsTxI")
        assert content.content_title == "A Gênese Estrutural do Condado Portucalense"
        assert content.id == ContentId("9IbNJ0EsTxI")
        assert content.title == "A Gênese Estrutural do Condado Portucalense"

        prov = MediaProvenance(url="https://youtube.com/watch?v=9IbNJ0EsTxI")

        src = SourceTranscript(channel=ch, provenance=prov, content=content)
        # Check SourceTranscript parity via Value Objects
        assert src.channel.channel_id == ChannelId("UCxyz1234567890ab")
        assert src.content.content_id == ContentId("9IbNJ0EsTxI")
        assert src.channel.channel_name == ChannelName("Marcelo Andrade")
        assert src.content.content_title == "A Gênese Estrutural do Condado Portucalense"

        fluid = FluidTranscript(channel=ch, provenance=prov, content=content)
        # Check FluidTranscript parity via Value Objects
        assert fluid.channel.channel_id == ChannelId("UCxyz1234567890ab")
        assert fluid.content.content_id == ContentId("9IbNJ0EsTxI")
        assert fluid.channel.channel_name == ChannelName("Marcelo Andrade")
        assert fluid.content.content_title == "A Gênese Estrutural do Condado Portucalense"

        root_tx = Transcript(source=src, fluid=fluid)
        # Check Transcript root aggregate parity via Value Objects
        assert root_tx.channel is not None and root_tx.channel.channel_id == ChannelId(
            "UCxyz1234567890ab"
        )
        assert root_tx.content is not None and root_tx.content.content_id == ContentId(
            "9IbNJ0EsTxI"
        )
        assert root_tx.channel is not None and root_tx.channel.channel_name == ChannelName(
            "Marcelo Andrade"
        )
        assert (
            root_tx.content is not None
            and root_tx.content.content_title == "A Gênese Estrutural do Condado Portucalense"
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
        assert ctx.channel.channel_id == ChannelId("UCxyz1234567890ab")
        assert ctx.content.content_id == ContentId("9IbNJ0EsTxI")
        assert ctx.channel.channel_name == ChannelName("Marcelo Andrade")
        assert ctx.content.content_title == "A Gênese Estrutural do Condado Portucalense"
