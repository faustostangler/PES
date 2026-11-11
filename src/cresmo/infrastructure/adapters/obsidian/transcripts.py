"""Raw transcript and enriched compendium serialization for Obsidian vault.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import contextlib
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from cresmo.domain.entities import (
    StageTranscript,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
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
        data_dir: Path | None = None,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.enriched_dir = Path(enriched_dir)
        self.data_dir = Path(data_dir).resolve() if data_dir is not None else self.raw_dir.parent
        self.fluid_dir = Path(fluid_dir) if fluid_dir is not None else (self.data_dir / "fluid")

    def resolve_stage_dir(self, stage: str | StageName) -> Path:
        """Resolve dynamic stage directory following canonical data/{stage} structure (ADR-058)."""
        stage_key = stage.value if hasattr(stage, "value") else str(stage).strip()
        if stage_key == "raw":
            return self.raw_dir
        if stage_key == "fluid":
            return self.fluid_dir
        if stage_key == "enriched":
            return self.enriched_dir
        return self.data_dir / stage_key

    def _format_stage_frontmatter(
        self, transcript: StageTranscript, stage_name: str = ""
    ) -> str:
        """Format canonical monomorphic YAML frontmatter for any stage transcript (ADR-058)."""
        description = transcript.provenance.description or ""
        indented_description = "\n".join("  " + line for line in description.splitlines())
        date_str = (
            transcript.provenance.publication_date.strftime("%Y%m%d")
            if transcript.provenance.publication_date
            else str(transcript.metadata.get("video_date") or "")
        )
        raw_title = transcript.content.title or transcript.content.id.value
        escaped_title = raw_title.replace('"', '\\"')
        escaped_channel = transcript.channel.name.replace('"', '\\"')
        escaped_category = (transcript.channel.category or "uncategorized").replace('"', '\\"')
        channel_id_value = (
            transcript.channel.id.value if transcript.channel.id else "unknown_channel"
        )

        lines = [
            "---",
            f'video_title: "{escaped_title}"',
            f"video_id: {transcript.content.id.value}",
            f'channel_name: "{escaped_channel}"',
            f"channel_id: {channel_id_value}",
            f'channel_category: "{escaped_category}"',
            f"url: {transcript.provenance.url}",
            f"video_date: {date_str}",
        ]
        if transcript.pass_count is not None:
            lines.append(f"pass_count: {transcript.pass_count}")
        lines.extend([
            "video_description: |",
            f"{indented_description}",
            "---",
        ])
        return "\n".join(lines)

    def save_stage_transcript(
        self,
        stage: str | StageName,
        transcript: StageTranscript,
        *,
        target_dir: Path | None = None,
    ) -> None:
        """Persist stage transcript envelope atomically with canonical YAML frontmatter (ADR-058)."""
        stage_key = stage.value if hasattr(stage, "value") else str(stage).strip()
        base_dir = target_dir or self.resolve_stage_dir(stage_key)
        channel_dir = base_dir / sanitize_filename(transcript.channel.name)
        file_path = channel_dir / f"{transcript.content.id.value}.md"

        yaml_header = self._format_stage_frontmatter(transcript, stage_key)
        raw_title = transcript.content.title or "Untitled Compendium"
        body_payload = transcript.content.text.strip()
        if (
            stage_key in ("gap_filler", "enriched") or target_dir == self.enriched_dir
        ) and not body_payload.startswith("# "):
            body_text = f"# {raw_title}\n\n{body_payload}"
        else:
            body_text = body_payload

        content = f"{yaml_header}\n\n{body_text}"
        atomic_write(file_path, content)

    def _deserialize_stage_transcript(
        self, file_path: Path, content_id: ContentId, stage_key: str = ""
    ) -> StageTranscript | None:
        """Internal helper to deserialize a markdown stage file into a monomorphic StageTranscript."""
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            if stage_key in ("gap_filler", "enriched"):
                return None
            channel = Channel(name=file_path.parent.name)
            provenance = MediaProvenance.create(
                url=f"file://{file_path.resolve()}",
                description="",
            )
            content = Content.create(
                id=content_id,
                title=file_path.stem,
                text=text,
            )
            return StageTranscript(
                channel=channel,
                provenance=provenance,
                content=content,
            )

        frontmatter_text, raw_body = match.groups()
        metadata = yaml.safe_load(frontmatter_text) or {}

        channel_name = str(
            metadata.get("channel_name") or metadata.get("channel") or file_path.parent.name
        )
        raw_title_meta = metadata.get("video_title") or metadata.get("title")
        if raw_title_meta:
            title = str(raw_title_meta)
        elif stage_key in ("gap_filler", "enriched"):
            title = file_path.stem
        else:
            title = ""
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
            else:
                try:
                    upload_date = date.fromisoformat(date_str[:10])
                except (ValueError, TypeError):
                    upload_date = None
        video_description = str(metadata.get("video_description") or "")

        raw_pass_count = metadata.get("pass_count")
        pass_count: int | None = None
        if raw_pass_count is not None:
            with contextlib.suppress(ValueError, TypeError):
                pass_count = int(raw_pass_count)

        channel = Channel(
            name=ChannelName(channel_name),
            id=ChannelId.from_string(raw_channel_id) if raw_channel_id else None,
            category=channel_category,
        )
        provenance = MediaProvenance.create(
            url=source_url,
            description=video_description,
            publication_date=upload_date,
        )

        body_payload = raw_body.strip()
        if "### Extra Info" in body_payload and body_payload.startswith("# "):
            body_lines = body_payload.splitlines()
            body_payload = "\n".join(body_lines[1:]).strip()

        content = Content.create(
            id=content_id,
            title=title,
            text=body_payload,
            session_id=f"{channel.id.value if channel.id else channel.name}:{content_id.value}",
        )
        return StageTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
            pass_count=pass_count,
            metadata={"video_date": str(raw_date)} if raw_date else {},
        )

    def get_stage_transcript(
        self, stage: str | StageName, content_id: ContentId
    ) -> StageTranscript | None:
        """Retrieve persisted stage transcript envelope by stage name and content ID (ADR-058)."""
        stage_key = stage.value if hasattr(stage, "value") else str(stage).strip()
        stage_dir = self.resolve_stage_dir(stage_key)
        target_name = f"{content_id.value}.md"

        matched = list(stage_dir.glob(f"**/{target_name}")) if stage_dir.exists() else []
        if not matched:
            if stage_key in ("fluid_prose", "fluid") and self.fluid_dir.exists() and self.fluid_dir != stage_dir:
                matched = list(self.fluid_dir.glob(f"**/{target_name}"))
            elif stage_key in ("gap_filler", "enriched") and self.enriched_dir.exists() and self.enriched_dir != stage_dir:
                matched = list(self.enriched_dir.glob(f"**/{target_name}"))
            elif stage_key == "raw" and self.raw_dir.exists() and self.raw_dir != stage_dir:
                matched = list(self.raw_dir.glob(f"**/{target_name}"))

        if not matched:
            return None

        file_path = matched[0]
        return self._deserialize_stage_transcript(file_path, content_id, stage_key=stage_key)

    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all enriched markdown file paths for a given channel."""
        ch_name = sanitize_filename(channel_name)
        candidates: set[Path] = set()
        for d in (self.resolve_stage_dir("gap_filler"), self.enriched_dir):
            ch_dir = d / ch_name
            if ch_dir.exists() and ch_dir.is_dir():
                candidates.update(
                    p for p in ch_dir.glob("*.md") if p.is_file() and not p.name.startswith(("_", "."))
                )
        return sorted(candidates)

    def get_fluid_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all fluid markdown file paths for a given channel."""
        ch_name = sanitize_filename(channel_name)
        candidates: set[Path] = set()
        for d in (self.resolve_stage_dir("fluid_prose"), self.fluid_dir):
            ch_dir = d / ch_name
            if ch_dir.exists() and ch_dir.is_dir():
                candidates.update(
                    p for p in ch_dir.glob("*.md") if p.is_file() and not p.name.startswith(("_", "."))
                )
        return sorted(candidates)
