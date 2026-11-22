"""Hermetic unit tests for SkillDocumentLoader and YAML frontmatter stripping (ADR-071)."""

from __future__ import annotations

from pathlib import Path

from cresmo.infrastructure.adapters.prompts.skill_loader import (
    SkillDocumentLoader,
    strip_yaml_frontmatter,
)


class TestSkillDocumentLoader:
    """Unit tests covering SKILL.md resolution, frontmatter stripping, caching, and skill_block."""

    def test_strip_yaml_frontmatter_removes_leading_metadata_only(self) -> None:
        raw = "---\nname: demo-skill\ndescription: demo\n---\n\n# Body Heading\nContent."
        assert strip_yaml_frontmatter(raw) == "# Body Heading\nContent."
        plain = "# Plain Heading\n---\nHorizontal rule."
        assert strip_yaml_frontmatter(plain) == plain

    def test_read_skill_caches_and_handles_missing_skill(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "demo-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\nname: demo\n---\nFirst version.", encoding="utf-8")

        loader = SkillDocumentLoader(skills_dir=tmp_path)
        assert loader.skills_dir == tmp_path
        assert loader.read_skill("demo-skill") == "First version."

        # Modify on disk to verify in-memory cache hit
        skill_file.write_text("Second version.", encoding="utf-8")
        assert loader.read_skill("demo-skill") == "First version."
        assert loader.read_skill("nonexistent-skill") == ""

    def test_build_skill_replacements_separates_inline_and_skill_block(
        self, tmp_path: Path
    ) -> None:
        for name, body in (
            ("cresmo-style-guide", "# Style Guide"),
            ("cresmo-gap-filler", "# Gap Filler"),
        ):
            d = tmp_path / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n{body}", encoding="utf-8")

        loader = SkillDocumentLoader(skills_dir=tmp_path)
        replacements = loader.build_skill_replacements(
            skills=("cresmo-style-guide", "cresmo-gap-filler"),
            templates=("Guide: {{cresmo-style-guide}}\nOther: {{skill_block}}",),
        )
        assert replacements["cresmo-style-guide"] == "# Style Guide"
        assert replacements["cresmo-gap-filler"] == "# Gap Filler"
        assert "cresmo-gap-filler:\n# Gap Filler" in replacements["skill_block"]
        assert "cresmo-style-guide" not in replacements["skill_block"]
