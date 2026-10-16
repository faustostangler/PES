"""Hexagonal Anonymizer Port for PII sanitization and credential redaction.

Conforms to:
- ADR-017: Context & Privacy Isolation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class AnonymizerPort(ABC):
    """Hexagonal Port for data anonymization, PII redaction, and credential scrubbing.

    Conforms to ADR-017. Decouples privacy and LGPD compliance rules from infrastructure
    telemetry collectors and application use cases.
    """

    @abstractmethod
    def mask_text(self, text: str) -> str:
        """Sanitize raw text string by redacting PII (emails, phones) and sensitive secrets.

        Args:
            text: Unsanitized input string.

        Returns:
            Sanitized string with sensitive tokens replaced with redaction markers.
        """
        raise NotImplementedError("Implement mask_text contract.")

    @abstractmethod
    def mask_mapping(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Recursively scrub sensitive keys and redact sensitive string values in a dictionary.

        Args:
            data: Key-value mapping potentially containing credentials or PII.

        Returns:
            Clean copy of the dictionary with sensitive fields redacted or removed.
        """
        raise NotImplementedError("Implement mask_mapping contract.")

    @abstractmethod
    def mask_span_attributes(self, attributes: Mapping[str, Any]) -> dict[str, Any]:
        """Sanitize OpenTelemetry span attributes before export.

        Args:
            attributes: Raw span attributes mapping.

        Returns:
            Clean dictionary conforming to OpenTelemetry types with sensitive data removed.
        """
        raise NotImplementedError("Implement mask_span_attributes contract.")
