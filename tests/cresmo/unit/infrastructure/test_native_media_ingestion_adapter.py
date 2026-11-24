"""Unit tests for NativeMediaIngestionAdapter.

Verifies native subtitle extraction, Whisper local fallback with ephemeral
scratch cleanup, rate limit (HTTP 429) mitigation, and channel feed discovery
without invoking external network or legacy isb.ai scripts (SPEC-004).
"""

from __future__ import annotations

import json
import sys
import types
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
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
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import (
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
        mock_transcriber = MagicMock()
        adapter._transcriber = mock_transcriber

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.object(
                adapter, "_fetch_url_content", return_value=json.dumps(fake_json3)
            ) as mock_fetch,
        ):
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            transcript = adapter.ingest_single_video(video_url=video_url, output_dir=tmp_path)

            assert transcript is not None
            assert transcript.content.id == ContentId("dQw4w9WgXcQ")
            assert transcript.channel.name == "Political Theory"
            assert "A teoria da circulação das elites postula" in transcript.content.text
            assert "Vilfredo Pareto desenvolveu esta formulação." in transcript.content.text

            # Verify that whisper audio fallback was NOT invoked
            mock_transcriber.transcribe.assert_not_called()
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
            mock_fallback.return_value = "Transcribed from Whisper"

            transcript = adapter.ingest_single_video(video_url=video_url, output_dir=tmp_path)

            assert transcript is not None
            assert transcript.content.text == "Transcribed from Whisper"
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

        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = "Verbatim audio transcript via Whisper."
        adapter = NativeMediaIngestionAdapter(transcriber=mock_transcriber)
        captured_scratch_dirs: list[Path] = []

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info

            def fake_download(urls: list[str]) -> None:
                # Simulate downloading audio file into output_dir parameter
                # The adapter should configure ydl outtmpl to a temp directory
                pass

            mock_ydl.download.side_effect = fake_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

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
                assert transcript.content.text == "Verbatim audio transcript via Whisper."
                mock_transcriber.transcribe.assert_called_once()

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

        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = "Audio transcript content."
        adapter = NativeMediaIngestionAdapter(transcriber=mock_transcriber)

        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = fake_info

            def fake_download(urls: list[str]) -> None:
                pass

            mock_ydl.download.side_effect = fake_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

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
                assert transcript.content.text == "Audio transcript content."

                # Verify audio was preserved in output_dir / channel_name
                expected_audio = tmp_path / "KeepAudioChannel" / "keepAudioVid.m4a"
                assert expected_audio.exists()
                assert expected_audio.read_text() == "dummy audio file content"

    def test_fetch_url_content_uses_dynamic_headers_and_pooled_httpx(self) -> None:
        mock_generator = MagicMock()
        mock_generator.get_random_headers.return_value = {
            "User-Agent": "DynamicTestUA/1.0",
            "Accept": "text/html",
        }
        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.text = "sample subtitle payload"
        mock_client.get.return_value = mock_resp

        adapter = NativeMediaIngestionAdapter(
            header_generator=mock_generator,
            http_client=mock_client,
        )

        content = adapter._fetch_url_content("https://video.google.com/timedtext?v=test")

        assert content == "sample subtitle payload"
        mock_generator.get_random_headers.assert_called_once()
        mock_client.get.assert_called_once_with(
            "https://video.google.com/timedtext?v=test",
            headers={"User-Agent": "DynamicTestUA/1.0", "Accept": "text/html"},
        )
        mock_resp.raise_for_status.assert_called_once()
        # Injected client must not be closed by adapter.close()
        adapter.close()
        mock_client.close.assert_not_called()

    def test_owned_httpx_client_is_lazy_reused_and_closed(self) -> None:
        adapter = NativeMediaIngestionAdapter(request_timeout=12.0)
        assert adapter._http_client is None

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_resp = MagicMock()
            mock_resp.text = "ok"
            mock_client.get.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            with adapter as ctx_adapter:
                assert ctx_adapter._fetch_url_content("https://example.com/1") == "ok"
                assert ctx_adapter._fetch_url_content("https://example.com/2") == "ok"

            mock_client_cls.assert_called_once()
            _, kwargs = mock_client_cls.call_args
            assert kwargs["timeout"] == 12.0
            assert kwargs["follow_redirects"] is True
            assert kwargs["limits"].max_connections == 20
            assert kwargs["limits"].max_keepalive_connections == 10
            assert mock_client.get.call_count == 2
            mock_client.close.assert_called_once()

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

            with patch.object(adapter, "_transcribe_audio_fallback", return_value="Text"):
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
        from cresmo.infrastructure.adapters.media.subtitles import is_native_subtitle_url

        assert is_native_subtitle_url(None) is False

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
        mock_client = MagicMock(spec=httpx.Client)
        adapter = NativeMediaIngestionAdapter(http_client=mock_client)

        # 429 raises RateLimitExceededError
        req_429 = httpx.Request("GET", "https://test")
        resp_429 = httpx.Response(429, request=req_429)
        mock_client.get.return_value = resp_429
        with pytest.raises(RateLimitExceededError, match="HTTP 429"):
            adapter._fetch_url_content("https://test")

        # 500 raises IngestionNetworkError
        req_500 = httpx.Request("GET", "https://test")
        resp_500 = httpx.Response(500, request=req_500)
        mock_client.get.return_value = resp_500
        with pytest.raises(IngestionNetworkError, match="HTTP error"):
            adapter._fetch_url_content("https://test")

        # Transport / generic network exception raises IngestionNetworkError
        mock_client.get.side_effect = httpx.ConnectError("Connection reset")
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
        adapter = NativeMediaIngestionAdapter(whisper_device="cpu", whisper_compute_type="int8")

        fake_ct2 = types.ModuleType("ctranslate2")
        fake_ct2.get_cuda_device_count = lambda: 0  # type: ignore[attr-defined]
        fake_fw = types.ModuleType("faster_whisper")
        fake_fw.WhisperModel = MagicMock(side_effect=RuntimeError("Whisper weights corrupt"))  # type: ignore[attr-defined]

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.dict(sys.modules, {"ctranslate2": fake_ct2, "faster_whisper": fake_fw}),
            patch("pathlib.Path.glob") as mock_glob,
            pytest.raises(CresmoInfrastructureError, match="Whisper transcription failed"),
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            mock_glob.return_value = [tmp_path / "dummy_audio.m4a"]

            adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=error",
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )

    def test_transcribe_audio_fallback_keep_audio_copies_file(self, tmp_path: Path) -> None:
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = "Transcribed speech content."
        adapter = NativeMediaIngestionAdapter(transcriber=mock_transcriber)

        dummy_audio = tmp_path / "scratch_dummy.m4a"
        dummy_audio.write_bytes(b"FAKE AUDIO BYTES")

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("tempfile.TemporaryDirectory") as mock_tempdir,
        ):
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            scratch_dir = tmp_path / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            audio_in_scratch = scratch_dir / "dQw4w9WgXcQ.m4a"
            audio_in_scratch.write_bytes(b"FAKE AUDIO DATA")

            mock_tempdir.return_value.__enter__.return_value = str(scratch_dir)

            body = adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=True,
                channel_name="Test Channel",
            )

            assert body == "Transcribed speech content."
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
                return_value="Transcribed from audio fallback.",
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
            assert transcript.content.text == "Transcribed from audio fallback."
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
        from cresmo.infrastructure.adapters.media.subtitles import parse_published_datetime

        dt = parse_published_datetime("20240315")
        assert dt.year == 2024 and dt.month == 3 and dt.day == 15
        dt_fallback = parse_published_datetime(None)
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
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import InMemoryMetricReader

        from cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter import (
            OtlpMetricsAdapter,
        )

        reader = InMemoryMetricReader()
        metrics_adapter = OtlpMetricsAdapter(meter_provider=MeterProvider(metric_readers=[reader]))

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
            metrics_data = reader.get_metrics_data()
            assert metrics_data is not None
            points = [
                dp
                for rm in metrics_data.resource_metrics
                for sm in rm.scope_metrics
                for m in sm.metrics
                if m.name == "cresmo_media_ingestion_duration_seconds"
                for dp in m.data.data_points
            ]
            assert len(points) == 1
            assert dict(points[0].attributes or {}) == {
                "channel_id": "",
                "modality": "url",
                "status": "success",
            }

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

        for term in (
            "Connection reset by peer",
            "Operation timed out",
            "Name or service not known",
            "Network unreachable",
        ):
            with pytest.raises(IngestionNetworkError, match="Ingestion network connectivity error"):
                adapter._handle_yt_dlp_error(Exception(term))

        with pytest.raises(
            CresmoInfrastructureError, match="Media extraction infrastructure error"
        ):
            adapter._handle_yt_dlp_error(Exception("Some unknown yt-dlp internal error"))

    def test_transcribe_audio_fallback_keep_audio_and_cleanup(self, tmp_path: Path) -> None:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (
            [MagicMock(text="  Transcribed text content  ")],
            MagicMock(),
        )
        fake_ct2 = types.ModuleType("ctranslate2")
        fake_ct2.get_cuda_device_count = lambda: 0  # type: ignore[attr-defined]
        fake_fw = types.ModuleType("faster_whisper")
        fake_fw.WhisperModel = MagicMock(return_value=mock_model)  # type: ignore[attr-defined]

        adapter = NativeMediaIngestionAdapter(whisper_device="cpu", whisper_compute_type="int8")
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
            patch.dict(sys.modules, {"ctranslate2": fake_ct2, "faster_whisper": fake_fw}),
        ):
            mock_ydl = MagicMock()
            mock_ydl.download.side_effect = mock_ydl_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            body = adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=123",
                output_dir=tmp_path,
                whisper_model="tiny",
                keep_audio=True,
                channel_name="Science Today",
            )

            assert body == "Transcribed text content"
            saved_audio = tmp_path / "Science Today" / dummy_audio_name
            assert saved_audio.exists()
            assert saved_audio.read_bytes() == b"dummy audio bytes"
            opts = mock_ydl_cls.call_args[0][0]
            assert opts["format"] == "bestaudio/best"
            assert "%(id)s.%(ext)s" in opts["outtmpl"]
            assert opts["quiet"] is True
            assert opts["no_warnings"] is True
            assert "extractor_args" not in opts
            assert "ignore_no_formats_error" not in opts
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
            body = adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=sub_success",
                info=fake_info,
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
                channel_name="MyChannel",
            )
            assert body == "Primeiro paragrafo falado."
            mock_fetch.assert_called_once_with("https://subs.google.com/timedtext?v=sub_success")

    def test_transcribe_audio_fallback_no_downloaded_file_raises_error(
        self, tmp_path: Path
    ) -> None:
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(IngestionNetworkError, match="no file was found"):
                adapter._transcribe_audio_fallback(
                    video_url="https://youtube.com/watch?v=123",
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                    channel_name="UploaderOnly",
                )

    def test_transcribe_audio_fallback_whisper_error_raises_infra_error(
        self, tmp_path: Path
    ) -> None:
        adapter = NativeMediaIngestionAdapter(whisper_device="cpu", whisper_compute_type="int8")

        def mock_ydl_download(urls: list[str]) -> None:
            import glob

            scratch_dirs = glob.glob("/tmp/cresmo_scratch_*")
            if scratch_dirs:
                latest = max(scratch_dirs, key=lambda d: Path(d).stat().st_mtime)
                (Path(latest) / "audio.mp3").write_bytes(b"dummy")

        fake_ct2 = types.ModuleType("ctranslate2")
        fake_ct2.get_cuda_device_count = lambda: 0  # type: ignore[attr-defined]
        fake_fw = types.ModuleType("faster_whisper")
        fake_fw.WhisperModel = MagicMock(side_effect=RuntimeError("CUDA OOM"))  # type: ignore[attr-defined]

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch.dict(sys.modules, {"ctranslate2": fake_ct2, "faster_whisper": fake_fw}),
        ):
            mock_ydl = MagicMock()
            mock_ydl.download.side_effect = mock_ydl_download
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(
                CresmoInfrastructureError, match="Whisper transcription failed: CUDA OOM"
            ):
                adapter._transcribe_audio_fallback(
                    video_url="https://youtube.com/watch?v=123",
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                    channel_name="Unknown_Channel",
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
        assert transcript.content.text == "Qubits can exist in superposition."
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
        assert transcript.channel.url == "https://www.youtube.com/@Chan"
        assert ch_id is not None
        assert ch_id.value == "uploader_xyz"

    def test_build_ydl_opts_options_injection(self, tmp_path: Path) -> None:
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text(
            "# Netscape HTTP Cookie File\n.youtube.com TRUE / FALSE 0 SID secret", encoding="utf-8"
        )

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
            assert opts["ignore_no_formats_error"] is True
            assert opts["extractor_args"] == {
                "youtube": {"skip": ["dash", "hls", "translated_subs"]}
            }
            assert mock_ydl.extract_info.call_args[1]["download"] is False

    def test_ensure_yt_dlp_plugins_loaded_is_one_shot(self) -> None:
        from cresmo.infrastructure.adapters.media.subtitles import (
            _reset_yt_dlp_plugins_cache,
            ensure_yt_dlp_plugins_loaded,
        )

        _reset_yt_dlp_plugins_cache()
        try:
            with patch("yt_dlp.plugins.load_all_plugins") as mock_load:
                ensure_yt_dlp_plugins_loaded()
                ensure_yt_dlp_plugins_loaded()
                ensure_yt_dlp_plugins_loaded()
                mock_load.assert_called_once()
        finally:
            _reset_yt_dlp_plugins_cache()

    def test_discover_channel_feed_uses_adapter_rss_fast_path_and_respects_flag(self) -> None:
        now = datetime.now(UTC)
        atom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <title>CanonicalChan</title>
  <entry>
    <yt:videoId>rssvid11111</yt:videoId>
    <title>RSS Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=rssvid11111"/>
    <published>{now.strftime("%Y-%m-%dT%H:%M:%S+00:00")}</published>
  </entry>
</feed>"""
        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.text = atom_xml
        mock_client.get.return_value = mock_resp

        adapter = NativeMediaIngestionAdapter(http_client=mock_client, enable_rss_fast_path=True)
        query = ChannelFeedQuery(
            channel_url="https://www.youtube.com/channel/UC1234567890123456789012",
            lookback_days=7,
            max_videos=10,
        )
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            items = adapter.discover_channel_feed(query)
        assert len(items) == 1
        assert items[0].content_id == ContentId("rssvid11111")
        mock_ydl_cls.assert_not_called()

        adapter_no_rss = NativeMediaIngestionAdapter(
            http_client=mock_client, enable_rss_fast_path=False
        )
        mock_client.get.reset_mock()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"entries": []}
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            adapter_no_rss.discover_channel_feed(query)
        mock_client.get.assert_not_called()
        mock_ydl_cls.assert_called_once()

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
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import InMemoryMetricReader

        from cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter import (
            OtlpMetricsAdapter,
        )

        reader = InMemoryMetricReader()
        metrics = OtlpMetricsAdapter(meter_provider=MeterProvider(metric_readers=[reader]))
        adapter = NativeMediaIngestionAdapter(metrics_port=metrics)

        with (
            patch.object(
                adapter,
                "_fetch_video_metadata",
                return_value={"id": "fail1", "channel": "FailChan"},
            ),
            patch.object(
                adapter, "_resolve_transcript_body", side_effect=RuntimeError("Whisper exploded")
            ),
            pytest.raises(RuntimeError, match="Whisper exploded"),
        ):
            adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=fail1",
                output_dir=tmp_path,
            )

        metrics_data = reader.get_metrics_data()
        assert metrics_data is not None
        points = [
            dp
            for rm in metrics_data.resource_metrics
            for sm in rm.scope_metrics
            for m in sm.metrics
            if m.name == "cresmo_media_ingestion_duration_seconds"
            for dp in m.data.data_points
        ]
        assert len(points) == 1
        assert dict(points[0].attributes or {}) == {
            "channel_id": "",
            "modality": "url",
            "status": "failure",
        }

    def test_resolve_transcript_body_empty_raises_domain_validation_error(
        self, tmp_path: Path
    ) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value=None),
            patch.object(adapter, "_transcribe_audio_fallback", return_value=""),
            pytest.raises(DomainValidationError, match="Extracted transcript body is empty"),
        ):
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
            patch.object(
                adapter, "_fetch_url_content", side_effect=RateLimitExceededError("HTTP 429")
            ),
            pytest.raises(RateLimitExceededError),
        ):
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
            patch.object(adapter, "_transcribe_audio_fallback", return_value="Fallback body"),
        ):
            body = adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=sub_err",
                info={"id": "sub_err", "channel": "Chan"},
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
                channel_name="Chan",
            )
            assert body == "Fallback body"
            assert "Failed to fetch or parse native subtitles" in caplog.text
            assert "Falling back to Whisper" in caplog.text

    def test_detect_js_runtime_precedence_and_none(self) -> None:
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
        assert (
            adapter._sanitize_fs_name("Channel: With / Illegal * Chars?")
            == "Channel_ With _ Illegal _ Chars_"
        )
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
            patch.object(
                adapter,
                "_resolve_transcript_body",
                return_value="Resolved body text",
            ),
        ):
            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=ingest_ok_1",
                output_dir=tmp_path,
                whisper_model="tiny",
                keep_audio=False,
            )
            assert transcript is not None
            assert transcript.content.title == "Ingested Title"
            assert transcript.content.text == "Resolved body text"
            assert transcript.channel.name == "IngestChan"
            assert transcript.channel.id is not None
            assert transcript.channel.id.value == "UC_ingest_123"

    def test_extract_channel_name_fallback_hierarchy(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        # 1. Prefer 'channel'
        assert (
            adapter._extract_channel_name({"channel": "PrimaryChannel", "uploader": "Ignored"})
            == "PrimaryChannel"
        )
        # 2. Fall back to 'uploader'
        assert adapter._extract_channel_name({"uploader": "FallbackUploader"}) == "FallbackUploader"
        # 3. Default to 'Unknown_Channel'
        assert adapter._extract_channel_name({}) == "Unknown_Channel"

    def test_ingest_single_video_resolve_body_failure_records_resolved_channel_in_metrics(
        self, tmp_path: Path
    ) -> None:
        mock_metrics = MagicMock()
        adapter = NativeMediaIngestionAdapter(metrics_port=mock_metrics)
        fake_info = {
            "id": "vid_err_429",
            "channel": "RobustChannel",
            "channel_id": "UC_robust_1",
        }
        with (
            patch.object(adapter, "_fetch_video_metadata", return_value=fake_info),
            patch.object(
                adapter,
                "_resolve_transcript_body",
                side_effect=RateLimitExceededError("HTTP 429"),
            ),
            pytest.raises(RateLimitExceededError),
        ):
            adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=vid_err_429",
                output_dir=tmp_path,
            )

        mock_metrics.observe_histogram.assert_called_once()
        call_labels = mock_metrics.observe_histogram.call_args[1]["labels"]
        assert call_labels["channel_id"] == "UC_robust_1"
        assert "channel_name" not in call_labels
        assert call_labels["status"] == "failure"


class TestMediaMutationHardening:
    """Additional hermetic tests closing boundary, subtitle, and lifecycle mutation gaps."""

    def test_ensure_yt_dlp_plugins_loaded_retries_after_failure_and_logs(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        from cresmo.infrastructure.adapters.media import subtitles as subtitles_mod

        caplog.set_level(logging.DEBUG)
        subtitles_mod._reset_yt_dlp_plugins_cache()
        assert subtitles_mod._PLUGINS_LOADED is False
        try:
            with patch(
                "yt_dlp.plugins.load_all_plugins",
                side_effect=[RuntimeError("plugin boom"), None],
            ) as mock_load:
                subtitles_mod.ensure_yt_dlp_plugins_loaded()
                assert subtitles_mod._PLUGINS_LOADED is False
                assert any(
                    r.getMessage() == "Failed to load yt-dlp plugins: plugin boom"
                    for r in caplog.records
                )

                subtitles_mod.ensure_yt_dlp_plugins_loaded()
                assert subtitles_mod._PLUGINS_LOADED is True

                subtitles_mod.ensure_yt_dlp_plugins_loaded()
                assert mock_load.call_count == 2
        finally:
            subtitles_mod._reset_yt_dlp_plugins_cache()

    def test_reconstruct_json3_paragraphs_boundaries_and_filtering(self) -> None:
        from cresmo.infrastructure.adapters.media.subtitles import reconstruct_json3_paragraphs

        assert reconstruct_json3_paragraphs({}) == ""

        data_mixed = {
            "events": [
                {"tStartMs": 0},
                {"aAppend": 1, "segs": [{"utf8": "ignored append"}]},
                {"segs": [{"utf8": "alpha"}]},
                {"segs": [{"utf8": "   "}]},
                {"segs": [{}, {"utf8": "beta "}, {"utf8": "gamma"}]},
            ]
        }
        assert reconstruct_json3_paragraphs(data_mixed) == "alpha beta gamma"

        data_threshold = {
            "events": [
                {"segs": [{"utf8": "s1"}]},
                {"segs": [{"utf8": "s2"}]},
                {"segs": [{"utf8": "s3"}]},
                {"segs": [{"utf8": "s4"}]},
                {"segs": [{"utf8": "s5"}]},
                {"segs": [{"utf8": "s6"}]},
            ]
        }
        assert reconstruct_json3_paragraphs(data_threshold) == "s1 s2 s3 s4\n\ns5 s6"

        data_punct = {
            "events": [
                {"segs": [{"utf8": "One."}]},
                {"segs": [{"utf8": "Two!"}]},
                {"segs": [{"utf8": "Three?"}]},
                {"segs": [{"utf8": "Four"}]},
                {"segs": [{"utf8": "five"}]},
            ]
        }
        assert reconstruct_json3_paragraphs(data_punct) == "One.\n\nTwo!\n\nThree?\n\nFour five"

    def test_find_native_subtitle_url_language_precedence_and_auto_captions(self) -> None:
        from itertools import pairwise

        from cresmo.infrastructure.adapters.media.subtitles import (
            find_in_auto_captions,
            find_native_subtitle_url,
        )

        pt_order = ["pt-orig", "pt-BR", "pt", "pt-PT", "en-orig", "en", "en-US", "fr"]
        for higher, lower in pairwise(pt_order):
            info_pt = {
                "language": "PT-BR",
                "subtitles": {
                    lower: [{"ext": "json3", "url": f"https://subs/{lower}"}],
                    higher: [{"ext": "json3", "url": f"https://subs/{higher}"}],
                },
            }
            assert find_native_subtitle_url(info_pt) == f"https://subs/{higher}"

        en_order = ["en-orig", "en", "en-US", "pt-orig", "pt-BR", "pt", "pt-PT", "fr"]
        for higher, lower in pairwise(en_order):
            info_en = {
                "language": None,
                "subtitles": {
                    lower: [{"ext": "json3", "url": f"https://subs/{lower}"}],
                    higher: [{"ext": "json3", "url": f"https://subs/{higher}"}],
                },
            }
            assert find_native_subtitle_url(info_en) == f"https://subs/{higher}"

        # Auto-captions: "orig" key beats "en"
        assert (
            find_native_subtitle_url(
                {
                    "language": "en",
                    "automatic_captions": {
                        "en": [{"ext": "json3", "url": "https://subs/en"}],
                        "orig": [{"ext": "json3", "url": "https://subs/orig"}],
                    },
                }
            )
            == "https://subs/orig"
        )
        # Auto-captions: non-preferred *-orig ("es-orig") still beats "en"
        assert (
            find_native_subtitle_url(
                {
                    "language": "en",
                    "automatic_captions": {
                        "en": [{"ext": "json3", "url": "https://subs/en"}],
                        "es-orig": [{"ext": "json3", "url": "https://subs/es-orig"}],
                    },
                }
            )
            == "https://subs/es-orig"
        )
        # Auto-captions: is_pt_video=True prioritizes pt-orig over en-orig and fr-orig
        assert (
            find_native_subtitle_url(
                {
                    "language": "pt",
                    "automatic_captions": {
                        "fr-orig": [{"ext": "json3", "url": "https://subs/fr-orig"}],
                        "en-orig": [{"ext": "json3", "url": "https://subs/en-orig"}],
                        "pt-orig": [{"ext": "json3", "url": "https://subs/pt-orig"}],
                    },
                }
            )
            == "https://subs/pt-orig"
        )
        # Auto-captions: is_pt_video=False prioritizes en-orig over pt-orig and fr-orig
        assert (
            find_native_subtitle_url(
                {
                    "language": "en",
                    "automatic_captions": {
                        "fr-orig": [{"ext": "json3", "url": "https://subs/fr-orig"}],
                        "pt-orig": [{"ext": "json3", "url": "https://subs/pt-orig"}],
                        "en-orig": [{"ext": "json3", "url": "https://subs/en-orig"}],
                    },
                }
            )
            == "https://subs/en-orig"
        )
        # Auto-captions: ordered_langs beats fallback dict order
        assert (
            find_in_auto_captions(
                {
                    "fr": [{"ext": "json3", "url": "https://subs/fr"}],
                    "en": [{"ext": "json3", "url": "https://subs/en"}],
                },
                ordered_langs=["en"],
                is_pt_video=False,
            )
            == "https://subs/en"
        )

    def test_parse_upload_date_and_published_datetime_strict_8_digits_and_utc(self) -> None:
        from cresmo.infrastructure.adapters.media.subtitles import (
            parse_published_datetime,
            parse_upload_date,
        )

        # 6-digit string parses in strptime("%Y%m%d") unless len==8 is enforced
        assert parse_upload_date("202411") is None
        assert parse_upload_date("abcdefgh") is None

        dt_valid = parse_published_datetime("20240315")
        assert dt_valid == datetime(2024, 3, 15, 0, 0, tzinfo=UTC)
        assert dt_valid.tzinfo == UTC

        dt_short = parse_published_datetime("202411")
        assert dt_short.year >= 2026
        assert dt_short.tzinfo == UTC

        assert parse_published_datetime(None).tzinfo == UTC
        assert parse_published_datetime("20249999").tzinfo == UTC

    def test_default_adapter_configuration_and_explicit_js_runtime(self, tmp_path: Path) -> None:
        import threading
        import time

        adapter = NativeMediaIngestionAdapter()
        assert adapter.request_timeout == 30.0
        assert adapter._enable_rss_fast_path is True

        audio_file = tmp_path / "default.m4a"
        audio_file.write_bytes(b"audio")
        active = 0
        max_active = 0
        lock = threading.Lock()
        two_inside = threading.Event()

        def slow_transcribe(*_args: object, **_kwargs: object) -> tuple[list[MagicMock], MagicMock]:
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
                if active == 2:
                    two_inside.set()
            two_inside.wait(timeout=0.5)
            time.sleep(0.03)
            with lock:
                active -= 1
            return ([MagicMock(text="ok")], MagicMock())

        mock_model = MagicMock()
        mock_model.transcribe.side_effect = slow_transcribe
        fake_ct2 = types.ModuleType("ctranslate2")
        fake_ct2.get_cuda_device_count = lambda: 1  # type: ignore[attr-defined]
        fake_fw = types.ModuleType("faster_whisper")
        fake_fw.WhisperModel = MagicMock(return_value=mock_model)  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"ctranslate2": fake_ct2, "faster_whisper": fake_fw}):
            assert adapter._transcriber.resolve_device() == "cuda"
            assert adapter._transcriber.resolve_compute_type("cuda") == "float16"
            assert adapter._transcriber.resolve_compute_type("cpu") == "int8"
            threads = [
                threading.Thread(target=adapter._transcriber.transcribe, args=(audio_file, "base"))
                for _ in range(3)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        assert max_active == 2
        assert mock_model.transcribe.call_args.kwargs["vad_filter"] is True

        with patch("shutil.which", return_value=None):
            explicit_js_adapter = NativeMediaIngestionAdapter(js_runtime_name="deno")
        assert explicit_js_adapter._build_ydl_opts({})["js_runtimes"] == {"deno": {}}

        custom_adapter = NativeMediaIngestionAdapter(
            whisper_concurrency_limit=1,
            whisper_device="cpu",
            whisper_compute_type="float32",
            whisper_vad_filter=False,
        )
        assert custom_adapter._transcriber.resolve_device() == "cpu"
        assert custom_adapter._transcriber.resolve_compute_type("cuda") == "float32"
        assert custom_adapter._transcriber._vad_filter is False
        assert custom_adapter._transcriber._semaphore._value == 1

    def test_owned_httpx_client_http2_detection_and_close_reset(self) -> None:
        adapter = NativeMediaIngestionAdapter()
        with (
            patch("importlib.util.find_spec", return_value=object()) as mock_find_spec,
            patch("httpx.Client") as mock_client_cls,
        ):
            mock_client_cls.return_value = MagicMock()
            adapter._get_http_client()
            mock_find_spec.assert_called_once_with("h2")
            assert mock_client_cls.call_args.kwargs["http2"] is True
            assert mock_client_cls.call_args.kwargs["timeout"] == 30.0

            adapter.close()
            assert adapter._http_client is None
            adapter._get_http_client()
            assert mock_client_cls.call_count == 2

        adapter_no_h2 = NativeMediaIngestionAdapter()
        with (
            patch("importlib.util.find_spec", return_value=None) as mock_find_spec,
            patch("httpx.Client") as mock_client_cls,
        ):
            adapter_no_h2._get_http_client()
            mock_find_spec.assert_called_once_with("h2")
            assert mock_client_cls.call_args.kwargs["http2"] is False

    def test_build_ydl_opts_skips_empty_cookie_file_and_extracts_canonical_id(
        self, tmp_path: Path
    ) -> None:
        empty_cookies = tmp_path / "empty_cookies.txt"
        empty_cookies.write_text("", encoding="utf-8")
        adapter = NativeMediaIngestionAdapter(cookie_file=empty_cookies)
        opts = adapter._build_ydl_opts({})
        assert "cookiefile" not in opts

        one_byte_cookies = tmp_path / "one_byte_cookies.txt"
        one_byte_cookies.write_text("a", encoding="utf-8")
        adapter_1b = NativeMediaIngestionAdapter(cookie_file=one_byte_cookies)
        assert adapter_1b._build_ydl_opts({})["cookiefile"] == str(one_byte_cookies.resolve())

        assert adapter._extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert (
            adapter._reconstruct_json3_paragraphs({"events": [{"segs": [{"utf8": "Hi"}]}]}) == "Hi"
        )

    def test_transcribe_audio_fallback_defaults_nested_existing_dir_and_errors(
        self, tmp_path: Path
    ) -> None:
        import tempfile
        from typing import Any

        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = "Ok body"
        adapter = NativeMediaIngestionAdapter(transcriber=mock_transcriber)

        nested_output = tmp_path / "nested" / "out"
        real_tempdir = tempfile.TemporaryDirectory

        def tracking_tempdir(*args: Any, **kwargs: Any) -> tempfile.TemporaryDirectory[str]:
            td = real_tempdir(*args, **kwargs)
            (Path(td.name) / "vid.m4a").write_bytes(b"audio")
            return td

        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("tempfile.TemporaryDirectory", side_effect=tracking_tempdir),
        ):
            mock_ydl_cls.return_value.__enter__.return_value = MagicMock()
            body = adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=nested_output,
                whisper_model="base",
                keep_audio=True,
            )

        assert body == "Ok body"
        assert (nested_output / "Unknown_Channel" / "vid.m4a").exists()
        opts = mock_ydl_cls.call_args[0][0]
        assert Path(opts["outtmpl"]).name == "%(id)s.%(ext)s"
        transcribe_call = mock_transcriber.transcribe.call_args
        assert isinstance(transcribe_call.args[0], Path)
        assert transcribe_call.args[0].name == "vid.m4a"
        assert transcribe_call.kwargs["model_name"] == "base"

        # Existing destination dir succeeds (exist_ok=True)
        with (
            patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
            patch("tempfile.TemporaryDirectory", side_effect=tracking_tempdir),
        ):
            mock_ydl_cls.return_value.__enter__.return_value = MagicMock()
            adapter._transcribe_audio_fallback(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=nested_output,
                whisper_model="base",
                keep_audio=True,
            )

        # Download exception delegates to _handle_yt_dlp_error
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.download.side_effect = RuntimeError("HTTP Error 429")
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            with pytest.raises(RateLimitExceededError, match="HTTP 429"):
                adapter._transcribe_audio_fallback(
                    video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                    output_dir=tmp_path,
                    whisper_model="base",
                    keep_audio=False,
                )

    def test_fetch_video_metadata_and_extract_channel_url_call_args_and_logs(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(logging.DEBUG)
        adapter = NativeMediaIngestionAdapter()
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"id": "123"}
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl

            adapter._fetch_video_metadata("https://youtube.com/watch?v=123")
            mock_ydl.extract_info.assert_called_once_with(
                "https://youtube.com/watch?v=123", download=False
            )

            mock_ydl.extract_info.reset_mock()
            mock_ydl.extract_info.return_value = {"channel_id": "UC1234567890123456789012"}
            adapter.extract_channel_url_from_video("https://www.youtube.com/watch?v=abc12345")
            mock_ydl.extract_info.assert_called_once_with(
                "https://www.youtube.com/watch?v=abc12345", download=False
            )

            mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
            assert (
                adapter.extract_channel_url_from_video(
                    "https://www.youtube.com/watch?v=unavailable"
                )
                is None
            )
            assert any(
                r.getMessage() == "Could not extract channel URL from video "
                "'https://www.youtube.com/watch?v=unavailable' "
                "via flat extraction: Video unavailable"
                for r in caplog.records
            )

    def test_resolve_transcript_body_fallback_args_video_id_and_warning_log(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(logging.WARNING)
        adapter = NativeMediaIngestionAdapter()

        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value="https://subs.url"),
            patch.object(adapter, "_fetch_url_content", side_effect=RuntimeError("decode err")),
            patch.object(
                adapter, "_transcribe_audio_fallback", return_value="Whisper text"
            ) as mock_fb,
        ):
            body = adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                info={},
                output_dir=tmp_path,
                whisper_model="small",
                keep_audio=True,
            )
            assert body == "Whisper text"
            mock_fb.assert_called_once_with(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                output_dir=tmp_path,
                whisper_model="small",
                keep_audio=True,
                channel_name="Unknown_Channel",
            )
            assert any(
                r.getMessage()
                == "Failed to fetch or parse native subtitles from 'https://subs.url': "
                "decode err. Falling back to Whisper."
                for r in caplog.records
            )

        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value=None),
            patch.object(adapter, "_transcribe_audio_fallback", return_value=""),
            pytest.raises(DomainValidationError, match="dQw4w9WgXcQ"),
        ):
            adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                info={},
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )

        with (
            patch.object(adapter, "_find_native_subtitle_url", return_value=None),
            patch.object(adapter, "_transcribe_audio_fallback", return_value=""),
            pytest.raises(DomainValidationError, match="empty_vid"),
        ):
            adapter._resolve_transcript_body(
                video_url="https://youtube.com/watch?v=other",
                info={"id": "empty_vid"},
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
            )

    def test_build_raw_transcript_aggregate_taxonomy_url_and_missing_fields(self) -> None:
        mock_taxonomy = MagicMock()
        mock_taxonomy.classify.return_value = ("Political Philosophy", "evergreen")
        adapter = NativeMediaIngestionAdapter(taxonomy_port=mock_taxonomy)

        transcript, _ = adapter._build_raw_transcript_aggregate(
            video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            info={},
            body="Body text",
            channel_name="QuantumHub",
        )
        mock_taxonomy.classify.assert_called_once_with("QuantumHub")
        assert transcript.channel.category == "Political Philosophy"
        assert transcript.provenance.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert transcript.content.id == ContentId("dQw4w9WgXcQ")
        assert transcript.content.title == ""

        with pytest.raises(DomainValidationError, match="bad id!"):
            adapter._build_raw_transcript_aggregate(
                video_url="bad id!",
                info={"id": "bad id!"},
                body="Body text",
                channel_name="QuantumHub",
            )

    def test_ingest_single_video_defaults_metrics_and_discover_error_handler(
        self, tmp_path: Path
    ) -> None:
        mock_metrics = MagicMock()
        adapter = NativeMediaIngestionAdapter(metrics_port=mock_metrics)
        fake_info = {
            "id": "ingest_ok_1",
            "title": "Ingested Title",
            "channel": "IngestChan",
            "channel_id": "UC1234567890123456789012",
        }
        with (
            patch.object(adapter, "_fetch_video_metadata", return_value=fake_info) as mock_meta,
            patch.object(adapter, "_resolve_transcript_body", return_value="Body") as mock_resolve,
        ):
            transcript = adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=ingest_ok_1",
                output_dir=tmp_path,
            )
            assert transcript is not None
            mock_meta.assert_called_once_with("https://youtube.com/watch?v=ingest_ok_1")
            mock_resolve.assert_called_once_with(
                video_url="https://youtube.com/watch?v=ingest_ok_1",
                info=fake_info,
                output_dir=tmp_path,
                whisper_model="base",
                keep_audio=False,
                channel_name="IngestChan",
            )

        elapsed = mock_metrics.observe_histogram.call_args.args[1]
        labels = mock_metrics.observe_histogram.call_args.kwargs["labels"]
        assert 0.0 <= elapsed < 10.0
        assert labels == {
            "channel_id": "UC1234567890123456789012",
            "modality": "url",
            "status": "success",
        }

        mock_metrics.reset_mock()
        with patch.object(adapter, "_fetch_video_metadata", return_value=None):
            assert (
                adapter.ingest_single_video(
                    video_url="https://youtube.com/watch?v=none_meta",
                    output_dir=tmp_path,
                )
                is None
            )
        assert mock_metrics.observe_histogram.call_args.kwargs["labels"] == {
            "channel_id": "",
            "modality": "url",
            "status": "failure",
        }

        mock_metrics.reset_mock()
        with (
            patch.object(
                adapter, "_fetch_video_metadata", side_effect=IngestionNetworkError("boom")
            ),
            pytest.raises(IngestionNetworkError),
        ):
            adapter.ingest_single_video(
                video_url="https://youtube.com/watch?v=err_meta",
                output_dir=tmp_path,
            )
        assert mock_metrics.observe_histogram.call_args.kwargs["labels"] == {
            "channel_id": "",
            "modality": "url",
            "status": "failure",
        }

        # discover_channel_feed forwards _handle_yt_dlp_error
        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@HandleChan",
            lookback_days=7,
            max_videos=10,
        )
        with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("HTTP Error 429")
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            with pytest.raises(RateLimitExceededError, match="HTTP 429"):
                adapter.discover_channel_feed(query)
