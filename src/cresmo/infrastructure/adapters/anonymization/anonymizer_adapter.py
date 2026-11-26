"""Anonymizer infrastructure adapters for Cresmo.

Conforms to ADR-017:
    - Implements AnonymizerPort using compiled regular expressions for PII and secret redaction.
    - Provides recursive dictionary sanitization.
    - Provides OpenTelemetry span attribute scrubbing for LGPD compliance.
    - Provides NoOpAnonymizerAdapter for testing and passthrough execution.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

from cresmo.application.ports import AnonymizerPort

_REDACTED_SECRET_MARKER: Final[str] = "[REDACTED_SECRET]"
_REDACTED_EMAIL_MARKER: Final[str] = "[REDACTED_EMAIL]"

# Pre-compiled high-performance regular expressions
_EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)

_SECRET_TOKEN_REGEX = re.compile(
    r"(?i)\b(?:sk-[A-Za-z0-9-_]{10,}|AIzaSy[A-Za-z0-9-_]{30,}|Bearer\s+[A-Za-z0-9._~+/-]{15,})\b"
)

_SENSITIVE_KEY_EXACT = {
    "token",
    "auth",
    "authorization",
    "cookie",
    "password",
    "secret",
    "api_key",
    "apikey",
    "private_key",
}

_SENSITIVE_KEY_SUBSTRINGS = (
    "cookie",
    "password",
    "secret",
    "api_key",
    "apikey",
    "private_key",
    "auth_token",
    "access_token",
    "refresh_token",
    "bearer_token",
    "client_secret",
)


def _is_sensitive_key(key: str) -> bool:
    """Determine if a dictionary or attribute key holds sensitive authentication data."""
    key_lower = key.lower()
    if key_lower in _SENSITIVE_KEY_EXACT:
        return True
    return any(sub in key_lower for sub in _SENSITIVE_KEY_SUBSTRINGS)


class RegexAnonymizerAdapter(AnonymizerPort):
    """Production Anonymizer adapter utilizing compiled regular expressions.

    Ensures LGPD compliance and protects sensitive credentials across telemetry,
    logging, and external export boundaries.
    """

    def _mask_text(self, text: str) -> str:
        """Sanitize raw text by replacing emails, secrets, and auth tokens with markers.

        Args:
            text: Raw input text.

        Returns:
            Sanitized text string.
        """
        if not text:
            return text

        # Step 1: Redact secrets / bearer tokens / API keys
        sanitized = _SECRET_TOKEN_REGEX.sub(_REDACTED_SECRET_MARKER, text)

        # Step 2: Redact email addresses
        sanitized = _EMAIL_REGEX.sub(_REDACTED_EMAIL_MARKER, sanitized)

        return sanitized

    def mask_mapping(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Recursively scrub sensitive keys and redact sensitive string values.

        Args:
            data: Arbitrary key-value mapping.

        Returns:
            Clean dictionary copy with sensitive fields scrubbed.
        """
        result: dict[str, Any] = {}
        for key, value in data.items():
            str_key = key if isinstance(key, str) else str(key)
            if _is_sensitive_key(str_key):
                # Scrub entire sensitive entry (e.g. cookie headers or tokens)
                continue

            if isinstance(value, str):
                result[key] = self._mask_text(value)
            elif isinstance(value, Mapping):
                result[key] = self.mask_mapping(value)
            elif isinstance(value, list):
                result[key] = [
                    self.mask_mapping(v)
                    if isinstance(v, Mapping)
                    else self._mask_text(v)
                    if isinstance(v, str)
                    else v
                    for v in value
                ]
            else:
                result[key] = value

        return result


class NoOpAnonymizerAdapter(AnonymizerPort):
    """Passthrough adapter for testing or when anonymization is explicitly disabled."""

    def mask_mapping(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Passthrough dictionary without modification."""
        return dict(data)
