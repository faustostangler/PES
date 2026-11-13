"""Unit tests for decoupled JsonPromptProvider and Channel Taxonomy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import ChannelName, PromptKey
from cresmo.domain.value_objects.prompt import ChatPrompt
from cresmo.infrastructure.adapters.prompt_provider import (
    JsonPromptProvider,
)
from cresmo.infrastructure.adapters.prompts.builders import (
    PROMPT_BUILDER_REGISTRY,
    PromptBuilderRegistry,
    PromptTemplateHost,
)


def _dummy_builder(provider: PromptTemplateHost, **context: Any) -> ChatPrompt:
    return ChatPrompt.from_system_and_user(system="s", user="u")


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
        assert "gap_filler" in provider._templates
        assert "long_expander" in provider._templates
        assert "wide_expander" in provider._templates
        assert "atomic_inventory" in provider._templates
        assert "atomic_batch" in provider._templates
        assert "reconcile_mocs" in provider._templates
        assert "judge_gap_filler" in provider._templates

    def test_judge_gap_filler_prompt_formatting(self) -> None:
        provider = JsonPromptProvider()
        prompt = provider.get_prompt(
            PromptKey.JUDGE_GAP_FILLER,
            stage_name="gap_filler",
            criteria_json='["epistemic_grounding_segregation", "conceptual_mechanical_decomposition"]',
            source_text="Source fluid transcript.",
            candidate_text="Candidate compendium text.",
        )
        assert prompt.system_prompt is not None
        assert "epistemic_grounding_segregation" in prompt.system_prompt
        assert "conceptual_mechanical_decomposition" in prompt.system_prompt
        assert "braudelian_stratification" in prompt.system_prompt
        assert "genealogy_hidden_agency" in prompt.system_prompt
        assert "competing_hypotheses" in prompt.system_prompt
        assert "extra_info_granularity" in prompt.system_prompt
        assert "linear_style_naturalism" in prompt.system_prompt
        user_msg = prompt.get_last_user_content()
        assert "Source fluid transcript." in user_msg
        assert "Candidate compendium text." in user_msg

    def test_gap_filler_prompt_embeds_skill_and_style_guide(self) -> None:
        provider = JsonPromptProvider()

        prompt1 = provider.get_prompt(
            PromptKey.GAP_FILLER,
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("Tech Channel"),
            file_name="test.txt",
            source_text="Source fluid text here.",
        )
        s1 = prompt1.system_prompt or ""
        p1 = prompt1.get_last_user_content()
        assert isinstance(s1, str)
        assert "Your Skill:" in s1
        assert "cresmo-gap-filler:\n" in s1
        assert "Cresmo Style Guide:" in s1
        assert "# Guia de Estilo Cresmo" in s1
        assert "{{cresmo-style-guide}}" not in s1
        assert "{{skill_block}}" not in s1
        assert s1.count("# Guia de Estilo Cresmo") == 1
        assert "Português do Brasil" in s1
        assert "Transcrição:\nSource fluid text here." in p1

        prompt2 = provider.get_prompt(
            PromptKey.GAP_FILLER,
            pass_num=2,
            total_passes=3,
            channel_name=ChannelName("Tech Channel"),
            file_name="test.txt",
            source_text="Source fluid text here.",
            current_text="Draft from pass 1.",
        )
        s2 = prompt2.system_prompt or ""
        assert s1 == s2

    def test_long_and_wide_expander_prompts(self) -> None:
        provider = JsonPromptProvider()

        long_prompt = provider.get_prompt(
            PromptKey.LONG_EXPANDER,
            compendium_body="Main body text.",
            complementary_info="Supplementary info.",
        )
        long_s = long_prompt.system_prompt or ""
        long_p = long_prompt.get_last_user_content()
        assert isinstance(long_s, str)
        assert "Main body text." in long_p
        assert "Supplementary info." in long_p
        assert "Fernand Braudel" in long_s
        assert long_s.startswith(provider.catalog[PromptKey.LONG_EXPANDER].description)
        assert "longitudinal" in long_p.lower()
        assert not long_p.startswith(long_s[:30])

        wide_prompt = provider.get_prompt(
            PromptKey.WIDE_EXPANDER,
            current_text="Longitudinally expanded text.",
        )
        wide_s = wide_prompt.system_prompt or ""
        wide_p = wide_prompt.get_last_user_content()
        assert isinstance(wide_s, str)
        assert "Longitudinally expanded text." in wide_p
        assert "Karl Jaspers" in wide_s
        assert wide_s.startswith(provider.catalog[PromptKey.WIDE_EXPANDER].description)
        assert "synchronic" in wide_p.lower()
        assert not wide_p.startswith(wide_s[:30])

    def test_inventory_and_batch_notes_and_mocs_prompts(self) -> None:
        provider = JsonPromptProvider()

        inv_prompt = provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            content_title="Compendium Title",
            channel_name=ChannelName("Channel Name"),
            compendium_body="Enriched content body.",
        )
        inv_s = inv_prompt.system_prompt or ""
        inv_p = inv_prompt.get_last_user_content()
        assert isinstance(inv_s, str)
        assert "Compendium Title" in inv_p
        assert "Channel Name" in inv_p
        assert "Enriched content body." in inv_p

        judge_inv_prompt = provider.get_prompt(
            PromptKey.JUDGE_ATOMIC_INVENTORY,
            content_title="Compendium Title",
            channel_name=ChannelName("Channel Name"),
            compendium_body="Enriched content body.",
            inventory_json='[{"title": "Target 1", "type": "entity"}]',
        )
        judge_inv_s = judge_inv_prompt.system_prompt or ""
        judge_inv_p = judge_inv_prompt.get_last_user_content()
        assert isinstance(judge_inv_s, str)
        assert "Compendium Title" in judge_inv_p
        assert "Channel Name" in judge_inv_p
        assert '[{"title": "Target 1", "type": "entity"}]' in judge_inv_p
        assert "true" in judge_inv_p.lower()

        batch_prompt = provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title="Compendium Title",
            channel_name=ChannelName("Channel Name"),
            compendium_body="Enriched content body.",
            targets_json='[{"title": "Target 1"}]',
        )
        batch_s = batch_prompt.system_prompt or ""
        batch_p = batch_prompt.get_last_user_content()
        assert isinstance(batch_s, str)
        assert "Compendium Title" in batch_p
        assert "target entities to synthesize" in batch_p.lower()
        assert '[{"title": "Target 1"}]' in batch_p

        mocs_prompt = provider.get_prompt(
            PromptKey.RECONCILE_MOCS,
            notes_json='[{"title": "Note 1"}]',
        )
        mocs_s = mocs_prompt.system_prompt or ""
        mocs_p = mocs_prompt.get_last_user_content()
        assert isinstance(mocs_s, str)
        assert "vault atomic notes to reconcile" in mocs_p.lower()
        assert '[{"title": "Note 1"}]' in mocs_p

    def test_custom_prompts_json_override(self, tmp_path: Path) -> None:
        custom_prompts = {
            "gap_filler": {
                "skill_name": "none",
                "user_prompt": "{description}: Pass {pass_num}/{total_passes} for {channel_name} with source: {source_text}{draft_section}",
            },
            "long_expander": {
                "skill_name": "none",
                "user_prompt": "{description}: {compendium_body} + {complementary_info}",
            },
            "wide_expander": {
                "skill_name": "none",
                "user_prompt": "{description}: {text}",
            },
            "atomic_inventory": {
                "skill_name": "none",
                "user_prompt": "{description}: {content_title} on {channel_name} with {compendium_body}",
            },
            "atomic_batch": {
                "skill_name": "none",
                "user_prompt": "{description}: {content_title} on {channel_name} body {compendium_body} targets {targets_json}",
            },
            "reconcile_mocs": {
                "skill_name": "none",
                "user_prompt": "{description}: {notes_json}",
            },
            "judge_atomic_inventory": {
                "skill_name": "none",
                "system_prompt": "Custom Judge System Instruction",
                "user_prompt": "{description}: {content_title} on {channel_name} with {inventory_json}",
            },
        }
        custom_file = tmp_path / "custom_prompts.json"
        custom_file.write_text(json.dumps(custom_prompts), encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=custom_file)
        prompt1 = provider.get_prompt(
            PromptKey.GAP_FILLER,
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("Custom Channel"),
            file_name="custom.txt",
            source_text="text",
        )
        expected_desc = provider.catalog[PromptKey.GAP_FILLER].description
        assert (
            prompt1.get_last_user_content()
            == f"{expected_desc}: Pass 1/3 for Custom Channel with source: text"
        )
        assert prompt1.system_prompt == expected_desc

        prompt2 = provider.get_prompt(
            PromptKey.GAP_FILLER,
            pass_num=2,
            total_passes=3,
            channel_name=ChannelName("Custom Channel"),
            file_name="custom.txt",
            source_text="text",
            current_text="draft",
        )
        assert (
            prompt2.get_last_user_content()
            == f'{expected_desc}: Pass 2/3 for Custom Channel with source: text\n<draft pass="1">\ndraft\n</draft>\n'
        )
        assert prompt2.system_prompt == expected_desc

        prompt_long = provider.get_prompt(
            PromptKey.LONG_EXPANDER, compendium_body="Body", complementary_info="Info"
        )
        expected_long_desc = provider.catalog[PromptKey.LONG_EXPANDER].description
        assert prompt_long.get_last_user_content() == f"{expected_long_desc}: Body + Info"
        assert prompt_long.system_prompt == expected_long_desc

        prompt_wide = provider.get_prompt(PromptKey.WIDE_EXPANDER, current_text="WideText")
        expected_wide_desc = provider.catalog[PromptKey.WIDE_EXPANDER].description
        assert prompt_wide.get_last_user_content() == f"{expected_wide_desc}: WideText"
        assert prompt_wide.system_prompt == expected_wide_desc

        prompt_inv = provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            content_title="Title",
            channel_name=ChannelName("Channel"),
            compendium_body="Body",
        )
        expected_inv_desc = provider.catalog[PromptKey.ATOMIC_INVENTORY].description
        assert (
            prompt_inv.get_last_user_content() == f"{expected_inv_desc}: Title on Channel with Body"
        )
        assert prompt_inv.system_prompt == expected_inv_desc

        prompt_j_inv = provider.get_prompt(
            PromptKey.JUDGE_ATOMIC_INVENTORY,
            content_title="Title",
            channel_name=ChannelName("Channel"),
            compendium_body="Body",
            inventory_json='[{"title": "T1"}]',
        )
        expected_j_inv_desc = provider.catalog[PromptKey.JUDGE_ATOMIC_INVENTORY].description
        assert (
            prompt_j_inv.get_last_user_content()
            == f'{expected_j_inv_desc}: Title on Channel with [{{"title": "T1"}}]'
        )
        assert prompt_j_inv.system_prompt == "Custom Judge System Instruction"

        prompt_batch = provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title="Title",
            channel_name=ChannelName("Channel"),
            compendium_body="Body",
            targets_json="Targets",
        )
        expected_batch_desc = provider.catalog[PromptKey.ATOMIC_BATCH].description
        assert (
            prompt_batch.get_last_user_content()
            == f"{expected_batch_desc}: Title on Channel body Body targets Targets"
        )
        assert prompt_batch.system_prompt == expected_batch_desc

        prompt_mocs = provider.get_prompt(PromptKey.RECONCILE_MOCS, notes_json="Notes")
        expected_mocs_desc = provider.catalog[PromptKey.RECONCILE_MOCS].description
        assert prompt_mocs.get_last_user_content() == f"{expected_mocs_desc}: Notes"
        assert prompt_mocs.system_prompt == expected_mocs_desc

    def test_custom_prompts_file_corrupted_falls_back_to_bundled(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "corrupted.json"
        bad_file.write_text("NOT VALID JSON", encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=bad_file)
        assert "gap_filler" in provider._templates
        assert len(provider._templates) > 0

    def test_bundled_resource_load_failure_clears_templates(self) -> None:
        with patch("importlib.resources.files", side_effect=RuntimeError("Resource unavailable")):
            provider = JsonPromptProvider()
            assert provider._templates == {}

    def test_resolve_skills_dir_custom_and_fallback(self, tmp_path: Path) -> None:
        # Custom exists
        custom_skills = tmp_path / "custom_skills"
        custom_skills.mkdir()
        assert JsonPromptProvider._resolve_skills_dir(custom_skills) == custom_skills

        # Custom does not exist, check fallback
        non_existent = tmp_path / "non_existent"
        with patch("cresmo.infrastructure.adapters.prompt_provider._CANDIDATE_SKILLS_DIRS", ()):
            assert JsonPromptProvider._resolve_skills_dir(non_existent) is None

        # Candidate exists
        candidate_dir = tmp_path / "candidate_skills"
        candidate_dir.mkdir()
        with patch(
            "cresmo.infrastructure.adapters.prompt_provider._CANDIDATE_SKILLS_DIRS",
            (candidate_dir,),
        ):
            assert JsonPromptProvider._resolve_skills_dir(non_existent) == candidate_dir

    def test_skill_content_and_skill_block_caching(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        sample_skill = skills_dir / "cresmo-sample"
        sample_skill.mkdir()
        skill_md = sample_skill / "SKILL.md"
        skill_md.write_text("   Skill documentation content   \n", encoding="utf-8")

        provider = JsonPromptProvider(skills_dir=skills_dir)
        block = provider._get_skill_block("cresmo-sample")
        assert "cresmo-sample:\n" in block
        assert "Skill documentation content" in block

        # Cached call
        assert provider._get_skill_content("cresmo-sample") == "Skill documentation content"

        # Missing skill returns empty string
        assert provider._get_skill_block("non-existent-skill") == ""

        # Skills dir is None
        provider_no_skills = JsonPromptProvider(skills_dir=tmp_path / "no_such_dir")
        provider_no_skills.skills_dir = None
        assert provider_no_skills._get_skill_content("cresmo-sample") == ""
        assert provider_no_skills._get_skill_block("cresmo-sample") == ""

    def test_skill_read_exception_handled_gracefully(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        sample_skill = skills_dir / "bad-skill"
        sample_skill.mkdir()
        skill_md = sample_skill / "SKILL.md"
        skill_md.write_text("Valid text", encoding="utf-8")

        provider = JsonPromptProvider(skills_dir=skills_dir)
        with patch.object(Path, "read_text", side_effect=PermissionError("Cannot read")):
            content = provider._get_skill_content("bad-skill")
            assert content == ""
            assert provider._get_skill_block("bad-skill") == ""

    def test_safe_format_handles_nested_json_braces(self) -> None:
        template = 'Task: {task}. Schema: {{"key": "{value}", "list": [1, 2]}}'
        formatted = JsonPromptProvider._safe_format(template, task="Extract", value="TestVal")
        assert formatted == 'Task: Extract. Schema: {{"key": "TestVal", "list": [1, 2]}}'

    def test_empty_user_template_fails_fast_without_hardcoded_fallbacks(self) -> None:
        """Verify zero inline hardcoded prompt fallbacks exist when user template is empty."""
        import pytest

        from cresmo.domain.exceptions import DomainValidationError

        provider = JsonPromptProvider()
        provider._templates = {
            "gap_filler": {"user_prompt": ""},
        }

        with pytest.raises(DomainValidationError, match="ChatMessage content cannot be empty"):
            provider.get_prompt(
                PromptKey.GAP_FILLER,
                pass_num=1,
                total_passes=2,
                channel_name=ChannelName("ChName"),
                file_name="f.txt",
                source_text="RawText",
            )

    def test_get_raw_index_3_pass_prompts(self) -> None:
        provider = JsonPromptProvider()
        assert "raw_index_summary" in provider._templates
        assert "raw_index_concepts" in provider._templates
        assert "raw_index_synthesis" in provider._templates

        # Pass 1: Concepts (from transcript excerpt)
        concepts_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_CONCEPTS,
            content_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        concepts_system_instructions = concepts_prompt.system_prompt or ""
        concepts_user_prompt = concepts_prompt.get_last_user_content()
        assert "comma-separated" in concepts_system_instructions.lower()
        assert "Vilfredo Pareto and Elites" in concepts_user_prompt
        assert "A circulação de elites" in concepts_user_prompt

        # Pass 2: Summary (from transcript excerpt)
        summary_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_SUMMARY,
            content_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        summary_system_instructions = summary_prompt.system_prompt or ""
        summary_user_prompt = summary_prompt.get_last_user_content()
        assert "synthesize" in summary_system_instructions.lower()
        assert "Português do Brasil" in summary_system_instructions
        assert "Vilfredo Pareto and Elites" in summary_user_prompt
        assert "A circulação de elites" in summary_user_prompt

        # Pass 3: Synthesis (from summary)
        synthesis_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_SYNTHESIS,
            content_title="Vilfredo Pareto and Elites",
            summary="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        synthesis_system_instructions = synthesis_prompt.system_prompt or ""
        synthesis_user_prompt = synthesis_prompt.get_last_user_content()
        assert "paratactic" in synthesis_system_instructions.lower()
        assert "ner" in synthesis_system_instructions.lower()
        assert (
            "single continuous paragraph" in synthesis_system_instructions.lower()
            or "single paragraph" in synthesis_system_instructions.lower()
        )
        assert "Vilfredo Pareto and Elites" in synthesis_user_prompt
        assert "A circulação de elites" in synthesis_user_prompt

    def test_get_judge_raw_index_prompts(self) -> None:
        provider = JsonPromptProvider()
        assert "judge_raw_index_summary" in provider._templates
        assert "judge_raw_index_concepts" in provider._templates
        assert "judge_raw_index_synthesis" in provider._templates

        # Summary Judge
        summary_judge_prompt = provider.get_prompt(
            PromptKey.JUDGE_RAW_INDEX_SUMMARY,
            content_title="Pareto and Elites",
            transcript_excerpt="Explicando a circulação das elites na política.",
            summary="Resumo fiel da circulação das elites.",
            language="Português do Brasil",
        )
        summary_judge_system_instructions = summary_judge_prompt.system_prompt or ""
        summary_judge_user_prompt = summary_judge_prompt.get_last_user_content()
        assert "impartial" in summary_judge_system_instructions.lower()
        assert "evaluator" in summary_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in summary_judge_system_instructions.lower()
        assert "Pareto and Elites" in summary_judge_user_prompt
        assert "Explicando a circulação das elites na política." in summary_judge_user_prompt
        assert "Resumo fiel da circulação das elites." in summary_judge_user_prompt
        assert "true" in summary_judge_user_prompt.lower()

        # Concepts Judge
        concepts_judge_prompt = provider.get_prompt(
            PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
            content_title="Pareto and Elites",
            transcript_excerpt="Explicando a circulação das elites na política.",
            concepts="Circulação de Elites, Pareto",
            language="Português do Brasil",
        )
        concepts_judge_system_instructions = concepts_judge_prompt.system_prompt or ""
        concepts_judge_user_prompt = concepts_judge_prompt.get_last_user_content()
        assert "impartial" in concepts_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in concepts_judge_system_instructions.lower()
        assert "Pareto and Elites" in concepts_judge_user_prompt
        assert "Explicando a circulação das elites na política." in concepts_judge_user_prompt
        assert "Circulação de Elites, Pareto" in concepts_judge_user_prompt
        assert "true" in concepts_judge_user_prompt.lower()

        # Synthesis Judge
        synthesis_judge_prompt = provider.get_prompt(
            PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
            content_title="Pareto and Elites",
            transcript_excerpt="Explicando a circulação das elites na política.",
            synthesis="A circulação de elites reflete a alternância política segundo Pareto.",
            language="Português do Brasil",
        )
        synthesis_judge_system_instructions = synthesis_judge_prompt.system_prompt or ""
        synthesis_judge_user_prompt = synthesis_judge_prompt.get_last_user_content()
        assert "impartial evaluator" in synthesis_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in synthesis_judge_system_instructions.lower()
        assert "Pareto and Elites" in synthesis_judge_user_prompt
        assert "Explicando a circulação das elites na política." in synthesis_judge_user_prompt
        assert (
            "A circulação de elites reflete a alternância política segundo Pareto."
            in synthesis_judge_user_prompt
        )
        assert "true" in synthesis_judge_user_prompt.lower()


class TestPromptBuilderRegistry:
    """Hermetic unit tests for the first-class typed PromptBuilderRegistry."""

    def test_default_registry_contains_all_prompt_keys(self) -> None:
        assert PROMPT_BUILDER_REGISTRY.is_frozen
        assert len(PROMPT_BUILDER_REGISTRY) == len(PromptKey)
        for key in PromptKey:
            assert key in PROMPT_BUILDER_REGISTRY
            builder = PROMPT_BUILDER_REGISTRY.get(key)
            assert callable(builder)
            assert PROMPT_BUILDER_REGISTRY[key] is builder

    def test_registry_registration_and_decorator_syntax(self) -> None:
        registry = PromptBuilderRegistry()

        def custom_builder(provider: Any, **context: Any) -> ChatPrompt:
            return ChatPrompt.from_system_and_user(system="sys", user="user")

        registry.register(PromptKey.FLUID_PROSE, custom_builder)
        assert registry.get(PromptKey.FLUID_PROSE) is custom_builder

        @registry.register(PromptKey.LONG_EXPANDER)
        def decorated_builder(provider: Any, **context: Any) -> ChatPrompt:
            return ChatPrompt.from_system_and_user(system="dec_sys", user="dec_user")

        assert registry.get(PromptKey.LONG_EXPANDER) is decorated_builder

    def test_registry_frozen_guard(self) -> None:
        registry = PromptBuilderRegistry()
        registry.register(
            PromptKey.FLUID_PROSE,
            _dummy_builder,
        )
        registry.freeze()
        assert registry.is_frozen

        import pytest

        with pytest.raises(RuntimeError, match="frozen"):
            registry.register(
                PromptKey.LONG_EXPANDER,
                _dummy_builder,
            )

        with pytest.raises(RuntimeError, match="frozen"):

            @registry.register(PromptKey.WIDE_EXPANDER)
            def _fn(provider: PromptTemplateHost, **context: Any) -> ChatPrompt:
                return ChatPrompt.from_system_and_user(system="s", user="u")

    def test_registry_completeness_validation(self) -> None:
        registry = PromptBuilderRegistry()
        registry.register(
            PromptKey.FLUID_PROSE,
            _dummy_builder,
        )

        import pytest

        with pytest.raises(ValueError, match="Missing prompt builders for keys"):
            registry.validate_completeness()

        # Passes when validating only registered subset
        registry.validate_completeness(expected_keys=[PromptKey.FLUID_PROSE])

    def test_registry_dependency_injection_into_json_provider(self, tmp_path: Path) -> None:
        mock_registry = PromptBuilderRegistry()
        mock_registry.register(
            PromptKey.FLUID_PROSE,
            lambda provider, **context: ChatPrompt.from_system_and_user(
                system="Injected System",
                user=f"Injected User: {context.get('content_title', '')}",
            ),
        )
        mock_registry.freeze()

        provider = JsonPromptProvider(registry=mock_registry)
        prompt = provider.get_prompt(PromptKey.FLUID_PROSE, content_title="Custom Injection")
        assert prompt.system_prompt == "Injected System"
        assert prompt.get_last_user_content() == "Injected User: Custom Injection"

    def test_unsupported_key_raises_value_error(self) -> None:
        registry = PromptBuilderRegistry()
        import pytest

        with pytest.raises(ValueError, match="Unsupported prompt key"):
            registry.get(PromptKey.FLUID_PROSE)

    def test_multi_skill_block_resolution(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-a" / "SKILL.md").write_text("Skill A Spec Content", encoding="utf-8")
        (skills_dir / "skill-b").mkdir()
        (skills_dir / "skill-b" / "SKILL.md").write_text("Skill B Spec Content", encoding="utf-8")

        custom_prompts = {
            "multi_skill_test": {
                "task": "Test Multi Skill Task",
                "skills": ["skill-a", "skill-b"],
                "system_prompt": "{task}\n\n{skill_block}",
                "user_prompt": "Run task with {input_val}",
            }
        }
        prompts_file = tmp_path / "prompts.json"
        prompts_file.write_text(json.dumps(custom_prompts), encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=prompts_file, skills_dir=skills_dir)
        sys_inst, user_tpl = provider.get_chat_prompt_template("multi_skill_test")
        assert "skill-a:\n" in sys_inst
        assert "Skill A Spec Content" in sys_inst
        assert "skill-b:\n" in sys_inst
        assert "Skill B Spec Content" in sys_inst
        assert user_tpl == "Run task with {input_val}"

    def test_fluid_prose_embeds_cresmo_style_guide_and_fluid_prose(self) -> None:
        provider = JsonPromptProvider()
        prompt = provider.get_prompt(
            PromptKey.FLUID_PROSE,
            channel_name="Test Channel",
            file_name="test.txt",
            raw_text="Test spoken raw transcript content.",
        )
        sys_inst = prompt.system_prompt or ""
        assert "cresmo-style-guide:\n" in sys_inst
        assert "cresmo-fluid-prose:\n" in sys_inst
        assert "Daniel Dennett" in sys_inst
        assert "Emil Cioran" in sys_inst
        assert "Friedrich Nietzsche" in sys_inst
        assert "Jorge Luis Borges" in sys_inst
        assert "Nassim Nicholas Taleb" in sys_inst
        assert "Test spoken raw transcript content." in prompt.get_last_user_content()

    def test_json_prompt_provider_respects_settings_paths(self, tmp_path: Path) -> None:
        """Verify JsonPromptProvider respects prompts_path and skills_dir from settings."""
        custom_prompts_file = tmp_path / "custom_settings_prompts.json"
        custom_skills_dir = tmp_path / "custom_settings_skills"
        custom_skills_dir.mkdir()
        (custom_skills_dir / "cresmo-custom").mkdir()
        (custom_skills_dir / "cresmo-custom" / "SKILL.md").write_text(
            "Custom Skill Doc", encoding="utf-8"
        )

        custom_prompts = {
            "fluid_prose": {
                "skill_name": "cresmo-custom",
                "system_prompt": "Custom System {cresmo-custom}",
                "user_prompt": "Custom User {raw_text}",
            }
        }
        custom_prompts_file.write_text(json.dumps(custom_prompts), encoding="utf-8")

        from unittest.mock import Mock

        mock_settings = Mock()
        mock_settings.prompts_path = custom_prompts_file
        mock_settings.skills_dir = custom_skills_dir
        mock_settings.language = "en-US"

        provider = JsonPromptProvider(settings=mock_settings)
        assert provider.prompts_path == custom_prompts_file
        assert provider.skills_dir == custom_skills_dir
        assert provider.language == "en-US"

    def test_builders_have_zero_inline_prompt_fallbacks(self) -> None:
        """Verify builders.py contains zero inline prompt fallback blocks per ADR-011 and ADR-051."""
        import inspect

        from cresmo.infrastructure.adapters.prompts import builders

        source = inspect.getsource(builders)
        assert "if not template and not system_template:" not in source
        assert "Transform raw transcript into clean, continuous fluid prose" not in source
