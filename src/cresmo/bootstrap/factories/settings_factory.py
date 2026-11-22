"""Settings factory and memoization provider.

Conforms to:
- ADR-002: Presentation CLI & Humble Object
- ADR-005: Multi-Role 12-Factor Container & Settings
- ADR-048: Architectural Remediation (Config Singleton in Infrastructure)
- ADR-067: Humble Presentation CLI and Run/Sync Use Cases
"""

from __future__ import annotations

from typing import Any

from cresmo.infrastructure.config import (
    CresmoSettings,
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)


def load_fresh_settings(overrides: dict[str, Any] | None = None) -> CresmoSettings:
    """Instantiate fresh validated CresmoSettings with optional immutable overrides."""
    settings = CresmoSettings()
    if overrides:
        return settings.model_copy(update=overrides)
    return settings


__all__ = [
    "CresmoSettings",
    "get_shared_settings",
    "load_fresh_settings",
    "reset_shared_settings",
    "resolve_shared_settings",
]
