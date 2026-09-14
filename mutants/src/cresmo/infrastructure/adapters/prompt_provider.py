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
from cresmo.infrastructure.config import find_workspace_root

logger = logging.getLogger(__name__)

_CANDIDATE_SKILLS_DIRS = (
    Path.cwd() / ".agents" / "skills",
    find_workspace_root() / ".agents" / "skills",
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁJsonPromptProviderǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut: MutantDict = {}  # type: ignore
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut: MutantDict = {}  # type: ignore


class JsonPromptProvider(PromptProviderPort):
    """Hexagonal Adapter providing prompt templates from JSON and embedding skills."""

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ__init____mutmut)
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

    def xǁJsonPromptProviderǁ__init____mutmut_orig(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    def xǁJsonPromptProviderǁ__init____mutmut_1(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = None
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    def xǁJsonPromptProviderǁ__init____mutmut_2(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = None
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    def xǁJsonPromptProviderǁ__init____mutmut_3(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(None)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    def xǁJsonPromptProviderǁ__init____mutmut_4(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = None
        self._skill_cache: dict[str, str] = {}
        self._load_templates()

    def xǁJsonPromptProviderǁ__init____mutmut_5(
        self,
        prompts_path: Path | None = None,
        skills_dir: Path | None = None,
    ) -> None:
        self.prompts_path = prompts_path
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self._templates: dict[str, dict[str, str]] = {}
        self._skill_cache: dict[str, str] = None
        self._load_templates()

    @staticmethod
    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut)
    def _resolve_skills_dir(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory."""
        if custom_dir is not None and custom_dir.exists():
            return custom_dir
        for candidate in _CANDIDATE_SKILLS_DIRS:
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_orig(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory."""
        if custom_dir is not None and custom_dir.exists():
            return custom_dir
        for candidate in _CANDIDATE_SKILLS_DIRS:
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_1(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory."""
        if custom_dir is not None or custom_dir.exists():
            return custom_dir
        for candidate in _CANDIDATE_SKILLS_DIRS:
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_2(custom_dir: Path | None) -> Path | None:
        """Resolve valid filesystem path to .agents/skills directory."""
        if custom_dir is None and custom_dir.exists():
            return custom_dir
        for candidate in _CANDIDATE_SKILLS_DIRS:
            if candidate.exists():
                return candidate
        return None

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ_load_templates__mutmut)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_orig(self) -> None:
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_1(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None or self.prompts_path.exists():
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_2(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is None and self.prompts_path.exists():
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_3(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = None
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_4(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(None)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_5(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding=None))
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_6(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="XXutf-8XX"))
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_7(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="UTF-8"))
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_8(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info(None, self.prompts_path)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_9(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", None)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_10(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info(self.prompts_path)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_11(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", )
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_12(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("XXLoaded custom prompts from: %sXX", self.prompts_path)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_13(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("loaded custom prompts from: %s", self.prompts_path)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_14(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("LOADED CUSTOM PROMPTS FROM: %S", self.prompts_path)
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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_15(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning(None, self.prompts_path, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_16(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", None, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_17(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", self.prompts_path, None)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_18(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning(self.prompts_path, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_19(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_20(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed reading custom prompts from %s: %s", self.prompts_path, )

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_21(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("XXFailed reading custom prompts from %s: %sXX", self.prompts_path, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_22(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("failed reading custom prompts from %s: %s", self.prompts_path, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_23(self) -> None:
        """Load prompt template dictionary from explicit path or package resource."""
        if self.prompts_path is not None and self.prompts_path.exists():
            try:
                self._templates = json.loads(self.prompts_path.read_text(encoding="utf-8"))
                logger.info("Loaded custom prompts from: %s", self.prompts_path)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("FAILED READING CUSTOM PROMPTS FROM %S: %S", self.prompts_path, exc)

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

    def xǁJsonPromptProviderǁ_load_templates__mutmut_24(self) -> None:
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
            res_traversable = None
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_25(self) -> None:
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
                None
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_26(self) -> None:
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
            res_traversable = importlib.resources.files(None).joinpath(
                "prompts.json"
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_27(self) -> None:
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
            res_traversable = importlib.resources.files("XXcresmo.infrastructure.resourcesXX").joinpath(
                "prompts.json"
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_28(self) -> None:
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
            res_traversable = importlib.resources.files("CRESMO.INFRASTRUCTURE.RESOURCES").joinpath(
                "prompts.json"
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_29(self) -> None:
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
                "XXprompts.jsonXX"
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_30(self) -> None:
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
                "PROMPTS.JSON"
            )
            content = res_traversable.read_text(encoding="utf-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_31(self) -> None:
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
            content = None
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_32(self) -> None:
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
            content = res_traversable.read_text(encoding=None)
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_33(self) -> None:
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
            content = res_traversable.read_text(encoding="XXutf-8XX")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_34(self) -> None:
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
            content = res_traversable.read_text(encoding="UTF-8")
            self._templates = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_35(self) -> None:
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
            self._templates = None
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_36(self) -> None:
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
            self._templates = json.loads(None)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_37(self) -> None:
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
            logger.error(None, exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_38(self) -> None:
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
            logger.error("Failed loading bundled prompts.json resource: %s", None)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_39(self) -> None:
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
            logger.error(exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_40(self) -> None:
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
            logger.error("Failed loading bundled prompts.json resource: %s", )
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_41(self) -> None:
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
            logger.error("XXFailed loading bundled prompts.json resource: %sXX", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_42(self) -> None:
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
            logger.error("failed loading bundled prompts.json resource: %s", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_43(self) -> None:
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
            logger.error("FAILED LOADING BUNDLED PROMPTS.JSON RESOURCE: %S", exc)
            self._templates = {}

    def xǁJsonPromptProviderǁ_load_templates__mutmut_44(self) -> None:
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
            self._templates = None

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut)
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

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_orig(self, skill_name: str) -> str:
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

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_1(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name not in self._skill_cache:
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

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_2(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is None:
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

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_3(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = None
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_4(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name * "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_5(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir * skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_6(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "XXSKILL.mdXX"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_7(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "skill.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_8(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.MD"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_9(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = None
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_10(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding=None).strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_11(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="XXutf-8XX").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_12(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="UTF-8").strip()
                    self._skill_cache[skill_name] = text
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_13(self, skill_name: str) -> str:
        """Read and cache the SKILL.md specification for a skill."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        if self.skills_dir is not None:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    text = skill_file.read_text(encoding="utf-8").strip()
                    self._skill_cache[skill_name] = None
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_14(self, skill_name: str) -> str:
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
                    logger.warning(None, skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_15(self, skill_name: str) -> str:
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
                    logger.warning("Failed reading skill %s: %s", None, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_16(self, skill_name: str) -> str:
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
                    logger.warning("Failed reading skill %s: %s", skill_file, None)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_17(self, skill_name: str) -> str:
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
                    logger.warning(skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_18(self, skill_name: str) -> str:
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
                    logger.warning("Failed reading skill %s: %s", exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_19(self, skill_name: str) -> str:
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
                    logger.warning("Failed reading skill %s: %s", skill_file, )

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_20(self, skill_name: str) -> str:
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
                    logger.warning("XXFailed reading skill %s: %sXX", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_21(self, skill_name: str) -> str:
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
                    logger.warning("failed reading skill %s: %s", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_22(self, skill_name: str) -> str:
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
                    logger.warning("FAILED READING SKILL %S: %S", skill_file, exc)

        self._skill_cache[skill_name] = ""
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_23(self, skill_name: str) -> str:
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

        self._skill_cache[skill_name] = None
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_24(self, skill_name: str) -> str:
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

        self._skill_cache[skill_name] = "XXXX"
        return ""

    def xǁJsonPromptProviderǁ_get_skill_content__mutmut_25(self, skill_name: str) -> str:
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
        return "XXXX"

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut)
    def _get_skill_block(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if not content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    def xǁJsonPromptProviderǁ_get_skill_block__mutmut_orig(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if not content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    def xǁJsonPromptProviderǁ_get_skill_block__mutmut_1(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = None
        if not content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    def xǁJsonPromptProviderǁ_get_skill_block__mutmut_2(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(None)
        if not content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    def xǁJsonPromptProviderǁ_get_skill_block__mutmut_3(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if content:
            return ""
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    def xǁJsonPromptProviderǁ_get_skill_block__mutmut_4(self, skill_name: str) -> str:
        """Generate formatted skill specification block if skill is available."""
        content = self._get_skill_content(skill_name)
        if not content:
            return "XXXX"
        return f"--- SKILL SPECIFICATION ({skill_name}) ---\n{content}\n\n"

    @staticmethod
    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁ_safe_format__mutmut)
    def _safe_format(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_orig(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_1(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = None
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_2(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = None
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_3(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(None, str(val))
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_4(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", None)
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_5(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(str(val))
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_6(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", )
        return result

    @staticmethod
    def xǁJsonPromptProviderǁ_safe_format__mutmut_7(template: str, **kwargs: Any) -> str:
        """Safely substitute named {keys} without failing on literal JSON braces."""
        result = template
        for key, val in kwargs.items():
            result = result.replace(f"{{{key}}}", str(None))
        return result

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_1(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_2(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "XXgap_filler_pass1XX" if pass_num == 1 else "gap_filler_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_3(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "GAP_FILLER_PASS1" if pass_num == 1 else "gap_filler_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_4(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "gap_filler_pass1" if pass_num != 1 else "gap_filler_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_5(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "gap_filler_pass1" if pass_num == 2 else "gap_filler_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_6(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "gap_filler_pass1" if pass_num == 1 else "XXgap_filler_pass_subsequentXX"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_7(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes."""
        key = "gap_filler_pass1" if pass_num == 1 else "GAP_FILLER_PASS_SUBSEQUENT"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_8(
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
        legacy_key = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_9(
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
        legacy_key = "XXstage2_pass1XX" if pass_num == 1 else "stage2_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_10(
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
        legacy_key = "STAGE2_PASS1" if pass_num == 1 else "stage2_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_11(
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
        legacy_key = "stage2_pass1" if pass_num != 1 else "stage2_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_12(
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
        legacy_key = "stage2_pass1" if pass_num == 2 else "stage2_pass_subsequent"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_13(
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
        legacy_key = "stage2_pass1" if pass_num == 1 else "XXstage2_pass_subsequentXX"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_14(
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
        legacy_key = "stage2_pass1" if pass_num == 1 else "STAGE2_PASS_SUBSEQUENT"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_15(
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
        entry = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_16(
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
        entry = self._templates.get(key) and self._templates.get(legacy_key, {})
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_17(
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
        entry = self._templates.get(None) or self._templates.get(legacy_key, {})
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_18(
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
        entry = self._templates.get(key) or self._templates.get(None, {})
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_19(
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
        entry = self._templates.get(key) or self._templates.get(legacy_key, None)
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_20(
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
        entry = self._templates.get(key) or self._templates.get({})
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_21(
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
        entry = self._templates.get(key) or self._templates.get(legacy_key, )
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_22(
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
        task = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_23(
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
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_24(
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
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_25(
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
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_26(
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
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_27(
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
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_28(
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
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_29(
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
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_30(
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
        skill_name = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_31(
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
        skill_name = entry.get(None, "cresmo-expander")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_32(
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
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_33(
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
        skill_name = entry.get("cresmo-expander")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_34(
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
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_35(
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
        skill_name = entry.get("XXskill_nameXX", "cresmo-expander")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_36(
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
        skill_name = entry.get("SKILL_NAME", "cresmo-expander")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_37(
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
        skill_name = entry.get("skill_name", "XXcresmo-expanderXX")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_38(
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
        skill_name = entry.get("skill_name", "CRESMO-EXPANDER")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_39(
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
        template = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_40(
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
        template = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_41(
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
        template = entry.get("template", None)
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_42(
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
        template = entry.get("")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_43(
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
        template = entry.get("template", )
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_44(
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
        template = entry.get("XXtemplateXX", "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_45(
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
        template = entry.get("TEMPLATE", "")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_46(
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
        template = entry.get("template", "XXXX")
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_47(
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
        skill_block = None

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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_48(
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
        skill_block = self._get_skill_block(None)

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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_49(
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

        if pass_num != 1:
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_50(
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

        if pass_num == 2:
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_51(
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
            if template:
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_52(
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
                    "XXTransform into continuous fluid Markdown prose with analytical headings (## and ###) XX"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_53(
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
                    "transform into continuous fluid markdown prose with analytical headings (## and ###) "
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_54(
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
                    "TRANSFORM INTO CONTINUOUS FLUID MARKDOWN PROSE WITH ANALYTICAL HEADINGS (## AND ###) "
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_55(
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
                    "XXand mandatory '## Informações Complementares' section.XX"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_56(
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
                    "and mandatory '## informações complementares' section."
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_57(
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
                    "AND MANDATORY '## INFORMAÇÕES COMPLEMENTARES' SECTION."
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_58(
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
                None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_59(
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
                task=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_60(
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
                total_passes=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_61(
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
                channel_name=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_62(
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
                skill_block=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_63(
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
                file_name=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_64(
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
                raw_text=None,
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_65(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_66(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_67(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_68(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_69(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_70(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_71(
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_72(
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
        prev_draft = None
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_73(
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
        prev_draft = current_text if current_text is None else raw_text
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_74(
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
        if template:
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_75(
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
                f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num + 1} TO ENRICH) ---\n{prev_draft}\n\n"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_76(
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
                f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num - 2} TO ENRICH) ---\n{prev_draft}\n\n"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_77(
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
                "XXExecute Socratic gap filling and theoretical densification.XX"
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_78(
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
                "execute socratic gap filling and theoretical densification."
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_79(
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
                "EXECUTE SOCRATIC GAP FILLING AND THEORETICAL DENSIFICATION."
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

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_80(
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
            None,
            task=task,
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_81(
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
            task=None,
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_82(
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
            pass_num=None,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_83(
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
            total_passes=None,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_84(
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
            prev_pass_num=None,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_85(
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
            channel_name=None,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_86(
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
            skill_block=None,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_87(
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
            raw_text=None,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_88(
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
            current_text=None,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_89(
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
            task=task,
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_90(
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
            pass_num=pass_num,
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_91(
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
            total_passes=total_passes,
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_92(
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
            prev_pass_num=pass_num - 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_93(
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
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_94(
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
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_95(
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
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_96(
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
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_97(
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
            )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_98(
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
            prev_pass_num=pass_num + 1,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    def xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_99(
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
            prev_pass_num=pass_num - 2,
            channel_name=channel_name,
            skill_block=skill_block,
            raw_text=raw_text,
            current_text=prev_draft,
        )

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_1(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = None
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_2(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") and self._templates.get(
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_3(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get(None) or self._templates.get(
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_4(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("XXlong_expanderXX") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_5(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("LONG_EXPANDER") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_6(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            None, {}
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_7(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", None
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_8(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            {}
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_9(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", )
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_10(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "XXstage3_long_expanderXX", {}
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_11(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "STAGE3_LONG_EXPANDER", {}
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_12(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = None
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_13(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_14(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_15(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_16(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_17(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_18(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_19(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_20(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = None
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_21(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get(None, "cresmo-long-expander")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_22(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_23(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("cresmo-long-expander")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_24(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_25(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("XXskill_nameXX", "cresmo-long-expander")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_26(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("SKILL_NAME", "cresmo-long-expander")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_27(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "XXcresmo-long-expanderXX")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_28(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt."""
        entry = self._templates.get("long_expander") or self._templates.get(
            "stage3_long_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "CRESMO-LONG-EXPANDER")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_29(
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
        template = None
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_30(
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
        template = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_31(
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
        template = entry.get("template", None)
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_32(
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
        template = entry.get("")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_33(
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
        template = entry.get("template", )
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_34(
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
        template = entry.get("XXtemplateXX", "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_35(
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
        template = entry.get("TEMPLATE", "")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_36(
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
        template = entry.get("template", "XXXX")
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_37(
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
        skill_block = None

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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_38(
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
        skill_block = self._get_skill_block(None)

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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_39(
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

        if template:
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

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_40(
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
            None,
            task=task,
            skill_block=skill_block,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_41(
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
            task=None,
            skill_block=skill_block,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_42(
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
            skill_block=None,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_43(
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
            compendium_body=None,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_44(
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
            complementary_info=None,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_45(
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
            task=task,
            skill_block=skill_block,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_46(
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
            skill_block=skill_block,
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_47(
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
            compendium_body=compendium_body,
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_48(
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
            complementary_info=complementary_info,
        )

    def xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_49(
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
            )

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_1(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = None
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_2(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") and self._templates.get(
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_3(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get(None) or self._templates.get(
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_4(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("XXwide_expanderXX") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_5(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("WIDE_EXPANDER") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_6(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            None, {}
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_7(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", None
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_8(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            {}
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_9(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", )
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_10(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "XXstage3_wide_expanderXX", {}
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_11(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "STAGE3_WIDE_EXPANDER", {}
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_12(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = None
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_13(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_14(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_15(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_16(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_17(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_18(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_19(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_20(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = None
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_21(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get(None, "cresmo-wide-expander")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_22(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_23(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("cresmo-wide-expander")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_24(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_25(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("XXskill_nameXX", "cresmo-wide-expander")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_26(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("SKILL_NAME", "cresmo-wide-expander")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_27(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "XXcresmo-wide-expanderXX")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_28(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "CRESMO-WIDE-EXPANDER")
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

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_29(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = None
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_30(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get(None, "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_31(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", None)
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_32(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_33(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", )
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_34(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("XXtemplateXX", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_35(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("TEMPLATE", "")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_36(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt."""
        entry = self._templates.get("wide_expander") or self._templates.get(
            "stage3_wide_expander", {}
        )
        task = entry.get("task", "")
        skill_name = entry.get("skill_name", "cresmo-wide-expander")
        template = entry.get("template", "XXXX")
        skill_block = self._get_skill_block(skill_name)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_37(
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
        skill_block = None

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_38(
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
        skill_block = self._get_skill_block(None)

        if not template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_39(
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

        if template:
            return f"{task}\n\n{skill_block}{current_text}"
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_40(
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
            None,
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_41(
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
            task=None,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_42(
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
            skill_block=None,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_43(
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
            text=None,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_44(
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
            task=task,
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_45(
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
            skill_block=skill_block,
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_46(
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
            text=current_text,
        )

    def xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_47(
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
            )

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_1(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = None
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_2(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") and self._templates.get(
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_3(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get(None) or self._templates.get(
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_4(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("XXatomic_inventoryXX") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_5(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("ATOMIC_INVENTORY") or self._templates.get(
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_6(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            None, {}
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_7(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", None
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_8(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            {}
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_9(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", )
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_10(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "XXstage4_inventoryXX", {}
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_11(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "STAGE4_INVENTORY", {}
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_12(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = None
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_13(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_14(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_15(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_16(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_17(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_18(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_19(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt."""
        entry = self._templates.get("atomic_inventory") or self._templates.get(
            "stage4_inventory", {}
        )
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_20(
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
        skill_name = None
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_21(
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
        skill_name = entry.get(None, "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_22(
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
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_23(
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
        skill_name = entry.get("cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_24(
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
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_25(
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
        skill_name = entry.get("XXskill_nameXX", "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_26(
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
        skill_name = entry.get("SKILL_NAME", "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_27(
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
        skill_name = entry.get("skill_name", "XXcresmo-atomicXX")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_28(
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
        skill_name = entry.get("skill_name", "CRESMO-ATOMIC")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_29(
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
        template = None
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_30(
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
        template = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_31(
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
        template = entry.get("template", None)
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_32(
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
        template = entry.get("")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_33(
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
        template = entry.get("template", )
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_34(
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
        template = entry.get("XXtemplateXX", "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_35(
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
        template = entry.get("TEMPLATE", "")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_36(
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
        template = entry.get("template", "XXXX")
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_37(
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
        skill_block = None

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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_38(
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
        skill_block = self._get_skill_block(None)

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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_39(
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

        if template:
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

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_40(
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
                'XXOutput strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]XX'
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_41(
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
                'output strictly a json array: [{"title": "...", "type": "entity|concept|event|process"}]'
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_42(
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
                'OUTPUT STRICTLY A JSON ARRAY: [{"TITLE": "...", "TYPE": "ENTITY|CONCEPT|EVENT|PROCESS"}]'
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_43(
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
            None,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_44(
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
            task=None,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_45(
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
            skill_block=None,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_46(
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
            compendium_title=None,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_47(
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
            channel_name=None,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_48(
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
            compendium_body=None,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_49(
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
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_50(
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
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_51(
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
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_52(
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
            channel_name=channel_name,
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_53(
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
            compendium_body=compendium_body,
        )

    def xǁJsonPromptProviderǁget_inventory_prompt__mutmut_54(
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
            )

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_1(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = None
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_2(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch")
            or self._templates.get("synthesize_atomic_batch") and self._templates.get("stage5_batch_notes", {})
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_3(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch") and self._templates.get("synthesize_atomic_batch")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_4(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get(None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_5(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("XXatomic_batchXX")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_6(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("ATOMIC_BATCH")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_7(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch")
            or self._templates.get(None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_8(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch")
            or self._templates.get("XXsynthesize_atomic_batchXX")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_9(
        self,
        compendium_title: str,
        channel_name: str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt."""
        entry = (
            self._templates.get("atomic_batch")
            or self._templates.get("SYNTHESIZE_ATOMIC_BATCH")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_10(
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
            or self._templates.get(None, {})
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_11(
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
            or self._templates.get("stage5_batch_notes", None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_12(
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
            or self._templates.get({})
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_13(
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
            or self._templates.get("stage5_batch_notes", )
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_14(
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
            or self._templates.get("XXstage5_batch_notesXX", {})
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_15(
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
            or self._templates.get("STAGE5_BATCH_NOTES", {})
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_16(
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
        task = None
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_17(
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
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_18(
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
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_19(
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
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_20(
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
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_21(
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
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_22(
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
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_23(
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
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_24(
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
        skill_name = None
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_25(
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
        skill_name = entry.get(None, "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_26(
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
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_27(
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
        skill_name = entry.get("cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_28(
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
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_29(
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
        skill_name = entry.get("XXskill_nameXX", "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_30(
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
        skill_name = entry.get("SKILL_NAME", "cresmo-atomic")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_31(
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
        skill_name = entry.get("skill_name", "XXcresmo-atomicXX")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_32(
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
        skill_name = entry.get("skill_name", "CRESMO-ATOMIC")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_33(
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
        template = None
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_34(
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
        template = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_35(
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
        template = entry.get("template", None)
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_36(
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
        template = entry.get("")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_37(
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
        template = entry.get("template", )
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_38(
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
        template = entry.get("XXtemplateXX", "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_39(
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
        template = entry.get("TEMPLATE", "")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_40(
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
        template = entry.get("template", "XXXX")
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_41(
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
        skill_block = None

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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_42(
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
        skill_block = self._get_skill_block(None)

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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_43(
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

        if template:
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_44(
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
                "XXOutput strictly a JSON array of note objects.XX"
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_45(
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
                "output strictly a json array of note objects."
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_46(
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
                "OUTPUT STRICTLY A JSON ARRAY OF NOTE OBJECTS."
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

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_47(
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
            None,
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_48(
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
            task=None,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_49(
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
            skill_block=None,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_50(
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
            compendium_title=None,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_51(
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
            channel_name=None,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_52(
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
            compendium_body=None,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_53(
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
            targets_json=None,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_54(
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
            task=task,
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_55(
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
            skill_block=skill_block,
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_56(
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
            compendium_title=compendium_title,
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_57(
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
            channel_name=channel_name,
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_58(
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
            compendium_body=compendium_body,
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_59(
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
            targets_json=targets_json,
        )

    def xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_60(
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
            )

    @_mutmut_mutated(mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_orig(
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_1(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = None
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_2(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs") and self._templates.get("stage6_mocs", {})
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_3(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs") and self._templates.get("mocs")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_4(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get(None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_5(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("XXreconcile_mocsXX")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_6(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("RECONCILE_MOCS")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_7(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get(None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_8(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("XXmocsXX")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_9(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("MOCS")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_10(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get(None, {})
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_11(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_12(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get({})
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_13(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", )
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_14(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("XXstage6_mocsXX", {})
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_15(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("STAGE6_MOCS", {})
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_16(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = None
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_17(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_18(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("task", None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_19(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_20(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("task", )
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_21(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("XXtaskXX", "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_22(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("TASK", "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_23(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt."""
        entry = (
            self._templates.get("reconcile_mocs")
            or self._templates.get("mocs")
            or self._templates.get("stage6_mocs", {})
        )
        task = entry.get("task", "XXXX")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_24(
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
        skill_name = None
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_25(
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
        skill_name = entry.get(None, "cresmo-moc-manager")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_26(
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
        skill_name = entry.get("skill_name", None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_27(
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
        skill_name = entry.get("cresmo-moc-manager")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_28(
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
        skill_name = entry.get("skill_name", )
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_29(
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
        skill_name = entry.get("XXskill_nameXX", "cresmo-moc-manager")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_30(
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
        skill_name = entry.get("SKILL_NAME", "cresmo-moc-manager")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_31(
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
        skill_name = entry.get("skill_name", "XXcresmo-moc-managerXX")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_32(
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
        skill_name = entry.get("skill_name", "CRESMO-MOC-MANAGER")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_33(
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
        template = None
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_34(
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
        template = entry.get(None, "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_35(
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
        template = entry.get("template", None)
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_36(
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
        template = entry.get("")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_37(
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
        template = entry.get("template", )
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_38(
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
        template = entry.get("XXtemplateXX", "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_39(
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
        template = entry.get("TEMPLATE", "")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_40(
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
        template = entry.get("template", "XXXX")
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_41(
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
        skill_block = None

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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_42(
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
        skill_block = self._get_skill_block(None)

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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_43(
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

        if template:
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

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_44(
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
                "XXOutput strictly a JSON array of MOC objects.XX"
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_45(
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
                "output strictly a json array of moc objects."
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_46(
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
                "OUTPUT STRICTLY A JSON ARRAY OF MOC OBJECTS."
            )
        return self._safe_format(
            template,
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_47(
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
            None,
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_48(
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
            task=None,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_49(
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
            skill_block=None,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_50(
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
            notes_json=None,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_51(
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
            task=task,
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_52(
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
            skill_block=skill_block,
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_53(
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
            notes_json=notes_json,
        )

    def xǁJsonPromptProviderǁget_mocs_prompt__mutmut_54(
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
            )

mutants_xǁJsonPromptProviderǁ__init____mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ__init____mutmut['xǁJsonPromptProviderǁ__init____mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ__init____mutmut['xǁJsonPromptProviderǁ__init____mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ__init____mutmut['xǁJsonPromptProviderǁ__init____mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ__init____mutmut['xǁJsonPromptProviderǁ__init____mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ__init____mutmut['xǁJsonPromptProviderǁ__init____mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁ__init____mutmut_5 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut['xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut['xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ_resolve_skills_dir__mutmut_2 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_load_templates__mutmut['xǁJsonPromptProviderǁ_load_templates__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁ_load_templates__mutmut_44 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_content__mutmut['xǁJsonPromptProviderǁ_get_skill_content__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_content__mutmut_25 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_block__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut['xǁJsonPromptProviderǁ_get_skill_block__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_block__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut['xǁJsonPromptProviderǁ_get_skill_block__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_block__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut['xǁJsonPromptProviderǁ_get_skill_block__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_block__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_get_skill_block__mutmut['xǁJsonPromptProviderǁ_get_skill_block__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁ_get_skill_block__mutmut_4 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁ_safe_format__mutmut['xǁJsonPromptProviderǁ_safe_format__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁ_safe_format__mutmut_7 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_47 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_48'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_48 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_49'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_49 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_50'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_50 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_51'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_51 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_52'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_52 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_53'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_53 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_54'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_54 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_55'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_55 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_56'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_56 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_57'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_57 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_58'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_58 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_59'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_59 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_60'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_60 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_61'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_61 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_62'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_62 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_63'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_63 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_64'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_64 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_65'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_65 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_66'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_66 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_67'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_67 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_68'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_68 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_69'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_69 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_70'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_70 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_71'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_71 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_72'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_72 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_73'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_73 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_74'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_74 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_75'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_75 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_76'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_76 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_77'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_77 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_78'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_78 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_79'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_79 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_80'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_80 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_81'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_81 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_82'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_82 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_83'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_83 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_84'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_84 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_85'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_85 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_86'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_86 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_87'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_87 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_88'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_88 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_89'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_89 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_90'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_90 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_91'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_91 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_92'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_92 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_93'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_93 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_94'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_94 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_95'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_95 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_96'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_96 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_97'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_97 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_98'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_98 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut['xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_99'] = JsonPromptProvider.xǁJsonPromptProviderǁget_gap_filler_prompt__mutmut_99 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_47 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_48'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_48 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_long_expander_prompt__mutmut['xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_49'] = JsonPromptProvider.xǁJsonPromptProviderǁget_long_expander_prompt__mutmut_49 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut['xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_wide_expander_prompt__mutmut_47 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_47 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_48'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_48 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_49'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_49 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_50'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_50 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_51'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_51 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_52'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_52 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_53'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_53 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_inventory_prompt__mutmut['xǁJsonPromptProviderǁget_inventory_prompt__mutmut_54'] = JsonPromptProvider.xǁJsonPromptProviderǁget_inventory_prompt__mutmut_54 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_47 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_48'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_48 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_49'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_49 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_50'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_50 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_51'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_51 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_52'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_52 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_53'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_53 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_54'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_54 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_55'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_55 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_56'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_56 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_57'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_57 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_58'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_58 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_59'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_59 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut['xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_60'] = JsonPromptProvider.xǁJsonPromptProviderǁget_batch_notes_prompt__mutmut_60 # type: ignore # mutmut generated

mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['_mutmut_orig'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_orig # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_1'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_1 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_2'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_2 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_3'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_3 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_4'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_4 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_5'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_5 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_6'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_6 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_7'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_7 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_8'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_8 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_9'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_9 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_10'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_10 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_11'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_11 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_12'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_12 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_13'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_13 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_14'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_14 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_15'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_15 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_16'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_16 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_17'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_17 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_18'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_18 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_19'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_20'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_20 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_21'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_21 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_22'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_22 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_23'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_23 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_24'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_24 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_25'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_25 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_26'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_26 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_27'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_27 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_28'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_28 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_29'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_29 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_30'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_30 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_31'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_31 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_32'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_32 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_33'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_33 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_34'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_34 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_35'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_35 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_36'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_36 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_37'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_37 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_38'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_38 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_39'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_39 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_40'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_40 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_41'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_41 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_42'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_42 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_43'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_43 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_44'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_44 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_45'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_45 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_46'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_46 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_47'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_47 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_48'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_48 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_49'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_49 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_50'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_50 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_51'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_51 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_52'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_52 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_53'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_53 # type: ignore # mutmut generated
mutants_xǁJsonPromptProviderǁget_mocs_prompt__mutmut['xǁJsonPromptProviderǁget_mocs_prompt__mutmut_54'] = JsonPromptProvider.xǁJsonPromptProviderǁget_mocs_prompt__mutmut_54 # type: ignore # mutmut generated
