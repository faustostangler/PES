#!/usr/bin/env python3
"""Sanity check script to verify the refactored playground modules and helpers work correctly."""

import sys
from pathlib import Path

# Add parent directory to path to resolve local imports
sys.path.append(str(Path(__file__).parent))

from downloader import find_subtitle_url, reconstruct_json3_paragraphs, reconstruct_srv1_paragraphs
from helper import clean_filename, get_full_upload_date, is_within_range, sanitize_for_path, format_date_for_path, parse_yaml_header, parse_merged_transcriptions


def test_clean_filename():
    print("Testing clean_filename...")
    assert clean_filename("Concept: A / B ? C") == "Concept A  B  C"
    assert clean_filename("Entity Name|With<Special>Chars") == "Entity NameWithSpecialChars"
    print("  ✓ clean_filename works!")


def test_is_within_range():
    print("Testing is_within_range...")
    from datetime import UTC, datetime, timedelta

    # 2 days ago
    date_str = (datetime.now(UTC) - timedelta(days=2)).strftime("%Y%m%d")
    assert is_within_range(date_str, 5) is True

    # 10 days ago
    date_str_old = (datetime.now(UTC) - timedelta(days=10)).strftime("%Y-%m-%dT12:00:00Z")
    assert is_within_range(date_str_old, 5) is False
    print("  ✓ is_within_range works!")


def test_get_full_upload_date():
    print("Testing get_full_upload_date...")
    info = {"timestamp": 1716987600, "upload_date": "20240529"} # 2024-05-29 UTC
    date_out = get_full_upload_date(info)
    assert "2024" in date_out

    info_no_ts = {"upload_date": "20240529"}
    assert get_full_upload_date(info_no_ts) == "20240529"
    print("  ✓ get_full_upload_date works!")


def test_find_subtitle_url():
    print("Testing find_subtitle_url...")
    info = {
        "subtitles": {
            "pt-BR": [{"ext": "json3", "url": "http://pt-br-json3"}],
            "en": [{"ext": "srv1", "url": "http://en-srv1"}]
        }
    }
    lang, url = find_subtitle_url(info, "json3")
    assert lang == "pt-BR"
    assert url == "http://pt-br-json3"

    lang, url = find_subtitle_url(info, "srv1")
    assert lang == "en"
    assert url == "http://en-srv1"
    print("  ✓ find_subtitle_url works!")


def test_reconstruct_json3_paragraphs():
    print("Testing reconstruct_json3_paragraphs...")
    # Mock json3 data structure
    data = {
        "events": [
            {
                "tStartMs": 0,
                "dDurationMs": 1000,
                "segs": [{"utf8": "Hello"}]
            },
            {
                "tStartMs": 1500,
                "dDurationMs": 1000,
                "segs": [{"utf8": "world."}]
            },
            {
                "tStartMs": 5000, # Large gap (3.5s > 2s silence_threshold)
                "dDurationMs": 1000,
                "segs": [{"utf8": "This is a new paragraph."}]
            }
        ]
    }
    transcript = reconstruct_json3_paragraphs(data, silence_threshold_ms=2000, punctuation_limit=5)
    print(repr(transcript))
    assert "Hello world." in transcript
    assert "\n\n" in transcript
    assert "This is a new paragraph." in transcript
    print("  ✓ reconstruct_json3_paragraphs works!")


def test_reconstruct_srv1_paragraphs():
    print("Testing reconstruct_srv1_paragraphs...")
    # Mock srv1 XML structure
    xml_data = """<?xml version="1.0" encoding="utf-8" ?>
    <transcript>
        <text start="0" dur="1">First chunk of text.</text>
        <text start="1" dur="1">Second chunk.</text>
        <text start="2" dur="1">Third chunk.</text>
        <text start="3" dur="1">Fourth chunk.</text>
        <text start="4" dur="1">Fifth chunk.</text>
        <text start="5" dur="1">Sixth chunk.</text>
    </transcript>
    """
    # 5 punctuation marks limit should trigger split
    transcript = reconstruct_srv1_paragraphs(xml_data, punctuation_limit=3)
    print(repr(transcript))
    paragraphs = transcript.split("\n\n")
    assert len(paragraphs) >= 2
    print("  ✓ reconstruct_srv1_paragraphs works!")


def test_sanitize_for_path():
    print("Testing sanitize_for_path...")
    assert sanitize_for_path("Science & Technology") == "science_technology"
    assert sanitize_for_path("Augusto Galego") == "augusto_galego"
    assert sanitize_for_path("hello-world_test 123!") == "hello_world_test_123"
    assert sanitize_for_path(None) == "unknown"
    assert sanitize_for_path("") == "unknown"
    print("  ✓ sanitize_for_path works!")


def test_format_date_for_path():
    print("Testing format_date_for_path...")
    assert format_date_for_path("2026-06-01T12:27:10+00:00") == "2026-06-01"
    assert format_date_for_path("20260601") == "2026-06-01"
    assert format_date_for_path("") == "unknown_date"
    assert format_date_for_path(None) == "unknown_date"
    print("  ✓ format_date_for_path works!")


def test_parse_yaml_header():
    print("Testing parse_yaml_header...")
    import tempfile
    content = """---
url: https://youtube.com/watch?v=123
channel_id: UC_test
video_id: 123
video_description: |
  multi-line description
  here
---
some actual text content
"""
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
        try:
            meta = parse_yaml_header(tmp_path)
            assert meta.get("url") == "https://youtube.com/watch?v=123"
            assert meta.get("channel_id") == "UC_test"
            assert meta.get("video_id") == "123"
        finally:
            tmp_path.unlink()
    print("  ✓ parse_yaml_header works!")


def test_parse_merged_transcriptions():
    print("Testing parse_merged_transcriptions...")
    import tempfile
    content = """---
video_title: "Title 1"
video_id: ABC
video_description: |
  Line 1
  Line 2
---
Transcript text 1

---
video_title: "Title 2"
video_id: DEF
---
Transcript text 2
"""
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
        try:
            blocks = parse_merged_transcriptions(tmp_path)
            assert len(blocks) == 2
            
            assert blocks[0]["metadata"].get("video_title") == "Title 1"
            assert blocks[0]["metadata"].get("video_id") == "ABC"
            assert blocks[0]["metadata"].get("video_description") == "Line 1\nLine 2"
            assert blocks[0]["text"] == "Transcript text 1"
            
            assert blocks[1]["metadata"].get("video_title") == "Title 2"
            assert blocks[1]["metadata"].get("video_id") == "DEF"
            assert blocks[1]["text"] == "Transcript text 2"
        finally:
            tmp_path.unlink()
    print("  ✓ parse_merged_transcriptions works!")


if __name__ == "__main__":
    print("=== RUNNING PLAYGROUND REFACTOR SANITY CHECKS ===")
    test_clean_filename()
    test_is_within_range()
    test_get_full_upload_date()
    test_sanitize_for_path()
    test_format_date_for_path()
    test_parse_yaml_header()
    test_parse_merged_transcriptions()
    test_find_subtitle_url()
    test_reconstruct_json3_paragraphs()
    test_reconstruct_srv1_paragraphs()
    print("=================== ALL CHECKS PASSED ===================")
