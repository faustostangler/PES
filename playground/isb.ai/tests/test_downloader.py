import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Since pytest will run from the root directory, let's ensure we can import downloader and sync_channels.
# The pyproject.toml adds 'playground/isb.ai' to pyright extraPaths, and we should be able to import directly
# if the current working directory includes it or if we append it to sys.path.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import downloader
import sync_channels

@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_success(mock_ytdl_class):
    """Should successfully fetch metadata on the first try."""
    mock_instance = MagicMock()
    mock_ytdl_class.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {"id": "test_id", "title": "Test Title"}

    url = "https://www.youtube.com/watch?v=test_id"
    result = downloader.extract_video_metadata(url)

    assert result == {"id": "test_id", "title": "Test Title"}
    mock_ytdl_class.assert_called_once()


@patch("downloader.apply_cookies_to_ydl_opts")
@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_auto_refresh_on_bot_detection(mock_ytdl_class, mock_apply_cookies):
    """Should auto-refresh cookies and retry when bot/login challenge is detected."""
    mock_instance_bot_err = MagicMock()
    mock_instance_bot_err.extract_info.side_effect = Exception("Sign in to confirm you’re not a bot.")

    mock_instance_success = MagicMock()
    mock_instance_success.extract_info.return_value = {"id": "test_id", "title": "Test Title"}

    mock_ytdl_class.return_value.__enter__.side_effect = [
        mock_instance_bot_err,
        mock_instance_success
    ]

    url = "https://www.youtube.com/watch?v=test_id"
    result = downloader.extract_video_metadata(url)

    assert result == {"id": "test_id", "title": "Test Title"}
    assert mock_ytdl_class.call_count == 2
    # Verify apply_cookies_to_ydl_opts was called with force_refresh=True on retry
    assert mock_apply_cookies.call_count == 2
    assert mock_apply_cookies.call_args_list[1][1].get("force_refresh") is True


@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_returns_empty_dict_on_unresolvable_error(mock_ytdl_class):
    """Should return empty dict gracefully on unresolvable failure."""
    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = Exception("Network Unreachable")
    mock_ytdl_class.return_value.__enter__.return_value = mock_instance

    url = "https://www.youtube.com/watch?v=test_id"
    result = downloader.extract_video_metadata(url)

    assert result == {}


@patch("downloader.apply_cookies_to_ydl_opts")
@patch("downloader.yt_dlp.YoutubeDL")
def test_download_audio_as_ogg_auto_refresh_on_bot_detection(mock_ytdl_class, mock_apply_cookies):
    """Should auto-refresh cookies and retry if download fails with bot challenge."""
    mock_instance_bot_err = MagicMock()
    mock_instance_bot_err.extract_info.side_effect = Exception("Sign in to confirm you’re not a bot.")

    mock_instance_success = MagicMock()

    mock_ytdl_class.return_value.__enter__.side_effect = [
        mock_instance_bot_err,
        mock_instance_success
    ]

    url = "https://www.youtube.com/watch?v=test_id"
    output_dir = Path("/tmp")
    video_id = "test_id"

    result = downloader.download_audio_as_ogg(url, output_dir, video_id)

    assert result == Path("/tmp/test_id.ogg").resolve()
    assert mock_ytdl_class.call_count == 2
    assert mock_apply_cookies.call_count == 2
    assert mock_apply_cookies.call_args_list[1][1].get("force_refresh") is True


@patch("sync_channels.yt_dlp.YoutubeDL")
def test_fetch_channel_recent_videos_success(mock_ytdl_class):
    """Should extract channel recent videos using YouTube playlist."""
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        "entries": [{"id": "vid1", "url": "url1"}]
    }
    mock_ytdl_class.return_value.__enter__.return_value = mock_instance

    result = sync_channels.fetch_channel_recent_videos("UC12345", limit=5)

    assert len(result) == 1
    assert result[0]["id"] == "vid1"
    mock_ytdl_class.assert_called_once()


