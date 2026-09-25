"""Use case for consolidating enriched compendiums into master RAG files per channel.

Aggregates markdown compendiums in ascending chronological order (oldest first)
up to the configured word limit without splitting files in the middle. Generates
sequentially numbered master documents per channel category.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import re

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import ChannelName, ContentId, MasterDocumentResult
from cresmo.infrastructure.config import CresmoSettings

CHUNK_SEPARATOR: str = "\n\n---\n\n"
_DATE_PATTERN = re.compile(r'video_date:\s*["\']?(\d{4,8})["\']?')
_CATEGORY_PATTERN = re.compile(r'channel_category:\s*["\']?([^"\'\n]+)["\']?')
_VIDEO_ID_PATTERN = re.compile(r'video_id:\s*["\']?([a-zA-Z0-9_-]+)["\']?')


def count_words(text: str) -> int:
    """Count the total number of whitespace-delimited words in a string.

    Args:
        text: Source text string.

    Returns:
        Total word count integer.
    """
    return len(text.split())


def parse_metadata_from_content(
    content: str, channel_name: ChannelName | str, fallback_stem: str
) -> tuple[int, str, ContentId]:
    """Extract (video_date, channel_category, video_id) from YAML frontmatter.

    Args:
        content: Raw markdown text with YAML frontmatter.
        channel_name: Channel identifier for fallback categorization.
        fallback_stem: File stem fallback if video_id is absent.

    Returns:
        Tuple of (date_integer, category_string, video_id ContentId).
    """
    # 1. Parse video_date
    date_match = _DATE_PATTERN.search(content)
    sort_date = 99999999
    if date_match:
        try:
            sort_date = int(date_match.group(1))
        except ValueError:
            pass

    # 2. Parse channel_category
    category_match = _CATEGORY_PATTERN.search(content)
    if category_match and category_match.group(1).strip():
        category = category_match.group(1).strip()
    else:
        category, _ = classify_channel(str(channel_name))

    # 3. Parse video_id
    video_id_match = _VIDEO_ID_PATTERN.search(content)
    raw_video_id = (
        video_id_match.group(1).strip()
        if video_id_match and video_id_match.group(1).strip()
        else fallback_stem
    )
    video_id = ContentId.from_string(raw_video_id)

    return sort_date, category, video_id


class ConcatMasterUseCase:
    """Consolidates enriched compendiums into sequential master documents for RAG.

    Conforms to:
    - SPEC-001: Core Knowledge Synthesis Specifications
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-019: Primary execute() method unification and ChannelName Value Object
    """

    def __init__(
        self,
        vault_port: VaultRepositoryPort,
        settings: CresmoSettings | None = None,
    ) -> None:
        """Initialize use case with vault port and operational settings.

        Args:
            vault_port: Port providing file read and master document write capabilities.
            settings: Configuration settings holding target word caps.
        """
        self.vault_port = vault_port
        self.settings = settings if settings is not None else CresmoSettings()

    def execute(
        self,
        channel_name: ChannelName | str,
        max_words: int | None = None,
    ) -> list[MasterDocumentResult]:
        """Aggregate all enriched files for a specific channel into sequential master files (Primary Entrypoint).

        Args:
            channel_name: Name of the channel whose enriched documents to aggregate.
            max_words: Optional word limit override (defaults to settings.concat_max_words).

        Returns:
            List of MasterDocumentResult value objects representing created parts.
        """
        effective_max = max_words if max_words is not None else self.settings.concat_max_words
        files = self.vault_port.get_enriched_files_for_channel(channel_name)
        if not files:
            return []

        # Read and inspect each file's date, category, and words
        docs: list[tuple[int, str, str, ContentId, int]] = []
        resolved_category: str | None = None

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if not content:
                continue

            sort_date, category, video_id = parse_metadata_from_content(
                content=content,
                channel_name=channel_name,
                fallback_stem=file_path.stem,
            )
            if resolved_category is None:
                resolved_category = category

            word_count = count_words(content)
            docs.append((sort_date, file_path.name, content, video_id, word_count))

        if not docs:
            return []

        # Chronological sort: oldest first (ascending by sort_date, then file name)
        docs.sort(key=lambda doc_tuple: (doc_tuple[0], doc_tuple[1]))

        channel_category = resolved_category or classify_channel(channel_name)[0]

        # Group documents into parts without ever splitting a single file
        parts: list[list[tuple[str, ContentId, int]]] = []
        current_part: list[tuple[str, ContentId, int]] = []
        current_part_words = 0

        for _, _, content, video_id, doc_words in docs:
            if current_part_words + doc_words > effective_max and current_part:
                parts.append(current_part)
                current_part = [(content, video_id, doc_words)]
                current_part_words = doc_words
            else:
                current_part.append((content, video_id, doc_words))
                current_part_words += doc_words

        if current_part:
            parts.append(current_part)

        # Clear prior master parts for this channel
        self.vault_port.clear_master_documents_for_channel(
            channel_name=channel_name,
            channel_category=channel_category,
        )

        results: list[MasterDocumentResult] = []
        for part_num, part_docs in enumerate(parts, start=1):
            merged_content = CHUNK_SEPARATOR.join(doc[0] for doc in part_docs) + "\n"
            total_words = count_words(merged_content)
            video_ids: tuple[ContentId, ...] = tuple(doc[1] for doc in part_docs)

            out_path = self.vault_port.save_master_document(
                channel_name=channel_name,
                channel_category=channel_category,
                part_number=part_num,
                content=merged_content,
            )

            results.append(
                MasterDocumentResult(
                    channel_name=channel_name,
                    channel_category=channel_category,
                    output_path=out_path,
                    part_number=part_num,
                    word_count=total_words,
                    document_count=len(part_docs),
                    video_ids=video_ids,
                )
            )

        return results

    def execute_for_channel(
        self,
        channel_name: ChannelName | str,
        max_words: int | None = None,
    ) -> list[MasterDocumentResult]:
        """Legacy alias delegating to execute() for backward compatibility."""
        return self.execute(channel_name=channel_name, max_words=max_words)

    def execute_all(
        self,
        max_words: int | None = None,
    ) -> dict[str, list[MasterDocumentResult]]:
        """Discover all channel subdirectories in enriched/ and aggregate each channel.

        Returns:
            Mapping of channel names to their generated MasterDocumentResult lists.
        """
        enriched_root = self.settings.enriched_dir
        if not enriched_root.exists() or not enriched_root.is_dir():
            return {}

        channel_dirs = sorted(
            d.name
            for d in enriched_root.iterdir()
            if d.is_dir() and not d.name.startswith((".", "_"))
        )
        all_results: dict[str, list[MasterDocumentResult]] = {}

        for channel_name in channel_dirs:
            channel_results = self.execute_for_channel(
                channel_name=channel_name, max_words=max_words
            )
            if channel_results:
                all_results[channel_name] = channel_results

        return all_results
