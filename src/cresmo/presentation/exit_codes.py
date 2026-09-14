"""Standardized process exit codes for the Cresmo CLI taxonomy."""

from __future__ import annotations

EXIT_SUCCESS: int = 0
EXIT_INTERNAL_ERROR: int = 1
EXIT_CONFIG_OR_USAGE_ERROR: int = 2
EXIT_DOMAIN_VALIDATION_ERROR: int = 3
EXIT_RATE_LIMIT_EXCEEDED: int = 4
EXIT_INGESTION_ERROR: int = 5
