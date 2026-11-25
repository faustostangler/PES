"""Parity contract tests proving JsonPromptProvider and LangfusePromptProvider normalize identically.

Conforms to:
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.domain.value_objects import ChannelName, PromptKey
from cresmo.infrastructure.adapters.prompts.context_normalizer import normalize_prompt_context
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider

SAMPLE_CONTEXTS: dict[PromptKey, dict[str, Any]] = {
    PromptKey.FLUID_PROSE: {"raw_text": "Raw transcript."},
    PromptKey.JUDGE_FLUID_PROSE: {
        "stage_name": "fluid_prose",
        "criteria_json": '["orality_removal"]',
        "source_text": "Raw",
        "candidate_text": "Cand",
    },
    PromptKey.GAP_FILLER: {
        "source_text": "Fluid text",
        "pass_num": 2,
        "current_text": "Draft 1",
        "channel_name": ChannelName("Tech"),
    },
    PromptKey.JUDGE_GAP_FILLER: {
        "stage_name": "gap_filler",
        "criteria_json": '["braudelian_stratification"]',
        "source_text": "Fluid",
        "candidate_text": "Expanded",
    },
    PromptKey.OLLAMA_CRITIQUE: {
        "stage_name": "fluid_prose",
        "overall_score": "0.62",
        "criteria_failures": "orality_removal",
    },
    PromptKey.LONG_EXPANDER: {
        "source_text": "Gap filled draft",
        "pass_num": 2,
        "current_text": "Long pass 1",
    },
    PromptKey.JUDGE_LONG_EXPANDER: {
        "stage_name": "long_expander",
        "criteria_json": '["longue_duree_stratification"]',
        "source_text": "Gap filled draft",
        "candidate_text": "Longitudinally expanded draft",
    },
    PromptKey.WIDE_EXPANDER: {
        "source_text": "Longitudinally expanded draft",
        "pass_num": 2,
        "current_text": "Wide pass 1",
    },
    PromptKey.JUDGE_WIDE_EXPANDER: {
        "stage_name": "wide_expander",
        "criteria_json": '["synchronic_connectivity"]',
        "source_text": "Longitudinally expanded draft",
        "candidate_text": "Horizontally expanded draft",
    },
    PromptKey.RAW_INDEX_SUMMARY: {
        "content_title": "Video 1",
        "transcript_excerpt": "Excerpt 1",
    },
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: {
        "stage_name": "raw_index_synthesis",
        "criteria_json": '["index_synthesis_quality"]',
        "source_text": "Summary 1",
        "candidate_text": "Synthesis 1",
    },
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: {
        "stage_name": "raw_index_summary",
        "criteria_json": '["index_synthesis_quality"]',
        "source_text": "Excerpt 1",
        "candidate_text": "Summary 1",
    },
    PromptKey.RAW_INDEX_CONCEPTS: {
        "content_title": "Video 1",
        "transcript_excerpt": "Excerpt 1",
    },
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: {
        "stage_name": "raw_index_concepts",
        "criteria_json": '["index_synthesis_quality"]',
        "source_text": "Excerpt 1",
        "candidate_text": "Concept A",
    },
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: {"previous_output": "Old concepts"},
    PromptKey.RAW_INDEX_SYNTHESIS: {
        "channel_name": ChannelName("Tech"),
        "content_title": "Video 1",
        "summary": "Summary 1",
    },
    PromptKey.ATOMIC_INVENTORY: {
        "channel_name": ChannelName("Tech"),
        "content_title": "Video 1",
        "compendium_body": "Body",
    },
    PromptKey.JUDGE_ATOMIC_INVENTORY: {
        "stage_name": "atomic_inventory",
        "criteria_json": '["inventory_coherence"]',
        "source_text": "Body",
        "candidate_text": "[]",
    },
    PromptKey.ATOMIC_BATCH: {
        "channel_name": ChannelName("Tech"),
        "content_title": "Video 1",
        "compendium_body": "Body",
        "targets_json": "[]",
    },
    PromptKey.RECONCILE_MOCS: {
        "existing_mocs": "MOC A",
        "notes_json": "[]",
    },
}


class TestPromptNormalizationParity:
    """Ensure local JSON and remote Langfuse prompt providers receive identical normalized vars."""

    def test_sample_contexts_cover_every_prompt_key(self) -> None:
        assert set(SAMPLE_CONTEXTS.keys()) == set(PromptKey)

    @pytest.mark.parametrize("key", list(PromptKey))
    def test_langfuse_compile_kwargs_match_local_normalized_context(self, key: PromptKey) -> None:
        ctx = SAMPLE_CONTEXTS[key]
        expected_vars = normalize_prompt_context(key, ctx)

        mock_prompt = MagicMock()
        mock_prompt.name = f"cresmo-{key.value}"
        mock_prompt.version = 1
        mock_prompt.compile.return_value = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ]
        mock_client = MagicMock()
        mock_client.get_prompt.return_value = mock_prompt

        local_provider = JsonPromptProvider()
        remote_provider = LangfusePromptProvider(
            langfuse_client=mock_client,
            fallback_provider=local_provider,
        )

        remote_provider.get_prompt(key, **ctx)
        mock_prompt.compile.assert_called_once_with(**expected_vars)

        local_chat = local_provider.get_prompt(key, **ctx)
        assert local_chat.system_prompt is not None
        assert local_chat.system_prompt.strip() != ""
        assert local_chat.messages[-1].content.strip() != ""
