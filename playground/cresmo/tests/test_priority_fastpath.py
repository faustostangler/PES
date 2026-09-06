from pathlib import Path
import sys

# Ensure cresmo directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from cresmo_pipeline import resolve_priority_blocks
from cresmo_shared import extract_video_id, read_priority_video_ids


def test_extract_video_id_raw_slug():
    """Verify raw 11-character YouTube video IDs are extracted directly."""
    assert extract_video_id("TsrEV6nkdjo") == "TsrEV6nkdjo"
    assert extract_video_id("50ASgJc0310") == "50ASgJc0310"
    assert extract_video_id("  -yGHG3pnHLg  ") == "-yGHG3pnHLg"


def test_extract_video_id_youtube_urls():
    """Verify various YouTube URL formats are correctly parsed to 11-character video IDs."""
    assert extract_video_id("https://www.youtube.com/watch?v=TsrEV6nkdjo") == "TsrEV6nkdjo"
    assert extract_video_id("https://www.youtube.com/watch?v=TsrEV6nkdjo&t=120s&feature=shared") == "TsrEV6nkdjo"
    assert extract_video_id("http://youtube.com/watch?feature=shared&v=50ASgJc0310") == "50ASgJc0310"
    assert extract_video_id("https://youtu.be/50ASgJc0310?si=test1234") == "50ASgJc0310"
    assert extract_video_id("https://www.youtube.com/shorts/TsrEV6nkdjo") == "TsrEV6nkdjo"
    assert extract_video_id("https://www.youtube.com/embed/50ASgJc0310") == "50ASgJc0310"


def test_extract_video_id_invalid_or_comments():
    """Verify comments, empty strings, and invalid strings return None."""
    assert extract_video_id("# Professor Ricardo Marcílio") is None
    assert extract_video_id("   # comment with spaces   ") is None
    assert extract_video_id("") is None
    assert extract_video_id("   ") is None
    assert extract_video_id("not_a_valid_id") is None
    assert extract_video_id("https://example.com/not-youtube") is None


def test_read_priority_video_ids(tmp_path: Path):
    """Verify priority playlist files are read with order preservation and deduplication."""
    playlist_file = tmp_path / "playlist-priority.txt"
    content = """
# Priority videos for today
https://www.youtube.com/watch?v=TsrEV6nkdjo
50ASgJc0310

# Duplicates should be ignored
TsrEV6nkdjo
https://youtu.be/50ASgJc0310

# Another video
https://www.youtube.com/watch?v=UDrDg6uUOVs
"""
    playlist_file.write_text(content, encoding="utf-8")

    ids = read_priority_video_ids(playlist_file)
    assert ids == ["TsrEV6nkdjo", "50ASgJc0310", "UDrDg6uUOVs"]


def test_read_priority_video_ids_nonexistent(tmp_path: Path):
    """Verify non-existent file returns empty list gracefully."""
    missing = tmp_path / "does_not_exist.txt"
    assert read_priority_video_ids(missing) == []


def test_resolve_priority_blocks_fast_path(tmp_path: Path):
    """Verify resolve_priority_blocks finds matching files directly and returns them in priority order."""
    raw_dir = tmp_path / "raw"
    ch1 = raw_dir / "Channel One"
    ch2 = raw_dir / "Channel Two"
    ch1.mkdir(parents=True)
    ch2.mkdir(parents=True)

    # File 1: TsrEV6nkdjo
    f1 = ch1 / "2023-01-01-TsrEV6nkdjo.txt"
    f1.write_text(
        "---\nvideo_id: TsrEV6nkdjo\nvideo_title: Video One\nchannel_name: Channel One\n---\nTranscript 1 content.\n",
        encoding="utf-8",
    )

    # File 2: 50ASgJc0310
    f2 = ch2 / "2023-02-01-50ASgJc0310.txt"
    f2.write_text(
        "---\nvideo_id: 50ASgJc0310\nvideo_title: Video Two\nchannel_name: Channel Two\n---\nTranscript 2 content.\n",
        encoding="utf-8",
    )

    # File 3: Other regular video
    f3 = ch1 / "2023-03-01-regular12345.txt"
    f3.write_text(
        "---\nvideo_id: regular12345\nvideo_title: Video Regular\nchannel_name: Channel One\n---\nTranscript 3 content.\n",
        encoding="utf-8",
    )

    # Request priority in reverse: 50ASgJc0310 first, then TsrEV6nkdjo
    priority_ids = ["50ASgJc0310", "TsrEV6nkdjo"]
    processed_log = {}

    blocks = resolve_priority_blocks(
        priority_ids=priority_ids,
        raw_dir=raw_dir,
        processed_log=processed_log,
        force=False,
    )

    assert len(blocks) == 2
    assert blocks[0]["metadata"]["video_id"] == "50ASgJc0310"
    assert blocks[1]["metadata"]["video_id"] == "TsrEV6nkdjo"


def test_resolve_priority_blocks_idempotency(tmp_path: Path):
    """Verify already-processed videos are skipped unless force=True."""
    raw_dir = tmp_path / "raw"
    ch = raw_dir / "Channel One"
    ch.mkdir(parents=True)

    f = ch / "2023-01-01-TsrEV6nkdjo.txt"
    f.write_text(
        "---\nvideo_id: TsrEV6nkdjo\nvideo_title: Video One\nchannel_name: Channel One\n---\nTranscript 1.\n",
        encoding="utf-8",
    )

    processed_log = {"TsrEV6nkdjo": "2026-09-01T00:00:00"}

    # With force=False: should be skipped
    blocks = resolve_priority_blocks(
        priority_ids=["TsrEV6nkdjo"],
        raw_dir=raw_dir,
        processed_log=processed_log,
        force=False,
    )
    assert len(blocks) == 0

    # With force=True: should be included
    blocks_forced = resolve_priority_blocks(
        priority_ids=["TsrEV6nkdjo"],
        raw_dir=raw_dir,
        processed_log=processed_log,
        force=True,
    )
    assert len(blocks_forced) == 1
    assert blocks_forced[0]["metadata"]["video_id"] == "TsrEV6nkdjo"
