"""Raw transcript and enriched compendium serialization for Obsidian vault.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import contextlib
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Final

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

_EXPANDED_STAGES: frozenset[str] = frozenset(
    {
        StageName.GAP_FILLER,
        StageName.LONG_EXPANDER,
        StageName.WIDE_EXPANDER,
    }
)
_COMPACT_DATE_FORMAT: Final[str] = "%Y%m%d"
_ISO_DATE_PREFIX_LENGTH: Final[int] = 10
_DEFAULT_CATEGORY_UNCATEGORIZED: Final[str] = "uncategorized"
_DEFAULT_CHANNEL_ID_UNKNOWN: Final[str] = "unknown_channel"
_DEFAULT_COMPENDIUM_TITLE: Final[str] = "Untitled Compendium"
_EXTRA_INFO_MARKER: Final[str] = "### Extra Info"
_H1_PREFIX: Final[str] = "# "
_FRONTMATTER_FENCE: Final[str] = "---"
_FRONTMATTER_DESC_INDENT: Final[str] = "  "
_FILE_URI_PREFIX: Final[str] = "file://"
_MARKDOWN_EXT: Final[str] = ".md"
_MARKDOWN_GLOB_ALL: Final[str] = "*.md"
_INTERNAL_FILE_PREFIXES: Final[tuple[str, ...]] = ("_", ".")
_UTF8_ENCODING: Final[str] = "utf-8"
_SESSION_ID_SEPARATOR: Final[str] = ":"
_METADATA_KEY_VIDEO_DATE: Final[str] = "video_date"
_KEY_CHANNEL_NAME: Final[str] = "channel_name"
_KEY_VIDEO_TITLE: Final[str] = "video_title"
_KEY_CHANNEL_ID: Final[str] = "channel_id"
_KEY_CHANNEL_CATEGORY: Final[str] = "channel_category"
_KEY_URL: Final[str] = "url"
_KEY_VIDEO_DESCRIPTION: Final[str] = "video_description"
_KEY_PASS_COUNT: Final[str] = "pass_count"


class TranscriptVaultHandler:
    """Handles filesystem persistence and retrieval of staged pipeline transcripts."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir).resolve()

    def resolve_stage_dir(self, stage: str | StageName) -> Path:
        """Resolve dynamic stage directory following canonical data/{stage} structure (ADR-058)."""
        stage_key = stage.value if isinstance(stage, StageName) else str(stage).strip()
        return self.data_dir / stage_key

    def _format_stage_frontmatter(self, transcript: StageTranscript) -> str:
        """Format canonical monomorphic YAML frontmatter for any stage transcript (ADR-058)."""
        description = transcript.provenance.description or ""
        indented_description = "\n".join(
            _FRONTMATTER_DESC_INDENT + line for line in description.splitlines()
        )
        date_str = (
            transcript.provenance.publication_date.strftime(_COMPACT_DATE_FORMAT)
            if transcript.provenance.publication_date
            else str(transcript.metadata.get(_METADATA_KEY_VIDEO_DATE) or "")
        )
        raw_title = transcript.content.title or transcript.content.id.value
        escaped_title = raw_title.replace('"', '\\"')
        escaped_channel = transcript.channel.name.replace('"', '\\"')
        escaped_category = (
            transcript.channel.category or _DEFAULT_CATEGORY_UNCATEGORIZED
        ).replace('"', '\\"')
        channel_id_value = (
            transcript.channel.id.value if transcript.channel.id else _DEFAULT_CHANNEL_ID_UNKNOWN
        )

        lines = [
            _FRONTMATTER_FENCE,
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
        lines.extend(
            [
                "video_description: |",
                f"{indented_description}",
                _FRONTMATTER_FENCE,
            ]
        )
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
        file_path = channel_dir / f"{transcript.content.id.value}{_MARKDOWN_EXT}"

        yaml_header = self._format_stage_frontmatter(transcript)
        raw_title = transcript.content.title or _DEFAULT_COMPENDIUM_TITLE
        body_payload = transcript.content.text.strip()
        if stage_key in _EXPANDED_STAGES and not body_payload.startswith(_H1_PREFIX):
            body_text = f"{_H1_PREFIX}{raw_title}\n\n{body_payload}"
        else:
            body_text = body_payload

        content = f"{yaml_header}\n\n{body_text}"
        atomic_write(file_path, content)

    def _deserialize_stage_transcript(
        self, file_path: Path, content_id: ContentId, stage_key: str = ""
    ) -> StageTranscript | None:
        """Internal helper to deserialize a markdown stage file into a monomorphic StageTranscript."""
        text = file_path.read_text(encoding=_UTF8_ENCODING)
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            if stage_key in _EXPANDED_STAGES:
                return None
            channel = Channel(name=file_path.parent.name)
            provenance = MediaProvenance.create(
                url=f"{_FILE_URI_PREFIX}{file_path.resolve()}",
                description="",
            )
            content = Content(
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

        channel_name = str(metadata.get(_KEY_CHANNEL_NAME) or file_path.parent.name)
        raw_title_meta = metadata.get(_KEY_VIDEO_TITLE)
        if raw_title_meta:
            title = str(raw_title_meta)
        elif stage_key in _EXPANDED_STAGES:
            title = file_path.stem
        else:
            title = ""
        raw_channel_id = str(metadata.get(_KEY_CHANNEL_ID) or "")
        channel_category = str(metadata.get(_KEY_CHANNEL_CATEGORY) or "")
        source_url = str(metadata.get(_KEY_URL) or "")
        raw_date = metadata.get(_METADATA_KEY_VIDEO_DATE)
        upload_date = None
        if raw_date:
            date_str = str(raw_date).strip()
            if len(date_str) == ISO_DATE_COMPACT_LENGTH and date_str.isdigit():
                with contextlib.suppress(ValueError):
                    upload_date = (
                        datetime.strptime(date_str, _COMPACT_DATE_FORMAT)
                        .replace(tzinfo=UTC)
                        .date()
                    )
            else:
                try:
                    upload_date = date.fromisoformat(date_str[:_ISO_DATE_PREFIX_LENGTH])
                except (ValueError, TypeError):
                    upload_date = None
        video_description = str(metadata.get(_KEY_VIDEO_DESCRIPTION) or "")

        raw_pass_count = metadata.get(_KEY_PASS_COUNT)
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
        if _EXTRA_INFO_MARKER in body_payload and body_payload.startswith(_H1_PREFIX):
            body_lines = body_payload.splitlines()
            body_payload = "\n".join(body_lines[1:]).strip()

        content = Content(
            id=content_id,
            title=title,
            text=body_payload,
            session_id=(
                f"{channel.id.value if channel.id else channel.name}"
                f"{_SESSION_ID_SEPARATOR}{content_id.value}"
            ),
        )
        return StageTranscript(
            channel=channel,
            provenance=provenance,
            content=content,
            pass_count=pass_count,
            metadata={_METADATA_KEY_VIDEO_DATE: str(raw_date)} if raw_date else {},
        )

    def get_stage_transcript(
        self, stage: str | StageName, content_id: ContentId
    ) -> StageTranscript | None:
        """Retrieve persisted stage transcript envelope by stage name and content ID (ADR-058)."""
        stage_key = stage.value if hasattr(stage, "value") else str(stage).strip()
        stage_dir = self.resolve_stage_dir(stage_key)
        target_name = f"{content_id.value}{_MARKDOWN_EXT}"

        matched = list(stage_dir.glob(f"**/{target_name}")) if stage_dir.exists() else []
        if not matched:
            return None

        file_path = matched[0]
        return self._deserialize_stage_transcript(file_path, content_id, stage_key=stage_key)

    def get_stage_files_for_channel(
        self, stage_name: str | StageName, channel_name: ChannelName
    ) -> list[Path]:
        """Retrieve sorted list of all markdown file paths for a stage and channel."""
        stage_key = stage_name.value if isinstance(stage_name, StageName) else str(stage_name)
        ch_name = sanitize_filename(channel_name)
        ch_dir = self.resolve_stage_dir(stage_key) / ch_name
        if not ch_dir.exists() or not ch_dir.is_dir():
            return []
        return sorted(
            p
            for p in ch_dir.glob(_MARKDOWN_GLOB_ALL)
            if p.is_file() and not p.name.startswith(_INTERNAL_FILE_PREFIXES)
        )
