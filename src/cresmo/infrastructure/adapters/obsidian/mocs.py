"""Map of Content (MOC), WikiLink rewriting, and Master Document management.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

import yaml

from cresmo.domain.entities import MapOfContent
from cresmo.domain.value_objects import ChannelName, NoteTitle
from cresmo.infrastructure.adapters.obsidian.utils import (
    atomic_write,
    channel_to_slug,
    sanitize_filename,
)

_MARKDOWN_EXT: Final[str] = ".md"
_MARKDOWN_GLOB_ALL: Final[str] = "**/*.md"
_UTF8_ENCODING: Final[str] = "utf-8"
_FRONTMATTER_FENCE: Final[str] = "---"
_MOC_TYPE_VALUE: Final[str] = "moc"
_MOC_NOTES_HEADING: Final[str] = "## Notas Associadas"
_KEY_TITLE: Final[str] = "title"
_KEY_TYPE: Final[str] = "type"
_KEY_THEME: Final[str] = "theme"


class MocVaultHandler:
    """Handles Map of Content persistence, WikiLink link rewrites, and master documents."""

    def __init__(self, vault_dir: Path, mocs_dir: Path, master_dir: Path) -> None:
        self.vault_dir = vault_dir
        self.mocs_dir = mocs_dir
        self.master_dir = master_dir

    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist Map of Content in vault/MOCs/ atomically."""
        target_path = self.mocs_dir / f"{sanitize_filename(moc.title.value)}{_MARKDOWN_EXT}"

        frontmatter_dict = {
            _KEY_TITLE: moc.title.value,
            _KEY_TYPE: _MOC_TYPE_VALUE,
            _KEY_THEME: moc.theme,
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

        lines: list[str] = [
            _FRONTMATTER_FENCE,
            frontmatter_yaml.strip(),
            _FRONTMATTER_FENCE,
            "",
            f"# [[{moc.title.value}]]",
            "",
            moc.overview,
            "",
            _MOC_NOTES_HEADING,
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

        for file_path in self.vault_dir.glob(_MARKDOWN_GLOB_ALL):
            try:
                content = file_path.read_text(encoding=_UTF8_ENCODING)
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
        filename = f"{channel_slug}_{part_number:03d}{_MARKDOWN_EXT}"
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
        pattern = f"{channel_slug}_*{_MARKDOWN_EXT}"
        for p in cat_dir.glob(pattern):
            if p.is_file():
                p.unlink(missing_ok=True)
