"""Taxonomy infrastructure adapters implementing ChannelTaxonomyPort (ADR-071)."""

from __future__ import annotations

from cresmo.infrastructure.adapters.taxonomy.json_taxonomy_adapter import (
    JsonTaxonomyCatalogAdapter,
    TaxonomyCatalogError,
    load_taxonomy_catalog,
)

__all__ = [
    "JsonTaxonomyCatalogAdapter",
    "TaxonomyCatalogError",
    "load_taxonomy_catalog",
]
