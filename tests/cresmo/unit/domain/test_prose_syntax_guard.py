"""Unit tests for Fluid Prose and Gap Filler Syntax Guard.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: Section 2.1 (prose_syntax_guard)
"""

from __future__ import annotations

from cresmo.domain.services.prose_syntax_guard import (
    extract_extra_info_section,
    validate_expanded_prose_syntax,
    validate_fluid_prose_syntax,
)


def test_empty_or_whitespace_text_fails_fast() -> None:
    assert validate_fluid_prose_syntax("") == ["Text is empty or whitespace."]
    assert validate_fluid_prose_syntax("   \n\t  ") == ["Text is empty or whitespace."]


def test_valid_fluid_prose_passes_syntax_validation() -> None:
    valid_text = (
        "## The Emergence of Financial Institutions\n\n"
        "In the seventeenth century, the earliest stock exchanges consolidated in Amsterdam. "
        "Liquidity dynamics established new horizons for maritime trade, "
        "enabling efficient capital allocation across multiple investors.\n\n"
        "### The Emergence of the Secondary Market\n\n"
        "The tradability of equity stakes lowered the liquidity cost of enterprises."
    )
    violations = validate_fluid_prose_syntax(valid_text)
    assert violations == []


def test_line_1_heading_contract_boundaries() -> None:
    # 1. H1 failure
    h1_text = "# Invalid H1 Title\n\nProse body."
    assert validate_fluid_prose_syntax(h1_text) == [
        "Line 1 must start with '## ' (found: '# Invalid H1 Title...')"
    ]

    # 2. H3 failure
    h3_text = "### Invalid H3 Title\n\nProse body."
    assert validate_fluid_prose_syntax(h3_text) == [
        "Line 1 must start with '## ' (found: '### Invalid H3 Title...')"
    ]

    # 3. Missing trailing space after '##'
    no_space_text = "##TitleWithoutSpace\n\nProse body."
    assert validate_fluid_prose_syntax(no_space_text) == [
        "Line 1 must start with '## ' (found: '##TitleWithoutSpace...')"
    ]

    # 4. Truncation at 40 characters
    long_title = "X" * 50
    assert validate_fluid_prose_syntax(f"{long_title}\n\nBody.") == [
        f"Line 1 must start with '## ' (found: '{'X' * 40}...')"
    ]


def test_yaml_frontmatter_boundaries() -> None:
    # Delimiter on separate line in body
    text_1 = "## Text Start\n\nProse content.\n---\nOther content."
    assert validate_fluid_prose_syntax(text_1) == [
        "Text must contain zero YAML frontmatter delimiters ('---')."
    ]

    # Trailing whitespace on delimiter line
    text_2 = "## Text Start\n\nProse content.\n---   \nOther content."
    assert validate_fluid_prose_syntax(text_2) == [
        "Text must contain zero YAML frontmatter delimiters ('---')."
    ]

    # Hyphens within normal words are permitted
    text_3 = "## Text Start\n\nThe post-structuralist and pre-modern debate continued."
    assert validate_fluid_prose_syntax(text_3) == []


def test_em_dash_contract() -> None:
    invalid_text = (
        "## Historical Structure\n\n"
        "The government decision — made without public consultation — sparked a strong reaction."
    )
    assert validate_fluid_prose_syntax(invalid_text) == [
        "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
    ]

    # Hyphen and en-dash do not trigger em-dash violation
    valid_text = "## Historical Structure\n\nPeriod from 1914–1918 and cost-benefit relationship."
    assert validate_fluid_prose_syntax(valid_text) == []


