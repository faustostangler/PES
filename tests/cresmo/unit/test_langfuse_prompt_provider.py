"""Unit tests for LangfusePromptProvider adapter.

Conforms to ADR-014 and ADR-017:
    - Verifies prompt compilation using remote Langfuse client when reachable.
    - Verifies guaranteed availability fallback to JsonPromptProvider when offline or failing.
    - Verifies prompt version tracking.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langfuse.api.core import ApiError

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import ChannelName, PromptKey
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
        sys_inst, prompt = provider.get_prompt(
            PromptKey.GAP_FILLER_PASS1,
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

    def test_remote_langfuse_get_chat_prompt_resolves_system_and_user(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        mock_client = MagicMock()
        mock_prompt_obj = MagicMock()
        mock_prompt_obj.compile.return_value = [
            {"role": "system", "content": "System directive from Langfuse Cloud Chat"},
            {"role": "user", "content": "User input payload compiled from Langfuse Cloud"},
        ]
        mock_prompt_obj.version = 3
        mock_client.get_prompt.return_value = mock_prompt_obj

        provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=fallback_provider,
            label="production",
        )

        sys_inst, prompt = provider.get_prompt(
            PromptKey.GAP_FILLER_PASS1,
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Sample transcript text.",
        )

        assert sys_inst == "System directive from Langfuse Cloud Chat"
        assert prompt == "User input payload compiled from Langfuse Cloud"
        mock_client.get_prompt.assert_called_once()
        args, kwargs = mock_client.get_prompt.call_args
        assert args[0] == "cresmo-gap-filler-pass1"
        assert kwargs["label"] == "production"
        assert kwargs["type"] == "chat"
        assert provider.get_last_prompt_version("cresmo-gap-filler-pass1") == 3

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
        sys_inst, prompt = provider.get_prompt(
            PromptKey.GAP_FILLER_PASS1,
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

    def test_resilience_when_langfuse_raises_not_found_404(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        """ApiError(404) means the prompt hasn't been created in Langfuse yet.

        Must fall back silently (with a WARNING, not an exception).
        """
        mock_client = MagicMock()
        mock_client.get_prompt.side_effect = ApiError(status_code=404, body="Not Found")

        provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=fallback_provider,
            label="production",
        )

        sys_inst, prompt = provider.get_prompt(
            PromptKey.GAP_FILLER_PASS1,
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Fallback text on 404.",
        )

        assert isinstance(sys_inst, str)
        assert isinstance(prompt, str)
        assert "Fallback text on 404." in prompt

    def test_resilience_when_langfuse_raises_api_error_non_404(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        """ApiError with a non-404 status (e.g. 500) must also fall back gracefully."""
        mock_client = MagicMock()
        mock_client.get_prompt.side_effect = ApiError(status_code=500, body="Internal Server Error")

        provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=fallback_provider,
            label="production",
        )

        sys_inst, prompt = provider.get_prompt(
            PromptKey.GAP_FILLER_PASS1,
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("sandeco"),
            file_name="ep01.md",
            raw_text="Fallback text on 500.",
        )

        assert isinstance(sys_inst, str)
        assert isinstance(prompt, str)
        assert "Fallback text on 500." in prompt

    def test_all_prompt_keys_dispatched_via_unified_interface(
        self, fallback_provider: JsonPromptProvider
    ) -> None:
        provider = LangfusePromptProvider(
            langfuse_client=None,
            fallback_provider=fallback_provider,
        )
        assert isinstance(provider, PromptProviderPort)

        # Test expanders
        long_sys, long_prompt = provider.get_prompt(
            PromptKey.LONG_EXPANDER,
            compendium_body="Body text",
            complementary_info="Dates and facts",
        )
        assert isinstance(long_sys, str)
        assert "Body text" in long_prompt

        wide_sys, wide_prompt = provider.get_prompt(
            PromptKey.WIDE_EXPANDER,
            current_text="Axial text",
        )
        assert isinstance(wide_sys, str)
        assert "Axial text" in wide_prompt

        inv_sys, inventory_prompt = provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            compendium_title="Compendium title",
            channel_name=ChannelName("sandeco"),
            compendium_body="Compendium body",
        )
        assert isinstance(inv_sys, str)
        assert "Compendium body" in inventory_prompt

        batch_sys, atomic_batch_prompt = provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            compendium_title="Compendium title",
            channel_name=ChannelName("sandeco"),
            compendium_body="Compendium body",
            targets_json="Inventory JSON",
        )
        assert isinstance(batch_sys, str)
        assert "Compendium body" in atomic_batch_prompt

        moc_sys, moc_prompt = provider.get_prompt(
            PromptKey.RECONCILE_MOCS,
            notes_json="Notes summary",
        )
        assert isinstance(moc_sys, str)
        assert "Notes summary" in moc_prompt

        raw_sys, raw_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_SUMMARY,
            video_title="Pareto",
            transcript_excerpt="Excerpt",
        )
        assert isinstance(raw_sys, str)
        assert "Pareto" in raw_prompt
