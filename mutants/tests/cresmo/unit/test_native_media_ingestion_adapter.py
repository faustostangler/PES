"""Unit tests for NativeMediaIngestionAdapter.

Verifies native subtitle extraction, Whisper local fallback with ephemeral
scratch cleanup, rate limit (HTTP 429) mitigation, and channel feed discovery
without invoking external network or legacy isb.ai scripts (SPEC-004).
"""

from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp
import yt_dlp.utils

from cresmo.domain.exceptions import (
    CresmoInfrastructureError,
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import ChannelFeedQuery, ChannelId, ContentId
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
            assert transcript.content.id == ContentId("dQw4w9WgXcQ")
            assert transcript.channel.name == "Political Theory"
            assert "A teoria da circulação das elites postula" in transcript.content.body
            assert "Vilfredo Pareto desenvolveu esta formulação." in transcript.content.body

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
            assert transcript.content.body == "Transcribed from Whisper"
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
                assert transcript.content.id == ContentId("dQw4w9WgXcQ")
                assert transcript.channel.name == "Podcast Channel"
                assert transcript.content.body == "Verbatim audio transcript via Whisper."

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
                assert transcript.content.body == "Audio transcript content."

                # Verify audio was preserved in output_dir / channel_name
                expected_audio = tmp_path / "KeepAudioChannel" / "keepAudioVid.m4a"
                assert expected_audio.exists()
                assert expected_audio.read_text() == "dummy audio file content"

    def test_fetch_url_content_uses_dynamic_headers(self) -> None:
        mock_generator = MagicMock()
        mock_generator.get_random_headers.return_value = {
            "User-Agent": "DynamicTestUA/1.0",
            "Accept": "text/html",
        }
        adapter = NativeMediaIngestionAdapter(header_generator=mock_generator)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b"sample subtitle payload"
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            content = adapter._fetch_url_content("https://video.google.com/timedtext?v=test")

            assert content == "sample subtitle payload"
            mock_generator.get_random_headers.assert_called_once()
            called_req = mock_urlopen.call_args[0][0]
            assert isinstance(called_req, urllib.request.Request)
            assert called_req.headers.get("User-agent") == "DynamicTestUA/1.0"
            assert called_req.headers.get("Accept") == "text/html"

    def test_yt_dlp_options_include_dynamic_http_headers(self, tmp_path: Path) -> None:
        mock_generator = MagicMock()
        mock_generator.get_random_headers.return_value = {
            "User-Agent": "YtDlpTestUA/2.0",
            "Sec-Ch-Ua-Platform": '"Linux"',
        }
        adapter = NativeMediaIngestionAdapter(header_generator=mock_generator)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "id": "mock_video_12345",
                "title": "Mock Title",
                "subtitles": {},
                "automatic_captions": {},
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with patch.object(adapter, "_transcribe_audio_fallback", return_value=("Text", "Chan")):
                adapter.ingest_single_video(
                    "https://youtube.com/watch?v=mock_video_12345", output_dir=tmp_path
                )

            mock_ydl_cls.assert_called()
            ydl_opts = mock_ydl_cls.call_args[0][0]
            assert "http_headers" in ydl_opts
            assert ydl_opts["http_headers"]["User-Agent"] == "YtDlpTestUA/2.0"
            assert ydl_opts["http_headers"]["Sec-Ch-Ua-Platform"] == '"Linux"'

    def test_extract_channel_url_from_video_success(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "channel_url": "https://www.youtube.com/@ChannelHandle",
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            res = adapter.extract_channel_url_from_video("https://www.youtube.com/watch?v=abc12345")
            assert res == "https://www.youtube.com/@ChannelHandle/videos"
            opts = mock_ydl_cls.call_args[0][0]
            assert opts["extract_flat"] is True
            assert opts["quiet"] is True
            assert opts["no_warnings"] is True
            assert mock_ydl.extract_info.call_args[1]["download"] is False

    def test_extract_channel_url_from_video_fallback_to_channel_id(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "channel_id": "UC1234567890abcdef",
            }
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            res = adapter.extract_channel_url_from_video("https://www.youtube.com/watch?v=abc12345")
            assert res == "https://www.youtube.com/playlist?list=UU1234567890abcdef"

    def test_extract_channel_url_from_video_returns_none_on_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        caplog.set_level(logging.DEBUG)
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            res = adapter.extract_channel_url_from_video(
                "https://www.youtube.com/watch?v=unavailable"
            )
            assert res is None
            assert "Could not extract channel URL from video" in caplog.text
            assert "via flat extraction: Video unavailable" in caplog.text

    def test_extract_video_id_fallback_to_path_stem(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        assert adapter._extract_video_id("local_custom_video_123.mp4") == "local_custom_video_123"

    def test_is_native_subtitle_url_none_returns_false(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        assert adapter._is_native_subtitle_url(None) is False

    def test_find_native_subtitle_url_non_pt_video(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        info = {
            "language": "en",
            "subtitles": {
                "en": [{"ext": "json3", "url": "https://video.google.com/timedtext?lang=en"}],
            },
            "automatic_captions": {},
        }
        url = adapter._find_native_subtitle_url(info)
        assert url == "https://video.google.com/timedtext?lang=en"

    def test_find_native_subtitle_url_fallback_any_manual_language(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        info = {
            "language": "es",
            "subtitles": {
                "fr": [{"ext": "json3", "url": "https://video.google.com/timedtext?lang=fr"}],
            },
            "automatic_captions": {},
        }
        url = adapter._find_native_subtitle_url(info)
        assert url == "https://video.google.com/timedtext?lang=fr"

    def test_find_native_subtitle_url_automatic_captions_orig_and_fallbacks(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        # Test auto captions with orig suffix
        info_orig = {
            "language": "pt",
            "subtitles": {},
            "automatic_captions": {
                "pt-orig": [
                    {"ext": "json3", "url": "https://video.google.com/timedtext?lang=pt-orig"}
                ],
            },
        }
        assert (
            adapter._find_native_subtitle_url(info_orig)
            == "https://video.google.com/timedtext?lang=pt-orig"
        )

        # Test auto captions any language fallback
        info_any = {
            "language": "it",
            "subtitles": {},
            "automatic_captions": {
                "de": [{"ext": "json3", "url": "https://video.google.com/timedtext?lang=de"}],
            },
        }
        assert (
            adapter._find_native_subtitle_url(info_any)
            == "https://video.google.com/timedtext?lang=de"
        )

    def test_fetch_url_content_http_errors(self) -> None:
        import urllib.error
        from email.message import Message

        adapter = NativeMediaIngestionAdapter()

        # 429 raises RateLimitExceededError
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://test", code=429, msg="Too Many Requests", hdrs=Message(), fp=None
            )
            with pytest.raises(RateLimitExceededError, match="HTTP 429"):
                adapter._fetch_url_content("https://test")

        # 500 raises IngestionNetworkError
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://test", code=500, msg="Internal Server Error", hdrs=Message(), fp=None
            )
            with pytest.raises(IngestionNetworkError, match="HTTP error"):
                adapter._fetch_url_content("https://test")

        # Generic network exception raises IngestionNetworkError
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = ConnectionResetError("Connection reset")
            with pytest.raises(IngestionNetworkError, match="Network error"):
                adapter._fetch_url_content("https://test")

    def test_handle_yt_dlp_error_generic_raises_cresmo_infrastructure_error(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with pytest.raises(
            CresmoInfrastructureError, match="Media extraction infrastructure error"
        ):
            adapter._handle_yt_dlp_error(ValueError("Unexpected parser state"))

    def test_transcribe_audio_fallback_empty_scratch_raises_error(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            pytest.raises(IngestionNetworkError, match="no file was found"),
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            # yt-dlp finishes but scratch dir contains no downloaded files
            adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=empty",
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )

    def test_transcribe_audio_fallback_whisper_failure_raises_infrastructure_error(
        self, tmp_path: Path
    ) -> None:
        adapter = NativeMediaIngestionAdapter()

        def fake_download(urls: list[str]) -> None:
            # Create dummy audio file in temp scratch
            pass

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model") as mock_whisper_load,
            patch("pathlib.Path.glob") as mock_glob,
            pytest.raises(CresmoInfrastructureError, match="Whisper transcription failed"),
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            mock_glob.return_value = [tmp_path / "dummy_audio.m4a"]
            mock_whisper_load.side_effect = RuntimeError("Whisper weights corrupt")

            adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=error",
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )

    def test_transcribe_audio_fallback_keep_audio_copies_file(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()

        dummy_audio = tmp_path / "scratch_dummy.m4a"
        dummy_audio.write_bytes(b"FAKE AUDIO BYTES")

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model") as mock_whisper_load,
            patch("tempfile.TemporaryDirectory") as mock_tempdir,
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            scratch_dir = tmp_path / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            audio_in_scratch = scratch_dir / "dQw4w9WgXcQ.m4a"
            audio_in_scratch.write_bytes(b"FAKE AUDIO DATA")

            mock_tempdir.return_value.__enter__.return_value = str(scratch_dir)

            mock_model = MagicMock()
            mock_model.transcribe.return_value = {"text": "Transcribed speech content."}
            mock_whisper_load.return_value = mock_model

            body, channel = adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=True,
                info={"channel": "Test Channel"},
            )

            assert body == "Transcribed speech content."
            assert channel == "Test Channel"
            # Verify audio was copied to output_dir / Test Channel
            preserved_audio = tmp_path / "Test Channel" / "dQw4w9WgXcQ.m4a"
            assert preserved_audio.exists()
            assert preserved_audio.read_bytes() == b"FAKE AUDIO DATA"

    def test_ingest_single_video_subtitle_fetch_fails_falls_back_to_whisper(
        self, tmp_path: Path
    ) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {
            "id": "dQw4w9WgXcQ",
            "title": "Fallback Video",
            "channel": "Fallback Channel",
            "language": "pt",
            "subtitles": {
                "pt": [{"ext": "json3", "url": "https://video.google.com/timedtext?v=fail"}],
            },
            "automatic_captions": {},
        }

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(
                adapter,
                "_fetch_url_content",
                side_effect=IngestionNetworkError("Subtitle connection refused"),
            ),
            patch.object(
                adapter,
                "_transcribe_audio_fallback",
                return_value=("Transcribed from audio fallback.", "Fallback_Channel"),
            ) as mock_whisper_fb,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
            )

            assert transcript is not None
            assert transcript.content.body == "Transcribed from audio fallback."
            mock_whisper_fb.assert_called_once()

    def test_acl_date_parsing_helpers(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        # Valid upload_date
        assert adapter._parse_upload_date("20240315") == datetime(2024, 3, 15, tzinfo=UTC).date()
        # Invalid or empty
        assert adapter._parse_upload_date("") is None
        assert adapter._parse_upload_date(None) is None
        assert adapter._parse_upload_date("invalid_date") is None
        assert adapter._parse_upload_date("2024") is None

        # Published datetime
        dt = adapter._parse_published_datetime("20240315")
        assert dt.year == 2024 and dt.month == 3 and dt.day == 15
        dt_fallback = adapter._parse_published_datetime(None)
        assert isinstance(dt_fallback, datetime)

    def test_ingest_single_video_vo_extraction_and_publication_date(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {
            "id": "abc12345678",
            "title": "Vo Extraction Test",
            "channel": "Channel / Slashed",
            "channel_id": "UC1234567890123456789012",
            "upload_date": "20240520",
            "description": "Video description text",
            "subtitles": {
                "en": [
                    {
                        "ext": "json3",
                        "url": "https://video.google.com/timedtext?v=test",
                    }
                ]
            },
        }

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(
                adapter,
                "_fetch_url_content",
                return_value=json.dumps({"events": [{"segs": [{"utf8": "Hello world"}]}]}),
            ),
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=abc12345678",
                output_dir=tmp_path,
            )

            assert transcript is not None
            assert transcript.content.id == ContentId("abc12345678")
            assert transcript.channel.name == "Channel _ Slashed"
            assert transcript.channel.id == ChannelId("UC1234567890123456789012")
            assert (
                transcript.provenance.publication_date == datetime(2024, 5, 20, tzinfo=UTC).date()
            )

    def test_extract_channel_url_from_video_uploads_playlist(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {
            "channel_id": "UCtestChannelId12345678",
        }

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            url = adapter.extract_channel_url_from_video("https://youtube.com/watch?v=abc12345678")
            assert url == "https://www.youtube.com/playlist?list=UUtestChannelId12345678"

    def test_ingest_single_video_records_media_ingestion_metrics(self, tmp_path: Path) -> None:
        """SPEC-008 Scenario 6: Ingestion Latency Recording via MetricsPort."""
        from prometheus_client import CollectorRegistry

        from cresmo.infrastructure.adapters.prometheus_metrics_adapter import (
            PrometheusMetricsAdapter,
        )

        registry = CollectorRegistry(auto_describe=True)
        metrics_adapter = PrometheusMetricsAdapter(registry=registry)

        adapter = NativeMediaIngestionAdapter(metrics_port=metrics_adapter)
        fake_info = {
            "id": "ingest_metric_01",
            "title": "Metric Ingestion Test",
            "channel": "Sandeco_Channel",
            "upload_date": "20240520",
            "subtitles": {
                "en": [
                    {
                        "ext": "json3",
                        "url": "https://video.google.com/timedtext?v=test",
                    }
                ]
            },
        }

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(
                adapter,
                "_fetch_url_content",
                return_value=json.dumps({"events": [{"segs": [{"utf8": "Hello world"}]}]}),
            ),
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=ingest_metric_01",
                output_dir=tmp_path,
            )

            assert transcript is not None
            sample_count = registry.get_sample_value(
                "cresmo_media_ingestion_duration_seconds_count",
                {
                    "channel_id": "",
                    "channel_name": "Sandeco_Channel",
                    "modality": "url",
                    "status": "success",
                },
            )
            assert sample_count == 1.0

    def test_handle_yt_dlp_error_exhaustive(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with pytest.raises(RateLimitExceededError, match="HTTP 429"):
            adapter._handle_yt_dlp_error(Exception("HTTP Error 429"))
        with pytest.raises(RateLimitExceededError, match="HTTP 429"):
            adapter._handle_yt_dlp_error(Exception("Error: Too Many Requests received"))

        with pytest.raises(IngestionNetworkError, match="YouTube bot-detection challenge"):
            adapter._handle_yt_dlp_error(Exception("Sign in to confirm you’re not a bot"))
        with pytest.raises(IngestionNetworkError, match="YouTube bot-detection challenge"):
            adapter._handle_yt_dlp_error(Exception("Please confirm you're not a bot to proceed"))

        for term in ("Connection reset by peer", "Operation timed out", "Name or service not known", "Network unreachable"):
            with pytest.raises(IngestionNetworkError, match="Ingestion network connectivity error"):
                adapter._handle_yt_dlp_error(Exception(term))

        with pytest.raises(CresmoInfrastructureError, match="Media extraction infrastructure error"):
            adapter._handle_yt_dlp_error(Exception("Some unknown yt-dlp internal error"))

    def test_transcribe_audio_fallback_keep_audio_and_cleanup(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {"channel": "Science Today", "uploader": "SciUploader"}
        dummy_audio_name = "test_audio.m4a"

        def mock_ydl_download(urls: list[str]) -> None:
            # Create a fake audio file in scratch directory
            import glob
            scratch_dirs = glob.glob("/tmp/cresmo_scratch_*")
            if scratch_dirs:
                latest = max(scratch_dirs, key=lambda d: Path(d).stat().st_mtime)
                (Path(latest) / dummy_audio_name).write_bytes(b"dummy audio bytes")

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model") as mock_load_model,
        ):
            mock_ydl = MagicMock()
            mock_ydl.download.side_effect = mock_ydl_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            mock_model = MagicMock()
            mock_model.transcribe.return_value = {"text": "  Transcribed text content  "}
            mock_load_model.return_value = mock_model

            body, channel = adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=123",
                output_dir=tmp_path,
                whisper_model="tiny",
                keep_audio=True,
                info=fake_info,
            )

            assert body == "Transcribed text content"
            assert channel == "Science Today"
            saved_audio = tmp_path / "Science Today" / dummy_audio_name
            assert saved_audio.exists()
            assert saved_audio.read_bytes() == b"dummy audio bytes"
            opts = mock_ydl_cls.call_args[0][0]
            assert opts["format"] == "bestaudio/best"
            assert "%(id)s.%(ext)s" in opts["outtmpl"]
            assert opts["quiet"] is True
            assert opts["no_warnings"] is True
            assert mock_ydl.download.call_args[0][0] == ["https://youtube.com/watch?v=123"]

    def test_resolve_transcript_body_with_native_subtitles_success(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {
            "id": "sub_success",
            "channel": "MyChannel",
            "subtitles": {
                "pt": [{"ext": "json3", "url": "https://subs.google.com/timedtext?v=sub_success"}]
            },
        }
        raw_json3 = json.dumps({"events": [{"segs": [{"utf8": "Primeiro paragrafo falado."}]}]})
        with patch.object(adapter, "_fetch_url_content", return_value=raw_json3) as mock_fetch:
            body, chan = adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=sub_success",
                info=fake_info,
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )
            assert body == "Primeiro paragrafo falado."
            assert chan == "MyChannel"
            mock_fetch.assert_called_once_with("https://subs.google.com/timedtext?v=sub_success")

    def test_transcribe_audio_fallback_no_downloaded_file_raises_error(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model"),
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(IngestionNetworkError, match="no file was found"):
                adapter._transcribe_audio_fallback(
                    video_url="https://youtube.com/watch?v=123",
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                    info={"uploader": "UploaderOnly"},
                )

    def test_transcribe_audio_fallback_whisper_error_raises_infra_error(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()

        def mock_ydl_download(urls: list[str]) -> None:
            import glob
            scratch_dirs = glob.glob("/tmp/cresmo_scratch_*")
            if scratch_dirs:
                latest = max(scratch_dirs, key=lambda d: Path(d).stat().st_mtime)
                (Path(latest) / "audio.mp3").write_bytes(b"dummy")

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("whisper.load_model", side_effect=RuntimeError("CUDA OOM")),
        ):
            mock_ydl = MagicMock()
            mock_ydl.download.side_effect = mock_ydl_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(CresmoInfrastructureError, match="Whisper transcription failed: CUDA OOM"):
                adapter._transcribe_audio_fallback(
                    video_url="https://youtube.com/watch?v=123",
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                    info=None,
                )

    def test_build_raw_transcript_aggregate_attributes(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        info = {
            "id": "vid999",
            "channel_id": "UC_channel_123",
            "channel_url": "https://youtube.com/@channel123",
            "upload_date": "20231225",
            "title": "Quantum Computing 101",
            "description": "Intro to qubits and entanglement",
        }
        transcript, ch_id = adapter._build_raw_transcript_aggregate(
            video_url="https://youtube.com/watch?v=vid999",
            info=info,
            body="Qubits can exist in superposition.",
            channel_name="QuantumHub",
        )
        assert transcript.channel.name == "QuantumHub"
        assert transcript.channel.url == "https://youtube.com/@channel123"
        assert transcript.content.title == "Quantum Computing 101"
        assert transcript.content.body == "Qubits can exist in superposition."
        assert transcript.provenance.description == "Intro to qubits and entanglement"
        assert ch_id is not None
        assert ch_id.value == "UC_channel_123"

    def test_build_raw_transcript_aggregate_channel_url_empty_becomes_none(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        info = {
            "id": "vid000",
            "uploader_id": "uploader_xyz",
            "channel_url": "",
            "upload_date": "",
            "title": "Title",
            "description": "",
        }
        transcript, ch_id = adapter._build_raw_transcript_aggregate(
            video_url="https://youtube.com/watch?v=vid000",
            info=info,
            body="body",
            channel_name="Chan",
        )
        assert transcript.channel.url is None
        assert ch_id is not None
        assert ch_id.value == "uploader_xyz"

    def test_build_ydl_opts_options_injection(self, tmp_path: Path) -> None:
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n.youtube.com TRUE / FALSE 0 SID secret", encoding="utf-8")

        adapter = NativeMediaIngestionAdapter(
            cookie_file=cookie_file,
            js_runtime_name="node",
        )

        base_opts = {"quiet": True, "http_headers": {"Custom-Header": "Preserved"}}
        opts = adapter._build_ydl_opts(base_opts)

        assert opts["quiet"] is True
        assert opts["http_headers"] == {"Custom-Header": "Preserved"}
        assert opts["cookiefile"] == str(cookie_file)
        assert opts["js_runtimes"] == {"node": {}}

    def test_fetch_video_metadata_none_returns_error(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = None
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(IngestionNetworkError, match="yt-dlp returned no metadata"):
                adapter._fetch_video_metadata("https://youtube.com/watch?v=empty_meta")

    def test_fetch_video_metadata_options_and_success(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"id": "123", "title": "Test"}
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            res = adapter._fetch_video_metadata("https://youtube.com/watch?v=123")
            assert res == {"id": "123", "title": "Test"}
            opts = mock_ydl_cls.call_args[0][0]
            assert opts["skip_download"] is True
            assert opts["quiet"] is True
            assert opts["no_warnings"] is True
            assert mock_ydl.extract_info.call_args[1]["download"] is False

    def test_fetch_video_metadata_exception_handled(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = RuntimeError("timed out")
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(IngestionNetworkError, match="Ingestion network connectivity error"):
                adapter._fetch_video_metadata("https://youtube.com/watch?v=123")

    def test_ingest_single_video_when_metadata_none_returns_none(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch.object(adapter, "_fetch_video_metadata", return_value=None):
            res = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=no_meta",
                output_dir=tmp_path,
            )
            assert res is None

    def test_ingest_single_video_exception_records_failure_metric(self, tmp_path: Path) -> None:
        from prometheus_client import CollectorRegistry
        from cresmo.infrastructure.adapters.prometheus_metrics_adapter import PrometheusMetricsAdapter

        registry = CollectorRegistry(auto_describe=True)
        metrics = PrometheusMetricsAdapter(registry=registry)
        adapter = NativeMediaIngestionAdapter(metrics_port=metrics)

        with (
            patch.object(adapter, "_fetch_video_metadata", return_value={"id": "fail1", "channel": "FailChan"}),
            patch.object(adapter, "_resolve_transcript_body", side_effect=RuntimeError("Whisper exploded")),
        ):
            with pytest.raises(RuntimeError, match="Whisper exploded"):
                adapter.ingest_single_video(
                    video_url="https://youtube.com/watch?v=fail1",
                    output_dir=tmp_path,
                )

            sample_count = registry.get_sample_value(
                "cresmo_media_ingestion_duration_seconds_count",
                {
                    "channel_id": "",
                    "channel_name": "Unknown_Channel",
                    "modality": "url",
                    "status": "failure",
                },
            )
            assert sample_count == 1.0

    def test_resolve_transcript_body_empty_raises_domain_validation_error(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value=None),
            patch.object(adapter, "_transcribe_audio_fallback", return_value=("", "Chan")),
        ):
            with pytest.raises(DomainValidationError, match="Extracted transcript body is empty"):
                adapter._resolve_transcript_body(
                    video_url="https://youtube.com/watch?v=empty_vid",
                    info={"id": "empty_vid"},
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                )

    def test_resolve_transcript_body_rate_limit_reraised(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value="https://subs.url"),
            patch.object(adapter, "_fetch_url_content", side_effect=RateLimitExceededError("HTTP 429")),
        ):
            with pytest.raises(RateLimitExceededError):
                adapter._resolve_transcript_body(
                    video_url="https://youtube.com/watch?v=rl_vid",
                    info={"id": "rl_vid"},
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                )

    def test_resolve_transcript_body_native_sub_exception_falls_back_to_whisper(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        caplog.set_level(logging.WARNING)
        adapter = NativeMediaIngestionAdapter()
        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value="https://subs.url"),
            patch.object(adapter, "_fetch_url_content", return_value="invalid json {{{"),
            patch.object(adapter, "_transcribe_audio_fallback", return_value=("Fallback body", "Chan")),
        ):
            body, chan = adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=sub_err",
                info={"id": "sub_err", "channel": "Chan"},
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )
            assert body == "Fallback body"
            assert chan == "Chan"
            assert "Failed to fetch or parse native subtitles" in caplog.text
            assert "Falling back to Whisper" in caplog.text

    def test_detect_js_runtime_precedence_and_none(self) -> None:
        import shutil
        adapter = NativeMediaIngestionAdapter()
        with patch("shutil.which", side_effect=lambda x: "/usr/bin/node" if x == "node" else None):
            assert adapter._detect_js_runtime() == "node"

        with patch("shutil.which", side_effect=lambda x: "/usr/bin/deno" if x == "deno" else None):
            assert adapter._detect_js_runtime() == "deno"

        with patch("shutil.which", side_effect=lambda x: "/usr/bin/bun" if x == "bun" else None):
            assert adapter._detect_js_runtime() == "bun"

        with patch("shutil.which", return_value=None):
            assert adapter._detect_js_runtime() is None

    def test_sanitize_fs_name_illegal_chars_and_fallbacks(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        assert adapter._sanitize_fs_name("Valid Channel") == "Valid Channel"
        assert adapter._sanitize_fs_name("Channel: With / Illegal * Chars?") == "Channel_ With _ Illegal _ Chars_"
        assert adapter._sanitize_fs_name("") == "Unknown_Channel"
        assert adapter._sanitize_fs_name("   ") == "Unknown_Channel"
        assert adapter._sanitize_fs_name("///") == "___"

    def test_build_raw_transcript_aggregate_no_channel_id_returns_none(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        info = {
            "id": "vid111",
            "title": "Title 111",
        }
        transcript, ch_id = adapter._build_raw_transcript_aggregate(
            video_url="https://youtube.com/watch?v=vid111",
            info=info,
            body="body text",
            channel_name="NoChannelID",
        )
        assert ch_id is None
        assert transcript.channel.id is None
        assert transcript.provenance.description == ""
        assert transcript.provenance.publication_date is None

    def test_ingest_single_video_success_flow(self, tmp_path: Path) -> None:
        adapter = NativeMediaIngestionAdapter()
        fake_info = {
            "id": "ingest_ok_1",
            "title": "Ingested Title",
            "channel": "IngestChan",
            "channel_id": "UC_ingest_123",
            "upload_date": "20240101",
        }
        with (
            patch.object(adapter, "_fetch_video_metadata", return_value=fake_info),
            patch.object(adapter, "_resolve_transcript_body", return_value=("Resolved body text", "IngestChan")),
        ):
            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=ingest_ok_1",
                output_dir=tmp_path,
                whisper_model="tiny",
                keep_audio=False,
            )
            assert transcript is not None
            assert transcript.content.title == "Ingested Title"
            assert transcript.content.body == "Resolved body text"
            assert transcript.channel.name == "IngestChan"
            assert transcript.channel.id is not None
            assert transcript.channel.id.value == "UC_ingest_123"
