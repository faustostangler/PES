"""Unit tests for expanded stage transcript post-processing domain service."""

from __future__ import annotations

import pytest

from cresmo.domain.entities.transcripts import StageTranscript
from cresmo.domain.exceptions import StageTranscriptStructureError
from cresmo.domain.services.stage_post_processor import post_process_expanded_transcript
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
    session_id: str = "sess_expanded_1",
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


class TestPostProcessExpandedTranscript:
    """Comprehensive behavioral tests for post_process_expanded_transcript."""

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

        result = post_process_expanded_transcript(candidate, source)

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

    def test_propagates_passes_executed_from_candidate_metadata(self) -> None:
        source = _make_source_transcript(title="Source Title")
        candidate = CandidateText(
            text="## Section One\n\nDense prose.\n\n### Extra Info\n\n1. Reference detail.",
            stage_name="long_expander",
            metadata={"passes_executed": 4},
        )

        result = post_process_expanded_transcript(candidate, source, pass_count=1)

        assert result.pass_count == 4

    def test_accepts_plain_string_candidate_and_falls_back_to_source_title(self) -> None:
        source = _make_source_transcript(title="Source Fallback Title")
        plain_candidate = (
            "## Section Only\n\nMain narrative content.\n\n### Extra Info\n\nSupplemental note."
        )

        result = post_process_expanded_transcript(plain_candidate, source, pass_count=3)

        assert result.content.title == "Source Fallback Title"
        assert result.content.text == (
            "## Section Only\n\nMain narrative content.\n\n### Extra Info\n\nSupplemental note."
        )
        assert result.pass_count == 3

    def test_falls_back_to_untitled_transcript_and_clamps_non_positive_pass_count(self) -> None:
        source = _make_source_transcript(title="")
        candidate = "## Heading\n\nBody.\n\n### Extra Info\n\nDetails."

        result = post_process_expanded_transcript(candidate, source, pass_count=0)

        assert result.content.title == "Untitled Transcript"
        assert result.pass_count == 1

    def test_raises_exact_error_when_extra_info_section_is_missing(self) -> None:
        source = _make_source_transcript()
        candidate = "## Heading\n\nBody without extra info."

        with pytest.raises(StageTranscriptStructureError) as exc_info:
            post_process_expanded_transcript(candidate, source)

        assert (
            exc_info.value.args[0]
            == "Missing mandatory complementary information section '### Extra Info'."
        )

    def test_raises_exact_error_when_main_body_is_empty(self) -> None:
        source = _make_source_transcript()
        candidate = "# Title Only\n\n### Extra Info\n\nOrphan extra info."

        with pytest.raises(StageTranscriptStructureError) as exc_info:
            post_process_expanded_transcript(candidate, source)

        assert exc_info.value.args[0] == "StageTranscript body cannot be empty."

    def test_raises_exact_error_when_extra_info_body_is_empty(self) -> None:
        source = _make_source_transcript()
        candidate = "## Main Section\n\nBody exists.\n\n### Extra Info\n   \n"

        with pytest.raises(StageTranscriptStructureError) as exc_info:
            post_process_expanded_transcript(candidate, source)

        assert (
            exc_info.value.args[0]
            == "StageTranscript must contain a non-empty 'Extra Info' section."
        )

    @pytest.mark.parametrize(
        ("metadata", "fallback_pass_count", "expected_pass_count"),
        [
            ({"passes_executed": "invalid"}, 3, 3),
            ({"passes_executed": None}, 2, 2),
            ({"passes_executed": True}, 4, 4),
            ({"passes_executed": 0}, 5, 1),
        ],
    )
    def test_ignores_invalid_or_bool_passes_executed_and_clamps_zero(
        self,
        metadata: dict[str, object],
        fallback_pass_count: int,
        expected_pass_count: int,
    ) -> None:
        source = _make_source_transcript(title="Source Title")
        candidate = CandidateText(
            text="## Section\n\nBody.\n\n### Extra Info\n\n1. Detail.",
            stage_name="long_expander",
            metadata=metadata,
        )

        result = post_process_expanded_transcript(
            candidate,
            source,
            pass_count=fallback_pass_count,
        )

        assert result.pass_count == expected_pass_count
