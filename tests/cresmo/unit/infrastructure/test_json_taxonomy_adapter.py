"""Unit tests for relocated JsonTaxonomyCatalogAdapter (ADR-071).

Conforms to:
    - ADR-062: Structural Consolidation & ChannelTaxonomyPort
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

from cresmo.infrastructure.adapters.taxonomy import JsonTaxonomyCatalogAdapter


class TestJsonTaxonomyCatalogAdapter:
    """Hermetic unit tests for JSON-backed channel classification."""

    def test_known_politics_br_channel(self) -> None:
        category, volatility = JsonTaxonomyCatalogAdapter().classify("ancapsu")
        assert category == "politics_br"
        assert volatility == "volatile"

    def test_known_tech_ai_channel(self) -> None:
        category, volatility = JsonTaxonomyCatalogAdapter().classify("Fabio Akita")
        assert category == "tech_ai"
        assert volatility == "perennial"

    def test_known_finance_channel(self) -> None:
        category, volatility = JsonTaxonomyCatalogAdapter().classify("Fernando Ulrich")
        assert category == "finance"
        assert volatility == "perennial"

    def test_unknown_channel_fallback(self) -> None:
        category, volatility = JsonTaxonomyCatalogAdapter().classify(
            "Some Unknown Channel Name 12345"
        )
        assert category == "uncategorized"
        assert volatility == "volatile"
