"""Data models and accumulators for batch source discovery.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    SyncFilterCriteria,
)

DEFAULT_CHANNEL_MAX_VIDEOS: Final[int] = 50
DEFAULT_RAW_DATA_DIR: Final[Path] = Path("data/raw")
DEFAULT_PLAYLIST_MANIFEST_PATH: Final[Path] = Path("data/playlist.txt")


@dataclass(frozen=True)
class BatchSource:
    """Represents an atomic input item for batch processing.

    Attributes:
        kind: Source modality discriminator (SourceModality.FILE or SourceModality.URL).
        target: File path string or web URL.
        content_id: Strongly-typed canonical media identifier.
    """

    kind: SourceModality
    target: str
    content_id: ContentId | None = None


@dataclass(frozen=True)
class BatchDiscoveryQuery:
    """Encapsulates input parameters for batch source discovery.

    Conforms to ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering.
    """

    explicit_manifest: Path | None = None
    priority_texts_dir: Path | None = None
    playlist_priority_path: Path | None = None
    playlist_path: Path | None = None
    raw_dir: Path | None = None
    scan_raw: bool = True
    lookback_days: int | None = None
    channel_max_videos: int = DEFAULT_CHANNEL_MAX_VIDEOS
    discovery_workers: int | None = None
    enable_channel_crawler: bool = True
    filter_criteria: SyncFilterCriteria = field(default_factory=SyncFilterCriteria)
    queue_maxsize: int | None = None


@dataclass(frozen=True, slots=True)
class DiscoveryPaths:
    """Immutable filesystem path bundle injected into DiscoverBatchSourcesUseCase (ADR-074)."""

    raw_dir: Path = DEFAULT_RAW_DATA_DIR
    playlist_path: Path = DEFAULT_PLAYLIST_MANIFEST_PATH
    playlist_priority_path: Path | None = None
    priority_texts_dir: Path | None = None


def _resolve_content_id(
    target: str,
    raw_id: ContentId | str | None,
) -> ContentId | None:
    """Resolve ContentId from explicit ID candidate or target path/URL."""
    if raw_id is not None:
        if isinstance(raw_id, ContentId):
            return raw_id
        try:
            return ContentId.from_url_or_token(raw_id)
        except (ValueError, TypeError):
            pass

    for candidate in (target, Path(target).stem):
        try:
            return ContentId.from_url_or_token(candidate)
        except (ValueError, TypeError):
            continue
    return None


def _is_already_seen(
    seen_vids: set[ContentId | str],
    dedup_token: str,
    resolved_id: ContentId | None,
    raw_id: ContentId | str | None,
) -> bool:
    """Check if identifier or token has already been seen in accumulator."""
    if dedup_token in seen_vids:
        return True
    if resolved_id is not None and resolved_id in seen_vids:
        return True
    return raw_id is not None and str(raw_id) in seen_vids


def _record_seen_identifiers(
    seen_vids: set[ContentId | str],
    dedup_token: str,
    resolved_id: ContentId | None,
    raw_id: ContentId | str | None,
    target: str,
) -> None:
    """Record all aliases and tokens of a processed source into seen_vids."""
    seen_vids.add(dedup_token)
    if raw_id is not None:
        seen_vids.add(raw_id if not isinstance(raw_id, ContentId) else raw_id.value)
    if resolved_id is not None:
        seen_vids.add(resolved_id)
        seen_vids.add(resolved_id.value)
    stem = Path(target).stem
    if stem:
        seen_vids.add(stem)


class _BatchSourceAccumulator:
    """Encapsulates thread-safe deduplication and ordered accumulation of batch sources."""

    def __init__(self, on_source_added: Callable[[BatchSource], None] | None = None) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[ContentId | str] = set()
        self.on_source_added = on_source_added
        self._lock = threading.Lock()

    def mark_seen(self, *identifiers: str) -> None:
        """Register raw file or token identifiers as seen in a thread-safe manner."""
        with self._lock:
            for identifier in identifiers:
                if identifier:
                    self.seen_vids.add(identifier)

    def add_source(
        self,
        kind: SourceModality,
        target: str,
        content_id: ContentId | None = None,
    ) -> BatchSource | None:
        """Append a source and register its identifier for deduplication."""
        with self._lock:
            resolved_id = _resolve_content_id(target, content_id)
            dedup_token: str = (
                resolved_id.value
                if resolved_id is not None
                else (str(content_id) if content_id is not None else Path(target).stem)
            )

            if _is_already_seen(self.seen_vids, dedup_token, resolved_id, content_id):
                return None

            _record_seen_identifiers(self.seen_vids, dedup_token, resolved_id, content_id, target)

            batch_source = BatchSource(kind=kind, target=target, content_id=resolved_id)
            self.sources.append(batch_source)
            callback = self.on_source_added

        if callback is not None:
            callback(batch_source)
        return batch_source

    def has_seen(self, identifier: str | ContentId) -> bool:
        """Check if an identifier (video ID, stem, or ContentId) was already registered."""
        with self._lock:
            if identifier in self.seen_vids:
                return True
            if isinstance(identifier, ContentId):
                return identifier.value in self.seen_vids
            try:
                content_id = ContentId.from_url_or_token(identifier)
                if content_id in self.seen_vids or content_id.value in self.seen_vids:
                    return True
            except (ValueError, TypeError):
                content_id = None
            stem = Path(identifier).stem
            return stem in self.seen_vids if stem else False
