"""Mechanical invariant validation service for fluid prose compendia.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

import re

_BULLET_LINE_PATTERN = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_BLOCKQUOTE_LINE_PATTERN = re.compile(r"^\s*>", re.MULTILINE)
_TABLE_LINE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_YAML_DELIMITER_PATTERN = re.compile(r"^---\s*$", re.MULTILINE)


def validate_fluid_prose_mechanical_invariants(text: str) -> list[str]:
    """Validate deterministic mechanical and syntactic invariants of fluid prose text.

    Args:
        text: Candidate fluid prose markdown string.

    Returns:
        list[str]: Violations detected. An empty list denotes complete syntactic compliance.
    """
    violations: list[str] = []
    stripped = text.strip()

    if not stripped:
        return ["Text is empty or whitespace."]

    # 1. Line 1 Contract: Must begin with '## '
    first_line = stripped.splitlines()[0].strip()
    if not first_line.startswith("## "):
        violations.append(f"Line 1 must start with '## ' (found: '{first_line[:40]}...')")

    # 2. Zero YAML Frontmatter
    if _YAML_DELIMITER_PATTERN.search(stripped):
        violations.append("Text must contain zero YAML frontmatter delimiters ('---').")

    # 3. Zero Em-Dashes ('—')
    if "—" in stripped:
        violations.append(
            "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
        )

    # 4. Zero Bullet Points
    if _BULLET_LINE_PATTERN.search(stripped):
        violations.append("Text must contain zero bullet points or list markers ('*', '-', '+').")

    # 5. Zero Markdown Tables
    if _TABLE_LINE_PATTERN.search(stripped) or ("|" in stripped and "-|-" in stripped):
        violations.append("Text must contain zero markdown table markers ('|').")

    # 6. Zero Blockquotes
    if _BLOCKQUOTE_LINE_PATTERN.search(stripped):
        violations.append("Text must contain zero blockquotes ('>').")

    # 7. Paragraph Segmentation: Body must be structured into distinct paragraphs
    body_paragraphs = [
        p.strip() for p in stripped.split("\n\n") if p.strip() and not p.strip().startswith("##")
    ]
    if len(body_paragraphs) == 1 and len(body_paragraphs[0].split()) > 80:
        violations.append(
            "Text must contain distinct paragraphs separated by blank lines (monolithic wall of text detected)."
        )

    return violations


_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*##\s+Informações\s+Complementares\s*$",
    re.MULTILINE,
)
_BOLD_ENTITY_PATTERN = re.compile(r"\*\*([^*]+)\*\*")


def extract_complementary_section(text: str) -> str:
    """Extract text from the mandatory '## Informações Complementares' section."""
    match = _COMPLEMENTARY_REGEX.search(text)
    if not match:
        return ""
    return text[match.end() :].strip()


def validate_gap_filler_mechanical_invariants(text: str) -> list[str]:
    """Validate deterministic mechanical and syntactic invariants for gap_filler compendia.

    Args:
        text: Candidate gap_filler markdown text.

    Returns:
        list[str]: Violations detected. Empty list indicates full compliance.
    """
    violations: list[str] = []
    stripped = text.strip()

    if not stripped:
        return ["Text is empty or whitespace."]

    # 1. Line 1 Contract: Must begin with '## '
    first_line = stripped.splitlines()[0].strip()
    if not first_line.startswith("## "):
        violations.append(f"Line 1 must start with '## ' (found: '{first_line[:40]}...')")

    # 2. Zero YAML Frontmatter
    if _YAML_DELIMITER_PATTERN.search(stripped):
        violations.append("Text must contain zero YAML frontmatter delimiters ('---').")

    # 3. Zero Em-Dashes ('—')
    if "—" in stripped:
        violations.append(
            "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
        )

    # 4. Mandatory '## Informações Complementares' section
    comp_match = _COMPLEMENTARY_REGEX.search(stripped)
    if not comp_match:
        violations.append(
            "Missing mandatory complementary section '## Informações Complementares'."
        )
        main_body = stripped
        comp_section = ""
    else:
        main_body = stripped[: comp_match.start()].strip()
        comp_section = stripped[comp_match.end() :].strip()
        if not comp_section:
            violations.append("Section '## Informações Complementares' is empty.")
        if not main_body:
            violations.append("Main body text before '## Informações Complementares' is empty.")

    # 5. Zero Markdown Tables in main body
    if _TABLE_LINE_PATTERN.search(main_body) or ("|" in main_body and "-|-" in main_body):
        violations.append("Main body must contain zero markdown table markers ('|').")

    # 6. Zero Bullet Points in main body
    if _BULLET_LINE_PATTERN.search(main_body):
        violations.append(
            "Main body must contain zero bullet points or list markers ('*', '-', '+')."
        )

    # 7. Zero Blockquotes in main body
    if _BLOCKQUOTE_LINE_PATTERN.search(main_body):
        violations.append("Main body must contain zero blockquotes ('>').")

    # 8. Zero Bullet Points in complementary section (must be numbered continuous paragraphs)
    if comp_section and _BULLET_LINE_PATTERN.search(comp_section):
        violations.append(
            "Complementary section must contain zero bullet points or list markers ('*', '-', '+'). "
            "Use numbered continuous paragraphs ('1. ', '2. ')."
        )

    return violations


_NUMBERED_ITEM_PATTERN = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)


def count_complementary_items(comp_text: str) -> int:
    """Count discrete numbered items or distinct paragraphs in complementary section."""
    numbered = _NUMBERED_ITEM_PATTERN.findall(comp_text)
    if numbered:
        return len(numbered)
    paragraphs = [p for p in comp_text.split("\n\n") if p.strip()]
    return len(paragraphs) if paragraphs else 1


def check_complementary_mechanical_saturation(
    prev_text: str,
    current_text: str,
    max_delta_items: int = 5,
) -> bool:
    """Evaluate Layer 1 mechanical saturation between consecutive passes.

    Conforms to Lead Architect directives:
    1. Delta de Comprimento: variação no número de itens/parágrafos de informações complementares < 5.
    2. NER Overlap: 100% das entidades em negrito (**...**) na seção complementar atual
       já estavam presentes na passagem anterior (zero novas entidades introduzidas).
    """
    prev_comp = extract_complementary_section(prev_text)
    curr_comp = extract_complementary_section(current_text)

    if not prev_comp or not curr_comp:
        return False

    prev_items = count_complementary_items(prev_comp)
    curr_items = count_complementary_items(curr_comp)

    delta_items = abs(curr_items - prev_items)
    if delta_items >= max_delta_items:
        return False

    prev_entities = {
        e.strip().lower() for e in _BOLD_ENTITY_PATTERN.findall(prev_comp) if e.strip()
    }
    curr_entities = {
        e.strip().lower() for e in _BOLD_ENTITY_PATTERN.findall(curr_comp) if e.strip()
    }

    # If any new bold entity was introduced in the current pass, not saturated yet
    return curr_entities.issubset(prev_entities)
