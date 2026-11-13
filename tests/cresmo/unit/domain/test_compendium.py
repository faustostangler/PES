"""Unit tests for compendium post-processing domain service."""

from __future__ import annotations

import pytest

from cresmo.domain.entities.transcripts import StageTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.services.compendium import post_process_enriched_compendium
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
)


def _make_source_transcript(
    *,
    title: str = "Source Title",
    session_id: str = "sess_compendium_1",
    metadata: dict[str, object] | None = None,
) -> StageTranscript:
    return StageTranscript(
        channel=Channel(name=ChannelName("Canal Teste"), id=ChannelId("UC_TEST_COMP")),
        provenance=MediaProvenance.create(url="https://youtube.com/watch?v=comp0001"),
        content=Content(
            id=ContentId("comp0001"),
            title=title,
            text="## Raw\n\nOriginal content.",
            session_id=session_id,
        ),
        metadata=metadata if metadata is not None else {"origin": "unit", "wave": 1},
    )


class TestPostProcessEnrichedCompendium:
    """Comprehensive behavioral tests for post_process_enriched_compendium."""

    def test_extracts_h1_title_and_preserves_triad_and_metadata(self) -> None:
        source = _make_source_transcript(
            title="Old Source Title",
            session_id="sess_42",
            metadata={"origin": "unit", "keep": True},
        )
        candidate = CandidateText(
            text=(
                "   # New Extracted Title   \n\n"
                "## Section One\n\n"
                "Dense prose paragraph.\n\n"
                "### Extra Info\n\n"
                "Reference detail."
            ),
            stage_name="gap_filler",
        )

        result = post_process_enriched_compendium(candidate, source)

        assert result.channel == source.channel
        assert result.provenance == source.provenance
        assert result.content.id == ContentId("comp0001")
        assert result.content.title == "New Extracted Title"
        assert result.content.session_id == "sess_42"
        assert result.content.text == (
            "## Section One\n\nDense prose paragraph.\n\n### Extra Info\n\nReference detail."
        )
        assert result.pass_count == 1
        assert result.metadata == {"origin": "unit", "keep": True}
        assert result.metadata is not source.metadata

    def test_accepts_plain_string_candidate_and_falls_back_to_source_title(self) -> None:
        source = _make_source_transcript(title="Source Fallback Title")
        plain_candidate = (
            "## Section Only\n\nMain narrative content.\n\n### Extra Info\n\nSupplemental note."
        )

        result = post_process_enriched_compendium(plain_candidate, source, pass_count=3)

        assert result.content.title == "Source Fallback Title"
        assert result.content.text == (
            "## Section Only\n\nMain narrative content.\n\n### Extra Info\n\nSupplemental note."
        )
        assert result.pass_count == 3

    def test_falls_back_to_untitled_compendium_and_clamps_non_positive_pass_count(self) -> None:
        source = _make_source_transcript(title="")
        candidate = "## Heading\n\nBody.\n\n### Extra Info\n\nDetails."

        result = post_process_enriched_compendium(candidate, source, pass_count=0)

        assert result.content.title == "Untitled Compendium"
        assert result.pass_count == 1

    def test_raises_exact_error_when_extra_info_section_is_missing(self) -> None:
        source = _make_source_transcript()
        candidate = "## Heading\n\nBody without extra info."

        with pytest.raises(CompendiumStructureError) as exc_info:
            post_process_enriched_compendium(candidate, source)

        assert (
            exc_info.value.args[0]
            == "Missing mandatory complementary information section '### Extra Info'."
        )

    def test_raises_exact_error_when_main_body_is_empty(self) -> None:
        source = _make_source_transcript()
        candidate = "# Title Only\n\n### Extra Info\n\nOrphan extra info."

        with pytest.raises(CompendiumStructureError) as exc_info:
            post_process_enriched_compendium(candidate, source)

        assert exc_info.value.args[0] == "StageTranscript body cannot be empty."

    def test_raises_exact_error_when_extra_info_body_is_empty(self) -> None:
        source = _make_source_transcript()
        candidate = "## Main Section\n\nBody exists.\n\n### Extra Info\n   \n"

        with pytest.raises(CompendiumStructureError) as exc_info:
            post_process_enriched_compendium(candidate, source)

        assert (
            exc_info.value.args[0]
            == "StageTranscript must contain a non-empty 'Extra Info' section."
        )
