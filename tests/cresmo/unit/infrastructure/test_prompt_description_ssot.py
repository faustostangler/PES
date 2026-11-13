"""Verification tests for ADR-052: Prompt Catalog SSOT Consolidation in JSON Resource."""

from __future__ import annotations

import json
from pathlib import Path

from cresmo.domain.value_objects import PromptKey
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider, load_prompt_catalog


class TestPromptDescriptionSsot:
    """Verifies that prompts.json is the sole SSOT for descriptions, templates, and metadata."""

    def test_prompts_json_contains_zero_task_keys_and_zero_task_placeholders(self) -> None:
        """Enforces that prompts.json has completely purged the 'task' key and {task} token."""
        json_path = (
            Path(__file__).resolve().parents[4]
            / "src"
            / "cresmo"
            / "infrastructure"
            / "resources"
            / "prompts.json"
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))

        for key, entry in data.items():
            assert "task" not in entry, (
                f"Key '{key}' in prompts.json still contains forbidden 'task' attribute."
            )
            assert "active" not in entry, (
                f"Key '{key}' in prompts.json still contains dead 'active' attribute."
            )
            sys_p = entry.get("system_prompt", "")
            user_p = entry.get("user_prompt", "")
            assert "{task}" not in sys_p and "{{task}}" not in sys_p, (
                f"Key '{key}' system_prompt still contains legacy 'task' token."
            )
            assert "{task}" not in user_p and "{{task}}" not in user_p, (
                f"Key '{key}' user_prompt still contains legacy 'task' token."
            )

    def test_json_provider_resolves_system_instruction_from_catalog_description(self) -> None:
        """Enforces that JsonPromptProvider and builders resolve description strictly from PromptCatalog."""
        provider = JsonPromptProvider()
        sys_inst, _ = provider.get_chat_prompt_template(PromptKey.FLUID_PROSE)
        expected_desc = provider.catalog[PromptKey.FLUID_PROSE].description
        assert expected_desc.rstrip(".") in sys_inst

    def test_gap_filler_resolves_description_from_catalog(self) -> None:
        """Enforces that gap_filler builder resolves description from PromptCatalog."""
        catalog = load_prompt_catalog()
        provider = JsonPromptProvider()
        sys_inst, _ = provider.get_chat_prompt_template(PromptKey.GAP_FILLER)
        expected_desc = catalog[PromptKey.GAP_FILLER].description
        assert expected_desc in sys_inst
