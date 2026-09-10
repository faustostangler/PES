"""Unit tests for Cresmo JSON atomic notes, Pydantic models, and markdown rendering."""

import json
from pathlib import Path
import sys
import pytest

# Ensure playground/cresmo is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cresmo_pipeline import (
    AtomicNoteModel,
    CausalMatrixModel,
    CrossContextModel,
    extract_json_payload,
    is_valid_atomic_json,
    parse_and_proliferate_notes,
)


def test_atomic_note_model_structured_rendering():
    """Verify AtomicNoteModel renders structured attributes to markdown compliant with cresmo format."""
    note = AtomicNoteModel(
        title="Guimarães",
        type="entity",
        content=["geografia", "geografia/centro_urbano"],
        domain="geografia_historica",
        cluster="centros_de_poder_medieval",
        source="marcelo-andrade/9IbNJ0EsTxI",
        aliases=["Berço da Nação", "Vila de Guimarães"],
        definition="Guimarães constituiu o centro administrativo original do Condado Portucalense.",
        direct_relations=[
            "[[Guimarães]] -> abrigou a corte de -> [[Henrique de Borgonha]]",
            "[[Guimarães]] -> testemunhou a insurreição de -> [[1128-06-24 Batalha de São Mamede]]",
        ],
        causal_matrix=CausalMatrixModel(
            cause="Fundação do mosteiro e da fortaleza defensiva por Mumadona Dias.",
            effect="Fixação do centro de gravidade político do Condado Portucalense.",
            epistemic_attribution="Documentos cartorários medievais.",
        ),
        cross_context=CrossContextModel(
            precursors="Origem ancorada na fortificação condal do século X.",
            lateral_events="Articulação defensiva contemporânea com [[Braga]].",
            aftermath="Perda da condição de capital administrativa com [[1131 Transferência da Capital para Coimbra]].",
        ),
    )

    md = note.to_markdown()

    assert "type: entity" in md
    assert "- geografia" in md
    assert "- geografia/centro_urbano" in md
    assert "domain: geografia_historica" in md
    assert "cluster: centros_de_poder_medieval" in md
    assert "source: marcelo-andrade/9IbNJ0EsTxI" in md
    assert '"Berço da Nação"' in md
    assert "# Guimarães" in md
    assert "## Definição e Análise Contextual" in md
    assert "Guimarães constituiu o centro administrativo" in md
    assert "## Conexões e Relações Diretas" in md
    assert "* [[Guimarães]] -> abrigou a corte" in md
    assert "## Matriz Causal e Atribuição Epistêmica" in md
    assert "* **Causa / Premissa:** Fundação do mosteiro" in md
    assert "* **Efeito / Impacto:** Fixação do centro" in md
    assert "* **Atribuição Epistêmica:** Documentos cartorários" in md
    assert "## Redes de Conexão e Contexto Cruzado" in md
    assert "* **Precursores e Ancestralidade:** Origem ancorada" in md
    assert "* **Eventos Laterais e Paralelos:** Articulação defensiva" in md
    assert "* **Desdobramentos e Posteridade:** Perda da condição" in md


def test_atomic_note_model_with_portuguese_keys():
    """Verify AtomicNoteModel accepts Portuguese field names transparently."""
    raw_data = {
        "title": "Afonso Henriques",
        "type": "entity",
        "definicao": "Primeiro rei de Portugal.",
        "conexoes": ["[[Afonso Henriques]] -> filho de -> [[Henrique de Borgonha]]"],
        "matriz_causal": {
            "causa": "Revolta contra Teresa de Leão.",
            "efeito": "Independência política de Portugal.",
            "atribuicao_epistemica": "Crônica dos Godos.",
        },
        "redes_conexao": {
            "precursores": "Tradição dinástica da Borgonha.",
            "eventos_laterais": "Conflito com o Reino de Leão.",
            "desdobramentos": "Fundação da Monarquia Portuguesa.",
        },
    }

    note = AtomicNoteModel.model_validate(raw_data)
    assert note.title == "Afonso Henriques"
    assert note.definition == "Primeiro rei de Portugal."
    assert len(note.direct_relations) == 1
    assert note.causal_matrix is not None
    assert note.causal_matrix.cause == "Revolta contra Teresa de Leão."
    assert note.cross_context is not None
    assert note.cross_context.precursors == "Tradição dinástica da Borgonha."

    md = note.to_markdown()
    assert "# Afonso Henriques" in md
    assert "Primeiro rei de Portugal." in md
    assert "* **Causa / Premissa:** Revolta contra Teresa de Leão." in md


def test_atomic_note_model_raw_markdown_override():
    """Verify AtomicNoteModel respects raw markdown if directly provided."""
    raw_markdown = """---
type: concept
aliases: ["Feudalismo Ibérico"]
---
# Feudalismo Ibérico

## Definição e Análise Contextual
Sistema senhorial diferenciado na Península Ibérica.
"""
    note = AtomicNoteModel(
        title="Feudalismo Ibérico",
        type="concept",
        markdown=raw_markdown,
    )

    md = note.to_markdown()
    assert "# Feudalismo Ibérico" in md
    assert "type: concept" in md
    assert "Sistema senhorial diferenciado" in md