def test_bullet_list_markers() -> None:
    # Asterisk bullet
    text_asterisk = "## Synthesis\n\n* Item A\n* Item B"
    assert validate_fluid_prose_syntax(text_asterisk) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Hyphen bullet
    text_hyphen = "## Synthesis\n\n- Item A\n- Item B"
    assert validate_fluid_prose_syntax(text_hyphen) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Plus bullet
    text_plus = "## Synthesis\n\n+ Item A\n+ Item B"
    assert validate_fluid_prose_syntax(text_plus) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Indented bullet
    text_indented = "## Synthesis\n\n   * Indented item"
    assert validate_fluid_prose_syntax(text_indented) == [
        "Text must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    # Negative test: math operators and inline symbols do not trigger bullet violations
    text_math = "## Calculation\n\nValue of +5 and -10 in the final result."
    assert validate_fluid_prose_syntax(text_math) == []


def test_markdown_tables_contract() -> None:
    # Standard pipe table row
    text_pipe = "## Table\n\n| Column A | Column B |\n| 1 | 2 |"
    assert validate_fluid_prose_syntax(text_pipe) == [
        "Text must contain zero markdown table markers ('|')."
    ]

    # Delimiter row marker
    text_delimiter = "## Table\n\nHeader | Header\n---|---\nData | Data"
    assert validate_fluid_prose_syntax(text_delimiter) == [
        "Text must contain zero markdown table markers ('|')."
    ]

    # Negative test: single inline pipe in prose without table markers
    text_pipe_inline = "## Prose\n\nOption A | Option B as a disjunctive alternative."
    assert validate_fluid_prose_syntax(text_pipe_inline) == []


def test_blockquotes_contract() -> None:
    # Standard blockquote
    text_quote = "## Analysis\n\n> Direct block quotation."
    assert validate_fluid_prose_syntax(text_quote) == ["Text must contain zero blockquotes ('>')."]

    # Indented blockquote
    text_indented_quote = "## Analysis\n\n  > Indented quotation."
    assert validate_fluid_prose_syntax(text_indented_quote) == [
        "Text must contain zero blockquotes ('>')."
    ]

    # Negative test: greater-than comparison in prose
    text_gt = "## Comparison\n\nThe value of X > Y indicates economic convergence."
    assert validate_fluid_prose_syntax(text_gt) == []


def test_paragraph_segmentation_boundaries() -> None:
    # Exactly 80 words in 1 paragraph -> PASS
    p80 = " ".join([f"word{i}" for i in range(80)])
    text_80 = f"## Title\n\n{p80}"
    assert validate_fluid_prose_syntax(text_80) == []

    # Exactly 81 words in 1 paragraph -> MONOLITHIC WALL OF TEXT VIOLATION
    p81 = " ".join([f"word{i}" for i in range(81)])
    text_81 = f"## Title\n\n{p81}"
    assert validate_fluid_prose_syntax(text_81) == [
        "Text must contain distinct paragraphs separated by blank lines (monolithic wall of text detected)."
    ]

    # 100 words split across two paragraphs -> PASS
    p50_a = " ".join([f"word{i}" for i in range(50)])
    p50_b = " ".join([f"term{i}" for i in range(50)])
    text_split = f"## Title\n\n{p50_a}\n\n{p50_b}"
    assert validate_fluid_prose_syntax(text_split) == []

    # Headings do not count towards single-body paragraph wall of text
    text_headings_only = "## Main Title\n\n### Subtitle A\n\n### Subtitle B"
    assert validate_fluid_prose_syntax(text_headings_only) == []


def test_multiple_simultaneous_violations() -> None:
    invalid_text = (
        "# H1 Title\n\n"
        "---\n\n"
        "Narrative with em-dash — forbidden.\n\n"
        "* Bullet item\n\n"
        "> Blockquote line\n\n"
        "| Column A | Column B |"
    )
    violations = validate_fluid_prose_syntax(invalid_text)
    assert len(violations) == 6
    assert violations[0].startswith("Line 1 must start with '## '")
    assert "YAML frontmatter" in violations[1]
    assert "em-dashes" in violations[2]
    assert "bullet points" in violations[3]
    assert "table markers" in violations[4]
    assert "blockquotes" in violations[5]


def test_extract_extra_info_section() -> None:
    text_with = (
        "## Main Body\n\nAnalytical prose text.\n\n"
        "### Extra Info\n\n1. First detail.\n\n2. Second detail."
    )
    assert extract_extra_info_section(text_with) == "1. First detail.\n\n2. Second detail."
    assert extract_extra_info_section("## Body Only\n\nNo extra info section.") == ""


def test_validate_expanded_prose_syntax() -> None:
    valid_expanded = (
        "## Main Title\n\n"
        "Introductory paragraph about the subject without lists or tables.\n\n"
        "### Extra Info\n\n"
        "1. Numbered contextual detail.\n\n"
        "2. Second detail referencing **Entity**."
    )
    assert validate_expanded_prose_syntax(valid_expanded) == []

    # Missing mandatory Extra Info section
    missing_comp = "## Main Title\n\nSingle paragraph."
    assert validate_expanded_prose_syntax(missing_comp) == [
        "Missing mandatory complementary section '### Extra Info'."
    ]

    # Missing Extra Info with forbidden main-body bullet
    missing_with_bullet = "## Main Title\n\n* Bullet without extra info."
    assert validate_expanded_prose_syntax(missing_with_bullet) == [
        "Missing mandatory complementary section '### Extra Info'.",
        "Main body must contain zero bullet points or list markers ('*', '-', '+').",
    ]

    # Empty or whitespace text
    assert validate_expanded_prose_syntax("") == ["Text is empty or whitespace."]
    assert validate_expanded_prose_syntax("   \n\t ") == ["Text is empty or whitespace."]

    # Em-dash violation
    em_dash_text = valid_expanded + " — with forbidden em-dash."
    assert validate_expanded_prose_syntax(em_dash_text) == [
        "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
    ]

    # Empty Extra Info section
    empty_extra_info = "## Main Title\n\nValid body paragraph.\n\n### Extra Info\n\n   "
    assert validate_expanded_prose_syntax(empty_extra_info) == [
        "Section '### Extra Info' is empty."
    ]

    # Main body violations (table, bullet, blockquote)
    table_in_body = "## Main Title\n\n| Col A | Col B |\n\n### Extra Info\n\n1. Detail."
    assert validate_expanded_prose_syntax(table_in_body) == [
        "Main body must contain zero markdown table markers ('|')."
    ]

    bullet_in_body = "## Main Title\n\n- Bullet item\n\n### Extra Info\n\n1. Detail."
    assert validate_expanded_prose_syntax(bullet_in_body) == [
        "Main body must contain zero bullet points or list markers ('*', '-', '+')."
    ]

    quote_in_body = "## Main Title\n\n> Quoted line\n\n### Extra Info\n\n1. Detail."
    assert validate_expanded_prose_syntax(quote_in_body) == [
        "Main body must contain zero blockquotes ('>')."
    ]

    # Bullet list inside Extra Info section
    bullet_in_extra = "## Main Title\n\nValid body paragraph.\n\n### Extra Info\n\n* Bullet detail."
    assert validate_expanded_prose_syntax(bullet_in_extra) == [
        (
            "Complementary section must contain zero bullet points or list markers ('*', '-', '+'). "
            "Use numbered continuous paragraphs ('1. ', '2. ')."
        )
    ]

    # Empty main body before Extra Info
    empty_main_body = "### Extra Info\n\n1. Orphan detail."
    assert validate_expanded_prose_syntax(empty_main_body) == [
        "Line 1 must start with '## ' (found: '### Extra Info...')",
        "Main body text before '### Extra Info' is empty.",
    ]
