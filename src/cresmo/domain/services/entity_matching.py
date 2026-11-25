"""Pure domain entity title normalization helpers for matching and deduplication."""

from __future__ import annotations

import re
from typing import Final

_HONORIFIC_PREFIXES: Final[tuple[str, ...]] = ("dom ", "dona ", "d. ", "d ")
_PUNCT_COLLAPSE_RE: Final[re.Pattern[str]] = re.compile(r"[\s\-_.,()]+")
_MIN_HONORIFIC_NORMALIZED_LENGTH: Final[int] = 4


def normalize_entity_title_for_matching(title: str) -> str:
    """Normalize an entity title by stripping Portuguese honorifics and punctuation."""
    norm = title.lower().strip()
    for prefix in _HONORIFIC_PREFIXES:
        if norm.startswith(prefix):
            candidate = norm[len(prefix) :].strip()
            if len(candidate) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
                norm = candidate
            break
    return _PUNCT_COLLAPSE_RE.sub("", norm)
