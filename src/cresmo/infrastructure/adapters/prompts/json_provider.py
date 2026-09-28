"""Decoupled JSON Prompt Provider Adapter.

Loads LLM prompt templates from a centralized JSON resource and integrates
embedded agent skill specifications (e.g. cresmo-expander, cresmo-atomic),
guaranteeing complete decoupling from hard-coded strings in domain and application logic.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-017: Prompt Management with Langfuse & Local Fallback
    - SPEC-001: Core Knowledge Synthesis Specifications (Prompt Decoupling)
"""

from __future__ import annotations

import importlib.resources
import json
import logging
from pathlib import Path
from typing import Any

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import ChannelName
from cresmo.infrastructure.adapters.prompts.registry import PromptKey
from cresmo.infrastructure.paths import find_workspace_root

logger = logging.getLogger(__name__)

_CANDIDATE_SKILLS_DIRS = (
    Path.cwd() / ".agents" / "skills",
    find_workspace_root() / ".agents" / "skills",
)


class JsonPromptProvider(PromptProviderPort):
    """Hexagonal Adapter providing prompt templates from JSON and embedding skills.

    Acts as an Anti-Corruption Layer (ACL), ensuring prompt engineering templates and
    agent skill markdown files (.agents/skills) are managed externally from domain code.

    Attributes:
        prompts_path: Optional explicit filesystem path to a JSON templates file.
        skills_dir: Resolved directory containing agent skill markdown files.
    """

    def __init__(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        """Initialize prompt provider and load templates from disk or package resources.

        Args:
            prompts_path: Optional custom path to prompts.json. If None, loads package default.
            skills_dir: Optional custom path to .agents/skills directory.
        """
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    @staticmethod
    def _resolve_skills_dir(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory.

        Args:
            custom_dir: Optional explicitly provided path.

        Returns:
            Resolved Path instance if valid, or None.
        """
        if custom_dir is not None and custom_dir.exists():
            return custom_dir
        import cresmo.infrastructure.adapters.prompt_provider as facade_mod

        candidates = getattr(facade_mod, "_CANDIDATE_SKILLS_DIRS", _CANDIDATE_SKILLS_DIRS)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _load_templates(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", self.prompts_path, exc)

        # Fallback to bundled package resource
        try:
            resource_traversable = importlib.resources.files(
                "cresmo.infrastructure.resources"
            ).joinpath("prompts.json")
            content = resource_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def _get_skill_content(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def _get_skill_block(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if not content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    @staticmethod
    def _safe_format(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result

    def get_raw_prompt_template(self, template_key: str | PromptKey) -> str:
        """Retrieve unformatted raw prompt template with embedded skill block.

        Args:
            template_key: Key in prompts.json (e.g. 'gap_filler_pass1') or PromptKey enum.

        Returns:
            Raw prompt template string with {skill_block} and {task} resolved.
        """
        key_str = template_key.value if isinstance(template_key, PromptKey) else template_key
        entry = self._templates.get(key_str, {})
        skill_name = entry.get("skill_name", "")
        skill_block = self._get_skill_block(skill_name) if skill_name else ""
        task = entry.get("task", "")

        system_instruction = entry.get("system_instruction", "")
        template = entry.get("template", "")

        tpl = template or system_instruction or task or entry.get("task", "")

        return tpl.replace("{task}", task).replace("{skill_block}", skill_block)

    def get_gap_filler_prompt(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: ChannelName,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Socratic gap filling."""
        key = (
            PromptKey.GAP_FILLER_PASS1.value
            if pass_num == 1
            else PromptKey.GAP_FILLER_PASS_SUBSEQUENT.value
        )
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if pass_num == 1:
            if not template and not system_template:
                sys_inst = f"{task}\n\n{skill_block}".strip()
                user_p = (
                    f"Source Channel: {channel_name}\n"
                    f"File: {file_name}\n\n"
                    f"Transcript:\n{raw_text}\n\n"
                    "Transform into continuous fluid Markdown prose with analytical headings (## and ###) "
                    "and mandatory '## Informações Complementares' section."
                )
                return sys_inst, user_p

            return self._format_paired_prompt(
                key,
                total_passes=total_passes,
                channel_name=channel_name,
                file_name=file_name,
                raw_text=raw_text,
            )

        # Subsequent passes (pass 2, 3, etc.)
        prev_draft = current_text if current_text is not None else raw_text
        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            user_p = (
                f"Source Channel: {channel_name}\n\n"
                f"--- ORIGINAL RAW TRANSCRIPT (GROUND TRUTH REFERENCE) ---\n{raw_text}\n\n"
                f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num - 1} TO ENRICH) ---\n{prev_draft}\n\n"
                "Execute Socratic gap filling and theoretical densification."
            )
            return sys_inst, user_p

        return self._format_paired_prompt(
            key,
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def get_long_expander_prompt(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Braudelian longitudinal expansion."""
        key = PromptKey.LONG_EXPANDER.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-long-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            user_p = (
                f"Content:\n{compendium_body}\n\n"
                f"## Informações Complementares\n{complementary_info}"
            )
            return sys_inst, user_p

        return self._format_paired_prompt(
            key,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Jaspers synchronic wide expansion."""
        key = PromptKey.WIDE_EXPANDER.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            return sys_inst, current_text

        return self._format_paired_prompt(
            key,
            current_text=current_text,
            text=current_text,
        )

    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic inventory extraction."""
        key = PromptKey.ATOMIC_INVENTORY.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            user_p = (
                f"Title: {compendium_title}\n"
                f"Channel: {channel_name}\n\n"
                f"Content:\n{compendium_body}\n\n"
                'Output strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]'
            )
            return sys_inst, user_p

        return self._format_paired_prompt(
            key,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def get_judge_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName | str,
        compendium_body: str,
        inventory_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic inventory LLM-as-a-judge verification."""
        ch_str = channel_name.value if isinstance(channel_name, ChannelName) else channel_name
        return self._format_paired_prompt(
            PromptKey.JUDGE_ATOMIC_INVENTORY.value,
            compendium_title=compendium_title,
            channel_name=ch_str,
            compendium_body=compendium_body,
            inventory_json=inventory_json,
        )

    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
        targets_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic note batch synthesis."""
        key = PromptKey.ATOMIC_BATCH.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            user_p = (
                f"Source Compendium Title: {compendium_title}\n"
                f"Source Channel: {channel_name}\n\n"
                f"Source Context:\n{compendium_body}\n\n"
                f"Target Entities to Synthesize in this batch:\n{targets_json}\n\n"
                "Output strictly a JSON array of note objects."
            )
            return sys_inst, user_p

        return self._format_paired_prompt(
            key,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def get_mocs_prompt(
        self,
        notes_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for MOC reconciliation."""
        key = PromptKey.RECONCILE_MOCS.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-moc-manager")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            user_p = (
                f"Atomic Notes in Vault:\n{notes_json}\n\n"
                "Output strictly a JSON array of MOC objects."
            )
            return sys_inst, user_p

        return self._format_paired_prompt(
            key,
            notes_json=notes_json,
        )

    def _format_paired_prompt(
        self,
        template_key: str,
        **kwargs: Any,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) pair for a given template key."""
        entry = self._templates.get(template_key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "")
        skill_block = self._get_skill_block(skill_name) if skill_name else ""
        system_template = entry.get("system_instruction", "")
        if system_template:
            system_instruction = self._safe_format(
                system_template, task=task, skill_block=skill_block, **kwargs
            )
        else:
            system_instruction = f"{task}\n\n{skill_block}".strip() if (task or skill_block) else ""
        template = entry.get("template", "")
        user_prompt = self._safe_format(template, task=task, skill_block=skill_block, **kwargs)
        return system_instruction, user_prompt

    def _format_single_prompt(
        self,
        template_key: str,
        **kwargs: Any,
    ) -> str:
        """Format a single user prompt string for a given template key."""
        entry = self._templates.get(template_key, {})
        task = entry.get("task", "")
        template = entry.get("template", "")
        return self._safe_format(template, task=task, **kwargs)

    def get_raw_index_summary_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Pass 1 raw transcript summarization."""
        return self._format_paired_prompt(
            PromptKey.RAW_INDEX_SUMMARY.value,
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            language=language,
        )

    def get_raw_index_concepts_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for key concepts extraction from raw transcript."""
        return self._format_paired_prompt(
            PromptKey.RAW_INDEX_CONCEPTS.value,
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            language=language,
        )

    def get_raw_index_concepts_rewrite_prompt(
        self,
        previous_output: str,
        language: str = "Português do Brasil",
    ) -> str:
        """Format corrective rewrite prompt when key concepts extraction violates format rules."""
        return self._format_single_prompt(
            "raw_index_concepts_rewrite",
            previous_output=previous_output,
            language=language,
            language_upper=language.upper(),
        )

    def get_raw_index_synthesis_prompt(
        self,
        video_title: str,
        summary: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for dense paratactic synthesis paragraph."""
        return self._format_paired_prompt(
            "raw_index_synthesis",
            video_title=video_title,
            summary=summary,
            language=language,
        )

    def get_judge_raw_index_summary_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        summary: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge summary compliance verification."""
        return self._format_paired_prompt(
            "judge_raw_index_summary",
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            summary=summary,
            language=language,
        )

    def get_judge_raw_index_concepts_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        concepts: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge concepts compliance verification."""
        return self._format_paired_prompt(
            "judge_raw_index_concepts",
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            concepts=concepts,
            language=language,
        )

    def get_judge_raw_index_synthesis_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        synthesis: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge synthesis compliance verification."""
        return self._format_paired_prompt(
            "judge_raw_index_synthesis",
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            summary=transcript_excerpt,
            synthesis=synthesis,
            language=language,
        )
