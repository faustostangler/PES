"""Text validation, sanitation, and parsing utilities for transcript indexing.

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
"""

from __future__ import annotations

import re
from typing import Final

_MIN_MULTILINE_LINE_COUNT: Final[int] = 2

_INDICATIVE_PREFIXES = (
    "key concept:",
    "key concepts:",
    "conceito-chave:",
    "conceito chave:",
    "conceitos-chave:",
    "conceitos chave:",
    "conceito:",
    "concept:",
    "síntese conceitual:",
    "sintese conceitual:",
    "síntese:",
    "sintese:",
    "synthesis:",
)

_FORBIDDEN_PREFIX_REGEX = re.compile(
    r"^\s*(?:\*{1,3}|#{1,6}\s*)?"
    r"(?:key\s*concepts?|keywords?|palavras?-chave|conceitos?(?:-chave)?|tópicos?|termo-chave|síntese(?: conceitual)?|sintese(?: conceitual)?|synthesis|linha\s*[12]|line\s*[12])"
    r"\s*[:：\-–—]",
    re.IGNORECASE,
)


def is_valid_raw_index_output(raw_output: str) -> bool:
    """Validate that raw index output conforms to expected structure without forbidden labels.

    Args:
        raw_output: Generative LLM response text.

    Returns:
        True if response contains no forbidden prefixes and has valid structure.
    """
    clean = raw_output.strip()
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    if not lines:
        return False
    first_line = lines[0]
    if _FORBIDDEN_PREFIX_REGEX.search(first_line):
        return False
    clean_first = first_line.strip("\"'`*#_")
    if _FORBIDDEN_PREFIX_REGEX.search(clean_first):
        return False

    # Must have either multi-line structure (Line 1: concepts, Line 2+: synthesis)
    # or single-line comma-delimited structure (<concept>, <synthesis>).
    if len(lines) >= _MIN_MULTILINE_LINE_COUNT:
        return True
    return "," in first_line


def is_valid_concepts_output(raw_output: str) -> bool:
    """Validate whether LLM concepts output is clean of forbidden prefixes and labels.

    Args:
        raw_output: Generative LLM response text for key concepts pass.

    Returns:
        True if response is non-empty and contains no forbidden labels or prefixes.
    """
    clean = raw_output.strip()
    if not clean:
        return False
    first_line = clean.splitlines()[0].strip()
    if _FORBIDDEN_PREFIX_REGEX.search(first_line):
        return False
    clean_first = first_line.strip("\"'`*#_")
    return not _FORBIDDEN_PREFIX_REGEX.search(clean_first)


def is_valid_synthesis_paragraph(
    raw_output: str,
    min_words: int = 20,
    max_words: int = 120,
) -> bool:
    """Validate that candidate synthesis output is a single paragraph of appropriate size.

    Args:
        raw_output: Candidate synthesis paragraph from LLM.
        min_words: Minimum word threshold.
        max_words: Maximum word threshold.

    Returns:
        True if the output meets paragraph formatting and size constraints; False otherwise.
    """
    clean = raw_output.strip()
    if not clean:
        return False
    if _FORBIDDEN_PREFIX_REGEX.search(clean):
        return False
    clean_first = clean.splitlines()[0].strip("\"'`*#_")
    if _FORBIDDEN_PREFIX_REGEX.search(clean_first):
        return False

    # Reject multi-paragraph markdown outputs separated by empty lines
    paragraphs = [p.strip() for p in clean.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        return False

    # Reject markdown bullet lists or numbered lists
    for line in clean.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "1.", "2.", "• ")):
            return False

    words = clean.split()
    return min_words <= len(words) <= max_words


def can_retry(attempts: int, max_rewrites: int) -> bool:
    """Determine whether another retry attempt is permitted.

    A max_rewrites value of 0 or negative signifies unbounded (infinite) retries.

    Args:
        attempts: Number of rewrite attempts completed so far.
        max_rewrites: Configured threshold limit (0 = infinite).

    Returns:
        True if another attempt is allowed; False otherwise.
    """
    if max_rewrites <= 0:
        return True
    return attempts < max_rewrites


# Backward-compatible alias
_can_retry = can_retry


def parse_judge_boolean(raw_output: str) -> bool:
    """Parse boolean verdict from LLM-as-a-judge deterministic response.

    Args:
        raw_output: Verbatim output from judge LLM invocation.

    Returns:
        True if the response confirms compliance ('true'); False otherwise.
    """
    if not raw_output:
        return False
    clean = raw_output.strip()
    clean = re.sub(r"^```(?:json|txt)?\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    clean = clean.strip().strip(".,;:!?\"'()")
    lower = clean.lower()
    return lower == "true" or lower.startswith("true")


def clean_text_line(text: str) -> str:
    """Strip markdown formatting, quotes, and conversational prefixes from a single line.

    Args:
        text: Raw line text from LLM response.

    Returns:
        Sanitized clean string line.
    """
    clean = text.strip().strip("\"'`*#_")
    lower = clean.lower()
    for prefix in _INDICATIVE_PREFIXES:
        if lower.startswith(prefix):
            clean = clean[len(prefix) :].strip().strip("\"'`*#_")
            lower = clean.lower()
    return clean.strip()


_clean_text_line = clean_text_line


def clean_concept_line(line: str) -> str:
    """Sanitize Line 1 into comma-separated concepts with zero labels or meta-prefixes.

    Args:
        line: Raw first line from LLM response.

    Returns:
        Comma-separated string of clean concept terms.
    """
    clean = clean_text_line(line)
    clean = _FORBIDDEN_PREFIX_REGEX.sub("", clean).strip().strip("\"'`*#_:")
    parts = [p.strip().strip("\"'`*#_") for p in clean.split(",") if p.strip().strip("\"'`*#_")]
    if parts:
        return ", ".join(parts)
    return clean or "Síntese Conceitual"


_clean_concept_line = clean_concept_line


def parse_raw_index_response(raw_output: str, fallback_title: str) -> tuple[str, str]:
    """Parse LLM output into (key_concept, paratactic_synthesis) with fallbacks.

    Supports both:
    1. Multi-line format:
       Line 1: Key Concept
       Line 2+: Paratactic paragraph
    2. Single-line format:
       <Key Concept>, <Synthesis sentence>

    Args:
        raw_output: Generative LLM response text.
        fallback_title: Video title used as fallback concept if extraction is empty.

    Returns:
        Tuple of (key_concept, paratactic_synthesis).
    """
    clean_output = raw_output.strip()
    lines = [line.strip() for line in clean_output.splitlines() if line.strip()]

    if not lines:
        return "Síntese Conceitual", fallback_title

    # Multi-line format
    if len(lines) >= _MIN_MULTILINE_LINE_COUNT:
        concept = clean_concept_line(lines[0])
        synthesis = " ".join(lines[1:])
        synthesis = clean_text_line(synthesis)
        if not concept:
            concept = "Síntese Conceitual"
        if not synthesis:
            synthesis = fallback_title
        return concept, synthesis

    # Single-line format (e.g. "Concept, Synthesis")
    single_line = lines[0]
    if "," in single_line:
        part_c, part_s = single_line.split(",", 1)
        concept = clean_concept_line(part_c)
        synthesis = clean_text_line(part_s)
        if not concept:
            concept = "Síntese Conceitual"
        if not synthesis:
            synthesis = fallback_title
        return concept, synthesis

    # If single line without comma, treat line as concept or synthesis
    cleaned = clean_text_line(single_line)
    return "Síntese Conceitual", cleaned or fallback_title
