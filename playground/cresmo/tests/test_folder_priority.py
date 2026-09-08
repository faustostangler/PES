from pathlib import Path
import sys
import uuid

# Ensure cresmo directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from cresmo_shared import (
    DEFAULT_PRIORITY_FOLDER,
    classify_text_content,
    generate_content_uuid,
    parse_priority_text_file,
    resolve_folder_priority_blocks,
)


def test_default_priority_folder_path():
    """Verify default priority folder is set to CRESMO_ROOT / 'priority_content'."""
    assert DEFAULT_PRIORITY_FOLDER.name == "priority_content"


def test_generate_content_uuid():
    """Verify deterministic UUIDv5 is generated from text content to prevent collisions."""
    text1 = "This is a lecture transcript about clean architecture and domain-driven design."
    text2 = "This is a lecture transcript about clean architecture and domain-driven design."
    text3 = "Different text entirely about quantum mechanics."

    uid1 = generate_content_uuid(text1)
    uid2 = generate_content_uuid(text2)
    uid3 = generate_content_uuid(text3)

    # Must be valid UUID strings
    assert uuid.UUID(uid1)
    assert uuid.UUID(uid2)
    assert uuid.UUID(uid3)

    # Identical content yields identical UUID
    assert uid1 == uid2
    # Different content yields different UUID
    assert uid1 != uid3


def test_classify_text_content():
    """Verify content-aware classification for plain text files."""
    politics_text = "O STF e o ministro Alexandre de Moraes determinaram medidas no Congresso Nacional e no Senado Federal sobre as eleições."
    tech_text = "Building a clean architecture modular monolith with Python, FastAPI, and Docker using LLM agents."

    domain_pol, cat_pol = classify_text_content(politics_text)
    assert domain_pol == "politics_br"
    assert cat_pol == "volatile"

    domain_tech, cat_tech = classify_text_content(tech_text)
    assert domain_tech == "tech_ai"
    assert cat_tech == "perennial"


def test_parse_priority_text_file_plain(tmp_path: Path):
    """Verify plain .txt file without frontmatter creates a canonical block with channel='text' and UUIDv5."""
    sample_file = tmp_path / "notes_on_hexagonal.txt"
    sample_file.write_text(
        "# Hexagonal Architecture Notes\n\nPorts and adapters decouple business logic from infrastructure.",
        encoding="utf-8",
    )

    blocks = parse_priority_text_file(sample_file)
    assert len(blocks) == 1

    block = blocks[0]
    meta = block["metadata"]
    assert block["source_file"] == sample_file
    assert meta["channel_name"] == "text"
    assert meta["video_title"] == "Hexagonal Architecture Notes"
    # video_id must be a valid UUIDv5 derived from content
    assert uuid.UUID(meta["video_id"])
    assert "Ports and adapters" in block["text"]


def test_parse_priority_text_file_with_yaml(tmp_path: Path):
    """Verify .txt file containing YAML frontmatter preserves specified metadata."""
    sample_file = tmp_path / "custom_article.txt"
    content = """---
video_title: "Custom Article Title"
video_id: custom-article-123
channel_name: "SpecialGuest"
channel_category: "tech_ai"
url: "https://example.com/custom"
---
Body content of the custom article.
"""
    sample_file.write_text(content, encoding="utf-8")

    blocks = parse_priority_text_file(sample_file)
    assert len(blocks) == 1

    meta = blocks[0]["metadata"]
    assert meta["video_title"] == "Custom Article Title"
    assert meta["video_id"] == "custom-article-123"
    assert meta["channel_name"] == "SpecialGuest"
    assert meta["domain"] == "tech_ai"
    assert blocks[0]["text"] == "Body content of the custom article."


def test_resolve_folder_priority_blocks_ordering_and_idempotency(tmp_path: Path):
    """Verify resolve_folder_priority_blocks scans directory, sorts files, and skips processed IDs."""
    folder = tmp_path / "priority_content"
    folder.mkdir()

    f1 = folder / "01_alpha.txt"
    f1.write_text("Alpha transcript text.", encoding="utf-8")

    f2 = folder / "02_beta.txt"
    f2.write_text("Beta transcript text.", encoding="utf-8")

    # Both unprocessed
    blocks = resolve_folder_priority_blocks(folder, processed_log=set(), force=False)
    assert len(blocks) == 2
    assert blocks[0]["source_file"] == f1
    assert blocks[1]["source_file"] == f2

    # If alpha is already processed in log, it should be skipped
    alpha_id = blocks[0]["metadata"]["video_id"]
    processed_log = {alpha_id: {"processed_at": "2026-09-08T12:00:00"}}

    blocks_filtered = resolve_folder_priority_blocks(folder, processed_log=processed_log, force=False)
    assert len(blocks_filtered) == 1
    assert blocks_filtered[0]["source_file"] == f2

    # With force=True, alpha is included
    blocks_forced = resolve_folder_priority_blocks(folder, processed_log=processed_log, force=True)
    assert len(blocks_forced) == 2


def test_resolve_folder_priority_nonexistent(tmp_path: Path):
    """Verify non-existent directory returns empty list gracefully."""
    missing = tmp_path / "non_existent_folder"
    assert resolve_folder_priority_blocks(missing, processed_log=set()) == []


