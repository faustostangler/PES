"""Application utility for extracting and parsing JSON payloads from LLM responses.

Handles standard JSON, markdown code fence wrapping (```json ... ```),
and outermost bracket extraction.
"""

from __future__ import annotations

import json
import re
from typing import Any

_MARKDOWN_CODE_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")


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
        pass

    # 2. Markdown code fence match
    matches = _MARKDOWN_CODE_FENCE_PATTERN.findall(content)
    for candidate in matches:
        candidate_clean = candidate.strip()
        try:
            return json.loads(candidate_clean)
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
            pass

    # 4. Outermost object braces attempt
    start_brace = content.find("{")
    end_brace = content.rfind("}")
    if start_brace != -1 and end_brace > start_brace:
        candidate = content[start_brace : end_brace + 1].strip()
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            pass

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")
