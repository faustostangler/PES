"""Application Port for deterministic channel-to-domain taxonomy classification.

Decouples pure Domain/Application logic from external channel catalog files
(e.g., bundled taxonomy JSON or remote configuration catalogs).

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- ADR-062: Structural Refactoring & Hexagonal Purity
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from cresmo.domain.taxonomy import (
    DEFAULT_CHANNEL_CATEGORY,
    DEFAULT_CHANNEL_DOMAIN,
    classify_channel_from_catalog,
)

if TYPE_CHECKING:
    from cresmo.domain.value_objects import ChannelName


class ChannelTaxonomyPort(ABC):
    """Abstract Port interface for classifying channels into domain and volatility."""

    @abstractmethod
    def classify(self, channel_name: ChannelName | str) -> tuple[str, str]:
        """Classify source channel deterministically into (domain, volatility_category)."""
        raise NotImplementedError


class NoOpChannelTaxonomyPort(ChannelTaxonomyPort):
    """Fallback taxonomy port returning default uncategorized/volatile classification."""

    def classify(self, channel_name: ChannelName | str) -> tuple[str, str]:
        """Return empty-catalog fallback classification via pure domain function."""
        _ = channel_name
        return classify_channel_from_catalog("", {}) or (
            DEFAULT_CHANNEL_DOMAIN,
            DEFAULT_CHANNEL_CATEGORY,
        )


__all__ = [
    "ChannelTaxonomyPort",
    "NoOpChannelTaxonomyPort",
]
