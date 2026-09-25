"""Unit tests for decoupled JsonPromptProvider and Channel Taxonomy."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import ChannelName
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
            channel_name=ChannelName("Tech Channel"),
            file_name="test.txt",
            raw_text="Raw text here.",
        )
        assert "Pass 1/3" in p1
        assert "Tech Channel" in p1
        assert "test.txt" in p1
        assert "Raw text here." in p1

        p2 = provider.get_gap_filler_prompt(
            pass_num=2,
            total_passes=3,
            channel_name=ChannelName("Tech Channel"),
            file_name="test.txt",
            raw_text="Raw text here.",
            current_text="Draft from pass 1.",
        )
        assert "Pass 2/3" in p2
        assert "PASS 1 TO ENRICH" in p2
        assert "Tech Channel" in p2
        assert "Draft from pass 1." in p2
        assert p1 != p2

    def test_gap_filler_subsequent_passes_fallback_when_current_text_is_none(self) -> None:
        provider = JsonPromptProvider()
        p2 = provider.get_gap_filler_prompt(
            pass_num=2,
            total_passes=3,
            channel_name=ChannelName("Tech Channel"),
            file_name="test.txt",
            raw_text="Fallback to raw when current_text is None.",
            current_text=None,
        )
        assert "Fallback to raw when current_text is None." in p2

    def test_long_and_wide_expander_prompts(self) -> None:
        provider = JsonPromptProvider()

        long_p = provider.get_long_expander_prompt(
            compendium_body="Main body text.",
            complementary_info="Supplementary info.",
        )
        assert "Main body text." in long_p
        assert "Supplementary info." in long_p
        assert "Fernand Braudel" in long_p

        wide_p = provider.get_wide_expander_prompt(
            current_text="Longitudinally expanded text.",
        )
        assert "Longitudinally expanded text." in wide_p
        assert "Karl Jaspers" in wide_p

    def test_inventory_and_batch_notes_and_mocs_prompts(self) -> None:
        provider = JsonPromptProvider()

        inv_p = provider.get_inventory_prompt(
            compendium_title="Compendium Title",
            channel_name=ChannelName("Channel Name"),
            compendium_body="Enriched content body.",
        )
        assert "Compendium Title" in inv_p
        assert "Channel Name" in inv_p
        assert "Enriched content body." in inv_p

        batch_p = provider.get_batch_notes_prompt(
            compendium_title="Compendium Title",
            channel_name=ChannelName("Channel Name"),
            compendium_body="Enriched content body.",
            targets_json='[{"title": "Target 1"}]',
        )
        assert "Compendium Title" in batch_p
        assert "Target Entities to Synthesize in this batch:" in batch_p
        assert '[{"title": "Target 1"}]' in batch_p

        mocs_p = provider.get_mocs_prompt(
            notes_json='[{"title": "Note 1"}]',
        )
        assert "Atomic Notes in Vault:" in mocs_p
        assert '[{"title": "Note 1"}]' in mocs_p

    def test_custom_prompts_json_override(self, tmp_path: Path) -> None:
        custom_prompts = {
            "gap_filler_pass1": {
                "task": "Custom Task 1",
                "skill_name": "none",
                "template": "{task}: Custom Pass 1 for {channel_name} in {file_name} with {raw_text} (total: {total_passes})",
            },
            "gap_filler_pass_subsequent": {
                "task": "Custom Task 2",
                "skill_name": "none",
                "template": "{task}: Custom Pass {pass_num}/{total_passes} (prev {prev_pass_num}) for {channel_name} with {raw_text} & {current_text}",
            },
            "long_expander": {
                "task": "Custom Long",
                "skill_name": "none",
                "template": "{task}: {compendium_body} + {complementary_info}",
            },
            "wide_expander": {
                "task": "Custom Wide",
                "skill_name": "none",
                "template": "{task}: {text}",
            },
            "atomic_inventory": {
                "task": "Custom Inv",
                "skill_name": "none",
                "template": "{task}: {compendium_title} on {channel_name} with {compendium_body}",
            },
            "atomic_batch": {
                "task": "Custom Batch",
                "skill_name": "none",
                "template": "{task}: {compendium_title} on {channel_name} body {compendium_body} targets {targets_json}",
            },
            "reconcile_mocs": {
                "task": "Custom MOC",
                "skill_name": "none",
                "template": "{task}: {notes_json}",
            },
        }
        custom_file = tmp_path / "custom_prompts.json"
        custom_file.write_text(json.dumps(custom_prompts), encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=custom_file)
        p1 = provider.get_gap_filler_prompt(
            pass_num=1,
            total_passes=3,
            channel_name=ChannelName("Custom Channel"),
            file_name="custom.txt",
            raw_text="text",
        )
        assert (
            p1
            == "Custom Task 1: Custom Pass 1 for Custom Channel in custom.txt with text (total: 3)"
        )

        p2 = provider.get_gap_filler_prompt(
            pass_num=2,
            total_passes=3,
            channel_name=ChannelName("Custom Channel"),
            file_name="custom.txt",
            raw_text="raw",
            current_text="draft",
        )
        assert p2 == "Custom Task 2: Custom Pass 2/3 (prev 1) for Custom Channel with raw & draft"

        p_long = provider.get_long_expander_prompt("Body", "Info")
        assert p_long == "Custom Long: Body + Info"

        p_wide = provider.get_wide_expander_prompt("WideText")
        assert p_wide == "Custom Wide: WideText"

        p_inv = provider.get_inventory_prompt("Title", ChannelName("Channel"), "Body")
        assert p_inv == "Custom Inv: Title on Channel with Body"

        p_batch = provider.get_batch_notes_prompt(
            "Title", ChannelName("Channel"), "Body", "Targets"
        )
        assert p_batch == "Custom Batch: Title on Channel body Body targets Targets"

        p_mocs = provider.get_mocs_prompt("Notes")
        assert p_mocs == "Custom MOC: Notes"

    def test_custom_prompts_file_corrupted_falls_back_to_bundled(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "corrupted.json"
        bad_file.write_text("NOT VALID JSON", encoding="utf-8")

        provider = JsonPromptProvider(prompts_path=bad_file)
        assert "gap_filler_pass1" in provider._templates
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
        assert "--- SKILL SPECIFICATION (cresmo-sample) ---" in block
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

    def test_fallbacks_when_template_is_empty(self) -> None:
        provider = JsonPromptProvider()
        # Clear out templates to trigger all hardcoded fallbacks
        provider._templates = {
            "gap_filler_pass1": {"task": "Clean raw", "template": ""},
            "gap_filler_pass_subsequent": {"task": "Deepen prose", "template": ""},
            "long_expander": {"task": "Longue Duree", "template": ""},
            "wide_expander": {"task": "Axial Time", "template": ""},
            "atomic_inventory": {"task": "Extract Items", "template": ""},
            "atomic_batch": {"task": "Synthesize Notes", "template": ""},
            "reconcile_mocs": {"task": "Map MOCs", "template": ""},
        }

        # Gap filler pass 1 fallback
        p1 = provider.get_gap_filler_prompt(1, 2, ChannelName("ChName"), "f.txt", "RawText")
        assert "Clean raw" in p1
        assert "Source Channel: ChName" in p1
        assert "File: f.txt" in p1
        assert "Transcript:\nRawText" in p1
        assert "## Informações Complementares" in p1

        # Gap filler pass 2 fallback with current_text
        p2 = provider.get_gap_filler_prompt(
            2, 2, ChannelName("ChName"), "f.txt", "RawText", current_text="DraftText"
        )
        assert "Deepen prose" in p2
        assert "Source Channel: ChName" in p2
        assert "--- ORIGINAL RAW TRANSCRIPT (GROUND TRUTH REFERENCE) ---\nRawText" in p2
        assert "--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS 1 TO ENRICH) ---\nDraftText" in p2
        assert "Execute Socratic gap filling and theoretical densification." in p2

        # Gap filler pass 2 fallback without current_text
        p2_none = provider.get_gap_filler_prompt(
            2, 2, ChannelName("ChName"), "f.txt", "RawText", current_text=None
        )
        assert (
            "--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS 1 TO ENRICH) ---\nRawText" in p2_none
        )

        # Long expander fallback
        p_long = provider.get_long_expander_prompt("BodyText", "ComplementaryText")
        assert "Longue Duree" in p_long
        assert "Content:\nBodyText" in p_long
        assert "## Informações Complementares\nComplementaryText" in p_long

        # Wide expander fallback
        p_wide = provider.get_wide_expander_prompt("WideText")
        assert "Axial Time" in p_wide
        assert "WideText" in p_wide
        assert p_wide.endswith("WideText")

        # Atomic inventory fallback
        p_inv = provider.get_inventory_prompt("Title", ChannelName("Channel"), "Body")
        assert "Extract Items" in p_inv
        assert "Title: Title" in p_inv
        assert "Channel: Channel" in p_inv
        assert "Content:\nBody" in p_inv
        assert (
            'Output strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]'
            in p_inv
        )

        # Atomic batch fallback
        p_batch = provider.get_batch_notes_prompt(
            "Title", ChannelName("Channel"), "Body", '[{"title": "E1"}]'
        )
        assert "Synthesize Notes" in p_batch
        assert "Source Compendium Title: Title" in p_batch
        assert "Source Channel: Channel" in p_batch
        assert "Source Context:\nBody" in p_batch
        assert 'Target Entities to Synthesize in this batch:\n[{"title": "E1"}]' in p_batch
        assert "Output strictly a JSON array of note objects." in p_batch

        # MOCs fallback
        p_mocs = provider.get_mocs_prompt('[{"title": "Note1"}]')
        assert "Map MOCs" in p_mocs
        assert 'Atomic Notes in Vault:\n[{"title": "Note1"}]' in p_mocs
        assert "Output strictly a JSON array of MOC objects." in p_mocs

    def test_get_raw_index_3_pass_prompts(self) -> None:
        provider = JsonPromptProvider()
        assert "raw_index_summary" in provider._templates
        assert "raw_index_concepts" in provider._templates
        assert "raw_index_synthesis" in provider._templates

        # Pass 1: Concepts (from transcript excerpt)
        concepts_system_instructions, concepts_user_prompt = provider.get_raw_index_concepts_prompt(
            video_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        assert "comma-separated" in concepts_system_instructions.lower()
        assert "Vilfredo Pareto and Elites" in concepts_user_prompt
        assert "A circulação de elites" in concepts_user_prompt

        # Pass 2: Summary (from transcript excerpt)
        summary_system_instructions, summary_user_prompt = provider.get_raw_index_summary_prompt(
            video_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        assert "summarize" in summary_system_instructions.lower()
        assert "Português do Brasil" in summary_system_instructions
        assert "Vilfredo Pareto and Elites" in summary_user_prompt
        assert "A circulação de elites" in summary_user_prompt

        # Pass 3: Synthesis (from summary)
        synthesis_system_instructions, synthesis_user_prompt = (
            provider.get_raw_index_synthesis_prompt(
                video_title="Vilfredo Pareto and Elites",
                summary="A circulação de elites explica a alternância de poder.",
                language="Português do Brasil",
            )
        )
        assert "paratactic" in synthesis_system_instructions.lower()
        assert "ner" in synthesis_system_instructions.lower()
        assert "single paragraph" in synthesis_system_instructions.lower()
        assert "Vilfredo Pareto and Elites" in synthesis_user_prompt
        assert "A circulação de elites" in synthesis_user_prompt

    def test_get_judge_raw_index_prompts(self) -> None:
        provider = JsonPromptProvider()
        assert "judge_raw_index_summary" in provider._templates
        assert "judge_raw_index_concepts" in provider._templates
        assert "judge_raw_index_synthesis" in provider._templates

        # Summary Judge
        summary_judge_system_instructions, summary_judge_user_prompt = (
            provider.get_judge_raw_index_summary_prompt(
                video_title="Pareto and Elites",
                transcript_excerpt="Explicando a circulação das elites na política.",
                summary="Resumo fiel da circulação das elites.",
                language="Português do Brasil",
            )
        )
        assert "impartial evaluator" in summary_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in summary_judge_system_instructions.lower()
        assert "Pareto and Elites" in summary_judge_user_prompt
        assert "Explicando a circulação das elites na política." in summary_judge_user_prompt
        assert "Resumo fiel da circulação das elites." in summary_judge_user_prompt
        assert "true" in summary_judge_user_prompt.lower()

        # Concepts Judge
        concepts_judge_system_instructions, concepts_judge_user_prompt = (
            provider.get_judge_raw_index_concepts_prompt(
                video_title="Pareto and Elites",
                transcript_excerpt="Explicando a circulação das elites na política.",
                concepts="Circulação de Elites, Pareto",
                language="Português do Brasil",
            )
        )
        assert "impartial evaluator" in concepts_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in concepts_judge_system_instructions.lower()
        assert "Pareto and Elites" in concepts_judge_user_prompt
        assert "Explicando a circulação das elites na política." in concepts_judge_user_prompt
        assert "Circulação de Elites, Pareto" in concepts_judge_user_prompt
        assert "true" in concepts_judge_user_prompt.lower()

        # Synthesis Judge
        synthesis_judge_system_instructions, synthesis_judge_user_prompt = (
            provider.get_judge_raw_index_synthesis_prompt(
                video_title="Pareto and Elites",
                transcript_excerpt="Explicando a circulação das elites na política.",
                synthesis="A circulação de elites reflete a alternância política segundo Pareto.",
                language="Português do Brasil",
            )
        )
        assert "impartial evaluator" in synthesis_judge_system_instructions.lower()
        assert "strictly with 'true' or 'false'" in synthesis_judge_system_instructions.lower()
        assert "Pareto and Elites" in synthesis_judge_user_prompt
        assert "Explicando a circulação das elites na política." in synthesis_judge_user_prompt
        assert (
            "A circulação de elites reflete a alternância política segundo Pareto."
            in synthesis_judge_user_prompt
        )
        assert "true" in synthesis_judge_user_prompt.lower()
