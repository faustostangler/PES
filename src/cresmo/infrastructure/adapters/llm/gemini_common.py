"""Shared Google Gemini API resilience, retry logging, and thinking-level utilities.

Centralizes transient error classification, tenacity retry logging, and
model-aware ThinkingConfig construction across GeminiLLMAdapter and
GeminiJudgeAdapter to eliminate code duplication (DRY).

Conforms to:
    - ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation
    - ADR-064: Gemini Free-Tier Catalog, Thinking Level Governance & Param Hygiene
"""

from __future__ import annotations

from collections.abc import Callable
from http import HTTPStatus
from typing import Any, Final

import httpx
import structlog
from google.genai import errors, types
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

from cresmo.infrastructure.adapters.llm.gemini_pool import (
    CredentialPoolExhaustedError,
    is_quota_exhausted_error,
)
from cresmo.infrastructure.config import GEMINI_THINKING_LEVELS

logger = structlog.get_logger(__name__)

TRANSIENT_NETWORK_PATTERNS: tuple[str, ...] = (
    "503",
    "504",
    "429",
    "UNAVAILABLE",
    "DEADLINE_EXCEEDED",
    "ResourceExhausted",
    "RESOURCE_EXHAUSTED",
    "high demand",
    "rate limit",
    "quota",
    "Connection reset",
    "connection reset",
    "Server disconnected",
    "RemoteDisconnected",
    "RemoteProtocolError",
    "broken pipe",
    "peer closed",
    "connection closed",
    "closed before response",
    "timed out",
    "timeout",
    "socket.timeout",
)

