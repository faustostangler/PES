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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__parse_json_candidate__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__parse_json_candidate__mutmut)
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


def x__parse_json_candidate__mutmut_orig(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_1(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(None)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", candidate))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_2(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(None)
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_3(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(None, candidate))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_4(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", None))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_5(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(candidate))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_6(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", ))
    except (json.JSONDecodeError, ValueError):
        return None


def x__parse_json_candidate__mutmut_7(candidate: str) -> Any | None:
    """Attempt decoding JSON string directly or with trailing-comma repair."""
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return json.loads(_TRAILING_COMMA_PATTERN.sub(r"XX\1XX", candidate))
    except (json.JSONDecodeError, ValueError):
        return None

mutants_x__parse_json_candidate__mutmut['_mutmut_orig'] = x__parse_json_candidate__mutmut_orig # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_1'] = x__parse_json_candidate__mutmut_1 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_2'] = x__parse_json_candidate__mutmut_2 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_3'] = x__parse_json_candidate__mutmut_3 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_4'] = x__parse_json_candidate__mutmut_4 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_5'] = x__parse_json_candidate__mutmut_5 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_6'] = x__parse_json_candidate__mutmut_6 # type: ignore # mutmut generated
mutants_x__parse_json_candidate__mutmut['x__parse_json_candidate__mutmut_7'] = x__parse_json_candidate__mutmut_7 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__find_balanced_closing_brace__mutmut)
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


def x__find_balanced_closing_brace__mutmut_orig(text: str, start: int) -> int | None:
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


