"""Raw transcript and enriched compendium serialization for Obsidian vault.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
from pathlib import Path

import yaml

from cresmo.domain.entities import EnrichedCompendium, SourceTranscript
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    NoteTitle,
)
from cresmo.infrastructure.adapters.obsidian.utils import (
    _FRONTMATTER_PATTERN,
    ISO_DATE_COMPACT_LENGTH,
    atomic_write,
    sanitize_filename,
)


class TranscriptVaultHandler:
    """Handles filesystem persistence and retrieval of source transcripts and enriched compendiums."""

    def __init__(self, raw_dir: Path, enriched_dir: Path) -> None:
        self.raw_dir = raw_dir
        self.enriched_dir = enriched_dir

    def save_transcript(self, transcript: SourceTranscript) -> None:
        """Persist source transcript with canonical YAML frontmatter."""
        channel_dir = self.raw_dir / sanitize_filename(transcript.channel_name)
        file_path = channel_dir / f"{transcript.content_id.value}.md"

        desc = transcript.video_description or ""
        desc_indented = "\n".join("  " + l for l in desc.splitlines())
        date_str = transcript.upload_date.strftime("%Y%m%d") if transcript.upload_date else ""
        raw_title = (
            transcript.title.value
            if isinstance(transcript.title, NoteTitle)
            else (transcript.title or transcript.content_id.value)
        )
        escaped_title = raw_title.replace('"', '\\"')
        escaped_channel = str(transcript.channel_name).replace('"', '\\"')
        escaped_category = (transcript.channel_category or "uncategorized").replace('"', '\\"')
        channel_id_val = transcript.channel_id or "unknown_channel"

        yaml_header = (
            f"---\n"
            f'video_title: "{escaped_title}"\n'
            f"video_id: {transcript.content_id.value}\n"
            f'channel_name: "{escaped_channel}"\n'
            f"channel_id: {channel_id_val}\n"
            f'channel_category: "{escaped_category}"\n'
            f"url: {transcript.source_url}\n"
            f"video_date: {date_str}\n"
            f"video_description: |\n"
            f"{desc_indented}\n"
            f"---"
        )
        content = f"{yaml_header}\n\n{transcript.body}"
        atomic_write(file_path, content)

    def get_raw_transcript(self, content_id: ContentId) -> SourceTranscript | None:
        """Retrieve source transcript by searching raw/ directory."""
        target_name = f"{content_id.value}.md"
        matched = list(self.raw_dir.glob(f"**/{target_name}"))
        if not matched:
            return None

        file_path = matched[0]
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return SourceTranscript(
                content_id=content_id,
                channel_name=ChannelName(file_path.parent.name),
                body=text,
            )

        fm_text, body = match.groups()
        meta = yaml.safe_load(fm_text) or {}
        ch_name = str(meta.get("channel_name") or meta.get("channel") or file_path.parent.name)
        title = str(meta.get("video_title") or meta.get("title") or "")
        ch_id = str(meta.get("channel_id") or "")
        ch_cat = str(meta.get("channel_category") or meta.get("domain") or "")
        url = str(meta.get("url") or meta.get("source_url") or "")
        raw_date = meta.get("video_date") or meta.get("upload_date")
        upload_date = None
        if raw_date:
            date_str = str(raw_date).strip()
            if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
                with contextlib.suppress(ValueError):
                    upload_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC).date()
        desc = str(meta.get("video_description") or "")

        return SourceTranscript(
            content_id=content_id,
            channel_name=ChannelName(ch_name),
            body=body.strip(),
            title=title,
            source_url=url,
            upload_date=upload_date,
            channel_id=ChannelId.from_string(ch_id) if ch_id else None,
            channel_category=ch_cat,
            video_description=desc,
        )

    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory with canonical YAML frontmatter."""
        channel_dir = self.enriched_dir / sanitize_filename(compendium.channel_name)
        file_path = channel_dir / f"{compendium.content_id.value}.md"

        desc = compendium.video_description or ""
        desc_indented = "\n".join("  " + l for l in desc.splitlines())
        escaped_title = compendium.title.value.replace('"', '\\"')
        escaped_channel = str(compendium.channel_name).replace('"', '\\"')
        escaped_category = (compendium.channel_category or "uncategorized").replace('"', '\\"')
        channel_id_val = compendium.channel_id or "unknown_channel"

        yaml_header = (
            f"---\n"
            f'video_title: "{escaped_title}"\n'
            f"video_id: {compendium.content_id.value}\n"
            f'channel_name: "{escaped_channel}"\n'
            f"channel_id: {channel_id_val}\n"
            f'channel_category: "{escaped_category}"\n'
            f"url: {compendium.source_url}\n"
            f"video_date: {compendium.video_date}\n"
            f"pass_count: {compendium.pass_count}\n"
            f"video_description: |\n"
            f"{desc_indented}\n"
            f"---"
        )
        body_text = (
            f"# {compendium.title.value}\n\n"
            f"{compendium.body}\n\n"
            f"## Informações Complementares\n\n"
            f"{compendium.complementary_info}"
        )
        content = f"{yaml_header}\n\n{body_text}"
        atomic_write(file_path, content)

    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID."""
        target_name = f"{content_id.value}.md"
        matched = list(self.enriched_dir.glob(f"**/{target_name}"))
        if not matched:
            return None

        file_path = matched[0]
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return None

        fm_text, raw_body = match.groups()
        meta = yaml.safe_load(fm_text) or {}

        # Split into main body and complementary info
        parts = raw_body.split("## Informações Complementares")
        body_part = parts[0].strip()
        comp_part = parts[1].strip() if len(parts) > 1 else ""

        # Strip initial # title if present
        if body_part.startswith("# "):
            body_lines = body_part.splitlines()
            body_part = "\n".join(body_lines[1:]).strip()

        ch_name = str(meta.get("channel_name") or meta.get("channel") or file_path.parent.name)
        title = str(meta.get("video_title") or meta.get("title") or file_path.stem)
        ch_id = str(meta.get("channel_id") or "")
        ch_cat = str(meta.get("channel_category") or meta.get("domain") or "")
        url = str(meta.get("url") or meta.get("source_url") or "")
        v_date = str(meta.get("video_date") or "")
        desc = str(meta.get("video_description") or "")

        return EnrichedCompendium(
            content_id=content_id,
            channel_name=ChannelName(ch_name),
            title=NoteTitle(title),
            body=body_part,
            complementary_info=comp_part,
            pass_count=int(meta.get("pass_count", 1)),
            channel_id=ChannelId.from_string(ch_id) if ch_id else None,
            channel_category=ch_cat,
            source_url=url,
            video_date=v_date,
            video_description=desc,
        )

    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all enriched markdown file paths for a given channel."""
        ch_dir = self.enriched_dir / sanitize_filename(channel_name)
        if not ch_dir.exists() or not ch_dir.is_dir():
            return []
        return sorted(
            p for p in ch_dir.glob("*.md") if p.is_file() and not p.name.startswith(("_", "."))
        )
