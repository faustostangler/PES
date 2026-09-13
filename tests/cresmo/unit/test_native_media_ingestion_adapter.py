"""Unit tests for NativeMediaIngestionAdapter.

Verifies native subtitle extraction, Whisper local fallback with ephemeral
scratch cleanup, rate limit (HTTP 429) mitigation, and channel feed discovery
without invoking external network or legacy isb.ai scripts (SPEC-004).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from cresmo.domain.exceptions import IngestionNetworkError, RateLimitExceededError
from cresmo.domain.value_objects import ChannelFeedQuery, ContentId
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)


class TestNativeMediaIngestionAdapter:
    """Hermetic unit tests for NativeMediaIngestionAdapter."""

    def test_ingest_single_video_with_native_subtitles_json3(self, tmp_path: Path) -> None:
        video_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        fake_info = {
            "id": "dQw4w9WgXcQ",
            "title": "Vilfredo Pareto and Elites",
            "channel": "Political Theory",
            "language": "pt",
            "subtitles": {
                "pt-orig": [
                    {
                        "ext": "json3",
                        "url": "https://video.google.com/timedtext?v=dQw4w9WgXcQ&lang=pt-orig",
                    }
                ]
            },
            "automatic_captions": {},
        }

        fake_json3 = {
            "events": [
                {
                    "tStartMs": 0,
                    "dDurationMs": 2000,
                    "segs": [
                        {"utf8": "A teoria da circulação das elites postula "},
                        {"utf8": "que minorias governam."},
                    ],
                },
                {
                    "tStartMs": 5000,
                    "dDurationMs": 2500,
                    "segs": [{"utf8": "Vilfredo Pareto desenvolveu esta formulação."}],
                },
            ]
        }

        adapter = NativeMediaIngestionAdapter()

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(
                adapter, "_fetch_url_content", return_value=json.dumps(fake_json3)
            ) as mock_fetch,
            patch("whisper.load_model") as mock_whisper,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            transcript = adapter.ingest_single_video(video_url=video_url, output_dir=tmp_path)

            assert transcript is not None
            assert transcript.content_id == ContentId("dQw4w9WgXcQ")
            assert transcript.channel_name == "Political Theory"
            assert "A teoria da circulação das elites postula" in transcript.body
            assert "Vilfredo Pareto desenvolveu esta formulação." in transcript.body

            # Verify that whisper audio fallback was NOT invoked
            mock_whisper.assert_not_called()
            mock_fetch.assert_called_once_with(
                "https://video.google.com/timedtext?v=dQw4w9WgXcQ&lang=pt-orig"
            )

    def test_ingest_single_video_rejects_tlang_subtitles(self, tmp_path: Path) -> None:
        video_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        # Subtitles containing tlang= should be completely filtered out
        fake_info = {
            "id": "dQw4w9WgXcQ",
            "title": "Machine Translated Captions",
            "channel": "Machine Channel",
            "language": "en",
            "subtitles": {},
            "automatic_captions": {
                "pt": [
                    {
                        "ext": "json3",
                        "url": "https://video.google.com/timedtext?v=dQw4w9WgXcQ&lang=en&tlang=pt",
                    }
                ]
            },
        }

        adapter = NativeMediaIngestionAdapter()

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(adapter, "_transcribe_audio_fallback") as mock_fallback,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            mock_fallback.return_value = ("Transcribed from Whisper", "Machine Channel")

            transcript = adapter.ingest_single_video(video_url=video_url, output_dir=tmp_path)

            assert transcript is not None
            assert transcript.body == "Transcribed from Whisper"
            mock_fallback.assert_called_once()

    def test_ingest_single_video_whisper_fallback_and_scratch_cleanup(self, tmp_path: Path) -> None:
        video_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        fake_info = {
            "id": "dQw4w9WgXcQ",
            "title": "Audio Only Video",
            "channel": "Podcast Channel",
            "subtitles": {},
            "automatic_captions": {},
        }

        adapter = NativeMediaIngestionAdapter()
        captured_scratch_dirs: list[Path] = []

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model") as mock_whisper_loader,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info

            def fake_download(urls: list[str]) -> None:
                # Simulate downloading audio file into output_dir parameter
                # The adapter should configure ydl outtmpl to a temp directory
                pass

            mock_ydl.download.side_effect = fake_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            mock_model = MagicMock()
            mock_model.transcribe.return_value = {"text": "Verbatim audio transcript via Whisper."}
            mock_whisper_loader.return_value = mock_model

            # Intercept tempfile.TemporaryDirectory to monitor cleanup
            import tempfile
            from typing import Any

            real_tempdir = tempfile.TemporaryDirectory

            def tracking_tempdir(*args: Any, **kwargs: Any) -> tempfile.TemporaryDirectory[str]:
                td = real_tempdir(*args, **kwargs)
                captured_scratch_dirs.append(Path(td.name))
                # Create a dummy audio file inside to test deletion
                (Path(td.name) / "audio.m4a").write_text("fake audio bytes")
                return td

            with patch("tempfile.TemporaryDirectory", side_effect=tracking_tempdir):
                transcript = adapter.ingest_single_video(video_url=video_url, output_dir=tmp_path)

                assert transcript is not None
                assert transcript.content_id == ContentId("dQw4w9WgXcQ")
                assert transcript.channel_name == "Podcast Channel"
                assert transcript.body == "Verbatim audio transcript via Whisper."

                # Verify scratch dir was wiped clean
                assert len(captured_scratch_dirs) == 1
                assert not captured_scratch_dirs[0].exists()

    def test_discover_channel_feed_success(self) -> None:
        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@TheoryChannel",
            lookback_days=7,
            max_videos=10,
        )

        fake_flat_playlist = {
            "id": "@TheoryChannel",
            "title": "Theory Channel Playlist",
            "entries": [
                {
                    "id": "video11111111",
                    "title": "Pareto and Mosca",
                    "url": "https://youtube.com/watch?v=video11111111",
                    "channel": "Theory Channel",
                    "upload_date": datetime.now(UTC).strftime("%Y%m%d"),
                },
                {
                    "id": "video22222222",
                    "title": "Robert Michels Oligarchy",
                    "url": "https://youtube.com/watch?v=video22222222",
                    "channel": "Theory Channel",
                    "upload_date": "20240101",
                },
            ],
        }

        adapter = NativeMediaIngestionAdapter()

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_flat_playlist
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            items = adapter.discover_channel_feed(query=query)

            assert len(items) == 2
            assert items[0].content_id == ContentId("video11111111")
            assert items[0].title == "Pareto and Mosca"
            assert items[0].channel_name == "Theory Channel"
            assert items[1].content_id == ContentId("video22222222")

    def test_error_translation_rate_limit_429(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError(
                "HTTP Error 429: Too Many Requests"
            )
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(RateLimitExceededError):
                adapter.ingest_single_video(
                    "https://youtube.com/watch?v=rateLimitVid", output_dir=tmp_path
                )

    def test_error_translation_network_error(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError(
                "Connection reset by peer"
            )
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(IngestionNetworkError):
                adapter.ingest_single_video(
                    "https://youtube.com/watch?v=netErrorVid", output_dir=tmp_path
                )

    def test_ingest_single_video_keep_audio(self, tmp_path: Path) -> None:
        video_url = "https://youtube.com/watch?v=keepAudioVid"
        fake_info = {
            "id": "keepAudioVid",
            "title": "Keep Audio Test",
            "channel": "KeepAudioChannel",
            "subtitles": {},
            "automatic_captions": {},
        }

        adapter = NativeMediaIngestionAdapter()

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model") as mock_whisper_loader,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info

            def fake_download(urls: list[str]) -> None:
                pass

            mock_ydl.download.side_effect = fake_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            mock_model = MagicMock()
            mock_model.transcribe.return_value = {"text": "Audio transcript content."}
            mock_whisper_loader.return_value = mock_model

            import tempfile
            from typing import Any

            real_tempdir = tempfile.TemporaryDirectory

            def tracking_tempdir(*args: Any, **kwargs: Any) -> tempfile.TemporaryDirectory[str]:
                td = real_tempdir(*args, **kwargs)
                (Path(td.name) / "keepAudioVid.m4a").write_text("dummy audio file content")
                return td

            with patch("tempfile.TemporaryDirectory", side_effect=tracking_tempdir):
                transcript = adapter.ingest_single_video(
                    video_url=video_url,
                    output_dir=tmp_path,
                    keep_audio=True,
                )

                assert transcript is not None
                assert transcript.body == "Audio transcript content."

                # Verify audio was preserved in output_dir / channel_name
                expected_audio = tmp_path / "KeepAudioChannel" / "keepAudioVid.m4a"
                assert expected_audio.exists()
                assert expected_audio.read_text() == "dummy audio file content"

    def test_ingest_channels_and_playlists(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch.object(adapter, "ingest_single_video") as mock_single:
            mock_single.side_effect = [
                MagicMock(content_id=ContentId("vid11111111")),
                None,
                MagicMock(content_id=ContentId("vid33333333")),
            ]

            results = adapter.ingest_channels_and_playlists(
                playlist_urls=["https://url1", "https://url2", "https://url3"],
                output_dir=tmp_path,
            )

            assert len(results) == 2
            assert mock_single.call_count == 3
