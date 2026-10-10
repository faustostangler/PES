"""Unit tests for Fluid Prose Mechanical Invariant Validator.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

import pytest

from cresmo.domain.services.mechanical_validator import (
    validate_fluid_prose_mechanical_invariants,
)


def test_valid_fluid_prose_passes_mechanical_validation() -> None:
    valid_text = (
        "## O Surgimento das Instituições Financeiras\n\n"
        "No século **17**, as primeiras bolsas de valores consolidaram-se em Amsterdã. "
        "A dinâmica de liquidez estabeleceu novos horizontes para o comércio marítimo, "
        "permitindo alocação eficiente de capital entre múltiplos investidores.\n\n"
        "### A Emergência do Mercado Secundário\n\n"
        "A negociabilidade de participações acionárias reduziu o custo de liquidez das empresas."
    )
    violations = validate_fluid_prose_mechanical_invariants(valid_text)
    assert violations == []


def test_fails_when_line_1_not_heading_2() -> None:
    invalid_text = (
        "# Título com H1 Não Permitido\n\n"
        "Texto em prosa sem divisão adequada."
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("Line 1 must start with '## '" in v for v in violations)


def test_fails_when_yaml_frontmatter_present() -> None:
    invalid_text = (
        "---\n"
        "title: Vídeo de Economia\n"
        "---\n\n"
        "## Início do Texto\n\n"
        "Conteúdo em prosa."
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("YAML frontmatter" in v for v in violations)


def test_fails_when_em_dash_present() -> None:
    invalid_text = (
        "## Estrutura Histórica\n\n"
        "A decisão do governo — tomada sem consulta pública — gerou forte reação."
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("em-dash" in v.lower() for v in violations)


def test_fails_when_bullet_lists_present() -> None:
    invalid_text = (
        "## Síntese de Fatores\n\n"
        "Os principais motores econômicos foram:\n"
        "* Crescimento da produção agrícola\n"
        "* Expansão das rotas marítimas\n"
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("bullet" in v.lower() for v in violations)


def test_fails_when_table_present() -> None:
    invalid_text = (
        "## Comércio e Preços\n\n"
        "| Produto | Preço |\n"
        "| Grãos | 10 |\n"
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("table" in v.lower() for v in violations)


def test_fails_when_blockquote_present() -> None:
    invalid_text = (
        "## Análise Documental\n\n"
        "> Esta citação em bloco é proibida pelas diretrizes do Cresmo.\n\n"
        "A narrativa segue normalmente."
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert any("blockquote" in v.lower() for v in violations)
