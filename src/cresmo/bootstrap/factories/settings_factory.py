"""Settings factory and memoization provider.

Conforms to:
- ADR-002: Presentation CLI & Humble Object
- ADR-005: Multi-Role 12-Factor Container & Settings
- ADR-048: Architectural Remediation (Config Singleton in Infrastructure)
"""

from __future__ import annotations

from cresmo.infrastructure.config import (
    CresmoSettings,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)

__all__ = [
    "CresmoSettings",
    "get_shared_settings",
    "reset_shared_settings",
    "resolve_shared_settings",
]
