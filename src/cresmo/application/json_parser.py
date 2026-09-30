"""Application utility for extracting and parsing JSON payloads from LLM responses.

Functions as an Anti-Corruption Layer (ACL) translating non-deterministic LLM generative
text into strongly structured Python primitives, handling conversational markdown code fence
wrapping (```json ... ```), trailing commas, and partial responses.

Conforms to:
- SPEC-001: §3 (Defensive LLM Response Parsing & Extraction)
- ADR-001 (Application Decoupling from Generative Variance)
"""

from __future__ import annotations

import json
import re
from typing import Any

# Regex to extract JSON wrapped in markdown codeblocks
_MARKDOWN_CODE_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")
# ACL Sanitizer: strip trailing commas before closing braces/brackets (common LLM hallucination)
_TRAILING_COMMA_PATTERN = re.compile(r",\s*([\]}])")


def _parse_json_candidate(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate))
    except (json.JSONDecodeError, ValueError):
        return None


def _find_balanced_closing_brace(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, n):
        char = text[i]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def _extract_individual_objects(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.

    Args:
        text: Raw text potentially containing multiple balanced JSON objects.

    Returns:
        List of successfully decoded dictionary objects.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "{":
            end = _find_balanced_closing_brace(text, i)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def _extract_bracketed(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def extract_json_data(raw_content: str) -> Any:
    """Extract and parse JSON payload from raw LLM output.

    Args:
        raw_content: Raw text returned by LLM model.

    Returns:
        Parsed JSON object or array.

    Raises:
        ValueError: If no valid JSON payload could be extracted.
    """
    content = raw_content.strip()

    # 1. Direct parse attempt
    if (parsed := _parse_json_candidate(content)) is not None:
        return parsed

    # 2. Markdown code fence match
    for candidate in _MARKDOWN_CODE_FENCE_PATTERN.findall(content):
        if (parsed := _parse_json_candidate(candidate.strip())) is not None:
            return parsed

    # 3. Outermost array brackets attempt
    if (arr := _extract_bracketed(content, "[", "]")) is not None and (
        parsed := _parse_json_candidate(arr)
    ) is not None:
        return parsed

    # 4. Outermost object braces attempt
    if (obj := _extract_bracketed(content, "{", "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")
