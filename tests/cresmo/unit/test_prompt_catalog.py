"""Unit tests for Unified Prompt Catalog SSOT in JSON (ADR-052).

Verifies that prompts.json is the sole SSOT for prompt templates, descriptions,
and metadata, maintaining strict bijective validation with domain PromptKey.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cresmo.domain.value_objects import PromptKey
from cresmo.infrastructure.adapters.prompts.catalog import (
    PromptCatalog,
    PromptCatalogError,
    PromptSpec,
    load_prompt_catalog,
)


class TestPromptCatalog:
    """Test suite verifying PromptCatalog integrity, validation, and fail-fast guarantees."""

    def test_load_bundled_catalog_matches_all_prompt_keys(self) -> None:
        """Verify that the bundled prompts.json contains all canonical PromptKey members with 1:1 bijection."""
        catalog = load_prompt_catalog()
        assert isinstance(catalog, PromptCatalog)
        assert len(catalog) == len(PromptKey)
        for key in PromptKey:
            assert key in catalog
            spec = catalog[key]
            assert isinstance(spec, PromptSpec)
            assert spec.key == key
            assert len(spec.description.strip()) > 0
            assert spec.langfuse_name.startswith("cresmo-")

    def test_prompt_spec_langfuse_slug_override(self) -> None:
        """Verify that langfuse_slug override in prompts.json is respected."""
        catalog = load_prompt_catalog()
        reconcile_spec = catalog[PromptKey.RECONCILE_MOCS]
        assert reconcile_spec.langfuse_slug == "cresmo-mocs-reconciliation"
        assert reconcile_spec.langfuse_name == "cresmo-mocs-reconciliation"

    def test_prompt_spec_deterministic_langfuse_name(self) -> None:
        """Verify default deterministic naming for prompts without slug override."""
        catalog = load_prompt_catalog()
        fluid_spec = catalog[PromptKey.FLUID_PROSE]
        assert fluid_spec.langfuse_slug is None
        assert fluid_spec.langfuse_name == "cresmo-fluid-prose"

    def test_load_catalog_missing_key_raises_error(self, tmp_path: Path) -> None:
        """Verify that a catalog file missing a canonical PromptKey raises PromptCatalogError."""
        incomplete_data = {
            "fluid_prose": {
                "description": "Fluid prose test",
                "system_prompt": "sys",
                "user_prompt": "usr",
                "skills": [],
            }
        }
        test_file = tmp_path / "prompts_incomplete.json"
        test_file.write_text(json.dumps(incomplete_data), encoding="utf-8")

        with pytest.raises(PromptCatalogError, match="Missing canonical PromptKey"):
            load_prompt_catalog(test_file)

    def test_load_catalog_extra_key_raises_error(self, tmp_path: Path) -> None:
        """Verify that an unrecognized key in prompts.json raises PromptCatalogError."""
        catalog = load_prompt_catalog()
        raw_dict = {
            k.value: {
                "description": spec.description,
                "system_prompt": spec.system_prompt,
                "user_prompt": spec.user_prompt,
                "skills": spec.skills,
            }
            for k, spec in catalog.items()
        }
        raw_dict["unrecognized_extra_key"] = {
            "description": "Extra",
            "system_prompt": "sys",
            "user_prompt": "usr",
            "skills": [],
        }
        test_file = tmp_path / "prompts_extra.json"
        test_file.write_text(json.dumps(raw_dict), encoding="utf-8")

        with pytest.raises(PromptCatalogError, match="Unrecognized prompt keys"):
            load_prompt_catalog(test_file)

    def test_prompt_spec_forbids_extra_fields(self) -> None:
        """Verify that PromptSpec rejects unknown extra attributes (e.g. legacy 'task')."""
        with pytest.raises(ValidationError):
            PromptSpec(
                key=PromptKey.FLUID_PROSE,
                description="Test desc",
                system_prompt="sys",
                user_prompt="usr",
                skills=[],
                task="legacy task should fail",  # type: ignore[call-arg]
            )

    def test_catalog_lookup_by_key_and_string(self) -> None:
        """Verify lookup by PromptKey enum and raw string."""
        catalog = load_prompt_catalog()
        spec_enum = catalog[PromptKey.GAP_FILLER]
        spec_str = catalog["gap_filler"]
        assert spec_enum == spec_str

    def test_catalog_lookup_by_langfuse_name(self) -> None:
        """Verify reverse lookup by remote Langfuse name."""
        catalog = load_prompt_catalog()
        spec = catalog.get_by_langfuse_name("cresmo-mocs-reconciliation")
        assert spec is not None
        assert spec.key == PromptKey.RECONCILE_MOCS

        spec_fluid = catalog.get_by_langfuse_name("cresmo-fluid-prose")
        assert spec_fluid is not None
        assert spec_fluid.key == PromptKey.FLUID_PROSE

    def test_catalog_invalid_key_raises_key_error(self) -> None:
        """Verify that looking up a nonexistent key raises KeyError with exact diagnostic."""
        catalog = load_prompt_catalog()
        with pytest.raises(KeyError, match="Unknown prompt key: 'nonexistent'"):
            _ = catalog["nonexistent"]
