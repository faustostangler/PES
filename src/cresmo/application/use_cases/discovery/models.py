"""Data models and accumulators for batch source discovery.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    SyncFilterCriteria,
)


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

    def __post_init__(self) -> None:
        if isinstance(self.kind, str) and not isinstance(self.kind, SourceModality):
            try:
                modality = SourceModality(self.kind.strip().lower())
            except ValueError as exc:
                raise ValueError(
                    f"Invalid BatchSource modality '{self.kind}'. Expected SourceModality.FILE or SourceModality.URL."
                ) from exc
            object.__setattr__(self, "kind", modality)
        if self.content_id is not None and not isinstance(self.content_id, ContentId):
            object.__setattr__(self, "content_id", ContentId.from_string(self.content_id))

    @property
    def vid(self) -> str | None:
        """Backward-compatible accessor for the string representation of content_id."""
        if self.content_id is None:
            return None
        return self.content_id.value if isinstance(self.content_id, ContentId) else self.content_id

    @property
    def display_name(self) -> str:
        """Human-readable representation for CLI logs."""
        if self.kind is SourceModality.FILE:
            return Path(self.target).name
        return self.target


@dataclass(frozen=True)
class BatchDiscoveryQuery:
    """Encapsulates input parameters for batch source discovery.

    Conforms to ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering.
    """

    explicit_manifest: Path | None = None
    manifest_path: Path | None = None
    priority_texts_dir: Path | None = None
    playlist_priority_path: Path | None = None
    playlist_path: Path | None = None
    raw_dir: Path | None = None
    scan_raw: bool = True
    lookback_days: int | None = None
    channel_max_videos: int = 50
    discovery_workers: int | None = None
    enable_channel_crawler: bool = True
    filter_criteria: SyncFilterCriteria = None  # type: ignore[assignment]
    queue_maxsize: int | None = None

    def __post_init__(self) -> None:
        # Ensure filter_criteria is always a valid SyncFilterCriteria (never None)
        if self.filter_criteria is None:
            object.__setattr__(self, "filter_criteria", SyncFilterCriteria())


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

    def add_source(
        self,
        kind: SourceModality,
        target: str,
        vid: ContentId | None = None,
        content_id: ContentId | None = None,
    ) -> BatchSource | None:
        """Append a source and register its identifier for deduplication."""
        with self._lock:
            raw_id = content_id if content_id is not None else vid
            resolved_id = _resolve_content_id(target, raw_id)
            dedup_token: str = (
                resolved_id.value
                if resolved_id is not None
                else (str(raw_id) if raw_id is not None else Path(target).stem)
            )

            if _is_already_seen(self.seen_vids, dedup_token, resolved_id, raw_id):
                return None

            _record_seen_identifiers(self.seen_vids, dedup_token, resolved_id, raw_id, target)

            src = BatchSource(kind=kind, target=target, content_id=resolved_id)
            self.sources.append(src)
            cb = self.on_source_added

        if cb is not None:
            cb(src)
        return src

    def register_identifier(self, target_str: str | ContentId) -> None:
        """Register video ID or path stem into the deduplication set."""
        with self._lock:
            if isinstance(target_str, ContentId):
                self.seen_vids.add(target_str)
                self.seen_vids.add(target_str.value)
                return
            self.seen_vids.add(target_str)
            try:
                cid = ContentId.from_url_or_token(target_str)
                self.seen_vids.add(cid)
                self.seen_vids.add(cid.value)
            except (ValueError, TypeError):
                cid = None
            stem = Path(target_str).stem
            if stem:
                self.seen_vids.add(stem)

    def has_seen(self, identifier: str | ContentId) -> bool:
        """Check if an identifier (video ID, stem, or ContentId) was already registered."""
        with self._lock:
            if identifier in self.seen_vids:
                return True
            if isinstance(identifier, ContentId):
                return identifier.value in self.seen_vids
            try:
                cid = ContentId.from_url_or_token(identifier)
                if cid in self.seen_vids or cid.value in self.seen_vids:
                    return True
            except (ValueError, TypeError):
                cid = None
            stem = Path(identifier).stem
            return stem in self.seen_vids if stem else False
