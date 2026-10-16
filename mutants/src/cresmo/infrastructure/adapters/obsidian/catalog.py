"""Channel semantic catalog and brain.csv tabular index management.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from cresmo.domain.value_objects import ChannelName, ContentId, RawIndexEntry
from cresmo.infrastructure.adapters.obsidian.utils import sanitize_filename


class ChannelCatalogHandler:
    """Handles channel-level semantic markdown catalog and global brain.csv indexing."""

    def __init__(self, raw_dir: Path, data_dir: Path) -> None:
        self.raw_dir = raw_dir
        self.data_dir = data_dir

    def get_channel_index_path(self, channel_name: ChannelName) -> Path:
        """Return absolute path to channel's _index_{channel_name}.md."""
        clean_channel = sanitize_filename(channel_name)
        return self.raw_dir / f"_index_{clean_channel}.md"

    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        """Retrieve set of ContentIds already indexed in the channel's _index_{channel_name}.md."""
        index_file = self.get_channel_index_path(channel_name)
        if not index_file.exists() or not index_file.is_file():
            return set()
        try:
            content = index_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return set()

        ids: set[ContentId] = set()
        for match in re.finditer(r"\*\*Video ID\*\*:\s*`([a-zA-Z0-9_-]{1,64})`", content):
            try:
                ids.add(ContentId(match.group(1)))
            except (ValueError, TypeError):
                continue
        for match in re.finditer(r"\[([a-zA-Z0-9_-]{1,64})\]\((https?://[^\)]+)\)", content):
            try:
                ids.add(ContentId(match.group(1)))
            except (ValueError, TypeError):
                continue
        return ids

    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/raw/<channel_name>/_canal.md atomically."""
        index_file = self.get_channel_index_path(channel_name)
        index_file.parent.mkdir(parents=True, exist_ok=True)

        header = ""
        if not index_file.exists() or index_file.stat().st_size == 0:
            header = f"# Canal: {channel_name}\n\n"

        block = entry.to_markdown_block() + "\n---\n\n"
        with open(index_file, "a", encoding="utf-8") as f:
            if header:
                f.write(header)
            f.write(block)
            f.flush()

    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/brain.csv atomically.

        Uses semicolon (`;`) delimiter and full field quoting (`QUOTE_ALL`)
        to prevent comma-separated key concepts from fragmenting into spurious columns.
        """
        csv_file = self.data_dir / "brain.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        write_header = not csv_file.exists() or csv_file.stat().st_size == 0
        with open(csv_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)
            if write_header:
                writer.writerow(
                    ["channel_category", "channel_name", "filename", "key_concept", "synthesis"]
                )
            writer.writerow(entry.to_csv_row())
            f.flush()
