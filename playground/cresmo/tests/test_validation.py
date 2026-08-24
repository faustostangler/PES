"""Unit tests for Cresmo stage completion validators and multi-pass checks."""

from pathlib import Path
import pytest

from cresmo_pipeline import (
    is_valid_atomic_xml,
    is_valid_enriched_markdown,
    is_valid_reconciliation_log,
)


def test_is_valid_enriched_markdown_valid(tmp_path: Path):
    """Verify is_valid_enriched_markdown returns True for structurally sound markdown."""
    f = tmp_path / "valid.md"
    content = """---
video_title: "Test Video"
video_id: "12345"
---

## Geopolítica de Infraestrutura

Texto contínuo da análise macroeconômica sem listas ou tabelas.
Apresenta densidade conceitual e fatos históricos empíricos verificáveis.

## Informações Complementares

1. O Porto de Mariel constitui um polo logístico regional.
2. O BNDES operou linhas de financiamento para bens de engenharia.
"""
    f.write_text(content, encoding="utf-8")
    assert is_valid_enriched_markdown(f, min_bytes=100) is True


def test_is_valid_enriched_markdown_missing_complementary(tmp_path: Path):
    """Verify is_valid_enriched_markdown returns False if complementary info section is missing."""
    f = tmp_path / "incomplete.md"
    content = """---
video_title: "Test Video"
---

## Geopolítica de Infraestrutura

Texto contínuo sem a seção final obrigatória de informações complementares.
"""
    f.write_text(content, encoding="utf-8")
    assert is_valid_enriched_markdown(f, min_bytes=50) is False


def test_is_valid_enriched_markdown_too_short(tmp_path: Path):
    """Verify is_valid_enriched_markdown returns False if size is below minimum threshold."""
    f = tmp_path / "short.md"
    f.write_text("## Intro\n## Informações Complementares\n", encoding="utf-8")
    assert is_valid_enriched_markdown(f, min_bytes=300) is False


def test_is_valid_atomic_xml_valid(tmp_path: Path):
    """Verify is_valid_atomic_xml returns True for valid XML containing note blocks."""
    f = tmp_path / "valid.xml"
    content = """<xml>
<notas>
<nota>
# [Nota 1]
Conteúdo detalhado.
</nota>
</notas>
</xml>
"""
    f.write_text(content, encoding="utf-8")
    assert is_valid_atomic_xml(f, min_bytes=50) is True


def test_is_valid_atomic_xml_invalid(tmp_path: Path):
    """Verify is_valid_atomic_xml returns False for malformed XML without note markers."""
    f = tmp_path / "invalid.xml"
    f.write_text("Some text without xml or nota tags", encoding="utf-8")
    assert is_valid_atomic_xml(f, min_bytes=10) is False


def test_is_valid_reconciliation_log(tmp_path: Path):
    """Verify is_valid_reconciliation_log checks existence and minimum size."""
    f = tmp_path / "reconciliation.md"
    f.write_text("# Report\n\n- All notes integrated successfully.", encoding="utf-8")
    assert is_valid_reconciliation_log(f, min_bytes=20) is True
    assert is_valid_reconciliation_log(f, min_bytes=500) is False
