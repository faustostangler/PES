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

from cresmo.domain.entities import EnrichedCompendium, FluidTranscript, SourceTranscript
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    NoteTitle,
)
from cresmo.infrastructure.adapters.obsidian.utils import (
    _FRONTMATTER_PATTERN,
    ISO_DATE_COMPACT_LENGTH,
    atomic_write,
    sanitize_filename,
)


class TranscriptVaultHandler:
    """Handles filesystem persistence and retrieval of source transcripts, fluid transcripts, and enriched compendiums."""

    def __init__(
        self,
        raw_dir: Path,
        enriched_dir: Path,
        fluid_dir: Path | None = None,
    ) -> None:
        self.raw_dir = raw_dir
        self.enriched_dir = enriched_dir
        self.fluid_dir = fluid_dir or (raw_dir.parent / "fluid")

    def save_transcript(self, transcript: SourceTranscript) -> None:
        """Persist source transcript with canonical YAML frontmatter."""
        channel_dir = self.raw_dir / sanitize_filename(transcript.channel.name)
        file_path = channel_dir / f"{transcript.content.id.value}.md"

        description = transcript.provenance.description or ""
        indented_description = "\n".join("  " + line for line in description.splitlines())
        date_str = (
            transcript.provenance.publication_date.strftime("%Y%m%d")
            if transcript.provenance.publication_date
            else ""
        )
        raw_title = transcript.content.title or transcript.content.id.value
        escaped_title = raw_title.replace('"', '\\"')
        escaped_channel = transcript.channel.name.replace('"', '\\"')
        escaped_category = (transcript.channel.category or "uncategorized").replace('"', '\\"')
        channel_id_value = (
            transcript.channel.id.value if transcript.channel.id else "unknown_channel"
        )

        yaml_header = (
            f"---\n"
            f'video_title: "{escaped_title}"\n'
            f"video_id: {transcript.content.id.value}\n"
            f'channel_name: "{escaped_channel}"\n'
            f"channel_id: {channel_id_value}\n"
            f'channel_category: "{escaped_category}"\n'
            f"url: {transcript.provenance.url}\n"
            f"video_date: {date_str}\n"
            f"video_description: |\n"
            f"{indented_description}\n"
            f"---"
        )
        content = f"{yaml_header}\n\n{transcript.content.body}"
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
            channel = Channel(name=file_path.parent.name)
            provenance = MediaProvenance.create(
                url=f"file://{file_path.resolve()}",
                description="",
            )
            content = Content.create(
                id=content_id,
                title=file_path.stem,
                body=text,
            )
            return SourceTranscript(
                channel=channel,
                provenance=provenance,
                content=content,
            )

        frontmatter_text, body = match.groups()
        metadata = yaml.safe_load(frontmatter_text) or {}
        channel_name = str(
            metadata.get("channel_name") or metadata.get("channel") or file_path.parent.name
        )
        title = str(metadata.get("video_title") or metadata.get("title") or "")
        raw_channel_id = str(metadata.get("channel_id") or "")
        channel_category = str(metadata.get("channel_category") or metadata.get("domain") or "")
        source_url = str(metadata.get("url") or metadata.get("source_url") or "")
        raw_date = metadata.get("video_date") or metadata.get("upload_date")
        upload_date = None
        if raw_date:
            date_str = str(raw_date).strip()
            if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
                with contextlib.suppress(ValueError):
                    upload_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC).date()
        video_description = str(metadata.get("video_description") or "")

        channel = Channel(
            name=channel_name,
            id=ChannelId.from_string(raw_channel_id) if raw_channel_id else None,
            category=channel_category,
        )
        provenance = MediaProvenance.create(
            url=source_url,
            description=video_description,
            publication_date=upload_date,
        )
        content = Content.create(
            id=content_id,
            title=title,
            body=body.strip(),
        )
        return SourceTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )

    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory with canonical YAML frontmatter."""
        channel_dir = self.enriched_dir / sanitize_filename(compendium.channel_name)
        file_path = channel_dir / f"{compendium.content_id.value}.md"

        description = compendium.video_description or ""
        indented_description = "\n".join("  " + line for line in description.splitlines())
        escaped_title = compendium.title.value.replace('"', '\\"')
        escaped_channel = str(compendium.channel_name).replace('"', '\\"')
        escaped_category = (compendium.channel_category or "uncategorized").replace('"', '\\"')
        channel_id_value = compendium.channel_id or "unknown_channel"

        yaml_header = (
            f"---\n"
            f'video_title: "{escaped_title}"\n'
            f"video_id: {compendium.content_id.value}\n"
            f'channel_name: "{escaped_channel}"\n'
            f"channel_id: {channel_id_value}\n"
            f'channel_category: "{escaped_category}"\n'
            f"url: {compendium.source_url}\n"
            f"video_date: {compendium.video_date}\n"
            f"pass_count: {compendium.pass_count}\n"
            f"video_description: |\n"
            f"{indented_description}\n"
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

        frontmatter_text, raw_body = match.groups()
        metadata = yaml.safe_load(frontmatter_text) or {}

        # Split into main body and complementary info
        parts = raw_body.split("## Informações Complementares")
        body_part = parts[0].strip()
        complementary_part = parts[1].strip() if len(parts) > 1 else ""

        # Strip initial # title if present
        if body_part.startswith("# "):
            body_lines = body_part.splitlines()
            body_part = "\n".join(body_lines[1:]).strip()

        channel_name = str(
            metadata.get("channel_name") or metadata.get("channel") or file_path.parent.name
        )
        title = str(metadata.get("video_title") or metadata.get("title") or file_path.stem)
        raw_channel_id = str(metadata.get("channel_id") or "")
        channel_category = str(metadata.get("channel_category") or metadata.get("domain") or "")
        source_url = str(metadata.get("url") or metadata.get("source_url") or "")
        video_date = str(metadata.get("video_date") or "")
        video_description = str(metadata.get("video_description") or "")

        return EnrichedCompendium(
            content_id=content_id,
            channel_name=ChannelName(channel_name),
            title=NoteTitle(title),
            body=body_part,
            complementary_info=complementary_part,
            pass_count=int(metadata.get("pass_count", 1)),
            channel_id=ChannelId.from_string(raw_channel_id) if raw_channel_id else None,
            channel_category=channel_category,
            source_url=source_url,
            video_date=video_date,
            video_description=video_description,
        )

    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all enriched markdown file paths for a given channel."""
        channel_dir = self.enriched_dir / sanitize_filename(channel_name)
        if not channel_dir.exists() or not channel_dir.is_dir():
            return []
        return sorted(
            p for p in channel_dir.glob("*.md") if p.is_file() and not p.name.startswith(("_", "."))
        )

    def save_fluid_transcript(self, transcript: FluidTranscript) -> None:
        """Persist fluid transcript with canonical YAML frontmatter into fluid/ directory."""
        channel_dir = self.fluid_dir / sanitize_filename(transcript.channel.name)
        file_path = channel_dir / f"{transcript.content.id.value}.md"

        description = transcript.provenance.description or ""
        indented_description = "\n".join("  " + line for line in description.splitlines())
        date_str = (
            transcript.provenance.publication_date.strftime("%Y%m%d")
            if transcript.provenance.publication_date
            else ""
        )
        raw_title = transcript.content.title or transcript.content.id.value
        escaped_title = raw_title.replace('"', '\\"')
        escaped_channel = transcript.channel.name.replace('"', '\\"')
        escaped_category = (transcript.channel.category or "uncategorized").replace('"', '\\"')
        channel_id_value = (
            transcript.channel.id.value if transcript.channel.id else "unknown_channel"
        )

        yaml_header = (
            f"---\n"
            f'video_title: "{escaped_title}"\n'
            f"video_id: {transcript.content.id.value}\n"
            f'channel_name: "{escaped_channel}"\n'
            f"channel_id: {channel_id_value}\n"
            f'channel_category: "{escaped_category}"\n'
            f"url: {transcript.provenance.url}\n"
            f"video_date: {date_str}\n"
            f"video_description: |\n"
            f"{indented_description}\n"
            f"---"
        )
        content = f"{yaml_header}\n\n{transcript.content.body}"
        atomic_write(file_path, content)

    def get_fluid_transcript(self, content_id: ContentId) -> FluidTranscript | None:
        """Retrieve fluid transcript by searching fluid/ directory."""
        target_name = f"{content_id.value}.md"
        matched = list(self.fluid_dir.glob(f"**/{target_name}"))
        if not matched:
            return None

        file_path = matched[0]
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            channel = Channel(name=file_path.parent.name)
            provenance = MediaProvenance.create(
                url=f"file://{file_path.resolve()}",
                description="",
            )
            content = Content.create(
                id=content_id,
                title=file_path.stem,
                body=text,
            )
            return FluidTranscript(
                channel=channel,
                provenance=provenance,
                content=content,
            )

        frontmatter_text, body = match.groups()
        metadata = yaml.safe_load(frontmatter_text) or {}
        channel_name = str(
            metadata.get("channel_name") or metadata.get("channel") or file_path.parent.name
        )
        title = str(metadata.get("video_title") or metadata.get("title") or "")
        raw_channel_id = str(metadata.get("channel_id") or "")
        channel_category = str(metadata.get("channel_category") or metadata.get("domain") or "")
        source_url = str(metadata.get("url") or metadata.get("source_url") or "")
        raw_date = metadata.get("video_date") or metadata.get("upload_date")
        upload_date = None
        if raw_date:
            date_str = str(raw_date).strip()
            if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
                with contextlib.suppress(ValueError):
                    upload_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC).date()
        video_description = str(metadata.get("video_description") or "")

        channel = Channel(
            name=channel_name,
            id=ChannelId.from_string(raw_channel_id) if raw_channel_id else None,
            category=channel_category,
        )
        provenance = MediaProvenance.create(
            url=source_url,
            description=video_description,
            publication_date=upload_date,
        )
        content = Content.create(
            id=content_id,
            title=title,
            body=body.strip(),
        )
        return FluidTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
        )

    def get_fluid_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all fluid markdown file paths for a given channel."""
        channel_dir = self.fluid_dir / sanitize_filename(channel_name)
        if not channel_dir.exists() or not channel_dir.is_dir():
            return []
        return sorted(
            p for p in channel_dir.glob("*.md") if p.is_file() and not p.name.startswith(("_", "."))
        )
