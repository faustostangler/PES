"""Pure Domain syntactic pre-flight guards for fluid prose and gap-filler compendia.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §2.1 (prose_syntax_guard)
"""

from __future__ import annotations

import re

_BULLET_LINE_PATTERN = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_BLOCKQUOTE_LINE_PATTERN = re.compile(r"^\s*>", re.MULTILINE)
_TABLE_LINE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_YAML_DELIMITER_PATTERN = re.compile(r"^---\s*$", re.MULTILINE)
_EXTRA_INFO_PATTERN = re.compile(r"^\s*###\s+Extra\s+Info\s*$", re.MULTILINE)


def _collect_common_header_and_inline_violations(stripped: str) -> list[str]:
    """Validate Line 1 heading, zero YAML frontmatter, and zero em-dash invariants."""
    violations: list[str] = []

    first_line = stripped.splitlines()[0].strip()
    if not first_line.startswith("## "):
        violations.append(f"Line 1 must start with '## ' (found: '{first_line[:40]}...')")

    if _YAML_DELIMITER_PATTERN.search(stripped):
        violations.append("Text must contain zero YAML frontmatter delimiters ('---').")

    if "—" in stripped:
        violations.append(
            "Text must contain zero em-dashes ('—'). Use commas or separate sentences."
        )

    return violations


def _collect_forbidden_block_violations(text: str, *, scope_label: str) -> list[str]:
    """Validate zero bullets, markdown tables, and blockquotes within a text scope."""
    violations: list[str] = []

    if _BULLET_LINE_PATTERN.search(text):
        violations.append(
            f"{scope_label} must contain zero bullet points or list markers ('*', '-', '+')."
        )

    if _TABLE_LINE_PATTERN.search(text) or ("|" in text and "-|-" in text):
        violations.append(f"{scope_label} must contain zero markdown table markers ('|').")

    if _BLOCKQUOTE_LINE_PATTERN.search(text):
        violations.append(f"{scope_label} must contain zero blockquotes ('>').")

    return violations


def extract_extra_info_section(text: str) -> str:
    """Extract stripped content following the mandatory '### Extra Info' heading.

    Args:
        text: Candidate markdown compendium text.

    Returns:
        str: Stripped text after the '### Extra Info' heading, or empty string if absent.
    """
    match = _EXTRA_INFO_PATTERN.search(text)
    if not match:
        return ""
    return text[match.end() :].strip()


def validate_fluid_prose_syntax(text: str) -> list[str]:
    """Validate deterministic syntactic invariants for fluid_prose compendia.

    Args:
        text: Candidate fluid prose markdown string.

    Returns:
        list[str]: Diagnostic violation messages. Empty list indicates full syntactic compliance.
    """
    stripped = text.strip()
    if not stripped:
        return ["Text is empty or whitespace."]

    violations = _collect_common_header_and_inline_violations(stripped)
    violations.extend(_collect_forbidden_block_violations(stripped, scope_label="Text"))

    body_paragraphs = [
        p.strip() for p in stripped.split("\n\n") if p.strip() and not p.strip().startswith("##")
    ]
    if len(body_paragraphs) == 1 and len(body_paragraphs[0].split()) > 80:
        violations.append(
            "Text must contain distinct paragraphs separated by blank lines (monolithic wall of text detected)."
        )

    return violations


def validate_gap_filler_syntax(text: str) -> list[str]:
    """Validate deterministic syntactic invariants for gap_filler compendia.

    Args:
        text: Candidate gap_filler markdown string.

    Returns:
        list[str]: Diagnostic violation messages. Empty list indicates full syntactic compliance.
    """
    stripped = text.strip()
    if not stripped:
        return ["Text is empty or whitespace."]

    violations = _collect_common_header_and_inline_violations(stripped)

    extra_info_match = _EXTRA_INFO_PATTERN.search(stripped)
    if not extra_info_match:
        violations.append("Missing mandatory complementary section '### Extra Info'.")
        main_body = stripped
        complementary_section = ""
    else:
        main_body = stripped[: extra_info_match.start()].strip()
        complementary_section = stripped[extra_info_match.end() :].strip()
        if not complementary_section:
            violations.append("Section '### Extra Info' is empty.")
        if not main_body:
            violations.append("Main body text before '### Extra Info' is empty.")

    violations.extend(_collect_forbidden_block_violations(main_body, scope_label="Main body"))

    if complementary_section and _BULLET_LINE_PATTERN.search(complementary_section):
        violations.append(
            "Complementary section must contain zero bullet points or list markers ('*', '-', '+'). "
            "Use numbered continuous paragraphs ('1. ', '2. ')."
        )

    return violations
