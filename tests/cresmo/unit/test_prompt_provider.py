"""Unit tests for decoupled JsonPromptProvider and Channel Taxonomy."""

from __future__ import annotations

import json
from pathlib import Path

from cresmo.domain.taxonomy import classify_channel
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider


class TestChannelTaxonomy:
    """Hermetic unit tests for channel classification."""

    def test_known_politics_br_channel(self) -> None:
        category, volatility = classify_channel("ancapsu")
        assert category == "politics_br"
        assert volatility == "volatile"

    def test_known_tech_ai_channel(self) -> None:
        category, volatility = classify_channel("Fabio Akita")
        assert category == "tech_ai"
        assert volatility == "perennial"

    def test_known_finance_channel(self) -> None:
        category, volatility = classify_channel("Fernando Ulrich")
        assert category == "finance"
        assert volatility == "perennial"

    def test_unknown_channel_fallback(self) -> None:
        category, volatility = classify_channel("Some Unknown Channel Name 12345")
        assert category == "uncategorized"
        assert volatility == "volatile"


class TestJsonPromptProvider:
    """Hermetic unit tests for prompt template loading and skill embedding."""

    def test_default_prompt_provider_loads_bundled_json(self) -> None:
        provider = JsonPromptProvider()
        assert len(provider._templates) > 0
        assert "gap_filler_pass1" in provider._templates
        assert "gap_filler_pass_subsequent" in provider._templates
        assert "long_expander" in provider._templates
        assert "wide_expander" in provider._templates
        assert "atomic_inventory" in provider._templates
        assert "atomic_batch" in provider._templates
        assert "reconcile_mocs" in provider._templates

    def test_gap_filler_differentiates_pass1_and_subsequent_passes(self) -> None:
        provider = JsonPromptProvider()

        p1 = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name="Tech Channel",
            file_name="test.txt",
            raw_text="Raw text here.",
        )
        assert "Pass 1/3" in p1
        assert "Raw text here." in p1

        p2 = provider.get_gap_filler_prompt(
            pass_num=2,
            total_passes=3,
            channel_name="Tech Channel",
            file_name="test.txt",
            raw_text="Raw text here.",
            current_text="Draft from pass 1.",
        )
        assert "Pass 2/3" in p2
        assert "Draft from pass 1." in p2
        assert p1 != p2

    def test_long_and_wide_expander_prompts(self) -> None:
        provider = JsonPromptProvider()

        long_p = provider.get_long_expander_prompt(
            compendium_body="Main body text.",
            complementary_info="Supplementary info.",
        )
        assert "Main body text." in long_p
        assert "Supplementary info." in long_p

        wide_p = provider.get_wide_expander_prompt(
            current_text="Longitudinally expanded text.",
        )
        assert "Longitudinally expanded text." in wide_p

    def test_custom_prompts_json_override(self, tmp_path: Path) -> None:
        custom_prompts = {
            "gap_filler_pass1": {
                "task": "Custom Task 1",
                "skill_name": "none",
                "template": "{task}: Custom Pass 1 for {channel_name}",
            },
            "gap_filler_pass_subsequent": {
                "task": "Custom Task 2",
                "skill_name": "none",
                "template": "{task}: Custom Pass {pass_num} for {channel_name}",
            },
        }
        custom_file = tmp_path / "custom_prompts.json"
        custom_file.write_text(json.dumps(custom_prompts), encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=custom_file)
        p1 = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name="Custom Channel",
            file_name="custom.txt",
            raw_text="text",
        )
        assert p1 == "Custom Task 1: Custom Pass 1 for Custom Channel"
