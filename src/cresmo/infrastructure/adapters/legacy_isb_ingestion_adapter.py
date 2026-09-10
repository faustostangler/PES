"""Anti-Corruption Layer (ACL) Adapter for Legacy isb.ai Media Ingestion.

Encapsulates legacy downloader and sync_channels scripts without leaking
sys.path alterations or global state into clean domain layers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from cresmo.application.ports import MediaIngestionPort
from cresmo.domain.entities import RawTranscript
from cresmo.domain.exceptions import IngestionNetworkError, RateLimitExceededError
from cresmo.domain.value_objects import ContentId

_VIDEO_ID_REGEX = re.compile(r"(?:v=|\/)([a-zA-Z0-9_-]{8,64})(?:[&?]|\Z)")
_FRONTMATTER_REGEX = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$")


class LegacyIsbIngestionAdapter(MediaIngestionPort):
    """ACL Adapter wrapping playground/isb.ai functionality."""

    def __init__(self, isb_dir: Path | None = None) -> None:
        if isb_dir is None:
            # Default to workspace playground/isb.ai
            workspace_root = Path(__file__).resolve().parents[4]
            self.isb_dir = workspace_root / "playground" / "isb.ai"
        else:
            self.isb_dir = Path(isb_dir).resolve()

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video identifier from URL string."""
        match = _VIDEO_ID_REGEX.search(url)
        if match:
            return match.group(1)
        # Fallback to URL stem if already an ID
        return Path(url).stem

    def _call_legacy_sync_single(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str,
        keep_audio: bool,
    ) -> Path | None:
        """Isolated call to legacy sync_channels.sync_single_video."""
        # Ensure isb_dir is dynamically available only within this method context
        str_isb = str(self.isb_dir)
        path_added = False
        if str_isb not in sys.path and self.isb_dir.exists():
            sys.path.insert(0, str_isb)
            path_added = True

        try:
            import sync_channels  # type: ignore[import-not-found]

            sync_channels.sync_single_video(
                url=video_url,
                output_dir=output_dir,
                model_name=whisper_model,
                keep_audio=keep_audio,
            )
            vid = self._extract_video_id(video_url)
            matched = list(output_dir.glob(f"**/*{vid}*.*"))
            text_files = [p for p in matched if p.suffix in (".txt", ".md")]
            return text_files[0] if text_files else None
        finally:
            if path_added and str_isb in sys.path:
                sys.path.remove(str_isb)

    def _parse_transcript_file(self, file_path: Path, video_id: str) -> RawTranscript:
        """Parse legacy transcript file into RawTranscript domain aggregate."""
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_REGEX.match(text)
        if not match:
            return RawTranscript(
                content_id=ContentId(video_id),
                channel_name=file_path.parent.name,
                body=text.strip(),
            )

        fm_text, body = match.groups()
        meta = yaml.safe_load(fm_text) or {}
        cid_str = str(meta.get("id", video_id))
        channel = str(meta.get("channel", file_path.parent.name))
        return RawTranscript(
            content_id=ContentId(cid_str),
            channel_name=channel,
            body=body.strip(),
        )

    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Fetch subtitles or transcribe audio for a single video via legacy ACL.

        Args:
            video_url: Target YouTube video URL.
            output_dir: Directory where raw transcript will be stored.
            whisper_model: Whisper STT model variant.
            keep_audio: Whether to preserve downloaded audio file.

        Returns:
            RawTranscript domain entity, or None if not found.

        Raises:
            RateLimitExceededError: If upstream returns HTTP 429.
            IngestionNetworkError: If download fails due to network/transcription.
        """
        video_id = self._extract_video_id(video_url)
        output_dir = Path(output_dir).resolve()

        try:
            result_file = self._call_legacy_sync_single(
                video_url=video_url,
                output_dir=output_dir,
                whisper_model=whisper_model,
                keep_audio=keep_audio,
            )
            if not result_file or not result_file.exists():
                return None
            return self._parse_transcript_file(result_file, video_id)
        except Exception as exc:
            err_msg = str(exc)
            if "429" in err_msg or "Too Many Requests" in err_msg:
                raise RateLimitExceededError(
                    f"Upstream rate limit (429) hit while ingesting '{video_url}': {err_msg}"
                ) from exc
            raise IngestionNetworkError(
                f"Legacy ingestion failed for '{video_url}': {err_msg}"
            ) from exc

    def ingest_channels_and_playlists(
        self,
        playlist_urls: list[str],
        output_dir: Path,
        days_lookback: int = 730,
        whisper_model: str = "base",
        keep_audio: bool = False,
        max_workers: int = 4,
    ) -> list[RawTranscript]:
        """Crawl channels/playlists and ingest new videos within lookback window.

        Args:
            playlist_urls: List of YouTube channel/playlist URLs.
            output_dir: Output storage directory.
            days_lookback: Max age of videos to crawl.
            whisper_model: Whisper model for fallback transcription.
            keep_audio: Whether to keep audio files.
            max_workers: Concurrent ingestion workers.

        Returns:
            List of newly ingested RawTranscript entities.
        """
        output_dir = Path(output_dir).resolve()
        str_isb = str(self.isb_dir)
        path_added = False
        if str_isb not in sys.path and self.isb_dir.exists():
            sys.path.insert(0, str_isb)
            path_added = True

        try:
            import sync_channels  # type: ignore[import-not-found]

            csv_path = output_dir.parent / "isb_brain.csv"
            sync_channels.sync_channels_and_seeds(
                days=days_lookback,
                output_dir=output_dir,
                model_name=whisper_model,
                keep_audio=keep_audio,
                playlist_urls=playlist_urls,
                csv_path=csv_path,
                max_workers=max_workers,
            )

            results: list[RawTranscript] = []
            for file_path in output_dir.glob("**/*.*"):
                if file_path.suffix in (".txt", ".md"):
                    vid = file_path.stem
                    try:
                        transcript = self._parse_transcript_file(file_path, vid)
                        results.append(transcript)
                    except (OSError, ValueError, yaml.YAMLError):
                        continue
            return results
        except Exception as exc:
            err_msg = str(exc)
            if "429" in err_msg:
                raise RateLimitExceededError(
                    f"Upstream rate limit (429) during batch crawl: {err_msg}"
                ) from exc
            raise IngestionNetworkError(f"Batch crawl failed: {err_msg}") from exc
        finally:
            if path_added and str_isb in sys.path:
                sys.path.remove(str_isb)