def x__find_balanced_closing_brace__mutmut_1(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = None
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


def x__find_balanced_closing_brace__mutmut_2(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 1
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


def x__find_balanced_closing_brace__mutmut_3(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = None
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


def x__find_balanced_closing_brace__mutmut_4(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = True
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


def x__find_balanced_closing_brace__mutmut_5(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = None
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


def x__find_balanced_closing_brace__mutmut_6(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = True
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


def x__find_balanced_closing_brace__mutmut_7(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = None
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


def x__find_balanced_closing_brace__mutmut_8(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(None, n):
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


def x__find_balanced_closing_brace__mutmut_9(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, None):
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


def x__find_balanced_closing_brace__mutmut_10(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(n):
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


def x__find_balanced_closing_brace__mutmut_11(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, ):
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


def x__find_balanced_closing_brace__mutmut_12(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, n):
        char = None
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


def x__find_balanced_closing_brace__mutmut_13(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, n):
        char = text[i]
        if in_string:
            if escape:
                escape = None
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


def x__find_balanced_closing_brace__mutmut_14(text: str, start: int) -> int | None:
    """Find the index of the matching closing brace for a JSON block starting at start."""
    depth = 0
    in_string = False
    escape = False
    n = len(text)
    for i in range(start, n):
        char = text[i]
        if in_string:
            if escape:
                escape = True
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


def x__find_balanced_closing_brace__mutmut_15(text: str, start: int) -> int | None:
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
            elif char != "\\":
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


def x__find_balanced_closing_brace__mutmut_16(text: str, start: int) -> int | None:
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
            elif char == "XX\\XX":
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


def x__find_balanced_closing_brace__mutmut_17(text: str, start: int) -> int | None:
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
                escape = None
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


def x__find_balanced_closing_brace__mutmut_18(text: str, start: int) -> int | None:
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
                escape = False
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


def x__find_balanced_closing_brace__mutmut_19(text: str, start: int) -> int | None:
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
            elif char != '"':
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


def x__find_balanced_closing_brace__mutmut_20(text: str, start: int) -> int | None:
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
            elif char == 'XX"XX':
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


def x__find_balanced_closing_brace__mutmut_21(text: str, start: int) -> int | None:
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
                in_string = None
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


def x__find_balanced_closing_brace__mutmut_22(text: str, start: int) -> int | None:
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
                in_string = True
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


def x__find_balanced_closing_brace__mutmut_23(text: str, start: int) -> int | None:
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
            if char != '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_24(text: str, start: int) -> int | None:
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
            if char == 'XX"XX':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_25(text: str, start: int) -> int | None:
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
                in_string = None
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_26(text: str, start: int) -> int | None:
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
                in_string = False
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_27(text: str, start: int) -> int | None:
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
            elif char != "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_28(text: str, start: int) -> int | None:
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
            elif char == "XX{XX":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_29(text: str, start: int) -> int | None:
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
                depth = 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_30(text: str, start: int) -> int | None:
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
                depth -= 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_31(text: str, start: int) -> int | None:
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
                depth += 2
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_32(text: str, start: int) -> int | None:
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
            elif char != "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_33(text: str, start: int) -> int | None:
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
            elif char == "XX}XX":
                depth -= 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_34(text: str, start: int) -> int | None:
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
                depth = 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_35(text: str, start: int) -> int | None:
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
                depth += 1
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_36(text: str, start: int) -> int | None:
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
                depth -= 2
                if depth == 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_37(text: str, start: int) -> int | None:
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
                if depth != 0:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_38(text: str, start: int) -> int | None:
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
                if depth == 1:
                    return i + 1
    return None


def x__find_balanced_closing_brace__mutmut_39(text: str, start: int) -> int | None:
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
                    return i - 1
    return None


def x__find_balanced_closing_brace__mutmut_40(text: str, start: int) -> int | None:
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
                    return i + 2
    return None

mutants_x__find_balanced_closing_brace__mutmut['_mutmut_orig'] = x__find_balanced_closing_brace__mutmut_orig # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_1'] = x__find_balanced_closing_brace__mutmut_1 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_2'] = x__find_balanced_closing_brace__mutmut_2 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_3'] = x__find_balanced_closing_brace__mutmut_3 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_4'] = x__find_balanced_closing_brace__mutmut_4 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_5'] = x__find_balanced_closing_brace__mutmut_5 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_6'] = x__find_balanced_closing_brace__mutmut_6 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_7'] = x__find_balanced_closing_brace__mutmut_7 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_8'] = x__find_balanced_closing_brace__mutmut_8 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_9'] = x__find_balanced_closing_brace__mutmut_9 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_10'] = x__find_balanced_closing_brace__mutmut_10 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_11'] = x__find_balanced_closing_brace__mutmut_11 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_12'] = x__find_balanced_closing_brace__mutmut_12 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_13'] = x__find_balanced_closing_brace__mutmut_13 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_14'] = x__find_balanced_closing_brace__mutmut_14 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_15'] = x__find_balanced_closing_brace__mutmut_15 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_16'] = x__find_balanced_closing_brace__mutmut_16 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_17'] = x__find_balanced_closing_brace__mutmut_17 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_18'] = x__find_balanced_closing_brace__mutmut_18 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_19'] = x__find_balanced_closing_brace__mutmut_19 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_20'] = x__find_balanced_closing_brace__mutmut_20 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_21'] = x__find_balanced_closing_brace__mutmut_21 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_22'] = x__find_balanced_closing_brace__mutmut_22 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_23'] = x__find_balanced_closing_brace__mutmut_23 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_24'] = x__find_balanced_closing_brace__mutmut_24 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_25'] = x__find_balanced_closing_brace__mutmut_25 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_26'] = x__find_balanced_closing_brace__mutmut_26 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_27'] = x__find_balanced_closing_brace__mutmut_27 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_28'] = x__find_balanced_closing_brace__mutmut_28 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_29'] = x__find_balanced_closing_brace__mutmut_29 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_30'] = x__find_balanced_closing_brace__mutmut_30 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_31'] = x__find_balanced_closing_brace__mutmut_31 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_32'] = x__find_balanced_closing_brace__mutmut_32 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_33'] = x__find_balanced_closing_brace__mutmut_33 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_34'] = x__find_balanced_closing_brace__mutmut_34 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_35'] = x__find_balanced_closing_brace__mutmut_35 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_36'] = x__find_balanced_closing_brace__mutmut_36 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_37'] = x__find_balanced_closing_brace__mutmut_37 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_38'] = x__find_balanced_closing_brace__mutmut_38 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_39'] = x__find_balanced_closing_brace__mutmut_39 # type: ignore # mutmut generated
mutants_x__find_balanced_closing_brace__mutmut['x__find_balanced_closing_brace__mutmut_40'] = x__find_balanced_closing_brace__mutmut_40 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__extract_individual_objects__mutmut)
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


def x__extract_individual_objects__mutmut_orig(text: str) -> list[dict[str, Any]]:
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


def x__extract_individual_objects__mutmut_1(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.

    Args:
        text: Raw text potentially containing multiple balanced JSON objects.

    Returns:
        List of successfully decoded dictionary objects.
    """
    objects: list[dict[str, Any]] = None
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


def x__extract_individual_objects__mutmut_2(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.

    Args:
        text: Raw text potentially containing multiple balanced JSON objects.

    Returns:
        List of successfully decoded dictionary objects.
    """
    objects: list[dict[str, Any]] = []
    i = None
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


def x__extract_individual_objects__mutmut_3(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.

    Args:
        text: Raw text potentially containing multiple balanced JSON objects.

    Returns:
        List of successfully decoded dictionary objects.
    """
    objects: list[dict[str, Any]] = []
    i = 1
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


def x__extract_individual_objects__mutmut_4(text: str) -> list[dict[str, Any]]:
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
    n = None
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


def x__extract_individual_objects__mutmut_5(text: str) -> list[dict[str, Any]]:
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
    while i <= n:
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


def x__extract_individual_objects__mutmut_6(text: str) -> list[dict[str, Any]]:
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
        if text[i] != "{":
            end = _find_balanced_closing_brace(text, i)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_7(text: str) -> list[dict[str, Any]]:
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
        if text[i] == "XX{XX":
            end = _find_balanced_closing_brace(text, i)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_8(text: str) -> list[dict[str, Any]]:
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
            end = None
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_9(text: str) -> list[dict[str, Any]]:
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
            end = _find_balanced_closing_brace(None, i)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_10(text: str) -> list[dict[str, Any]]:
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
            end = _find_balanced_closing_brace(text, None)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_11(text: str) -> list[dict[str, Any]]:
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
            end = _find_balanced_closing_brace(i)
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_12(text: str) -> list[dict[str, Any]]:
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
            end = _find_balanced_closing_brace(text, )
            if end is not None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_13(text: str) -> list[dict[str, Any]]:
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
            if end is None:
                parsed = _parse_json_candidate(text[i:end])
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_14(text: str) -> list[dict[str, Any]]:
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
                parsed = None
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_15(text: str) -> list[dict[str, Any]]:
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
                parsed = _parse_json_candidate(None)
                if isinstance(parsed, dict):
                    objects.append(parsed)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_16(text: str) -> list[dict[str, Any]]:
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
                    objects.append(None)
                i = end
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_17(text: str) -> list[dict[str, Any]]:
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
                i = None
                continue
        i += 1
    return objects


def x__extract_individual_objects__mutmut_18(text: str) -> list[dict[str, Any]]:
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
                break
        i += 1
    return objects


def x__extract_individual_objects__mutmut_19(text: str) -> list[dict[str, Any]]:
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
        i = 1
    return objects


def x__extract_individual_objects__mutmut_20(text: str) -> list[dict[str, Any]]:
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
        i -= 1
    return objects


def x__extract_individual_objects__mutmut_21(text: str) -> list[dict[str, Any]]:
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
        i += 2
    return objects

mutants_x__extract_individual_objects__mutmut['_mutmut_orig'] = x__extract_individual_objects__mutmut_orig # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_1'] = x__extract_individual_objects__mutmut_1 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_2'] = x__extract_individual_objects__mutmut_2 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_3'] = x__extract_individual_objects__mutmut_3 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_4'] = x__extract_individual_objects__mutmut_4 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_5'] = x__extract_individual_objects__mutmut_5 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_6'] = x__extract_individual_objects__mutmut_6 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_7'] = x__extract_individual_objects__mutmut_7 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_8'] = x__extract_individual_objects__mutmut_8 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_9'] = x__extract_individual_objects__mutmut_9 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_10'] = x__extract_individual_objects__mutmut_10 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_11'] = x__extract_individual_objects__mutmut_11 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_12'] = x__extract_individual_objects__mutmut_12 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_13'] = x__extract_individual_objects__mutmut_13 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_14'] = x__extract_individual_objects__mutmut_14 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_15'] = x__extract_individual_objects__mutmut_15 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_16'] = x__extract_individual_objects__mutmut_16 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_17'] = x__extract_individual_objects__mutmut_17 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_18'] = x__extract_individual_objects__mutmut_18 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_19'] = x__extract_individual_objects__mutmut_19 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_20'] = x__extract_individual_objects__mutmut_20 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_21'] = x__extract_individual_objects__mutmut_21 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__extract_bracketed__mutmut)
def _extract_bracketed(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_orig(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_1(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = None
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_2(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(None)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_3(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.rfind(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_4(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = None
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_5(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(None)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_6(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.find(close_ch)
    if start != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_7(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 or end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_8(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start == -1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_9(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != +1 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_10(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -2 and end > start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_11(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end >= start:
        return text[start : end + 1].strip()
    return None


def x__extract_bracketed__mutmut_12(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end - 1].strip()
    return None


def x__extract_bracketed__mutmut_13(text: str, open_ch: str, close_ch: str) -> str | None:
    """Extract substring enclosed between first open_ch and last close_ch."""
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end > start:
        return text[start : end + 2].strip()
    return None

mutants_x__extract_bracketed__mutmut['_mutmut_orig'] = x__extract_bracketed__mutmut_orig # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_1'] = x__extract_bracketed__mutmut_1 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_2'] = x__extract_bracketed__mutmut_2 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_3'] = x__extract_bracketed__mutmut_3 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_4'] = x__extract_bracketed__mutmut_4 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_5'] = x__extract_bracketed__mutmut_5 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_6'] = x__extract_bracketed__mutmut_6 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_7'] = x__extract_bracketed__mutmut_7 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_8'] = x__extract_bracketed__mutmut_8 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_9'] = x__extract_bracketed__mutmut_9 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_10'] = x__extract_bracketed__mutmut_10 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_11'] = x__extract_bracketed__mutmut_11 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_12'] = x__extract_bracketed__mutmut_12 # type: ignore # mutmut generated
mutants_x__extract_bracketed__mutmut['x__extract_bracketed__mutmut_13'] = x__extract_bracketed__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_extract_json_data__mutmut)
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


def x_extract_json_data__mutmut_orig(raw_content: str) -> Any:
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


def x_extract_json_data__mutmut_1(raw_content: str) -> Any:
    """Extract and parse JSON payload from raw LLM output.

    Args:
        raw_content: Raw text returned by LLM model.

    Returns:
        Parsed JSON object or array.

    Raises:
        ValueError: If no valid JSON payload could be extracted.
    """
    content = None

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


def x_extract_json_data__mutmut_2(raw_content: str) -> Any:
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
    if (parsed := _parse_json_candidate(None)) is not None:
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


def x_extract_json_data__mutmut_3(raw_content: str) -> Any:
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
    if (parsed := _parse_json_candidate(content)) is None:
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


def x_extract_json_data__mutmut_4(raw_content: str) -> Any:
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
    for candidate in _MARKDOWN_CODE_FENCE_PATTERN.findall(None):
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


def x_extract_json_data__mutmut_5(raw_content: str) -> Any:
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
        if (parsed := _parse_json_candidate(None)) is not None:
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


def x_extract_json_data__mutmut_6(raw_content: str) -> Any:
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
        if (parsed := _parse_json_candidate(candidate.strip())) is None:
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


def x_extract_json_data__mutmut_7(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "[", "]")) is not None or (
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


def x_extract_json_data__mutmut_8(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(None, "[", "]")) is not None and (
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


def x_extract_json_data__mutmut_9(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, None, "]")) is not None and (
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


def x_extract_json_data__mutmut_10(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "[", None)) is not None and (
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


def x_extract_json_data__mutmut_11(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed("[", "]")) is not None and (
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


def x_extract_json_data__mutmut_12(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "]")) is not None and (
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


def x_extract_json_data__mutmut_13(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "[", )) is not None and (
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


def x_extract_json_data__mutmut_14(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "XX[XX", "]")) is not None and (
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


def x_extract_json_data__mutmut_15(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "[", "XX]XX")) is not None and (
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


def x_extract_json_data__mutmut_16(raw_content: str) -> Any:
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
    if (arr := _extract_bracketed(content, "[", "]")) is None and (
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


def x_extract_json_data__mutmut_17(raw_content: str) -> Any:
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
        parsed := _parse_json_candidate(None)
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


def x_extract_json_data__mutmut_18(raw_content: str) -> Any:
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
    ) is None:
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


def x_extract_json_data__mutmut_19(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "{", "}")) is not None or (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_20(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(None, "{", "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_21(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, None, "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_22(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "{", None)) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_23(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed("{", "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_24(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_25(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "{", )) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_26(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "XX{XX", "}")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_27(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "{", "XX}XX")) is not None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_28(raw_content: str) -> Any:
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
    if (obj := _extract_bracketed(content, "{", "}")) is None and (
        parsed := _parse_json_candidate(obj)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_29(raw_content: str) -> Any:
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
        parsed := _parse_json_candidate(None)
    ) is not None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_30(raw_content: str) -> Any:
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
    ) is None:
        return parsed

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    if extracted := _extract_individual_objects(content):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_31(raw_content: str) -> Any:
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
    if extracted := _extract_individual_objects(None):
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_32(raw_content: str) -> Any:
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
        if len(extracted) != 1:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_33(raw_content: str) -> Any:
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
        if len(extracted) == 2:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_34(raw_content: str) -> Any:
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
            return extracted[1]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:200]}")


def x_extract_json_data__mutmut_35(raw_content: str) -> Any:
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

    raise ValueError(None)


def x_extract_json_data__mutmut_36(raw_content: str) -> Any:
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

    raise ValueError(f"Failed to extract valid JSON payload: {raw_content[:201]}")

mutants_x_extract_json_data__mutmut['_mutmut_orig'] = x_extract_json_data__mutmut_orig # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_1'] = x_extract_json_data__mutmut_1 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_2'] = x_extract_json_data__mutmut_2 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_3'] = x_extract_json_data__mutmut_3 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_4'] = x_extract_json_data__mutmut_4 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_5'] = x_extract_json_data__mutmut_5 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_6'] = x_extract_json_data__mutmut_6 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_7'] = x_extract_json_data__mutmut_7 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_8'] = x_extract_json_data__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_9'] = x_extract_json_data__mutmut_9 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_10'] = x_extract_json_data__mutmut_10 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_11'] = x_extract_json_data__mutmut_11 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_12'] = x_extract_json_data__mutmut_12 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_13'] = x_extract_json_data__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_14'] = x_extract_json_data__mutmut_14 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_15'] = x_extract_json_data__mutmut_15 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_16'] = x_extract_json_data__mutmut_16 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_17'] = x_extract_json_data__mutmut_17 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_18'] = x_extract_json_data__mutmut_18 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_19'] = x_extract_json_data__mutmut_19 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_20'] = x_extract_json_data__mutmut_20 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_21'] = x_extract_json_data__mutmut_21 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_22'] = x_extract_json_data__mutmut_22 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_23'] = x_extract_json_data__mutmut_23 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_24'] = x_extract_json_data__mutmut_24 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_25'] = x_extract_json_data__mutmut_25 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_26'] = x_extract_json_data__mutmut_26 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_27'] = x_extract_json_data__mutmut_27 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_28'] = x_extract_json_data__mutmut_28 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_29'] = x_extract_json_data__mutmut_29 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_30'] = x_extract_json_data__mutmut_30 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_31'] = x_extract_json_data__mutmut_31 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_32'] = x_extract_json_data__mutmut_32 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_33'] = x_extract_json_data__mutmut_33 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_34'] = x_extract_json_data__mutmut_34 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_35'] = x_extract_json_data__mutmut_35 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_36'] = x_extract_json_data__mutmut_36 # type: ignore # mutmut generated
