"""TDD unit and integration tests for Two-Phase Batched Atomic Notes Generation."""

import json
from pathlib import Path
import sys
import pytest

# Ensure playground/cresmo is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cresmo_llm import MockLLMAdapter
from cresmo_pipeline import cresmo_notes, is_valid_atomic_json


def test_cresmo_notes_batched_creates_inventory_and_all_notes(tmp_path: Path) -> None:
    """Verify cresmo_notes discovers inventory first, then synthesizes notes in batches of <= 5."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = enriched_dir / "vid_test.md"
    enriched_file.write_text(
        "## Deep Analysis\n\nLongue durée analysis of multiple concepts.\n\n## Informações Complementares\nDetails.",
        encoding="utf-8",
    )

    # 7 items total -> should result in 1 inventory call + 2 batch calls (5 + 2)
    mock_inventory = [
        {"title": f"Concept {i}", "type": "concept", "domain": "test_domain"}
        for i in range(1, 8)
    ]
    mock_batch_1 = [
        {
            "title": f"Concept {i}",
            "type": "concept",
            "definition": f"Detailed definition of concept {i}.",
            "direct_relations": [f"[[Concept {i}]] -> relates to -> [[Context]]"],
        }
        for i in range(1, 6)
    ]
    mock_batch_2 = [
        {
            "title": f"Concept {i}",
            "type": "concept",
            "definition": f"Detailed definition of concept {i}.",
            "direct_relations": [f"[[Concept {i}]] -> relates to -> [[Context]]"],
        }
        for i in range(6, 8)
    ]

    responses = [
        json.dumps(mock_inventory),
        f"```json\n{json.dumps(mock_batch_1)}\n```",
        f"```json\n{json.dumps(mock_batch_2)}\n```",
    ]

    adapter = MockLLMAdapter()
    # Provide responses sequentially via side effect
    def canned_response_generator() -> str:
        idx = len(adapter.call_history) - 1
        return responses[idx] if idx < len(responses) else "[]"

    adapter.transform = lambda prompt, system_instruction=None, temperature=None: (  # type: ignore[assignment]
        adapter.call_history.append({
            "prompt": prompt,
            "system_instruction": system_instruction,
            "temperature": temperature,
        }) or canned_response_generator()
    )

    meta = {"channel_name": "TestChannel", "video_id": "vid_test"}
    json_file, is_new = cresmo_notes(
        enriched_file=enriched_file,
        meta=meta,
        llm=adapter,
        force=True,
    )

    assert is_new is True
    assert json_file.exists()
    assert is_valid_atomic_json(json_file)

    # Total calls: 1 (Inventory) + 2 (Batches of 5 and 2) = 3 calls
    assert len(adapter.call_history) == 3
    # Verify deterministic temperature 0.0 was used across all calls
    assert all(c["temperature"] == 0.0 for c in adapter.call_history)

    # Verify unified output file structure
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert "inventory" in data
    assert len(data["inventory"]) == 7
    assert "notes" in data
    assert len(data["notes"]) == 7
    assert data["notes"][0]["title"] == "Concept 1"
    assert data["notes"][6]["title"] == "Concept 7"


def test_cresmo_notes_batched_resumes_interrupted_run(tmp_path: Path) -> None:
    """Verify cresmo_notes resumes an interrupted run without re-generating existing notes."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = enriched_dir / "vid_resume.md"
    enriched_file.write_text("## Topic\nContent\n## Informações Complementares\nNotes.", encoding="utf-8")

    json_file = enriched_dir / "vid_resume.json"
    # Pre-existing file with full inventory (6 items), but only batch 1 (3 items) was generated
    inventory = [{"title": f"Item {i}", "type": "concept"} for i in range(1, 7)]
    existing_notes = [
        {"title": f"Item {i}", "type": "concept", "definition": f"Definition of Item {i}"}
        for i in range(1, 4)
    ]
    initial_payload = {
        "video_id": "vid_resume",
        "channel_name": "TestChannel",
        "inventory": inventory,
        "notes": existing_notes,
    }
    json_file.write_text(json.dumps(initial_payload, indent=2), encoding="utf-8")

    # Remaining items to generate: Items 4, 5, 6
    remaining_batch = [
        {"title": f"Item {i}", "type": "concept", "definition": f"Definition of Item {i}"}
        for i in range(4, 7)
    ]
    adapter = MockLLMAdapter(canned_response=json.dumps(remaining_batch))

    meta = {"channel_name": "TestChannel", "video_id": "vid_resume"}
    result_file, is_new = cresmo_notes(
        enriched_file=enriched_file,
        meta=meta,
        llm=adapter,
        force=False,
    )

    assert result_file == json_file
    assert is_new is True

    # Exactly 1 call should have been made for the remaining batch (Items 4-6)
    assert len(adapter.call_history) == 1
    call_prompt = adapter.call_history[0]["prompt"]
    assert "Item 4" in call_prompt
    assert "Item 5" in call_prompt
    assert "Item 6" in call_prompt
    assert "Item 1" not in call_prompt  # Already generated!

    # Final file should contain all 6 notes
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert len(data["notes"]) == 6
    titles = [n["title"] for n in data["notes"]]
    assert titles == [f"Item {i}" for i in range(1, 7)]


def test_cresmo_notes_batched_skips_when_fully_complete(tmp_path: Path) -> None:
    """Verify cresmo_notes immediately skips if inventory and all notes are already complete."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = enriched_dir / "vid_done.md"
    enriched_file.write_text("## Topic\nContent\n## Informações Complementares\nNotes.", encoding="utf-8")

    json_file = enriched_dir / "vid_done.json"
    inventory = [{"title": f"Done {i}", "type": "concept"} for i in range(1, 6)]
    completed_notes = [
        {"title": f"Done {i}", "type": "concept", "definition": f"Definition {i}"}
        for i in range(1, 6)
    ]
    payload = {
        "video_id": "vid_done",
        "channel_name": "TestChannel",
        "inventory": inventory,
        "notes": completed_notes,
    }
    json_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    adapter = MockLLMAdapter()
    meta = {"channel_name": "TestChannel", "video_id": "vid_done"}
    result_file, is_new = cresmo_notes(
        enriched_file=enriched_file,
        meta=meta,
        llm=adapter,
        force=False,
    )

    assert result_file == json_file
    assert is_new is False
    # Zero LLM calls
    assert len(adapter.call_history) == 0
