"""Map of Content (MOC), WikiLink rewriting, and Master Document management.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from cresmo.domain.entities import MapOfContent
from cresmo.domain.value_objects import ChannelName, NoteTitle
from cresmo.infrastructure.adapters.obsidian.utils import (
    atomic_write,
    channel_to_slug,
    sanitize_filename,
)


class MocVaultHandler:
    """Handles Map of Content persistence, WikiLink link rewrites, and master documents."""

    def __init__(self, vault_dir: Path, mocs_dir: Path, master_dir: Path) -> None:
        self.vault_dir = vault_dir
        self.mocs_dir = mocs_dir
        self.master_dir = master_dir

    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist Map of Content in vault/MOCs/ atomically."""
        target_path = self.mocs_dir / f"{sanitize_filename(moc.title.value)}.md"

        frontmatter_dict = {
            "title": moc.title.value,
            "type": "moc",
            "theme": moc.theme,
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

        lines: list[str] = [
            "---",
            frontmatter_yaml.strip(),
            "---",
            "",
            f"# [[{moc.title.value}]]",
            "",
            moc.overview,
            "",
            "## Notas Associadas",
        ]
        for note_title in moc.associated_notes:
            lines.append(f"- [[{note_title.value}]]")
        lines.append("")

        atomic_write(target_path, "\n".join(lines).strip() + "\n")

    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        """Rewrite all inbound [[old_title]] links to [[new_title]] across all markdown files in vault/.

        Returns:
            Count of files updated.
        """
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0

        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated_count = 0

        for file_path in self.vault_dir.glob("**/*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError:
                continue

            def _repl(m: re.Match[str]) -> str:
                pipe_part = m.group(1) or ""
                return f"[[{new_val}{pipe_part}]]"

            new_content, count = pattern.subn(_repl, content)
            if count > 0:
                atomic_write(file_path, new_content)
                updated_count += 1

        return updated_count

    def save_master_document(
        self,
        channel_name: ChannelName,
        channel_category: str,
        part_number: int,
        content: str,
    ) -> Path:
        """Persist aggregated master document to master/<channel_category>/<channel_slug>_001.md."""
        cat_dir = self.master_dir / channel_to_slug(channel_category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        channel_slug = channel_to_slug(channel_name)
        filename = f"{channel_slug}_{part_number:03d}.md"
        target_path = cat_dir / filename
        atomic_write(target_path, content)
        return target_path

    def clear_master_documents_for_channel(
        self,
        channel_name: ChannelName,
        channel_category: str,
    ) -> None:
        """Delete previous master parts for channel before writing fresh sequential parts."""
        cat_dir = self.master_dir / channel_to_slug(channel_category)
        channel_slug = channel_to_slug(channel_name)
        if not cat_dir.exists() or not cat_dir.is_dir():
            return
        pattern = f"{channel_slug}_*.md"
        for p in cat_dir.glob(pattern):
            if p.is_file():
                p.unlink(missing_ok=True)
