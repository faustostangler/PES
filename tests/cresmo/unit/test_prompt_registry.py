"""Unit tests for Decoupled Prompt Registry and Metadata.

Conforms to ADR-001 (Modular Monolith Domain Integrity) and
ADR-017 (Prompt Management with Langfuse & Local Fallback).
"""

from __future__ import annotations

import pytest

from cresmo.infrastructure.adapters.prompts.registry import (
    PROMPT_REGISTRY,
    PromptKey,
    PromptMetadata,
    get_prompt_metadata,
)


class TestPromptRegistry:
    """Test suite verifying prompt registry integrity and metadata lookup."""

    def test_prompt_registry_contains_all_canonical_keys(self) -> None:
        """Verify that all 15 canonical PromptKey members are registered in PROMPT_REGISTRY."""
        expected_keys = {
            "fluid_prose",
            "gap_filler_pass1",
            "gap_filler_pass_subsequent",
            "long_expander",
            "wide_expander",
            "atomic_inventory",
            "judge_atomic_inventory",
            "atomic_batch",
            "reconcile_mocs",
            "raw_index_summary",
            "raw_index_concepts",
            "raw_index_concepts_rewrite",
            "raw_index_synthesis",
            "judge_raw_index_summary",
            "judge_raw_index_concepts",
            "judge_raw_index_synthesis",
        }
        assert len(PromptKey) == 16
        assert {k.value for k in PromptKey} == expected_keys
        for key in PromptKey:
            assert key in PROMPT_REGISTRY
            meta = PROMPT_REGISTRY[key]
            assert isinstance(meta, PromptMetadata)
            assert meta.key == key
            assert meta.langfuse_name.startswith("cresmo-")
            assert len(meta.skill_name) > 0
            assert len(meta.description) > 0

    def test_prompt_registry_keys_are_unique(self) -> None:
        """Verify that all Langfuse names and keys are distinct without collisions."""
        langfuse_names = [meta.langfuse_name for meta in PROMPT_REGISTRY.values()]
        assert len(langfuse_names) == len(set(langfuse_names))

        keys = list(PROMPT_REGISTRY.keys())
        assert len(keys) == len(set(keys))

    def test_get_prompt_metadata_by_key_and_string(self) -> None:
        """Verify lookup by PromptKey enum and raw string."""
        meta_enum = get_prompt_metadata(PromptKey.GAP_FILLER_PASS1)
        meta_str = get_prompt_metadata("gap_filler_pass1")

        assert meta_enum == meta_str
        assert meta_enum.langfuse_name == "cresmo-gap-filler-pass1"
        assert meta_enum.skill_name == "cresmo-gap-filler"

    def test_get_prompt_metadata_fluid_prose(self) -> None:
        """Verify lookup for decoupled fluid_prose prompt."""
        meta = get_prompt_metadata(PromptKey.FLUID_PROSE)
        assert meta.langfuse_name == "cresmo-fluid-prose"
        assert meta.skill_name == "cresmo-fluid-prose"

    def test_get_prompt_metadata_invalid_key_raises(self) -> None:
        """Verify that looking up an unknown prompt key raises KeyError."""
        with pytest.raises(KeyError, match="Unknown prompt key: 'nonexistent_prompt'"):
            get_prompt_metadata("nonexistent_prompt")
