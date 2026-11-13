"""Domain taxonomy and channel classification primitives for Cresmo Knowledge Synthesis.

Provides deterministic channel handle/URL candidate extraction and catalog-driven
classification into knowledge domains and volatility types (perennial vs. volatile).
Channel lists are externalized into infrastructure resources behind ChannelTaxonomyPort.

Conforms to:
- SPEC-001: §2.1 (Domain Taxonomy & Categorization Rules)
- ADR-001: Modular Monolith Domain Integrity
- ADR-062: Structural Refactoring & Hexagonal Purity
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cresmo.domain.value_objects import ChannelName

DEFAULT_CHANNEL_DOMAIN: str = "uncategorized"
DEFAULT_CHANNEL_CATEGORY: str = "volatile"

TaxonomyCatalog = Mapping[str, tuple[str, frozenset[str]]]
ChannelClassifierFn = Callable[["ChannelName | str"], tuple[str, str]]


def _extract_channel_candidates(raw: str) -> list[str]:
    """Extract candidate channel handles, slugs, and normalized tokens from URL or raw text."""
    candidates: list[str] = [raw]
    if "/@" in raw:
        _, _, after_at = raw.partition("/@")
        slug = after_at.partition("/")[0].partition("?")[0].strip()
        if slug:
            candidates.extend([f"@{slug}", slug])
    elif raw.startswith("@"):
        slug = raw[1:].strip()
        if slug:
            candidates.append(slug)
    elif "/" in raw:
        base_raw = raw.partition("?")[0]
        parts = [part for part in base_raw.split("/") if part]
        if parts:
            slug = parts[-1].strip()
            if slug:
                candidates.append(slug)
    return candidates


def classify_channel_from_catalog(
    channel_name: ChannelName | str,
    catalog: TaxonomyCatalog,
) -> tuple[str, str]:
    """Classify source channel deterministically against an injected taxonomy catalog.

    Args:
        channel_name: Human-readable name, handle, or URL of the channel.
        catalog: Mapping of domain name to (volatility_category, normalized_channel_set).

    Returns:
        Tuple of (domain_name, volatility_category) defaulting to
        (DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY).
    """
    raw = str(channel_name).lower().strip()
    candidates = _extract_channel_candidates(raw)

    for name_clean in candidates:
        for domain, (volatility, channels_set) in catalog.items():
            if name_clean in channels_set:
                return domain, volatility

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY
