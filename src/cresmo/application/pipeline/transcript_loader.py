"""File-based transcript loader and metadata parser for the synthesis pipeline."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from cresmo.application.ports.storage import VaultRepositoryPort

from cresmo.domain.entities import SourceTranscript
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    is_processable_transcript_file,
)

logger = logging.getLogger(__name__)

_MIN_CONTENT_ID_LENGTH: int = 8
_MAX_CONTENT_ID_LENGTH: int = 64
_FRONTMATTER_REGEX = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$")


def _derive_content_id(stem: str, raw_body: str) -> ContentId:
    """Derive deterministic and compliant ContentId string."""
    clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
    if _MIN_CONTENT_ID_LENGTH <= len(clean_stem) <= _MAX_CONTENT_ID_LENGTH:
        content_id_str = clean_stem
    else:
        prefix = clean_stem[:24] if clean_stem else "text"
        suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
        content_id_str = f"{prefix}_{suffix}"
    return ContentId(value=content_id_str)


def _parse_frontmatter_dict(fm_text: str, filename: str) -> dict[str, Any]:
    """Parse YAML text safely with logging fallback for invalid syntax."""
    try:
        return yaml.safe_load(fm_text) or {}
    except (yaml.YAMLError, ValueError, TypeError, KeyError) as exc:
        logger.debug(
            "[pipeline] Malformed YAML frontmatter in '%s', retaining defaults: %s",
            filename,
            exc,
        )
        return {}


def _extract_frontmatter(raw_body: str, filename: str) -> tuple[str, dict[str, Any]]:
    """Extract body text and frontmatter dictionary if YAML header exists."""
    if not raw_body.startswith("---"):
        return raw_body, {}
    fm_match = _FRONTMATTER_REGEX.match(raw_body)
    if not fm_match:
        return raw_body, {}
    fm_text, parsed_body = fm_match.groups()
    meta = _parse_frontmatter_dict(fm_text, filename)
    return parsed_body.strip(), meta


def _resolve_metadata(
    meta: dict[str, Any],
    file_path: Path,
    stem: str,
) -> tuple[str, ChannelName, ChannelId | None, str, str, str]:
    """Resolve entity attributes combining explicit frontmatter and path conventions."""
    title = str(
        meta.get("video_title")
        or meta.get("title")
        or stem.replace("_", " ").replace("-", " ").title()
    )
    channel_raw = str(
        meta.get("channel_name")
        or meta.get("channel")
        or (file_path.parent.name if file_path.parent.name else "text")
    )
    channel_name = ChannelName(channel_raw)

    raw_cid = meta.get("channel_id")
    channel_id_obj: ChannelId | None = (
        ChannelId.from_string(str(raw_cid)) if raw_cid else ChannelId("priority_text")
    )
    category = str(
        meta.get("channel_category") or meta.get("domain") or classify_channel(channel_name)[0]
    )
    source_url = str(meta.get("url") or f"file://{file_path.resolve()}")
    video_description = str(meta.get("video_description") or "")

    return title, channel_name, channel_id_obj, category, source_url, video_description


def load_transcript_from_file(file_path: Path) -> SourceTranscript:
    """Parse and construct SourceTranscript domain entity from a local file.

    Handles YAML frontmatter metadata overrides and enforces security invariants:
    - Rejects internal Cresmo system files and index databases
    - Verifies file exists and contains non-empty body
    - Derives deterministic and compliant ContentId

    Args:
        file_path: Path to the transcript markdown or text file.

    Returns:
        Validated SourceTranscript domain aggregate root.

    Raises:
        CresmoDomainError: If file is missing, empty, or a reserved system artifact.
    """
    if not is_processable_transcript_file(file_path):
        raise CresmoDomainError(
            f"File '{file_path.name}' is an internal Cresmo artifact or system index "
            "and cannot be processed as a transcript."
        )

    if not file_path.is_file():
        raise CresmoDomainError(f"Priority text file not found: {file_path}")

    raw_body = file_path.read_text(encoding="utf-8").strip()
    if not raw_body:
        raise CresmoDomainError(f"Priority text file is empty: {file_path}")

    content_id = _derive_content_id(file_path.stem, raw_body)
    body, meta = _extract_frontmatter(raw_body, file_path.name)
    title, ch_name, ch_id, category, source_url, description = _resolve_metadata(
        meta, file_path, file_path.stem
    )

    return SourceTranscript(
        content_id=content_id,
        channel_name=ch_name,
        body=body,
        title=title,
        source_url=source_url,
        channel_id=ch_id,
        channel_category=category,
        video_description=description,
    )


def load_manifest_urls(manifest_path: Path) -> list[str]:
    """Parse a manifest file containing URLs into a list of non-empty target strings."""
    if not manifest_path.is_file():
        raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    return [
        line_str for line in lines if (line_str := line.strip()) and not line_str.startswith("#")
    ]


def is_subpath(target_path: Path, parent_dir: Path | None) -> bool:
    """Determine whether a target file path is located within a parent directory."""
    if parent_dir is None:
        return False
    try:
        return target_path.resolve().is_relative_to(parent_dir.resolve())
    except (ValueError, RuntimeError):
        return False


def ensure_raw_saved_in_vault(
    vault_port: VaultRepositoryPort,
    file_path: Path,
    raw: SourceTranscript,
    raw_dir: Path | None = None,
) -> None:
    """Persist raw transcript in vault if not already located inside the target raw directory."""
    vault_raw_dir = getattr(vault_port, "raw_dir", None)
    if is_subpath(file_path, raw_dir) or is_subpath(file_path, vault_raw_dir):
        return
    vault_port.save_raw_transcript(raw)
