"""Standardized process exit codes for the Cresmo CLI taxonomy.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

# Process completed successfully without invariant breaches
EXIT_SUCCESS: int = 0

# Unhandled catastrophic exception or internal invariant failure
EXIT_INTERNAL_ERROR: int = 1

# Invalid CLI flag combinations, missing mandatory configs, or usage syntax error
EXIT_CONFIG_OR_USAGE_ERROR: int = 2

# Domain rule violation (e.g. empty transcript body, invalid note typology, cyclic MOC link)
EXIT_DOMAIN_VALIDATION_ERROR: int = 3

# Remote API quota exhausted (HTTP 429) or rate limiter saturated
EXIT_RATE_LIMIT_EXCEEDED: int = 4

# Media ingestion failure (network socket timeout, unresolvable feed, or audio download failure)
EXIT_INGESTION_ERROR: int = 5
