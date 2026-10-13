"""Gemini Credential Pool and Quota-Aware Failover Rotation.

Implements Strategy A1 + B2:
- Primary key (index 0) is always prioritized.
- Subsequent keys serve as successive fallbacks when earlier keys are in cooldown.
- Key rotation happens ONLY on HTTP 429 (RESOURCE_EXHAUSTED / quota exhaustion).
- HTTP 503 (UNAVAILABLE / high demand) does NOT rotate credentials.
- Recovery timer uses the server's provided retryDelay; as soon as a higher-priority
  key's cooldown expires, it immediately regains priority.
- If all keys are in cooldown, raises CredentialPoolExhaustedError (fail-fast).
- Secret keys are never exposed in log output (obfuscated sha256 alias format).

Conforms to:
    - ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation
    - SPEC-041: Gemini Credential Pool Specifications
"""

from __future__ import annotations

import hashlib
import logging
import re
import threading
import time
from collections.abc import Callable
from typing import Any, TypeVar

from google import genai
from google.genai import errors

__all__ = [
    "CredentialPoolExhaustedError",
    "GeminiCredentialPool",
    "is_quota_exhausted_error",
    "parse_retry_delay_from_error",
]

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CredentialPoolExhaustedError(RuntimeError):
    """Raised when all credentials in the pool are temporarily in cooldown."""

    def __init__(self, retry_after_seconds: float, message: str | None = None) -> None:
        self.retry_after_seconds = max(0.0, retry_after_seconds)
        formatted_message = message or (
            f"All Gemini API credentials are currently exhausted in cooldown. "
            f"Earliest credential will recover in {self.retry_after_seconds:.1f}s."
        )
        super().__init__(formatted_message)


def parse_retry_delay_from_error(exc: BaseException, default_delay: float = 60.0) -> float:
    """Extract retry delay in seconds from Google GenAI error messages or details.

    Supports patterns like:
    - "Please retry in 45s" / "Please retry in 45.2s"
    - 'retryDelay': '33968s' / 'retry_delay': '33968s'
    - 'retryDelay: "33968s"'
    - violation descriptions with seconds.

    Args:
        exc: Exception raised by Google GenAI.
        default_delay: Fallback cooldown seconds if no retryDelay is extracted.

    Returns:
        Extracted or default cooldown delay in seconds.
    """
    msg = str(exc)
    # Pattern 1: Please retry in X.Xs
    match = re.search(r"[Pp]lease retry in\s+([0-9]+(?:\.[0-9]+)?)\s*s", msg)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass

    # Pattern 2: retryDelay: "33968s" or 'retryDelay': '33968s'
    match = re.search(r"retry_?[Dd]elay['\"]?\s*:\s*['\"]?([0-9]+(?:\.[0-9]+)?)\s*s?['\"]?", msg)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass

    # Pattern 3: quota reset or backoff in seconds
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*s\s*backoff", msg)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass

    return default_delay


def is_quota_exhausted_error(exc: BaseException) -> bool:
    """Determine if an exception represents an HTTP 429 quota exhaustion.

    CRITICAL INVARIANT (ADR-041 §2.3):
    - Rotation occurs ONLY on HTTP 429 (RESOURCE_EXHAUSTED).
    - HTTP 503 (UNAVAILABLE / server overloaded / high demand) is NOT quota exhaustion
      and must NOT trigger credential rotation.

    Args:
        exc: Raised exception to classify.

    Returns:
        True if the error is specifically HTTP 429 / quota exhaustion; False otherwise.
    """
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        if code == 429:
            return True
        if code in (500, 502, 503, 504):
            return False

    msg = str(exc)

    # Explicitly exclude 503 and high demand first
    if any(p in msg for p in ("503", "UNAVAILABLE", "high demand", "Service Unavailable")):
        return False

    # Match 429 / ResourceExhausted indicators
    return any(
        p in msg
        for p in (
            "429",
            "ResourceExhausted",
            "RESOURCE_EXHAUSTED",
            "Too Many Requests",
            "Quota exceeded",
            "quota exhausted",
            "Exceeded rate limit",
        )
    )


