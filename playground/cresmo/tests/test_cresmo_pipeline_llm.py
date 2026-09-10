"""Integration tests for Cresmo pipeline stages with LLM Transformation Port."""

import json
from pathlib import Path
import pytest

from cresmo_llm import MockLLMAdapter
import cresmo_pipeline


def test_gap_filler_with_llm_adapter(tmp_path: Path):
    """Verify cresmo_gap_filler directly uses LLMTransformationPort without polling or sleep."""
    raw_file = tmp_path / "test_raw.txt"
    raw_file.write_text("Raw transcript content about geopolitics.", encoding="utf-8")
    enriched_dir = tmp_path / "enriched"

    mock_response = (
        "## Resumo Analítico\n\n"
        + "Texto contínuo sem oralidades com densidade histórica.\n" * 20
        + "\n\n## Informações Complementares\n"
        + "- Fato histórico 1\n"
        + "- Fato histórico 2\n"
    )
    adapter = MockLLMAdapter(canned_response=mock_response)

    meta = {"channel_name": "TestChannel", "video_id": "vid_abc123"}
    enriched_file = cresmo_pipeline.cresmo_gap_filler(
        txt_file=raw_file,
        meta=meta,
        llm=adapter,
        output_dir=enriched_dir,
        total_passes=2,
        force=True,
    )

    assert enriched_file.exists()
    assert len(adapter.call_history) == 2
    assert "## Resumo Analítico" in enriched_file.read_text(encoding="utf-8")
    assert "## Informações Complementares" in enriched_file.read_text(encoding="utf-8")


def test_expander_with_llm_adapter(tmp_path: Path):
    """Verify cresmo_expander executes 2 inner steps using LLMTransformationPort."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = enriched_dir / "vid_exp.md"
    enriched_file.write_text(
        "## Base Text\n" + "x" * 600 + "\n## Informações Complementares\nInitial notes",
        encoding="utf-8",
    )

    raw_file = tmp_path / "raw.txt"
    raw_file.write_text("Ground truth", encoding="utf-8")

    mock_response = (
        "## Expanded Compendium\n\n"
        + "Longue durée analysis and synchronic cross-sections.\n" * 20
        + "\n\n## Informações Complementares\n"
        + "- Comparative civilizational dossier\n"
    )
    adapter = MockLLMAdapter(canned_response=mock_response)

    meta = {"channel_name": "TestChannel", "video_id": "vid_exp"}
    result_file = cresmo_pipeline.cresmo_expander(
        enriched_file=enriched_file,
        meta=meta,
        llm=adapter,
        raw_file=raw_file,
        force=True,
    )

    assert result_file == enriched_file
    assert len(adapter.call_history) == 2  # Step 1 (long) + Step 2 (wide)
    content = result_file.read_text(encoding="utf-8")
    assert "Expanded Compendium" in content


def test_notes_with_llm_adapter(tmp_path: Path):
    """Verify cresmo_notes extracts JSON atomic notes via LLMTransformationPort."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = enriched_dir / "vid_notes.md"
    enriched_file.write_text(
        "## Enriched Topic\n" + "Valid enriched content.\n" * 30 + "\n## Informações Complementares\nDetails.",
        encoding="utf-8",
    )

    canned_json = json.dumps([
        {
            "title": "Geopolítica de Recursos Hídricos",
            "type": "concept",
            "domain": "geopolitics",
            "cluster": "infrastructure",
            "definition": "Análise das rotas fluviais e bacias hidrográficas estratégicas.",
            "direct_quote": "A água molda as fronteiras naturais.",
            "cresmo_synthesis": "Síntese dos impactos geopolíticos.",
        }
    ])
    # Wrap in markdown codeblock as LLMs often do
    canned_response = f"```json\n{canned_json}\n```"
    adapter = MockLLMAdapter(canned_response=canned_response)

    meta = {"channel_name": "TestChannel", "video_id": "vid_notes"}
    json_file, is_new = cresmo_pipeline.cresmo_notes(
        enriched_file=enriched_file,
        meta=meta,
        llm=adapter,
        force=True,
    )

    assert is_new is True
    assert json_file.exists()
    assert len(adapter.call_history) == 2  # 1 inventory discovery + 1 batch synthesis
    assert all(c["temperature"] == 0.0 for c in adapter.call_history)
    loaded_data = json.loads(json_file.read_text(encoding="utf-8"))
    loaded_notes = loaded_data["notes"] if isinstance(loaded_data, dict) else loaded_data
    assert len(loaded_notes) == 1
    assert loaded_notes[0]["title"] == "Geopolítica de Recursos Hídricos"


def test_moc_manager_with_llm_adapter(tmp_path: Path):
    """Verify cresmo_moc_manager generates reconciliation log via LLMTransformationPort."""
    enriched_dir = tmp_path / "enriched" / "TestChannel"
    enriched_dir.mkdir(parents=True, exist_ok=True)
    json_file = enriched_dir / "vid_moc.json"
    json_file.write_text('[{"title": "Test", "type": "concept", "definition": "Desc"}]', encoding="utf-8")

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    (wiki_dir / "_index.json").write_text('{"notes": {}}', encoding="utf-8")

    adapter = MockLLMAdapter(canned_response="Reconciliation completed successfully.")

    meta = {"channel_name": "TestChannel", "video_id": "vid_moc"}
    rec_log = cresmo_pipeline.cresmo_moc_manager(
        json_file=json_file,
        meta=meta,
        llm=adapter,
        cresmo_wiki_dir=wiki_dir,
        force=True,
    )

    assert rec_log.exists()
    assert len(adapter.call_history) == 1
    assert "Cresmo MOC Reconciliation Report" in rec_log.read_text(encoding="utf-8")
