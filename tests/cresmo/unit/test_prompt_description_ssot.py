"""Red phase test for ADR-050: Elimination of Prompt Task Duplication and SSOT Consolidation in PROMPT_REGISTRY."""

from __future__ import annotations

import json
from pathlib import Path

from cresmo.domain.value_objects import PromptKey
from cresmo.infrastructure.adapters.prompts import PROMPT_REGISTRY, JsonPromptProvider


class TestPromptDescriptionSsot:
    """Verifies that PROMPT_REGISTRY.description is the sole SSOT and prompts.json has zero 'task' keys."""

    def test_prompts_json_contains_zero_task_keys_and_zero_task_placeholders(self) -> None:
        """Enforces that prompts.json has completely purged the 'task' key and {task} token."""
        json_path = (
            Path(__file__).resolve().parents[3]
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
            sys_p = entry.get("system_prompt", "")
            user_p = entry.get("user_prompt", "")
            assert "{task}" not in sys_p, (
                f"Key '{key}' system_prompt still contains legacy '{{task}}' token."
            )
            assert "{task}" not in user_p, (
                f"Key '{key}' user_prompt still contains legacy '{{task}}' token."
            )

    def test_json_provider_resolves_system_instruction_from_registry_description(self) -> None:
        """Enforces that JsonPromptProvider and builders resolve description strictly from PROMPT_REGISTRY."""
        provider = JsonPromptProvider()
        sys_inst, _ = provider.get_chat_prompt_template(PromptKey.FLUID_PROSE)
        expected_desc = PROMPT_REGISTRY[PromptKey.FLUID_PROSE].description
        assert expected_desc in sys_inst

    def test_gap_filler_resolves_description_from_registry(self) -> None:
        """Enforces that gap_filler builder resolves description from PROMPT_REGISTRY."""
        provider = JsonPromptProvider()
        sys_inst, _ = provider.get_chat_prompt_template(PromptKey.GAP_FILLER)
        expected_desc = PROMPT_REGISTRY[PromptKey.GAP_FILLER].description
        assert expected_desc in sys_inst