@patch("downloader.time.sleep")
@patch("downloader.parse_json3_to_paragraphs")
def test_get_youtube_audio_or_transcript_retries_on_429_when_subtitles_exist(mock_parse_json3, mock_sleep):
    """Should retry fetching subtitles with sleep when HTTP 429 occurs on existing subtitles."""
    import urllib.error
    downloader.reset_429_state()
    # Simulates 429 on first 2 calls, then success on 3rd call
    mock_parse_json3.side_effect = [
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        "Subtitles retrieved successfully after waiting"
    ]

    info = {
        "id": "test_vid",
        "title": "Test Title",
        "subtitles": {"en": [{"ext": "json3", "url": "http://test_url"}]}
    }

    txt, ogg, vid = downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid", info=info)

    assert txt == "Subtitles retrieved successfully after waiting"
    assert ogg is None
    assert vid == "test_vid"
    assert mock_parse_json3.call_count == 3
    assert mock_sleep.call_count == 2
    assert downloader.get_429_attempt_count() == 0


@patch("downloader.download_audio_as_ogg")
@patch("downloader.parse_json3_to_paragraphs")
@patch("downloader.time.sleep")
def test_get_youtube_audio_or_transcript_falls_back_to_whisper_after_5_failed_attempts(mock_sleep, mock_parse_json3, mock_download_ogg):
    """Should fall back to Whisper after 5 accumulated failed exponential 429 attempts on subtitles."""
    import urllib.error
    downloader.reset_429_state()
    mock_parse_json3.side_effect = urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None)
    mock_download_ogg.return_value = Path("/tmp/test_vid.ogg")

    info = {
        "id": "test_vid",
        "title": "Test Title",
        "subtitles": {"en": [{"ext": "json3", "url": "http://test_url"}]}
    }

    txt, ogg, vid = downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid", info=info)

    assert txt is None
    assert ogg == "/tmp/test_vid.ogg"
    assert vid == "test_vid"
    assert mock_parse_json3.call_count == 5
    assert mock_sleep.call_count == 5
    assert mock_download_ogg.call_count == 1
    assert downloader.get_429_attempt_count() == 5


@patch("downloader.download_audio_as_ogg")
@patch("downloader.parse_json3_to_paragraphs")
@patch("downloader.time.sleep")
def test_get_youtube_audio_or_transcript_continues_exponential_streak_on_next_video(mock_sleep, mock_parse_json3, mock_download_ogg):
    """Next video should continue accumulated exponential streak without resetting and fallback to Whisper if 429 persists."""
    import urllib.error
    downloader.reset_429_state()
    mock_parse_json3.side_effect = urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None)
    mock_download_ogg.return_value = Path("/tmp/test_vid.ogg")

    info = {
        "id": "test_vid",
        "title": "Test Title",
        "subtitles": {"en": [{"ext": "json3", "url": "http://test_url"}]}
    }

    # Video 1: accumulates 5 failed attempts, falls back to Whisper
    downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid1", info=info)
    assert downloader.get_429_attempt_count() == 5

    # Video 2: starts with 429 attempt count = 5 (does 1 attempt with current exponential backoff, then Whisper)
    downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid2", info=info)
    assert downloader.get_429_attempt_count() == 6
    assert mock_download_ogg.call_count == 2


@patch("downloader.download_audio_as_ogg")
@patch("downloader.parse_json3_to_paragraphs")
@patch("downloader.time.sleep")
def test_get_youtube_audio_or_transcript_resets_streak_on_permitted_access(mock_sleep, mock_parse_json3, mock_download_ogg):
    """Permitted subtitle access should reset accumulated 429 attempt count to 0."""
    import urllib.error
    downloader.reset_429_state()
    mock_parse_json3.side_effect = [
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        urllib.error.HTTPError("http://test", 429, "Too Many Requests", {}, None),
        "Subtitles retrieved successfully"
    ]
    mock_download_ogg.return_value = Path("/tmp/test_vid.ogg")

    info = {
        "id": "test_vid",
        "title": "Test Title",
        "subtitles": {"en": [{"ext": "json3", "url": "http://test_url"}]}
    }

    # Video 1: fails 5 times, falls back to Whisper
    downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid1", info=info)
    assert downloader.get_429_attempt_count() == 5

    # Video 2: succeeds on 1st attempt (6th total call to parse_json3)
    txt, ogg, vid = downloader.get_youtube_audio_or_transcript("http://youtube.com/watch?v=test_vid2", info=info)
    assert txt == "Subtitles retrieved successfully"
    assert downloader.get_429_attempt_count() == 0  # Reset!


