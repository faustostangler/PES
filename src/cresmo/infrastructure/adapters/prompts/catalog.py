"""Unified Prompt Catalog SSOT and Metadata Specification for Cresmo.

Provides a Single Source of Truth (SSOT) loaded directly from prompts.json,
mapping internal template keys, Langfuse versioned prompt names, agent skills,
and semantic descriptions with fail-fast bijective validation against PromptKey.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-014: Fail-Fast Observability Preflight
    - ADR-017: Prompt Management with Langfuse & Local Fallback
    - ADR-052: Prompt Catalog SSOT Consolidation in JSON Resource
"""

from __future__ import annotations

import importlib.resources
import json
from collections.abc import Iterator, Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from cresmo.domain.value_objects import PromptKey
from cresmo.infrastructure.config import CresmoSettings


class PromptCatalogError(Exception):
    """Raised when prompt catalog fails schema validation or PromptKey bijection."""


class PromptSpec(BaseModel):
    """Immutable specification and linkage for a registered prompt template.

    Attributes:
        key: Canonical internal PromptKey enum (SSOT).
        description: Architectural responsibility and synthesis intent.
        system_prompt: System instruction template.
        user_prompt: User instruction template.
        skills: List of required skill identifiers to embed.
        langfuse_slug: Optional custom remote prompt slug override.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: PromptKey
    description: str
    system_prompt: str = ""
    user_prompt: str = ""
    skills: list[str] = Field(default_factory=list)
    langfuse_slug: str | None = None

    @property
    def langfuse_name(self) -> str:
        """Deterministic remote Langfuse identifier (e.g. PromptKey.FLUID_PROSE -> cresmo-fluid-prose)."""
        return self.langfuse_slug or f"cresmo-{self.key.value.replace('_', '-')}"


class PromptCatalog(Mapping[PromptKey, PromptSpec]):
    """Immutable, bijectively validated catalog of prompt templates indexed by PromptKey."""

    def __init__(self, specs: dict[PromptKey, PromptSpec]) -> None:
        """Initialize catalog with validated mapping of PromptKey to PromptSpec."""
        self._specs: dict[PromptKey, PromptSpec] = dict(specs)
        self._by_langfuse_name: dict[str, PromptSpec] = {
            spec.langfuse_name: spec for spec in self._specs.values()
        }

    def __getitem__(self, key: PromptKey | str) -> PromptSpec:
        """Retrieve PromptSpec by PromptKey enum, key string, or langfuse_name.

        Args:
            key: PromptKey instance or string representation.

        Returns:
            Immutable PromptSpec instance.

        Raises:
            KeyError: If key is not found in the catalog.
        """
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


def load_prompt_catalog(path: Path | None = None) -> PromptCatalog:
    """Load and strictly validate the prompt catalog from disk or bundled package resource.

    Args:
        path: Optional explicit filesystem path to a JSON templates file.

    Returns:
        Immutable PromptCatalog instance bijectively verified against PromptKey.

    Raises:
        PromptCatalogError: If JSON fails schema parsing or fails 1:1 bijection with PromptKey.
    """
    raw_text: str | None = None
    if path is not None and path.exists():
        try:
            raw_text = path.read_text(encoding="utf-8")
            _ = json.loads(raw_text)
        except Exception:  # noqa: BLE001
            raw_text = None

    if raw_text is None:
        resource_traversable = importlib.resources.files(
            CresmoSettings.DEFAULT_PROMPTS_RESOURCE_PACKAGE
        ).joinpath(CresmoSettings.DEFAULT_PROMPTS_RESOURCE_NAME)
        raw_text = resource_traversable.read_text(encoding="utf-8")

    try:
        raw_data = json.loads(raw_text)
    except Exception as exc:
        raise PromptCatalogError(f"Failed to parse prompt JSON: {exc}") from exc

    if not isinstance(raw_data, dict):
        raise PromptCatalogError("Prompt catalog root must be a JSON object.")

    canonical_key_values = {k.value: k for k in PromptKey}
    json_keys = set(raw_data.keys())
    expected_keys = set(canonical_key_values.keys())

    missing_keys = expected_keys - json_keys
    if missing_keys:
        raise PromptCatalogError(
            f"Missing canonical PromptKey entries in catalog: {sorted(missing_keys)}"
        )

    extra_keys = json_keys - expected_keys
    if extra_keys:
        raise PromptCatalogError(f"Unrecognized prompt keys in catalog: {sorted(extra_keys)}")

    specs: dict[PromptKey, PromptSpec] = {}
    for key_str, entry in raw_data.items():
        if not isinstance(entry, dict):
            raise PromptCatalogError(f"Prompt entry '{key_str}' must be a JSON object.")
        enum_key = canonical_key_values[key_str]
        entry_copy = dict(entry)
        try:
            spec = PromptSpec(key=enum_key, **entry_copy)
            specs[enum_key] = spec
        except Exception as exc:
            raise PromptCatalogError(
                f"Failed validating PromptSpec for '{key_str}': {exc}"
            ) from exc

    return PromptCatalog(specs)


__all__ = [
    "PromptCatalog",
    "PromptCatalogError",
    "PromptSpec",
    "load_prompt_catalog",
]
