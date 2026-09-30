"""Batch Source Discovery Use Case for the Cresmo Knowledge Engine.

Orchestrates raw transcript ingestion, manifest parsing, concurrent channel resolution,
and lookback feed discovery via a streaming Producer-Consumer pattern.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-001: Modular Monolith Domain Integrity
- ADR-003: PES Production Architecture
- ADR-026: Clean Code Anti-Patterns & Code Smell Governance (Modularization)
"""

from cresmo.application.use_cases.discovery import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
    _BatchSourceAccumulator,
    extract_raw_file_metadata,
    is_channel_or_playlist_feed,
    load_transcript_files,
    matches_category_target,
    matches_channel_target,
    matches_video_target,
    read_manifest_lines,
)

# Backwards compatibility aliases
_matches_channel_target = matches_channel_target
_matches_category_target = matches_category_target
_matches_video_target = matches_video_target

__all__ = [
    "BatchDiscoveryQuery",
    "BatchSource",
    "DiscoverBatchSourcesUseCase",
    "_BatchSourceAccumulator",
    "_matches_category_target",
    "_matches_channel_target",
    "_matches_video_target",
    "extract_raw_file_metadata",
    "is_channel_or_playlist_feed",
    "load_transcript_files",
    "matches_category_target",
    "matches_channel_target",
    "matches_video_target",
    "read_manifest_lines",
]
