"""Discovery sub-package for Cresmo batch media discovery.

Re-exports core models, services, and orchestrator use cases.
"""

from cresmo.application.use_cases.discovery.channel_crawler import ChannelFeedCrawlerService
from cresmo.application.use_cases.discovery.discover_batch_sources import (
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.discovery.lake_scanner import LakeScannerService
from cresmo.application.use_cases.discovery.manifests import (
    extract_raw_file_metadata,
    is_channel_or_playlist_feed,
    load_transcript_files,
    matches_category_target,
    matches_channel_target,
    matches_video_target,
    read_manifest_lines,
)
from cresmo.application.use_cases.discovery.models import (
    BatchDiscoveryQuery,
    BatchSource,
    _BatchSourceAccumulator,
)

__all__ = [
    "BatchDiscoveryQuery",
    "BatchSource",
    "ChannelFeedCrawlerService",
    "DiscoverBatchSourcesUseCase",
    "LakeScannerService",
    "_BatchSourceAccumulator",
    "extract_raw_file_metadata",
    "is_channel_or_playlist_feed",
    "load_transcript_files",
    "matches_category_target",
    "matches_channel_target",
    "matches_video_target",
    "read_manifest_lines",
]
