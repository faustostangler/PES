"""Unit tests for Cresmo Domain Taxonomy and Channel Classification.

Verifies deterministic channel-to-knowledge-domain mapping, volatility assignment,
case normalization, and default fallback per SPEC-001 §2.
"""

from __future__ import annotations

import pytest

from cresmo.domain.taxonomy import (
    DEFAULT_CHANNEL_CATEGORY,
    DEFAULT_CHANNEL_DOMAIN,
    classify_channel,
)


class TestDomainTaxonomy:
    """Hermetic unit tests for classify_channel taxonomy resolution."""

    @pytest.mark.parametrize(
        ("channel_name", "expected_domain", "expected_volatility"),
        [
            # 1. Politics BR (Volatile)
            ("ancapsu", "politics_br", "volatile"),
            ("deltan dallagnol", "politics_br", "volatile"),
            ("  VISÃO LIBERTÁRIA  ", "politics_br", "volatile"),
            # 2. Geopolitics (Volatile)
            ("china unscripted", "geopolitics", "volatile"),
            ("serpentza", "geopolitics", "volatile"),
            ("  PROFESSOR RICARDO MARCILIO  ", "geopolitics", "volatile"),
            # 3. Tech & AI (Perennial)
            ("fabio akita", "tech_ai", "perennial"),
            ("ai engineer", "tech_ai", "perennial"),
            ("  FABIO AKITA  ", "tech_ai", "perennial"),
            # 4. Finance (Perennial)
            ("fernando ulrich", "finance", "perennial"),
            ("o primo rico", "finance", "perennial"),
            ("  FERNANDO ULRICH  ", "finance", "perennial"),
            # 5. Engineering (Perennial)
            ("ciencia todo dia", "engineering", "perennial"),
            ("technology connections", "engineering", "perennial"),
            ("  TECHNOLOGY CONNECTIONS  ", "engineering", "perennial"),
            # 6. Architecture (Perennial)
            ("ugreen consultoria e educacao", "architecture", "perennial"),
            ("planarq campos", "architecture", "perennial"),
            ("  PLANARQ CAMPOS  ", "architecture", "perennial"),
            # 7. History (Perennial)
            ("the present past", "history", "perennial"),
            ("marcelo andrade", "history", "perennial"),
            ("  THE PRESENT PAST  ", "history", "perennial"),
            # 8. Philosophy (Perennial)
            ("clóvis de barros", "philosophy", "perennial"),
            ("jefferson fisher", "philosophy", "perennial"),
            ("  JEFFERSON FISHER  ", "philosophy", "perennial"),
            # 9. Health (Perennial)
            ("sleepwise", "health", "perennial"),
            ("arata academy", "health", "perennial"),
            ("  SLEEPWISE  ", "health", "perennial"),
            # 10. Entertainment (Volatile)
            ("canal 90", "entertainment", "volatile"),
            ("canal peewee", "entertainment", "volatile"),
            ("  CANAL 90  ", "entertainment", "volatile"),
            # Fallback (Uncategorized Volatile)
            ("unknown random channel 987654", "uncategorized", "volatile"),
            ("", "uncategorized", "volatile"),
            ("   ", "uncategorized", "volatile"),
        ],
    )
    def test_classify_channel_branches(
        self,
        channel_name: str,
        expected_domain: str,
        expected_volatility: str,
    ) -> None:
        domain, volatility = classify_channel(channel_name)
        assert domain == expected_domain
        assert volatility == expected_volatility

    def test_default_constants(self) -> None:
        assert DEFAULT_CHANNEL_DOMAIN == "uncategorized"
        assert DEFAULT_CHANNEL_CATEGORY == "volatile"
