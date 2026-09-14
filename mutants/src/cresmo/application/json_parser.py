"""Application utility for extracting and parsing JSON payloads from LLM responses.

Handles standard JSON, markdown code fence wrapping (```json ... ```),
and outermost bracket extraction.
"""

from __future__ import annotations

import json
import re
from typing import Any

_MARKDOWN_CODE_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")
_TRAILING_COMMA_PATTERN = re.compile(r",\s*([\]}])")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__extract_individual_objects__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__extract_individual_objects__mutmut)
def _extract_individual_objects(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_orig(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_1(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = None
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


def x__extract_individual_objects__mutmut_2(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = None
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


def x__extract_individual_objects__mutmut_3(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 1
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


def x__extract_individual_objects__mutmut_4(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = None
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


def x__extract_individual_objects__mutmut_5(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i <= n:
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


def x__extract_individual_objects__mutmut_6(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = None
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


def x__extract_individual_objects__mutmut_7(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] != "{":
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


def x__extract_individual_objects__mutmut_8(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "XX{XX":
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


def x__extract_individual_objects__mutmut_9(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = None
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


def x__extract_individual_objects__mutmut_10(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = 2
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


def x__extract_individual_objects__mutmut_11(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = 1
            in_string = None
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


def x__extract_individual_objects__mutmut_12(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = 1
            in_string = True
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


def x__extract_individual_objects__mutmut_13(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = 1
            in_string = False
            escape = None
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


def x__extract_individual_objects__mutmut_14(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
    """
    objects: list[dict[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        outer_prev_i = i
        if text[i] == "{":
            depth = 1
            in_string = False
            escape = True
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


def x__extract_individual_objects__mutmut_15(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            start = None
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


def x__extract_individual_objects__mutmut_16(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i = 1
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


def x__extract_individual_objects__mutmut_17(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i -= 1
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


def x__extract_individual_objects__mutmut_18(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i += 2
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


def x__extract_individual_objects__mutmut_19(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            while i < n or depth > 0:
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


def x__extract_individual_objects__mutmut_20(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            while i <= n and depth > 0:
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


def x__extract_individual_objects__mutmut_21(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            while i < n and depth >= 0:
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


def x__extract_individual_objects__mutmut_22(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            while i < n and depth > 1:
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


def x__extract_individual_objects__mutmut_23(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                inner_prev_i = None
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


def x__extract_individual_objects__mutmut_24(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_25(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_26(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_27(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_28(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_29(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_30(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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


def x__extract_individual_objects__mutmut_31(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char != '"':
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


def x__extract_individual_objects__mutmut_32(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char == 'XX"XX':
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


def x__extract_individual_objects__mutmut_33(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        in_string = None
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


def x__extract_individual_objects__mutmut_34(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        in_string = True
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


def x__extract_individual_objects__mutmut_35(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    if char != '"':
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


def x__extract_individual_objects__mutmut_36(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    if char == 'XX"XX':
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


def x__extract_individual_objects__mutmut_37(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        in_string = None
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


def x__extract_individual_objects__mutmut_38(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        in_string = False
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


def x__extract_individual_objects__mutmut_39(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char != "{":
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


def x__extract_individual_objects__mutmut_40(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char == "XX{XX":
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


def x__extract_individual_objects__mutmut_41(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth = 1
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


def x__extract_individual_objects__mutmut_42(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth -= 1
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


def x__extract_individual_objects__mutmut_43(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth += 2
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


def x__extract_individual_objects__mutmut_44(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char != "}":
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


def x__extract_individual_objects__mutmut_45(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    elif char == "XX}XX":
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


def x__extract_individual_objects__mutmut_46(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth = 1
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


def x__extract_individual_objects__mutmut_47(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth += 1
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


def x__extract_individual_objects__mutmut_48(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        depth -= 2
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


def x__extract_individual_objects__mutmut_49(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                i = 1
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


def x__extract_individual_objects__mutmut_50(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                i -= 1
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


def x__extract_individual_objects__mutmut_51(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                i += 2
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


def x__extract_individual_objects__mutmut_52(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                if i < inner_prev_i:
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


def x__extract_individual_objects__mutmut_53(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    return
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


def x__extract_individual_objects__mutmut_54(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            if depth != 0:
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


def x__extract_individual_objects__mutmut_55(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            if depth == 1:
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


def x__extract_individual_objects__mutmut_56(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                candidate = None
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


def x__extract_individual_objects__mutmut_57(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    parsed = None
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


def x__extract_individual_objects__mutmut_58(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    parsed = json.loads(None)
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


def x__extract_individual_objects__mutmut_59(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        objects.append(None)
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


def x__extract_individual_objects__mutmut_60(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = None
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


def x__extract_individual_objects__mutmut_61(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = _TRAILING_COMMA_PATTERN.sub(None, candidate)
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


def x__extract_individual_objects__mutmut_62(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = _TRAILING_COMMA_PATTERN.sub(r"\1", None)
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


def x__extract_individual_objects__mutmut_63(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = _TRAILING_COMMA_PATTERN.sub(candidate)
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


def x__extract_individual_objects__mutmut_64(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = _TRAILING_COMMA_PATTERN.sub(r"\1", )
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


def x__extract_individual_objects__mutmut_65(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                    cleaned = _TRAILING_COMMA_PATTERN.sub(r"XX\1XX", candidate)
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


def x__extract_individual_objects__mutmut_66(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        parsed = None
                        if isinstance(parsed, dict):
                            objects.append(parsed)
                    except (json.JSONDecodeError, ValueError):
                        pass
        else:
            i += 1
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_67(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                        parsed = json.loads(None)
                        if isinstance(parsed, dict):
                            objects.append(parsed)
                    except (json.JSONDecodeError, ValueError):
                        pass
        else:
            i += 1
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_68(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
                            objects.append(None)
                    except (json.JSONDecodeError, ValueError):
                        pass
        else:
            i += 1
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_69(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i = 1
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_70(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i -= 1
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_71(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            i += 2
        if i <= outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_72(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
        if i < outer_prev_i:
            break
    return objects


def x__extract_individual_objects__mutmut_73(text: str) -> list[dict[str, Any]]:
    """Scan text for balanced curly brace blocks and parse each valid JSON object.

    Handles truncated responses or arrays with trailing syntax errors by
    extracting every syntactically valid object individually.
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
            return
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
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_22'] = x__extract_individual_objects__mutmut_22 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_23'] = x__extract_individual_objects__mutmut_23 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_24'] = x__extract_individual_objects__mutmut_24 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_25'] = x__extract_individual_objects__mutmut_25 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_26'] = x__extract_individual_objects__mutmut_26 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_27'] = x__extract_individual_objects__mutmut_27 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_28'] = x__extract_individual_objects__mutmut_28 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_29'] = x__extract_individual_objects__mutmut_29 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_30'] = x__extract_individual_objects__mutmut_30 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_31'] = x__extract_individual_objects__mutmut_31 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_32'] = x__extract_individual_objects__mutmut_32 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_33'] = x__extract_individual_objects__mutmut_33 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_34'] = x__extract_individual_objects__mutmut_34 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_35'] = x__extract_individual_objects__mutmut_35 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_36'] = x__extract_individual_objects__mutmut_36 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_37'] = x__extract_individual_objects__mutmut_37 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_38'] = x__extract_individual_objects__mutmut_38 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_39'] = x__extract_individual_objects__mutmut_39 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_40'] = x__extract_individual_objects__mutmut_40 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_41'] = x__extract_individual_objects__mutmut_41 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_42'] = x__extract_individual_objects__mutmut_42 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_43'] = x__extract_individual_objects__mutmut_43 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_44'] = x__extract_individual_objects__mutmut_44 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_45'] = x__extract_individual_objects__mutmut_45 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_46'] = x__extract_individual_objects__mutmut_46 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_47'] = x__extract_individual_objects__mutmut_47 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_48'] = x__extract_individual_objects__mutmut_48 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_49'] = x__extract_individual_objects__mutmut_49 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_50'] = x__extract_individual_objects__mutmut_50 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_51'] = x__extract_individual_objects__mutmut_51 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_52'] = x__extract_individual_objects__mutmut_52 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_53'] = x__extract_individual_objects__mutmut_53 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_54'] = x__extract_individual_objects__mutmut_54 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_55'] = x__extract_individual_objects__mutmut_55 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_56'] = x__extract_individual_objects__mutmut_56 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_57'] = x__extract_individual_objects__mutmut_57 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_58'] = x__extract_individual_objects__mutmut_58 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_59'] = x__extract_individual_objects__mutmut_59 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_60'] = x__extract_individual_objects__mutmut_60 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_61'] = x__extract_individual_objects__mutmut_61 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_62'] = x__extract_individual_objects__mutmut_62 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_63'] = x__extract_individual_objects__mutmut_63 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_64'] = x__extract_individual_objects__mutmut_64 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_65'] = x__extract_individual_objects__mutmut_65 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_66'] = x__extract_individual_objects__mutmut_66 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_67'] = x__extract_individual_objects__mutmut_67 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_68'] = x__extract_individual_objects__mutmut_68 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_69'] = x__extract_individual_objects__mutmut_69 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_70'] = x__extract_individual_objects__mutmut_70 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_71'] = x__extract_individual_objects__mutmut_71 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_72'] = x__extract_individual_objects__mutmut_72 # type: ignore # mutmut generated
mutants_x__extract_individual_objects__mutmut['x__extract_individual_objects__mutmut_73'] = x__extract_individual_objects__mutmut_73 # type: ignore # mutmut generated
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
    try:
        return json.loads(None)
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(None)
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(None, content))
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", None))
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(content))
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", ))
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"XX\1XX", content))
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", content))
        except (json.JSONDecodeError, ValueError):
            pass

    # 2. Markdown code fence match
    matches = None
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
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        try:
            return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", content))
        except (json.JSONDecodeError, ValueError):
            pass

    # 2. Markdown code fence match
    matches = _MARKDOWN_CODE_FENCE_PATTERN.findall(None)
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
        candidate_clean = None
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
            return json.loads(None)
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
                return json.loads(None)
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(None, candidate_clean))
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", None))
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(candidate_clean))
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", ))
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"XX\1XX", candidate_clean))
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
                break

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
    start_bracket = None
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
    start_bracket = content.find(None)
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
    start_bracket = content.rfind("[")
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
    start_bracket = content.find("XX[XX")
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
    end_bracket = None
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
    end_bracket = content.rfind(None)
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
    end_bracket = content.find("]")
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
    end_bracket = content.rfind("XX]XX")
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
    if start_bracket != -1 or end_bracket > start_bracket:
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
    if start_bracket == -1 and end_bracket > start_bracket:
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
    if start_bracket != +1 and end_bracket > start_bracket:
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
    if start_bracket != -2 and end_bracket > start_bracket:
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
    if start_bracket != -1 and end_bracket >= start_bracket:
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
        candidate = None
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
        candidate = content[start_bracket : end_bracket - 1].strip()
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
        candidate = content[start_bracket : end_bracket + 2].strip()
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
            return json.loads(None)
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


