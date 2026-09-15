"""Unit tests for repository anchor and workspace root discovery."""

from __future__ import annotations

from pathlib import Path

from cresmo.infrastructure.paths import find_workspace_root


class TestWorkspaceRootDiscovery:
    """Hermetic unit tests for find_workspace_root anchor resolution."""

    def test_find_workspace_root_default_locates_pyproject_root(self) -> None:
        root = find_workspace_root()
        assert root.is_dir()
        assert (root / "pyproject.toml").exists()

    def test_find_workspace_root_resolves_pyproject_marker(self, tmp_path: Path) -> None:
        proj_dir = tmp_path / "project"
        proj_dir.mkdir()
        (proj_dir / "pyproject.toml").write_text("", encoding="utf-8")
        deep_dir = proj_dir / "src" / "pkg" / "sub"
        deep_dir.mkdir(parents=True)

        found = find_workspace_root(start_path=deep_dir)
        assert found == proj_dir

    def test_find_workspace_root_resolves_git_marker(self, tmp_path: Path) -> None:
        proj_dir = tmp_path / "git_project"
        proj_dir.mkdir()
        (proj_dir / ".git").mkdir()
        deep_dir = proj_dir / "a" / "b" / "c"
        deep_dir.mkdir(parents=True)

        found = find_workspace_root(start_path=deep_dir)
        assert found == proj_dir

    def test_find_workspace_root_fallback_when_no_markers_found(self, tmp_path: Path) -> None:
        # Create a deep path with at least 4 levels so parents[3] is valid
        deep_dir = tmp_path / "l1" / "l2" / "l3" / "l4"
        deep_dir.mkdir(parents=True)

        # In tmp_path without pyproject.toml or .git, should fallback to parents[3]
        expected_fallback = deep_dir.resolve().parents[3]
        found = find_workspace_root(start_path=deep_dir)
        assert found == expected_fallback
