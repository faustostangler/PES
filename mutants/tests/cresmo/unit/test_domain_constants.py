"""Unit tests for Cresmo Domain Constants and File Classification predicates.

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- ADR-015: Reserved System Filenames and Derived Output Directory Isolation
"""

from pathlib import Path

from cresmo.domain.value_objects.constants import (
    MAX_CHANNEL_ID_LENGTH,
    MAX_CHANNEL_NAME_LENGTH,
    MAX_NOTE_TITLE_LENGTH,
    MIN_CANONICAL_CHANNEL_ID_LENGTH,
    MIN_CHANNEL_ID_LENGTH,
    RESERVED_DERIVED_DIRS,
    RESERVED_SYSTEM_FILENAMES,
    is_processable_transcript_file,
)


class TestDomainConstants:
    """Test suite for domain constants definitions and immutability."""

    def test_length_constants_values(self) -> None:
        assert MAX_CHANNEL_NAME_LENGTH == 120
        assert MAX_CHANNEL_ID_LENGTH == 64
        assert MIN_CHANNEL_ID_LENGTH == 2
        assert MIN_CANONICAL_CHANNEL_ID_LENGTH == 4
        assert MAX_NOTE_TITLE_LENGTH == 200

    def test_reserved_system_filenames_content(self) -> None:
        expected = {
            "_canal.md",
            "brain.csv",
            "cresmo_ledger.db",
            "cresmo_ledger.db-wal",
            "cresmo_ledger.db-shm",
            "playlist.txt",
            "playlist-priority.txt",
            "_index.json",
        }
        assert isinstance(RESERVED_SYSTEM_FILENAMES, frozenset)
        assert RESERVED_SYSTEM_FILENAMES == expected

    def test_reserved_derived_dirs_content(self) -> None:
        expected = {
            "enriched",
            "master",
            "vault",
            ".venv",
            "tests",
            "__pycache__",
        }
        assert isinstance(RESERVED_DERIVED_DIRS, frozenset)
        assert RESERVED_DERIVED_DIRS == expected


class TestIsProcessableTranscriptFile:
    """Test suite for is_processable_transcript_file predicate adhering to ADR-015."""

    def test_valid_markdown_and_text_files(self) -> None:
        assert is_processable_transcript_file("valid_transcript.md") is True
        assert is_processable_transcript_file("valid_transcript.txt") is True
        assert is_processable_transcript_file(Path("subdir/valid_transcript.MD")) is True
        assert is_processable_transcript_file(Path("subdir/valid_transcript.TXT")) is True

    def test_invalid_extensions(self) -> None:
        assert is_processable_transcript_file("data.json") is False
        assert is_processable_transcript_file("audio.mp3") is False
        assert is_processable_transcript_file("video.mp4") is False
        assert is_processable_transcript_file("table.csv") is False
        assert is_processable_transcript_file("script.py") is False
        assert is_processable_transcript_file("no_extension") is False

    def test_hidden_and_system_prefixed_files(self) -> None:
        assert is_processable_transcript_file("_catalog.md") is False
        assert is_processable_transcript_file(".hidden.md") is False
        assert is_processable_transcript_file("_internal.txt") is False

    def test_hidden_or_system_prefixed_directories(self) -> None:
        assert is_processable_transcript_file(".git/transcript.md") is False
        assert is_processable_transcript_file(".obsidian/notes.md") is False
        assert is_processable_transcript_file("root/_archive/transcript.md") is False
        assert is_processable_transcript_file(Path("/root/.trash/transcript.txt")) is False
        # Root directory "/" should not trigger startswith prefix check
        assert is_processable_transcript_file(Path("/data/valid.md")) is True

    def test_reserved_system_filenames(self) -> None:
        for reserved_name in RESERVED_SYSTEM_FILENAMES:
            assert is_processable_transcript_file(reserved_name) is False
            assert is_processable_transcript_file(f"subdir/{reserved_name}") is False
            assert is_processable_transcript_file(reserved_name.upper()) is False

    def test_backup_swap_and_temporary_files(self) -> None:
        assert is_processable_transcript_file("transcript.md.tmp") is False
        assert is_processable_transcript_file("transcript.md.bak") is False
        assert is_processable_transcript_file("transcript.txt.swp") is False
        assert is_processable_transcript_file("transcript.md~") is False

    def test_reserved_derived_directories(self) -> None:
        for derived_dir in RESERVED_DERIVED_DIRS:
            assert is_processable_transcript_file(f"{derived_dir}/transcript.md") is False
            assert is_processable_transcript_file(f"data/{derived_dir}/sub/transcript.txt") is False
            assert is_processable_transcript_file(f"{derived_dir.upper()}/transcript.md") is False
