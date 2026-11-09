"""Decoupled JSON Prompt Provider Adapter.

Loads LLM prompt templates from a centralized JSON resource catalog and integrates
embedded agent skill specifications (e.g. cresmo-expander, cresmo-atomic),
guaranteeing complete decoupling from hard-coded strings in domain and application logic.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-017: Prompt Management with Langfuse & Local Fallback
    - ADR-052: Prompt Catalog SSOT Consolidation in JSON Resource
    - SPEC-001: Core Knowledge Synthesis Specifications (Prompt Decoupling)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import structlog

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import ChatPrompt, PromptKey
from cresmo.infrastructure.adapters.prompts.builders import (
    PROMPT_BUILDER_REGISTRY,
    PromptBuilderRegistry,
)
from cresmo.infrastructure.adapters.prompts.catalog import (
    PromptCatalog,
    PromptSpec,
    load_prompt_catalog,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.paths import find_workspace_root

logger = structlog.get_logger(__name__)

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
        registry: PromptBuilderRegistry | None = None,
    ) -> None:
        """Initialize prompt provider and load templates from disk or package resources.

        Args:
            prompts_path: Optional custom path to prompts.json. If None, loads package default.
            skills_dir: Optional custom path to .agents/skills directory.
            language: Optional configured target language for prompt generation.
            settings: Optional runtime settings instance conforming to PipelineSettingsProtocol.
            registry: Optional first-class PromptBuilderRegistry instance.
        """
        self.settings: Any | None = settings
        self.prompts_path = prompts_path or (
            getattr(settings, "prompts_path", None) if settings is not None else None
        )
        resolved_skills_dir = skills_dir or (
            getattr(settings, "skills_dir", None) if settings is not None else None
        )
        self.skills_dir = self._resolve_skills_dir(resolved_skills_dir)
        self.language: str = (
            language
            or (getattr(settings, "language", None) if settings is not None else None)
            or CresmoSettings.DEFAULT_LANGUAGE
        )
        self._registry: PromptBuilderRegistry = registry or PROMPT_BUILDER_REGISTRY
        self._skill_cache: dict[str, str] = {}
        self._catalog: PromptCatalog | None = None
        self._templates: dict[str, dict[str, Any]] = {}
        self._load_templates()

    def _ensure_templates_loaded(self) -> None:
        """Lazily load catalog and custom templates on first access (ADR-055)."""
        if self._catalog is None:
            self._load_templates()

    @property
    def catalog(self) -> PromptCatalog:
        """Immutable PromptCatalog instance holding validated PromptSpec definitions."""
        self._ensure_templates_loaded()
        assert self._catalog is not None
        return self._catalog

    @property
    def templates(self) -> dict[str, dict[str, Any]]:
        """Dictionary of raw template dictionaries indexed by prompt key."""
        self._ensure_templates_loaded()
        return self._templates

    def _load_templates(self) -> None:
        """Load bundled prompt catalog and overlay optional custom prompts file."""
        try:
            self._catalog = load_prompt_catalog()
            self._templates = {k.value: spec.model_dump() for k, spec in self._catalog.items()}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed loading bundled prompt catalog: %s", exc)
            self._catalog = PromptCatalog({})
            self._templates = {}

        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                custom_data = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                if isinstance(custom_data, dict):
                    for k, v in custom_data.items():
                        if isinstance(v, dict):
                            self._templates[k] = v
                    logger.info("Loaded custom prompts from: %s", self.prompts_path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", self.prompts_path, exc)

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

    def _get_skill_content(self, skill_name: str) -> str:
        """Read, sanitize (stripping YAML frontmatter), and cache SKILL.md specification."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    content_clean = re.sub(
                        r"^---\s*\n.*?\n---\s*\n?", "", text, flags=re.DOTALL
                    ).strip()
                    self._skill_cache[skill_name] = content_clean
                    return content_clean
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def _get_skill_block(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if not content:
            return ""
        return f"\n\n{skill_name}:\n{content}"

    def _resolve_skill_block(self, entry: dict[str, Any] | PromptSpec) -> str:
        """Resolve combined skill specification blocks for an entry or spec."""
        if isinstance(entry, PromptSpec):
            skills = entry.skills
        else:
            skills = entry.get("skills", [])
            if not skills and "skill_name" in entry:
                skill_name = entry["skill_name"]
                skills = [skill_name] if skill_name else []
        if isinstance(skills, list) and skills:
            blocks = [self._get_skill_block(str(name)) for name in skills]
            return "".join(block for block in blocks if block)
        return ""

    @staticmethod
    def _safe_format(template: str, **kwargs: Any) -> str:
        """Safely substitute named {{keys}} or {keys} without failing on literal JSON braces."""
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value)).replace(f"{{{key}}}", str(value))
        return result

    def _get_description_for_key(self, key_str: str) -> str:
        """Resolve canonical prompt description from template overlay or catalog."""
        entry = self.templates.get(key_str, {})
        if entry.get("description"):
            return str(entry["description"])
        if key_str in self.catalog:
            return self.catalog[key_str].description
        return ""

    def _build_context_replacements(
        self,
        key_str: str,
        entry: dict[str, Any] | PromptSpec,
        **extra_kwargs: Any,
    ) -> dict[str, str]:
        """Build dictionary of static and dynamic context replacements for template tags."""
        skill_block = self._resolve_skill_block(entry)
        description = self._get_description_for_key(key_str)

        default_lang = self.language or CresmoSettings.DEFAULT_LANGUAGE
        replacements: dict[str, str] = {
            "description": description,
            "skill_block": skill_block,
            "language": default_lang,
        }

        for k, v in extra_kwargs.items():
            if v is not None:
                replacements[k] = str(v)

        return replacements

    def _replace_template_tags(self, template: str, replacements: dict[str, str]) -> str:
        """Find and substitute matching {{key}} or {key} tokens in template, leaving unmatched tokens intact."""
        if not template:
            return ""

        def _repl(match: re.Match[str]) -> str:
            token = match.group(1) or match.group(2)
            if token in replacements:
                return replacements[token]
            return match.group(0)

        return re.sub(r"\{\{([a-zA-Z0-9_\-]+)\}\}|\{([a-zA-Z0-9_\-]+)\}", _repl, template)

    def get_raw_prompt_template(self, key: str | PromptKey) -> str:
        """Retrieve unformatted raw prompt template with embedded skill block.

        Args:
            key: Key in prompts.json (e.g. 'gap_filler') or PromptKey enum.

        Returns:
            Raw prompt template string with {skill_block} and {description} resolved.
        """
        system_prompt, user_prompt = self.get_chat_prompt_template(key)
        return user_prompt or system_prompt

    def get_chat_prompt_template(self, key: str | PromptKey) -> tuple[str, str]:
        """Retrieve unformatted system prompt and user prompt with embedded skill block.

        Conforms to ADR-010, ADR-017, ADR-022, and ADR-050 for Chat-Native prompt governance.

        Args:
            key: Key in prompts.json (e.g. 'gap_filler') or PromptKey enum.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        key_str = key.value if isinstance(key, PromptKey) else key
        entry = self.templates.get(key_str, {})
        replacements = self._build_context_replacements(key_str, entry)

        system_prompt = entry.get("system_prompt", "")
        if not system_prompt and replacements.get("description"):
            system_prompt = replacements["description"]
        system_prompt = self._replace_template_tags(system_prompt, replacements)

        user_prompt = entry.get("user_prompt", "")
        if not user_prompt and replacements.get("description") and not system_prompt:
            user_prompt = replacements["description"]
        user_prompt = self._replace_template_tags(user_prompt, replacements)

        return system_prompt, user_prompt

    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> ChatPrompt:
        """Dispatch prompt formatting by canonical PromptKey.

        Args:
            key: Canonical PromptKey enum member.
            **context: Template variable substitutions.

        Returns:
            ChatPrompt instance containing messages and optional system prompt.
        """
        builder = self._registry.get(key)
        return builder(self, **context)

    def _format_paired_prompt(
        self,
        template_key: str,
        /,
        **kwargs: Any,
    ) -> ChatPrompt:
        """Format (system_prompt, user_prompt) pair into a ChatPrompt for a given template key."""
        entry = self.templates.get(template_key, {})
        description = self._get_description_for_key(template_key)
        skill_block = self._resolve_skill_block(entry)
        system_template = entry.get("system_prompt", "")
        if system_template:
            system_prompt = self._safe_format(
                system_template,
                description=description,
                skill_block=skill_block,
                **kwargs,
            )
        else:
            system_prompt = (
                f"{description}\n\n{skill_block}".strip() if (description or skill_block) else ""
            )
        user_template = entry.get("user_prompt", "")
        user_prompt = self._safe_format(
            user_template,
            description=description,
            skill_block=skill_block,
            **kwargs,
        )
        return ChatPrompt.from_system_and_user(
            user=user_prompt,
            system=system_prompt if system_prompt else None,
        )

    def _format_single_prompt(
        self,
        template_key: str,
        /,
        **kwargs: Any,
    ) -> ChatPrompt:
        """Format a single user prompt into a ChatPrompt for a given template key."""
        entry = self.templates.get(template_key, {})
        description = self._get_description_for_key(template_key)
        user_template = entry.get("user_prompt", "")
        user_prompt = self._safe_format(
            user_template,
            description=description,
            **kwargs,
        )
        return ChatPrompt.from_system_and_user(user=user_prompt, system=None)
