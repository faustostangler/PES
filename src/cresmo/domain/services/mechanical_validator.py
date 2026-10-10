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
    if not first_line.startswith("## ") or first_line.startswith("### "):
        violations.append(
            f"Line 1 must start with '## ' (found: '{first_line[:40]}...')"
        )

    # 2. Zero YAML Frontmatter
    if _YAML_DELIMITER_PATTERN.search(stripped):
        violations.append("Text must contain zero YAML frontmatter delimiters ('---').")

    # 3. Zero Em-Dashes ('—')
    if "—" in stripped:
        violations.append("Text must contain zero em-dashes ('—'). Use commas or separate sentences.")

    # 4. Zero Bullet Points
    if _BULLET_LINE_PATTERN.search(stripped):
        violations.append("Text must contain zero bullet points or list markers ('*', '-', '+').")

    # 5. Zero Markdown Tables
    if _TABLE_LINE_PATTERN.search(stripped) or ("|" in stripped and "-|-" in stripped):
        violations.append("Text must contain zero markdown table markers ('|').")

    # 6. Zero Blockquotes
    if _BLOCKQUOTE_LINE_PATTERN.search(stripped):
        violations.append("Text must contain zero blockquotes ('>').")

    return violations