def test_is_valid_atomic_json_scenarios(tmp_path: Path):
    """Test various valid and invalid atomic JSON files."""
    valid_file = tmp_path / "valid.json"
    valid_data = [
        {
            "title": "Condado Portucalense",
            "type": "entity",
            "definition": "Entidade territorial medieval autônoma sob a coroa de Leão.",
            "direct_relations": ["[[Condado Portucalense]] -> concedido a -> [[Henrique de Borgonha]]"],
        }
    ]
    valid_file.write_text(json.dumps(valid_data, indent=2), encoding="utf-8")
    assert is_valid_atomic_json(valid_file, min_bytes=50) is True

    # Empty array should be invalid
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]", encoding="utf-8")
    assert is_valid_atomic_json(empty_file, min_bytes=2) is False

    # Malformed JSON should be invalid
    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("[{title: no quotes}]", encoding="utf-8")
    assert is_valid_atomic_json(corrupt_file, min_bytes=10) is False

    # Missing file
    assert is_valid_atomic_json(tmp_path / "non_existent.json") is False


def test_parse_and_proliferate_json(tmp_path: Path):
    """Verify parse_and_proliferate_notes creates .md notes and updates _index.json from JSON."""
    json_file = tmp_path / "test_notes.json"
    notes_data = [
        {
            "title": "Batalha de São Mamede",
            "type": "event",
            "aliases": ["São Mamede 1128"],
            "definition": "Batalha decisiva de afirmação do poder de Afonso Henriques.",
            "direct_relations": ["[[Batalha de São Mamede]] -> consolidou a liderança de -> [[Afonso Henriques]]"],
        }
    ]
    json_file.write_text(json.dumps(notes_data, indent=2), encoding="utf-8")

    wiki_dir = tmp_path / "wiki"
    created = parse_and_proliferate_notes(json_file, cresmo_wiki_dir=wiki_dir, force=False)

    assert len(created) == 1
    event_file = wiki_dir / "event" / "Batalha de São Mamede.md"
    assert event_file.exists()
    content = event_file.read_text(encoding="utf-8")
    assert "type: event" in content
    assert "# Batalha de São Mamede" in content
    assert "Batalha decisiva" in content

    # Check _index.json
    index_file = wiki_dir / "_index.json"
    assert index_file.exists()
    index_data = json.loads(index_file.read_text(encoding="utf-8"))
    assert "Batalha de São Mamede" in index_data["notes"]
    assert index_data["notes"]["Batalha de São Mamede"]["type"] == "event"
    assert "São Mamede 1128" in index_data["notes"]["Batalha de São Mamede"]["aliases"]


def test_extract_json_payload_salvages_truncated_array():
    """Verify extract_json_payload rescues complete notes when LLM output is truncated mid-generation."""
    truncated = (
        "```json\n"
        "[\n"
        '  {"title": "Note 1", "type": "concept", "definition": "Desc 1"},\n'
        '  {"title": "Note 2", "type": "entity", "definition": "Desc 2"},\n'
        '  {"title": "Note 3", "type": "event", "definition": "Truncated mid-sent'
    )
    result = extract_json_payload(truncated)
    assert result is not None
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"
    assert data[1]["title"] == "Note 2"


def test_extract_json_payload_salvages_user_real_scenario():
    """Verify regression scenario where Gemini hit output token limit mid-definition of 10th note."""
    truncated_user_snippet = (
        '```json\n'
        '[\n'
        '  {"title": "Corredor de Rendas", "type": "concept", "definition": "O Corredor de Rendas delineia..."},\n'
        '  {"title": "Fronteira de Conveniência", "type": "concept", "definition": "A Fronteira..."},\n'
        '  {"title": "Patrimonialismo", "type": "concept", "definition": "Conceito sociológico..."},\n'
        '  {"title": "Brasil", "type": "entity", "definition": "Entidade geopolítica..."},\n'
        '  {"title": "Luso-brasileira", "type": "concept", "definition": "Termo que descreve..."},\n'
        '  {"title": "1383-1385 Crise Dinástica Portuguesa", "type": "event", "definition": "Período..."},\n'
        '  {"title": "Fernando I de Portugal", "type": "entity", "definition": "Último monarca..."},\n'
        '  {"title": "1383-10-22 Morte de Fernando I de Portugal", "type": "event", "definition": "Evento..."},\n'
        '  {"title": "Dinastia de Borgonha", "type": "entity", "definition": "Linhagem real..."},\n'
        '  {"title": "João I de Castela", "type": "entity", "definition": "Monarca da [[Coroa de Castela]] que, casado com [[Beatriz de Portugal]], filha de [[Fernando I de Portugal]], reivindicou o trono português após a morte de seu sogro em 1383. Sua pretensão representou uma ameaça existencial à independência de [[Portugal]], culminando na [[1383-1385 Crise Dinástica Portuguesa]] e na [[1385-08-14 Batalha de Aljubarrota]], onde suas forças foram derrotadas. A união dinástica implicaria a absorção do reino português'
    )
    result = extract_json_payload(truncated_user_snippet)
    assert result is not None
    notes = json.loads(result)
    assert len(notes) == 9
    assert notes[0]["title"] == "Corredor de Rendas"
    assert notes[8]["title"] == "Dinastia de Borgonha"


