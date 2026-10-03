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
from typing import Any, ClassVar

from cresmo.application.ports import PromptProviderPort
from cresmo.infrastructure.adapters.prompts.builders import PROMPT_BUILDER_DISPATCH_MAP
from cresmo.infrastructure.adapters.prompts.registry import PromptKey
from cresmo.infrastructure.config import CresmoSettings
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
        language: Canonical configured target language for prompt generation.
        settings: Optional runtime settings instance.
    """

    def __init__(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
        language: str | None = None,
        settings: Any | None = None,
    ) -> None:
        """Initialize prompt provider and load templates from disk or package resources.

        Args:
            prompts_path: Optional custom path to prompts.json. If None, loads package default.
            skills_dir: Optional custom path to .agents/skills directory.
            language: Optional configured target language for prompt generation.
            settings: Optional runtime settings instance conforming to PipelineSettingsProtocol.
        """
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self.language: str = (
            language
            or (getattr(settings, "language", None) if settings is not None else None)
            or CresmoSettings.DEFAULT_LANGUAGE
        )
        self.settings: Any | None = settings
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
        system_instruction = system_instruction.replace("{task}", task).replace(
            "{skill_block}", skill_block
        )

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
        builder = self._DISPATCH_MAP.get(key)
        if builder is None:
            raise ValueError(f"Unsupported prompt key: {key}")
        return builder(self, **context)

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

    _DISPATCH_MAP: ClassVar[dict[PromptKey, Any]] = PROMPT_BUILDER_DISPATCH_MAP
