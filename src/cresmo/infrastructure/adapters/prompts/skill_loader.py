"""Skill document resolution, YAML frontmatter stripping, and in-memory caching.

Conforms to:
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from cresmo.infrastructure.paths import find_workspace_root

_YAML_FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n.*?\r?\n---\s*(?:\r?\n)?", re.DOTALL)


def strip_yaml_frontmatter(text: str) -> str:
    """Remove leading YAML frontmatter block (`--- ... ---`) from Markdown text.

    Args:
        text: Raw Markdown skill document contents.

    Returns:
        Markdown text without leading YAML frontmatter, stripped of leading whitespace.
    """
    if not text.startswith("---"):
        return text
    match = _YAML_FRONTMATTER_RE.match(text)
    if match is None:
        return text
    return text[match.end() :].lstrip("\r\n")


class SkillDocumentLoader:
    """Resolve, strip frontmatter from, and cache `.agents/skills/*/SKILL.md` documents."""

    def __init__(self, skills_dir: Path | None = None) -> None:
        self._custom_skills_dir = skills_dir
        self._resolved_dir: Path | None = None
        self._cache: dict[str, str] = {}

    @property
    def skills_dir(self) -> Path:
        """Resolved root directory containing `<skill-name>/SKILL.md` folders."""
        if self._resolved_dir is None:
            if self._custom_skills_dir is not None:
                self._resolved_dir = self._custom_skills_dir
            else:
                self._resolved_dir = find_workspace_root() / ".agents" / "skills"
        return self._resolved_dir

    def read_skill(self, skill_name: str) -> str:
        """Read and cache one skill document with leading YAML frontmatter stripped.

        Args:
            skill_name: Skill directory name under ``skills_dir``.

        Returns:
            Clean Markdown body of ``SKILL.md``, or empty string if missing.
        """
        if skill_name in self._cache:
            return self._cache[skill_name]

        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if not skill_path.is_file():
            self._cache[skill_name] = ""
            return ""

        raw = skill_path.read_text(encoding="utf-8")
        cleaned = strip_yaml_frontmatter(raw).strip()
        self._cache[skill_name] = cleaned
        return cleaned

    def build_skill_replacements(
        self,
        skills: Sequence[str],
        templates: Sequence[str],
    ) -> dict[str, str]:
        """Build inline `{{<skill-name>}}` and aggregate `{{skill_block}}` replacements.

        Skills explicitly referenced inline via `{{<skill-name>}}` in any template are
        excluded from `skill_block` to prevent duplicate prompt injection.

        Args:
            skills: Ordered sequence of skill names declared for the prompt.
            templates: Prompt template texts (typically system and user turns).

        Returns:
            Replacement mapping keyed by each skill name plus ``"skill_block"``.
        """
        combined = "\n".join(templates)
        replacements: dict[str, str] = {}
        block_sections: list[str] = []

        for skill_name in skills:
            content = self.read_skill(skill_name)
            replacements[skill_name] = content
            inline_pattern = re.compile(rf"\{{\{{\s*{re.escape(skill_name)}\s*\}}\}}")
            if content and not inline_pattern.search(combined):
                block_sections.append(f"{skill_name}:\n{content}")

        replacements["skill_block"] = "\n\n".join(block_sections)
        return replacements
