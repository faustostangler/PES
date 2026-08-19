"""Unit tests for Cresmo XML parsing, non-destructive note proliferation, and cache guards."""

import json
from pathlib import Path
import pytest

from cresmo_pipeline import parse_and_proliferate_xml_notes


SAMPLE_XML_CONTENT = """
<xml>
<nota>
---
type: concept
aliases:
  - "Conceito Teste"
---
# [Conceito de Teste]

Texto explicativo inicial do conceito.
</nota>
</xml>
"""


def test_parse_and_proliferate_creates_new_note(tmp_path: Path):
    """Verify parse_and_proliferate_xml_notes creates a new .md note if it does not exist."""
    xml_file = tmp_path / "video_test.xml"
    xml_file.write_text(SAMPLE_XML_CONTENT, encoding="utf-8")

    wiki_dir = tmp_path / "wiki"
    created = parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=wiki_dir, force=False)

    assert len(created) == 1
    expected_note = wiki_dir / "concept" / "Conceito de Teste.md"
    assert expected_note.exists()
    assert "Texto explicativo inicial" in expected_note.read_text(encoding="utf-8")

    # Check _index.json
    index_file = wiki_dir / "_index.json"
    assert index_file.exists()
    index_data = json.loads(index_file.read_text(encoding="utf-8"))
    assert "Conceito de Teste" in index_data["notes"]


def test_parse_and_proliferate_preserves_existing_note_without_force(tmp_path: Path):
    """Verify parse_and_proliferate_xml_notes does NOT overwrite an existing enriched vault note when force=False."""
    wiki_dir = tmp_path / "wiki"
    concept_dir = wiki_dir / "concept"
    concept_dir.mkdir(parents=True, exist_ok=True)

    note_file = concept_dir / "Conceito de Teste.md"
    enriched_historical_content = "# [Conceito de Teste]\n\nConteúdo enriquecido pelo MOC Manager com [[Backlink]]!"
    note_file.write_text(enriched_historical_content, encoding="utf-8")

    xml_file = tmp_path / "video_test.xml"
    xml_file.write_text(SAMPLE_XML_CONTENT, encoding="utf-8")

    # Proliferate with force=False
    created = parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=wiki_dir, force=False)

    # Must NOT count as a newly created file and must NOT overwrite
    assert len(created) == 0
    assert note_file.read_text(encoding="utf-8") == enriched_historical_content


def test_parse_and_proliferate_overwrites_when_force_is_true(tmp_path: Path):
    """Verify parse_and_proliferate_xml_notes overwrites existing notes when force=True."""
    wiki_dir = tmp_path / "wiki"
    concept_dir = wiki_dir / "concept"
    concept_dir.mkdir(parents=True, exist_ok=True)

    note_file = concept_dir / "Conceito de Teste.md"
    note_file.write_text("Old content", encoding="utf-8")

    xml_file = tmp_path / "video_test.xml"
    xml_file.write_text(SAMPLE_XML_CONTENT, encoding="utf-8")

    # Proliferate with force=True
    created = parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=wiki_dir, force=True)

    assert len(created) == 1
    assert "Texto explicativo inicial" in note_file.read_text(encoding="utf-8")
