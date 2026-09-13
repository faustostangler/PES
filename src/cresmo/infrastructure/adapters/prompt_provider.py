"""Decoupled JSON Prompt Provider Adapter.

Loads LLM prompt templates from a centralized JSON resource and integrates
embedded agent skill specifications (e.g. cresmo-expander, cresmo-atomic),
guaranteeing complete decoupling from hard-coded strings in domain and application logic.
"""

from __future__ import annotations

import importlib.resources
import json
import logging
from pathlib import Path
from typing import Any

from cresmo.application.ports import PromptProviderPort

logger = logging.getLogger(__name__)

_CANDIDATE_SKILLS_DIRS = (
    Path.cwd() / ".agents" / "skills",
    Path(__file__).resolve().parents[4] / ".agents" / "skills",
)


class JsonPromptProvider(PromptProviderPort):
    """Hexagonal Adapter providing prompt templates from JSON and embedding skills."""

    def __init__(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    @staticmethod
    def _resolve_skills_dir(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory."""
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
            res_traversable = importlib.resources.files("cresmo.infrastructure.resources").joinpath(
                "prompts.json"
            )
            content = res_traversable.read_text(encoding="utf-8")
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

    def get_gap_filler_prompt(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "gap_filler_pass1" if pass_num == 1 else "gap_filler_pass_subsequent"
        legacy_key = "stage2_pass1" if pass_num == 1 else "stage2_pass_subsequent"
        entry = self._templates.get(key) or self._templates.get(legacy_key, {})
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-expander")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if pass_num == 1:
            if not template:
                return (
                    f"{task}\n\n"
                    f"{skill_block}"
                    f"Source Channel: {channel_name}\n"
                    f"File: {file_name}\n\n"
                    f"Transcript:\n{raw_text}\n\n"
                    "Transform into continuous fluid Markdown prose with analytical headings (## and ###) "
                    "and mandatory '## Informações Complementares' section."
                )
            return self._safe_format(
                template,
                task=task,
                total_passes=total_passes,
                channel_name=channel_name,
                skill_block=skill_block,
                file_name=file_name,
                raw_text=raw_text,
            )

        # Subsequent passes (pass 2, 3, etc.)
        prev_draft = current_text if current_text is not None else raw_text
        if not template:
            return (
                f"{task}\n\n"
                f"{skill_block}"
                f"Source Channel: {channel_name}\n\n"
                f"--- ORIGINAL RAW TRANSCRIPT (GROUND TRUTH REFERENCE) ---\n{raw_text}\n\n"
                f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num - 1} TO ENRICH) ---\n{prev_draft}\n\n"
                "Execute Socratic gap filling and theoretical densification."
            )
        return self._safe_format(
            template,
            task=task,
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def get_long_expander_prompt(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-long-expander")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return (
                f"{task}\n\n"
                f"{skill_block}"
                f"Content:\n{compendium_body}\n\n"
                f"## Informações Complementares\n{complementary_info}"
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return (
                f"{task}\n\n"
                f"{skill_block}"
                f"Title: {compendium_title}\n"
                f"Channel: {channel_name}\n\n"
                f"Content:\n{compendium_body}\n\n"
                'Output strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]'
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch")
            or self._templates.get("synthesize_atomic_batch")
            or self._templates.get("stage5_batch_notes", {})
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-atomic")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return (
                f"{task}\n\n"
                f"{skill_block}"
                f"Source Compendium Title: {compendium_title}\n"
                f"Source Channel: {channel_name}\n\n"
                f"Source Context:\n{compendium_body}\n\n"
                f"Target Entities to Synthesize in this batch:\n{targets_json}\n\n"
                "Output strictly a JSON array of note objects."
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def get_mocs_prompt(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-moc-manager")
        template = entry.get("template", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return (
                f"{task}\n\n"
                f"{skill_block}"
                f"Atomic Notes in Vault:\n{notes_json}\n\n"
                "Output strictly a JSON array of MOC objects."
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )
