"""Unit tests for Fluid Prose Mechanical Invariant Validator.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

from cresmo.domain.services.mechanical_validator import (
    validate_fluid_prose_mechanical_invariants,
)


def test_empty_or_whitespace_text_fails_fast() -> None:
    assert validate_fluid_prose_mechanical_invariants("") == ["Text is empty or whitespace."]
    assert validate_fluid_prose_mechanical_invariants("   \n\t  ") == [
        "Text is empty or whitespace."
    ]


def test_valid_fluid_prose_passes_mechanical_validation() -> None:
    valid_text = (
        "## O Surgimento das Instituições Financeiras\n\n"
        "No século 17, as primeiras bolsas de valores consolidaram-se em Amsterdã. "
        "A dinâmica de liquidez estabeleceu novos horizontes para o comércio marítimo, "
        "permitindo alocação eficiente de capital entre múltiplos investidores.\n\n"
        "### A Emergência do Mercado Secundário\n\n"
        "A negociabilidade de participações acionárias reduziu o custo de liquidez das empresas."
    )
    violations = validate_fluid_prose_mechanical_invariants(valid_text)
    assert violations == []


def test_line_1_heading_contract_boundaries() -> None:
    # 1. H1 failure
    h1_text = "# Título H1 Inválido\n\nCorpo em prosa."
    assert validate_fluid_prose_mechanical_invariants(h1_text) == [
        "Line 1 must start with '## ' (found: '# Título H1 Inválido...')"
    ]

    # 2. H3 failure
    h3_text = "### Título H3 Inválido\n\nCorpo em prosa."
    assert validate_fluid_prose_mechanical_invariants(h3_text) == [
        "Line 1 must start with '## ' (found: '### Título H3 Inválido...')"
    ]

    # 3. Missing trailing space after '##'
    no_space_text = "##Título Sem Espaço\n\nCorpo em prosa."
    assert validate_fluid_prose_mechanical_invariants(no_space_text) == [
        "Line 1 must start with '## ' (found: '##Título Sem Espaço...')"
    ]

    # 4. Truncation at 40 characters
    long_title = "X" * 50
    assert validate_fluid_prose_mechanical_invariants(f"{long_title}\n\nCorpo.") == [
        f"Line 1 must start with '## ' (found: '{'X' * 40}...')"
    ]


def test_yaml_frontmatter_boundaries() -> None:
    # Delimiter on separate line in body
    text_1 = "## Início do Texto\n\nConteúdo em prosa.\n---\nOutro conteúdo."
    assert validate_fluid_prose_mechanical_invariants(text_1) == [
        "Text must contain zero YAML frontmatter delimiters ('---')."
    ]

    # Trailing whitespace on delimiter line
    text_2 = "## Início do Texto\n\nConteúdo em prosa.\n---   \nOutro conteúdo."
    assert validate_fluid_prose_mechanical_invariants(text_2) == [
        "Text must contain zero YAML frontmatter delimiters ('---')."
    ]

    # Hyphens within normal sentence are permitted
    text_3 = "## Início do Texto\n\nO debate pós-estruturalista e pré-moderno continuou."
    assert validate_fluid_prose_mechanical_invariants(text_3) == []


def test_em_dash_contract() -> None:
    invalid_text = (
        "## Estrutura Histórica\n\n"
        "A decisão do governo — tomada sem consulta pública — gerou forte reação."
    )
    assert validate_fluid_prose_mechanical_invariants(invalid_text) == [
        "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
    ]

    # Hyphen and en-dash do not trigger em-dash error
    valid_text = "## Estrutura Histórica\n\nPeríodo de 1914–1918 e relação custo-benefício."
    assert validate_fluid_prose_mechanical_invariants(valid_text) == []


def test_bullet_list_markers() -> None:
    # Asterisk bullet
    text_asterisk = "## Síntese\n\n* Item A\n* Item B"
    assert validate_fluid_prose_mechanical_invariants(text_asterisk) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Hyphen bullet
    text_hyphen = "## Síntese\n\n- Item A\n- Item B"
    assert validate_fluid_prose_mechanical_invariants(text_hyphen) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Plus bullet
    text_plus = "## Síntese\n\n+ Item A\n+ Item B"
    assert validate_fluid_prose_mechanical_invariants(text_plus) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Indented bullet
    text_indented = "## Síntese\n\n   * Item indentado"
    assert validate_fluid_prose_mechanical_invariants(text_indented) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Negative test: math operators and inline symbols do not trigger bullet violations
    text_math = "## Cálculo\n\nValor de +5 e -10 no resultado final."
    assert validate_fluid_prose_mechanical_invariants(text_math) == []


def test_markdown_tables_contract() -> None:
    # Standard pipe table row
    text_pipe = "## Tabela\n\n| Coluna A | Coluna B |\n| 1 | 2 |"
    assert validate_fluid_prose_mechanical_invariants(text_pipe) == [
        "Text must contain zero markdown table markers ('|')."
    ]

    # Delimiter row marker
    text_delimiter = "## Tabela\n\nHeader | Header\n---|---\nData | Data"
    assert validate_fluid_prose_mechanical_invariants(text_delimiter) == [
        "Text must contain zero markdown table markers ('|')."
    ]

    # Negative test: single pipe inside prose without table markers
    text_pipe_inline = "## Prosa\n\nOpção A | Opção B como alternativa disjuntiva."
    assert validate_fluid_prose_mechanical_invariants(text_pipe_inline) == []


def test_blockquotes_contract() -> None:
    # Standard blockquote
    text_quote = "## Análise\n\n> Citação direta em bloco."
    assert validate_fluid_prose_mechanical_invariants(text_quote) == [
        "Text must contain zero blockquotes ('>')."
    ]

    # Indented blockquote
    text_indented_quote = "## Análise\n\n  > Citação indentada."
    assert validate_fluid_prose_mechanical_invariants(text_indented_quote) == [
        "Text must contain zero blockquotes ('>')."
    ]

    # Negative test: greater-than comparison in prose
    text_gt = "## Comparação\n\nO valor de X > Y indica convergência econômica."
    assert validate_fluid_prose_mechanical_invariants(text_gt) == []


def test_paragraph_segmentation_boundaries() -> None:
    # Exactly 80 words in 1 paragraph -> PASS
    p80 = " ".join([f"palavra{i}" for i in range(80)])
    text_80 = f"## Título\n\n{p80}"
    assert validate_fluid_prose_mechanical_invariants(text_80) == []

    # Exactly 81 words in 1 paragraph -> MONOLITHIC WALL OF TEXT VIOLATION
    p81 = " ".join([f"palavra{i}" for i in range(81)])
    text_81 = f"## Título\n\n{p81}"
    assert validate_fluid_prose_mechanical_invariants(text_81) == [
        "Text must contain distinct paragraphs separated by blank lines (monolithic wall of text detected)."
    ]

    # 100 words split across two paragraphs -> PASS
    p50_a = " ".join([f"palavra{i}" for i in range(50)])
    p50_b = " ".join([f"termo{i}" for i in range(50)])
    text_split = f"## Título\n\n{p50_a}\n\n{p50_b}"
    assert validate_fluid_prose_mechanical_invariants(text_split) == []

    # Headings do not count towards single-body paragraph wall of text
    text_headings_only = "## Título Principal\n\n### Subtítulo A\n\n### Subtítulo B"
    assert validate_fluid_prose_mechanical_invariants(text_headings_only) == []


def test_multiple_simultaneous_violations() -> None:
    invalid_text = (
        "# Título H1\n\n"
        "---\n\n"
        "Narrativa com em-dash — proibido.\n\n"
        "* Item com bullet\n\n"
        "> Citação em bloco\n\n"
        "| Coluna A | Coluna B |"
    )
    violations = validate_fluid_prose_mechanical_invariants(invalid_text)
    assert len(violations) == 6
    assert violations[0].startswith("Line 1 must start with '## '")
    assert "YAML frontmatter" in violations[1]
    assert "em-dashes" in violations[2]
    assert "bullet points" in violations[3]
    assert "table markers" in violations[4]
    assert "blockquotes" in violations[5]
