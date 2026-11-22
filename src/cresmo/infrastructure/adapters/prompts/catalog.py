"""Strict SSOT Prompt Catalog backed by manifest JSON + Langfuse-mirrored Markdown turns.

Conforms to:
    - ADR-010: Canonical Naming & Zero Legacy Shims
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

import importlib.resources
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from cresmo.domain.value_objects import PromptKey


class PromptCatalogError(Exception):
    """Raised when prompt catalog fails schema validation, Markdown lookup, or bijection."""


class PromptManifestEntry(BaseModel):
    """Strict manifest schema for one entry in `prompts.json` (bans inline prompt bodies)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    description: str
    type: Literal["chat"] = "chat"
    skills: list[str] = Field(default_factory=list)
    langfuse_slug: str | None = None


class PromptSpec(BaseModel):
    """Immutable specification and linkage for a registered chat prompt template."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: PromptKey
    description: str
    prompt_type: Literal["chat"] = "chat"
    system_prompt: str = ""
    user_prompt: str = ""
    skills: list[str] = Field(default_factory=list)
    langfuse_slug: str | None = None

    @property
    def langfuse_name(self) -> str:
        """Deterministic remote Langfuse identifier (e.g. PromptKey.FLUID_PROSE -> cresmo-fluid-prose)."""
        return self.langfuse_slug or f"cresmo-{self.key.value.replace('_', '-')}"

    def to_langfuse_chat_messages(self) -> list[dict[str, str]]:
        """Serialize prompt turns into Langfuse chat message list format."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]


class PromptCatalog(Mapping[PromptKey, PromptSpec]):
    """Immutable, bijectively validated catalog of prompt templates indexed by PromptKey."""

    def __init__(self, specs: dict[PromptKey, PromptSpec]) -> None:
        """Initialize catalog with validated mapping of PromptKey to PromptSpec."""
        self._specs: dict[PromptKey, PromptSpec] = dict(specs)
        self._by_langfuse_name: dict[str, PromptSpec] = {
            spec.langfuse_name: spec for spec in self._specs.values()
        }

    def __getitem__(self, key: PromptKey | str) -> PromptSpec:
        """Retrieve PromptSpec by PromptKey enum, key string, or langfuse_name."""
        if isinstance(key, PromptKey):
            if key in self._specs:
                return self._specs[key]
            raise KeyError(f"Unknown prompt key: '{key}'")
        try:
            enum_key = PromptKey(key)
            if enum_key in self._specs:
                return self._specs[enum_key]
        except ValueError:
            pass
        if key in self._by_langfuse_name:
            return self._by_langfuse_name[key]
        raise KeyError(f"Unknown prompt key: '{key}'")

    def __iter__(self) -> Iterator[PromptKey]:
        """Iterate over canonical PromptKey members in catalog."""
        return iter(self._specs)

    def __len__(self) -> int:
        """Return total count of registered prompts."""
        return len(self._specs)

    def __contains__(self, key: object) -> bool:
        """Check if PromptKey enum or string key exists in catalog."""
        if isinstance(key, PromptKey):
            return key in self._specs
        if isinstance(key, str):
            try:
                enum_key = PromptKey(key)
                return enum_key in self._specs
            except ValueError:
                return key in self._by_langfuse_name
        return False

    def get_by_langfuse_name(self, name: str) -> PromptSpec | None:
        """Lookup prompt spec by its canonical remote Langfuse name."""
        return self._by_langfuse_name.get(name)

    @property
    def langfuse_to_prompt_key(self) -> dict[str, PromptKey]:
        """Mapping from remote Langfuse names to canonical domain PromptKey."""
        return {name: spec.key for name, spec in self._by_langfuse_name.items()}


