"""Gemini LLM-as-a-Judge Adapter for Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
from typing import Any

from google import genai
from google.genai import errors, types
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    MessageRole,
    PromptKey,
)
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
from cresmo.infrastructure.config import (
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    DEFAULT_JUDGE_TEMPERATURE,
)

logger = logging.getLogger(__name__)

DEFAULT_PASS_THRESHOLD: float = DEFAULT_JUDGE_PASS_THRESHOLD
DEFAULT_MODEL: str = DEFAULT_JUDGE_GEMINI_MODEL
DEFAULT_TEMPERATURE: float = DEFAULT_JUDGE_TEMPERATURE


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__clean_json_markdown__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__clean_json_markdown__mutmut)
def _clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_orig(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_1(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = None
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_2(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = None
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_3(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(None, cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_4(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", None)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_5(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_6(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", )
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_7(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"XX```(?:json)?\s*([\s\S]*?)\s*```XX", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_8(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:JSON)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def x__clean_json_markdown__mutmut_9(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(None).strip()
    return cleaned


def x__clean_json_markdown__mutmut_10(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(2).strip()
    return cleaned

mutants_x__clean_json_markdown__mutmut['_mutmut_orig'] = x__clean_json_markdown__mutmut_orig # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_1'] = x__clean_json_markdown__mutmut_1 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_2'] = x__clean_json_markdown__mutmut_2 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_3'] = x__clean_json_markdown__mutmut_3 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_4'] = x__clean_json_markdown__mutmut_4 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_5'] = x__clean_json_markdown__mutmut_5 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_6'] = x__clean_json_markdown__mutmut_6 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_7'] = x__clean_json_markdown__mutmut_7 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_8'] = x__clean_json_markdown__mutmut_8 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_9'] = x__clean_json_markdown__mutmut_9 # type: ignore # mutmut generated
mutants_x__clean_json_markdown__mutmut['x__clean_json_markdown__mutmut_10'] = x__clean_json_markdown__mutmut_10 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__is_transient_genai_error__mutmut)
def _is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_orig(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_1(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = None
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_2(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(None, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_3(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, None, None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_4(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr("code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_5(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_6(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", )
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_7(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "XXcodeXX", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_8(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "CODE", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_9(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code not in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_10(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (430, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_11(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 501, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_12(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 503, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_13(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 504, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_14(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 505)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_15(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = None
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_16(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(None)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_17(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        None
    )


def x__is_transient_genai_error__mutmut_18(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern not in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_19(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "XX503XX",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_20(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "XX429XX",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_21(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "XXUNAVAILABLEXX",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_22(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "unavailable",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_23(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "XXResourceExhaustedXX",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_24(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "resourceexhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_25(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "RESOURCEEXHAUSTED",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_26(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "XXRESOURCE_EXHAUSTEDXX",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_27(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "resource_exhausted",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_28(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "XXhigh demandXX",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_29(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "HIGH DEMAND",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_30(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "XXrate limitXX",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_31(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "RATE LIMIT",
            "quota",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_32(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "XXquotaXX",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_33(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "QUOTA",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_34(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "XXConnection resetXX",
        )
    )


def x__is_transient_genai_error__mutmut_35(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_36(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "CONNECTION RESET",
        )
    )

mutants_x__is_transient_genai_error__mutmut['_mutmut_orig'] = x__is_transient_genai_error__mutmut_orig # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_1'] = x__is_transient_genai_error__mutmut_1 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_2'] = x__is_transient_genai_error__mutmut_2 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_3'] = x__is_transient_genai_error__mutmut_3 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_4'] = x__is_transient_genai_error__mutmut_4 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_5'] = x__is_transient_genai_error__mutmut_5 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_6'] = x__is_transient_genai_error__mutmut_6 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_7'] = x__is_transient_genai_error__mutmut_7 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_8'] = x__is_transient_genai_error__mutmut_8 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_9'] = x__is_transient_genai_error__mutmut_9 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_10'] = x__is_transient_genai_error__mutmut_10 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_11'] = x__is_transient_genai_error__mutmut_11 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_12'] = x__is_transient_genai_error__mutmut_12 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_13'] = x__is_transient_genai_error__mutmut_13 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_14'] = x__is_transient_genai_error__mutmut_14 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_15'] = x__is_transient_genai_error__mutmut_15 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_16'] = x__is_transient_genai_error__mutmut_16 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_17'] = x__is_transient_genai_error__mutmut_17 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_18'] = x__is_transient_genai_error__mutmut_18 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_19'] = x__is_transient_genai_error__mutmut_19 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_20'] = x__is_transient_genai_error__mutmut_20 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_21'] = x__is_transient_genai_error__mutmut_21 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_22'] = x__is_transient_genai_error__mutmut_22 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_23'] = x__is_transient_genai_error__mutmut_23 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_24'] = x__is_transient_genai_error__mutmut_24 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_25'] = x__is_transient_genai_error__mutmut_25 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_26'] = x__is_transient_genai_error__mutmut_26 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_27'] = x__is_transient_genai_error__mutmut_27 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_28'] = x__is_transient_genai_error__mutmut_28 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_29'] = x__is_transient_genai_error__mutmut_29 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_30'] = x__is_transient_genai_error__mutmut_30 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_31'] = x__is_transient_genai_error__mutmut_31 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_32'] = x__is_transient_genai_error__mutmut_32 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_33'] = x__is_transient_genai_error__mutmut_33 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_34'] = x__is_transient_genai_error__mutmut_34 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_35'] = x__is_transient_genai_error__mutmut_35 # type: ignore # mutmut generated
mutants_x__is_transient_genai_error__mutmut['x__is_transient_genai_error__mutmut_36'] = x__is_transient_genai_error__mutmut_36 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__wait_for_quota_or_backoff__mutmut)
def _wait_for_quota_or_backoff(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_orig(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_1(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome or retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_2(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = None
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_3(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_4(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = None
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_5(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(None)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_6(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = None
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_7(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(None, msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_8(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", None)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_9(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_10(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", )
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_11(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"XX[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)sXX", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_12(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_13(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[PP]LEASE RETRY IN ([0-9]+(?:\.[0-9]+)?)S", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_14(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_15(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = None
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_16(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(None, msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_17(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", None)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_18(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_19(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", )
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_20(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"XX['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]XX", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_21(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retrydelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_22(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]RETRYDELAY['\"]:\s*['\"]([0-9]+)S?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_23(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = None
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_24(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(None)
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_25(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(None))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_26(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(2))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_27(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = None
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_28(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested - random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_29(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(None, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_30(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, None)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_31(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_32(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, )
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_33(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(2.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_34(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 4.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_35(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        None,
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_36(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        None,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_37(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_38(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_39(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "XXGemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...XX",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_40(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "gemini quota exhausted (429). server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_41(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "GEMINI QUOTA EXHAUSTED (429). SERVER REQUESTED BACKOFF: WAITING %.1FS BEFORE RETRY...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_42(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = None
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_43(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=None, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_44(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=None)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_45(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_46(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, )
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_47(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=6, max=60)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_48(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=61)
    return float(exp_wait(retry_state))


def x__wait_for_quota_or_backoff__mutmut_49(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(None)


def x__wait_for_quota_or_backoff__mutmut_50(retry_state: RetryCallState) -> float:
    """Compute wait duration honoring API retryDelay if returned by Gemini, else exponential backoff."""
    if retry_state.outcome and retry_state.outcome.failed:
        exc = retry_state.outcome.exception()
        if exc is not None:
            msg = str(exc)
            match = re.search(r"[Pp]lease retry in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if not match:
                match = re.search(r"['\"]retryDelay['\"]:\s*['\"]([0-9]+)s?['\"]", msg)
            if match:
                try:
                    suggested = float(match.group(1))
                    wait_sec = suggested + random.uniform(1.0, 3.0)
                    logger.warning(
                        "Gemini quota exhausted (429). Server requested backoff: waiting %.1fs before retry...",
                        wait_sec,
                    )
                    return wait_sec
                except (ValueError, TypeError):
                    pass
    exp_wait = wait_random_exponential(min=5, max=60)
    return float(exp_wait(None))

mutants_x__wait_for_quota_or_backoff__mutmut['_mutmut_orig'] = x__wait_for_quota_or_backoff__mutmut_orig # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_1'] = x__wait_for_quota_or_backoff__mutmut_1 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_2'] = x__wait_for_quota_or_backoff__mutmut_2 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_3'] = x__wait_for_quota_or_backoff__mutmut_3 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_4'] = x__wait_for_quota_or_backoff__mutmut_4 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_5'] = x__wait_for_quota_or_backoff__mutmut_5 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_6'] = x__wait_for_quota_or_backoff__mutmut_6 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_7'] = x__wait_for_quota_or_backoff__mutmut_7 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_8'] = x__wait_for_quota_or_backoff__mutmut_8 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_9'] = x__wait_for_quota_or_backoff__mutmut_9 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_10'] = x__wait_for_quota_or_backoff__mutmut_10 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_11'] = x__wait_for_quota_or_backoff__mutmut_11 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_12'] = x__wait_for_quota_or_backoff__mutmut_12 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_13'] = x__wait_for_quota_or_backoff__mutmut_13 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_14'] = x__wait_for_quota_or_backoff__mutmut_14 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_15'] = x__wait_for_quota_or_backoff__mutmut_15 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_16'] = x__wait_for_quota_or_backoff__mutmut_16 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_17'] = x__wait_for_quota_or_backoff__mutmut_17 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_18'] = x__wait_for_quota_or_backoff__mutmut_18 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_19'] = x__wait_for_quota_or_backoff__mutmut_19 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_20'] = x__wait_for_quota_or_backoff__mutmut_20 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_21'] = x__wait_for_quota_or_backoff__mutmut_21 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_22'] = x__wait_for_quota_or_backoff__mutmut_22 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_23'] = x__wait_for_quota_or_backoff__mutmut_23 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_24'] = x__wait_for_quota_or_backoff__mutmut_24 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_25'] = x__wait_for_quota_or_backoff__mutmut_25 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_26'] = x__wait_for_quota_or_backoff__mutmut_26 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_27'] = x__wait_for_quota_or_backoff__mutmut_27 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_28'] = x__wait_for_quota_or_backoff__mutmut_28 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_29'] = x__wait_for_quota_or_backoff__mutmut_29 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_30'] = x__wait_for_quota_or_backoff__mutmut_30 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_31'] = x__wait_for_quota_or_backoff__mutmut_31 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_32'] = x__wait_for_quota_or_backoff__mutmut_32 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_33'] = x__wait_for_quota_or_backoff__mutmut_33 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_34'] = x__wait_for_quota_or_backoff__mutmut_34 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_35'] = x__wait_for_quota_or_backoff__mutmut_35 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_36'] = x__wait_for_quota_or_backoff__mutmut_36 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_37'] = x__wait_for_quota_or_backoff__mutmut_37 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_38'] = x__wait_for_quota_or_backoff__mutmut_38 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_39'] = x__wait_for_quota_or_backoff__mutmut_39 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_40'] = x__wait_for_quota_or_backoff__mutmut_40 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_41'] = x__wait_for_quota_or_backoff__mutmut_41 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_42'] = x__wait_for_quota_or_backoff__mutmut_42 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_43'] = x__wait_for_quota_or_backoff__mutmut_43 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_44'] = x__wait_for_quota_or_backoff__mutmut_44 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_45'] = x__wait_for_quota_or_backoff__mutmut_45 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_46'] = x__wait_for_quota_or_backoff__mutmut_46 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_47'] = x__wait_for_quota_or_backoff__mutmut_47 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_48'] = x__wait_for_quota_or_backoff__mutmut_48 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_49'] = x__wait_for_quota_or_backoff__mutmut_49 # type: ignore # mutmut generated
mutants_x__wait_for_quota_or_backoff__mutmut['x__wait_for_quota_or_backoff__mutmut_50'] = x__wait_for_quota_or_backoff__mutmut_50 # type: ignore # mutmut generated


@retry(
    retry=retry_if_exception(_is_transient_genai_error),
    wait=_wait_for_quota_or_backoff,
    stop=stop_after_attempt(5),
    reraise=True,
)
def _generate_content_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Generate content with automatic exponential backoff for transient rate limits (429)."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut: MutantDict = {}  # type: ignore


class GeminiJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing Google Gemini API with structured outputs."""

    @_mutmut_mutated(mutants_xǁGeminiJudgeAdapterǁ__init____mutmut)
    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_orig(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_1(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = None
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_2(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = None
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_3(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = None
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_4(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = None
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_5(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = None
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def xǁGeminiJudgeAdapterǁ__init____mutmut_6(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = None

    def xǁGeminiJudgeAdapterǁ__init____mutmut_7(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider and JsonPromptProvider()

    @property
    def client(self) -> Any:
        """Lazy-instantiate the Google GenAI client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "Gemini API key must be provided explicitly via api_key or client. "
                    "Bypassing Pydantic Settings via direct os.getenv is prohibited (ADR-026 Rule 9)."
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    @_mutmut_mutated(mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut)
    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_orig(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_1(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = None
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_2(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = None

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_3(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = None

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_4(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            None,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_5(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=None,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_6(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=None,
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_7(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=None,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_8(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=None,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_9(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_10(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_11(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_12(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_13(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_14(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(None),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_15(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = None
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_16(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=None,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_17(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=None,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_18(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type=None,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_19(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=None,
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_20(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_21(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_22(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_23(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_24(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="XXapplication/jsonXX",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_25(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="APPLICATION/JSON",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_26(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=None),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_27(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_28(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = None
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_29(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role=None,
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_30(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=None,
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_31(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_32(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_33(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="XXmodelXX" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_34(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="MODEL" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_35(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role != MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_36(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "XXuserXX",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_37(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "USER",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_38(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=None)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_39(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = None
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_40(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=None,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_41(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=None,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_42(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=None,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_43(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=None,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_44(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_45(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_46(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_47(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_48(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = None
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_49(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text and "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_50(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "XX{}XX"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_51(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning(None, exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_52(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", None)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_53(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning(exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_54(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", )
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_55(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("XXGeminiJudgeAdapter invocation failed: %sXX", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_56(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("geminijudgeadapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_57(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GEMINIJUDGEADAPTER INVOCATION FAILED: %S", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_58(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = None

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_59(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) / 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_60(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() + start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_61(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1001.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_62(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = None
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_63(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(None)
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_64(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(None))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_65(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error(None, raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_66(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", None)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_67(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error(raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_68(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", )
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_69(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("XXFailed to parse Gemini judge response as JSON: %sXX", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_70(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("failed to parse gemini judge response as json: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_71(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("FAILED TO PARSE GEMINI JUDGE RESPONSE AS JSON: %S", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_72(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(None) from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_73(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = None
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_74(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get(None, []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_75(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", None):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_76(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get([]):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_77(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", ):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_78(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("XXcriteriaXX", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_79(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("CRITERIA", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_80(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = None
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_81(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(None)
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_82(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["XXcriterionXX"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_83(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["CRITERION"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_84(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = None
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_85(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(None, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_86(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, None)
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_87(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_88(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, )
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_89(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(1.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_90(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(None, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_91(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, None))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_92(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_93(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, ))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_94(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(2.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_95(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(None)))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_96(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["XXscoreXX"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_97(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["SCORE"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_98(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = None
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_99(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(None)
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_100(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get(None, score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_101(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", None))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_102(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get(score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_103(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", ))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_104(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("XXpassedXX", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_105(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("PASSED", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_106(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val > self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_107(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    None
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_108(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=None,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_109(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=None,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_110(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=None,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_111(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=None,
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_112(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_113(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_114(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_115(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_116(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(None),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_117(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get(None, "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_118(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", None)),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_119(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_120(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", )),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_121(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("XXreasoningXX", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_122(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("REASONING", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_123(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "XXXX")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_124(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug(None, parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_125(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", None)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_126(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug(parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_127(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", )

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_128(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("XXSkipping unparseable judge criterion item: %sXX", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_129(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_130(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("SKIPPING UNPARSEABLE JUDGE CRITERION ITEM: %S", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_131(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = None
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_132(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(None)
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_133(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get(None, 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_134(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", None))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_135(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get(0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_136(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", ))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_137(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("XXoverall_scoreXX", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_138(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("OVERALL_SCORE", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_139(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 1.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_140(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = None
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_141(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(None, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_142(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, None)
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_143(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_144(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, )
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_145(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(1.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_146(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(None, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_147(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, None))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_148(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_149(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, ))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_150(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(2.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_151(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = None

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_152(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(None)

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_153(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get(None, overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_154(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", None))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_155(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get(overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_156(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", ))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_157(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("XXpassedXX", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_158(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("PASSED", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_159(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score > self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_160(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=None,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_161(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=None,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_162(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=None,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_163(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=None,
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_164(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider=None,
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_165(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=None,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_166(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=None,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_167(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_168(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_169(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_170(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_171(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_172(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_173(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_174(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(None),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_175(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="XXgeminiXX",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    def xǁGeminiJudgeAdapterǁevaluate__mutmut_176(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]
            response = _generate_content_with_retry(
                client=self.client,
                model=self._model,
                contents=contents,
                config=config,
            )
            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="GEMINI",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold

    @property
    def temperature(self) -> float:
        """Return the sampling temperature."""
        return self._temperature

    @property
    def model(self) -> str:
        """Return the model identifier."""
        return self._model

mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['_mutmut_orig'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_1'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_2'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_3'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_4'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_5'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_6'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁ__init____mutmut['xǁGeminiJudgeAdapterǁ__init____mutmut_7'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁ__init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['_mutmut_orig'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_orig # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_1'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_1 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_2'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_2 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_3'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_3 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_4'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_4 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_5'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_5 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_6'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_6 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_7'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_7 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_8'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_8 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_9'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_9 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_10'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_10 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_11'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_11 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_12'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_12 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_13'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_13 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_14'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_14 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_15'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_15 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_16'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_16 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_17'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_17 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_18'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_18 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_19'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_19 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_20'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_20 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_21'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_21 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_22'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_22 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_23'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_23 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_24'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_24 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_25'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_25 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_26'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_26 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_27'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_27 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_28'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_28 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_29'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_29 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_30'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_30 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_31'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_31 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_32'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_32 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_33'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_33 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_34'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_34 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_35'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_35 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_36'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_36 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_37'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_37 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_38'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_38 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_39'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_39 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_40'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_40 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_41'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_41 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_42'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_42 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_43'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_43 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_44'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_44 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_45'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_45 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_46'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_46 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_47'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_47 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_48'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_48 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_49'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_49 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_50'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_50 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_51'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_51 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_52'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_52 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_53'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_53 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_54'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_54 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_55'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_55 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_56'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_56 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_57'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_57 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_58'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_58 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_59'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_59 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_60'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_60 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_61'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_61 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_62'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_62 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_63'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_63 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_64'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_64 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_65'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_65 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_66'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_66 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_67'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_67 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_68'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_68 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_69'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_69 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_70'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_70 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_71'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_71 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_72'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_72 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_73'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_73 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_74'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_74 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_75'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_75 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_76'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_76 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_77'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_77 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_78'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_78 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_79'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_79 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_80'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_80 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_81'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_81 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_82'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_82 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_83'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_83 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_84'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_84 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_85'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_85 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_86'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_86 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_87'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_87 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_88'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_88 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_89'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_89 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_90'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_90 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_91'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_91 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_92'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_92 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_93'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_93 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_94'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_94 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_95'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_95 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_96'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_96 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_97'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_97 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_98'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_98 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_99'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_99 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_100'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_100 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_101'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_101 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_102'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_102 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_103'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_103 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_104'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_104 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_105'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_105 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_106'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_106 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_107'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_107 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_108'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_108 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_109'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_109 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_110'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_110 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_111'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_111 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_112'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_112 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_113'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_113 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_114'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_114 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_115'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_115 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_116'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_116 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_117'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_117 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_118'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_118 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_119'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_119 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_120'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_120 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_121'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_121 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_122'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_122 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_123'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_123 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_124'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_124 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_125'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_125 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_126'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_126 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_127'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_127 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_128'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_128 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_129'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_129 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_130'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_130 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_131'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_131 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_132'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_132 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_133'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_133 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_134'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_134 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_135'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_135 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_136'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_136 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_137'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_137 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_138'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_138 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_139'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_139 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_140'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_140 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_141'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_141 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_142'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_142 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_143'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_143 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_144'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_144 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_145'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_145 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_146'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_146 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_147'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_147 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_148'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_148 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_149'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_149 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_150'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_150 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_151'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_151 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_152'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_152 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_153'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_153 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_154'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_154 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_155'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_155 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_156'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_156 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_157'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_157 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_158'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_158 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_159'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_159 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_160'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_160 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_161'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_161 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_162'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_162 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_163'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_163 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_164'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_164 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_165'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_165 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_166'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_166 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_167'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_167 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_168'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_168 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_169'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_169 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_170'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_170 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_171'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_171 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_172'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_172 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_173'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_173 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_174'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_174 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_175'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_175 # type: ignore # mutmut generated
mutants_xǁGeminiJudgeAdapterǁevaluate__mutmut['xǁGeminiJudgeAdapterǁevaluate__mutmut_176'] = GeminiJudgeAdapter.xǁGeminiJudgeAdapterǁevaluate__mutmut_176 # type: ignore # mutmut generated


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_PASS_THRESHOLD",
    "DEFAULT_TEMPERATURE",
    "GeminiJudgeAdapter",
]
