"""Local JSON manifest + Markdown Chat-Native PromptProviderPort adapter.

Conforms to:
    - ADR-010: Canonical Naming & Zero Legacy Shims
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import PromptKey
from cresmo.domain.value_objects.prompt import ChatPrompt
from cresmo.infrastructure.adapters.prompts.catalog import (
    PromptCatalog,
    PromptSpec,
    load_prompt_catalog,
)
from cresmo.infrastructure.adapters.prompts.context_normalizer import (
    DEFAULT_LANGUAGE,
    normalize_prompt_context,
)
from cresmo.infrastructure.adapters.prompts.skill_loader import SkillDocumentLoader
from cresmo.infrastructure.adapters.prompts.template_renderer import TemplateRenderer


class JsonPromptProvider(PromptProviderPort):
    """Local prompt provider backed by `prompts.json` manifest + Markdown chat turns."""

    def __init__(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
        language: str | None = None,
        *,
        default_language: str = DEFAULT_LANGUAGE,
        skill_loader: SkillDocumentLoader | None = None,
        template_renderer: TemplateRenderer | None = None,
    ) -> None:
        resolved_lang = (
            language if isinstance(language, str) and language.strip() else default_language
        )

        self.prompts_path = prompts_path
        self.skills_dir = skills_dir
        self._prompts_path = prompts_path
        self.language = resolved_lang
        self.default_language = resolved_lang
        self._skill_loader = skill_loader or SkillDocumentLoader(skills_dir=skills_dir)
        self._renderer = template_renderer or TemplateRenderer()
        self._catalog: PromptCatalog | None = None
        self._templates: dict[str, dict[str, Any]] = {}
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self._catalog is None:
            self._catalog = load_prompt_catalog(path=self._prompts_path)
            self._templates = {
                spec.key.value: {
                    "description": spec.description,
                    "type": spec.prompt_type,
                    "system_prompt": spec.system_prompt,
                    "user_prompt": spec.user_prompt,
                    "skills": list(spec.skills),
                    "langfuse_slug": spec.langfuse_slug,
                }
                for spec in self._catalog.values()
            }

    @property
    def catalog(self) -> PromptCatalog:
        """Validated immutable prompt catalog."""
        self._ensure_loaded()
        assert self._catalog is not None
        return self._catalog

    @property
    def templates(self) -> dict[str, dict[str, Any]]:
        """Dictionary view of loaded prompt templates keyed by canonical PromptKey value."""
        self._ensure_loaded()
        return self._templates

    def _resolve_spec(self, key: str | PromptKey) -> PromptSpec:
        return self.catalog[key]

    def _build_static_replacements(self, spec: PromptSpec) -> dict[str, str]:
        replacements = self._skill_loader.build_skill_replacements(
            skills=spec.skills,
            templates=(spec.system_prompt, spec.user_prompt),
        )
        replacements["description"] = spec.description
        replacements["language"] = self.default_language
        return replacements

    def get_raw_prompt_template(self, key: str | PromptKey) -> str:
        """Return raw concatenated system + user template with static skills/description resolved."""
        system_tpl, user_tpl = self.get_chat_prompt_template(key)
        if system_tpl and user_tpl:
            return f"{system_tpl}\n\n{user_tpl}"
        return system_tpl or user_tpl

    def get_chat_prompt_template(self, key: str | PromptKey) -> tuple[str, str]:
        """Return `(system_template, user_template)` with skills resolved and runtime Mustache intact.

        Used by `cresmo seed-prompts` to upload Langfuse Chat-Native prompts while keeping
        runtime placeholders (`{{raw_text}}`, `{{draft_section}}`, etc.) uncompiled.
        """
        spec = self._resolve_spec(key)
        static_vars = self._build_static_replacements(spec)
        system_tpl = self._renderer.render(spec.system_prompt, static_vars)
        user_tpl = self._renderer.render(spec.user_prompt, static_vars)
        return system_tpl, user_tpl

    def get_prompt(self, key: PromptKey, **context: Any) -> ChatPrompt:
        """Render a complete local ChatPrompt with shared normalization and Mustache rendering.

        Args:
            key: Canonical PromptKey enum member.
            **context: Runtime template variables (including optional Domain VOs).

        Returns:
            Rendered ``ChatPrompt`` with both system and user turns preserved.
        """
        spec = self._resolve_spec(key)
        variables = self._build_static_replacements(spec)
        variables.update(
            normalize_prompt_context(
                key,
                context,
                default_language=self.default_language,
            )
        )
        system_rendered = self._renderer.render(spec.system_prompt, variables)
        user_rendered = self._renderer.render(spec.user_prompt, variables)
        return ChatPrompt.from_system_and_user(
            system=system_rendered,
            user=user_rendered,
        )
