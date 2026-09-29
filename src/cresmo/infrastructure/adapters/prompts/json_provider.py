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
import sys
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
        facade_mod = sys.modules.get("cresmo.infrastructure.adapters.prompt_provider")
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

    def get_chat_prompt_template(self, template_key: str | PromptKey) -> tuple[str, str]:
        """Retrieve unformatted system instruction and user template with embedded skill block.

        Conforms to ADR-010 and ADR-017 for Chat-Native prompt governance.

        Args:
            template_key: Key in prompts.json (e.g. 'gap_filler_pass1') or PromptKey enum.

        Returns:
            Tuple of (system_instruction, user_template).
        """
        key_str = template_key.value if isinstance(template_key, PromptKey) else template_key
        entry = self._templates.get(key_str, {})
        skill_name = entry.get("skill_name", "")
        skill_block = self._get_skill_block(skill_name) if skill_name else ""
        task = entry.get("task", "")

        system_instruction = entry.get("system_instruction", "")
        if not system_instruction and task:
            system_instruction = task
        system_instruction = system_instruction.replace("{task}", task).replace("{skill_block}", skill_block)

        user_template = entry.get("template", "")
        if not user_template and task and not system_instruction:
            user_template = task

        return system_instruction, user_template

    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> tuple[str, str]:
        """Dispatch prompt formatting by canonical PromptKey.

        Args:
            key: Canonical PromptKey enum member.
            **context: Template variable substitutions.

        Returns:
            Tuple containing (system_instruction, user_prompt).
        """
        match key:
            case PromptKey.GAP_FILLER_PASS1:
                return self._build_gap_filler_pass1(**context)
            case PromptKey.GAP_FILLER_PASS_SUBSEQUENT:
                return self._build_gap_filler_subsequent(**context)
            case PromptKey.LONG_EXPANDER:
                return self._build_long_expander(**context)
            case PromptKey.WIDE_EXPANDER:
                return self._build_wide_expander(**context)
            case PromptKey.ATOMIC_INVENTORY:
                return self._build_atomic_inventory(**context)
            case PromptKey.JUDGE_ATOMIC_INVENTORY:
                return self._build_judge_atomic_inventory(**context)
            case PromptKey.ATOMIC_BATCH:
                return self._build_atomic_batch(**context)
            case PromptKey.RECONCILE_MOCS:
                return self._build_reconcile_mocs(**context)
            case PromptKey.RAW_INDEX_SUMMARY:
                return self._format_paired_prompt(
                    PromptKey.RAW_INDEX_SUMMARY.value,
                    video_title=context.get("video_title", ""),
                    transcript_excerpt=context.get("transcript_excerpt", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case PromptKey.RAW_INDEX_CONCEPTS:
                return self._format_paired_prompt(
                    PromptKey.RAW_INDEX_CONCEPTS.value,
                    video_title=context.get("video_title", ""),
                    transcript_excerpt=context.get("transcript_excerpt", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case PromptKey.RAW_INDEX_CONCEPTS_REWRITE:
                lang = context.get("language", "Português do Brasil")
                prompt_text = self._format_single_prompt(
                    PromptKey.RAW_INDEX_CONCEPTS_REWRITE.value,
                    previous_output=context.get("previous_output", ""),
                    language=lang,
                    language_upper=lang.upper(),
                )
                return "", prompt_text
            case PromptKey.RAW_INDEX_SYNTHESIS:
                return self._format_paired_prompt(
                    PromptKey.RAW_INDEX_SYNTHESIS.value,
                    video_title=context.get("video_title", ""),
                    summary=context.get("summary", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case PromptKey.JUDGE_RAW_INDEX_SUMMARY:
                return self._format_paired_prompt(
                    PromptKey.JUDGE_RAW_INDEX_SUMMARY.value,
                    video_title=context.get("video_title", ""),
                    transcript_excerpt=context.get("transcript_excerpt", ""),
                    summary=context.get("summary", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case PromptKey.JUDGE_RAW_INDEX_CONCEPTS:
                return self._format_paired_prompt(
                    PromptKey.JUDGE_RAW_INDEX_CONCEPTS.value,
                    video_title=context.get("video_title", ""),
                    transcript_excerpt=context.get("transcript_excerpt", ""),
                    concepts=context.get("concepts", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case PromptKey.JUDGE_RAW_INDEX_SYNTHESIS:
                transcript_excerpt = context.get("transcript_excerpt", "")
                return self._format_paired_prompt(
                    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS.value,
                    video_title=context.get("video_title", ""),
                    transcript_excerpt=transcript_excerpt,
                    summary=transcript_excerpt,
                    synthesis=context.get("synthesis", ""),
                    language=context.get("language", "Português do Brasil"),
                )
            case _:
                raise ValueError(f"Unsupported prompt key: {key}")

    def _build_gap_filler_pass1(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.GAP_FILLER_PASS1.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        channel_name = context.get("channel_name", "")
        file_name = context.get("file_name", "")
        raw_text = context.get("raw_text", "")
        total_passes = context.get("total_passes", 1)

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

    def _build_gap_filler_subsequent(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.GAP_FILLER_PASS_SUBSEQUENT.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        pass_num = context.get("pass_num", 2)
        total_passes = context.get("total_passes", 2)
        channel_name = context.get("channel_name", "")
        raw_text = context.get("raw_text", "")
        current_text = context.get("current_text")
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

    def _build_long_expander(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.LONG_EXPANDER.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-long-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        compendium_body = context.get("compendium_body", "")
        complementary_info = context.get("complementary_info", "")

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

    def _build_wide_expander(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.WIDE_EXPANDER.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        current_text = context.get("current_text", "")

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            return sys_inst, current_text

        return self._format_paired_prompt(
            key,
            current_text=current_text,
            text=current_text,
        )

    def _build_atomic_inventory(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.ATOMIC_INVENTORY.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        compendium_title = context.get("compendium_title", "")
        channel_name = context.get("channel_name", "")
        compendium_body = context.get("compendium_body", "")

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

    def _build_judge_atomic_inventory(self, **context: Any) -> tuple[str, str]:
        channel_name = context.get("channel_name", "")
        ch_str = channel_name.value if isinstance(channel_name, ChannelName) else channel_name
        return self._format_paired_prompt(
            PromptKey.JUDGE_ATOMIC_INVENTORY.value,
            compendium_title=context.get("compendium_title", ""),
            channel_name=ch_str,
            compendium_body=context.get("compendium_body", ""),
            inventory_json=context.get("inventory_json", ""),
        )

    def _build_atomic_batch(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.ATOMIC_BATCH.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        compendium_title = context.get("compendium_title", "")
        channel_name = context.get("channel_name", "")
        compendium_body = context.get("compendium_body", "")
        targets_json = context.get("targets_json", "")

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

    def _build_reconcile_mocs(self, **context: Any) -> tuple[str, str]:
        key = PromptKey.RECONCILE_MOCS.value
        entry = self._templates.get(key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-moc-manager")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)
        notes_json = context.get("notes_json", "")

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
