"""Unit tests for RawIndexEntry Value Object.

Verifies domain validation, invariants, Markdown block rendering, and CSV row serialization.
"""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import ChannelName, ContentId, RawIndexEntry


class TestRawIndexEntry:
    """Tests for RawIndexEntry."""

    def test_valid_raw_index_entry_creation(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name=ChannelName("Political Theory"),
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula que minorias organizadas governam sociedades. Estruturas burocráticas cristalizam privilégios até a emergência de contra-elites.",
        )

        assert entry.video_id.value == "dQw4w9WgXcQ"
        assert entry.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert entry.title == "Vilfredo Pareto and Elites"
        assert entry.channel_name == "Political Theory"
        assert entry.key_concept == "Circulação de Elites"
        assert "minorias organizadas governam" in entry.synthesis
        assert entry.summary == ""
        assert entry.excerpt == ""

    def test_raw_index_entry_with_summary_and_excerpt(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name=ChannelName("Political Theory"),
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula que minorias organizadas governam sociedades.",
            summary="  Resumo estruturado do vídeo sobre elites governantes.  ",
            excerpt="  Trecho inicial da transcrição com o contexto histórico.  ",
        )

        assert entry.summary == "Resumo estruturado do vídeo sobre elites governantes."
        assert entry.excerpt == "Trecho inicial da transcrição com o contexto histórico."

    def test_markdown_block_format(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name=ChannelName("Political Theory"),
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula que minorias organizadas governam sociedades.",
        )

        md = entry.to_markdown_block()
        expected_md = (
            "### [Vilfredo Pareto and Elites](https://youtube.com/watch?v=dQw4w9WgXcQ)\n"
            "- **Video ID**: `dQw4w9WgXcQ` | **Conceito**: Circulação de Elites\n\n"
            "A circulação das elites postula que minorias organizadas governam sociedades.\n"
        )
        assert md == expected_md

    def test_csv_row_format(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name=ChannelName("Political Theory"),
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula\nque minorias organizadas governam.",
            channel_category="politics_br",
        )

        row = entry.to_csv_row()
        assert row == [
            "politics_br",
            "Political Theory",
            "dQw4w9WgXcQ.md",
            "Circulação de Elites",
            "A circulação das elites postula que minorias organizadas governam.",
        ]

    def test_coercion_and_normalization(self) -> None:
        entry = RawIndexEntry(
            video_id="  dQw4w9WgXcQ  ",  # type: ignore[arg-type]
            url="  https://youtube.com/watch?v=dQw4w9WgXcQ  ",
            title="  Vilfredo Pareto and Elites  ",
            channel_name="  Political Theory  ",  # type: ignore[arg-type]
            key_concept="  Circulação   de   Elites  ",
            synthesis="  A circulação das elites postula que minorias organizadas governam.  ",
            channel_category="  politics_br  ",
            summary="  Resumo  ",
            excerpt="  Trecho  ",
        )
        assert isinstance(entry.video_id, ContentId)
        assert entry.video_id.value == "dQw4w9WgXcQ"
        assert entry.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert entry.title == "Vilfredo Pareto and Elites"
        assert isinstance(entry.channel_name, ChannelName)
        assert entry.channel_name.value == "Political Theory"
        assert entry.key_concept == "Circulação de Elites"
        assert (
            entry.synthesis == "A circulação das elites postula que minorias organizadas governam."
        )
        assert entry.channel_category == "politics_br"
        assert entry.summary == "Resumo"
        assert entry.excerpt == "Trecho"

    def test_default_or_none_channel_category(self) -> None:
        entry1 = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://url",
            title="Title",
            channel_name=ChannelName("Channel"),
            key_concept="Concept",
            synthesis="Synthesis",
            channel_category="",
        )
        assert entry1.channel_category == ""

        entry2 = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://url",
            title="Title",
            channel_name=ChannelName("Channel"),
            key_concept="Concept",
            synthesis="Synthesis",
            channel_category=None,  # type: ignore[arg-type]
        )
        assert entry2.channel_category == ""

    def test_rejects_empty_fields(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^RawIndexEntry url cannot be empty\.$"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="",
                title="Title",
                channel_name=ChannelName("Channel"),
                key_concept="Concept",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match=r"^RawIndexEntry title cannot be empty\.$"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="",
                channel_name=ChannelName("Channel"),
                key_concept="Concept",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match=r"^ChannelName cannot be empty"):
            ChannelName("")

        with pytest.raises(
            DomainValidationError, match=r"^RawIndexEntry key_concept cannot be empty\.$"
        ):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="Title",
                channel_name=ChannelName("Channel"),
                key_concept="",
                synthesis="Synthesis",
            )

        with pytest.raises(
            DomainValidationError, match=r"^RawIndexEntry synthesis cannot be empty\.$"
        ):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="Title",
                channel_name=ChannelName("Channel"),
                key_concept="Concept",
                synthesis="",
            )
