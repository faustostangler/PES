"""Text validation, sanitation, and parsing utilities for transcript indexing.

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
"""

from __future__ import annotations

import re
from typing import Final

_STRIP_MARKDOWN_QUOTE_CHARS: Final[str] = "\"'`*#_"
_STRIP_CONCEPT_CHARS: Final[str] = "\"'`*#_:"
DEFAULT_SYNTHESIS_MIN_WORDS: Final[int] = 20
DEFAULT_SYNTHESIS_MAX_WORDS: Final[int] = 120
FORBIDDEN_LIST_LINE_PREFIXES: Final[tuple[str, ...]] = ("- ", "* ", "1.", "2.", "• ")
CONCEPT_LIST_SPLIT_CHAR: Final[str] = ","
CONCEPT_LIST_JOIN_SEP: Final[str] = ", "
FALLBACK_KEY_CONCEPT_TITLE: Final[str] = "Síntese Conceitual"

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
    clean_first = first_line.strip(_STRIP_MARKDOWN_QUOTE_CHARS)
    return not _FORBIDDEN_PREFIX_REGEX.search(clean_first)


def is_valid_synthesis_paragraph(
    raw_output: str,
    min_words: int = DEFAULT_SYNTHESIS_MIN_WORDS,
    max_words: int = DEFAULT_SYNTHESIS_MAX_WORDS,
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
    clean_first = clean.splitlines()[0].strip(_STRIP_MARKDOWN_QUOTE_CHARS)
    if _FORBIDDEN_PREFIX_REGEX.search(clean_first):
        return False

    # Reject multi-paragraph markdown outputs separated by empty lines
    paragraphs = [p.strip() for p in clean.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        return False

    # Reject markdown bullet lists or numbered lists
    for line in clean.splitlines():
        stripped = line.strip()
        if stripped.startswith(FORBIDDEN_LIST_LINE_PREFIXES):
            return False

    words = clean.split()
    return min_words <= len(words) <= max_words


def clean_text_line(text: str) -> str:
    """Strip markdown formatting, quotes, and conversational prefixes from a single line.

    Args:
        text: Raw line text from LLM response.

    Returns:
        Sanitized clean string line.
    """
    clean = text.strip().strip(_STRIP_MARKDOWN_QUOTE_CHARS)
    lower = clean.lower()
    for prefix in _INDICATIVE_PREFIXES:
        if lower.startswith(prefix):
            clean = clean[len(prefix) :].strip().strip(_STRIP_MARKDOWN_QUOTE_CHARS)
            lower = clean.lower()
    return clean.strip()


def clean_concept_line(line: str) -> str:
    """Sanitize Line 1 into comma-separated concepts with zero labels or meta-prefixes.

    Args:
        line: Raw first line from LLM response.

    Returns:
        Comma-separated string of clean concept terms.
    """
    clean = clean_text_line(line)
    clean = _FORBIDDEN_PREFIX_REGEX.sub("", clean).strip().strip(_STRIP_CONCEPT_CHARS)
    parts = [
        p.strip().strip(_STRIP_MARKDOWN_QUOTE_CHARS)
        for p in clean.split(CONCEPT_LIST_SPLIT_CHAR)
        if p.strip().strip(_STRIP_MARKDOWN_QUOTE_CHARS)
    ]
    if parts:
        return CONCEPT_LIST_JOIN_SEP.join(parts)
    return clean or FALLBACK_KEY_CONCEPT_TITLE
