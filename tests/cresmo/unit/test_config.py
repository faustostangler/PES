"""Hermetic unit tests for CresmoSettings and Anchor Marker resolution."""

from __future__ import annotations

from pathlib import Path

from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.paths import find_workspace_root


class TestAnchorMarkerResolution:
    """Validate resilient Anchor Marker workspace root discovery."""

    def test_find_workspace_root_discovers_pyproject_toml(self) -> None:
        root = find_workspace_root()
        assert (root / "pyproject.toml").exists()
        assert root.is_dir()

    def test_find_workspace_root_from_nested_directory(self) -> None:
        nested_path = Path(__file__).resolve()
        root = find_workspace_root(nested_path)
        assert (root / "pyproject.toml").exists()

    def test_find_workspace_root_with_simulated_synthetic_anchor(self, tmp_path: Path) -> None:
        repo_dir = tmp_path / "synthetic_repo"
        sub_dir = repo_dir / "a" / "b" / "c" / "d" / "e"
        sub_dir.mkdir(parents=True)
        (repo_dir / "pyproject.toml").touch()

        discovered = find_workspace_root(sub_dir)
        assert discovered == repo_dir

    def test_find_workspace_root_fallback_when_no_anchor(self, tmp_path: Path) -> None:
        leaf_dir = tmp_path / "l1" / "l2" / "l3" / "l4"
        leaf_dir.mkdir(parents=True)
        # Without any pyproject.toml or .git, falls back to parents[3]
        fallback = find_workspace_root(leaf_dir)
        assert fallback == leaf_dir.resolve().parents[3]


class TestCresmoSettings:
    """Validate settings defaults and derived property invariants."""

    def test_default_paths_anchor_to_workspace(self) -> None:
        settings = CresmoSettings()
        assert settings.data_dir.name == "data"
        assert settings.vault_dir.name == "vault"
        assert settings.raw_dir == settings.data_dir / "raw"
        assert settings.enriched_dir == settings.data_dir / "enriched"
        assert settings.index_path == settings.vault_dir / "_index.json"
        assert settings.sqlite_ledger_path == settings.data_dir / "cresmo_ledger.db"
        assert settings.browser_cookies == "firefox"
        assert settings.auto_extract_cookies is True
        assert settings.enable_channel_crawler is True
        assert settings.require_auth_cookies is False