def _read_markdown_turn(prompts_root: Any, key_name: str, filename: str) -> str:
    """Read one `{system,user}.md` turn from importlib Traversable or filesystem Path."""
    key_dir = prompts_root.joinpath(key_name)
    turn_file = key_dir.joinpath(filename)
    if not turn_file.is_file():
        raise PromptCatalogError(
            f"Missing required Markdown template '{key_name}/{filename}' for prompt key '{key_name}'."
        )
    return str(turn_file.read_text(encoding="utf-8"))


def _validate_no_orphan_prompt_dirs(prompts_root: Any, valid_keys: set[str]) -> None:
    """Fail fast if any subdirectory under `prompts/` does not correspond to a canonical PromptKey."""
    if not prompts_root.is_dir():
        raise PromptCatalogError(f"Prompt Markdown directory not found: {prompts_root}")
    orphans: list[str] = []
    for child in prompts_root.iterdir():
        if child.is_dir() and child.name != "__pycache__" and child.name not in valid_keys:
            orphans.append(child.name)
    if orphans:
        raise PromptCatalogError(f"Orphan prompt directories not in PromptKey: {sorted(orphans)}")


def load_prompt_catalog(path: Path | None = None) -> PromptCatalog:
    """Load and strictly validate the prompt catalog from manifest JSON and Markdown turns.

    Args:
        path: Optional explicit path to a manifest JSON file (whose sibling ``prompts/``
            directory contains ``<key>/{system,user}.md``). Defaults to bundled resources.

    Returns:
        Validated immutable ``PromptCatalog`` covering all canonical ``PromptKey`` values.

    Raises:
        PromptCatalogError: If JSON is invalid, manifest schema fails, Markdown turns are
            missing, orphan directories exist, or keys fail bijection with ``PromptKey``.
    """
    try:
        if path is not None:
            raw_text = path.read_text(encoding="utf-8")
            prompts_root: Any = path.parent / "prompts"
        else:
            res_root = importlib.resources.files("cresmo.infrastructure.resources")
            raw_text = res_root.joinpath("prompts.json").read_text(encoding="utf-8")
            prompts_root = importlib.resources.files("cresmo.infrastructure.resources.prompts")
    except Exception as exc:
        raise PromptCatalogError(f"Failed to read prompt catalog resource: {exc}") from exc

    try:
        raw_data: Any = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise PromptCatalogError(f"Invalid JSON in prompt manifest: {exc}") from exc

    if not isinstance(raw_data, dict):
        raise PromptCatalogError(
            "Prompt manifest root must be a JSON object mapping keys to specs."
        )

    valid_key_names = {member.value for member in PromptKey}
    raw_keys = set(raw_data.keys())

    unknown_keys = sorted(raw_keys - valid_key_names)
    if unknown_keys:
        raise PromptCatalogError(f"Unrecognized prompt keys not in PromptKey enum: {unknown_keys}")

    missing_keys = sorted(valid_key_names - raw_keys)
    if missing_keys:
        raise PromptCatalogError(f"Missing canonical PromptKey entries in manifest: {missing_keys}")

    _validate_no_orphan_prompt_dirs(prompts_root, valid_key_names)

    specs: dict[PromptKey, PromptSpec] = {}
    for key_member in PromptKey:
        entry_raw = raw_data[key_member.value]
        if not isinstance(entry_raw, dict):
            raise PromptCatalogError(
                f"Manifest entry for '{key_member.value}' must be a JSON object."
            )
        try:
            manifest_entry = PromptManifestEntry.model_validate(entry_raw)
        except ValidationError as exc:
            raise PromptCatalogError(
                f"Schema validation failed for manifest entry '{key_member.value}': {exc}"
            ) from exc

        system_prompt = _read_markdown_turn(prompts_root, key_member.value, "system.md")
        user_prompt = _read_markdown_turn(prompts_root, key_member.value, "user.md")

        specs[key_member] = PromptSpec(
            key=key_member,
            description=manifest_entry.description,
            prompt_type=manifest_entry.type,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            skills=list(manifest_entry.skills),
            langfuse_slug=manifest_entry.langfuse_slug,
        )

    return PromptCatalog(specs)
