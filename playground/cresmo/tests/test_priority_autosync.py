"""Unit tests for Cresmo priority on-demand auto-sync functionality."""

from pathlib import Path
import sys

# Ensure cresmo directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from cresmo_pipeline import resolve_priority_blocks
from cresmo_shared import read_priority_entries


def test_read_priority_entries(tmp_path: Path):
    """Verify read_priority_entries correctly extracts IDs and builds canonical URLs."""
    playlist_file = tmp_path / "playlist-priority.txt"
    content = """
# Priority videos
https://youtu.be/9IbNJ0EsTxI?si=test1234
TsrEV6nkdjo # raw slug with inline comment
https://www.youtube.com/watch?v=50ASgJc0310&t=45s

# Duplicates should be ignored
9IbNJ0EsTxI
https://www.youtube.com/watch?v=TsrEV6nkdjo
"""
    playlist_file.write_text(content, encoding="utf-8")

    entries = read_priority_entries(playlist_file)
    assert len(entries) == 3

    assert entries[0]["video_id"] == "9IbNJ0EsTxI"
    assert entries[0]["url"] == "https://youtu.be/9IbNJ0EsTxI?si=test1234"

    assert entries[1]["video_id"] == "TsrEV6nkdjo"
    assert entries[1]["url"] == "https://www.youtube.com/watch?v=TsrEV6nkdjo"

    assert entries[2]["video_id"] == "50ASgJc0310"
    assert entries[2]["url"] == "https://www.youtube.com/watch?v=50ASgJc0310&t=45s"


def test_resolve_priority_blocks_with_auto_sync_mock(tmp_path: Path):
    """Verify resolve_priority_blocks calls syncer when a file is absent and auto_sync=True."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)

    synced_urls = []

    def mock_syncer(video_id: str, url: str, target_raw_dir: Path) -> Path | None:
        synced_urls.append(url)
        ch_dir = target_raw_dir / "Channel Test"
        ch_dir.mkdir(parents=True, exist_ok=True)
        txt_path = ch_dir / f"2026-09-05-{video_id}.txt"
        txt_path.write_text(
            f"---\nvideo_id: {video_id}\nvideo_title: Synced Video\nchannel_name: Channel Test\n---\nSynced content.\n",
            encoding="utf-8",
        )
        return txt_path

    priority_entries = [
        {"video_id": "auto1234567", "url": "https://www.youtube.com/watch?v=auto1234567"}
    ]

    blocks = resolve_priority_blocks(
        priority_ids=priority_entries,
        raw_dir=raw_dir,
        processed_log=set(),
        force=False,
        auto_sync=True,
        syncer=mock_syncer,
    )

    assert len(synced_urls) == 1
    assert synced_urls[0] == "https://www.youtube.com/watch?v=auto1234567"
    assert len(blocks) == 1
    assert blocks[0]["metadata"]["video_id"] == "auto1234567"


def test_resolve_priority_blocks_auto_sync_disabled(tmp_path: Path):
    """Verify resolve_priority_blocks skips absent files when auto_sync=False."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)

    synced_urls = []

    def mock_syncer(video_id: str, url: str, target_raw_dir: Path) -> Path | None:
        synced_urls.append(url)
        return None

    priority_entries = [
        {"video_id": "missing1234", "url": "https://www.youtube.com/watch?v=missing1234"}
    ]

    blocks = resolve_priority_blocks(
        priority_ids=priority_entries,
        raw_dir=raw_dir,
        processed_log=set(),
        force=False,
        auto_sync=False,
        syncer=mock_syncer,
    )

    assert len(synced_urls) == 0
    assert len(blocks) == 0
