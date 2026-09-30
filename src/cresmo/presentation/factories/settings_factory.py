"""Settings factory and memoization provider.

Conforms to:
- ADR-002: Presentation CLI & Humble Object
- ADR-005: Multi-Role 12-Factor Container & Settings
"""

from __future__ import annotations

import functools

from cresmo.infrastructure.config import CresmoSettings


@functools.lru_cache(maxsize=1)
def get_shared_settings() -> CresmoSettings:
    """Return canonical cached CresmoSettings singleton.

    Prevents redundant .env disk reads and multiple configuration allocations
    across independent adapter factory invocations per ADR-002 §9.1.
    """
    return CresmoSettings()


def reset_shared_settings() -> None:
    """Clear cached settings singleton (used for test isolation)."""
    get_shared_settings.cache_clear()


def resolve_shared_settings(settings: CresmoSettings | None = None) -> CresmoSettings:
    """Resolve injected settings or fall back to the memoized single source of truth."""
    if settings is not None:
        return settings
    return get_shared_settings()