def test_rate_limit_telemetry_logging_and_estimation(tmp_path):
    """Should record 429 telemetry events to JSON and estimate average/median recovery timeout."""
    test_log = tmp_path / "test_rate_limit_log.json"

    # Log 429 failure and successful recovery
    downloader.log_rate_limit_telemetry("vid1", 1, 10.0, "RATE_LIMITED_429", 10.0, log_file=test_log)
    downloader.log_rate_limit_telemetry("vid1", 2, 20.0, "RATE_LIMITED_429", 30.0, log_file=test_log)
    downloader.log_rate_limit_telemetry("vid1", 2, 40.0, "SUCCESS", 70.0, log_file=test_log)

    downloader.log_rate_limit_telemetry("vid2", 1, 10.0, "RATE_LIMITED_429", 10.0, log_file=test_log)
    downloader.log_rate_limit_telemetry("vid2", 2, 20.0, "SUCCESS", 30.0, log_file=test_log)

    # Median of recovery times (70.0, 30.0) -> [30.0, 70.0] -> 70.0
    est = downloader.get_estimated_timeout_seconds(log_file=test_log)
    assert est is not None
    assert est > 0
    assert test_log.exists()


def test_ewma_base_quantum_update():
    """Should update base quantum using EWMA formula: B_k = alpha * B_{k-1} + (1 - alpha) * X_k."""
    downloader.reset_429_state(reset_quantum=True, default_quantum=1.0)
    assert downloader.get_base_backoff_quantum() == 1.0

    # Test with alpha = 0.8, initial B_0 = 1.0, observed X_1 = 0.5
    # B_1 = 0.8 * 1.0 + 0.2 * 0.5 = 0.8 + 0.1 = 0.9
    new_q = downloader.update_base_quantum(latency=0.5, alpha=0.8)
    assert pytest.approx(new_q, rel=1e-4) == 0.9
    assert pytest.approx(downloader.get_base_backoff_quantum(), rel=1e-4) == 0.9

    # X_2 = 2.0 -> B_2 = 0.8 * 0.9 + 0.2 * 2.0 = 0.72 + 0.40 = 1.12
    new_q = downloader.update_base_quantum(latency=2.0, alpha=0.8)
    assert pytest.approx(new_q, rel=1e-4) == 1.12


def test_calculate_backoff_delay():
    """Should calculate exponential backoff delay t(n) = min(t_max, B_k * 2^n) and support jitter."""
    # n = 0, 1, 2, 3 with base_quantum = 1.5, t_max = 60.0
    assert downloader.calculate_backoff_delay(n=0, base_quantum=1.5, t_max=60.0, jitter=False) == 1.5
    assert downloader.calculate_backoff_delay(n=1, base_quantum=1.5, t_max=60.0, jitter=False) == 3.0
    assert downloader.calculate_backoff_delay(n=2, base_quantum=1.5, t_max=60.0, jitter=False) == 6.0
    assert downloader.calculate_backoff_delay(n=3, base_quantum=1.5, t_max=60.0, jitter=False) == 12.0

    # Capped by t_max
    assert downloader.calculate_backoff_delay(n=10, base_quantum=1.5, t_max=60.0, jitter=False) == 60.0

    # With jitter: value should be in [0, t(n)]
    for _ in range(10):
        val = downloader.calculate_backoff_delay(n=2, base_quantum=2.0, t_max=60.0, jitter=True)
        assert 0.0 <= val <= 8.0




