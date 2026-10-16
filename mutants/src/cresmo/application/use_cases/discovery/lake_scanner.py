"""Local lake scanning and seed classification service for batch source discovery.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

from pathlib import Path

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
    BatchSource,
    _BatchSourceAccumulator,
)
from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
    normalize_to_uploads_playlist_url,
)


def _matches_channel_and_category(criteria: SyncFilterCriteria, chan_target: str) -> bool:
    """Check if channel target satisfies both channel target and category target criteria."""
    if criteria.is_empty():
        return True
    return matches_channel_target(criteria, chan_target) and matches_category_target(
        criteria, chan_target
    )


def _matches_video_entry(
    criteria: SyncFilterCriteria,
    cid: ContentId | None,
    url: str,
    local_chan: str | None,
) -> bool:
    """Evaluate whether a video entry satisfies video, channel, and category filter criteria."""
    if criteria.is_empty():
        return True
    if criteria.video_ids and not matches_video_target(criteria, cid or url, url):
        return False
    if criteria.channels and (not local_chan or not matches_channel_target(criteria, local_chan)):
        return False
    return not (
        criteria.categories
        and (not local_chan or not matches_category_target(criteria, local_chan))
    )


def _is_unresolved_video_candidate(
    criteria: SyncFilterCriteria,
    cid: ContentId | None,
    url: str,
) -> bool:
    """Check if a video without a resolved local channel matches isolated video ID criteria."""
    if criteria.is_empty():
        return True
    return bool(
        criteria.video_ids
        and matches_video_target(criteria, cid or url, url)
        and not criteria.channels
        and not criteria.categories
    )


class LakeScannerService:
    """Handles scanning of local filesystem lake, priority paths, and seed classification."""

    @staticmethod
    def collect_priority_texts(
        priority_texts_dir: Path | None,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> list[str]:
        """Collect local priority text/markdown files that bypass audio transcription."""
        criteria = filter_criteria or SyncFilterCriteria()
        priority_channels: list[str] = []
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            if not is_processable_transcript_file(pf):
                continue
            meta = extract_raw_file_metadata(pf)
            raw_chan = meta.get("channel") or meta.get("channel_id")
            vid = meta.get("video_id") or pf.stem

            matches = True
            if not criteria.is_empty():
                if criteria.video_ids and not matches_video_target(criteria, vid):
                    matches = False
                if criteria.channels and (
                    not raw_chan or not matches_channel_target(criteria, raw_chan)
                ):
                    matches = False
                if criteria.categories and (
                    not raw_chan or not matches_category_target(criteria, raw_chan)
                ):
                    matches = False

            if matches:
                resolved_pf = str(pf.resolve())
                acc.add_source(kind=SourceModality.FILE, target=resolved_pf)

            if raw_chan and (
                criteria.is_empty()
                or (
                    matches_channel_target(criteria, raw_chan)
                    and matches_category_target(criteria, raw_chan)
                )
            ):
                norm_chan = normalize_to_uploads_playlist_url(raw_chan)
                if norm_chan not in priority_channels:
                    priority_channels.append(norm_chan)
        return priority_channels

    @staticmethod
    def collect_priority_urls(
        playlist_priority_path: Path | None,
        local_video_channel_map: dict[str, str],
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> tuple[list[str], list[str]]:
        """Collect priority URLs scheduled for immediate processing."""
        criteria = filter_criteria or SyncFilterCriteria()
        priority_channels: list[str] = []
        unresolved_videos: list[str] = []
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            if is_channel_or_playlist_feed(pu):
                if _matches_channel_and_category(criteria, pu):
                    norm_chan = normalize_to_uploads_playlist_url(pu)
                    if norm_chan not in priority_channels:
                        priority_channels.append(norm_chan)
                continue

            cid = ContentId.extract_from_text(pu)
            vid_str = cid.value if cid else None
            local_chan = local_video_channel_map.get(vid_str) if vid_str else None

            if _matches_video_entry(criteria, cid, pu, local_chan) and not (
                cid and acc.has_seen(cid)
            ):
                acc.add_source(kind=SourceModality.URL, target=pu, content_id=cid)

            if local_chan:
                if _matches_channel_and_category(criteria, local_chan):
                    norm_local = normalize_to_uploads_playlist_url(local_chan)
                    if norm_local not in priority_channels:
                        priority_channels.append(norm_local)
            elif pu not in unresolved_videos and _is_unresolved_video_candidate(criteria, cid, pu):
                unresolved_videos.append(pu)
        return priority_channels, unresolved_videos

    @staticmethod
    def scan_raw_lake(
        raw_dir: Path | None,
        scan_raw: bool,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        criteria = filter_criteria or SyncFilterCriteria()
        local_video_to_channel: dict[str, str] = {}
        if raw_dir is None or not raw_dir.is_dir():
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            if not is_processable_transcript_file(rf):
                continue
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem

            already_seen = acc.has_seen(stem) or acc.has_seen(canonical_vid)

            # Record in accumulator so discovered feeds know these already exist in local lake
            acc.seen_vids.add(stem)
            acc.seen_vids.add(canonical_vid)

            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not already_seen:
                matches = True
                if not criteria.is_empty():
                    if criteria.video_ids and not matches_video_target(criteria, canonical_vid):
                        matches = False
                    if criteria.channels and (
                        not chan_url or not matches_channel_target(criteria, chan_url)
                    ):
                        matches = False
                    if criteria.categories and (
                        not chan_url or not matches_category_target(criteria, chan_url)
                    ):
                        matches = False
                if matches:
                    resolved_rf = str(rf.resolve())
                    if not any(s.target == resolved_rf for s in acc.sources):
                        acc.sources.append(
                            BatchSource(kind=SourceModality.FILE, target=resolved_rf)
                        )

        return local_video_to_channel

    @staticmethod
    def classify_seeds(
        playlist_path: Path | None,
        local_video_channel_map: dict[str, str],
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups.

        ADR-012: Applies channel filter criteria and returns channels sorted alphabetically.
        """
        criteria = filter_criteria or SyncFilterCriteria()
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_video_channel_map.values():
            if c_url not in probed_channels and _matches_channel_and_category(criteria, c_url):
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels and _matches_channel_and_category(criteria, mu):
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
                continue

            cid = ContentId.extract_from_text(mu)
            vid_str = cid.value if cid else None
            local_chan = local_video_channel_map.get(vid_str) if vid_str else None

            if _matches_video_entry(criteria, cid, mu, local_chan) and not (
                cid and acc.has_seen(cid)
            ):
                acc.add_source(kind=SourceModality.URL, target=mu, content_id=cid)

            if local_chan:
                if local_chan not in probed_channels and _matches_channel_and_category(
                    criteria, local_chan
                ):
                    probed_channels.add(local_chan)
                    channels_to_probe.append(local_chan)
            elif mu not in remote_videos and _is_unresolved_video_candidate(criteria, cid, mu):
                remote_videos.append(mu)

        # ADR-012: Enforce strict alphabetical ordering of channels before feed probing
        channels_to_probe = sorted(channels_to_probe, key=lambda c: c.lower())

        return channels_to_probe, remote_videos, probed_channels