GEMINI_MODEL_PREFIX: Final[str] = "gemini:"
_THINKING_MINIMAL: Final[str] = "minimal"
_THINKING_LOW: Final[str] = "low"
_THINKING_MEDIUM: Final[str] = "medium"
_THINKING_HIGH: Final[str] = "high"
_THINKING_XHIGH: Final[str] = "xhigh"
_GEMMA_4_MODEL_PREFIX: Final[str] = "gemma-4"
_GEMINI_4_HYDROGEN_MODEL_PREFIX: Final[str] = "gemini-4-hydrogen"
_STANDARD_CLAMP_MODEL_PREFIXES: Final[tuple[str, ...]] = (
    "gemini-3.8-",
    "gemini-4-",
    "gemini-3.1-pro",
    "gemini-2.5-",
)
_TRANSIENT_HTTP_STATUS_CODES: Final[frozenset[int]] = frozenset(
    {
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
)
_RETRY_MIN_WAIT_SECONDS: Final[int] = 2
_RETRY_MAX_WAIT_SECONDS: Final[int] = 20
_RETRY_MAX_ATTEMPTS: Final[int] = 3
_ZERO_SLEEP_SECONDS: Final[float] = 0.0
_KEY_THINKING_LEVEL: Final[str] = "thinking_level"

_THINKING_LEVEL_ENUM_MAP: Final[dict[str, types.ThinkingLevel]] = {
    _THINKING_MINIMAL: types.ThinkingLevel.MINIMAL,
    _THINKING_LOW: types.ThinkingLevel.LOW,
    _THINKING_MEDIUM: types.ThinkingLevel.MEDIUM,
    _THINKING_HIGH: types.ThinkingLevel.HIGH,
}


def is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
    if isinstance(
        exc, (ConnectionError, TimeoutError, httpx.TransportError, httpx.TimeoutException)
    ):
        return True
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in _TRANSIENT_HTTP_STATUS_CODES
    msg = str(exc)
    return any(pattern in msg for pattern in TRANSIENT_NETWORK_PATTERNS)


def is_transient_cluster_error(exc: BaseException) -> bool:
    """Determine if an exception represents a retryable 5xx or cluster network condition.

    CRITICAL INVARIANT (ADR-041 §2.3):
    HTTP 429 (quota exhaustion) is NOT retried here because it must immediately trigger
    credential rotation via GeminiCredentialPool.
    """
    if is_quota_exhausted_error(exc):
        return False
    return is_transient_genai_error(exc)


def log_gemini_retry_attempt(retry_state: RetryCallState) -> None:
    """Emit structured debug log before sleeping between Gemini cluster retry attempts."""
    exc = (
        retry_state.outcome.exception()
        if retry_state.outcome is not None and retry_state.outcome.failed
        else None
    )
    sleep_seconds = (
        retry_state.next_action.sleep
        if retry_state.next_action is not None
        else _ZERO_SLEEP_SECONDS
    )
    logger.debug(
        "[GeminiRetry] Attempt %d failed (%s). Retrying in %.1fs...",
        retry_state.attempt_number,
        exc,
        sleep_seconds,
    )


@retry(
    retry=retry_if_exception(is_transient_cluster_error),
    wait=wait_random_exponential(min=_RETRY_MIN_WAIT_SECONDS, max=_RETRY_MAX_WAIT_SECONDS),
    stop=stop_after_attempt(_RETRY_MAX_ATTEMPTS),
    before_sleep=log_gemini_retry_attempt,
    reraise=True,
)
def generate_content_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Execute Google GenAI content generation with bounded exponential backoff on transient errors."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )


def execute_with_model_failover[T](
    *,
    primary_model: str,
    fallback_model: str | None,
    operation: Callable[[str, bool], T],
    adapter_label: str,
) -> T:
    """Execute Gemini model invocation with secondary model failover on non-quota failures."""
    try:
        return operation(primary_model, False)
    except Exception as exc:
        if (
            isinstance(exc, CredentialPoolExhaustedError)
            or is_quota_exhausted_error(exc)
            or not fallback_model
            or fallback_model == primary_model
        ):
            raise
        logger.warning(
            "[%s] Primary model '%s' failed (%s). Failing over to '%s'.",
            adapter_label,
            primary_model,
            exc,
            fallback_model,
        )
        return operation(fallback_model, True)


def resolve_effective_thinking_level(
    model: str,
    thinking_level: str | None,
) -> str | None:
    """Normalize and clamp thinking_level to values supported by the target Gemini/Gemma model.

    Why clamping is required: Free-tier models expose heterogeneous reasoning-effort tiers
    (e.g. Gemma 4 accepts only 'minimal'/'high', Gemini 4 Hydrogen rejects 'minimal' while
    supporting 'xhigh', Gemini 3.8 Flash accepts 'low'/'medium'/'high'). Clamping ensures
    swapping GEMINI_MODEL never triggers HTTP 400 InvalidArgument errors.
    """
    if thinking_level is None:
        return None

    level = thinking_level.strip().lower()
    if level not in GEMINI_THINKING_LEVELS:
        raise ValueError(
            f"Unsupported thinking_level '{thinking_level}'. Expected one of {GEMINI_THINKING_LEVELS}."
        )

    normalized_model = model.removeprefix(GEMINI_MODEL_PREFIX).strip().lower()

    if normalized_model.startswith(_GEMMA_4_MODEL_PREFIX):
        return _THINKING_MINIMAL if level in (_THINKING_MINIMAL, _THINKING_LOW) else _THINKING_HIGH

    if normalized_model.startswith(_GEMINI_4_HYDROGEN_MODEL_PREFIX):
        return _THINKING_LOW if level == _THINKING_MINIMAL else level

    if normalized_model.startswith(_STANDARD_CLAMP_MODEL_PREFIXES):
        if level == _THINKING_MINIMAL:
            return _THINKING_LOW
        if level == _THINKING_XHIGH:
            return _THINKING_HIGH
        return level

    if level == _THINKING_XHIGH:
        return _THINKING_HIGH
    return level


def build_thinking_config(
    model: str,
    thinking_level: str | None,
) -> types.ThinkingConfig | None:
    """Build Google GenAI ThinkingConfig for the target model and thinking_level."""
    effective = resolve_effective_thinking_level(model=model, thinking_level=thinking_level)
    if effective is None or thinking_level is None:
        return None

    requested_norm = thinking_level.strip().lower()
    if effective != requested_norm:
        logger.debug(
            "[GeminiThinking] Clamped thinking_level '%s' -> '%s' for model '%s'",
            requested_norm,
            effective,
            model,
        )

    enum_val = _THINKING_LEVEL_ENUM_MAP.get(effective)
    if enum_val is not None:
        return types.ThinkingConfig(thinking_level=enum_val)

    # SDK 2.22.0 ThinkingLevel enum omits 'xhigh' supported by Gemini 4 Hydrogen
    return types.ThinkingConfig.model_validate({_KEY_THINKING_LEVEL: effective})


__all__ = [
    "TRANSIENT_NETWORK_PATTERNS",
    "build_thinking_config",
    "execute_with_model_failover",
    "generate_content_with_retry",
    "is_transient_cluster_error",
    "is_transient_genai_error",
    "log_gemini_retry_attempt",
    "resolve_effective_thinking_level",
]
