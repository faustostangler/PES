import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import stage2 module which we will create next
import stage2

def test_clean_gemini_response():
    """Should correctly strip code block wrapping from Gemini response."""
    wrapped_md = "```markdown\n# Structured Note\nSome content\n```"
    cleaned = stage2.clean_gemini_response(wrapped_md)
    assert cleaned == "# Structured Note\nSome content"

    wrapped_json = "```json\n{\n  \"key\": \"value\"\n}\n```"
    cleaned_json = stage2.clean_gemini_response(wrapped_json)
    assert cleaned_json == "{\n  \"key\": \"value\"\n}"

    no_wrap = "Plain text content"
    assert stage2.clean_gemini_response(no_wrap) == "Plain text content"

def test_validate_response():
    """Should validate non-empty responses and reject error states or too short responses."""
    assert stage2.validate_response("A very valid response text that is long enough to pass validation thresholds.") is True
    assert stage2.validate_response("") is False
    assert stage2.validate_response("Too short") is False
    assert stage2.validate_response("Something went wrong with the request, please try again.") is False

def test_discover_unprocessed_files(tmp_path):
    """Should find all .txt files in raw_dir that do not exist in enriched_dir."""
    raw_dir = tmp_path / "raw"
    enriched_dir = tmp_path / "enriched"

    raw_dir.mkdir()
    enriched_dir.mkdir()

    # Create dummy channels
    (raw_dir / "ChannelA").mkdir()
    (raw_dir / "ChannelB").mkdir()
    (enriched_dir / "ChannelA").mkdir()

    # Create raw files
    file1 = raw_dir / "ChannelA" / "video1.txt"
    file2 = raw_dir / "ChannelA" / "video2.txt"
    file3 = raw_dir / "ChannelB" / "video3.txt"
    file1.touch()
    file2.touch()
    file3.touch()

    # Create enriched files (video1 is already processed)
    (enriched_dir / "ChannelA" / "video1.txt").touch()

    unprocessed = stage2.discover_unprocessed_files(raw_dir, enriched_dir)
    
    # Only video2 and video3 should be unprocessed
    unprocessed_rel = [p.relative_to(raw_dir) for p in unprocessed]
    assert Path("ChannelA/video2.txt") in unprocessed_rel
    assert Path("ChannelB/video3.txt") in unprocessed_rel
    assert Path("ChannelA/video1.txt") not in unprocessed_rel

def test_parse_raw_file(tmp_path):
    """Should parse a raw file's YAML header and its text transcript separately."""
    raw_file = tmp_path / "raw_video.txt"
    raw_file.write_text("""---
video_title: "Test Title"
video_id: 12345
---
Here goes the transcript text of the video.
It spans multiple lines.
""", encoding="utf-8")

    yaml_header, text = stage2.parse_raw_file(raw_file)
    assert "video_title" in yaml_header
    assert yaml_header["video_title"] == "Test Title"
    assert yaml_header["video_id"] == "12345"
    assert "Here goes the transcript text" in text
    assert "multiple lines." in text

@patch("stage2.call_detranscriptor")
@patch("stage2.call_expander")
@patch("stage2.call_downgrader")
def test_process_file(mock_downgrader, mock_expander, mock_detranscriptor, tmp_path):
    """Should run full Stage 2 pipeline on a raw file and save the output in the target directory."""
    raw_dir = tmp_path / "raw"
    enriched_dir = tmp_path / "enriched"
    raw_dir.mkdir()
    enriched_dir.mkdir()

    channel_dir = raw_dir / "TestChannel"
    channel_dir.mkdir()
    raw_file = channel_dir / "video1.txt"
    raw_file.write_text("""---
video_title: "Title"
video_id: 999
---
Raw transcript content
""", encoding="utf-8")

    mock_detranscriptor.return_value = "Detranscribed content"
    mock_expander.return_value = "Expanded content"
    mock_downgrader.return_value = "Downgraded final content"

    mock_processor = MagicMock()

    stage2.process_file(raw_file, enriched_dir, mock_processor, raw_dir=raw_dir)

    target_file = enriched_dir / "TestChannel" / "video1.txt"
    assert target_file.exists()

    content = target_file.read_text(encoding="utf-8")
    assert "video_title: Title" in content
    assert "video_id: 999" in content
    assert "Downgraded final content" in content

