"""Unit tests for decoupled manifest + Markdown JsonPromptProvider (ADR-052, ADR-071)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cresmo.domain.value_objects import ChannelName, PromptKey
from cresmo.infrastructure.adapters.prompts.catalog import PromptCatalogError, load_prompt_catalog
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider


def _write_custom_prompt_bundle(
    root: Path,
    overrides: dict[str, dict[str, object]],
) -> Path:
    """Write a complete manifest JSON and sibling `prompts/<key>/{system,user}.md`."""
    bundled = load_prompt_catalog()
    prompts_dir = root / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, object]] = {}

    for key, spec in bundled.items():
        override = overrides.get(key.value, {})
        key_dir = prompts_dir / key.value
        key_dir.mkdir(parents=True, exist_ok=True)
        sys_text = str(override.get("system_prompt", spec.system_prompt))
        usr_text = str(override.get("user_prompt", spec.user_prompt))
        (key_dir / "system.md").write_text(sys_text, encoding="utf-8")
        (key_dir / "user.md").write_text(usr_text, encoding="utf-8")

        raw_skills = override.get("skills")
        skills = [str(s) for s in raw_skills] if isinstance(raw_skills, list) else list(spec.skills)
        entry: dict[str, object] = {
            "description": str(override.get("description", spec.description)),
            "type": "chat",
            "skills": skills,
        }
        if spec.langfuse_slug is not None:
            entry["langfuse_slug"] = spec.langfuse_slug
        manifest[key.value] = entry

    manifest_file = root / "prompts.json"
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_file


class TestJsonPromptProvider:
    """Hermetic unit tests for prompt template loading, Mustache rendering, and skill embedding."""

    def test_default_prompt_provider_loads_bundled_manifest_and_markdown(self) -> None:
        provider = JsonPromptProvider()
        for key in (
            "gap_filler",
            "long_expander",
            "wide_expander",
            "atomic_inventory",
            "atomic_batch",
            "reconcile_mocs",
            "judge_gap_filler",
            "judge_long_expander",
            "judge_wide_expander",
        ):
            sys_tpl, user_tpl = provider.get_chat_prompt_template(key)
            assert sys_tpl
            assert user_tpl

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
        for criterion in (
            "epistemic_grounding_segregation",
            "conceptual_mechanical_decomposition",
            "braudelian_stratification",
            "genealogy_hidden_agency",
            "competing_hypotheses",
            "extra_info_granularity",
            "linear_style_naturalism",
        ):
            assert criterion in prompt.system_prompt
        user_msg = prompt.messages[-1].content
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
        p1 = prompt1.messages[-1].content
        assert "Your Skill:" in s1
        assert "cresmo-gap-filler:\n" in s1
        assert "Cresmo Style Guide:" in s1
        assert "# Guia de Estilo Cresmo" in s1
        assert "{{cresmo-style-guide}}" not in s1
        assert "{{skill_block}}" not in s1
        assert s1.count("# Guia de Estilo Cresmo") == 1
        assert "Português do Brasil" in s1
        assert "Source Transcript:\nSource fluid text here." in p1
        assert "<draft" not in p1

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
        p2 = prompt2.messages[-1].content
        assert s1 == s2
        assert "Source fluid text here." in p2
        assert '<draft pass="1">\nDraft from pass 1.\n</draft>' in p2

    def test_long_and_wide_expander_prompts(self) -> None:
        provider = JsonPromptProvider()

        long_prompt = provider.get_prompt(
            PromptKey.LONG_EXPANDER,
            source_text="Gap-filled baseline text.",
            pass_num=2,
            current_text="Longitudinal draft pass 1.",
        )
        long_s = long_prompt.system_prompt or ""
        long_p = long_prompt.messages[-1].content
        assert "Gap-filled baseline text." in long_p
        assert '<draft pass="1">\nLongitudinal draft pass 1.\n</draft>' in long_p
        assert "Cresmo Style Guide:\n" in long_s
        assert "cresmo-long-expander:\n" in long_s
        assert "voz autoral do narrador naturalista" in long_s
        assert "BUILD vs. REFINE" in long_s
        assert "<NO_NEW_GAPS/>" in long_s
        assert "Fernand Braudel" in long_s

        wide_prompt = provider.get_prompt(
            PromptKey.WIDE_EXPANDER,
            source_text="Longitudinally expanded text.",
            pass_num=2,
            current_text="Wide draft pass 1.",
        )
        wide_s = wide_prompt.system_prompt or ""
        wide_p = wide_prompt.messages[-1].content
        assert "Longitudinally expanded text." in wide_p
        assert '<draft pass="1">\nWide draft pass 1.\n</draft>' in wide_p
        assert "Cresmo Style Guide:\n" in wide_s
        assert "cresmo-wide-expander:\n" in wide_s
        assert "voz autoral do narrador naturalista" in wide_s
        assert "BUILD vs. REFINE" in wide_s
        assert "<NO_NEW_GAPS/>" in wide_s
        assert "Synchrony & Connectivity" in wide_s
        assert "Parallelism & Analogy" in wide_s
        assert wide_s.startswith("You are the Wide Expander agent within the Cresmo ecosystem.")

    def test_inventory_and_batch_notes_and_mocs_prompts(self) -> None:
        provider = JsonPromptProvider()

        inv_prompt = provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            content_title="Compendium Title",
            channel_name=ChannelName("Tech Channel"),
            compendium_body="Body text.",
        )
        assert "Compendium Title" in inv_prompt.messages[-1].content
        assert "Tech Channel" in inv_prompt.messages[-1].content

        batch_prompt = provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title="Compendium Title",
            channel_name=ChannelName("Tech Channel"),
            compendium_body="Body text.",
            targets_json='["Target 1"]',
        )
        assert '["Target 1"]' in batch_prompt.messages[-1].content

        mocs_prompt = provider.get_prompt(
            PromptKey.RECONCILE_MOCS,
            existing_mocs="MOC A",
            notes_json='[{"title": "Note 1"}]',
        )
        assert '[{"title": "Note 1"}]' in mocs_prompt.messages[-1].content

    def test_raw_index_3_pass_rewrite_and_judge_prompts(self) -> None:
        provider = JsonPromptProvider()

        concepts_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_CONCEPTS,
            content_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        assert "comma-separated" in (concepts_prompt.system_prompt or "").lower()
        assert "Vilfredo Pareto and Elites" in concepts_prompt.messages[-1].content

        # ADR-071 parity fix: RAW_INDEX_CONCEPTS_REWRITE preserves its system.md prompt
        rewrite_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
            previous_output="Concept A, Concept B",
            language="English",
        )
        assert rewrite_prompt.system_prompt is not None
        assert len(rewrite_prompt.system_prompt.strip()) > 100
        assert "English" in rewrite_prompt.system_prompt
        assert "Concept A, Concept B" in rewrite_prompt.messages[-1].content

        summary_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_SUMMARY,
            content_title="Vilfredo Pareto and Elites",
            transcript_excerpt="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        assert "synthesize" in (summary_prompt.system_prompt or "").lower()

        synthesis_prompt = provider.get_prompt(
            PromptKey.RAW_INDEX_SYNTHESIS,
            channel_name=ChannelName("Tech"),
            content_title="Vilfredo Pareto and Elites",
            summary="A circulação de elites explica a alternância de poder.",
            language="Português do Brasil",
        )
        assert "paratactic" in (synthesis_prompt.system_prompt or "").lower()

        judge_synth = provider.get_prompt(
            PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
            stage_name="raw_index_synthesis",
            criteria_json='["index_synthesis_quality"]',
            source_text="Explicando a circulação das elites na política.",
            candidate_text="A circulação de elites reflete a alternância política segundo Pareto.",
        )
        assert "impartial evaluator" in (judge_synth.system_prompt or "").lower()
        assert (
            "Explicando a circulação das elites na política." in judge_synth.messages[-1].content
        )

    def test_custom_manifest_and_markdown_override_and_multi_skill_block(
        self, tmp_path: Path
    ) -> None:
        skills_dir = tmp_path / "skills"
        for name, body in (
            ("skill-a", "Skill A Spec Content"),
            ("skill-b", "Skill B Spec Content"),
        ):
            (skills_dir / name).mkdir(parents=True)
            (skills_dir / name / "SKILL.md").write_text(body, encoding="utf-8")

        manifest_file = _write_custom_prompt_bundle(
            tmp_path,
            {
                "fluid_prose": {
                    "description": "Custom Fluid Desc",
                    "skills": ["skill-a", "skill-b"],
                    "system_prompt": "{{description}}\n\n{{skill_block}}",
                    "user_prompt": "Run task with {{raw_text}}",
                }
            },
        )

        provider = JsonPromptProvider(prompts_path=manifest_file, skills_dir=skills_dir)
        sys_inst, user_tpl = provider.get_chat_prompt_template(PromptKey.FLUID_PROSE)
        assert "Custom Fluid Desc" in sys_inst
        assert "skill-a:\nSkill A Spec Content" in sys_inst
        assert "skill-b:\nSkill B Spec Content" in sys_inst
        assert user_tpl == "Run task with {{raw_text}}"

        chat = provider.get_prompt(PromptKey.FLUID_PROSE, raw_text="Transcript body")
        assert chat.messages[-1].content == "Run task with Transcript body"

    def test_corrupted_manifest_raises_prompt_catalog_error(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "prompts.json"
        bad_file.write_text("NOT VALID JSON", encoding="utf-8")
        with pytest.raises(PromptCatalogError, match="Invalid JSON"):
            JsonPromptProvider(prompts_path=bad_file)

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
        assert "Test spoken raw transcript content." in prompt.messages[-1].content

    def test_json_prompt_provider_respects_settings_paths(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "custom_skills"
        (skills_dir / "cresmo-custom").mkdir(parents=True)
        (skills_dir / "cresmo-custom" / "SKILL.md").write_text("Custom Skill Doc", encoding="utf-8")

        manifest_file = _write_custom_prompt_bundle(
            tmp_path,
            {
                "fluid_prose": {
                    "skills": ["cresmo-custom"],
                    "system_prompt": "Custom System {{cresmo-custom}}",
                    "user_prompt": "Custom User {{raw_text}}",
                }
            },
        )

        provider = JsonPromptProvider(
            prompts_path=manifest_file,
            skills_dir=skills_dir,
            language="en-US",
        )
        assert provider.prompts_path == manifest_file
        assert provider.skills_dir == skills_dir
        assert provider.default_language == "en-US"
        chat = provider.get_prompt(PromptKey.FLUID_PROSE, raw_text="Hello")
        assert chat.system_prompt == "Custom System Custom Skill Doc"
        assert chat.messages[-1].content == "Custom User Hello"


def test_noop_prompt_provider_supports_expander_and_judge_keys() -> None:
    """Verify NoOpPromptProviderPort binds unified raw/current variables and all stage judge keys."""
    from cresmo.application.ports.prompt import NoOpPromptProviderPort

    noop = NoOpPromptProviderPort()
    for key in (PromptKey.LONG_EXPANDER, PromptKey.WIDE_EXPANDER):
        prompt = noop.get_prompt(
            key,
            raw_text="Unified source prose.",
            pass_num=2,
            total_passes=5,
            current_text="Draft pass 1.",
            channel_name="TestChan",
        )
        user_msg = prompt.messages[-1].content
        assert "Unified source prose." in user_msg
        assert "Draft pass 1." in user_msg

    for judge_key in (
        PromptKey.JUDGE_GAP_FILLER,
        PromptKey.JUDGE_LONG_EXPANDER,
        PromptKey.JUDGE_WIDE_EXPANDER,
    ):
        judge_prompt = noop.get_prompt(
            judge_key,
            stage_name=judge_key.value.removeprefix("judge_"),
            criteria_json='["extra_info_granularity"]',
            source_text="Source",
            candidate_text="Candidate",
        )
        assert "Candidate" in judge_prompt.messages[-1].content
