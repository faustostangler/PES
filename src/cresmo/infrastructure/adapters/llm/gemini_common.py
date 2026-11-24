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
from typing import Any

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

_THINKING_LEVEL_ENUM_MAP: dict[str, types.ThinkingLevel] = {
    "minimal": types.ThinkingLevel.MINIMAL,
    "low": types.ThinkingLevel.LOW,
    "medium": types.ThinkingLevel.MEDIUM,
    "high": types.ThinkingLevel.HIGH,
}


def is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
    if isinstance(
        exc, (ConnectionError, TimeoutError, httpx.TransportError, httpx.TimeoutException)
    ):
        return True
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
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
    sleep_seconds = retry_state.next_action.sleep if retry_state.next_action is not None else 0.0
    logger.debug(
        "[GeminiRetry] Attempt %d failed (%s). Retrying in %.1fs...",
        retry_state.attempt_number,
        exc,
        sleep_seconds,
    )


@retry(
    retry=retry_if_exception(is_transient_cluster_error),
    wait=wait_random_exponential(min=2, max=20),
    stop=stop_after_attempt(3),
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

    normalized_model = model.removeprefix("gemini:").strip().lower()

    if normalized_model.startswith("gemma-4"):
        return "minimal" if level in ("minimal", "low") else "high"

    if normalized_model.startswith("gemini-4-hydrogen"):
        return "low" if level == "minimal" else level

    if normalized_model.startswith(("gemini-3.8-", "gemini-4-", "gemini-3.1-pro", "gemini-2.5-")):
        if level == "minimal":
            return "low"
        if level == "xhigh":
            return "high"
        return level

    if level == "xhigh":
        return "high"
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
    return types.ThinkingConfig.model_validate({"thinking_level": effective})


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
