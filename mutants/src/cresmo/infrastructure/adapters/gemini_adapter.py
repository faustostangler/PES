"""Production LLM adapter integrating Google Gemini API and Langfuse Observability.

Adheres to EVAL-001 rubrics and stangler-surgery telemetry standards, capturing
prompt versions, trace IDs, latency, token counts, and structured outputs.
"""

from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import errors, types
from langfuse import Langfuse, observe
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from cresmo.application.ports import LLMTransformationPort


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__is_transient_genai_error__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__is_transient_genai_error__mutmut)
def _is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_orig(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_1(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_2(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_3(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_4(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_5(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_6(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_7(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_8(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_9(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_10(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_11(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_12(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_13(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_14(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_15(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_16(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_17(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        None
    )


def x__is_transient_genai_error__mutmut_18(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_19(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_20(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_21(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_22(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_23(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_24(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_25(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_26(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "XXhigh demandXX",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_27(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "HIGH DEMAND",
            "rate limit",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_28(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "XXrate limitXX",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_29(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "RATE LIMIT",
            "Connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_30(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "XXConnection resetXX",
        )
    )


def x__is_transient_genai_error__mutmut_31(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
            "connection reset",
        )
    )


def x__is_transient_genai_error__mutmut_32(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
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
            "high demand",
            "rate limit",
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


@retry(
    retry=retry_if_exception(_is_transient_genai_error),
    wait=wait_random_exponential(min=2, max=20),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _generate_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Execute model content generation with exponential backoff on transient errors."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
mutants_xǁGeminiLLMAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore


class GeminiLLMAdapter(LLMTransformationPort):
    """Production LLM adapter with Google Gemini API and Langfuse telemetry."""

    @_mutmut_mutated(mutants_xǁGeminiLLMAdapterǁ__init____mutmut)
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_orig(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_1(
        self,
        api_key: str | None = None,
        model_name: str = "XXgemini-3.5-flash-liteXX",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_2(
        self,
        api_key: str | None = None,
        model_name: str = "GEMINI-3.5-FLASH-LITE",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_3(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "XXgemini-3.1-flash-liteXX",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_4(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "GEMINI-3.1-FLASH-LITE",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_5(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8193,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_6(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = None
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_7(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = None
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_8(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = None

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_9(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_10(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = None
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_11(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get(None):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_12(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("XXLANGFUSE_PUBLIC_KEYXX"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_13(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("langfuse_public_key"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_14(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = None
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_15(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = ""

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_16(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_17(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = None
        else:
            self._client = genai.Client(api_key=api_key)

    def xǁGeminiLLMAdapterǁ__init____mutmut_18(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = None

    def xǁGeminiLLMAdapterǁ__init____mutmut_19(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=None)

    @observe(as_type="generation")
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation contract with full Langfuse observability span.

        Args:
            prompt: Text prompt for generation.
            system_instruction: Optional system instruction directive.
            temperature: Generation sampling temperature.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text.
        """
        eff_temperature = 0.2 if temperature is None else temperature
        config = types.GenerateContentConfig(
            temperature=eff_temperature,
            max_output_tokens=self.max_output_tokens,
            system_instruction=system_instruction,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        active_model = self.model_name
        try:
            response = _generate_with_retry(
                client=self._client,
                model=active_model,
                contents=prompt,
                config=config,
            )
        except Exception:
            if self.fallback_model_name and self.fallback_model_name != self.model_name:
                active_model = self.fallback_model_name
                response = _generate_with_retry(
                    client=self._client,
                    model=active_model,
                    contents=prompt,
                    config=config,
                )
            else:
                raise

        response_text = response.text or ""

        # Extract usage metadata
        usage_meta = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or len(prompt.split())
        candidate_tokens = getattr(usage_meta, "candidates_token_count", 0) or len(
            response_text.split()
        )

        # Bind output and token metadata to Langfuse generation span if active
        if self._langfuse is not None:
            try:
                self._langfuse.update_current_generation(
                    model=active_model,
                    output=response_text,
                    usage_details={"input": prompt_tokens, "output": candidate_tokens},
                )
            except (AttributeError, RuntimeError, ValueError):
                pass

        return response_text

mutants_xǁGeminiLLMAdapterǁ__init____mutmut['_mutmut_orig'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_1'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_2'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_3'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_4'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_5'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_6'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_7'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_8'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_9'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_10'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_11'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_12'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_13'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_14'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_15'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_16'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_17'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_18'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁGeminiLLMAdapterǁ__init____mutmut['xǁGeminiLLMAdapterǁ__init____mutmut_19'] = GeminiLLMAdapter.xǁGeminiLLMAdapterǁ__init____mutmut_19 # type: ignore # mutmut generated