class GeminiCredentialPool:
    """Thread-safe credential pool managing prioritized failover and cooldown recovery.

    Prioritization:
    - Primary key (index 0) is always preferred.
    - If index 0 is in cooldown, falls back to index 1, index 2, etc.
    - As soon as index 0's cooldown expires, the next lease() immediately picks index 0.
    """

    def __init__(
        self,
        keys: list[str],
        client_factory: Callable[[str], Any] | None = None,
    ) -> None:
        """Initialize the credential pool with an ordered list of API keys.

        Args:
            keys: Ordered list of Gemini API keys (index 0 has highest priority).
            client_factory: Optional factory callable to instantiate GenAI clients.
        """
        cleaned_keys = [k.strip() for k in keys if k and k.strip()]
        if not cleaned_keys:
            raise ValueError("GeminiCredentialPool requires at least one API key.")

        self._keys = cleaned_keys
        self._client_factory = client_factory or (
            lambda k: genai.Client(api_key=k) if k else genai.Client()
        )
        self._lock = threading.Lock()

        # Cooldown map: key_str -> monotonic timestamp when cooldown expires
        self._cooldown_until: dict[str, float] = {k: 0.0 for k in self._keys}

        # Client cache: key_str -> genai.Client instance
        self._clients: dict[str, Any] = {}
        # Pre-instantiate primary client for fail-fast verification
        if self._keys:
            self._clients[self._keys[0]] = self._client_factory(self._keys[0])

        # Pre-generate masked aliases: "key#idx:hash4"
        self._aliases: dict[str, str] = {}
        for idx, key in enumerate(self._keys):
            masked_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()[:4]
            self._aliases[key] = f"key#{idx}:{masked_hash}"

    @property
    def key_count(self) -> int:
        """Total number of credentials managed by the pool."""
        return len(self._keys)

    def get_alias(self, key_str: str) -> str:
        """Return the obfuscated identifier for a given key string."""
        return self._aliases.get(
            key_str,
            f"key#?:{hashlib.sha256(key_str.encode('utf-8')).hexdigest()[:4]}",
        )

    def lease(self) -> tuple[str, Any, str]:
        """Lease the highest-priority non-cooldown credential.

        Returns:
            Tuple of (raw_key, client_instance, masked_alias).

        Raises:
            CredentialPoolExhaustedError: If all credentials in the pool are in cooldown.
        """
        now = time.monotonic()
        with self._lock:
            # 1. Search sequentially from primary (index 0) to fallbacks
            for key in self._keys:
                cooldown_exp = self._cooldown_until.get(key, 0.0)
                if now >= cooldown_exp:
                    # Key is active
                    client = self._get_or_create_client(key)
                    return key, client, self._aliases[key]

            # 2. All keys are currently in cooldown: calculate minimal wait time
            min_wait = min(self._cooldown_until[k] for k in self._keys) - now
            raise CredentialPoolExhaustedError(
                retry_after_seconds=max(0.1, min_wait),
                message=(
                    f"All {len(self._keys)} Gemini credentials in pool are in cooldown. "
                    f"Earliest key will recover in {max(0.1, min_wait):.1f}s."
                ),
            )

    def report_quota_exhausted(self, key_str: str, retry_delay_seconds: float) -> None:
        """Mark a specific key in cooldown for the requested duration.

        Args:
            key_str: The raw key that hit 429.
            retry_delay_seconds: Duration in seconds to keep this key in cooldown.
        """
        alias = self.get_alias(key_str)
        delay = max(0.0, float(retry_delay_seconds))
        now = time.monotonic()
        cooldown_target = now + delay

        with self._lock:
            self._cooldown_until[key_str] = cooldown_target

        logger.warning(
            "[GeminiCredentialPool] Quota exhausted (429) for credential %s. "
            "Marked in cooldown for %.1fs. Failing over to next key in pool.",
            alias,
            delay,
        )

    def execute_with_failover(
        self,
        operation: Callable[[Any], T],
    ) -> T:
        """Execute an operation with client leasing and automatic 429 failover.

        Iterates through available keys if HTTP 429 is encountered, respecting
        cooldowns and raising immediately if all keys are exhausted or on non-429 errors.

        Args:
            operation: Callable accepting a `genai.Client` and returning a result.

        Returns:
            Result of successful operation execution.
        """
        attempted_keys: set[str] = set()

        while True:
            key, client, _alias = self.lease()

            if key in attempted_keys and len(attempted_keys) >= len(self._keys):
                # We already attempted all keys in this single operation attempt
                now = time.monotonic()
                min_wait = min(self._cooldown_until[k] for k in self._keys) - now
                raise CredentialPoolExhaustedError(retry_after_seconds=max(0.1, min_wait))

            attempted_keys.add(key)

            try:
                return operation(client)
            except BaseException as exc:
                if is_quota_exhausted_error(exc):
                    delay = parse_retry_delay_from_error(exc)
                    self.report_quota_exhausted(key, delay)
                    continue  # Try next available key
                # 503 or any other non-429 error is re-raised immediately
                raise

    def _get_or_create_client(self, key_str: str) -> Any:
        """Retrieve cached client or instantiate a new one via factory."""
        if key_str not in self._clients:
            self._clients[key_str] = self._client_factory(key_str)
        return self._clients[key_str]
