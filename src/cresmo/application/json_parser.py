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
        outer_prev_i = i
        if text[i] == "{":
            depth = 1
            in_string = False
            escape = False
            start = i
            i += 1
            while i < n and depth > 0:
                inner_prev_i = i
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
                i += 1
                if i <= inner_prev_i:
                    break
            if depth == 0:
                candidate = text[start:i]
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        objects.append(parsed)
                except (json.JSONDecodeError, ValueError):
                    cleaned = _TRAILING_COMMA_PATTERN.sub(r"\1", candidate)
                    try:
                        parsed = json.loads(cleaned)
                        if isinstance(parsed, dict):
                            objects.append(parsed)
                    except (json.JSONDecodeError, ValueError):
                        pass
        else:
            i += 1
        if i <= outer_prev_i:
            break
    return objects


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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", content))
        except (json.JSONDecodeError, ValueError):
            pass

    # 2. Markdown code fence match
    matches = _MARKDOWN_CODE_FENCE_PATTERN.findall(content)
    for candidate in matches:
        candidate_clean = candidate.strip()
        try:
            return json.loads(candidate_clean)
        except (json.JSONDecodeError, ValueError):
            try:
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate_clean))
            except (json.JSONDecodeError, ValueError):
                continue

    # 3. Outermost array brackets attempt
    start_bracket = content.find("[")
    end_bracket = content.rfind("]")
    if start_bracket != -1 and end_bracket > start_bracket:
        candidate = content[start_bracket : end_bracket + 1].strip()
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            try:
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate))
            except (json.JSONDecodeError, ValueError):
                pass

    # 4. Outermost object braces attempt
    start_brace = content.find("{")
    end_brace = content.rfind("}")
    if start_brace != -1 and end_brace > start_brace:
        candidate = content[start_brace : end_brace + 1].strip()
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            try:
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")
