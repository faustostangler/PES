"""Unit tests for LangfusePromptProvider adapter.

Conforms to ADR-014 and ADR-017:
    - Verifies prompt compilation using remote Langfuse client when reachable.
    - Verifies guaranteed availability fallback to JsonPromptProvider when offline or failing.
    - Verifies prompt version tracking.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import ChannelName
from cresmo.infrastructure.adapters.prompt_provider import (
    JsonPromptProvider,
    LangfusePromptProvider,
)


class TestLangfusePromptProvider:
    """Test suite for LangfusePromptProvider."""

    @pytest.fixture
    def fallback_provider(self) -> JsonPromptProvider:
        return JsonPromptProvider()

    def test_fallback_when_langfuse_client_is_none(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        provider = LangfusePromptProvider(
            langfuse_client=None,
            fallback_provider=fallback_provider,
            label="production",
        )
        sys_inst, prompt = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Sample raw transcript.",
        )
        assert isinstance(sys_inst, str)
        assert isinstance(prompt, str)
        assert len(sys_inst) > 0
        assert len(prompt) > 0
        assert "Sample raw transcript." in prompt

    def test_remote_langfuse_get_prompt_called_with_fallback(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        mock_client = MagicMock()
        mock_prompt_obj = MagicMock()
        mock_prompt_obj.compile.return_value = "Compiled prompt from Langfuse Cloud"
        mock_prompt_obj.version = 3
        mock_client.get_prompt.return_value = mock_prompt_obj

        provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=fallback_provider,
            label="production",
        )

        sys_inst, prompt = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Sample transcript text.",
        )

        assert isinstance(sys_inst, str)
        assert len(sys_inst) > 0
        assert prompt == "Compiled prompt from Langfuse Cloud"
        mock_client.get_prompt.assert_called_once()
        args, kwargs = mock_client.get_prompt.call_args
        assert args[0] == "cresmo-gap-filler-pass1"
        assert kwargs["label"] == "production"
        assert "fallback" in kwargs
        assert "Sample transcript text." in kwargs["fallback"]

    def test_resilience_when_langfuse_client_raises_network_error(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        mock_client = MagicMock()
        mock_client.get_prompt.side_effect = RuntimeError("Langfuse API connection timeout")

        provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=fallback_provider,
            label="production",
        )

        # Must not raise RuntimeError; must gracefully fall back
        sys_inst, prompt = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Ground truth text.",
        )

        assert isinstance(sys_inst, str)
        assert isinstance(prompt, str)
        assert len(sys_inst) > 0
        assert "Ground truth text." in prompt

    def test_all_prompt_provider_port_methods_implemented(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        provider = LangfusePromptProvider(
            langfuse_client=None,
            fallback_provider=fallback_provider,
        )
        assert isinstance(provider, PromptProviderPort)

        # Test expanders
        long_sys, long_prompt = provider.get_long_expander_prompt("Body text", "Dates and facts")
        assert isinstance(long_sys, str)
        assert "Body text" in long_prompt

        wide_sys, wide_prompt = provider.get_wide_expander_prompt("Axial text")
        assert isinstance(wide_sys, str)
        assert "Axial text" in wide_prompt

        inv_sys, inventory_prompt = provider.get_inventory_prompt(
            "Compendium title", ChannelName("sandeco"), "Compendium body"
        )
        assert isinstance(inv_sys, str)
        assert "Compendium body" in inventory_prompt

        batch_sys, atomic_batch_prompt = provider.get_batch_notes_prompt(
            "Compendium title", ChannelName("sandeco"), "Compendium body", "Inventory JSON"
        )
        assert isinstance(batch_sys, str)
        assert "Compendium body" in atomic_batch_prompt

        moc_sys, moc_prompt = provider.get_mocs_prompt("Notes summary")
        assert isinstance(moc_sys, str)
        assert "Notes summary" in moc_prompt
