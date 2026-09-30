"""Application Use Case for incrementally indexing raw transcripts.

Extracts a concise key concept and a dense paratactic synthesis paragraph from raw transcripts,
appending the result incrementally to both the channel's semantic catalog (_canal.md) and
the global tabular index (brain.csv).

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-001: Modular Monolith Domain Integrity
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-019: SOTA KISS Nomenclature & Value Objects
"""

from __future__ import annotations

import logging
from pathlib import Path

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases.indexing.distiller import LLMTranscriptDistiller
from cresmo.domain.entities import RawTranscript
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    NoteTitle,
    RawIndexEntry,
    is_processable_transcript_file,
)

logger = logging.getLogger(__name__)


class IndexRawTranscriptsUseCase:
    """Orchestrates paratactic conceptual indexing of raw media transcripts.

    Conforms to:
        - SPEC-001: Core Knowledge Synthesis Specifications (Incremental Indexing)
        - ADR-001: Modular Monolith Domain Integrity
        - ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation

    Attributes:
        vault_port: Repository port for reading raw transcripts and appending indexes.
        llm_indexing_port: LLM transformation port for key concept and synthesis extraction.
        prompt_provider: Provider port supplying indexing prompt templates.
        max_chars: Maximum character limit from transcript body fed into LLM prompt (0 = full text).
        temperature: Generation sampling temperature.
        language: Target synthesis language.
        max_rewrites: Maximum corrective rewrite attempts if output violates formatting.
    """

    def __init__(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = "Português do Brasil",
        max_rewrites: int = 3,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
        )

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Trigger warmup on the underlying indexing LLM port (ADR-019: direct contract call)."""
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)

    def _extract_concepts(
        self,
        video_id: ContentId,
        title: str,
        text: str,
        channel_name: ChannelName,
    ) -> str:
        return self._distiller.extract_concepts(
            video_id=video_id,
            title=title,
            text=text,
            channel_name=channel_name,
        )

    def _extract_summary(
        self,
        video_id: ContentId,
        title: str,
        text: str,
        channel_name: ChannelName,
    ) -> str:
        return self._distiller.extract_summary(
            video_id=video_id,
            title=title,
            text=text,
            channel_name=channel_name,
        )

    def _extract_synthesis(
        self,
        video_id: ContentId,
        title: str,
        excerpt: str,
        summary: str,
        channel_name: ChannelName,
    ) -> str:
        return self._distiller.extract_synthesis(
            video_id=video_id,
            title=title,
            excerpt=excerpt,
            summary=summary,
            channel_name=channel_name,
        )

    def execute(
        self,
        transcript: RawTranscript,
        force: bool = False,
    ) -> RawIndexEntry | None:
        """Index a single raw transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-019 (execute() method convention unification).
        """
        video_id = transcript.content_id
        channel_name = transcript.channel_name

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = (
            transcript.title.value
            if isinstance(transcript.title, NoteTitle)
            else (transcript.title or video_id.value)
        )

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.body.strip()
        if self.max_chars and self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
            )
            summary = self._extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
            )
            synthesis = self._extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.source_url
            if transcript.source_url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = (
            transcript.channel_category.strip()
            if getattr(transcript, "channel_category", None)
            else ""
        )
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content_id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def index_single_transcript(
        self,
        transcript: RawTranscript,
        force: bool = False,
    ) -> RawIndexEntry | None:
        """Legacy alias delegating to execute() for backward compatibility."""
        return self.execute(transcript=transcript, force=force)

    def index_channel(self, channel_name: ChannelName, force: bool = False) -> list[RawIndexEntry]:
        """Index all raw markdown transcripts under a channel folder.

        Args:
            channel_name: ChannelName Value Object representing the channel.
            force: If True, forces re-indexing of previously indexed transcripts.

        Returns:
            List of newly created RawIndexEntry instances.
        """
        indexed_entries: list[RawIndexEntry] = []
        raw_dir = getattr(self.vault_port, "raw_dir", None)
        if raw_dir is None:
            return indexed_entries

        cn = ChannelName.from_string(channel_name)
        ch_dir = Path(raw_dir) / cn.value
        if not ch_dir.exists() or not ch_dir.is_dir():
            return indexed_entries

        for file_path in sorted(ch_dir.glob("*.md")):
            # Skip system indexes, artifacts, and hidden files
            if not is_processable_transcript_file(file_path):
                continue

            content_id = ContentId(file_path.stem)
            transcript = self.vault_port.get_raw_transcript(content_id)
            if transcript is not None:
                entry = self.execute(transcript, force=force)
                if entry is not None:
                    indexed_entries.append(entry)

        return indexed_entries

    def index_all_channels(self, force: bool = False) -> dict[str, list[RawIndexEntry]]:
        """Index all raw transcripts across all channels in the raw directory.

        Args:
            force: If True, forces re-indexing across all channels.

        Returns:
            Dictionary mapping channel names to lists of newly generated RawIndexEntry items.
        """
        self.warmup()
        results: dict[str, list[RawIndexEntry]] = {}
        raw_dir = getattr(self.vault_port, "raw_dir", None)
        if raw_dir is None:
            return results

        raw_path = Path(raw_dir)
        if not raw_path.exists():
            return results

        for sub_dir in sorted(raw_path.iterdir()):
            if sub_dir.is_dir() and not sub_dir.name.startswith((".", "_")):
                entries = self.index_channel(ChannelName(sub_dir.name), force=force)
                if entries:
                    results[sub_dir.name] = entries

        return results
