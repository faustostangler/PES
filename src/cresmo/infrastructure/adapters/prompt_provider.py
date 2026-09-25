"""Decoupled JSON Prompt Provider Adapter.

Loads LLM prompt templates from a centralized JSON resource and integrates
embedded agent skill specifications (e.g. cresmo-expander, cresmo-atomic),
guaranteeing complete decoupling from hard-coded strings in domain and application logic.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
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
        for candidate in _CANDIDATE_SKILLS_DIRS:
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

    def get_raw_prompt_template(self, template_key: str) -> str:
        """Retrieve unformatted raw prompt template with embedded skill block.

        Args:
            template_key: Key in prompts.json (e.g. 'gap_filler_pass1').

        Returns:
            Raw prompt template string with {skill_block} and {task} resolved.
        """
        entry = self._templates.get(template_key, {})
        tpl = entry.get("template", entry.get("task", ""))
        skill_name = entry.get("skill_name", "")
        skill_block = self._get_skill_block(skill_name) if skill_name else ""
        task = entry.get("task", "")
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
        key = "gap_filler_pass1" if pass_num == 1 else "gap_filler_pass_subsequent"
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
        entry = self._templates.get("long_expander", {})
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
            "long_expander",
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Jaspers synchronic wide expansion."""
        entry = self._templates.get("wide_expander", {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", "")
        system_template = entry.get("system_instruction", "")
        skill_block = self._get_skill_block(skill_name)

        if not template and not system_template:
            sys_inst = f"{task}\n\n{skill_block}".strip()
            return sys_inst, current_text

        return self._format_paired_prompt(
            "wide_expander",
            text=current_text,
        )

    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic inventory extraction."""
        entry = self._templates.get("atomic_inventory", {})
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
            "atomic_inventory",
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
        targets_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic note batch synthesis."""
        entry = self._templates.get("atomic_batch", {})
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
            "atomic_batch",
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
        entry = self._templates.get("reconcile_mocs", {})
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
            "reconcile_mocs",
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
            "raw_index_summary",
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
            "raw_index_concepts",
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
            synthesis=synthesis,
            language=language,
        )


class LangfusePromptProvider(PromptProviderPort):
    """Hexagonal Adapter providing prompts via Langfuse with guaranteed local fallback.

    Conforms to ADR-014 and ADR-017:
        - When Langfuse is reachable, retrieves versioned prompts and configs.
        - Guaranteed Availability: When Langfuse is offline or fails, falls back immediately
          to the injected JsonPromptProvider with zero pipeline downtime.
        - Tracks active prompt object/version for linking to LLM generation observations.
    """

    def __init__(
        self,
        langfuse_client: Any | None,
        fallback_provider: PromptProviderPort,
        label: str = "production",
    ) -> None:
        """Initialize Langfuse prompt provider.

        Args:
            langfuse_client: Optional active Langfuse client instance.
            fallback_provider: Injected local PromptProviderPort fallback.
            label: Active prompt version label in Langfuse (e.g. 'production', 'staging').
        """
        self._client = langfuse_client
        self._fallback = fallback_provider
        self._label = label
        self._last_prompt_versions: dict[str, Any] = {}

    def get_last_prompt_version(self, prompt_name: str) -> Any | None:
        """Return the last resolved version for a given prompt identifier."""
        return self._last_prompt_versions.get(prompt_name)

    def _resolve_prompt(
        self,
        prompt_name: str,
        fallback_template: str,
        **kwargs: Any,
    ) -> str:
        """Attempt to fetch and compile prompt from Langfuse with seamless fallback.

        Args:
            prompt_name: Identifier for the prompt registered in Langfuse.
            fallback_template: Ground-truth fallback text generated by fallback provider.
            **kwargs: Template variable substitutions.

        Returns:
            Compiled prompt string.
        """
        if self._client is None:
            return fallback_template

        try:
            prompt = self._client.get_prompt(
                prompt_name,
                label=self._label,
                fallback=fallback_template,
            )
            if hasattr(prompt, "version"):
                self._last_prompt_versions[prompt_name] = prompt.version

            if hasattr(prompt, "compile"):
                return str(prompt.compile(**kwargs))
            return fallback_template
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "[LangfusePromptProvider] Prompt '%s' fetch skipped (%s), using local fallback",
                prompt_name,
                exc,
            )
            return fallback_template

    def get_gap_filler_prompt(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: ChannelName,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) via Langfuse with guaranteed fallback."""
        fallback_sys, fallback_user = self._fallback.get_gap_filler_prompt(
            pass_num=pass_num,
            total_passes=total_passes,
            channel_name=channel_name,
            file_name=file_name,
            raw_text=raw_text,
            current_text=current_text,
        )
        prompt_name = f"cresmo-gap-filler-pass{pass_num}"
        user_prompt = self._resolve_prompt(
            prompt_name=prompt_name,
            fallback_template=fallback_user,
            pass_num=pass_num,
            total_passes=total_passes,
            channel_name=channel_name,
            file_name=file_name,
            raw_text=raw_text,
            current_text=current_text or "",
        )
        return fallback_sys, user_prompt

    def get_long_expander_prompt(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for longitudinal expansion via Langfuse."""
        fallback_sys, fallback_user = self._fallback.get_long_expander_prompt(
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )
        user_prompt = self._resolve_prompt(
            prompt_name="cresmo-long-expander",
            fallback_template=fallback_user,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )
        return fallback_sys, user_prompt

    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for synchronic wide expansion via Langfuse."""
        fallback_sys, fallback_user = self._fallback.get_wide_expander_prompt(
            current_text=current_text
        )
        user_prompt = self._resolve_prompt(
            prompt_name="cresmo-wide-expander",
            fallback_template=fallback_user,
            current_text=current_text,
        )
        return fallback_sys, user_prompt

    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic inventory extraction via Langfuse."""
        fallback_sys, fallback_user = self._fallback.get_inventory_prompt(
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )
        user_prompt = self._resolve_prompt(
            prompt_name="cresmo-atomic-inventory",
            fallback_template=fallback_user,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )
        return fallback_sys, user_prompt

    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName,
        compendium_body: str,
        targets_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for atomic note batch synthesis via Langfuse."""
        fallback_sys, fallback_user = self._fallback.get_batch_notes_prompt(
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )
        user_prompt = self._resolve_prompt(
            prompt_name="cresmo-atomic-batch",
            fallback_template=fallback_user,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )
        return fallback_sys, user_prompt

    def get_mocs_prompt(
        self,
        notes_json: str,
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for MOC reconciliation via Langfuse."""
        fallback_sys, fallback_user = self._fallback.get_mocs_prompt(notes_json=notes_json)
        user_prompt = self._resolve_prompt(
            prompt_name="cresmo-mocs-reconciliation",
            fallback_template=fallback_user,
            notes_json=notes_json,
        )
        return fallback_sys, user_prompt

    def get_raw_index_summary_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Delegate raw index summary prompt formatting to local fallback."""
        return self._fallback.get_raw_index_summary_prompt(
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
        """Delegate raw index concepts prompt formatting to local fallback."""
        return self._fallback.get_raw_index_concepts_prompt(
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            language=language,
        )

    def get_raw_index_concepts_rewrite_prompt(
        self,
        previous_output: str,
        language: str = "Português do Brasil",
    ) -> str:
        """Delegate raw index concepts rewrite prompt formatting to local fallback."""
        return self._fallback.get_raw_index_concepts_rewrite_prompt(
            previous_output=previous_output,
            language=language,
        )

    def get_raw_index_synthesis_prompt(
        self,
        video_title: str,
        summary: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Delegate raw index synthesis prompt formatting to local fallback."""
        return self._fallback.get_raw_index_synthesis_prompt(
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
        """Delegate judge summary prompt formatting to local fallback."""
        return self._fallback.get_judge_raw_index_summary_prompt(
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
        """Delegate judge concepts prompt formatting to local fallback."""
        return self._fallback.get_judge_raw_index_concepts_prompt(
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
        """Delegate judge synthesis prompt formatting to local fallback."""
        return self._fallback.get_judge_raw_index_synthesis_prompt(
            video_title=video_title,
            transcript_excerpt=transcript_excerpt,
            synthesis=synthesis,
            language=language,
        )