def x_extract_json_data__mutmut_37(raw_content: str) -> Any:
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
                return json.loads(None)
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


def x_extract_json_data__mutmut_38(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(None, candidate))
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


def x_extract_json_data__mutmut_39(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", None))
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


def x_extract_json_data__mutmut_40(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(candidate))
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


def x_extract_json_data__mutmut_41(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", ))
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


def x_extract_json_data__mutmut_42(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"XX\1XX", candidate))
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


def x_extract_json_data__mutmut_43(raw_content: str) -> Any:
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
    start_brace = None
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


def x_extract_json_data__mutmut_44(raw_content: str) -> Any:
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
    start_brace = content.find(None)
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


def x_extract_json_data__mutmut_45(raw_content: str) -> Any:
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
    start_brace = content.rfind("{")
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


def x_extract_json_data__mutmut_46(raw_content: str) -> Any:
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
    start_brace = content.find("XX{XX")
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


def x_extract_json_data__mutmut_47(raw_content: str) -> Any:
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
    end_brace = None
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


def x_extract_json_data__mutmut_48(raw_content: str) -> Any:
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
    end_brace = content.rfind(None)
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


def x_extract_json_data__mutmut_49(raw_content: str) -> Any:
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
    end_brace = content.find("}")
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


def x_extract_json_data__mutmut_50(raw_content: str) -> Any:
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
    end_brace = content.rfind("XX}XX")
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


def x_extract_json_data__mutmut_51(raw_content: str) -> Any:
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
    if start_brace != -1 or end_brace > start_brace:
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


def x_extract_json_data__mutmut_52(raw_content: str) -> Any:
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
    if start_brace == -1 and end_brace > start_brace:
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


def x_extract_json_data__mutmut_53(raw_content: str) -> Any:
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
    if start_brace != +1 and end_brace > start_brace:
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


def x_extract_json_data__mutmut_54(raw_content: str) -> Any:
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
    if start_brace != -2 and end_brace > start_brace:
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


def x_extract_json_data__mutmut_55(raw_content: str) -> Any:
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
    if start_brace != -1 and end_brace >= start_brace:
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


def x_extract_json_data__mutmut_56(raw_content: str) -> Any:
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
        candidate = None
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


def x_extract_json_data__mutmut_57(raw_content: str) -> Any:
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
        candidate = content[start_brace : end_brace - 1].strip()
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


def x_extract_json_data__mutmut_58(raw_content: str) -> Any:
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
        candidate = content[start_brace : end_brace + 2].strip()
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


def x_extract_json_data__mutmut_59(raw_content: str) -> Any:
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
            return json.loads(None)
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


def x_extract_json_data__mutmut_60(raw_content: str) -> Any:
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
                return json.loads(None)
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_61(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(None, candidate))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_62(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", None))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_63(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(candidate))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_64(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"\1", ))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_65(raw_content: str) -> Any:
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
                return json.loads(_TRAILING_COMMA_PATTERN.sub(r"XX\1XX", candidate))
            except (json.JSONDecodeError, ValueError):
                pass

    # 5. Extract individual JSON objects (handles truncated responses or partial arrays)
    extracted = _extract_individual_objects(content)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_66(raw_content: str) -> Any:
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
    extracted = None
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_67(raw_content: str) -> Any:
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
    extracted = _extract_individual_objects(None)
    if extracted:
        if len(extracted) == 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_68(raw_content: str) -> Any:
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
        if len(extracted) == 1 or "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_69(raw_content: str) -> Any:
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
        if len(extracted) != 1 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_70(raw_content: str) -> Any:
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
        if len(extracted) == 2 and "[" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_71(raw_content: str) -> Any:
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
        if len(extracted) == 1 and "XX[XX" not in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_72(raw_content: str) -> Any:
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
        if len(extracted) == 1 and "[" in content:
            return extracted[0]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_73(raw_content: str) -> Any:
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
            return extracted[1]
        return extracted

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:200]}...")


