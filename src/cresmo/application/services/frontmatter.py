"""Shared YAML frontmatter parsing and zero-read header inspection service.

Conforms to:
    - ADR-055: Zero-Read Metadata Extraction
    - ADR-077: Consolidated YAML Frontmatter Parsing
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)

_FRONTMATTER_BLOCK_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[str, dict[str, Any]]:
    """Split a Markdown document into `(body, metadata)` using safe YAML parsing."""
    if not text.lstrip().startswith("---"):
        return text, {}

    match = _FRONTMATTER_BLOCK_PATTERN.match(text.lstrip())
    if not match:
        return text, {}

    yaml_text, body = match.group(1), match.group(2)
    try:
        loaded = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        logger.debug("Invalid YAML frontmatter ignored: %s", exc)
        return body, {}

    if not isinstance(loaded, dict):
        return body, {}
    return body, dict(loaded)


def read_frontmatter_header(path: Path, max_lines: int = 50) -> dict[str, Any]:
    """Read at most ``max_lines`` from disk and parse YAML frontmatter without full file read."""
    try:
        header_lines: list[str] = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for idx, line in enumerate(handle):
                if idx >= max_lines:
                    break
                header_lines.append(line)
                if idx > 0 and line.strip() == "---":
                    break
    except OSError as exc:
        logger.debug("Unable to read frontmatter header from %s: %s", path, exc)
        return {}

    if not header_lines or header_lines[0].strip() != "---":
        return {}

    end_idx = next(
        (idx for idx in range(1, len(header_lines)) if header_lines[idx].strip() == "---"),
        None,
    )
    if end_idx is None:
        return {}

    yaml_text = "".join(header_lines[1:end_idx])
    try:
        loaded = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        logger.debug("Invalid YAML header in %s: %s", path, exc)
        fallback: dict[str, Any] = {}
        for raw_line in header_lines[1:end_idx]:
            if ":" in raw_line:
                key_part, val_part = raw_line.split(":", 1)
                clean_key = key_part.strip()
                clean_val = val_part.strip().strip("\"'")
                if clean_key and clean_val:
                    fallback[clean_key] = clean_val
        return fallback

    return dict(loaded) if isinstance(loaded, dict) else {}
