"""Unit tests for ADR-057 Monomorphic StageTranscript Envelope and Pure Triad Ingestion.

Tests that:
1. StageTranscript requires pure Triad Value Objects (channel, provenance, content).
2. Loose primitive convenience arguments in __init__ are rejected or non-existent.
3. Tables in markdown are NOT rejected by the domain entity (delegated to LLM / Judge).
4. pass_count is type-validated as positive integer when present.
5. ContentId is validated in its own VO, not cross-coupled with provenance.url mismatch.
"""

import datetime

import pytest

from cresmo.domain.entities import StageTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
)


class TestADR057MonomorphicStageTranscript:
    """Verifies ADR-057 monomorphic envelope and pure triad composition."""

    def test_pure_triad_instantiation(self) -> None:
        """StageTranscript must be constructible with pure Channel, MediaProvenance, and Content."""
        channel = Channel(name=ChannelName("Test Channel"), id=ChannelId("UC123"))
        provenance = MediaProvenance.create(
            url="https://youtube.com/watch?v=abc123xyz00",
            publication_date=datetime.date(2026, 1, 1),
        )
        content = Content(
            id=ContentId("abc123xyz00"),
            title="Clean Title",
            body="Pure prose without loose arguments.\n\n### Extra Info\n\nExtra encyclopedic notes",
            session_id="UC123:abc123xyz00",
        )

        st = StageTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
            metadata={"source": "test"},
            pass_count=2,
        )

        assert st.channel == channel
        assert st.provenance == provenance
        assert st.content == content
        assert st.content.body == "Pure prose without loose arguments.\n\n### Extra Info\n\nExtra encyclopedic notes"
        assert st.content.title == "Clean Title"
        assert st.content.id == ContentId("abc123xyz00")
        assert st.pass_count == 2
        assert not hasattr(st, "body")
        assert not hasattr(st, "title")
        assert not hasattr(st, "content_id")
        assert not hasattr(st, "channel_name")
        assert not hasattr(st, "channel_id")
        assert not hasattr(st, "channel_category")
        assert not hasattr(st, "complementary_info")

    def test_rejection_of_missing_triad_value_objects(self) -> None:
        """StageTranscript must not accept missing channel, provenance or content."""
        with pytest.raises(TypeError):
            # Attempting legacy instantiation without triad VOs
            StageTranscript(channel_name="Loose Name", body="Loose Body")  # type: ignore[call-arg]

    def test_markdown_tables_are_allowed_in_domain_entity(self) -> None:
        """Domain entity does NOT reject markdown tables; syntax checks belong to LLM/Judge."""
        channel = Channel(name="Test Channel")
        provenance = MediaProvenance.create(url="https://example.com")
        content = Content(
            id=ContentId("cid_with_table"),
            title="Table Test",
            body="## Header\n\n| Col 1 | Col 2 |\n| --- | --- |\n| A | B |\n\nProse continues.",
        )

        stage = StageTranscript(channel=channel, provenance=provenance, content=content)
        assert "| Col 1 | Col 2 |" in stage.content.body

        fluid = StageTranscript(channel=channel, provenance=provenance, content=content)
        assert "| Col 1 | Col 2 |" in fluid.content.body

        comp = StageTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
            pass_count=1,
        )
        assert "| Col 1 | Col 2 |" in comp.content.body

    def test_url_mismatch_with_content_id_does_not_raise(self) -> None:
        """ContentId is its own VO; URL divergence in provenance does not fail entity creation."""
        channel = Channel(name="Test Channel")
        provenance = MediaProvenance.create(url="https://youtube.com/watch?v=different_id")
        content = Content(
            id=ContentId("local_file_id"),
            title="Different IDs",
            body="Valid body content.",
        )

        source = StageTranscript(channel=channel, provenance=provenance, content=content)
        assert source.content.id == ContentId("local_file_id")

    def test_pass_count_type_validation(self) -> None:
        """pass_count must be int >= 1 when provided."""
        channel = Channel(name="Test Channel")
        provenance = MediaProvenance.create(url="https://example.com")
        content = Content(id=ContentId("cid1"), title="T", body="Valid body.")

        with pytest.raises(CompendiumStructureError, match="pass_count must be at least 1"):
            StageTranscript(
                channel=channel,
                provenance=provenance,
                content=content,
                pass_count=0,
            )

        with pytest.raises(CompendiumStructureError, match="pass_count must be an integer"):
            StageTranscript(
                channel=channel,
                provenance=provenance,
                content=content,
                pass_count="invalid",  # type: ignore[arg-type]
            )

