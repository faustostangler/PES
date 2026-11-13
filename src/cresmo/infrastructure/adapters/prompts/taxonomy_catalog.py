"""Decoupled JSON Channel Taxonomy Catalog Adapter.

Loads deterministic channel-to-domain and volatility classifications from
externalized JSON resources, isolating Domain/Application logic from static datasets.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-062: Structural Refactoring & Hexagonal Purity
"""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from cresmo.application.ports.taxonomy import ChannelTaxonomyPort
from cresmo.domain.taxonomy import TaxonomyCatalog, classify_channel_from_catalog
from cresmo.infrastructure.config import CresmoSettings

if TYPE_CHECKING:
    from cresmo.domain.value_objects import ChannelName


class TaxonomyCatalogError(Exception):
    """Raised when the channel taxonomy JSON catalog fails loading or schema validation."""


class TaxonomyDomainSpec(BaseModel):
    """Schema for a single domain entry in taxonomy.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    volatility: Literal["volatile", "perennial"]
    channels: list[str] = Field(default_factory=list)


def load_taxonomy_catalog(taxonomy_path: Path | None = None) -> TaxonomyCatalog:
    """Load and validate channel taxonomy catalog from explicit path or bundled resource.

    Args:
        taxonomy_path: Optional explicit filesystem path overriding bundled taxonomy.json.

    Returns:
        Immutable TaxonomyCatalog mapping domain -> (volatility, frozenset[channel_tokens]).

    Raises:
        TaxonomyCatalogError: If JSON cannot be read, parsed, or validated.
    """
    if taxonomy_path is not None:
        if not taxonomy_path.exists():
            raise TaxonomyCatalogError(f"Taxonomy catalog file not found: {taxonomy_path}")
        try:
            raw_text = taxonomy_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise TaxonomyCatalogError(
                f"Failed to read taxonomy JSON '{taxonomy_path}': {exc}"
            ) from exc
    else:
        try:
            resource_traversable = importlib.resources.files(
                CresmoSettings.DEFAULT_TAXONOMY_RESOURCE_PACKAGE
            ).joinpath(CresmoSettings.DEFAULT_TAXONOMY_RESOURCE_NAME)
            raw_text = resource_traversable.read_text(encoding="utf-8")
        except Exception as exc:
            raise TaxonomyCatalogError(f"Failed to load bundled taxonomy resource: {exc}") from exc

    try:
        raw_data = json.loads(raw_text)
    except Exception as exc:
        raise TaxonomyCatalogError(f"Failed to parse taxonomy JSON: {exc}") from exc

    if not isinstance(raw_data, dict):
        raise TaxonomyCatalogError("Taxonomy catalog root must be a JSON object.")

    catalog: dict[str, tuple[str, frozenset[str]]] = {}
    for domain, entry in raw_data.items():
        if not isinstance(domain, str) or not domain.strip():
            raise TaxonomyCatalogError("Taxonomy domain keys must be non-empty strings.")
        if not isinstance(entry, dict):
            raise TaxonomyCatalogError(f"Taxonomy entry '{domain}' must be a JSON object.")
        try:
            spec = TaxonomyDomainSpec(**entry)
        except Exception as exc:
            raise TaxonomyCatalogError(
                f"Failed validating taxonomy entry for '{domain}': {exc}"
            ) from exc
        normalized_channels = frozenset(
            ch.lower().strip() for ch in spec.channels if isinstance(ch, str) and ch.strip()
        )
        catalog[domain.strip()] = (spec.volatility, normalized_channels)

    return catalog


class JsonTaxonomyCatalogAdapter(ChannelTaxonomyPort):
    """Hexagonal Adapter resolving channel taxonomy from bundled or configured JSON."""

    def __init__(self, taxonomy_path: Path | None = None) -> None:
        """Initialize adapter and eagerly validate the taxonomy JSON catalog."""
        self.taxonomy_path = taxonomy_path
        self._catalog: TaxonomyCatalog = load_taxonomy_catalog(taxonomy_path=taxonomy_path)

    @property
    def catalog(self) -> TaxonomyCatalog:
        """Expose immutable loaded taxonomy catalog."""
        return self._catalog

    def classify(self, channel_name: ChannelName | str) -> tuple[str, str]:
        """Classify source channel deterministically via loaded catalog."""
        return classify_channel_from_catalog(channel_name, self._catalog)


__all__ = [
    "JsonTaxonomyCatalogAdapter",
    "TaxonomyCatalogError",
    "TaxonomyDomainSpec",
    "load_taxonomy_catalog",
]
