"""Unit tests for Cresmo Domain Taxonomy and Channel Classification.

Verifies deterministic channel-to-knowledge-domain mapping, volatility assignment,
case normalization, and default fallback per SPEC-001 §2.
"""

from __future__ import annotations

import pytest

from cresmo.domain.taxonomy import (
    DEFAULT_CHANNEL_CATEGORY,
    DEFAULT_CHANNEL_DOMAIN,
    _extract_channel_candidates,
    classify_channel,
)
from cresmo.domain.value_objects import ChannelName


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

    def test_classify_channel_with_channel_name_vo(self) -> None:
        domain, volatility = classify_channel(ChannelName("Fabio Akita"))
        assert domain == "tech_ai"
        assert volatility == "perennial"

    def test_extract_channel_candidates_url_with_at_sign(self) -> None:
        candidates = _extract_channel_candidates("https://www.youtube.com/@ancapsu")
        assert "https://www.youtube.com/@ancapsu" in candidates
        assert "@ancapsu" in candidates
        assert "ancapsu" in candidates

        # With trailing path and query parameter
        c2 = _extract_channel_candidates("https://www.youtube.com/@ancapsu/videos?sub=1")
        assert c2 == [
            "https://www.youtube.com/@ancapsu/videos?sub=1",
            "@ancapsu",
            "ancapsu",
        ]

        # Query parameter immediately following handle without intervening slash
        c_query_direct = _extract_channel_candidates(
            "https://www.youtube.com/@ancapsu?sub_confirmation=1"
        )
        assert c_query_direct == [
            "https://www.youtube.com/@ancapsu?sub_confirmation=1",
            "@ancapsu",
            "ancapsu",
        ]

        # Multiple /@ segments: must extract first occurrence
        c_multi_at = _extract_channel_candidates("https://example.com/@ancapsu/@secondary")
        assert c_multi_at == [
            "https://example.com/@ancapsu/@secondary",
            "@ancapsu",
            "ancapsu",
        ]

        # Multiple slashes and multiple query parameters after /@
        c_deep = _extract_channel_candidates(
            "https://www.youtube.com/@ancapsu/videos/featured?sub=1?extra=2"
        )
        assert c_deep == [
            "https://www.youtube.com/@ancapsu/videos/featured?sub=1?extra=2",
            "@ancapsu",
            "ancapsu",
        ]

        # Empty slug after /@
        c3 = _extract_channel_candidates("https://www.youtube.com/@")
        assert c3 == ["https://www.youtube.com/@"]

    def test_extract_channel_candidates_handle_starting_with_at(self) -> None:
        c1 = _extract_channel_candidates("@ancapsu")
        assert c1 == ["@ancapsu", "ancapsu"]

        # Just @ with nothing after
        c2 = _extract_channel_candidates("@")
        assert c2 == ["@"]

    def test_extract_channel_candidates_url_with_regular_slashes(self) -> None:
        # Standard channel path with query parameters and trailing slash
        c1 = _extract_channel_candidates("https://www.youtube.com/c/ancapsu/?param=value?extra=1")
        assert c1 == [
            "https://www.youtube.com/c/ancapsu/?param=value?extra=1",
            "ancapsu",
        ]

        # Path where last component starts with @
        c2 = _extract_channel_candidates("https://www.youtube.com/c/@ancapsu")
        assert c2 == [
            "https://www.youtube.com/c/@ancapsu",
            "@ancapsu",
            "ancapsu",
        ]

        # Slashes only
        c3 = _extract_channel_candidates("///")
        assert c3 == ["///"]

    def test_classify_channel_with_urls_and_handles(self) -> None:
        # Classify via URL with /@
        d1, v1 = classify_channel("https://www.youtube.com/@ancapsu/about")
        assert d1 == "politics_br"
        assert v1 == "volatile"

        # Classify via handle @
        d2, v2 = classify_channel("@ancapsu")
        assert d2 == "politics_br"
        assert v2 == "volatile"

        # Classify via standard URL /
        d3, v3 = classify_channel("https://youtube.com/c/ancapsu")
        assert d3 == "politics_br"
        assert v3 == "volatile"