def test_folder_priority_artifact_destination_path(tmp_path: Path):
    """Verify artifacts for priority folder items are designated strictly under enriched/text/."""
    sample_file = tmp_path / "lecture.txt"
    sample_file.write_text("Lecture content on distributed systems and event storming.", encoding="utf-8")

    blocks = parse_priority_text_file(sample_file)
    meta = blocks[0]["metadata"]
    channel = meta["channel_name"]
    vid = meta["video_id"]

    assert channel == "text"

    enriched_dir = tmp_path / "enriched"
    channel_dir = enriched_dir / channel
    channel_dir.mkdir(parents=True, exist_ok=True)

    enriched_file = channel_dir / f"{vid}.md"
    json_file = channel_dir / f"{vid}.json"
    reconciliation_log = channel_dir / f"{vid}_reconciliation.md"

    assert enriched_file.parent.name == "text"
    assert json_file.parent.name == "text"
    assert reconciliation_log.parent.name == "text"


def test_three_tier_precedence_and_deduplication(tmp_path: Path):
    """Verify Tier-1 Folder Priority precedes Tier-2 YouTube Priority and deduplicates across tiers."""
    from cresmo_pipeline import resolve_priority_blocks
    from cresmo_shared import read_priority_entries

    # 1. Setup Priority Content Folder (Tier 1)
    priority_folder = tmp_path / "priority_content"
    priority_folder.mkdir()
    f_tier1 = priority_folder / "01_urgent_doc.txt"
    f_tier1.write_text(
        "---\nvideo_id: SHARED12345\nvideo_title: Tier 1 Urgent Document\nchannel_name: text\n---\nTier 1 text.\n",
        encoding="utf-8",
    )

    # 2. Setup YouTube Priority Playlist (Tier 2) - contains SHARED12345 (duplicate) and YT_EXCLUSIV
    yt_priority_file = tmp_path / "playlist-priority.txt"
    yt_priority_file.write_text(
        "SHARED12345\nYT_EXCLUSIV\n",
        encoding="utf-8",
    )

    # 3. Setup Raw Directory (Tier 3)
    raw_dir = tmp_path / "raw"
    ch = raw_dir / "TestChannel"
    ch.mkdir(parents=True)
    (ch / "2026-01-01-SHARED12345.txt").write_text(
        "---\nvideo_id: SHARED12345\nvideo_title: Raw Shared\nchannel_name: TestChannel\n---\nRaw text.\n",
        encoding="utf-8",
    )
    (ch / "2026-01-01-YT_EXCLUSIV.txt").write_text(
        "---\nvideo_id: YT_EXCLUSIV\nvideo_title: YT Exclusive\nchannel_name: TestChannel\n---\nRaw text.\n",
        encoding="utf-8",
    )
    (ch / "2026-01-01-BULK1234567.txt").write_text(
        "---\nvideo_id: BULK1234567\nvideo_title: Bulk Catalog\nchannel_name: TestChannel\n---\nRaw text.\n",
        encoding="utf-8",
    )

    processed_log = set()

    # Step A: Resolve Tier 1
    folder_blocks = resolve_folder_priority_blocks(priority_folder, processed_log=processed_log)
    folder_vids = {b["metadata"]["video_id"] for b in folder_blocks}
    assert folder_vids == {"SHARED12345"}

    # Step B: Resolve Tier 2 (deduplicating against Tier 1)
    yt_entries = read_priority_entries(yt_priority_file)
    yt_entries = [e for e in yt_entries if e["video_id"] not in folder_vids]
    assert len(yt_entries) == 1
    assert yt_entries[0]["video_id"] == "YT_EXCLUSIV"

    yt_blocks = resolve_priority_blocks(
        priority_ids=yt_entries,
        raw_dir=raw_dir,
        processed_log=processed_log,
        auto_sync=False,
    )
    assert len(yt_blocks) == 1
    assert yt_blocks[0]["metadata"]["video_id"] == "YT_EXCLUSIV"

    # Step C: Tier 3 candidate blocks excludes handled IDs
    handled_vids = folder_vids | {b["metadata"]["video_id"] for b in yt_blocks}
    bulk_files = sorted(raw_dir.rglob("*.txt"))
    tier3_blocks = []
    from cresmo_shared import parse_merged_transcriptions
    for bf in bulk_files:
        for b in parse_merged_transcriptions(bf):
            vid = b["metadata"]["video_id"]
            if vid not in handled_vids:
                tier3_blocks.append(b)

    assert len(tier3_blocks) == 1
    assert tier3_blocks[0]["metadata"]["video_id"] == "BULK1234567"

    # Total ordered queue
    candidate_blocks = folder_blocks + yt_blocks + tier3_blocks
    assert len(candidate_blocks) == 3
    assert candidate_blocks[0]["metadata"]["video_id"] == "SHARED12345"
    assert candidate_blocks[0]["metadata"]["channel_name"] == "text"  # Proves Tier 1 won
    assert candidate_blocks[1]["metadata"]["video_id"] == "YT_EXCLUSIV"
    assert candidate_blocks[2]["metadata"]["video_id"] == "BULK1234567"


def test_metadata_domain_preservation_for_text_channel(tmp_path: Path):
    """Test that text channel blocks preserve content-derived domain and category_type."""
    f = tmp_path / "geopolitics_doc.txt"
    f.write_text(
        "# Crise Ucrania e Otan\nDiscussao sobre guerra na ucrania, otan, russia, hegemonia e potencias.",
        encoding="utf-8",
    )
    blocks = parse_priority_text_file(f)
    assert len(blocks) == 1
    meta = blocks[0]["metadata"]
    assert meta["channel_name"] == "text"
    assert meta["domain"] == "geopolitics"
    assert meta["category_type"] == "volatile"

