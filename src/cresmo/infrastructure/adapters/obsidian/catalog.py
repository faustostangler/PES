"""Channel semantic catalog and brain.csv tabular index management.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Final

from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import ChannelName, ContentId, RawIndexEntry
from cresmo.infrastructure.adapters.obsidian.utils import sanitize_filename

_CHANNEL_INDEX_FILE_PREFIX: Final[str] = "_index_"
_MARKDOWN_EXT: Final[str] = ".md"
_UTF8_ENCODING: Final[str] = "utf-8"
_READ_ERRORS_IGNORE: Final[str] = "ignore"
_VIDEO_ID_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\*\*Video ID\*\*:\s*`([a-zA-Z0-9_-]{1,64})`"
)
_MARKDOWN_SECTION_SEPARATOR: Final[str] = "\n---\n\n"
_BRAIN_CSV_FILENAME: Final[str] = "brain.csv"
_CSV_DELIMITER: Final[str] = ";"
_BRAIN_CSV_HEADERS: Final[tuple[str, ...]] = (
    "channel_category",
    "channel_name",
    "filename",
    "key_concept",
    "synthesis",
)


class ChannelCatalogHandler:
    """Handles channel-level semantic markdown catalog and global brain.csv indexing."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir).resolve()
        self.raw_dir = self.data_dir / StageName.RAW.value

    def _get_channel_index_path(self, channel_name: ChannelName) -> Path:
        """Return absolute path to channel's _index_{channel_name}.md."""
        clean_channel = sanitize_filename(channel_name)
        return self.raw_dir / f"{_CHANNEL_INDEX_FILE_PREFIX}{clean_channel}{_MARKDOWN_EXT}"

    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        """Retrieve set of ContentIds already indexed in the channel's _index_{channel_name}.md."""
        index_file = self._get_channel_index_path(channel_name)
        if not index_file.exists() or not index_file.is_file():
            return set()
        try:
            content = index_file.read_text(encoding=_UTF8_ENCODING, errors=_READ_ERRORS_IGNORE)
        except OSError:
            return set()

        ids: set[ContentId] = set()
        for match in _VIDEO_ID_PATTERN.finditer(content):
            try:
                ids.add(ContentId(match.group(1)))
            except (ValueError, TypeError):
                continue
        return ids

    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/raw/_index_{channel_name}.md atomically."""
        index_file = self._get_channel_index_path(channel_name)
        index_file.parent.mkdir(parents=True, exist_ok=True)

        header = ""
        if not index_file.exists() or index_file.stat().st_size == 0:
            header = f"# Canal: {channel_name}\n\n"

        block = entry.to_markdown_block() + _MARKDOWN_SECTION_SEPARATOR
        with open(index_file, "a", encoding=_UTF8_ENCODING) as f:
            if header:
                f.write(header)
            f.write(block)
            f.flush()

    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/brain.csv atomically.

        Uses semicolon (`;`) delimiter and full field quoting (`QUOTE_ALL`)
        to prevent comma-separated key concepts from fragmenting into spurious columns.
        """
        csv_file = self.data_dir / _BRAIN_CSV_FILENAME
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        write_header = not csv_file.exists() or csv_file.stat().st_size == 0
        with open(csv_file, "a", encoding=_UTF8_ENCODING, newline="") as f:
            writer = csv.writer(f, delimiter=_CSV_DELIMITER, quoting=csv.QUOTE_ALL)
            if write_header:
                writer.writerow(list(_BRAIN_CSV_HEADERS))
            writer.writerow(entry.to_csv_row())
            f.flush()