def x_extract_json_data__mutmut_74(raw_content: str) -> Any:
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

    raise ValueError(None)


def x_extract_json_data__mutmut_75(raw_content: str) -> Any:
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

    raise ValueError(f"Failed to extract valid JSON payload from content: {raw_content[:201]}...")

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
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_37'] = x_extract_json_data__mutmut_37 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_38'] = x_extract_json_data__mutmut_38 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_39'] = x_extract_json_data__mutmut_39 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_40'] = x_extract_json_data__mutmut_40 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_41'] = x_extract_json_data__mutmut_41 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_42'] = x_extract_json_data__mutmut_42 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_43'] = x_extract_json_data__mutmut_43 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_44'] = x_extract_json_data__mutmut_44 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_45'] = x_extract_json_data__mutmut_45 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_46'] = x_extract_json_data__mutmut_46 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_47'] = x_extract_json_data__mutmut_47 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_48'] = x_extract_json_data__mutmut_48 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_49'] = x_extract_json_data__mutmut_49 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_50'] = x_extract_json_data__mutmut_50 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_51'] = x_extract_json_data__mutmut_51 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_52'] = x_extract_json_data__mutmut_52 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_53'] = x_extract_json_data__mutmut_53 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_54'] = x_extract_json_data__mutmut_54 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_55'] = x_extract_json_data__mutmut_55 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_56'] = x_extract_json_data__mutmut_56 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_57'] = x_extract_json_data__mutmut_57 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_58'] = x_extract_json_data__mutmut_58 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_59'] = x_extract_json_data__mutmut_59 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_60'] = x_extract_json_data__mutmut_60 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_61'] = x_extract_json_data__mutmut_61 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_62'] = x_extract_json_data__mutmut_62 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_63'] = x_extract_json_data__mutmut_63 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_64'] = x_extract_json_data__mutmut_64 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_65'] = x_extract_json_data__mutmut_65 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_66'] = x_extract_json_data__mutmut_66 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_67'] = x_extract_json_data__mutmut_67 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_68'] = x_extract_json_data__mutmut_68 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_69'] = x_extract_json_data__mutmut_69 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_70'] = x_extract_json_data__mutmut_70 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_71'] = x_extract_json_data__mutmut_71 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_72'] = x_extract_json_data__mutmut_72 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_73'] = x_extract_json_data__mutmut_73 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_74'] = x_extract_json_data__mutmut_74 # type: ignore # mutmut generated
mutants_x_extract_json_data__mutmut['x_extract_json_data__mutmut_75'] = x_extract_json_data__mutmut_75 # type: ignore # mutmut generated
