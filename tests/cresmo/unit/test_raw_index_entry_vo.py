"""Unit tests for RawIndexEntry Value Object.

Verifies domain validation, invariants, Markdown block rendering, and CSV row serialization.
"""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import ContentId, RawIndexEntry


class TestRawIndexEntry:
    """Tests for RawIndexEntry."""

    def test_valid_raw_index_entry_creation(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name="Political Theory",
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula que minorias organizadas governam sociedades. Estruturas burocráticas cristalizam privilégios até a emergência de contra-elites.",
        )

        assert entry.video_id.value == "dQw4w9WgXcQ"
        assert entry.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert entry.title == "Vilfredo Pareto and Elites"
        assert entry.channel_name == "Political Theory"
        assert entry.key_concept == "Circulação de Elites"
        assert "minorias organizadas governam" in entry.synthesis

    def test_markdown_block_format(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name="Political Theory",
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula que minorias organizadas governam sociedades.",
        )

        md = entry.to_markdown_block()
        assert "### [Vilfredo Pareto and Elites](https://youtube.com/watch?v=dQw4w9WgXcQ)" in md
        assert "`dQw4w9WgXcQ`" in md
        assert "**Conceito**: Circulação de Elites" in md
        assert "A circulação das elites postula" in md

    def test_csv_row_format(self) -> None:
        entry = RawIndexEntry(
            video_id=ContentId("dQw4w9WgXcQ"),
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Vilfredo Pareto and Elites",
            channel_name="Political Theory",
            key_concept="Circulação de Elites",
            synthesis="A circulação das elites postula\nque minorias organizadas governam.",
        )

        row = entry.to_csv_row()
        assert len(row) == 3
        assert row[0] == "dQw4w9WgXcQ.md"
        assert row[1] == "Circulação de Elites"
        # Newlines in synthesis should be collapsed into single line for CSV
        assert "\n" not in row[2]
        assert "A circulação das elites postula que minorias organizadas governam." == row[2]

    def test_rejects_empty_fields(self) -> None:
        with pytest.raises(DomainValidationError, match="cannot be empty"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="",
                title="Title",
                channel_name="Channel",
                key_concept="Concept",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match="cannot be empty"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="",
                channel_name="Channel",
                key_concept="Concept",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match="cannot be empty"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="Title",
                channel_name="",
                key_concept="Concept",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match="cannot be empty"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="Title",
                channel_name="Channel",
                key_concept="",
                synthesis="Synthesis",
            )

        with pytest.raises(DomainValidationError, match="cannot be empty"):
            RawIndexEntry(
                video_id=ContentId("dQw4w9WgXcQ"),
                url="https://url",
                title="Title",
                channel_name="Channel",
                key_concept="Concept",
                synthesis="",
            )
